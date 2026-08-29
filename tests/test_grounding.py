"""Tests for the built-in cross-check rules and config validation."""

import pytest

from docextract.config import ExtractionConfig
from docextract.grounding import Issue, date_parseable_rule, numeric_sum_rule


def test_numeric_sum_rule_flags_mismatch():
    rule = numeric_sum_rule(list_field="items", total_field="total", item_key="amount")
    extracted = {"total": 100.0, "items": [{"amount": 20.0}, {"amount": 50.0}]}
    issues = rule(extracted)
    assert issues is not None
    assert {i.field for i in issues} == {"total", "items"}
    assert all(isinstance(i, Issue) for i in issues)


def test_numeric_sum_rule_passes_within_tolerance():
    rule = numeric_sum_rule(list_field="items", total_field="total", item_key="amount", tolerance=0.01)
    extracted = {"total": 70.005, "items": [{"amount": 20.0}, {"amount": 50.0}]}
    assert rule(extracted) is None


def test_numeric_sum_rule_ignores_missing_data():
    rule = numeric_sum_rule(list_field="items", total_field="total")
    assert rule({"total": None, "items": None}) is None
    assert rule({"total": 100.0, "items": []}) is None


def test_date_parseable_rule_flags_unparseable():
    rule = date_parseable_rule("invoice_date")
    issues = rule({"invoice_date": "not a date"})
    assert issues is not None
    assert issues[0].field == "invoice_date"


def test_date_parseable_rule_accepts_default_formats():
    rule = date_parseable_rule("invoice_date")
    assert rule({"invoice_date": "2023-04-15"}) is None
    assert rule({"invoice_date": "04/15/2023"}) is None


def test_date_parseable_rule_custom_formats():
    rule = date_parseable_rule("invoice_date", formats=["%Y%m%d"])
    assert rule({"invoice_date": "20230415"}) is None
    assert rule({"invoice_date": "2023-04-15"}) is not None


def test_date_parseable_rule_ignores_missing_value():
    rule = date_parseable_rule("invoice_date")
    assert rule({"invoice_date": None}) is None


@pytest.mark.parametrize(
    "kwargs",
    [
        {"max_pages": 0},
        {"chunk_max_tokens": -1},
        {"pdf_render_dpi": 0},
        {"max_image_dim": -100},
        {"ocr_min_confidence": 1.5},
        {"ocr_min_confidence": -0.1},
    ],
)
def test_extraction_config_rejects_invalid_values(kwargs):
    with pytest.raises(ValueError):
        ExtractionConfig(**kwargs)


def test_extraction_config_accepts_valid_values():
    config = ExtractionConfig(max_pages=5, chunk_max_tokens=1000, ocr_min_confidence=0.5)
    assert config.max_pages == 5
