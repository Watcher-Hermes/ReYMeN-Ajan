# -*- coding: utf-8 -*-
"""ReYMeN_cli/blueprint_cmd.py — Blueprint Komutlari CLI.

Blueprint (otomasyon sabloni) yonetimi: listeleme,
detay gosterme ve calistirma.
ReYMeN'e ozgu is akisi sablonlarini JSON formatinda
.ReYMeN/blueprints/ altinda saklar.
"""

import json
import os
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, List, Optional, Tuple


# ---------------------------------------------------------------------------
# ReYMeN referans API — handle_blueprint_command icin veri yapilari
# ---------------------------------------------------------------------------


@dataclass
class BlueprintResponse:
    """Blueprint komut yaniti (text + opsiyonel ajan tohumlama)."""
    text: str
    agent_seed: Optional[str] = None


def _edit_distance(a: str, b: str) -> int:
    """Levenshtein uzakligi."""
    m, n = len(a), len(b)
    dp = list(range(n + 1))
    for i in range(1, m + 1):
        prev, dp[0] = dp[0], i
        for j in range(1, n + 1):
            temp = dp[j]
            dp[j] = prev if a[i - 1] == b[j - 1] else 1 + min(prev, dp[j], dp[j - 1])
            prev = temp
    return dp[n]


def match_blueprint(name: str) -> Tuple[Optional[Any], List[Any]]:
    """Blueprint'i ada gore bul: kesin → on-ek → yaklasik.

    Returns:
        (eslesen_blueprint_veya_None, aday_listesi) demeti
    """
    from cron.blueprint_catalog import CATALOG, get_blueprint

    bp = get_blueprint(name)
    if bp is not None:
        return bp, []

    candidates = [e for e in CATALOG if e.key.startswith(name)]
    if len(candidates) == 1:
        return candidates[0], []
    if len(candidates) > 1:
        return None, candidates

    threshold = max(3, len(name) // 3)
    if CATALOG:
        best = min(CATALOG, key=lambda e: _edit_distance(name, e.key))
        if _edit_distance(name, best.key) <= threshold:
            return best, []

    return None, []


def _build_agent_seed(entry) -> str:
    """Blueprint icin ajan tohumlama metni."""
    slot_desc = ", ".join(f"`{s.name}` ({s.label})" for s in entry.slots)
    return (
        f"The user wants to set up the **{entry.key}** automation blueprint.\n"
        f"Blueprint schedule pattern: '* * *'\n"
        f"Ask the user for each required slot: {slot_desc}.\n"
        f"Once you have all values, use the `cronjob tool` to create the job.\n"
        f"Blueprint key: `{entry.key}`"
    )


def handle_blueprint_command(args_str: str, origin=None) -> BlueprintResponse:
    """'/blueprint' komutunu isle.

    Args:
        args_str: Komut argumanlari (adi ve slot=deger ciflerini icerebilir)
        origin: Is kaynagi bilgisi

    Returns:
        BlueprintResponse
    """
    from cron.blueprint_catalog import CATALOG, BlueprintFillError, fill_blueprint
    import cron.jobs as cron_jobs

    args = (args_str or "").strip()

    if not args:
        lines = ["**Automation Blueprints**\n"]
        for entry in CATALOG:
            lines.append(f"• `{entry.key}` — {entry.title}: {entry.description}")
        return BlueprintResponse(text="\n".join(lines))

    parts = args.split()
    bp_name = parts[0]
    remaining = parts[1:]

    bp, candidates = match_blueprint(bp_name)
    if bp is None:
        if candidates:
            cand_keys = ", ".join(f"`{e.key}`" for e in candidates)
            return BlueprintResponse(
                text=f"No automation blueprint exactly matching {bp_name!r}. "
                     f"Did you mean: {cand_keys}?"
            )
        return BlueprintResponse(
            text=f"No automation blueprint matching {bp_name!r}. "
                 f"Try `/blueprint` to see all."
        )

    slot_values = {}
    for part in remaining:
        if "=" in part:
            k, v = part.split("=", 1)
            slot_values[k.strip()] = v.strip().strip('"')

    if not slot_values:
        seed = _build_agent_seed(bp)
        return BlueprintResponse(
            text=f"Let me help you set up **{bp.title}**.",
            agent_seed=seed,
        )

    try:
        spec = fill_blueprint(bp, slot_values, origin=origin)
    except BlueprintFillError as exc:
        slot_name = None
        for slot in bp.slots:
            if slot.name in str(exc):
                slot_name = slot.name
                break
        if slot_name:
            text = f"Can't set up `{bp.key}` — {slot_name}: {exc}"
        else:
            text = f"Can't set up `{bp.key}`: {exc}"
        return BlueprintResponse(text=text)

    create_spec = {k: v for k, v in spec.items() if k != "schedule_display"}
    cron_jobs.create_job(**create_spec)
    schedule = spec.get("schedule", "")
    return BlueprintResponse(text=f"Scheduled: **{bp.title}** ({schedule})")


class Renk:
    """ReYMeN Renk sinifi — blueprint_cmd ciktisi icin."""
    YESIL = "\033[92m"
    SARI = "\033[93m"
    KIRMIZI = "\033[91m"
    MAVI = "\033[94m"
    CYAN = "\033[96m"
    MOR = "\033[95m"
    KALIN = "\033[1m"
    SOLUK = "\033[2m"
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
    def kirmizi(cls, metin: str) -> str:
        return cls.boya(metin, cls.KIRMIZI)

    @classmethod
    def mavi(cls, metin: str) -> str:
        return cls.boya(metin, cls.MAVI)

    @classmethod
    def cyan(cls, metin: str) -> str:
        return cls.boya(metin, cls.CYAN)

    @classmethod
    def kalin(cls, metin: str) -> str:
        return cls.boya(metin, cls.KALIN)

    @classmethod
    def mor(cls, metin: str) -> str:
        return cls.boya(metin, cls.MOR)


PROJE_KOK = Path(__file__).parent.parent
BLUEPRINT_KLASOR = PROJE_KOK / ".ReYMeN" / "blueprints"


# Varsayilan blueprint'ler (sistemde yoksa kullanilir)
VARSAYILAN_BLUEPRINTS = {
    "hata-cozumu": {
        "name": "Hata Cozumu",
        "description": "Hata tespiti, analizi ve cozumu icin blueprint",
        "slots": ["hata_mesaji", "ek_bilgi"],
        "prompt_template": (
            "Bir hata cozumu yapilandirmasi baslatiliyor.\n"
            "Hata: {{hata_mesaji}}\n"
            "Ek bilgi: {{ek_bilgi}}\n"
            "Once hatayi analiz et, sonra cozum onerisi sun."
        ),
        "schedule_template": None,
    },
    "arastirma": {
        "name": "Arastirma",
        "description": "Konu arastirmasi ve bilgi toplama",
        "slots": ["konu", "derinlik"],
        "prompt_template": (
            "Arastirma baslatiliyor.\n"
            "Konu: {{konu}}\n"
            "Derinlik: {{derinlik}}\n"
            "Konuyla ilgili detayli bilgi topla ve ozetle."
        ),
        "schedule_template": "0 9 * * 1",
    },
    "rapor-olustur": {
        "name": "Rapor Olustur",
        "description": "Belirtilen baslikta rapor olusturma",
        "slots": ["baslik", "format"],
        "prompt_template": (
            "Rapor olusturuluyor.\n"
            "Baslik: {{baslik}}\n"
            "Format: {{format}}\n"
            "Istenen formatta detayli bir rapor hazirla."
        ),
        "schedule_template": None,
    },
}


def _blueprint_klasorunu_hazirla() -> Path:
    """Blueprint klasorunu olustur ve varsayilanlari yaz."""
    try:
        BLUEPRINT_KLASOR.mkdir(parents=True, exist_ok=True)
        for ad, icerik in VARSAYILAN_BLUEPRINTS.items():
            dosya = BLUEPRINT_KLASOR / f"{ad}.json"
            if not dosya.exists():
                with open(str(dosya), "w", encoding="utf-8") as f:
                    json.dump(icerik, f, indent=2, ensure_ascii=False)
        return BLUEPRINT_KLASOR
    except Exception as e:
        print(f"{Renk.kirmizi('[Blueprint]')} Klasor hazirlama hatasi: {e}")
        return BLUEPRINT_KLASOR


def _blueprint_oku(ad: str) -> Optional[dict]:
    """Blueprint JSON dosyasini oku."""
    try:
        dosya = BLUEPRINT_KLASOR / f"{ad}.json"
        if not dosya.exists():
            # Varsayilanlarda ara
            if ad in VARSAYILAN_BLUEPRINTS:
                return VARSAYILAN_BLUEPRINTS[ad]
            return None
        with open(str(dosya), "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def _blueprint_listesi() -> list[dict]:
    """Tum blueprint'leri listele."""
    try:
        _blueprint_klasorunu_hazirla()
        blueprintler = []

        # Dosyalardan oku
        if BLUEPRINT_KLASOR.exists():
            for dosya in sorted(BLUEPRINT_KLASOR.glob("*.json")):
                try:
                    with open(str(dosya), "r", encoding="utf-8") as f:
                        icerik = json.load(f)
                    icerik["_dosya"] = dosya.stem
                    blueprintler.append(icerik)
                except Exception:
                    pass

        return blueprintler
    except Exception:
        return []


def blueprint_listele() -> str:
    """Kullanilabilir blueprint'leri listele.

    Returns:
        str: Renkli blueprint listesi.
    """
    try:
        blueprintler = _blueprint_listesi()
        if not blueprintler:
            return f"{Renk.sari('[Blueprint]')} Henuz blueprint bulunamadi."

        satirlar = [
            f"{Renk.kalin(f'[Blueprint] Toplam {len(blueprintler)} blueprint:')}",
        ]

        for bp in blueprintler:
            ad = bp.get("_dosya", bp.get("name", "bilinmiyor"))
            aciklama = bp.get("description", "Aciklama yok")
            slot_sayisi = len(bp.get("slots", []))
            zamanli = "⏰" if bp.get("schedule_template") else "  "
            satirlar.append(
                f"  {Renk.cyan('📋')} {Renk.kalin(ad)} {zamanli}\n"
                f"    {aciklama[:70]}\n"
                f"    {Renk.soluk(f'Parametre: {slot_sayisi}')}"
            )

        return "\n".join(satirlar)
    except Exception as e:
        return f"{Renk.kirmizi('[Blueprint]')} Listeleme hatasi: {e}"


def blueprint_detay(ad: str) -> str:
    """Blueprint detaylarini goster.

    Args:
        ad: Blueprint adi.

    Returns:
        str: Renkli detay bilgisi.
    """
    try:
        bp = _blueprint_oku(ad)
        if not bp:
            return f"{Renk.kirmizi('[Blueprint]')} Blueprint bulunamadi: {ad}"

        name = bp.get("name", ad)
        satirlar = [
            Renk.kalin(f"[Blueprint] {name}"),
            f"  Aciklama: {bp.get('description', 'Yok')}",
        ]

        slots = bp.get("slots", [])
        if slots:
            satirlar.append(f"  {Renk.cyan('Parametreler:')}")
            for s in slots:
                satirlar.append(f"    - {s}")

        prompt = bp.get("prompt_template", "")
        if prompt:
            satirlar.append(f"  {Renk.cyan('Prompt Sabloni:')}")
            satirlar.append(f"    {prompt[:120].replace(chr(10), chr(10)+'    ')}")

        schedule = bp.get("schedule_template")
        if schedule:
            satirlar.append(f"  {Renk.yesil('Zamanlama:')} {schedule}")

        return "\n".join(satirlar)
    except Exception as e:
        return f"{Renk.kirmizi('[Blueprint]')} Detay hatasi: {e}"


def blueprint_calistir(ad: str, parametreler: Optional[dict] = None) -> str:
    """Blueprint'i calistir.

    Args:
        ad: Blueprint adi.
        parametreler: Blueprint parametreleri (slot degerleri).

    Returns:
        str: Calistirma sonucu.
    """
    try:
        bp = _blueprint_oku(ad)
        if not bp:
            return f"{Renk.kirmizi('[Blueprint]')} Blueprint bulunamadi: {ad}"

        parametreler = parametreler or {}
        slots = bp.get("slots", [])
        prompt_template = bp.get("prompt_template", "")

        # Slot degerlerini kontrol et
        for slot in slots:
            if slot not in parametreler:
                parametreler[slot] = f"<{slot}_degeri>"

        # Prompt'u doldur
        prompt = prompt_template
        for slot, deger in parametreler.items():
            prompt = prompt.replace("{{" + slot + "}}", str(deger))

        # Calistirma kaydi
        kayit = {
            "blueprint": ad,
            "calistirma_zamani": datetime.now().isoformat(),
            "parametreler": parametreler,
            "prompt": prompt[:200],
        }

        log_klasoru = PROJE_KOK / ".ReYMeN" / "logs" / "blueprints"
        log_klasoru.mkdir(parents=True, exist_ok=True)
        log_dosyasi = (
            log_klasoru / f"{ad}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        with open(str(log_dosyasi), "w", encoding="utf-8") as f:
            json.dump(kayit, f, indent=2, ensure_ascii=False)

        # Prompt ile bir alt surec baslat
        satirlar = [
            f"{Renk.yesil('[Blueprint]')} '{ad}' calistiriliyor...",
            f"  Parametreler: {parametreler}",
            f"  Log: {log_dosyasi}",
            f"\n{Renk.cyan('Olusturulan Prompt:')}",
            f"  {prompt[:200].replace(chr(10), chr(10)+'  ')}",
        ]

        if len(prompt) > 200:
            satirlar.append(f"  {Renk.soluk('... (devami kesildi)')}")

        satirlar.append(
            f"\n{Renk.kalin('Blueprint tamamlandi.')}"
        )

        return "\n".join(satirlar)
    except Exception as e:
        return f"{Renk.kirmizi('[Blueprint]')} Calistirma hatasi: {e}"
