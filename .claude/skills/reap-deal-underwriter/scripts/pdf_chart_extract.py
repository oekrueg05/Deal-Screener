#!/usr/bin/env python3
"""
pdf_chart_extract.py -- pull chart/graphic images out of a PDF report so a
figure that only exists as a chart (not extractable text) can actually be
read, instead of getting silently dropped or blended with a proxy number.

Concrete motivating case: Marcus & Millichap's Milwaukee multifamily
investment forecast report has real per-market cap rate data, but the
number lives in a chart graphic, not in the PDF's extractable text layer.

This script does the *mechanical* extraction only -- it does not try to read
the chart's values itself. The calling assistant (already multimodal) should
`Read` the saved image file(s) directly to read the axis labels and data
points, the same way it would look at a screenshot. That's deliberately
simpler and more reliable than routing through a second vision-API call from
inside the script.

Usage:
    python pdf_chart_extract.py --url "https://.../report.pdf" --out-dir /tmp/charts
    python pdf_chart_extract.py --file ./report.pdf --pages 4,7 --out-dir /tmp/charts
    python pdf_chart_extract.py --file ./report.pdf --render-pages 4 --out-dir /tmp/charts

--pages restricts embedded-image extraction to specific 1-indexed pages
(omit to scan the whole document). --render-pages additionally rasterizes
whole pages to PNG -- use this when a chart is drawn with vector graphics
rather than an embedded raster image, so get_images() finds nothing on that
page but the chart is still visually there.
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from _http import VerificationError, emit, fail, get_bytes, now_iso  # noqa: E402
from _pdf import extract_images, page_texts, render_page_png  # noqa: E402


def parse_pages(spec):
    if not spec:
        return None
    return sorted({int(p.strip()) for p in spec.split(",") if p.strip()})


def load_pdf_bytes(args):
    if args.file:
        with open(args.file, "rb") as f:
            return f.read()
    return get_bytes(args.url)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--url", help="URL of the PDF to fetch")
    source.add_argument("--file", help="Local path to an already-downloaded PDF")
    parser.add_argument("--out-dir", required=True, help="Directory to save extracted images into")
    parser.add_argument("--pages", default=None, help="Comma-separated 1-indexed pages to restrict embedded-image extraction to (default: all pages)")
    parser.add_argument("--render-pages", default=None, help="Comma-separated 1-indexed pages to additionally rasterize whole-page as PNG (for vector-drawn charts)")
    parser.add_argument("--min-bytes", type=int, default=4000, help="Skip embedded images smaller than this (logos/icons); default 4000")
    args = parser.parse_args(argv)

    try:
        pdf_bytes = load_pdf_bytes(args)
    except VerificationError as exc:
        fail(str(exc), url=args.url)
        return
    except OSError as exc:
        fail(f"could not read local file '{args.file}': {exc}")
        return

    if not pdf_bytes.startswith(b"%PDF"):
        fail(
            "fetched content is not a PDF (no %PDF header) -- the URL may have "
            "returned an HTML landing/paywall page instead of the file",
            url=args.url,
        )
        return

    pages = parse_pages(args.pages)
    render_pages = parse_pages(args.render_pages)

    images = extract_images(pdf_bytes, args.out_dir, pages=pages, min_bytes=args.min_bytes)

    rendered = []
    if render_pages:
        for page_num in render_pages:
            out_path = os.path.join(args.out_dir, f"page{page_num:03d}_full.png")
            try:
                render_page_png(pdf_bytes, page_num, out_path)
                rendered.append({"page": page_num, "path": out_path})
            except Exception as exc:  # noqa: BLE001 - report and continue
                rendered.append({"page": page_num, "error": str(exc)})

    texts = page_texts(pdf_bytes)
    pages_with_little_text = [
        page_num for page_num, text in texts if (pages is None or page_num in pages) and len(text.strip()) < 40
    ]

    result = {
        "source": args.url or args.file,
        "retrieved_at": now_iso(),
        "page_count": len(texts),
        "embedded_images_extracted": images,
        "rendered_pages": rendered,
        "pages_with_little_extractable_text": pages_with_little_text,
        "next_step": (
            "Read() the saved image file(s) listed above to read the chart's axis "
            "labels and data values directly -- this script only extracts them, "
            "it does not interpret them."
        ),
    }

    if not images and not rendered:
        result["note"] = (
            "No embedded raster images found (and no --render-pages given). If the "
            "chart is drawn with vector graphics rather than an embedded image, "
            "re-run with --render-pages <page> to rasterize the whole page instead."
        )

    emit(result)


if __name__ == "__main__":
    main()
