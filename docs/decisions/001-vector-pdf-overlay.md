# ADR-001 :: Use a vector PDF overlay

Last updated: `2026.08.27`

> Paperize will append a multiply-blend graphics stream to each source page
> using pikepdf. This delivers the intended warm-paper appearance without
> rasterizing or reconstructing the original document.

---

## 1. Decision

- Implement v0.1 in Python 3.12 with `pikepdf` and `click`.
- Modify existing PDFs by appending page-sized, multiply-blended vector fills.
- Keep texture deterministic and PDF-native.
- Preserve existing page streams and document structures.
- Accept encrypted PDFs that open without a supplied password and write an
  unencrypted result; reject files that require an unavailable password.
- Reject digitally signed PDFs in v0.1.
- Treat raster rendering as a separately approved fallback, not an automatic
  behavior.

## 2. Rationale

The core product promise is the same page with a warmer appearance. A PDF
graphics stream changes only presentation and therefore preserves selectable
text, embedded fonts, vector sharpness, links, outlines, and annotations.
`pikepdf` exposes the page resources and streams needed for this operation and
ships with its PDF engine in standard wheels.

A rendered image pipeline was rejected as the default because it increases
file size and can degrade text selection, accessibility, and print quality.
Rewriting individual colors inside arbitrary streams was rejected because PDF
graphics state is complex and can also live inside nested forms and images.
Rust and Go were rejected for v0.1 because their available PDF editing stacks
would require more low-level format work before testing the product hypothesis.

The tradeoff is that unusual transparency groups or non-conforming content
streams may render differently across viewers. A representative PDF corpus and
multi-viewer checks are therefore release requirements.

## 3. Design Implications

- The transformation engine never parses or reconstructs existing page text.
- Every added stream is isolated with PDF graphics-state save/restore operators.
- Page geometry comes from the effective crop box, including offset origins.
- Presets contain data only; transformation behavior does not branch by preset.
- Output is written beside a temporary file, reopened, verified, and atomically
  renamed.
- Structural checks cover page boxes, rotation, annotations, outlines, forms,
  and named destinations.
- Existing signatures are treated as a safety boundary. Legacy PDF permission
  flags do not block a local transformation when the file opens normally.

## 4. When to Revisit

Revisit this decision if corpus testing finds common PDFs where multiply blend
mode is ignored, page content leaves the graphics state unusable, or forms and
transparency groups render incorrectly. A rendered fallback may then be added
behind an explicit `--mode render` option with documented fidelity costs.
