# Architecture

Paperize is a local, single-process CLI. The command validates user input and
delegates to a PDF transformation pipeline. The pipeline inspects the source,
adds a vector overlay to each page, saves atomically, and verifies structural
invariants before exposing the output.

```text
CLI
→ validated configuration and preset
→ PDF safety inspection
→ page overlay engine
→ temporary output
→ structural verification
→ atomic rename
```

## Decisions

| ID | Decision | Status |
|---|---|---|
| [ADR-001](decisions/001-vector-pdf-overlay.md) | Use a vector PDF overlay implemented with pikepdf | Accepted |
