"""Rendering tests for the paper overlay."""

from pathlib import Path

import pymupdf
import pytest

from paperize.config import TransformRequest, UnitAmount
from paperize.pdf import paperize

MAX_WARM_BLUE = 245


@pytest.mark.parametrize("preset", ["cream", "parchment", "sepia"])
def test_presets_warm_neutral_background(source_pdf: Path, preset: str) -> None:
    """Every preset turns white into a warm, non-neutral background."""
    output = source_pdf.with_name(f"{preset}.pdf")
    paperize(
        TransformRequest(
            source=source_pdf,
            output=output,
            preset_name=preset,
            strength=UnitAmount(1.0),
            texture=UnitAmount(0.0),
        )
    )

    source_pixel = _pixel(source_pdf, x=300, y=400)
    output_pixel = _pixel(output, x=300, y=400)

    assert source_pixel == (255, 255, 255)
    assert output_pixel[0] > output_pixel[1] > output_pixel[2]
    assert output_pixel[2] < MAX_WARM_BLUE


def test_zero_strength_is_visually_neutral(source_pdf: Path) -> None:
    """Strength zero provides a useful no-effect boundary."""
    output = source_pdf.with_name("neutral.pdf")
    paperize(
        TransformRequest(
            source=source_pdf,
            output=output,
            preset_name="parchment",
            strength=UnitAmount(0.0),
            texture=UnitAmount(0.0),
        )
    )
    assert _pixel(output, x=300, y=400) == _pixel(source_pdf, x=300, y=400)


def _pixel(path: Path, *, x: int, y: int) -> tuple[int, int, int]:
    with pymupdf.open(path) as document:
        pixmap = document[0].get_pixmap(alpha=False)
        red, green, blue = pixmap.pixel(x, y)[:3]
    return red, green, blue
