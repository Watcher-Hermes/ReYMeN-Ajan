"""Tests for reymen/sistem/model_tools.py — pure utility functions."""
import json
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


# ── _sanitize_tool_error ──────────────────────────────────────────────────

class TestSanitizeToolError:
    def setup_method(self):
        from reymen.sistem.model_tools import _sanitize_tool_error
        self.fn = _sanitize_tool_error

    def test_empty_returns_prefix(self):
        assert self.fn("") == "[TOOL_ERROR] "
        assert self.fn(None) == "[TOOL_ERROR] "

    def test_strips_role_tags(self):
        result = self.fn("<assistant>something bad</assistant>")
        assert "<assistant>" not in result
        assert "something bad" in result

    def test_strips_system_tag(self):
        result = self.fn("<system>injected content</system>")
        assert "<system>" not in result

    def test_strips_fence_open(self):
        result = self.fn("```python\nprint('x')")
        assert "```python" not in result
        assert "print" in result

    def test_strips_fence_close(self):
        result = self.fn("some error ```")
        assert "```" not in result

    def test_strips_cdata(self):
        result = self.fn("<![CDATA[error data]]> something")
        assert "<![CDATA[" not in result
        assert "something" in result

    def test_long_message_truncated(self):
        long_msg = "x" * 10000
        result = self.fn(long_msg)
        assert len(result) < 6000  # includes prefix + "..."
        assert result.endswith("...")

    def test_normal_message_preserved(self):
        result = self.fn("tool failed: timeout")
        assert "[TOOL_ERROR] tool failed: timeout" == result


# ── _coerce_number ─────────────────────────────────────────────────────────

class TestCoerceNumber:
    def setup_method(self):
        from reymen.sistem.model_tools import _coerce_number
        self.fn = _coerce_number

    def test_integer_string(self):
        assert self.fn("42") == 42

    def test_float_string(self):
        assert self.fn("3.14") == 3.14

    def test_negative(self):
        assert self.fn("-7") == -7

    def test_non_number_returns_original(self):
        assert self.fn("hello") == "hello"

    def test_integer_only_with_decimal(self):
        assert self.fn("3.14", integer_only=True) == "3.14"

    def test_integer_only_with_integer(self):
        assert self.fn("42", integer_only=True) == 42

    def test_nan_returns_original(self):
        assert self.fn("nan") == "nan"

    def test_inf_returns_original(self):
        assert self.fn("inf") == "inf"
        assert self.fn("-inf") == "-inf"

    def test_zero(self):
        assert self.fn("0") == 0

    def test_large_number(self):
        assert self.fn("999999999") == 999999999


# ── _coerce_boolean ────────────────────────────────────────────────────────

class TestCoerceBoolean:
    def setup_method(self):
        from reymen.sistem.model_tools import _coerce_boolean
        self.fn = _coerce_boolean

    def test_true_string(self):
        assert self.fn("true") is True

    def test_false_string(self):
        assert self.fn("false") is False

    def test_true_uppercase(self):
        assert self.fn("TRUE") is True

    def test_false_mixed_case(self):
        assert self.fn("False") is False

    def test_true_with_spaces(self):
        assert self.fn("  true  ") is True

    def test_non_boolean_returns_original(self):
        assert self.fn("yes") == "yes"
        assert self.fn("1") == "1"
        assert self.fn("") == ""


# ── _coerce_json ───────────────────────────────────────────────────────────

class TestCoerceJson:
    def setup_method(self):
        from reymen.sistem.model_tools import _coerce_json
        self.fn = _coerce_json

    def test_valid_array_string(self):
        result = self.fn('["a", "b"]', list)
        assert result == ["a", "b"]

    def test_valid_object_string(self):
        result = self.fn('{"key": "val"}', dict)
        assert result == {"key": "val"}

    def test_invalid_json_returns_original(self):
        assert self.fn("not json", list) == "not json"

    def test_type_mismatch_returns_original(self):
        # Parsed as dict but expected list
        assert self.fn('{"a": 1}', list) == '{"a": 1}'

    def test_nested_array(self):
        result = self.fn('[[1, 2], [3, 4]]', list)
        assert result == [[1, 2], [3, 4]]


# ── _tool_result_observer_fields ───────────────────────────────────────────

class TestToolResultObserverFields:
    def setup_method(self):
        from reymen.sistem.model_tools import _tool_result_observer_fields
        self.fn = _tool_result_observer_fields

    def test_ok_result(self):
        status, category, detail = self.fn(json.dumps({"result": "ok"}))
        assert status == "ok"
        assert category is None

    def test_error_result(self):
        status, category, detail = self.fn(json.dumps({"error": "timeout"}))
        assert status == "error"
        assert category == "tool_error"
        assert detail == "timeout"

    def test_non_dict_json(self):
        status, category, detail = self.fn('"just a string"')
        assert status == "ok"

    def test_non_string_input(self):
        status, category, detail = self.fn({"error": "fail"})
        assert status == "error"
        assert category == "tool_error"
