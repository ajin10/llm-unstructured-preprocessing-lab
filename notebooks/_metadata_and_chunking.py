
"""
03_metadata_and_chunking.py

Goal:
- Take extracted "elements" (from HTML/PPTX/PDF parsing)
- Normalize them into a consistent schema
- Add lightweight metadata (source, section, page)
- Chunk into RAG-friendly text blocks

This is a lab-style script: readable, inspectable, and easy to extend.
"""

import os
import re
import json
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


# -----------------------------
# Helpers
# -----------------------------

def safe_get(d: Dict[str, Any], path: List[str], default=None):
    cur = d
    for k in path:
        if not isinstance(cur, dict) or k not in cur:
            return default
        cur = cur[k]
    return cur


def normalize_whitespace(text: str) -> str:
    text = text.replace("\u00a0", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def guess_section(prev_section: Optional[str], el: Dict[str, Any]) -> Optional[str]:
    """
    Heuristic:
    - If element is a Title, treat it as a section header.
    - Otherwise keep prior section.
    """
    el_type = (el.get("type") or "").lower()
    text = (el.get("text") or "").strip()

    if el_type == "title" and text:
        return text[:120]
    return prev_section


# -----------------------------
# Normalized record
# -----------------------------

@dataclass
class NormalizedChunk:
    chunk_id: str
    text: str
    metadata: Dict[str, Any]


def element_to_record(el: Dict[str, Any], source_name: str, section: Optional[str]) -> Optional[Dict[str, Any]]:
    """
    Convert an unstructured element dict -> minimal normalized record.
    """
    text = (el.get("text") or "").strip()
    if not text:
        return None

    el_type = el.get("type") or "Unknown"

    # Best-effort page number (PDF/API often stores it here)
    page_number = safe_get(el, ["metadata", "page_number"], None)

    # Some partitioners include filename/url in metadata
    filename = safe_get(el, ["metadata", "filename"], None) or source_name

    return {
        "type": el_type,
        "text": normalize_whitespace(text),
        "source": filename,
        "page": page_number,
        "section": section,
    }


# -----------------------------
# Chunking
# -----------------------------

def chunk_records(
    records: List[Dict[str, Any]],
    max_chars: int = 1200,
    overlap_chars: int = 150,
) -> List[NormalizedChunk]:
    """
    Simple character-based chunking that:
    - concatenates record texts
    - preserves section + page metadata
    - adds overlap for retrieval continuity
    """

    chunks: List[NormalizedChunk] = []
    buf = ""
    buf_meta = {
        "sources": set(),
        "pages": set(),
        "sections": set(),
    }

    def flush(final: bool = False):
        nonlocal buf, buf_meta, chunks

        text = normalize_whitespace(buf)
        if not text:
            buf = ""
            buf_meta = {"sources": set(), "pages": set(), "sections": set()}
            return

        chunk_id = f"chunk_{len(chunks)+1:04d}"
        metadata = {
            "sources": sorted([s for s in buf_meta["sources"] if s]),
            "pages": sorted([p for p in buf_meta["pages"] if p is not None]),
            "sections": sorted([s for s in buf_meta["sections"] if s]),
            "char_len": len(text),
        }
        chunks.append(NormalizedChunk(chunk_id=chunk_id, text=text, metadata=metadata))

        if final:
            buf = ""
            buf_meta = {"sources": set(), "pages": set(), "sections": set()}
            return

        # Carry overlap into next buffer
        overlap = text[-overlap_chars:] if overlap_chars > 0 else ""
        buf = overlap
        buf_meta = {"sources": set(), "pages": set(), "sections": set()}

    for r in records:
        piece = r["text"]
        # If adding this record crosses limit, flush first
        if buf and (len(buf) + 2 + len(piece)) > max_chars:
            flush(final=False)

        buf += ("\n\n" if buf else "") + piece
        buf_meta["sources"].add(r.get("source"))
        buf_meta["pages"].add(r.get("page"))
        buf_meta["sections"].add(r.get("section"))

    flush(final=True)
    return chunks


# -----------------------------
# Demo runner
# -----------------------------

def load_elements_json(path: str) -> List[Dict[str, Any]]:
    """
    Expecting: a JSON file with a list of element dicts.
    This keeps our repo course-independent:
    you can paste/convert outputs from scripts into this format.
    """
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError("Expected a JSON list of element dicts.")
    return data


def main():
    # Point this to a local artifact produced by your parsing scripts
    # Example: elements exported from HTML/PPTX/PDF partitioning
    input_path = os.getenv("ELEMENTS_JSON", "data/elements_sample.json")
    source_name = os.getenv("SOURCE_NAME", "sample_document")

    print("Input:", input_path)
    elements = load_elements_json(input_path)

    # Normalize
    records: List[Dict[str, Any]] = []
    current_section = None

    for el in elements:
        current_section = guess_section(current_section, el)
        rec = element_to_record(el, source_name=source_name, section=current_section)
        if rec:
            records.append(rec)

    print("Normalized records:", len(records))

    # Chunk
    chunks = chunk_records(records, max_chars=1200, overlap_chars=150)
    print("Chunks:", len(chunks))

    # Preview
    for c in chunks[:2]:
        print("\n---", c.chunk_id, "---")
        print("META:", json.dumps(c.metadata, indent=2))
        print(c.text[:600], "...\n")

    # Save chunk output
    out_path = os.getenv("CHUNKS_OUT", "data/chunks_sample.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(
            [{"chunk_id": c.chunk_id, "text": c.text, "metadata": c.metadata} for c in chunks],
            f,
            indent=2,
            ensure_ascii=False,
        )

    print("Saved:", out_path)


if __name__ == "__main__":
    main()
