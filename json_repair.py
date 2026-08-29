"""Recover a JSON object from raw LLM output that isn't guaranteed to be clean JSON."""

import json
import re
from typing import Any, Dict


def parse_json_from_llm(text: str) -> Dict[str, Any]:
    """Safely parse JSON from LLM output, handling markdown blocks and `<think>` tags."""
    text = text.strip()
    text = re.sub(r"<think\b[^>]*>.*?</think>", "", text, flags=re.DOTALL | re.IGNORECASE)

    match = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL | re.IGNORECASE)
    if match:
        try:
            return json.loads(match.group(1).strip())
        except Exception:
            pass

    brace_positions = [i for i, c in enumerate(text) if c == "{"]
    for pos in reversed(brace_positions):
        end = text.rfind("}", pos)
        if end > pos:
            try:
                obj = json.loads(text[pos:end + 1])
                if isinstance(obj, dict):
                    return obj
            except Exception:
                continue
    return {}
