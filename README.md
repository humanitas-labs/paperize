# Paperize

Turn bright white PDF pages into warm, comfortable paper while preserving the
original layout, selectable text, vectors, links, and annotations.

Paperize modifies PDF content streams directly. It does not rasterize pages or
rebuild text, so the original layout, selectable text, vectors, links, and
annotations remain intact.

## Install

```console
uv tool install git+https://github.com/humanitas-labs/paperize.git
paperize --version
```

The distribution is named `paperize-pdf`; the installed command is `paperize`.
For a local clone, run `uv tool install .` from the repository root.

`uv` installs commands into its user tool directory. If `paperize` is not found
after installation, add that directory to your shell path and open a new shell:

```console
uv tool update-shell
```

## Usage

Basic command:

```console
paperize input.pdf
# writes input-paperized.pdf
```

Choose a preset or tune the effect:

```console
paperize input.pdf --preset cream
paperize input.pdf --preset sepia --strength 0.6 --texture 0.15
paperize input.pdf -o comfortable.pdf
```

The default `parchment` preset uses a soft elliptical falloff from `#FAEDDB` at
the broad page center to `#FFE6C3` near the perimeter. The transition begins
only in the outer portion of the page and varies subtly, but deterministically,
from page to page. Paperize leaves the original text and ink colors alone.

Preset defaults at full strength on a white source page:

| Preset | Broad center | Page edge | Texture | Vignette width | Character |
|---|---|---|---:|---:|---|
| `cream` | `#FAE8B8` | `#C79E66` | `0.03` | `0.32` | Golden cream |
| `parchment` | `#FAEDDB` | `#FFE6C3` | `0.08` | `0.32` | Light, warm paper |
| `sepia` | `#E0AD66` | `#9E6633` | `0.12` | `0.32` | Strong aged-paper effect |

All presets use the variable edge vignette by default. `--strength` scales the
whole treatment, while `--texture`, `--vignette`, and `--vignette-width`
override their individual preset defaults with values from `0` through `1`.
Vignette width is the fraction of the center-to-edge radius occupied by the
transition; smaller values confine the effect closer to the page edge.

The vignette strength and paper texture are independently tunable:

```console
paperize input.pdf --vignette 0.7
paperize input.pdf --vignette-width 0.12
paperize input.pdf --texture 0
```

Paperize refuses to overwrite files unless `--force` is present. Accessible
encrypted PDFs are accepted and produce an ordinary unencrypted output. PDFs
that require an unavailable password fail normally. Digitally signed PDFs are
refused because rewriting them would invalidate the signature.

## Development

```console
uv sync --all-groups
uv run ruff format --check .
uv run ruff check .
uv run mypy src tests
uv run pytest
uv build
```

The approved implementation plan is in
[`./.plan/implementation-plan.md`](.plan/implementation-plan.md). Architecture
decisions are recorded in [`docs/architecture.md`](docs/architecture.md).
