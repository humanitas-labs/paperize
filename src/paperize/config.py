"""Validated Paperize configuration types."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from paperize.errors import OutputPathError

if TYPE_CHECKING:
    from pathlib import Path


@dataclass(frozen=True, slots=True)
class UnitAmount:
    """A finite numeric amount constrained to the inclusive range 0 through 1."""

    value: float

    def __post_init__(self) -> None:
        """Reject values outside the supported range."""
        if not 0.0 <= self.value <= 1.0:
            msg = f"expected a value between 0 and 1, got {self.value}"
            raise ValueError(msg)


@dataclass(frozen=True, slots=True)
class TransformRequest:
    """A fully resolved request to transform one PDF."""

    source: Path
    output: Path
    preset_name: str
    strength: UnitAmount
    texture: UnitAmount | None
    vignette: UnitAmount | None = None
    force: bool = False

    def validate_paths(self) -> None:
        """Validate source and destination invariants before opening the PDF."""
        if self.source.suffix.lower() != ".pdf":
            msg = f"source is not a PDF: {self.source}"
            raise OutputPathError(msg)
        if self.source.resolve() == self.output.resolve():
            msg = "output must not overwrite the source PDF"
            raise OutputPathError(msg)
        if not self.output.parent.is_dir():
            msg = f"output directory does not exist: {self.output.parent}"
            raise OutputPathError(msg)
        if self.output.exists() and not self.force:
            msg = f"output already exists: {self.output} (use --force to replace it)"
            raise OutputPathError(msg)


def default_output_path(source: Path) -> Path:
    """Return the conventional output path for a source PDF."""
    return source.with_name(f"{source.stem}-paperized.pdf")
