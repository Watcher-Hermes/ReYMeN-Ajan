# -*- coding: utf-8 -*-
"""gateway/platforms/whatsapp_common.py — WhatsApp Ortak Yardimcilari.

Iki WhatsApp platformu (whatsapp.py, whatsapp_cloud.py) arasinda
paylasilan fonksiyonlar: mesaj_temizle, numara_dogrula, medya_yukle.
"""

import os
import re
import json
import logging

try:
    import requests
    _REQUESTS_OK = True
except ImportError:
    _REQUESTS_OK = False

logger = logging.getLogger(__name__)


def mesaj_temizle(mesaj: str, max_uzunluk: int = 4096) -> str:
    """WhatsApp mesajini temizler ve kisaltir.

    - HTML/Markdown taglarini temizle
    - Asiri bosluklari sil
    - Maksimum uzunluga kisalt

    Args:
        mesaj: Ham mesaj metni
        max_uzunluk: Maksimum karakter sayisi (varsayilan: 4096)

    Returns:
        str: Temizlenmis mesaj
    """
    if not mesaj:
        return ""

    # HTML taglarini temizle
    temiz = re.sub(r"<[^>]+>", "", mesaj)
    # Markdown linklerini temizle [text](url) -> text
    temiz = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", temiz)
    # Birden fazla satir boslugunu teke indir
    temiz = re.sub(r"\n{3,}", "\n\n", temiz)
    # Bastaki ve sondaki bosluklari sil
    temiz = temiz.strip()

    # Maksimum uzunluga kisalt (son kelimeyi bolmeden)
    if len(temiz) > max_uzunluk:
        temiz = temiz[:max_uzunluk]
        # Son kelimeyi kirpmamaya calis
        son_bosluk = temiz.rfind(" ")
        if son_bosluk > max_uzunluk * 0.8:
            temiz = temiz[:son_bosluk]
        temiz += "..."

    return temiz


def numara_dogrula(numara: str) -> bool:
    """Telefon numarasinin gecerliligini dogrular.

    Desteklenen formatlar:
    - 905551234567 (Türkiye, basinda + yok)
    - +905551234567 (uluslararasi)
    - 00905551234567 (uluslararasi, 00 ile)

    Args:
        numara: Dogrulanacak telefon numarasi

    Returns:
        bool: Numara gecerli ise True
    """
    if not numara:
        return False

    # Tum bosluk, tire, parantezleri kaldir
    temiz = re.sub(r"[\s\-\(\)\.]", "", numara)

    # + veya 00 ile baslayabilir
    if temiz.startswith("+"):
        temiz = temiz[1:]
    elif temiz.startswith("00"):
        temiz = temiz[2:]

    # Sadece rakam kaldi mi?
    if not temiz.isdigit():
        return False

    # Minimum 10, maksimum 15 hane (ITU-T E.164)
    if len(temiz) < 10 or len(temiz) > 15:
        return False

    return True


def medya_yukle(dosya_yolu: str, token: str = None, phone_id: str = None) -> dict:
    """WhatsApp Cloud API'ye medya dosyasi yukler.

    Args:
        dosya_yolu: Yuklenecek dosyanin yolu
        token: WhatsApp access token (env'den okunur)
        phone_id: WhatsApp Phone Number ID (env'den okunur)

    Returns:
        dict: {"durum": "basarili", "media_id": "..."} veya hata
    """
    if not _REQUESTS_OK:
        return {"durum": "hata", "hata": "requests kutuphanesi yok."}

    if not os.path.isfile(dosya_yolu):
        return {"durum": "hata", "hata": f"Dosya bulunamadi: {dosya_yolu}"}

    token = token or os.environ.get("WHATSAPP_TOKEN", "")
    phone_id = phone_id or os.environ.get("WHATSAPP_PHONE_ID", "")

    if not token or not phone_id:
        return {"durum": "hata", "hata": "WHATSAPP_TOKEN/PHONE_ID ayarlanmamis."}

    try:
        with open(dosya_yolu, "rb") as f:
            r = requests.post(
                f"https://graph.facebook.com/v18.0/{phone_id}/media",
                files={"file": f},
                data={
                    "messaging_product": "whatsapp",
                    "type": "application/octet-stream",
                },
                headers={"Authorization": f"Bearer {token}"},
                timeout=30,
            )
        data = r.json()
        if r.status_code == 200 and data.get("id"):
            return {"durum": "basarili", "media_id": data["id"]}
        return {"durum": "hata", "hata": f"Yukleme hatasi {r.status_code}: {data}"}
    except Exception as e:
        return {"durum": "hata", "hata": str(e)}


def ping() -> bool:
    """Ortak modulun calistigini kontrol eder."""
    return True


import re as _re


def format_message(mesaj):
    if mesaj is None:
        return None
    if mesaj == "":
        return ""
    # Preserve code blocks
    parts = _re.split(r'(```[\s\S]*?```)', mesaj)
    result = []
    for i, part in enumerate(parts):
        if i % 2 == 1:  # code block
            result.append(part)
        else:
            p = part
            p = _re.sub(r'\*\*(.+?)\*\*', r'*\1*', p)
            p = _re.sub(r'~~(.+?)~~', r'~\1~', p)
            p = _re.sub(r'^# (.+)$', r'*\1*', p, flags=_re.MULTILINE)
            p = _re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'\1 (\2)', p)
            result.append(p)
    return "".join(result)


def numara_normalize(numara):
    if not numara:
        return ""
    return _re.sub(r'[\+\s\-\(\)]', '', numara)


def jid_to_wa_id(jid):
    if not jid:
        return ""
    return jid.split("@")[0]


def is_broadcast_chat(jid):
    if not jid:
        return False
    return jid.endswith("@broadcast") or jid.endswith("@newsletter")


def dm_izinli(numara, policy, allowlist=None):
    if policy == "open":
        return True
    if policy == "disabled":
        return False
    if policy == "allowlist":
        return numara in (allowlist or set())
    return False


def grup_izinli(grup_id, policy, allowlist=None):
    return dm_izinli(grup_id, policy, allowlist)


def mention_patterns_derle(pattern_str):
    if not pattern_str:
        return []
    try:
        return [_re.compile(pattern_str)]
    except _re.error:
        return []


def mesaj_mention_iceriyor(body, bot_id, patterns=None):
    if not body:
        return False
    if f"@{bot_id}" in body:
        return True
    if patterns:
        for p in patterns:
            if p.search(body):
                return True
    return False
