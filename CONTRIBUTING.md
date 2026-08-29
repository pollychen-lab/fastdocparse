# Contributing

## Setup

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Running the tests

```bash
pytest -v
```

All 63 tests should pass before you open a PR. CI runs this automatically on every push and PR, but running it locally first saves a round-trip.

## Before opening a PR

- **Add or update tests for anything you change.** This project has been through several rounds of "found a real bug, added a regression test for it" — that pattern is the standard here, not the exception. A behavior change with no test is treated as unverified.
- **Run the full suite**, not just the file you touched — several modules interact (e.g. changes to `grounding.py`'s `check_substring` affect both `parser.py`'s merge logic and its final grounding check).
- **Keep the docs in sync.** If you change a CLI flag, a `Schema`/`Field` option, or the output shape, update the relevant file in `docs/` and/or `README.md` in the same PR. Stale docs have caused real confusion here before (see git history).
- **Don't break backward compatibility silently.** `DocumentParser.extract()`'s return shape (a dict with `_meta` + one entry per field) is a public contract — the CLI, `ExtractionResult`, and every test depend on it. If a change requires breaking it, say so explicitly in the PR description rather than letting it happen as a side effect.

## Code style

- No comments explaining *what* code does — names should carry that. Comments are for *why*: a non-obvious constraint, a workaround, a decision that would otherwise look arbitrary.
- Prefer extending an existing module's pattern over introducing a new one. E.g. a new document format is a new function in `parser.py`'s `INGESTION_HANDLERS`-style registry, not a parallel ingestion system; a new validation rule is a new factory function in `grounding.py`, not a new file.
- Config knobs belong in `config.py`'s `ExtractionConfig`, not as hardcoded constants scattered through the pipeline — that was a real bug here once (two disconnected page-limit constants caused silent data loss; see `config.py`'s comment on `max_pages`).

## Project structure

| File | Responsibility |
|---|---|
| `schema.py` | `Field`/`Schema` definitions + loaders (Python/JSON/YAML) |
| `schema_compiler.py` | Plain-English description → `Schema`, via one LLM call |
| `prompt_compiler.py` | `Schema` → extraction prompt |
| `llm_client.py` | OpenAI-compatible adapter, with retry/error handling |
| `pdf_utils.py` / `ocr_engine.py` | Document → text ingestion |
| `parser.py` | Orchestrates ingest → chunk → extract → merge → validate |
| `grounding.py` | Confidence/validation checks (grounding, constraints, cross-check rules) |
| `cache.py` | Opt-in caching for `DocumentParser.extract()` |
| `result.py` | Optional typed view of the output dict |
| `cli.py` | CLI wrapper — no logic that doesn't already exist above |

## Reporting issues

Include: the schema you used (or a minimal repro), the document type (not the document itself if it's sensitive), and the exact error/output vs. what you expected.
