"""Generate and append vector paper overlays to PDF pages."""

from __future__ import annotations

import random
from typing import TYPE_CHECKING

import pikepdf

if TYPE_CHECKING:
    from collections.abc import Iterable

    from paperize.config import UnitAmount
    from paperize.presets import PaperPreset, RgbColor

PAGE_BOX_SIZE = 4


def apply_overlay(
    pdf: pikepdf.Pdf,
    page: pikepdf.Page,
    *,
    page_index: int,
    preset: PaperPreset,
    strength: UnitAmount,
    texture: UnitAmount,
) -> None:
    """Append an isolated warm-paper overlay to one page."""
    paper_opacity = preset.base_opacity.value * strength.value
    paper_state = _add_graphics_state(page, paper_opacity, prefix="PprPaper")
    cropbox = tuple(float(value) for value in page.cropbox)
    if len(cropbox) != PAGE_BOX_SIZE:
        msg = "page crop box must contain four coordinates"
        raise ValueError(msg)

    page.contents_add(b"q\n", prepend=True)
    stream_parts = [
        "Q\nq\n",
        f"{paper_state} gs\n",
        f"{_rgb(preset.paper)} rg\n",
        f"{_rectangle(cropbox)} re f\n",
    ]
    if texture.value > 0:
        texture_opacity = min(0.10, 0.06 * texture.value * strength.value)
        texture_state = _add_graphics_state(page, texture_opacity, prefix="PprTexture")
        stream_parts.extend(
            _texture_commands(
                cropbox,
                state_name=str(texture_state),
                color=preset.texture_ink,
                seed=preset.texture_seed + page_index,
                amount=texture,
            )
        )
    stream_parts.append("Q\n")
    page.contents_add(pdf.make_stream("".join(stream_parts).encode("ascii")))


def _add_graphics_state(
    page: pikepdf.Page, opacity: float, *, prefix: str
) -> pikepdf.Name:
    state = pikepdf.Dictionary(
        Type=pikepdf.Name("/ExtGState"),
        BM=pikepdf.Name("/Multiply"),
        CA=opacity,
        ca=opacity,
    )
    return page.add_resource(
        state,
        pikepdf.Name("/ExtGState"),
        prefix=prefix,
        replace_existing=False,
    )


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


def _rgb(color: RgbColor) -> str:
    return f"{color.red:.4f} {color.green:.4f} {color.blue:.4f}"


def _rectangle(cropbox: tuple[float, ...]) -> str:
    x0, y0, x1, y1 = cropbox
    return f"{x0:.4f} {y0:.4f} {x1 - x0:.4f} {y1 - y0:.4f}"
