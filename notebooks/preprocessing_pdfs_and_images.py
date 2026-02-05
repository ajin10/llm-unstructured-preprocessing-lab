"""
04_preprocessing_pdfs_and_images.py

Goal:
- Parse PDFs using different strategies (basic vs layout-aware)
- Inspect how images, tables, and layout affect extracted elements
- Produce clean element artifacts for downstream normalization + chunking
"""

import json
from unstructured.partition.pdf import partition_pdf
from unstructured.partition.html import partition_html


# -----------------------------
# PDF parsing strategies
# -----------------------------

def parse_pdf_basic(path: str):
    return partition_pdf(
        filename=path,
        strategy="fast"
    )


def parse_pdf_layout_aware(path: str):
    return partition_pdf(
        filename=path,
        strategy="hi_res",
        infer_table_structure=True
    )


# -----------------------------
# Demo run
# -----------------------------

if __name__ == "__main__":
    pdf_path = "data/sample_pdf.pdf"

    basic_elements = parse_pdf_basic(pdf_path)
    layout_elements = parse_pdf_layout_aware(pdf_path)

    print("Basic elements:", len(basic_elements))
    print("Layout-aware elements:", len(layout_elements))

    # Save for inspection / later chunking
    with open("data/pdf_elements_basic.json", "w") as f:
        json.dump([e.to_dict() for e in basic_elements], f, indent=2)

    with open("data/pdf_elements_layout.json", "w") as f:
        json.dump([e.to_dict() for e in layout_elements], f, indent=2)
