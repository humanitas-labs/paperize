"""Rendering tests for the paper overlay."""

from pathlib import Path

import pikepdf
import pymupdf
import pytest

from paperize.config import TransformRequest, UnitAmount
from paperize.overlay import (
    VIGNETTE_RADIUS,
    VIGNETTE_WIDTH_JITTER_RATIO,
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
    width = UnitAmount(0.32)
    first = _vignette_transition_start(preset, 0, width)
    repeated = _vignette_transition_start(preset, 0, width)
    second = _vignette_transition_start(preset, 1, width)
    rendered_width = 1.0 - first

    assert first == repeated
    assert first != second
    assert rendered_width >= width.value * (1.0 - VIGNETTE_WIDTH_JITTER_RATIO)
    assert rendered_width <= width.value * (1.0 + VIGNETTE_WIDTH_JITTER_RATIO)


def test_narrower_vignette_width_moves_transition_toward_edge() -> None:
    """A smaller width leaves more of the page at the flat center color."""
    preset = get_preset("parchment")
    narrow = _vignette_transition_start(preset, 0, UnitAmount(0.12))
    default = _vignette_transition_start(preset, 0, UnitAmount(0.32))

    assert narrow > default
    assert narrow >= 0.85


def test_zero_vignette_width_uses_uniform_center_color(source_pdf: Path) -> None:
    """Width zero removes the edge transition without changing paper color."""
    output = source_pdf.with_name("zero-width.pdf")
    paperize(
        TransformRequest(
            source=source_pdf,
            output=output,
            preset_name="parchment",
            strength=UnitAmount(1.0),
            texture=UnitAmount(0.0),
            vignette=UnitAmount(1.0),
            vignette_width=UnitAmount(0.0),
        )
    )

    assert _near(_pixel(output, x=306, y=396), PARCHMENT_CENTER)
    assert _near(_pixel(output, x=5, y=396), PARCHMENT_CENTER)


def test_narrow_vignette_uses_concentric_radial_geometry(source_pdf: Path) -> None:
    """Narrow widths avoid stitched functions that some PDF viewers clip."""
    output = source_pdf.with_name("radial-geometry.pdf")
    paperize(
        TransformRequest(
            source=source_pdf,
            output=output,
            preset_name="parchment",
            strength=UnitAmount(1.0),
            texture=UnitAmount(0.0),
            vignette_width=UnitAmount(0.12),
        )
    )

    with pikepdf.Pdf.open(output) as document:
        shadings = document.pages[0].Resources.Shading
        shading = next(value for _name, value in shadings.items())
        coordinates = [float(value) for value in shading.Coords]

        assert int(shading.ShadingType) == 3
        assert int(shading.Function.FunctionType) == 2
        assert coordinates[2] > 0.4
        assert coordinates[5] == VIGNETTE_RADIUS


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
