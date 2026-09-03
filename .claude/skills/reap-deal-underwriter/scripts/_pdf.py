"""Shared PDF helpers (text + embedded image extraction) via PyMuPDF.

PyMuPDF (import name `fitz`, package name `pymupdf`) is used instead of
pdfplumber deliberately -- it handles both text and embedded-image
extraction from a single dependency with no cffi/cryptography build chain,
which matters for a script students will run in whatever Python environment
they happen to have.
"""
import io

import fitz  # PyMuPDF


def open_pdf(pdf_bytes):
    return fitz.open(stream=pdf_bytes, filetype="pdf")


def page_texts(pdf_bytes):
    """Return a list of (page_number_1indexed, text) for every page."""
    doc = open_pdf(pdf_bytes)
    try:
        return [(i + 1, doc[i].get_text()) for i in range(doc.page_count)]
    finally:
        doc.close()


def extract_images(pdf_bytes, out_dir, pages=None, min_bytes=4000):
    """
    Extract embedded raster images from a PDF to out_dir.

    pages: optional iterable of 1-indexed page numbers to restrict to.
    min_bytes: skip tiny images (logos, bullet icons) that are never chart data.

    Returns a list of dicts: {page, index, path, width, height, format}.
    """
    import os

    os.makedirs(out_dir, exist_ok=True)
    doc = open_pdf(pdf_bytes)
    saved = []
    try:
        page_range = range(doc.page_count) if pages is None else [p - 1 for p in pages]
        for page_index in page_range:
            if page_index < 0 or page_index >= doc.page_count:
                continue
            page = doc[page_index]
            for img_index, img in enumerate(page.get_images(full=True)):
                xref = img[0]
                try:
                    base = doc.extract_image(xref)
                except Exception:
                    continue
                image_bytes = base["image"]
                if len(image_bytes) < min_bytes:
                    continue
                ext = base.get("ext", "png")
                filename = f"page{page_index + 1:03d}_img{img_index:02d}.{ext}"
                path = os.path.join(out_dir, filename)
                with open(path, "wb") as f:
                    f.write(image_bytes)
                saved.append(
                    {
                        "page": page_index + 1,
                        "index": img_index,
                        "path": path,
                        "width": base.get("width"),
                        "height": base.get("height"),
                        "format": ext,
                    }
                )
    finally:
        doc.close()
    return saved


def render_page_png(pdf_bytes, page_number, out_path, zoom=2.0):
    """
    Render a full page to PNG (fallback for vector/chart-drawn figures that
    aren't embedded raster images PyMuPDF's get_images() can see).
    """
    doc = open_pdf(pdf_bytes)
    try:
        page = doc[page_number - 1]
        pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom))
        pix.save(out_path)
        return out_path
    finally:
        doc.close()
