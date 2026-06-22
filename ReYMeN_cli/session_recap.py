# -*- coding: utf-8 -*-
"""ReYMeN_cli/session_recap.py — Oturum Ozeti.

Aktif oturumun aktivite ozetini cikarir.
Mesaj sayisi, araci kullanim kategorileri ve son kullanici promptunu
icerir. ReYMeN CLI icin hafif bir session_recap alternatifidir.
"""

from datetime import datetime
from typing import Any


class Renk:
    """ReYMeN Renk sinifi — oturum ozeti renklendirmesi icin."""
    YESIL = "\033[92m"
    SARI = "\033[93m"
    KIRMIZI = "\033[91m"
    MAVI = "\033[94m"
    CYAN = "\033[96m"
    MOR = "\033[95m"
    KALIN = "\033[1m"
    SON = "\033[0m"

    @classmethod
    def boya(cls, metin: str, kod: str) -> str:
        return f"{kod}{metin}{cls.SON}"

    @classmethod
    def yesil(cls, metin: str) -> str:
        return cls.boya(metin, cls.YESIL)

    @classmethod
    def sari(cls, metin: str) -> str:
        return cls.boya(metin, cls.SARI)

    @classmethod
    def cyan(cls, metin: str) -> str:
        return cls.boya(metin, cls.CYAN)

    @classmethod
    def mor(cls, metin: str) -> str:
        return cls.boya(metin, cls.MOR)

    @classmethod
    def kalin(cls, metin: str) -> str:
        return cls.boya(metin, cls.KALIN)


def _count_tool_calls(messages: list) -> dict:
    """Mesaj listesindeki araci kullanimlarini kategorilere ayir.

    Kategoriler:
      - terminal: terminal, process tool calls
      - dosya: write_file, patch, read_file, search_files
      - web: web_search, web_fetch (html_fetch)
      - github: mcp_github_* tool calls
      - obsidian: mcp_obsidian_vault_* tool calls
      - diger: kalan tum tool call'lar

    Args:
        messages: Mesaj listesi (dict formatinda).

    Returns:
        dict: Kategori isimlerinden sayilara.
    """
    try:
        kategori_anahtarlari = {
            "terminal": {"terminal", "process"},
            "dosya": {"write_file", "patch", "read_file", "search_files"},
            "web": {"web_search", "html_fetch", "web_fetch"},
            "github": {"mcp_github"},
            "obsidian": {"mcp_obsidian_vault"},
        }
        sayac = {
            "terminal": 0,
            "dosya": 0,
            "web": 0,
            "github": 0,
            "obsidian": 0,
            "diger": 0,
        }

        for msg in messages:
            if not isinstance(msg, dict):
                continue
            tool_calls = msg.get("tool_calls") or msg.get("tool_call", [])
            if isinstance(tool_calls, dict):
                tool_calls = [tool_calls]
            if not isinstance(tool_calls, list):
                continue

            for tc in tool_calls:
                if isinstance(tc, dict):
                    arac_adi = (tc.get("function", {}).get("name", "") or
                                tc.get("name", "") or "")
                elif isinstance(tc, str):
                    arac_adi = tc
                else:
                    arac_adi = str(tc) if tc else ""

                eslesti = False
                for kategori, anahtarlar in kategori_anahtarlari.items():
                    if any(anahtar in arac_adi for anahtar in anahtarlar):
                        sayac[kategori] = sayac.get(kategori, 0) + 1
                        eslesti = True
                        break
                if not eslesti and arac_adi:
                    sayac["diger"] = sayac.get("diger", 0) + 1

        return sayac
    except Exception:
        return {"terminal": 0, "dosya": 0, "web": 0, "github": 0, "obsidian": 0, "diger": 0}


def _preview_latest(messages: list) -> str:
    """Son kullanici mesajinin ilk 120 karakterini goster.

    Args:
        messages: Mesaj listesi.

    Returns:
        str: Kisa prompt onizlemesi.
    """
    try:
        for msg in reversed(messages):
            if not isinstance(msg, dict):
                continue
            rol = msg.get("role", "")
            if rol == "user":
                icerik = msg.get("content", "")
                if isinstance(icerik, list):
                    for parca in icerik:
                        if isinstance(parca, dict) and parca.get("type") == "text":
                            icerik = parca.get("text", "")
                            break
                    else:
                        icerik = str(icerik)
                if not isinstance(icerik, str):
                    icerik = str(icerik)
                icerik = icerik.strip()
                if icerik:
                    return icerik[:120] + ("..." if len(icerik) > 120 else "")
        return "(onizleme yok)"
    except Exception:
        return "(onizleme hatasi)"


def build_recap(messages: list) -> str:
    """Oturum ozeti metni olustur.

    Son 20 mesaji analiz eder, araci kullanim kategorilerini sayar,
    oturum uzunlugunu ve son prompt onizlemesini dondurur.

    Args:
        messages: Tum oturum mesajlarinin listesi.

    Returns:
        str: Bicimlendirilmis oturum ozeti (renk kodlari ile).
    """
    try:
        toplam_mesaj = len(messages)
        son_20 = messages[-20:] if len(messages) > 20 else messages

        sayac = _count_tool_calls(son_20)
        prompt_preview = _preview_latest(son_20)

        # Insan mesajlarini say
        insan_mesaji = sum(
            1 for m in son_20 if isinstance(m, dict) and m.get("role") == "user"
        )
        asistan_mesaji = sum(
            1 for m in son_20 if isinstance(m, dict) and m.get("role") == "assistant"
        )

        # Tool call toplami
        toplam_arac = sum(sayac.values())

        # Ozet metnini olustur
        satirlar = [
            f"\n{Renk.kalin(Renk.cyan('═══ ReYMeN Oturum Ozeti ═══'))}",
            f"  {Renk.mor('Sure:')}      {toplam_mesaj} mesaj ({len(son_20)} son)",
            f"  {Renk.mor('Kullanici:')} {insan_mesaji} mesaj",
            f"  {Renk.mor('Asistan:')}   {asistan_mesaji} yanit",
        ]

        if toplam_arac > 0:
            satirlar.append(f"  {Renk.mor('Arac Kullanim:')}")
            emojiler = {
                "terminal": f"    {Renk.cyan('├')} terminal   : {sayac['terminal']}",
                "dosya": f"    {Renk.cyan('├')} dosya     : {sayac['dosya']}",
                "web": f"    {Renk.cyan('├')} web       : {sayac['web']}",
                "github": f"    {Renk.cyan('├')} github    : {sayac['github']}",
                "obsidian": f"    {Renk.cyan('├')} obsidian  : {sayac['obsidian']}",
                "diger": f"    {Renk.cyan('└')} diger     : {sayac['diger']}",
            }
            for kategori in ["terminal", "dosya", "web", "github", "obsidian", "diger"]:
                if sayac.get(kategori, 0) > 0:
                    satirlar.append(emojiler[kategori])

        satirlar.append(f"  {Renk.mor('Son Prompt:')}  {Renk.sari(prompt_preview)}")
        satirlar.append(Renk.kalin(Renk.cyan('═══════════════════════════\n')))

        return "\n".join(satirlar)
    except Exception as e:
        return f"[SessionRecap] Ozet olusturma hatasi: {e}"
