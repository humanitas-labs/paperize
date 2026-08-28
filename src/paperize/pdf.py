"""Orchestrate safe, verified PDF transformations."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING

import pikepdf

from paperize import __version__
from paperize.errors import InputPdfError, VerificationError
from paperize.inspect import PAPERIZE_INFO_KEY, inspect_safety, snapshot_structure
from paperize.overlay import OverlayStyle, apply_overlay
from paperize.presets import get_preset

if TYPE_CHECKING:
    from paperize.config import TransformRequest


def paperize(request: TransformRequest) -> Path:
    """Transform one PDF and atomically return the completed output path."""
    request.validate_paths()
    preset = get_preset(request.preset_name)
    texture = request.texture or preset.default_texture
    style = OverlayStyle(
        preset=preset,
        strength=request.strength,
        texture=texture,
        vignette=request.vignette or preset.default_vignette,
        vignette_width=(request.vignette_width or preset.default_vignette_width),
    )
    temporary = _temporary_output(request.output)

    try:
        with _open_pdf(request.source) as pdf:
            inspect_safety(pdf)
            expected = snapshot_structure(pdf)
            for page_index, page in enumerate(pdf.pages):
                apply_overlay(
                    pdf,
                    page,
                    page_index=page_index,
                    style=style,
                )
            pdf.docinfo[PAPERIZE_INFO_KEY] = f"paperize-pdf {__version__}"
            pdf.save(temporary)

        with _open_pdf(temporary) as written:
            actual = snapshot_structure(written)
            _verify_structure(actual, expected)
        temporary.replace(request.output)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise

    return request.output


def _open_pdf(path: Path) -> pikepdf.Pdf:
    try:
        return pikepdf.Pdf.open(path)
    except pikepdf.PasswordError as error:
        msg = f"cannot open encrypted PDF: {path}"
        raise InputPdfError(msg) from error
    except pikepdf.PdfError as error:
        msg = f"cannot read PDF: {path}: {error}"
        raise InputPdfError(msg) from error


def _temporary_output(output: Path) -> Path:
    descriptor, name = tempfile.mkstemp(
        dir=output.parent,
        prefix=f".{output.stem}-",
        suffix=".tmp.pdf",
    )
    os.close(descriptor)
    return Path(name)


def _verify_structure(actual: object, expected: object) -> None:
    if actual != expected:
        msg = "output changed protected document structure; no file was written"
        raise VerificationError(msg)
