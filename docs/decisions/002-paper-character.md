# ADR-002 :: Add a variable, edge-weighted elliptical vignette

Last updated: `2026.08.28`

> Paperize will add page depth with an elliptical radial multiply shading while
> leaving original text and ink colors unchanged.

---

## 1. Decision

- Draw a normalized radial paper shading with `#FAEDDB` at its center and
  `#FFE6C3` at its perimeter, transformed non-uniformly into an ellipse.
- Hold the center color flat across most of the page and begin the falloff only
  in the outer portion.
- Vary the transition boundary within a narrow deterministic range per page.
- Define width as the fraction of normalized center-to-edge radius occupied by
  the transition, with a default of `0.32`.
- Do not add a text- or ink-specific color layer.
- Define vignette colors and strengths in presets.
- Expose numeric vignette-strength and vignette-width overrides while enabling
  the effect by default.
- Scale every visual layer by the global `--strength` value.

## 2. Rationale

A radial shading can express exact center and perimeter paper colors in one
operation. Under multiply blending, white source pixels become the shading
colors while dark marks remain visible. Scaling normalized shading coordinates
to page width and height produces the soft elliptical falloff visible in older
paper without a bitmap texture. Concentric inner and outer ellipses hold the
center color flat before beginning the edge transition. This avoids a stitched
color function so narrow widths render consistently across PDF engines. A
seeded page index shifts that boundary slightly, giving pages natural variation
while keeping output reproducible.

A bitmap vignette was rejected because it adds resolution, compression, and
file-size concerns without improving the effect. Ink recoloring was removed
because preserving the source's original dark content is the preferred result.

## 3. Design Implications

- Layer order is radial paper multiply followed by texture multiply.
- The original content streams remain untouched.
- The vignette shading is clipped to the effective crop box.
- The default transition occupies roughly the outer 32% of normalized radius.
- Page variation is seeded, deterministic, and scaled to 20% of the selected
  width.
- `--strength 0` must neutralize every layer for a stable boundary test.

## 4. When to Revisit

Revisit if major PDF viewers disagree on radial shading rendering or if a more
irregular, non-elliptical edge treatment becomes necessary.
