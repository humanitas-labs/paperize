"""Generated PDF fixtures for Paperize tests."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pymupdf
import pytest

if TYPE_CHECKING:
    from pathlib import Path


@pytest.fixture
def source_pdf(tmp_path: Path) -> Path:
    """Create a representative born-digital PDF without external fixtures."""
    path = tmp_path / "source.pdf"
    document = pymupdf.open()

    first = document.new_page(width=612, height=792)
    first.insert_text((72, 96), "Paperize keeps this text selectable.", fontsize=18)
    first.draw_line((72, 116), (430, 116), color=(0.1, 0.1, 0.1), width=1)
    first.draw_rect(
        pymupdf.Rect(280, 200, 330, 250),
        color=(0.0, 0.0, 0.0),
        fill=(0.0, 0.0, 0.0),
    )
    first.insert_link(
        {
            "kind": pymupdf.LINK_URI,
            "from": pymupdf.Rect(72, 128, 220, 148),
            "uri": "https://example.com/paperize",
        }
    )
    first.add_text_annot((500, 96), "Preserve this note")

    second = document.new_page(width=792, height=612)
    second.insert_text((72, 96), "Landscape page", fontsize=18)
    second.set_rotation(90)

    document.set_toc([[1, "First page", 1], [1, "Second page", 2]])
    document.save(path)
    document.close()
    return path
