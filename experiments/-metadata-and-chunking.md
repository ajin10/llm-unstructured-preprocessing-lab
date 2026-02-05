# Experiment 002 — Metadata + Chunking for RAG (Practical Notes)

## Objective
Build a repeatable approach to:
- Keep **document structure** (titles/sections/pages) as metadata
- Turn raw parsed elements into **RAG-ready chunks**
- Produce clean, consistent chunk objects we can embed + store later

This experiment is intentionally “pre-RAG”: we stop right before embeddings/vector DB.

---

## Inputs
- Parsed “elements” JSON (example output from an extraction step)
- Each element typically contains:
  - `type` (Title, NarrativeText, ListItem, Table, Image, etc.)
  - `text` (when available)
  - metadata like `page_number`, `filename`, `languages`, etc.

Repository sample:
- `data/elements_sample.json`

---

## Why metadata matters (the short version)
If you chunk text without structure, retrieval becomes noisy.

What we want to preserve:
- **Source**: filename / doc id
- **Location**: page number / slide number
- **Hierarchy**: section title / parent title
- **Content type**: narrative vs list vs table

This helps:
- better filtering (“only slides”, “only tables”)
- better citations (page/slide references)
- better context assembly (include section title when returning an answer)

---

## Chunking approach used here
We use a simple, explainable strategy that works well as a baseline:

### Step A — Normalize elements
- Drop empty text
- Collapse whitespace
- Standardize metadata keys
- Keep `type` so we can treat Tables differently later

### Step B — Build a lightweight hierarchy
- When we see a `Title`, treat it as the current **active section**
- All following text inherits that section until the next title

### Step C — Chunk by characters (baseline)
- Target chunk size: ~800–1200 chars
- Overlap: ~100–200 chars
- We only chunk within the same `(source, section, page)` group when possible

Output format (what we want at the end):

```json
{
  "chunk_id": "doc1_p3_sec-Intro_0004",
  "text": "chunk text…",
  "metadata": {
    "source": "CoT.pdf",
    "page": 3,
    "section": "Introduction",
    "types": ["NarrativeText", "ListItem"]
  }
}
