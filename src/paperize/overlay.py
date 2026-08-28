"""Generate and append vector paper overlays to PDF pages."""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import TYPE_CHECKING

import pikepdf

if TYPE_CHECKING:
    from collections.abc import Iterable

    from paperize.config import UnitAmount
    from paperize.presets import PaperPreset, RgbColor

PAGE_BOX_SIZE = 4
VIGNETTE_RADIUS = 0.5
VIGNETTE_TRANSITION_CENTER = 0.68
VIGNETTE_TRANSITION_JITTER = 0.06


@dataclass(frozen=True, slots=True)
class OverlayStyle:
    """Resolved visual settings shared by every page in a document."""

    preset: PaperPreset
    strength: UnitAmount
    texture: UnitAmount
    vignette: UnitAmount


def apply_overlay(
    pdf: pikepdf.Pdf,
    page: pikepdf.Page,
    *,
    page_index: int,
    style: OverlayStyle,
) -> None:
    """Append an isolated warm-paper overlay to one page."""
    cropbox = tuple(float(value) for value in page.cropbox)
    if len(cropbox) != PAGE_BOX_SIZE:
        msg = "page crop box must contain four coordinates"
        raise ValueError(msg)

    page.contents_add(b"q\n", prepend=True)
    stream_parts = ["Q\nq\n"]
    stream_parts.extend(
        _paper_layer(
            page,
            cropbox=cropbox,
            page_index=page_index,
            style=style,
        )
    )
    stream_parts.extend(
        _texture_layer(
            page,
            cropbox=cropbox,
            page_index=page_index,
            style=style,
        )
    )
    stream_parts.append("Q\n")
    page.contents_add(pdf.make_stream("".join(stream_parts).encode("ascii")))


def _paper_layer(
    page: pikepdf.Page,
    *,
    cropbox: tuple[float, ...],
    page_index: int,
    style: OverlayStyle,
) -> Iterable[str]:
    state = _add_graphics_state(
        page,
        style.strength.value,
        blend_mode="/Multiply",
        prefix="PprPaperState",
    )
    if style.vignette.value == 0:
        return (
            f"{state} gs\n",
            f"{_rgb(style.preset.paper)} rg\n",
            f"{_rectangle(cropbox)} re f\n",
        )

    edge = _mix_color(
        style.preset.paper,
        style.preset.vignette_edge,
        style.vignette.value,
    )
    shading = _add_paper_shading(
        page,
        style.preset.paper,
        edge,
        transition_start=_vignette_transition_start(style.preset, page_index),
    )
    return _paper_shading_commands(
        cropbox,
        state_name=str(state),
        shading_name=str(shading),
    )


def _texture_layer(
    page: pikepdf.Page,
    *,
    cropbox: tuple[float, ...],
    page_index: int,
    style: OverlayStyle,
) -> Iterable[str]:
    if style.texture.value == 0:
        return ()
    opacity = min(0.10, 0.06 * style.texture.value * style.strength.value)
    state = _add_graphics_state(page, opacity, prefix="PprTexture")
    return _texture_commands(
        cropbox,
        state_name=str(state),
        color=style.preset.texture_ink,
        seed=style.preset.texture_seed + page_index,
        amount=style.texture,
    )


def _add_graphics_state(
    page: pikepdf.Page,
    opacity: float,
    *,
    blend_mode: str = "/Multiply",
    prefix: str,
) -> pikepdf.Name:
    state = pikepdf.Dictionary(
        Type=pikepdf.Name("/ExtGState"),
        BM=pikepdf.Name(blend_mode),
        CA=opacity,
        ca=opacity,
    )
    return page.add_resource(
        state,
        pikepdf.Name("/ExtGState"),
        prefix=prefix,
        replace_existing=False,
    )


def _add_paper_shading(
    page: pikepdf.Page,
    center: RgbColor,
    edge: tuple[float, float, float],
    *,
    transition_start: float,
) -> pikepdf.Name:
    flat_center = pikepdf.Dictionary(
        FunctionType=2,
        Domain=pikepdf.Array([0.0, 1.0]),
        C0=pikepdf.Array([center.red, center.green, center.blue]),
        C1=pikepdf.Array([center.red, center.green, center.blue]),
        N=1.0,
    )
    edge_falloff = pikepdf.Dictionary(
        FunctionType=2,
        Domain=pikepdf.Array([0.0, 1.0]),
        C0=pikepdf.Array([center.red, center.green, center.blue]),
        C1=pikepdf.Array(edge),
        N=1.35,
    )
    function = pikepdf.Dictionary(
        FunctionType=3,
        Domain=pikepdf.Array([0.0, 1.0]),
        Functions=pikepdf.Array([flat_center, edge_falloff]),
        Bounds=pikepdf.Array([transition_start]),
        Encode=pikepdf.Array([0.0, 1.0, 0.0, 1.0]),
    )
    shading = pikepdf.Dictionary(
        ShadingType=3,
        ColorSpace=pikepdf.Name("/DeviceRGB"),
        Coords=pikepdf.Array([0.5, 0.5, 0.0, 0.5, 0.5, VIGNETTE_RADIUS]),
        Function=function,
        Extend=pikepdf.Array([True, True]),
    )
    return page.add_resource(
        shading,
        pikepdf.Name("/Shading"),
        prefix="PprPaper",
        replace_existing=False,
    )


def _vignette_transition_start(preset: PaperPreset, page_index: int) -> float:
    """Return a stable per-page boundary for the edge vignette."""
    rng = random.Random(  # noqa: S311 - visual variation, not cryptography
        preset.texture_seed * 7 + page_index
    )
    return VIGNETTE_TRANSITION_CENTER + rng.uniform(
        -VIGNETTE_TRANSITION_JITTER,
        VIGNETTE_TRANSITION_JITTER,
    )


def _paper_shading_commands(
    cropbox: tuple[float, ...],
    *,
    state_name: str,
    shading_name: str,
) -> Iterable[str]:
    x0, y0, x1, y1 = cropbox
    width = x1 - x0
    height = y1 - y0
    yield "q\n"
    yield f"{state_name} gs\n"
    yield f"{_rectangle(cropbox)} re W n\n"
    yield f"{width:.4f} 0 0 {height:.4f} {x0:.4f} {y0:.4f} cm\n"
    yield f"{shading_name} sh\n"
    yield "Q\n"


def _texture_commands(
    cropbox: tuple[float, ...],
    *,
    state_name: str,
    color: RgbColor,
    seed: int,
    amount: UnitAmount,
) -> Iterable[str]:
    x0, y0, x1, y1 = cropbox
    width = x1 - x0
    height = y1 - y0
    count = max(12, round(110 * amount.value))
    rng = random.Random(seed)  # noqa: S311 - visual texture, not cryptography

    yield f"{state_name} gs\n"
    yield f"{_rgb(color)} RG\n"
    for _index in range(count):
        x = x0 + rng.random() * width
        y = y0 + rng.random() * height
        length = 4.0 + rng.random() * 18.0
        rise = rng.uniform(-0.7, 0.7)
        line_width = 0.12 + rng.random() * 0.28
        yield (
            f"{line_width:.3f} w {x:.3f} {y:.3f} m "
            f"{min(x + length, x1):.3f} {min(max(y + rise, y0), y1):.3f} l S\n"
        )


def _mix_color(
    center: RgbColor,
    edge: RgbColor,
    amount: float,
) -> tuple[float, float, float]:
    return (
        center.red + (edge.red - center.red) * amount,
        center.green + (edge.green - center.green) * amount,
        center.blue + (edge.blue - center.blue) * amount,
    )


def _rgb(color: RgbColor) -> str:
    return _rgb_tuple((color.red, color.green, color.blue))


def _rgb_tuple(color: tuple[float, float, float]) -> str:
    red, green, blue = color
    return f"{red:.6f} {green:.6f} {blue:.6f}"


def _rectangle(cropbox: tuple[float, ...]) -> str:
    x0, y0, x1, y1 = cropbox
    return f"{x0:.4f} {y0:.4f} {x1 - x0:.4f} {y1 - y0:.4f}"
