# -*- coding: utf-8 -*-
"""gateway/platforms/discord.py — Discord platform adapter."""

from __future__ import annotations
import json
import os
import urllib.request
import urllib.error
from typing import Iterator

try:
    import requests as _requests_mod
    _REQUESTS_OK = True
except ImportError:
    _requests_mod = None
    _REQUESTS_OK = False

_API_BASE = "https://discord.com/api/v10"
_TIMEOUT  = 10


def _token_al() -> str:
    return os.environ.get("DISCORD_BOT_TOKEN", "")


def send_message(
    channel_id: str,
    content: str,
    *,
    tts: bool = False,
    reply_to: str | None = None,
    embeds: list | None = None,
) -> dict:
    """Discord kanalina mesaj gonder."""
    if not _REQUESTS_OK:
        return {"durum": "hata", "hata": "requests modulu yok."}
    token = _token_al()
    if not token:
        return {"durum": "hata", "hata": "DISCORD_BOT_TOKEN ayarlanmamis."}

    url = f"{_API_BASE}/channels/{channel_id}/messages"
    payload: dict = {"content": content[:2000], "tts": tts}
    if reply_to is not None:
        payload["message_reference"] = {"message_id": reply_to}
    if embeds is not None:
        payload["embeds"] = embeds

    headers = {
        "Authorization": f"Bot {token}",
        "Content-Type": "application/json",
    }
    try:
        import requests
        r = requests.post(url, json=payload, headers=headers, timeout=_TIMEOUT)
        if r.status_code == 200:
            return {"durum": "basarili", "mesaj_id": r.json().get("id", "")}
        return {"durum": "hata", "hata": f"HTTP {r.status_code}: {r.text[:100]}"}
    except Exception as exc:
        exc_str = str(exc)
        if "Timeout" in type(exc).__name__ or "timeout" in exc_str.lower():
            return {"durum": "hata", "hata": f"Zaman asimi: {exc_str}"}
        return {"durum": "hata", "hata": exc_str}


def mesaj_gonder(channel_id: str, content: str) -> dict:
    """send_message icin kisa alias."""
    return send_message(channel_id, content)


def test():
    print("[Discord] test OK")


class DiscordPlatform:
    """send_message / receive_message interface'ini uygular."""

    def __init__(self, bot_token: str, varsayilan_kanal: str = ""):
        if not bot_token:
            raise ValueError("bot_token zorunlu.")
        self._token   = bot_token
        self._kanal   = varsayilan_kanal
        self._headers = {
            "Authorization": f"Bot {self._token}",
            "Content-Type":  "application/json",
            "User-Agent":    "ReYMeNBot/1.0",
        }

    # ── GÖNDERİM ─────────────────────────────────────
    def send_message(self, mesaj: str, kanal_id: str = "") -> dict:
        hedef = kanal_id or self._kanal
        if not hedef:
            return {"hata": "kanal_id zorunlu."}
        if not mesaj.strip():
            return {"hata": "mesaj boş olamaz."}

        url     = f"{_API_BASE}/channels/{hedef}/messages"
        payload = json.dumps({"content": mesaj[:2000]}).encode("utf-8")
        req     = urllib.request.Request(
            url, data=payload, headers=self._headers, method="POST"
        )
        try:
            with urllib.request.urlopen(req, timeout=_TIMEOUT) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            return {"hata": f"HTTP {e.code}: {e.reason}"}
        except urllib.error.URLError as e:
            return {"hata": f"Ağ hatası: {e.reason}"}

    # ── ALMA ─────────────────────────────────────────
    def receive_message(
        self, kanal_id: str = "", limit: int = 10
    ) -> list[dict]:
        hedef = kanal_id or self._kanal
        if not hedef:
            return [{"hata": "kanal_id zorunlu."}]

        limit = max(1, min(int(limit), 100))
        url   = f"{_API_BASE}/channels/{hedef}/messages?limit={limit}"
        req   = urllib.request.Request(url, headers=self._headers)
        try:
            with urllib.request.urlopen(req, timeout=_TIMEOUT) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            return [{"hata": f"HTTP {e.code}: {e.reason}"}]
        except urllib.error.URLError as e:
            return [{"hata": f"Ağ hatası: {e.reason}"}]

    # ── STREAM (iterator pattern) ─────────────────────
    def mesaj_akisi(self, kanal_id: str = "") -> Iterator[dict]:
        """Lazy: mesajları birer birer yield et."""
        for msg in self.receive_message(kanal_id, limit=50):
            yield msg


# ── REGISTRY KAYDI ───────────────────────────────────
def platform_olustur(konfig: dict) -> DiscordPlatform:
    """platform_registry.py bu factory'yi çağırır."""
    return DiscordPlatform(
        bot_token        = konfig.get("bot_token", ""),
        varsayilan_kanal = konfig.get("kanal_id",  ""),
    )
