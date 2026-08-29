# Document Extractor

Extract structured data from semi-structured documents — invoices, bills, tax forms, resumes, bank statements, shipment manifests — using any OpenAI-compatible LLM (OpenAI, Ollama, vLLM, Groq, etc.), with **per-field grounding and confidence**, not just raw extraction.

## Why this, not just another parser

Most extractors give you a value and no way to know if it's real. This one tells you:

- **`grounded`** — the value was found verbatim (or near-verbatim) in the source document text.
- **`ungrounded`** — the value doesn't appear in the source — likely a hallucination. Flag for human review.
- **`missing_required`** — a field you marked required came back empty.
- **`invalid_format`** — the value doesn't match a pattern/enum constraint you declared (e.g. a shipment status outside the allowed list).
- **`failed_check`** — a custom cross-field rule failed (e.g. line items don't sum to the stated total).

No extra LLM call for any of this — it's deterministic, string/rule-based validation against text you already extracted.

**Where it fits:** semi-structured documents with recurring fields (invoices, bills, tax forms, resumes, statements), and prose documents where *proving* a value came from the source matters (contracts, legal clauses, insurance claims). It is not a vision-LLM pipeline — it works from extracted text (digital PDF text layer, or local OCR for scans/images), which is what keeps it fast, cheap, and usable with small local models. Messy handwritten forms or complex multi-column layouts are a known weaker spot (see [document-extractor-spec.md](document-extractor-spec.md)).

## Two ways to use it

| | Who it's for | How |
|---|---|---|
| **CLI** | No coding needed | `python cli.py extract <file> <schema.json>` |
| **Python API** | Building it into your own app | `DocumentParser(client).extract(document_bytes, schema)` |

Defining *what* to extract also has two paths — hand-write a JSON/YAML schema file, or describe it in plain English and let the LLM draft the schema for you.

## Install

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

You also need access to an LLM. Either:
- An OpenAI API key (`export OPENAI_API_KEY=...` or pass `--api-key`), or
- A local model via [Ollama](https://ollama.com/) — no API key, no cloud, documents never leave your machine.

## Quickstart — CLI (no coding)

```bash
# 1. Extract using one of the bundled example schemas
python cli.py extract sample_invoice.png schemas/invoice.json \
  --model gpt-4o-mini --api-key sk-...

# Or with a local model via Ollama (no API key needed):
python cli.py extract sample_invoice.png schemas/invoice.json \
  --model llama3.2 --base-url http://localhost:11434/v1 --api-key ollama
```

Output is JSON, printed to stdout (or saved with `--output result.json`):

```json
{
  "_meta": { "truncated": false, "truncation_reason": null },
  "invoice_number": { "value": "INV-9011", "confidence": "high", "flags": ["grounded"] },
  "total_price": { "value": 100.0, "confidence": "high", "flags": ["grounded"] }
}
```

Don't want to write JSON at all? Describe the fields in plain English instead:

```bash
python cli.py schema-from-text \
  "I want the invoice number, total price, and vendor name. Invoice number and total are required." \
  --output schemas/my_invoice.json

# review schemas/my_invoice.json, then:
python cli.py extract my_invoice.pdf schemas/my_invoice.json
```

## Quickstart — Python API

```python
from schema import Schema, Field
from llm_client import LLMClient
from parser import DocumentParser

schema = Schema(
    name="Invoice",
    fields=[
        Field(name="invoice_number", description="The invoice number", required=True),
        Field(name="total_price", description="Total amount due", type="number", required=True),
    ],
)

client = LLMClient(model="gpt-4o-mini", api_key="sk-...")
# or: LLMClient(base_url="http://localhost:11434/v1", api_key="ollama", model="llama3.2")

parser = DocumentParser(client=client)

with open("invoice.pdf", "rb") as f:
    result = parser.extract(f.read(), schema)

print(result["invoice_number"])  # {'value': 'INV-9011', 'confidence': 'high', 'flags': ['grounded']}
```

## Full documentation

- [Getting Started](docs/getting-started.md) — step-by-step install, CLI, and API walkthroughs
- [Schema Guide](docs/schema-guide.md) — every field option (`type`, `required`, `pattern`, `enum`, `sub_fields`, few-shot `examples`), for JSON, YAML, and plain-English authoring
- [Output & Validation](docs/output-format.md) — the full result shape, what each confidence flag means, and how to write custom cross-check rules
- [Project spec](document-extractor-spec.md) — architecture, phased roadmap, honest competitive positioning

## Status

Core extraction, grounding, chunking, and both CLI/API paths are implemented and tested (`pytest test_parser.py`). Not yet done: PyPI packaging, a hosted API, and a formal license — see [document-extractor-spec.md](document-extractor-spec.md) for the roadmap.
