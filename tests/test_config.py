"""Tests for validated Paperize configuration."""

from pathlib import Path

import pytest

from paperize.config import TransformRequest, UnitAmount, default_output_path
from paperize.errors import OutputPathError


@pytest.mark.parametrize("value", [0.0, 0.5, 1.0])
def test_unit_amount_accepts_closed_unit_interval(value: float) -> None:
    """Boundary and interior values are valid."""
    assert UnitAmount(value).value == value


@pytest.mark.parametrize("value", [-0.01, 1.01])
def test_unit_amount_rejects_values_outside_interval(value: float) -> None:
    """Out-of-range values fail immediately."""
    with pytest.raises(ValueError, match="between 0 and 1"):
        UnitAmount(value)


def test_default_output_path_is_adjacent() -> None:
    """Default naming leaves the source path untouched."""
    source = Path("/books/essay.pdf")
    assert default_output_path(source) == Path("/books/essay-paperized.pdf")


def test_request_never_allows_source_overwrite(tmp_path: Path) -> None:
    """Force does not permit the destructive source-equals-output case."""
    source = tmp_path / "source.pdf"
    source.touch()
    request = TransformRequest(
        source=source,
        output=source,
        preset_name="parchment",
        strength=UnitAmount(1.0),
        texture=None,
        force=True,
    )
    with pytest.raises(OutputPathError, match="must not overwrite"):
        request.validate_paths()


def test_request_requires_pdf_suffix(tmp_path: Path) -> None:
    """The public pipeline rejects misleading input extensions."""
    source = tmp_path / "source.txt"
    source.touch()
    request = TransformRequest(
        source=source,
        output=tmp_path / "output.pdf",
        preset_name="parchment",
        strength=UnitAmount(1.0),
        texture=None,
    )
    with pytest.raises(OutputPathError, match="not a PDF"):
        request.validate_paths()


def test_request_requires_existing_output_directory(tmp_path: Path) -> None:
    """Atomic output requires a real destination directory."""
    source = tmp_path / "source.pdf"
    source.touch()
    request = TransformRequest(
        source=source,
        output=tmp_path / "missing" / "output.pdf",
        preset_name="parchment",
        strength=UnitAmount(1.0),
        texture=None,
    )
    with pytest.raises(OutputPathError, match="directory does not exist"):
        request.validate_paths()
