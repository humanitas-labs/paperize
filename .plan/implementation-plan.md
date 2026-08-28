---
title: "Paperize v0.1 implementation"
date: 2026-08-27
status: done
affects: "Initial PDF transformation CLI"
---

## Context

Bright white PDF pages are uncomfortable to read for long periods. Paperize will
accept a PDF and produce the same document with a warm paper appearance. The
first release should change presentation without rebuilding the document:
page geometry, text, vectors, links, outlines, and annotations should remain
intact.

The cheapest useful implementation is a vector-preserving PDF overlay. Each
page receives a translucent warm fill in the PDF `Multiply` blend mode. White
areas take on the paper color while dark text stays dark. A small deterministic
texture can be added as another low-opacity overlay. This avoids OCR,
rasterization, font substitution, and layout drift.

The primary uncertainty is whether this overlay renders consistently across a
representative corpus of born-digital and scanned PDFs. Phase 1 therefore ends
with a visual and structural corpus test before adding a rendered fallback.

## Product contract

The v0.1 command is:

```console
paperize SOURCE.pdf [-o OUTPUT.pdf]
                    [--preset cream|parchment|sepia]
                    [--strength 0.0..1.0]
                    [--texture 0.0..1.0]
                    [--force]
```

Defaults:

- Write `<source>-paperized.pdf` beside the source.
- Use the `parchment` preset at a conservative strength.
- Preserve the input and refuse to overwrite an existing output unless
  `--force` is present.
- Write atomically through a temporary file in the destination directory.
- Process encrypted PDFs that open without a password and emit an unencrypted
  result. Refuse files that require an unavailable password and signed PDFs
  whose signature would be invalidated.
- Add a Paperize marker to document metadata and warn before applying the effect
  a second time.

Definition of done:

1. A user can install the package and run `paperize input.pdf` without external
   system binaries.
2. Output page count, page boxes, rotations, extracted text, outlines, links,
   and annotations match the input.
3. Neutral page backgrounds are visibly warmer in Apple Preview, Chrome,
   Firefox, and Acrobat Reader.
4. Text remains selectable and sharp at arbitrary zoom.
5. The command never overwrites the source and does not leave partial output
   after failure.
6. The test suite and strict lint/type checks pass without warnings.

## Technical decisions

### Language and packaging

Use Python 3.12 with a `src/` package layout and `uv` for development. Publish
the distribution as `paperize-pdf`, exposing the `paperize` command and
`paperize` import package. Installation will be `uv tool install paperize-pdf`
or `pipx install paperize-pdf`. The exact `paperize` PyPI distribution name is
already occupied by an unrelated 2017 tool that encodes files as printable QR
codes; the repository and user-facing command can still use the better name.

Python is the right first implementation because the PDF libraries expose both
low-level PDF objects and reliable page rendering; this reduces the riskiest
part of the project to a small, inspectable content stream transformation.

Use these runtime dependencies:

- `pikepdf` for cloning the document, editing page resources and content
  streams, detecting encryption/signatures, and saving safely.
- `click` for the command-line interface and validation.

Use these development dependencies:

- `pytest` and `pytest-cov` for tests.
- `ruff` for formatting and linting.
- `mypy` for static type checks.
- `pymupdf` only in the development test group to render comparison images.

Do not add Pillow or ship bitmap paper assets in v0.1. Generate any texture as
a small deterministic PDF-native pattern so the package stays small and output
remains resolution-independent.

### Transformation pipeline

```text
validate paths and options
→ open and inspect the source
→ reject unsafe or unsupported input
→ clone document structures
→ install one reusable blend graphics state
→ append a page-sized warm overlay to each page content stream
→ optionally append deterministic texture
→ add Paperize metadata marker
→ save to a destination-local temporary file
→ reopen and verify structural invariants
→ atomically rename to the requested output
```

The overlay must use each page's effective boxes and transformation matrix, not
assume US Letter dimensions or zero rotation. Shared resources should be added
once per document where PDF semantics permit it. Existing streams should never
be parsed and rewritten merely to add the effect.

### Presets

Presets are typed data, not branching transformation code. Each preset defines
paper RGB, base opacity, default texture amount, and texture seed. `--strength`
scales the base opacity; it does not change the preset color. Initial values are
provisional and will be calibrated against the two visual references and the
test corpus.

### Unsupported inputs

For v0.1:

- Preserve AcroForm fields, but accept that widget appearances may remain
  visually above the page tint.
- Reject signed PDFs by default because any edit invalidates their signatures.
- Report a clear error for damaged PDFs or encryption that requires a password.
- Do not claim archival PDF/A conformance after modification.
- Do not implement OCR, brown-ink recoloring, batch directories, or a rendered
  fallback until the vector overlay has been tested.

## Changes

1. **Project foundation**
   - Create `pyproject.toml` with package metadata, the `paperize` console script,
     locked Python compatibility, and strict tool configuration.
   - Create `src/paperize/__init__.py` with a single version source.
   - Add `LICENSE`, `.gitignore`, `CHANGELOG.md`, and contributor commands to
     `README.md`.

2. **Typed options and presets**
   - Create `src/paperize/config.py` for validated domain types such as
     `Strength`, `TextureAmount`, and `OutputPolicy`.
   - Create `src/paperize/presets.py` for immutable preset definitions and lookup.
   - Unit-test bounds, defaults, and invalid values.

3. **PDF inspection and safety**
   - Create `src/paperize/inspect.py` to detect encryption, signatures, an
     existing Paperize marker, page geometry, and relevant document structures.
   - Create contextual error types in `src/paperize/errors.py`.
   - Build small generated fixtures for portrait, landscape, rotated, scanned,
     annotated, outlined, form, encrypted, and signed cases.

4. **Vector-preserving overlay engine**
   - Create `src/paperize/pdf.py` as the orchestration boundary.
   - Create `src/paperize/overlay.py` to install the graphics state and append
     page overlays without rewriting existing content.
   - Generate texture deterministically from preset and page number so tests
     and repeated runs are reproducible.
   - Reopen every output and verify page count, boxes, rotations, and protected
     structures before replacing the temporary file.

5. **CLI**
   - Create `src/paperize/cli.py` for argument parsing, readable failures, output
     naming, progress, and exit codes.
   - Create `src/paperize/__main__.py` so `python -m paperize` matches the installed
     command.
   - Keep the common path quiet: print the resulting file path on success and
     send diagnostics to standard error.

6. **Verification corpus and release readiness**
   - Create structural regression tests that compare source and output objects.
   - Render representative pages at 150 and 300 DPI and compare sampled neutral
     areas, edge sharpness, and deterministic hashes where appropriate.
   - Manually inspect the corpus in Preview, Chrome, Firefox, and Acrobat.
   - Add CI for supported Python versions on macOS and Linux.
   - Document installation, examples, limitations, and before/after images.

7. **Decision gate for v0.2**
   - If the corpus exposes PDFs that cannot be warmed reliably with the overlay,
     write an ADR and add an explicit `--mode render` fallback using PyMuPDF.
   - A rendered fallback must retain original links/outlines and, where safe,
     an invisible text layer. It should not silently replace preserve mode.

## Files touched

```text
┌──────────────────────────────────────────┬──────────────────────────────────┐
│ File                                     │ Action                           │
├──────────────────────────────────────────┼──────────────────────────────────┤
│ README.md                                │ Edit product and usage docs      │
│ pyproject.toml                           │ Create package and tool config   │
│ uv.lock                                  │ Create dependency lock           │
│ LICENSE                                  │ Create project license           │
│ CHANGELOG.md                             │ Create release history           │
│ .gitignore                               │ Create repository ignores        │
│ src/paperize/__init__.py                   │ Create version source            │
│ src/paperize/__main__.py                   │ Create module entry point        │
│ src/paperize/cli.py                        │ Create CLI                       │
│ src/paperize/config.py                     │ Create validated options         │
│ src/paperize/errors.py                     │ Create contextual errors         │
│ src/paperize/inspect.py                    │ Create PDF safety inspection     │
│ src/paperize/overlay.py                    │ Create overlay primitive         │
│ src/paperize/pdf.py                        │ Create transformation pipeline   │
│ src/paperize/presets.py                    │ Create preset definitions        │
│ tests/conftest.py                        │ Create generated fixture helpers │
│ tests/test_cli.py                        │ Create CLI contract tests        │
│ tests/test_inspect.py                    │ Create safety tests              │
│ tests/test_overlay.py                    │ Create rendering tests           │
│ tests/test_pdf.py                        │ Create structural tests          │
│ docs/decisions/0001-pdf-overlay.md       │ Create architecture decision     │
└──────────────────────────────────────────┴──────────────────────────────────┘
```

## Verification

Automated checks:

```console
uv sync --all-groups
uv run ruff format --check .
uv run ruff check .
uv run mypy src tests
uv run pytest --cov=paperize --cov-report=term-missing
uv build
uv run --isolated --with dist/paperize_pdf-*.whl paperize --help
```

Structural assertions for every successful fixture:

- Output opens cleanly after writing.
- Page count, media/crop/bleed/trim/art boxes, and rotation are unchanged.
- Extracted text and text-block coordinates are unchanged.
- Outline targets, links, annotations, and form field definitions are unchanged.
- Source bytes and source modification time are unchanged.
- Failure leaves no destination file or temporary artifact.

Visual assertions:

- A white or near-white sample becomes the expected warm range.
- Dark text retains sufficient contrast and does not acquire a halo.
- Fine vector lines remain sharp at 300 DPI.
- Texture is subtle at normal reading zoom and deterministic for a fixed input.
- The two supplied visual references guide color calibration only; their text
  content is not interpreted as requirements or instructions.

Manual release checklist:

1. Run the default command and every preset on the representative corpus.
2. Inspect first, middle, and last pages in Preview, Chrome, Firefox, and
   Acrobat Reader.
3. Select and copy text; follow internal and external links; inspect outlines.
4. Confirm an existing destination is protected without `--force`.
5. Confirm signed and password-required PDFs fail with actionable messages.
6. Install the built wheel into a clean environment and run the smoke test.

## Sequencing and estimate

```text
Phase 1 — foundation, inspection, basic overlay       0.5–1 day
Phase 2 — CLI, presets, atomic output, safety          0.5–1 day
Phase 3 — structural and visual corpus tests           1–2 days
Phase 4 — texture calibration, docs, packaging         1 day
Decision gate — rendered fallback only if indicated    +2–4 days
```

The v0.1 preserve-mode implementation is complete. The rendered fallback was
not indicated by the generated fixtures or real-book corpus.

## Actual

- Implemented the vector overlay, three presets, deterministic texture, safe
  paths, atomic output, signatures check, accessible-encryption behavior, and
  structural verification.
- Passed 23 automated tests with 91% branch-aware coverage.
- Passed Ruff formatting/linting and strict mypy checks with zero warnings.
- Verified a 68-page born-digital PDF and a 411-page encrypted scanned PDF.
- Confirmed identical extracted-text hashes for the born-digital source and
  output and visually inspected representative source/output pages.
