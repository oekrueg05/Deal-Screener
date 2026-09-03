import json
import os

import pytest

import pdf_chart_extract

FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")


def load_bytes(name):
    with open(os.path.join(FIXTURES, name), "rb") as f:
        return f.read()


def test_parse_pages():
    assert pdf_chart_extract.parse_pages("4,7,2") == [2, 4, 7]
    assert pdf_chart_extract.parse_pages(None) is None
    assert pdf_chart_extract.parse_pages("") is None


def test_extracts_embedded_chart_image_from_url(monkeypatch, tmp_path, capsys):
    pdf_bytes = load_bytes("report_with_chart_image.pdf")
    monkeypatch.setattr(pdf_chart_extract, "get_bytes", lambda url: pdf_bytes)

    pdf_chart_extract.main(
        ["--url", "https://example.com/report.pdf", "--out-dir", str(tmp_path), "--min-bytes", "100"]
    )
    out = json.loads(capsys.readouterr().out)

    assert out["page_count"] == 2
    assert len(out["embedded_images_extracted"]) == 1
    img = out["embedded_images_extracted"][0]
    assert img["page"] == 1
    assert os.path.exists(img["path"])
    # page 2 has real text, so it shouldn't show up as "little extractable text"
    assert 2 not in out["pages_with_little_extractable_text"]


def test_extracts_from_local_file(tmp_path, capsys):
    pdf_path = os.path.join(FIXTURES, "report_with_chart_image.pdf")
    pdf_chart_extract.main(
        ["--file", pdf_path, "--out-dir", str(tmp_path), "--pages", "1", "--min-bytes", "100"]
    )
    out = json.loads(capsys.readouterr().out)
    assert len(out["embedded_images_extracted"]) == 1
    assert out["embedded_images_extracted"][0]["page"] == 1


def test_non_pdf_content_fails_loudly(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(pdf_chart_extract, "get_bytes", lambda url: b"<html>not a pdf</html>")
    with pytest.raises(SystemExit) as exc_info:
        pdf_chart_extract.main(["--url", "https://example.com/oops", "--out-dir", str(tmp_path)])
    assert exc_info.value.code == 1
    err = json.loads(capsys.readouterr().err)
    assert "not a PDF" in err["error"]


def test_no_images_found_notes_render_pages_fallback(tmp_path, capsys):
    # page 2 of the fixture has no embedded image
    pdf_path = os.path.join(FIXTURES, "report_with_chart_image.pdf")
    pdf_chart_extract.main(
        ["--file", pdf_path, "--out-dir", str(tmp_path), "--pages", "2"]
    )
    out = json.loads(capsys.readouterr().out)
    assert out["embedded_images_extracted"] == []
    assert "render-pages" in out["note"]
