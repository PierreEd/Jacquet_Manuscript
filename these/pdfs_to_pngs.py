#!/usr/bin/env python3
"""
Recursively convert all PDFs under a root directory to 300-dpi PNGs.

Output layout (default):
  - For /path/to/root/sub/dir/file.pdf
  - PNGs go to /path/to/root/sub/dir/file_png/file_p001.png, file_p002.png, ...

Install:
  pip install pymupdf
"""

from __future__ import annotations
from pathlib import Path
import sys

import fitz  # PyMuPDF


DPI = 300
# PyMuPDF renders at 72 dpi by default; scale factor = DPI / 72
SCALE = DPI / 72.0


def pdf_to_pngs(pdf_path: Path, out_mode: str = "sibling_folder") -> None:
    """
    Convert one PDF to PNGs at DPI.
    out_mode:
      - "sibling_folder": create a folder next to the PDF: <stem>_png/
      - "same_folder": put PNGs next to PDF (can clutter)
    """
    if out_mode == "sibling_folder":
        out_dir = pdf_path.with_name(f"{pdf_path.stem}_png")
    elif out_mode == "same_folder":
        out_dir = pdf_path.parent
    else:
        raise ValueError("out_mode must be 'sibling_folder' or 'same_folder'")

    out_dir.mkdir(parents=True, exist_ok=True)

    doc = fitz.open(pdf_path)
    mat = fitz.Matrix(SCALE, SCALE)

    for i in range(doc.page_count):
        page = doc.load_page(i)
        pix = page.get_pixmap(matrix=mat, alpha=False)  # alpha=False => opaque PNG
        out_file = out_dir / f"{pdf_path.stem}_p{i+1:03d}.png"
        pix.save(out_file)

    doc.close()


def main(root: Path) -> int:
    if not root.exists():
        print(f"Error: root path does not exist: {root}", file=sys.stderr)
        return 2

    pdfs = sorted(root.rglob("*.pdf"))
    if not pdfs:
        print(f"No PDFs found under: {root}")
        return 0

    print(f"Found {len(pdfs)} PDFs under {root}")
    for pdf in pdfs:
        try:
            print(f"Converting: {pdf}")
            pdf_to_pngs(pdf, out_mode="sibling_folder")
        except Exception as e:
            print(f"  FAILED: {pdf} -> {e}", file=sys.stderr)

    print("Done.")
    return 0


if __name__ == "__main__":
    # Usage: python pdfs_to_pngs.py /path/to/root
    root_dir = Path(sys.argv[1]).expanduser().resolve() if len(sys.argv) > 1 else Path.cwd()
    raise SystemExit(main(root_dir))
