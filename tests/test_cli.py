"""Command-line contract tests."""

from pathlib import Path

import pikepdf
from click.testing import CliRunner

from paperize.cli import cli


def test_cli_writes_default_output(source_pdf: Path) -> None:
    """The common command prints and creates the conventional output path."""
    runner = CliRunner()
    result = runner.invoke(cli, [str(source_pdf)])
    expected = source_pdf.with_name("source-paperized.pdf")

    assert result.exit_code == 0, result.output
    assert result.output.strip() == str(expected)
    assert expected.exists()


def test_cli_protects_existing_output(source_pdf: Path) -> None:
    """Existing outputs require an explicit force flag."""
    runner = CliRunner()
    output = source_pdf.with_name("existing.pdf")
    output.write_text("do not overwrite")

    result = runner.invoke(cli, [str(source_pdf), "-o", str(output)])

    assert result.exit_code == 1
    assert "use --force" in result.output
    assert output.read_text() == "do not overwrite"


def test_cli_force_replaces_existing_output(source_pdf: Path) -> None:
    """Force permits replacing the destination but never the source."""
    runner = CliRunner()
    output = source_pdf.with_name("existing.pdf")
    output.write_text("replace me")

    result = runner.invoke(
        cli,
        [str(source_pdf), "-o", str(output), "--force", "--texture", "0"],
    )

    assert result.exit_code == 0, result.output
    with pikepdf.Pdf.open(output) as opened:
        assert len(opened.pages) == 2


def test_cli_reports_invalid_pdf(tmp_path: Path) -> None:
    """Malformed input returns an actionable Click error."""
    runner = CliRunner()
    source = tmp_path / "broken.pdf"
    source.write_text("not a PDF")

    result = runner.invoke(cli, [str(source)])

    assert result.exit_code == 1
    assert "cannot read PDF" in result.output


def test_cli_version() -> None:
    """The installed command exposes the package version."""
    result = CliRunner().invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert result.output.strip() == "paperize, version 0.3.0"


def test_cli_accepts_vignette_override(source_pdf: Path) -> None:
    """The edge vignette can be disabled independently."""
    output = source_pdf.with_name("overrides.pdf")
    result = CliRunner().invoke(
        cli,
        [
            str(source_pdf),
            "-o",
            str(output),
            "--vignette",
            "0",
            "--vignette-width",
            "0.12",
        ],
    )
    assert result.exit_code == 0, result.output
    assert output.exists()
