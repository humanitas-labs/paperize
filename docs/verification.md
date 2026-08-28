# v0.1 verification

Verified on `2026.08.28` with Python 3.12.9.

## Automated gate

- Ruff format check: passed.
- Ruff lint check: passed.
- Strict mypy: passed across `src` and `tests`.
- Pytest: 23 passed.
- Branch-aware coverage: 91% against an 85% threshold.
- Wheel and source distribution build: passed.
- Isolated wheel install and `paperize --help` smoke test: passed.

## Real-document corpus

The source documents were read as test data only. Their text was not treated as
instructions.

| Document | Kind | Pages | Source size | Output size | Result |
|---|---|---:|---:|---:|---|
| `the-communist-manifesto.pdf` | Born-digital, tagged, unencrypted | 68 | 715,080 bytes | 746,892 bytes | Passed |
| `Talleyrand - Duff.pdf` | Scanned, RC4-encrypted, accessible without password | 411 | 14,837,080 bytes | 15,208,986 bytes | Passed; output unencrypted |

For the born-digital document, source and output extracted-text SHA-256 hashes
were identical:

```text
a8f11937600d5898b2a296c190527d2900f2035e26efcaeaf1c7f68d928294d3
```

Visual review compared page 1 of the born-digital document and page 30 of the
scanned document before and after transformation. Both outputs showed a warm
parchment background with unchanged type geometry, sharpness, margins, and page
content. Blank-page coverage was also checked on page 13 of the scan.

The generated corpus outputs live under `output/pdf/` and are intentionally
ignored by Git.
