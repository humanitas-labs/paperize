"""End-to-end tests for the PDF transformation pipeline."""

from pathlib import Path

import pikepdf
import pymupdf

from paperize.config import TransformRequest, UnitAmount
from paperize.inspect import PAPERIZE_INFO_KEY, snapshot_structure
from paperize.pdf import paperize


def test_paperize_preserves_document_structure(source_pdf: Path) -> None:
    """The overlay changes presentation without changing protected structure."""
    output = source_pdf.with_name("output.pdf")
    source_bytes = source_pdf.read_bytes()
    with pikepdf.Pdf.open(source_pdf) as source:
        expected_structure = snapshot_structure(source)

    completed = paperize(_request(source_pdf, output))

    assert completed == output
    assert output.exists()
    assert source_pdf.read_bytes() == source_bytes
    with pikepdf.Pdf.open(output) as written:
        assert snapshot_structure(written) == expected_structure
        assert str(written.docinfo[PAPERIZE_INFO_KEY]) == "paperize-pdf 0.2.0"


def test_paperize_preserves_text_links_and_outlines(source_pdf: Path) -> None:
    """User-visible navigation and selectable text survive transformation."""
    output = source_pdf.with_name("output.pdf")
    paperize(_request(source_pdf, output))

    with pymupdf.open(source_pdf) as source, pymupdf.open(output) as written:
        assert len(written) == len(source)
        assert [page.get_text() for page in written] == [
            page.get_text() for page in source
        ]
        assert written.get_toc() == source.get_toc()
        assert _semantic_links(written[0]) == _semantic_links(source[0])
        assert _annotation_count(written[0]) == _annotation_count(source[0])


def _request(source: Path, output: Path) -> TransformRequest:
    return TransformRequest(
        source=source,
        output=output,
        preset_name="parchment",
        strength=UnitAmount(1.0),
        texture=UnitAmount(0.0),
    )


def _annotation_count(page: pymupdf.Page) -> int:
    return len(list(page.annots() or ()))


def _semantic_links(page: pymupdf.Page) -> list[dict[str, object]]:
    return [
        {key: value for key, value in link.items() if key != "xref"}
        for link in page.get_links()
    ]
