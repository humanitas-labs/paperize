"""Inspect PDF safety boundaries and structural invariants."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, cast

import pikepdf

from paperize.errors import (
    AlreadyPaperizedError,
    SignedPdfError,
)

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator

PAGE_BOX_SIZE = 4

PAPERIZE_INFO_KEY = "/Paperize"


@dataclass(frozen=True, slots=True)
class PageStructure:
    """Page properties that Paperize promises not to change."""

    mediabox: tuple[float, float, float, float]
    cropbox: tuple[float, float, float, float]
    rotation: int
    annotation_count: int


@dataclass(frozen=True, slots=True)
class DocumentStructure:
    """Document properties used to verify a transformation."""

    pages: tuple[PageStructure, ...]
    has_outlines: bool
    has_acroform: bool
    has_names: bool
    field_count: int


def inspect_safety(pdf: pikepdf.Pdf) -> None:
    """Reject inputs whose security or history should not be rewritten."""
    if has_signature(pdf):
        msg = "the PDF contains a digital signature that rewriting would invalidate"
        raise SignedPdfError(msg)
    if PAPERIZE_INFO_KEY in pdf.docinfo:
        msg = "the PDF has already been paperized"
        raise AlreadyPaperizedError(msg)


def has_signature(pdf: pikepdf.Pdf) -> bool:
    """Return whether the AcroForm tree contains a signature field or value."""
    acroform = pdf.Root.get("/AcroForm")
    if acroform is None:
        return False
    fields = _as_fields(acroform.get("/Fields"))
    for field in _walk_fields(fields):
        if field.get("/FT") == pikepdf.Name("/Sig"):
            return True
        value = field.get("/V")
        if value is not None and value.get("/Type") == pikepdf.Name("/Sig"):
            return True
    return False


def snapshot_structure(pdf: pikepdf.Pdf) -> DocumentStructure:
    """Capture the structural properties protected by post-write verification."""
    page_structures = tuple(_snapshot_page(page) for page in pdf.pages)
    acroform = pdf.Root.get("/AcroForm")
    fields = () if acroform is None else _as_fields(acroform.get("/Fields"))
    return DocumentStructure(
        pages=page_structures,
        has_outlines=pdf.Root.get("/Outlines") is not None,
        has_acroform=acroform is not None,
        has_names=pdf.Root.get("/Names") is not None,
        field_count=sum(1 for _field in _walk_fields(fields)),
    )


def _snapshot_page(page: pikepdf.Page) -> PageStructure:
    return PageStructure(
        mediabox=_box_tuple(page.mediabox),
        cropbox=_box_tuple(page.cropbox),
        rotation=int(page.obj.get("/Rotate", 0)),
        annotation_count=len(page.obj.get("/Annots", [])),
    )


def _box_tuple(box: pikepdf.Array) -> tuple[float, float, float, float]:
    values = tuple(float(value) for value in box)
    if len(values) != PAGE_BOX_SIZE:
        msg = f"expected a four-value page box, got {len(values)}"
        raise ValueError(msg)
    left, bottom, right, top = values
    return left, bottom, right, top


def _walk_fields(fields: Iterable[pikepdf.Object]) -> Iterator[pikepdf.Object]:
    for field in fields:
        yield field
        kids = _as_fields(field.get("/Kids"))
        yield from _walk_fields(kids)


def _as_fields(value: pikepdf.Object | None) -> Iterable[pikepdf.Object]:
    if value is None:
        return ()
    return cast("Iterable[pikepdf.Object]", value)
