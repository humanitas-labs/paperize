# Changelog

All notable changes to Paperize will be documented in this file.

## 0.3.0 - 2026.08.28

- Add `--vignette-width` to control how far the edge transition extends toward
  the page center.
- Scale deterministic page-to-page variation to the selected width.
- Preserve the existing appearance with a default width of `0.32`.
- Use concentric radial geometry for consistent narrow-vignette rendering
  across PDF viewers.

## 0.2.0 - 2026.08.28

- Add an elliptical paper shading from `#FAEDDB` at the center to `#FFE6C3`
  around the perimeter.
- Keep the center color broad and delay the shading transition until near the
  page edge.
- Vary the vignette extent subtly and deterministically from page to page.
- Add a `--vignette` control while preserving original text and ink colors.

## 0.1.0 - 2026.08.28

- Add the initial vector-preserving PDF transformation CLI.
- Add cream, parchment, and sepia presets with optional paper texture.
- Preserve document structure, reject signed inputs, and process accessible
  encrypted inputs into ordinary unencrypted outputs.
