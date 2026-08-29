"""Pre-built schemas with few-shot examples for common document types.

Loaded from schemas/*.json rather than declared twice — schemas/invoice.json is the
single source of truth; editing it updates both the CLI template and this import.
"""

from pathlib import Path

from schema import Schema

_SCHEMAS_DIR = Path(__file__).parent / "schemas"

INVOICE_SCHEMA = Schema.from_file(_SCHEMAS_DIR / "invoice.json")
