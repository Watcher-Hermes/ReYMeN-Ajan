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
    """Webhook platform adaptörü — gateway/run.py ve testler için."""

    platform = "webhook"

    def __init__(self, config=None):
        self._mesaj_isleyici = None
        self._sunucu = None

        # Config'den veya env'den oku
        cfg = {}
        if config is not None and hasattr(config, "extra"):
            cfg = config.extra or {}

        self._port = int(cfg.get("port") or os.environ.get("WEBHOOK_PORT", "8644") or "8644")
        self._secret = cfg.get("secret") or os.environ.get("WEBHOOK_SECRET", "")

        if "enabled" in cfg:
            self._enabled = bool(cfg["enabled"])
        else:
            env_val = os.environ.get("WEBHOOK_ENABLED", "true").lower()
            self._enabled = env_val not in ("false", "0", "no", "off")

    @property
    def aktif(self) -> bool:
        return self._sunucu is not None

    def mesaj_isleyici_kaydet(self, fn):
        self._mesaj_isleyici = fn

    def baslat(self):
        if not self._enabled:
            return None
        try:
            import gateway.webhook as _gw
            sunucu = _gw.WebhookGateway(port=self._port, secret=self._secret)
            self._sunucu = sunucu
            sonuc = sunucu.baslat()
            return sonuc if sonuc is not None else self._port
        except Exception:
            return self._port

    def durdur(self):
        if self._sunucu is not None:
            try:
                self._sunucu.durdur()
            except Exception:
                pass
            self._sunucu = None

    def gonder(self, hedef: str, mesaj: str) -> str:
        return mesaj_gonder(hedef, mesaj)

    async def connect(self):
        sonuc = self.baslat()
        return sonuc is not None

    async def disconnect(self):
        self.durdur()

    async def send_message(self, hedef: str, mesaj: str, **kwargs) -> dict:
        try:
            sonuc = mesaj_gonder(hedef, mesaj)
            if "Gonderildi" in sonuc or "Gönderildi" in sonuc:
                return {"success": True, "sonuc": sonuc}
            return {"success": False, "hata": sonuc}
        except Exception as e:
            return {"success": False, "hata": str(e)}

    def ping(self) -> bool:
        return True


def mesaj_gonder(hedef: str, mesaj: str) -> str:
    """Webhook URL'sine POST istegi gonder."""
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
