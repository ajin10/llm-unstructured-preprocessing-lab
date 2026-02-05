# Experiment 003 — PDF & Image-Aware Preprocessing

## Objective
Understand how document **layout and visual structure** impact preprocessing quality
for LLM and RAG pipelines.

This experiment focuses on PDFs and image-heavy documents, where
simple text extraction often fails.

---

## Why PDFs and Images are Hard
Unlike plain text:
- PDFs encode **visual layout**, not logical structure
- Tables, columns, images, and captions are spatial
- Reading order is ambiguous

If we ignore layout:
- Tables collapse into unreadable text
- Headings lose hierarchy
- Images are dropped entirely

---

## Approaches Compared

### 1. Basic PDF Parsing
- Fast
- Text-first
- Minimal layout awareness

**Pros**
- Cheap
- Quick ingestion

**Cons**
- Poor table handling
- Broken reading order

---

### 2. Layout-Aware Parsing
- Uses document layout detection
- Preserves tables and sections
- Produces richer metadata

**Pros**
- Much better for RAG
- Enables table-aware retrieval

**Cons**
- Slower
- Higher compute cost

---

## Key Observations
- Layout-aware parsing produces **more elements**
- Metadata becomes richer (tables, titles, page context)
- Chunking quality improves downstream

---

## Takeaway for RAG Systems
For enterprise documents:
- PDFs should almost always use layout-aware parsing
- Image-heavy documents need preprocessing, not raw ingestion
- Parsing strategy directly impacts retrieval quality

This experiment feeds directly into:
- Metadata normalization
- Chunking strategy selection
- Embedding quality
