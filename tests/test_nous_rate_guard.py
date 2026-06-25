# -*- coding: utf-8 -*-
"""Tests for agent/nous_rate_guard.py — rate limit detection, state management."""

import json
import os
import tempfile
import time
from unittest.mock import patch, MagicMock

import pytest


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def tmp_state_dir(tmp_path):
    """Patch _state_path to use a temp directory."""
    state_dir = tmp_path / "rate_limits"
    state_dir.mkdir()
    state_file = state_dir / "nous.json"

    import agent.nous_rate_guard as mod
    with patch.object(mod, "_state_path", return_value=str(state_file)):
        yield state_file


# ---------------------------------------------------------------------------
# _parse_reset_seconds
# ---------------------------------------------------------------------------

class TestParseResetSeconds:
    def test_none_headers(self):
        from agent.nous_rate_guard import _parse_reset_seconds
        assert _parse_reset_seconds(None) is None

    def test_empty_headers(self):
        from agent.nous_rate_guard import _parse_reset_seconds
        assert _parse_reset_seconds({}) is None

    def test_priority_1h_header(self):
        from agent.nous_rate_guard import _parse_reset_seconds
        h = {
            "x-ratelimit-reset-requests-1h": "120",
            "x-ratelimit-reset-requests": "30",
        }
        assert _parse_reset_seconds(h) == 120.0

    def test_fallback_to_per_minute(self):
        from agent.nous_rate_guard import _parse_reset_seconds
        h = {"x-ratelimit-reset-requests": "45"}
        assert _parse_reset_seconds(h) == 45.0

    def test_fallback_to_retry_after(self):
        from agent.nous_rate_guard import _parse_reset_seconds
        h = {"retry-after": "10"}
        assert _parse_reset_seconds(h) == 10.0

    def test_non_numeric_ignored(self):
        from agent.nous_rate_guard import _parse_reset_seconds
        h = {"retry-after": "not-a-number"}
        assert _parse_reset_seconds(h) is None

    def test_zero_ignored(self):
        from agent.nous_rate_guard import _parse_reset_seconds
        h = {"retry-after": "0"}
        assert _parse_reset_seconds(h) is None


# ---------------------------------------------------------------------------
# format_remaining
# ---------------------------------------------------------------------------

class TestFormatRemaining:
    def test_seconds(self):
        from agent.nous_rate_guard import format_remaining
        assert format_remaining(45) == "45s"

    def test_minutes(self):
        from agent.nous_rate_guard import format_remaining
        assert format_remaining(120) == "2m"

    def test_minutes_and_seconds(self):
        from agent.nous_rate_guard import format_remaining
        assert format_remaining(125) == "2m 5s"

    def test_hours(self):
        from agent.nous_rate_guard import format_remaining
        assert format_remaining(7200) == "2h"

    def test_hours_and_minutes(self):
        from agent.nous_rate_guard import format_remaining
        assert format_remaining(7500) == "2h 5m"

    def test_zero(self):
        from agent.nous_rate_guard import format_remaining
        assert format_remaining(0) == "0s"


# ---------------------------------------------------------------------------
# _parse_buckets_from_headers
# ---------------------------------------------------------------------------

class TestParseBuckets:
    def test_no_headers(self):
        from agent.nous_rate_guard import _parse_buckets_from_headers
        assert _parse_buckets_from_headers(None) == {}
        assert _parse_buckets_from_headers({}) == {}

    def test_no_ratelimit_headers(self):
        from agent.nous_rate_guard import _parse_buckets_from_headers
        assert _parse_buckets_from_headers({"content-type": "application/json"}) == {}

    def test_extracts_all_buckets(self):
        from agent.nous_rate_guard import _parse_buckets_from_headers
        h = {
            "x-ratelimit-remaining-requests": "50",
            "x-ratelimit-reset-requests": "30.5",
            "x-ratelimit-remaining-requests-1h": "100",
            "x-ratelimit-reset-requests-1h": "1800",
            "x-ratelimit-remaining-tokens": "5000",
            "x-ratelimit-reset-tokens": "60",
            "x-ratelimit-remaining-tokens-1h": "100000",
            "x-ratelimit-reset-tokens-1h": "3600",
        }
        buckets = _parse_buckets_from_headers(h)
        assert "requests" in buckets
        assert buckets["requests"] == (50, 30.5)
        assert "requests-1h" in buckets
        assert buckets["requests-1h"] == (100, 1800.0)


# ---------------------------------------------------------------------------
# _has_exhausted_bucket
# ---------------------------------------------------------------------------

class TestHasExhaustedBucket:
    def test_empty(self):
        from agent.nous_rate_guard import _has_exhausted_bucket
        assert _has_exhausted_bucket({}) is False

    def test_remaining_positive(self):
        from agent.nous_rate_guard import _has_exhausted_bucket
        assert _has_exhausted_bucket({"r": (5, 60.0)}) is False

    def test_exhausted_long_reset(self):
        from agent.nous_rate_guard import _has_exhausted_bucket
        assert _has_exhausted_bucket({"r": (0, 300.0)}) is True

    def test_exhausted_short_reset(self):
        """Reset window < 60s is treated as transient."""
        from agent.nous_rate_guard import _has_exhausted_bucket
        assert _has_exhausted_bucket({"r": (0, 30.0)}) is False

    def test_remaining_none_with_reset(self):
        from agent.nous_rate_guard import _has_exhausted_bucket
        assert _has_exhausted_bucket({"r": (None, 300.0)}) is False


# ---------------------------------------------------------------------------
# nous_rate_limit_remaining / record / clear
# ---------------------------------------------------------------------------

class TestStateManagement:
    def test_no_state_file(self, tmp_state_dir):
        from agent.nous_rate_guard import nous_rate_limit_remaining
        assert nous_rate_limit_remaining() is None

    def test_record_and_read(self, tmp_state_dir):
        from agent.nous_rate_guard import record_nous_rate_limit, nous_rate_limit_remaining
        record_nous_rate_limit(default_cooldown=120.0)
        remaining = nous_rate_limit_remaining()
        assert remaining is not None
        assert remaining > 0
        assert remaining <= 120.0

    def test_record_with_header(self, tmp_state_dir):
        from agent.nous_rate_guard import record_nous_rate_limit, nous_rate_limit_remaining
        h = {"retry-after": "90"}
        record_nous_rate_limit(headers=h)
        remaining = nous_rate_limit_remaining()
        assert remaining is not None
        assert 80 <= remaining <= 90

    def test_clear(self, tmp_state_dir):
        from agent.nous_rate_guard import (
            record_nous_rate_limit, clear_nous_rate_limit, nous_rate_limit_remaining,
        )
        record_nous_rate_limit(default_cooldown=300)
        assert nous_rate_limit_remaining() is not None
        clear_nous_rate_limit()
        assert nous_rate_limit_remaining() is None

    def test_expired_state(self, tmp_state_dir):
        """State with reset_at in the past should return None."""
        import agent.nous_rate_guard as mod
        state = {"reset_at": time.time() - 100, "recorded_at": time.time() - 200, "reset_seconds": 100}
        tmp_state_dir.write_text(json.dumps(state), encoding="utf-8")
        assert mod.nous_rate_limit_remaining() is None

    def test_corrupt_json(self, tmp_state_dir):
        import agent.nous_rate_guard as mod
        tmp_state_dir.write_text("not json{{{", encoding="utf-8")
        assert mod.nous_rate_limit_remaining() is None


# ---------------------------------------------------------------------------
# rate_guard_izin_ver
# ---------------------------------------------------------------------------

class TestRateGuardIzinVer:
    def test_non_nous_provider(self):
        from agent.nous_rate_guard import rate_guard_izin_ver
        assert rate_guard_izin_ver("deepseek") is True
        assert rate_guard_izin_ver("openrouter") is True

    def test_nous_provider_no_state(self):
        from agent.nous_rate_guard import rate_guard_izin_ver
        with patch("agent.nous_rate_guard.nous_rate_limit_remaining", return_value=None):
            assert rate_guard_izin_ver("nous") is True

    def test_nous_provider_rate_limited(self):
        from agent.nous_rate_guard import rate_guard_izin_ver
        with patch("agent.nous_rate_guard.nous_rate_limit_remaining", return_value=60.0):
            assert rate_guard_izin_ver("nous") is False

    def test_case_insensitive(self):
        from agent.nous_rate_guard import rate_guard_izin_ver
        with patch("agent.nous_rate_guard.nous_rate_limit_remaining", return_value=60.0):
            assert rate_guard_izin_ver("NOUS") is False


# ---------------------------------------------------------------------------
# is_genuine_nous_rate_limit
# ---------------------------------------------------------------------------

class TestIsGenuineRateLimit:
    def test_no_headers_no_state(self):
        from agent.nous_rate_guard import is_genuine_nous_rate_limit
        assert is_genuine_nous_rate_limit(headers=None, last_known_state=None) is False

    def test_exhausted_in_headers(self):
        from agent.nous_rate_guard import is_genuine_nous_rate_limit
        h = {
            "x-ratelimit-remaining-requests": "0",
            "x-ratelimit-reset-requests": "300",
        }
        assert is_genuine_nous_rate_limit(headers=h) is True

    def test_transient_429(self):
        """Short reset window → transient, not genuine."""
        from agent.nous_rate_guard import is_genuine_nous_rate_limit
        h = {
            "x-ratelimit-remaining-requests": "0",
            "x-ratelimit-reset-requests": "5",
        }
        assert is_genuine_nous_rate_limit(headers=h) is False

    def test_exhausted_in_last_known_state(self):
        from agent.nous_rate_guard import is_genuine_nous_rate_limit

        class FakeBucket:
            def __init__(self, limit, remaining, reset):
                self.limit = limit
                self.remaining = remaining
                self.remaining_seconds_now = reset

        class FakeState:
            requests_hour = FakeBucket(100, 0, 300)
            tokens_hour = None
            requests_min = None
            tokens_min = None

        assert is_genuine_nous_rate_limit(last_known_state=FakeState()) is True


# ---------------------------------------------------------------------------
# RateGuard class (from nous_rate_guard.py shim)
# ---------------------------------------------------------------------------

class TestRateGuardClass:
    def test_allows_within_limit(self):
        from nous_rate_guard import RateGuard
        rg = RateGuard(max_per_second=100, max_concurrent=5)
        assert rg.izin_ver("deepseek") is True

    def test_blocks_concurrent_overflow(self):
        from nous_rate_guard import RateGuard
        import time as _time_mod
        t = [1000.0]
        with patch("nous_rate_guard._time.monotonic", side_effect=lambda: t.__setitem__(0, t[0] + 1) or t[0]):
            rg = RateGuard(max_per_second=10000, max_concurrent=2)
            rg.istek_basla("a")
            rg.istek_basla("b")
            assert rg.izin_ver("c") is False  # 2/2 active
            rg.istek_bitir("a")
            assert rg.izin_ver("c") is True  # 1/2 active

    def test_blocks_rate_limit(self):
        from nous_rate_guard import RateGuard
        rg = RateGuard(max_per_second=1, max_concurrent=10)
        rg.istek_basla("a")
        assert rg.izin_ver("b") is False  # too fast

    def test_basla_bitir_lifecycle(self):
        from nous_rate_guard import RateGuard
        rg = RateGuard(max_per_second=1000, max_concurrent=5)
        rg.istek_basla("x")
        assert "x" in rg._aktif
        rg.istek_bitir("x")
        assert "x" not in rg._aktif

    def test_bitir_unknown_provider(self):
        from nous_rate_guard import RateGuard
        rg = RateGuard()
        rg.istek_bitir("nonexistent")  # should not raise
