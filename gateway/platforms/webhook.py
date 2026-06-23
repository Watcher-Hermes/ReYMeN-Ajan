# -*- coding: utf-8 -*-
"""gateway/platforms/webhook.py — Webhook Platformu.

HTTP POST ile herhangi bir webhook URL'sine mesaj gonderir.
"""

import os
import json
import requests

_INSECURE_NO_AUTH = "no_auth"
_INSECURE_MODES = {"no_auth"}
_DYNAMIC_ROUTES_FILENAME = "routes.json"


def check_webhook_requirements() -> bool:
    return True


def baslat():
    pass


def durdur():
    pass


class WebhookAdapter:
    platform = "webhook"

    def __init__(self, config=None):
        self._mesaj_isleyici = None
        self._sunucu = None
        cfg = {}
        if config and hasattr(config, "extra"):
            cfg = config.extra or {}
        elif isinstance(config, dict):
            cfg = config
        self._port = int(cfg.get("port", os.environ.get("WEBHOOK_PORT", 8644)))
        self._secret = cfg.get("secret", os.environ.get("WEBHOOK_SECRET", ""))
        _env_enabled = os.environ.get("WEBHOOK_ENABLED", "true").lower() not in ("false", "0", "no", "off")
        self._enabled = bool(cfg.get("enabled", _env_enabled))

    @property
    def aktif(self):
        return self._sunucu is not None

    def mesaj_isleyici_kaydet(self, fn):
        self._mesaj_isleyici = fn

    def baslat(self):
        if not self._enabled:
            return None
        try:
            from gateway.webhook import WebhookGateway
            self._sunucu = WebhookGateway()
            sonuc = self._sunucu.baslat()
            return sonuc if sonuc is not None else self._port
        except Exception:
            return None

    def durdur(self):
        if self._sunucu:
            try:
                self._sunucu.durdur()
            except Exception:
                pass
        self._sunucu = None

    def gonder(self, url, mesaj) -> str:
        return mesaj_gonder(url, mesaj)

    async def connect(self):
        self.baslat()
        return True

    async def disconnect(self):
        self.durdur()

    async def send_message(self, chat_id, content, **kwargs) -> dict:
        try:
            sonuc = mesaj_gonder(chat_id, str(content))
            if "Gonderildi" in sonuc or "Gönderildi" in sonuc:
                return {"success": True, "durum": "basarili", "sonuc": sonuc}
            return {"success": False, "durum": "hata", "hata": sonuc}
        except Exception as e:
            return {"success": False, "durum": "hata", "hata": str(e)}

    def ping(self) -> bool:
        return True


def mesaj_gonder(hedef: str, mesaj: str) -> str:
    """Webhook URL'sine POST istegi gonder.

    Args:
        hedef: Webhook URL'si
        mesaj: Gonderilecek veri

    Returns:
        Durum mesaji
    """
    if not hedef.startswith("http"):
        return "[Webhook]: Gecerli bir URL gerekli."

    try:
        payload = {
            "text": mesaj[:4000],
            "source": "ReYMeN",
            "timestamp": __import__("datetime").datetime.now().isoformat(),
        }
        r = requests.post(
            hedef,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10,
        )
        if 200 <= r.status_code < 300:
            return f"[Webhook]: Gonderildi (HTTP {r.status_code})."
        return f"[Webhook]: Hata {r.status_code}: {r.text[:100]}"
    except requests.Timeout:
        return "[Webhook]: Zaman asimi."
    except Exception as e:
        return f"[Webhook]: Hata: {e}"
