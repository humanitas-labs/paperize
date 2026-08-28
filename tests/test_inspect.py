"""Tests for PDF safety inspection."""

from pathlib import Path

import pikepdf
import pytest

from paperize.errors import (
    AlreadyPaperizedError,
    SignedPdfError,
)
from paperize.inspect import PAPERIZE_INFO_KEY, inspect_safety


def test_rejects_signature_field(tmp_path: Path) -> None:
    """A signature field is detected without validating its certificate."""
    path = tmp_path / "signed.pdf"
    pdf = pikepdf.Pdf.new()
    pdf.add_blank_page()
    signature = pdf.make_indirect(
        pikepdf.Dictionary(FT=pikepdf.Name("/Sig"), T="Approval")
    )
    pdf.Root.AcroForm = pikepdf.Dictionary(Fields=pikepdf.Array([signature]))
    pdf.save(path)

    with pikepdf.Pdf.open(path) as opened, pytest.raises(SignedPdfError):
        inspect_safety(opened)


def test_allows_accessible_encrypted_pdf(tmp_path: Path) -> None:
    """Legacy restrictions do not block a locally accessible transformation."""
    path = tmp_path / "encrypted.pdf"
    pdf = pikepdf.Pdf.new()
    pdf.add_blank_page()
    pdf.save(path, encryption=pikepdf.Encryption(owner="owner-secret", user=""))

    with pikepdf.Pdf.open(path) as opened:
        assert opened.is_encrypted
        inspect_safety(opened)


def test_rejects_existing_paperize_marker(tmp_path: Path) -> None:
    """Repeated processing cannot silently compound the effect."""
    path = tmp_path / "paperized.pdf"
    pdf = pikepdf.Pdf.new()
    pdf.add_blank_page()
    pdf.docinfo[PAPERIZE_INFO_KEY] = "paperize-pdf 0.1.0"
    pdf.save(path)

    with pikepdf.Pdf.open(path) as opened, pytest.raises(AlreadyPaperizedError):
        inspect_safety(opened)
