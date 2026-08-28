"""Command-line interface for Paperize."""

from __future__ import annotations

from pathlib import Path

import click

from paperize import __version__
from paperize.config import TransformRequest, UnitAmount, default_output_path
from paperize.errors import PaperizeError
from paperize.pdf import paperize
from paperize.presets import PRESETS


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(version=__version__, prog_name="paperize")
@click.argument(
    "source",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
)
@click.option(
    "--output",
    "-o",
    type=click.Path(dir_okay=False, path_type=Path),
    help="Output path. Defaults to SOURCE-paperized.pdf.",
)
@click.option(
    "--preset",
    type=click.Choice(tuple(PRESETS), case_sensitive=False),
    default="parchment",
    show_default=True,
)
@click.option(
    "--strength",
    type=click.FloatRange(0.0, 1.0),
    default=1.0,
    show_default=True,
    help="Scale the preset's paper-color strength.",
)
@click.option(
    "--texture",
    type=click.FloatRange(0.0, 1.0),
    default=None,
    help="Override the preset's texture amount.",
)
@click.option(
    "--vignette",
    type=click.FloatRange(0.0, 1.0),
    default=None,
    help="Override the preset's edge-vignette strength.",
)
@click.option(
    "--vignette-width",
    type=click.FloatRange(0.0, 1.0),
    default=None,
    help="Override how far the edge vignette extends toward the page center.",
)
@click.option("--force", is_flag=True, help="Replace an existing output file.")
def cli(
    source: Path,
    output: Path | None,
    preset: str,
    strength: float,
    texture: float | None,
    vignette: float | None,
    vignette_width: float | None,
    *,
    force: bool,
) -> None:
    """Turn bright white PDF pages into warm, comfortable paper."""
    request = TransformRequest(
        source=source,
        output=output or default_output_path(source),
        preset_name=preset.lower(),
        strength=UnitAmount(strength),
        texture=None if texture is None else UnitAmount(texture),
        vignette=None if vignette is None else UnitAmount(vignette),
        vignette_width=(None if vignette_width is None else UnitAmount(vignette_width)),
        force=force,
    )
    try:
        completed = paperize(request)
    except PaperizeError as error:
        raise click.ClickException(str(error)) from error
    except OSError as error:
        raise click.ClickException(str(error)) from error
    click.echo(completed)
