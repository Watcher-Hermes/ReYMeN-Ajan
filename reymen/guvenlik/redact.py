# -*- coding: utf-8 -*-
"""redact.py — PII temizleme fonksiyonlari.

Email, telefon, kredi karti, API key, TC kimlik numarasi gibi
hassas bilgileri regex ile bulur ve maskeler. IP adresi, URL
parametreleri ve hassas dosya yollari da temizlenir.
"""

import re
from typing import Tuple

# 1. Email: standard email format
_EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")

# 2. Telefon: exactly 10 contiguous digits starting with 1 or 5 (Turkcell/Vodafone/Turk Telekom)
_TELEFON_RE = re.compile(r"\b[15]\d{9}\b")

# 3. Kredi karti: 13-16 digits, optionally separated by spaces or dashes
_KART_RE = re.compile(r"\b(\d[ -]?){13,16}\b")

# 4. API Key: KEY=VALUE pattern where KEY contains API_KEY, TOKEN, SECRET etc.
_API_KEY_RE = re.compile(
    r"\b([A-Z_]*?(?:API_?KEY|TOKEN|SECRET|PASSWORD|AUTH)[A-Z_]*?)\s*=\s*['\"]?(\S+?)['\"]?\b",
    re.IGNORECASE,
)

# 5. TC Kimlik: exactly 11 digits, first digit 1-9 (cannot start with 0)
_TC_RE = re.compile(r"\b[1-9]\d{10}\b")

# 6. IPv4 adresleri (private/public ayrimi yapilmaz)
_IPV4_RE = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")

# 7. URL icindeki hassas query parametreleri (?key=..., ?token=..., ?password=...)
_URL_PARAM_RE = re.compile(
    r"([?&](?:api[_-]?key|token|secret|password|auth|access[_-]?token)=)[^&\s]+",
    re.IGNORECASE,
)

# 8. Hassas dosya yollari (Windows: C:\Users\<kullanici>\..., Unix: /home/<kullanici>/...)
_HASSAS_YOL_RE = re.compile(
    r"(?:[Cc]:\\Users\\[^\\]+\\|/home/[^/]+/|/root/)"
    r"(?:[A-Za-z0-9_\\/.-]+)?"
    r"(?:\.[a-zA-Z]{2,}|[A-Za-z0-9_-]+\.(?:key|pem|pfx|crt|p12|kdb|pkcs12))"
)


def email_temizle(text: str) -> str:
    """Email adreslerini [EMAIL] ile degistir."""
    if not text:
        return text
    return _EMAIL_RE.sub("[EMAIL]", text)


def telefon_temizle(text: str) -> str:
    """10 haneli telefon numaralarini [TELEFON] ile degistir.
    9 haneli sayilar temizlenmez (sadece 10 hane kurali)."""
    if not text:
        return text
    return _TELEFON_RE.sub("[TELEFON]", text)


def kart_temizle(text: str) -> str:
    """Kredi karti numaralarini [KART_NO] ile degistir.
    Destekler: 1234567890123456, 1234-5678-9012-3456, 1234 5678 9012 3456"""
    if not text:
        return text
    return _KART_RE.sub("[KART_NO]", text)


def api_key_temizle(text: str) -> str:
    """API key/token degerlerini [GIZLI] ile degistir.
    KEY=VALUE formatindaki degerleri maskeler."""
    if not text:
        return text

    def _mask(m):
        key = m.group(1)
        return f"{key}= [GIZLI]"

    return _API_KEY_RE.sub(_mask, text)


def tc_temizle(text: str) -> str:
    """TC kimlik numaralarini [TC_KIMLIK] ile degistir.
    0 ile baslayan 11 haneli sayilar gecersiz TC'dir, temizlenmez."""
    if not text:
        return text
    return _TC_RE.sub("[TC_KIMLIK]", text)


def ip_temizle(text: str) -> str:
    """IPv4 adreslerini [IP_ADRESI] ile degistir.
    Gecerli IPv4 range'inde olmayanlari (0.0.0.0, 999.999.999.999) atlar."""
    if not text:
        return text

    def _kontrol(m):
        parcalar = m.group(0).split(".")
        for p in parcalar:
            try:
                deger = int(p)
                if deger < 0 or deger > 255:
                    return m.group(0)  # gecersiz IP, dokunma
            except ValueError:
                return m.group(0)
        # 0.0.0.0 ve 255.255.255.255 ozel durum
        if all(p == "0" for p in parcalar):
            return m.group(0)
        if all(p == "255" for p in parcalar):
            return m.group(0)
        return "[IP_ADRESI]"

    return _IPV4_RE.sub(_kontrol, text)


def url_param_temizle(text: str) -> str:
    """URL icindeki hassas query parametre degerlerini temizler.
    Orn: ?api_key=abc123 -> ?api_key=[GIZLI]"""
    if not text:
        return text
    return _URL_PARAM_RE.sub(r"\1[GIZLI]", text)


def hassas_yol_temizle(text: str) -> str:
    """Hassas dosya yollari ve private key dosyalarini maskeler.
    Orn: C:\\Users\\admin\\.ssh\\id_rsa -> [HASSAS_YOL]"""
    if not text:
        return text
    return _HASSAS_YOL_RE.sub("[HASSAS_YOL]", text)


def tam_temizle(text: str, ekstra: Tuple[str, ...] = ()) -> str:
    """Tum PII'yi tek geciste temizle.

    Args:
        text: Temizlenecek metin
        ekstra: Ekstra temizlenecek kelimeler (opsiyonel)

    Returns:
        str: Temizlenmis metin
    """
    if not text:
        return text
    sonuc = email_temizle(text)
    sonuc = telefon_temizle(sonuc)
    sonuc = kart_temizle(sonuc)
    sonuc = api_key_temizle(sonuc)
    sonuc = tc_temizle(sonuc)
    sonuc = ip_temizle(sonuc)
    sonuc = url_param_temizle(sonuc)
    sonuc = hassas_yol_temizle(sonuc)
    for kelime in ekstra:
        sonuc = sonuc.replace(kelime, "[GIZLI]")
    return sonuc


def pii_raporu(text: str) -> dict:
    """Metinde hangi PII turlerinin bulundugunu raporlar.

    Args:
        text: Analiz edilecek metin

    Returns:
        dict: PII turu -> bulunan eleman sayisi
    """
    if not text:
        return {}
    rapor = {}
    try:
        email_say = len(_EMAIL_RE.findall(text))
        if email_say:
            rapor["email"] = email_say

        telefon_say = len(_TELEFON_RE.findall(text))
        if telefon_say:
            rapor["telefon"] = telefon_say

        kart_say = len(_KART_RE.findall(text))
        if kart_say:
            rapor["kart_numarasi"] = kart_say

        api_say = len(_API_KEY_RE.findall(text))
        if api_say:
            rapor["api_anahtari"] = api_say

        tc_say = len(_TC_RE.findall(text))
        if tc_say:
            rapor["tc_kimlik"] = tc_say

        ip_say = len(_IPV4_RE.findall(text))
        if ip_say:
            # gecerli IP'leri filtrele
            gecerli_ip = 0
            for m in _IPV4_RE.finditer(text):
                try:
                    parcalar = m.group(0).split(".")
                    degerler = [int(p) for p in parcalar]
                    if all(0 <= d <= 255 for d in degerler):
                        gecerli_ip += 1
                except ValueError:
                    pass
            if gecerli_ip:
                rapor["ip_adresi"] = gecerli_ip

        hassas_yol_say = len(_HASSAS_YOL_RE.findall(text))
        if hassas_yol_say:
            rapor["hassas_yol"] = hassas_yol_say

    except Exception:
        pass
    return rapor
