# Paperize

Turn bright white PDF pages into warm, comfortable paper while preserving the
original layout, selectable text, vectors, links, and annotations.

Paperize modifies PDF content streams directly. It does not rasterize pages or
rebuild text, so the original layout, selectable text, vectors, links, and
annotations remain intact.

## Install

```console
uv tool install paperize-pdf
```

The PyPI distribution is named `paperize-pdf` because the shorter distribution
name is occupied by an unrelated project. The installed command remains
`paperize`.

## Usage

Proposed command:

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

The vignette strength and paper texture are independently tunable:

```console
paperize input.pdf --vignette 0.7
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
