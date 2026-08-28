"""Domain errors surfaced by Paperize."""


class PaperizeError(Exception):
    """Base class for expected Paperize failures."""


class InputPdfError(PaperizeError):
    """The source is not a readable, supported PDF."""


class SignedPdfError(PaperizeError):
    """The source PDF contains a digital signature."""


class AlreadyPaperizedError(PaperizeError):
    """The source PDF already carries the Paperize marker."""


class OutputPathError(PaperizeError):
    """The destination path is unsafe or unavailable."""


class VerificationError(PaperizeError):
    """The written PDF failed structural verification."""
