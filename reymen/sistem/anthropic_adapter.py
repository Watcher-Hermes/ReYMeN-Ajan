# -*- coding: utf-8 -*-
"""Anthropic Messages API adaptörü — OpenAI formatından Anthropic formatına dönüşüm.

Adapted from Hermes Agent (MIT License, Nous Research)
https://github.com/NousResearch/hermes-agent

Temel işlevler:
  - OpenAI mesaj formatını Anthropic Messages API formatına çevirme
  - API key (x-api-key header) ve OAuth token (Bearer) auth desteği
  - Streaming destekli mesaj oluşturma
  - Model algılama: claude-sonnet-4, claude-opus-4, claude-3.5-haiku vb.
  - Thinking/reasoning modu desteği

Kullanım:
    from reymen.sistem.anthropic_adapter import (
        build_anthropic_client,
        convert_messages_to_anthropic,
        build_anthropic_kwargs,
        normalize_model_name,
    )
"""

from __future__ import annotations

import copy
import json
import logging
import math
import os
import re
import secrets
import stat
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════════
# SDK Erişimi — Tembel import ile anthropic SDK'sı
# ═══════════════════════════════════════════════════════════════════════════════

_anthropic_sdk: Any = ...  # sentinel — None means "tried and missing"


def _get_anthropic_sdk() -> Any:
    """``anthropic`` SDK modülünü tembel olarak içe aktarır. Yoksa None döner."""
    global _anthropic_sdk
    if _anthropic_sdk is ...:
        try:
            import anthropic as _sdk
            _anthropic_sdk = _sdk
        except ImportError:
            _anthropic_sdk = None
    return _anthropic_sdk


# ═══════════════════════════════════════════════════════════════════════════════
# Model Algılama ve Sınıflandırma
# ═══════════════════════════════════════════════════════════════════════════════

# Thinking bütçe seviyeleri (effort → token bütçesi)
THINKING_BUDGET = {"xhigh": 32000, "high": 16000, "medium": 8000, "low": 4000}

# Uyumlu thinking effort eşleme (ReYMeN effort → Anthropic adaptive effort)
ADAPTIVE_EFFORT_MAP = {
    "max": "max",
    "xhigh": "xhigh",
    "high": "high",
    "medium": "medium",
    "low": "low",
    "minimal": "low",
}

# Eski Claude aileleri — adaptive thinking desteklemez (sadece manual thinking)
_LEGACY_MANUAL_THINKING_CLAUDE_SUBSTRINGS = (
    "claude-3",
    "claude-opus-4-0", "claude-opus-4.0", "claude-opus-4-1", "claude-opus-4.1",
    "claude-sonnet-4-0", "claude-sonnet-4.0",
    "claude-opus-4-2025", "claude-sonnet-4-2025",
    "claude-opus-4-5", "claude-opus-4.5",
    "claude-sonnet-4-5", "claude-sonnet-4.5",
    "claude-haiku-4-5", "claude-haiku-4.5",
)

# xhigh desteklemeyen modeller (4.6 ailesi)
_NO_XHIGH_CLAUDE_SUBSTRINGS = (
    "claude-opus-4-6", "claude-opus-4.6",
    "claude-sonnet-4-6", "claude-sonnet-4.6",
)

# Max output token limitleri (model prefix → max_tokens)
_ANTHROPIC_OUTPUT_LIMITS = {
    "claude-fable": 128_000,
    "claude-opus-4-8": 128_000,
    "claude-opus-4-7": 128_000,
    "claude-opus-4-6": 128_000,
    "claude-sonnet-4-6": 64_000,
    "claude-opus-4-5": 64_000,
    "claude-sonnet-4-5": 64_000,
    "claude-haiku-4-5": 64_000,
    "claude-opus-4": 32_000,
    "claude-sonnet-4": 64_000,
    "claude-3-7-sonnet": 128_000,
    "claude-3-5-sonnet": 8_192,
    "claude-3-5-haiku": 8_192,
    "claude-3-opus": 4_096,
    "claude-3-sonnet": 4_096,
    "claude-3-haiku": 4_096,
    "minimax": 131_072,
    "qwen3": 65_536,
}
_ANTHROPIC_DEFAULT_OUTPUT_LIMIT = 128_000


def _is_claude_model(model: str | None) -> bool:
    """Verilen model adının Claude ailesinden olup olmadığını kontrol eder."""
    return "claude" in (model or "").lower()


def _get_anthropic_max_output(model: str) -> int:
    """Claude modeli için maksimum output token limitini bulur.

    Alt string eşleme kullanarak tarih damgalı model ID'lerini
    ve varyant eklerini düzgün eşler.
    """
    m = model.lower().replace(".", "-")
    best_key = ""
    best_val = _ANTHROPIC_DEFAULT_OUTPUT_LIMIT
    for key, val in _ANTHROPIC_OUTPUT_LIMITS.items():
        if key in m and len(key) > len(best_key):
            best_key = key
            best_val = val
    return best_val


def _supports_adaptive_thinking(model: str) -> bool:
    """Adaptive thinking destekleyen Claude modelleri için True döner (4.6+)."""
    if not _is_claude_model(model):
        return False
    m = model.lower()
    return not any(v in m for v in _LEGACY_MANUAL_THINKING_CLAUDE_SUBSTRINGS)


def _supports_xhigh_effort(model: str) -> bool:
    """'xhigh' adaptive effort seviyesini destekleyen modeller için True."""
    if not _supports_adaptive_thinking(model):
        return False
    m = model.lower()
    return not any(v in m for v in _NO_XHIGH_CLAUDE_SUBSTRINGS)


def _forbids_sampling_params(model: str) -> bool:
    """4.7+ modellerde temperature/top_p/top_k'yı reddeden modeller için True."""
    if not _is_claude_model(model):
        return False
    m = model.lower()
    if any(v in m for v in _NO_XHIGH_CLAUDE_SUBSTRINGS):
        return False
    return not any(v in m for v in _LEGACY_MANUAL_THINKING_CLAUDE_SUBSTRINGS)


def _supports_fast_mode(model: str) -> bool:
    """Fast Mode (speed=fast) destekleyen modeller için True (Opus 4.6)."""
    return any(v in model for v in ("opus-4-6", "opus-4.6"))


# ═══════════════════════════════════════════════════════════════════════════════
# Auth Yardımcıları
# ═══════════════════════════════════════════════════════════════════════════════

def _normalize_base_url_text(base_url: Any) -> str:
    """SDK/base transport URL değerlerini düz string'e dönüştürür."""
    if not base_url:
        return ""
    return str(base_url).strip()


def _is_third_party_anthropic_endpoint(base_url: str | None) -> bool:
    """Anthropic dışı Anthropic Messages API uç noktaları için True."""
    normalized = _normalize_base_url_text(base_url)
    if not normalized:
        return False
    normalized = normalized.rstrip("/").lower()
    if "anthropic.com" in normalized:
        return False
    return True


def _is_oauth_token(key: str) -> bool:
    """Key'in Anthropic OAuth/setup token olup olmadığını kontrol eder."""
    if not key:
        return False
    if key.startswith("sk-ant-api"):
        return False
    if key.startswith("sk-ant-"):
        return True
    if key.startswith("eyJ"):
        return True
    if key.startswith("cc-"):
        return True
    return False


def _requires_bearer_auth(base_url: str | None) -> bool:
    """Bearer auth gerektiren Anthropic uyumlu sağlayıcılar için True."""
    normalized = _normalize_base_url_text(base_url)
    if not normalized:
        return False
    normalized = normalized.rstrip("/").lower()
    return (
        normalized.startswith(("https://api.minimax.io/anthropic", "https://api.minimaxi.com/anthropic"))
        or "azure.com" in normalized
    )


# ═══════════════════════════════════════════════════════════════════════════════
# Beta Başlıkları
# ═══════════════════════════════════════════════════════════════════════════════

_COMMON_BETAS = [
    "interleaved-thinking-2025-05-14",
    "fine-grained-tool-streaming-2025-05-14",
]
_TOOL_STREAMING_BETA = "fine-grained-tool-streaming-2025-05-14"
_CONTEXT_1M_BETA = "context-1m-2025-08-07"
_FAST_MODE_BETA = "fast-mode-2026-02-01"
_OAUTH_ONLY_BETAS = [
    "claude-code-20250219",
    "oauth-2025-04-20",
]


def _common_betas_for_base_url(
    base_url: str | None,
    *,
    drop_context_1m_beta: bool = False,
) -> list[str]:
    """Uç noktaya uygun beta başlıklarını döner."""
    betas = list(_COMMON_BETAS)
    if drop_context_1m_beta:
        betas = [b for b in betas if b != _CONTEXT_1M_BETA]
    normalized = _normalize_base_url_text(base_url).lower() if base_url else ""
    if "azure.com" in normalized and not drop_context_1m_beta:
        betas.append(_CONTEXT_1M_BETA)
    if normalized.startswith(("https://api.minimax.io/anthropic", "https://api.minimaxi.com/anthropic")):
        stripped = {_TOOL_STREAMING_BETA, _CONTEXT_1M_BETA}
        return [b for b in betas if b not in stripped]
    return betas


# ═══════════════════════════════════════════════════════════════════════════════
# Client Oluşturma
# ═══════════════════════════════════════════════════════════════════════════════

def build_anthropic_client(
    api_key: str | Any,
    base_url: str | None = None,
    timeout: float | None = None,
    *,
    drop_context_1m_beta: bool = False,
) -> Any:
    """Anthropic istemcisi oluşturur, auth türünü otomatik algılar.

    ``api_key`` şu türleri kabul eder:
      - Normal API key (sk-ant-api*) → x-api-key header
      - OAuth setup-token (sk-ant-oat*) → Bearer auth
      - JWT (eyJ*) → Bearer auth

    *timeout* verilirse 900s yerine o değeri kullanır.
    """
    _sdk = _get_anthropic_sdk()
    if _sdk is None:
        raise ImportError(
            "Anthropic sağlayıcısı için 'anthropic' paketi gerekli. "
            "Kurulum: pip install 'anthropic>=0.39.0'"
        )

    try:
        from httpx import Timeout
    except ImportError:
        Timeout = None  # type: ignore[assignment,misc]

    normalized_base_url = _normalize_base_url_text(base_url)
    if normalized_base_url:
        normalized_base_url = re.sub(r"/v1/?$", "", normalized_base_url.rstrip("/"))

    _read_timeout = timeout if (isinstance(timeout, (int, float)) and timeout > 0) else 900.0
    kwargs: Dict[str, Any] = {}
    if Timeout is not None:
        kwargs["timeout"] = Timeout(timeout=float(_read_timeout), connect=10.0)

    if normalized_base_url:
        kwargs["base_url"] = normalized_base_url

    common_betas = _common_betas_for_base_url(
        normalized_base_url, drop_context_1m_beta=drop_context_1m_beta,
    )

    if _requires_bearer_auth(normalized_base_url):
        kwargs["auth_token"] = api_key
        if common_betas:
            kwargs["default_headers"] = {"anthropic-beta": ",".join(common_betas)}
    elif _is_third_party_anthropic_endpoint(base_url):
        kwargs["api_key"] = api_key
        if common_betas:
            kwargs["default_headers"] = {"anthropic-beta": ",".join(common_betas)}
    elif _is_oauth_token(api_key):
        all_betas = common_betas + _OAUTH_ONLY_BETAS
        kwargs["auth_token"] = api_key
        kwargs["default_headers"] = {
            "anthropic-beta": ",".join(all_betas),
        }
    else:
        kwargs["api_key"] = api_key
        if common_betas:
            kwargs["default_headers"] = {"anthropic-beta": ",".join(common_betas)}

    return _sdk.Anthropic(**kwargs)


# ═══════════════════════════════════════════════════════════════════════════════
# Token Çözümleme
# ═══════════════════════════════════════════════════════════════════════════════

def resolve_anthropic_token() -> Optional[str]:
    """Tüm mevcut kaynaklardan Anthropic token'ını çözer.

    Öncelik sırası:
      1. ANTHROPIC_TOKEN env değişkeni
      2. CLAUDE_CODE_OAUTH_TOKEN env değişkeni
      3. ANTHROPIC_API_KEY env değişkeni

    Token string veya None döner.
    """
    token = os.getenv("ANTHROPIC_TOKEN", "").strip()
    if token:
        return token

    cc_token = os.getenv("CLAUDE_CODE_OAUTH_TOKEN", "").strip()
    if cc_token:
        return cc_token

    api_key = os.getenv("ANTHROPIC_API_KEY", "").strip()
    if api_key:
        return api_key

    return None


# ═══════════════════════════════════════════════════════════════════════════════
# Model İsmi Normalizasyonu
# ═══════════════════════════════════════════════════════════════════════════════

def normalize_model_name(model: str, preserve_dots: bool = False) -> str:
    """Model adını Anthropic API için normalize eder.

    - 'anthropic/' ön ekini kaldırır
    - Noktaları tirelere çevirir (claude-opus-4.6 → claude-opus-4-6)
    - Bedrock model ID'lerini korur (anthropic.claude-opus-4-7)
    """
    lower = model.lower()
    if lower.startswith("anthropic/"):
        model = model[len("anthropic/"):]
    if not preserve_dots:
        if lower.startswith("anthropic.") or lower.startswith(("global.", "us.", "eu.", "ap.", "jp.")):
            return model
        _lower = model.lower()
        if _lower.startswith("claude-") or _lower.startswith("anthropic/"):
            model = model.replace(".", "-")
    return model


def _sanitize_tool_id(tool_id: str) -> str:
    """Araç çağrısı ID'sini Anthropic API için temizler."""
    if not tool_id:
        return "tool_0"
    sanitized = re.sub(r"[^a-zA-Z0-9_-]", "_", tool_id)
    return sanitized or "tool_0"


# ═══════════════════════════════════════════════════════════════════════════════
# Araç Dönüştürme (OpenAI → Anthropic)
# ═══════════════════════════════════════════════════════════════════════════════

def _normalize_tool_input_schema(schema: Any) -> Dict[str, Any]:
    """Araç şemalarını Anthropic için normalize eder.

    Anthropic'in reddettiği nullable union'ları (anyOf) temizler
    ve üst seviye oneOf/allOf/anyOf anahtarlarını düşürür.
    """
    if not schema:
        return {"type": "object", "properties": {}}
    if not isinstance(schema, dict):
        return {"type": "object", "properties": {}}
    normalized = dict(schema)
    # nullable union temizliği
    if "anyOf" in normalized and isinstance(normalized["anyOf"], list):
        non_null = [t for t in normalized["anyOf"] if t.get("type") != "null"]
        if len(non_null) == 1:
            merged = dict(non_null[0])
            for k, v in normalized.items():
                if k not in ("anyOf", "type"):
                    merged.setdefault(k, v)
            normalized = merged
    # Üst seviye union temizliği
    banned = {"oneOf", "allOf", "anyOf"}
    if banned & normalized.keys():
        normalized = {k: v for k, v in normalized.items() if k not in banned}
        if "type" not in normalized:
            normalized["type"] = "object"
    if normalized.get("type") == "object" and not isinstance(normalized.get("properties"), dict):
        normalized = {**normalized, "properties": {}}
    return normalized


def convert_tools_to_anthropic(tools: List[Dict]) -> List[Dict]:
    """OpenAI araç tanımlarını Anthropic formatına çevirer."""
    if not tools:
        return []
    result = []
    seen_names: set = set()
    for t in tools:
        fn = t.get("function", {})
        name = fn.get("name", "")
        if name and name in seen_names:
            logger.warning(
                "convert_tools_to_anthropic: tekrarlayan araç adı '%s' — ikincisi düşürülüyor",
                name,
            )
            continue
        if name:
            seen_names.add(name)
        anthropic_tool: Dict[str, Any] = {
            "name": name,
            "description": fn.get("description", ""),
            "input_schema": _normalize_tool_input_schema(
                fn.get("parameters", {"type": "object", "properties": {}})
            ),
        }
        cache_control = t.get("cache_control")
        if isinstance(cache_control, dict):
            anthropic_tool["cache_control"] = dict(cache_control)
        result.append(anthropic_tool)
    return result


# ═══════════════════════════════════════════════════════════════════════════════
# Mesaj Dönüştürme (OpenAI → Anthropic)
# ═══════════════════════════════════════════════════════════════════════════════

def _image_source_from_openai_url(url: str) -> Dict[str, str]:
    """OpenAI-style görsel URL'ini Anthropic image source formatına çevirer."""
    url = str(url or "").strip()
    if not url:
        return {"type": "url", "url": ""}
    if url.startswith("data:"):
        header, _, data = url.partition(",")
        media_type = "image/jpeg"
        if header.startswith("data:"):
            mime_part = header[len("data:"):].split(";", 1)[0].strip()
            if mime_part.startswith("image/"):
                media_type = mime_part
        return {"type": "base64", "media_type": media_type, "data": data}
    return {"type": "url", "url": url}


def _convert_content_part_to_anthropic(part: Any) -> Optional[Dict[str, Any]]:
    """Tek bir OpenAI-style içerik parçasını Anthropic formatına çevirer."""
    if part is None:
        return None
    if isinstance(part, str):
        return {"type": "text", "text": part}
    if not isinstance(part, dict):
        return {"type": "text", "text": str(part)}

    ptype = part.get("type")
    if ptype == "input_text":
        block: Dict[str, Any] = {"type": "text", "text": part.get("text", "")}
    elif ptype == "text":
        block = {"type": "text", "text": part.get("text", "")}
        cits = part.get("citations")
        if isinstance(cits, list) and cits:
            block["citations"] = cits
    elif ptype in {"image_url", "input_image"}:
        image_value = part.get("image_url", {})
        url = image_value.get("url", "") if isinstance(image_value, dict) else str(image_value or "")
        block = {"type": "image", "source": _image_source_from_openai_url(url)}
    else:
        block = dict(part)

    if isinstance(part.get("cache_control"), dict) and "cache_control" not in block:
        block["cache_control"] = dict(part["cache_control"])
    return block


def _convert_content_to_anthropic(content: Any) -> Any:
    """OpenAI-style çoklu medya içerik dizilerini Anthropic bloklarına çevirer."""
    if not isinstance(content, list):
        return content
    converted = []
    for part in content:
        block = _convert_content_part_to_anthropic(part)
        if block is not None:
            converted.append(block)
    return converted


def _content_parts_to_anthropic_blocks(parts: Any) -> List[Dict[str, Any]]:
    """OpenAI-style araç mesajı içerik parçalarını Anthropic tool_result iç bloklarına çevirer."""
    if not isinstance(parts, list):
        return []
    out: List[Dict[str, Any]] = []
    for part in parts:
        block = _convert_content_part_to_anthropic(part)
        if not block:
            continue
        btype = block.get("type")
        if btype == "text":
            text_val = block.get("text")
            if isinstance(text_val, str) and text_val:
                out.append({"type": "text", "text": text_val})
        elif btype == "image":
            src = block.get("source")
            if isinstance(src, dict) and src:
                out.append({"type": "image", "source": src})
    return out


def _extract_preserved_thinking_blocks(message: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Mesajda korunmuş Anthropic thinking bloklarını döner."""
    raw_details = message.get("reasoning_details")
    if not isinstance(raw_details, list):
        return []
    preserved: List[Dict[str, Any]] = []
    for detail in raw_details:
        if not isinstance(detail, dict):
            continue
        block_type = str(detail.get("type", "") or "").strip().lower()
        if block_type not in {"thinking", "redacted_thinking"}:
            continue
        preserved.append(copy.deepcopy(detail))
    return preserved


def _sanitize_replay_block(b: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Yeniden oynatma için Anthropic içerik bloğundaki output-only alanları temizler."""
    if not isinstance(b, dict):
        return None
    btype = b.get("type")
    if btype == "text":
        out: Dict[str, Any] = {"type": "text", "text": b.get("text", "")}
        cits = b.get("citations")
        if isinstance(cits, list) and cits:
            out["citations"] = cits
        if isinstance(b.get("cache_control"), dict):
            out["cache_control"] = b["cache_control"]
        return out
    if btype == "thinking":
        out = {"type": "thinking", "thinking": b.get("thinking", "")}
        if b.get("signature"):
            out["signature"] = b["signature"]
        return out
    if btype == "redacted_thinking":
        return {"type": "redacted_thinking", "data": b["data"]} if b.get("data") else None
    if btype == "tool_use":
        out = {
            "type": "tool_use",
            "id": _sanitize_tool_id(b.get("id", "")),
            "name": b.get("name", ""),
            "input": b.get("input", {}),
        }
        if isinstance(b.get("cache_control"), dict):
            out["cache_control"] = b["cache_control"]
        return out
    if btype == "image":
        src = b.get("source")
        return {"type": "image", "source": src} if isinstance(src, dict) else None
    return None


def _convert_assistant_message(m: Dict[str, Any]) -> Dict[str, Any]:
    """Asistan mesajını Anthropic içerik bloklarına çevirer.

    Thinking blokları, düzenli içerik ve araç çağrılarını işler.
    """
    content = m.get("content", "")
    # Anthropic interleaved-thinking hızlı yol
    ordered_blocks = m.get("anthropic_content_blocks")
    if isinstance(ordered_blocks, list) and ordered_blocks:
        redacted_input_by_id: Dict[str, Any] = {}
        for tc in m.get("tool_calls", []) or []:
            if not isinstance(tc, dict):
                continue
            fn = tc.get("function", {}) or {}
            raw_args = fn.get("arguments", "{}")
            try:
                parsed_args = json.loads(raw_args) if isinstance(raw_args, str) else raw_args
            except (json.JSONDecodeError, ValueError):
                parsed_args = {}
            redacted_input_by_id[_sanitize_tool_id(tc.get("id", ""))] = parsed_args
        replayed: List[Dict[str, Any]] = []
        for b in ordered_blocks:
            clean = _sanitize_replay_block(b)
            if clean is None:
                continue
            if clean.get("type") == "tool_use":
                redacted = redacted_input_by_id.get(clean.get("id", ""))
                if redacted is not None:
                    clean["input"] = redacted
            replayed.append(clean)
        if replayed:
            return {"role": "assistant", "content": replayed}

    blocks = _extract_preserved_thinking_blocks(m)
    if content:
        if isinstance(content, list):
            converted_content = _convert_content_to_anthropic(content)
            if isinstance(converted_content, list):
                blocks.extend(converted_content)
        else:
            blocks.append({"type": "text", "text": str(content)})
    for tc in m.get("tool_calls", []):
        if not tc or not isinstance(tc, dict):
            continue
        fn = tc.get("function", {})
        args = fn.get("arguments", "{}")
        try:
            parsed_args = json.loads(args) if isinstance(args, str) else args
        except (json.JSONDecodeError, ValueError):
            parsed_args = {}
        blocks.append({
            "type": "tool_use",
            "id": _sanitize_tool_id(tc.get("id", "")),
            "name": fn.get("name", ""),
            "input": parsed_args,
        })
    # reasoning_content → thinking bloğu (Kimi/DeepSeek için)
    reasoning_content = m.get("reasoning_content")
    _already_has_thinking = any(
        isinstance(b, dict) and b.get("type") in {"thinking", "redacted_thinking"}
        for b in blocks
    )
    if isinstance(reasoning_content, str) and not _already_has_thinking:
        blocks.insert(0, {"type": "thinking", "thinking": reasoning_content})
    effective = blocks or content
    if not effective or effective == "":
        effective = [{"type": "text", "text": "(empty)"}]
    return {"role": "assistant", "content": effective}


def _convert_tool_message_to_result(
    result: List[Dict[str, Any]], m: Dict[str, Any]
) -> None:
    """Araç mesajını Anthropic tool_result'a çevirer, ardışık sonuçları birleştirir."""
    content = m.get("content", "")
    multimodal_blocks: Optional[List[Dict[str, Any]]] = None
    if isinstance(content, dict) and content.get("_multimodal"):
        multimodal_blocks = _content_parts_to_anthropic_blocks(
            content.get("content") or []
        )
        if not multimodal_blocks and content.get("text_summary"):
            multimodal_blocks = [{"type": "text", "text": str(content["text_summary"])}]
    elif isinstance(content, list):
        converted = _content_parts_to_anthropic_blocks(content)
        if any(b.get("type") == "image" for b in converted):
            multimodal_blocks = converted
    if multimodal_blocks is None:
        stashed = m.get("_anthropic_content_blocks")
        if isinstance(stashed, list) and stashed:
            text_content = content if isinstance(content, str) and content.strip() else None
            multimodal_blocks = (
                [{"type": "text", "text": text_content}] + stashed
                if text_content else list(stashed)
            )
    if multimodal_blocks:
        result_content: Any = multimodal_blocks
    elif isinstance(content, str):
        result_content = content
    else:
        result_content = json.dumps(content) if content else "(no output)"
    if not result_content:
        result_content = "(no output)"
    tool_result = {
        "type": "tool_result",
        "tool_use_id": _sanitize_tool_id(m.get("tool_call_id", "")),
        "content": result_content,
    }
    if isinstance(m.get("cache_control"), dict):
        tool_result["cache_control"] = dict(m["cache_control"])
    if (
        result
        and result[-1]["role"] == "user"
        and isinstance(result[-1]["content"], list)
        and result[-1]["content"]
        and result[-1]["content"][0].get("type") == "tool_result"
    ):
        result[-1]["content"].append(tool_result)
    else:
        result.append({"role": "user", "content": [tool_result]})


def _convert_user_message(content: Any) -> Dict[str, Any]:
    """Kullanıcı mesajını Anthropic formatına çevirer."""
    if isinstance(content, list):
        converted_blocks = _convert_content_to_anthropic(content)
        if not converted_blocks or all(
            b.get("text", "").strip() == ""
            for b in converted_blocks
            if isinstance(b, dict) and b.get("type") == "text"
        ):
            converted_blocks = [{"type": "text", "text": "(empty message)"}]
        return {"role": "user", "content": converted_blocks}
    else:
        if not content or (isinstance(content, str) and not content.strip()):
            content = "(empty message)"
        return {"role": "user", "content": content}


def _strip_orphaned_tool_blocks(result: List[Dict[str, Any]]) -> None:
    """Eşleşmeyen tool_use/tool_result bloklarını temizler.

    Bağlam sıkıştırma veya oturum kısaltma her iki tarafı da
    kaldırabilir — Anthropic her ikisini de HTTP 400 ile reddeder.
    """
    tool_result_ids = set()
    for m in result:
        if m["role"] == "user" and isinstance(m["content"], list):
            for block in m["content"]:
                if block.get("type") == "tool_result":
                    tool_result_ids.add(block.get("tool_use_id"))
    for m in result:
        if m["role"] == "assistant" and isinstance(m["content"], list):
            kept = [
                b for b in m["content"]
                if b.get("type") != "tool_use" or b.get("id") in tool_result_ids
            ]
            if len(kept) != len(m["content"]) and any(
                isinstance(b, dict) and b.get("type") in {"thinking", "redacted_thinking"}
                for b in m["content"]
            ):
                m["_thinking_signature_invalidated"] = True
            m["content"] = kept
            if not m["content"]:
                m["content"] = [{"type": "text", "text": "(tool call removed)"}]

    tool_use_ids = set()
    for m in result:
        if m["role"] == "assistant" and isinstance(m["content"], list):
            for block in m["content"]:
                if block.get("type") == "tool_use":
                    tool_use_ids.add(block.get("id"))
    for m in result:
        if m["role"] == "user" and isinstance(m["content"], list):
            m["content"] = [
                b for b in m["content"]
                if b.get("type") != "tool_result" or b.get("tool_use_id") in tool_use_ids
            ]
            if not m["content"]:
                m["content"] = [{"type": "text", "text": "(tool result removed)"}]


def _merge_consecutive_roles(result: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Ardışık aynı rollü mesajları birleştirir (Anthropic alternation zorunluluğu)."""
    fixed = []
    for m in result:
        if fixed and fixed[-1]["role"] == m["role"]:
            if m["role"] == "user":
                prev_content = fixed[-1]["content"]
                curr_content = m["content"]
                if isinstance(prev_content, str) and isinstance(curr_content, str):
                    fixed[-1]["content"] = prev_content + "\n" + curr_content
                elif isinstance(prev_content, list) and isinstance(curr_content, list):
                    fixed[-1]["content"] = prev_content + curr_content
                else:
                    if isinstance(prev_content, str):
                        prev_content = [{"type": "text", "text": prev_content}]
                    if isinstance(curr_content, str):
                        curr_content = [{"type": "text", "text": curr_content}]
                    fixed[-1]["content"] = prev_content + curr_content
            else:
                if m.get("_thinking_signature_invalidated"):
                    fixed[-1]["_thinking_signature_invalidated"] = True
                if isinstance(m["content"], list):
                    m["content"] = [
                        b for b in m["content"]
                        if not (isinstance(b, dict) and b.get("type") in {"thinking", "redacted_thinking"})
                    ]
                prev_blocks = fixed[-1]["content"]
                curr_blocks = m["content"]
                if isinstance(prev_blocks, list) and isinstance(curr_blocks, list):
                    fixed[-1]["content"] = prev_blocks + curr_blocks
                elif isinstance(prev_blocks, str) and isinstance(curr_blocks, str):
                    fixed[-1]["content"] = prev_blocks + "\n" + curr_blocks
                else:
                    if isinstance(prev_blocks, str):
                        prev_blocks = [{"type": "text", "text": prev_blocks}]
                    if isinstance(curr_blocks, str):
                        curr_blocks = [{"type": "text", "text": curr_blocks}]
                    fixed[-1]["content"] = prev_blocks + curr_blocks
        else:
            fixed.append(m)
    return fixed


def _manage_thinking_signatures(
    result: List[Dict[str, Any]], base_url: str | None, model: str | None
) -> None:
    """Thinking bloklarını uç noktaya göre korur veya temizler.

    Anthropic thinking bloklarını tüm tur içeriğine karşı imzalar.
    Üçüncü taraf uç noktalar bu imzaları doğrulayamaz.
    """
    _THINKING_TYPES = frozenset(("thinking", "redacted_thinking"))
    _is_third_party = _is_third_party_anthropic_endpoint(base_url)

    last_assistant_idx = None
    for i in range(len(result) - 1, -1, -1):
        if result[i].get("role") == "assistant":
            last_assistant_idx = i
            break

    for idx, m in enumerate(result):
        if m.get("role") != "assistant" or not isinstance(m.get("content"), list):
            continue
        if _is_third_party or idx != last_assistant_idx:
            stripped = [
                b for b in m["content"]
                if not (isinstance(b, dict) and b.get("type") in _THINKING_TYPES)
            ]
            m["content"] = stripped or [{"type": "text", "text": "(thinking elided)"}]
        else:
            signature_dead = bool(m.get("_thinking_signature_invalidated"))
            new_content = []
            for b in m["content"]:
                if not isinstance(b, dict) or b.get("type") not in _THINKING_TYPES:
                    new_content.append(b)
                    continue
                if signature_dead:
                    thinking_text = b.get("thinking", "")
                    if thinking_text:
                        new_content.append({"type": "text", "text": thinking_text})
                    continue
                if b.get("type") == "redacted_thinking":
                    if b.get("data"):
                        new_content.append(b)
                elif b.get("signature"):
                    new_content.append(b)
                else:
                    thinking_text = b.get("thinking", "")
                    if thinking_text:
                        new_content.append({"type": "text", "text": thinking_text})
            m["content"] = new_content or [{"type": "text", "text": "(empty)"}]
        for b in m["content"]:
            if isinstance(b, dict) and b.get("type") in _THINKING_TYPES:
                b.pop("cache_control", None)
        m.pop("_thinking_signature_invalidated", None)


def _evict_old_screenshots(result: List[Dict[str, Any]]) -> None:
    """Sadece en güncel ekran görüntülerini korur (token tasarrufu)."""
    _MAX_KEEP_IMAGES = 3
    _image_count = 0
    for msg in reversed(result):
        content = msg.get("content")
        if not isinstance(content, list):
            continue
        for block in content:
            if not isinstance(block, dict) or block.get("type") != "tool_result":
                continue
            inner = block.get("content")
            if not isinstance(inner, list):
                continue
            has_image = any(
                isinstance(b, dict) and b.get("type") == "image" for b in inner
            )
            if not has_image:
                continue
            _image_count += 1
            if _image_count > _MAX_KEEP_IMAGES:
                block["content"] = [
                    b if b.get("type") != "image"
                    else {"type": "text", "text": "[screenshot removed to save context]"}
                    for b in inner
                ]


def convert_messages_to_anthropic(
    messages: List[Dict],
    base_url: str | None = None,
    model: str | None = None,
) -> Tuple[Optional[Any], List[Dict]]:
    """OpenAI formatındaki mesajları Anthropic formatına çevirer.

    Returns:
        (system_prompt, anthropic_messages) tuple'ı.
        System mesajları ayrı parametre olarak çıkarılır.

    Üçüncü taraf uç noktalarda thinking bloğu imzaları temizlenir.
    """
    system = None
    result: List[Dict[str, Any]] = []

    for m in messages:
        role = m.get("role", "user")
        content = m.get("content", "")

        if role == "system":
            if isinstance(content, list):
                has_cache = any(p.get("cache_control") for p in content if isinstance(p, dict))
                if has_cache:
                    system = [p for p in content if isinstance(p, dict)]
                else:
                    system = "\n".join(p["text"] for p in content if p.get("type") == "text")
            else:
                system = content
            continue

        if role == "assistant":
            result.append(_convert_assistant_message(m))
            continue

        if role == "tool":
            _convert_tool_message_to_result(result, m)
            continue

        result.append(_convert_user_message(content))

    _strip_orphaned_tool_blocks(result)
    result = _merge_consecutive_roles(result)
    _manage_thinking_signatures(result, base_url, model)
    _evict_old_screenshots(result)

    return system, result


# ═══════════════════════════════════════════════════════════════════════════════
# Anthropic Kwargs Oluşturma
# ═══════════════════════════════════════════════════════════════════════════════

_RESPONSES_ONLY_KWARGS = frozenset(
    {"instructions", "input", "store", "parallel_tool_calls"}
)


def sanitize_anthropic_kwargs(api_kwargs: Any, *, log_prefix: str = "") -> Any:
    """Anthropic Messages SDK çağrısından önce Responses-API-only anahtarları temizler."""
    if not isinstance(api_kwargs, dict):
        return api_kwargs
    leaked = _RESPONSES_ONLY_KWARGS.intersection(api_kwargs)
    if leaked:
        for _key in leaked:
            api_kwargs.pop(_key, None)
        logger.warning(
            "%sResponses-only anahtarları temizlendi: %s",
            log_prefix, sorted(leaked),
        )
    return api_kwargs


def build_anthropic_kwargs(
    model: str,
    messages: List[Dict],
    tools: Optional[List[Dict]],
    max_tokens: Optional[int],
    reasoning_config: Optional[Dict[str, Any]],
    tool_choice: Optional[str] = None,
    is_oauth: bool = False,
    preserve_dots: bool = False,
    context_length: Optional[int] = None,
    base_url: str | None = None,
    fast_mode: bool = False,
    drop_context_1m_beta: bool = False,
) -> Dict[str, Any]:
    """anthropic.messages.create() için kwargs oluşturur.

    Args:
        model: Model adı (claude-sonnet-4, claude-opus-4 vb.)
        messages: OpenAI formatında mesaj listesi
        tools: OpenAI formatında araç tanımları
        max_tokens: Maksimum output token (None = model varsayılanı)
        reasoning_config: Thinking/reasoning yapılandırması
        tool_choice: Araç seçim stratejisi (auto/required/none/isim)
        is_oauth: OAuth kimlik doğrulama modu
        preserve_dots: Model adındaki noktaları koru
        context_length: Toplam bağlam penceresi boyutu
        base_url: Üçüncü taraf API URL'si
        fast_mode: Hızlı mod (Opus 4.6)
    """
    system, anthropic_messages = convert_messages_to_anthropic(
        messages, base_url=base_url, model=model
    )
    anthropic_tools = convert_tools_to_anthropic(tools) if tools else []

    model = normalize_model_name(model, preserve_dots=preserve_dots)
    # max_tokens çözümleme
    resolved = None
    if max_tokens is not None and not isinstance(max_tokens, bool):
        if isinstance(max_tokens, (int, float)) and max_tokens > 0:
            try:
                if math.isfinite(max_tokens):
                    resolved = int(max_tokens)
            except Exception:
                pass
    if resolved is None:
        resolved = _get_anthropic_max_output(model)
    effective_max_tokens = max(resolved, 1)

    if context_length and effective_max_tokens > context_length:
        effective_max_tokens = max(context_length - 1, 1)

    # OAuth: Claude Code kimliği
    if is_oauth:
        cc_block = {"type": "text", "text": "You are Claude Code, Anthropic's official CLI for Claude."}
        if isinstance(system, list):
            system = [cc_block] + system
        elif isinstance(system, str) and system:
            system = [cc_block, {"type": "text", "text": system}]
        else:
            system = [cc_block]
        for block in system:
            if isinstance(block, dict) and block.get("type") == "text":
                text = block.get("text", "")
                text = text.replace("Hermes Agent", "ReYMeN Agent")
                text = text.replace("Hermes agent", "ReYMeN agent")
                text = text.replace("hermes-agent", "reymen-agent")
                text = text.replace("Nous Research", "ReYMeN Project")
                block["text"] = text

    kwargs: Dict[str, Any] = {
        "model": model,
        "messages": anthropic_messages,
        "max_tokens": effective_max_tokens,
    }

    if system:
        kwargs["system"] = system

    if anthropic_tools:
        kwargs["tools"] = anthropic_tools
        if tool_choice == "auto" or tool_choice is None:
            kwargs["tool_choice"] = {"type": "auto"}
        elif tool_choice == "required":
            kwargs["tool_choice"] = {"type": "any"}
        elif tool_choice == "none":
            kwargs.pop("tools", None)
        elif isinstance(tool_choice, str):
            kwargs["tool_choice"] = {"type": "tool", "name": tool_choice}

    # Thinking/reasoning yapılandırması
    if reasoning_config and isinstance(reasoning_config, dict):
        if reasoning_config.get("enabled") is not False and "haiku" not in model.lower():
            effort = str(reasoning_config.get("effort", "medium")).lower()
            budget = THINKING_BUDGET.get(effort, 8000)
            if _supports_adaptive_thinking(model):
                kwargs["thinking"] = {
                    "type": "adaptive",
                    "display": "summarized",
                }
                adaptive_effort = ADAPTIVE_EFFORT_MAP.get(effort, "medium")
                if adaptive_effort == "xhigh" and not _supports_xhigh_effort(model):
                    adaptive_effort = "max"
                kwargs["output_config"] = {"effort": adaptive_effort}
            else:
                kwargs["thinking"] = {"type": "enabled", "budget_tokens": budget}
                kwargs["temperature"] = 1
                kwargs["max_tokens"] = max(effective_max_tokens, budget + 4096)

    # 4.7+ sampling parametrelerini temizle
    if _forbids_sampling_params(model):
        for _sampling_key in ("temperature", "top_p", "top_k"):
            kwargs.pop(_sampling_key, None)

    # Fast mode (sadece Opus 4.6)
    if (
        fast_mode
        and not _is_third_party_anthropic_endpoint(base_url)
        and _supports_fast_mode(model)
    ):
        kwargs.setdefault("extra_body", {})["speed"] = "fast"
        betas = list(_common_betas_for_base_url(base_url, drop_context_1m_beta=drop_context_1m_beta))
        if is_oauth:
            betas.extend(_OAUTH_ONLY_BETAS)
        betas.append(_FAST_MODE_BETA)
        kwargs["extra_headers"] = {"anthropic-beta": ",".join(betas)}

    return kwargs


# ═══════════════════════════════════════════════════════════════════════════════
# Mesaj Oluşturma (Streaming Destekli)
# ═══════════════════════════════════ ile流_destekli

def _is_stream_unavailable_error(exc: Exception) -> bool:
    """Stream kullanılamıyorsa True döner."""
    err_lower = str(exc).lower()
    if "stream" in err_lower and "not supported" in err_lower:
        return True
    if "invokemodelwithresponsestream" in err_lower:
        return True
    return False


def create_anthropic_message(
    client: Any,
    api_kwargs: dict,
    *,
    log_prefix: str = "",
    prefer_stream: bool = True,
) -> Any:
    """Anthropic mesajı oluşturur, mümkünse stream üzerinden aggregation yapar.

    Bazı Anthropic uyumlu gateway'ler sadece SSE destekler —
    non-streaming istekleri görmezden gelir. Stream tercih edilir.
    """
    sanitize_anthropic_kwargs(api_kwargs, log_prefix=log_prefix)

    messages_api = getattr(client, "messages", None)
    stream_fn = getattr(messages_api, "stream", None)
    if prefer_stream and callable(stream_fn):
        stream_kwargs = dict(api_kwargs)
        stream_kwargs.pop("stream", None)
        try:
            with stream_fn(**stream_kwargs) as stream:
                return stream.get_final_message()
        except Exception as exc:
            if not _is_stream_unavailable_error(exc):
                raise
            logger.debug(
                "%sAnthropic stream kullanılamıyor; messages.create()'a geçiliyor: %s",
                log_prefix, exc,
            )

    create_kwargs = dict(api_kwargs)
    create_kwargs.pop("stream", None)
    return messages_api.create(**create_kwargs)
