"""Rendering tests for the paper overlay."""

from pathlib import Path

import pymupdf
import pytest

from paperize.config import TransformRequest, UnitAmount
from paperize.overlay import (
    VIGNETTE_TRANSITION_CENTER,
    VIGNETTE_TRANSITION_JITTER,
    _vignette_transition_start,
)
from paperize.pdf import paperize
from paperize.presets import get_preset

MAX_WARM_BLUE = 245
PARCHMENT_CENTER = (250, 237, 219)
PARCHMENT_EDGE = (255, 230, 195)


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


def test_parchment_uses_exact_center_and_edge_colors(source_pdf: Path) -> None:
    """Default parchment lands on the requested radial color endpoints."""
    output = source_pdf.with_name("endpoints.pdf")
    paperize(
        TransformRequest(
            source=source_pdf,
            output=output,
            preset_name="parchment",
            strength=UnitAmount(1.0),
            texture=UnitAmount(0.0),
            vignette=UnitAmount(1.0),
        )
    )

    assert _near(_pixel(output, x=306, y=396), PARCHMENT_CENTER)
    assert _near(_pixel(output, x=150, y=396), PARCHMENT_CENTER)
    assert _near(_pixel(output, x=5, y=396), PARCHMENT_EDGE)


def test_black_marks_keep_their_original_color(source_pdf: Path) -> None:
    """Paper treatment does not recolor the document's dark content."""
    output = source_pdf.with_name("original-ink.pdf")
    paperize(
        TransformRequest(
            source=source_pdf,
            output=output,
            preset_name="parchment",
            strength=UnitAmount(1.0),
            texture=UnitAmount(0.0),
            vignette=UnitAmount(1.0),
        )
    )

    assert _pixel(output, x=300, y=225) == _pixel(source_pdf, x=300, y=225)


def test_vignette_size_varies_deterministically_by_page() -> None:
    """Edge falloff varies naturally by page but remains reproducible."""
    preset = get_preset("parchment")
    first = _vignette_transition_start(preset, 0)
    repeated = _vignette_transition_start(preset, 0)
    second = _vignette_transition_start(preset, 1)

    assert first == repeated
    assert first != second
    assert first >= VIGNETTE_TRANSITION_CENTER - VIGNETTE_TRANSITION_JITTER
    assert first <= VIGNETTE_TRANSITION_CENTER + VIGNETTE_TRANSITION_JITTER


def _pixel(path: Path, *, x: int, y: int) -> tuple[int, int, int]:
    with pymupdf.open(path) as document:
        pixmap = document[0].get_pixmap(alpha=False)
        red, green, blue = pixmap.pixel(x, y)[:3]
    return red, green, blue


def _near(
    actual: tuple[int, int, int],
    expected: tuple[int, int, int],
    tolerance: int = 2,
) -> bool:
    return all(
        abs(actual_channel - expected_channel) <= tolerance
        for actual_channel, expected_channel in zip(actual, expected, strict=True)
    )
