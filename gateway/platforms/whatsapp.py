# -*- coding: utf-8 -*-
"""gateway/platforms/whatsapp.py — WhatsApp Platformu.

WhatsApp Business API veya webhook uzerinden mesaj gonderir.
"""

import logging
import os
import shutil
import subprocess

try:
    import requests
    _REQUESTS_OK = True
except ImportError:
    _REQUESTS_OK = False

logger = logging.getLogger(__name__)


def _token_al() -> str:
    token = os.environ.get("WHATSAPP_TOKEN", "")
    if token and not token.startswith("***"):
        return token
    return ""


def _config_str(key, default="") -> str:
    return os.environ.get(key, default)


def _config_bool(key) -> bool:
    return os.environ.get(key, "").lower() in ("true", "1", "yes", "on")


def ping() -> bool:
    if not _REQUESTS_OK:
        return False
    token = _token_al()
    if not token:
        return False
    phone_id = _config_str("WHATSAPP_PHONE_ID")
    if not phone_id:
        return False
    try:
        requests.get(
            f"https://graph.facebook.com/v18.0/{phone_id}",
            headers={"Authorization": f"Bearer {token}"},
            timeout=5,
        )
        return True
    except Exception:
        return False


def node_mevcut() -> bool:
    if shutil.which("node") is None:
        return False
    try:
        subprocess.run(["node", "--version"], capture_output=True, timeout=3)
        return True
    except Exception:
        return False


def bridge_script_bul() -> "str | None":
    path = os.path.join(os.path.dirname(__file__), "..", "..", "whatsapp_bridge", "index.js")
    if os.path.isfile(path):
        return path
    return None


def baslat():
    logger.info("[whatsapp] Platform baslatildi")


def durdur():
    logger.info("[whatsapp] Platform durduruldu")


def mesaj_gonder(hedef: str, mesaj: str, reply_to=None) -> str:
    """WhatsApp'a mesaj gonder.

    Args:
        hedef: Telefon numarasi (uluslararasi, +90xxxxxxxxx)
        mesaj: Gonderilecek metin
        reply_to: Yanit verilecek mesaj ID'si (opsiyonel)
    """
    if not _REQUESTS_OK:
        return "[WhatsApp]: requests modulu yok."

    token = _token_al()
    if not token:
        return "[WhatsApp]: WHATSAPP_TOKEN ayarlanmamis."

    phone_id = _config_str("WHATSAPP_PHONE_ID")
    if not phone_id:
        return "[WhatsApp]: WHATSAPP_PHONE_ID ayarlanmamis."

    if _config_str("WHATSAPP_DM_POLICY") == "disabled":
        return "[WhatsApp]: DM izni kapali."

    api_version = _config_str("WHATSAPP_API_VERSION", "v18.0")

    payload = {
        "messaging_product": "whatsapp",
        "to": hedef,
        "type": "text",
        "text": {"body": mesaj[:4096]},
    }
    if reply_to is not None:
        payload["context"] = {"message_id": reply_to}

    try:
        r = requests.post(
            f"https://graph.facebook.com/{api_version}/{phone_id}/messages",
            json=payload,
            headers={"Authorization": f"Bearer {token}"},
            timeout=15,
        )
        if r.status_code == 200:
            return "[WhatsApp]: Mesaj gonderildi."
        try:
            err_msg = r.json().get("error", {}).get("message", "")
        except Exception:
            err_msg = r.text[:100]
        return f"[WhatsApp]: Hata {r.status_code}: {err_msg}" if err_msg else f"[WhatsApp]: Hata {r.status_code}"
    except Exception as e:
        return f"[WhatsApp]: Hata: {e}"


def send_message_json(hedef, payload) -> dict:
    if not _REQUESTS_OK:
        return {"durum": "hata", "hata": "requests modulu yok"}
    token = _token_al()
    phone_id = _config_str("WHATSAPP_PHONE_ID")
    api_version = _config_str("WHATSAPP_API_VERSION", "v18.0")
    try:
        r = requests.post(
            f"https://graph.facebook.com/{api_version}/{phone_id}/messages",
            json=payload,
            headers={"Authorization": f"Bearer {token}"},
            timeout=15,
        )
        if r.status_code == 200:
            return {"durum": "basarili"}
        return {"durum": "hata", "hata": f"{r.status_code} {r.text[:100]}"}
    except Exception as e:
        return {"durum": "hata", "hata": str(e)}


def send_media(hedef, dosya_yolu) -> str:
    if not _REQUESTS_OK:
        return "[WhatsApp]: requests yok."
    try:
        from gateway.platforms import whatsapp_common as _wc
        if not getattr(_wc, "_REQUESTS_OK", True):
            return "[WhatsApp]: whatsapp_common requests modulu yuklenemedi."
    except Exception:
        pass
    return mesaj_gonder(hedef, f"[Dosya]: {dosya_yolu}")


class WhatsAppAdapter:
    platform = "whatsapp"

    def __init__(self):
        self.platform = "whatsapp"

    async def connect(self):
        return bool(os.environ.get("WHATSAPP_TOKEN", ""))

    async def disconnect(self):
        pass

    async def send(self, chat_id, content):
        r = mesaj_gonder(chat_id, content)
        return type("R", (), {"success": "gonderildi" in r.lower()})()
