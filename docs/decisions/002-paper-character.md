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
- Do not add a text- or ink-specific color layer.
- Define vignette colors and strengths in presets.
- Expose a numeric vignette override while enabling the effect by default.
- Scale every visual layer by the global `--strength` value.

## 2. Rationale

A radial shading can express exact center and perimeter paper colors in one
operation. Under multiply blending, white source pixels become the shading
colors while dark marks remain visible. Scaling normalized shading coordinates
to page width and height produces the soft elliptical falloff visible in older
paper without a bitmap texture. A stitching function holds the center color
flat before beginning the edge transition. A seeded page index shifts that
boundary slightly, giving pages natural variation while keeping output
reproducible.

A bitmap vignette was rejected because it adds resolution, compression, and
file-size concerns without improving the effect. Ink recoloring was removed
because preserving the source's original dark content is the preferred result.

## 3. Design Implications

- Layer order is radial paper multiply followed by texture multiply.
- The original content streams remain untouched.
- The vignette shading is clipped to the effective crop box.
- The transition begins between 62% and 74% of the normalized radius.
- Page variation is seeded and deterministic.
- `--strength 0` must neutralize every layer for a stable boundary test.

## 4. When to Revisit

Revisit if major PDF viewers disagree on radial shading rendering or if a more
irregular, non-elliptical edge treatment becomes necessary.
