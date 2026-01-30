"""
02_parsing_html_pptx_pdf.py

Goal:
- Parse HTML + PPTX locally with `unstructured`
- Parse PDF with Unstructured API (hi_res + table inference)

Notes:
- Local parsing requires: unstructured
- PDF hi_res via API requires: unstructured-client + API key + URL
"""

import os
import json
import warnings

warnings.filterwarnings("ignore")

# ---- Local parsers (HTML / PPTX) ----
from unstructured.partition.html import partition_html
from unstructured.partition.pptx import partition_pptx

# ---- API client (PDF hi_res) ----
from unstructured_client import UnstructuredClient
from unstructured_client.models import shared
from unstructured_client.models.errors import SDKError


def dump_elements(elements, limit=None):
    """Convert Unstructured elements to JSON-friendly dicts and pretty print."""
    if hasattr(elements[0], "to_dict"):
        element_dicts = [el.to_dict() for el in elements]
    else:
        # API returns dict-like elements already
        element_dicts = elements

    if limit is not None:
        element_dicts = element_dicts[:limit]

    print(json.dumps(element_dicts, indent=2))


def parse_html_local(path: str):
    elements = partition_html(filename=path)
    print(f"\n[HTML] Parsed {len(elements)} elements from: {path}")
    dump_elements(elements, limit=5)


def parse_pptx_local(path: str):
    elements = partition_pptx(filename=path)
    print(f"\n[PPTX] Parsed {len(elements)} elements from: {path}")
    dump_elements(elements, limit=5)


def parse_pdf_via_api(path: str):
    api_key = os.environ.get("UNSTRUCTURED_API_KEY")
    api_url = os.environ.get("UNSTRUCTURED_API_URL")

    if not api_key or not api_url:
        raise RuntimeError(
            "Missing UNSTRUCTURED_API_KEY or UNSTRUCTURED_API_URL env vars.\n"
            "Set them before running:\n"
            "  export UNSTRUCTURED_API_KEY='...'\n"
            "  export UNSTRUCTURED_API_URL='...'\n"
        )

    client = UnstructuredClient(
        api_key_auth=api_key,
        server_url=api_url,
    )

    with open(path, "rb") as f:
        files = shared.Files(
            content=f.read(),
            file_name=os.path.basename(path),
        )

    req = shared.PartitionParameters(
        files=files,
        strategy="hi_res",
        pdf_infer_table_structure=True,
        languages=["eng"],
    )

    try:
        resp = client.general.partition(req)
        elements = resp.elements or []
        print(f"\n[PDF/API] Parsed {len(elements)} elements from: {path}")
        dump_elements(elements, limit=5)
    except SDKError as e:
        print("\n[PDF/API] Unstructured API call failed:")
        print(e)


if __name__ == "__main__":
    # Put your sample files here (keep them small / non-sensitive)
    # Recommended repo layout:
    #   data/sample.html
    #   data/sample.pptx
    #   data/sample.pdf
    html_path = "data/sample.html"
    pptx_path = "data/sample.pptx"
    pdf_path = "data/sample.pdf"

    if os.path.exists(html_path):
        parse_html_local(html_path)
    else:
        print(f"\n[SKIP] HTML file not found: {html_path}")

    if os.path.exists(pptx_path):
        parse_pptx_local(pptx_path)
    else:
        print(f"\n[SKIP] PPTX file not found: {pptx_path}")

    if os.path.exists(pdf_path):
        # Only runs if you set env vars + have a pdf
        parse_pdf_via_api(pdf_path)
    else:
        print(f"\n[SKIP] PDF file not found: {pdf_path}")
