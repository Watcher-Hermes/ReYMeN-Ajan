# -*- coding: utf-8 -*-
"""
reymen_memory_provider.py — ReYMeN özel memory yönetimi.

Hermes built-in memory tool'unu override eder.
MEMORY.md + USER.md dosyalarını direkt yönetir.
Limit: 50.000 karakter (config'deki memory_char_limit'i kullanır).
"""

import json
import os
import re
import time
from pathlib import Path
from typing import Optional, Dict, List, Any

# ── Varsayılan yapılandırma ──────────────────────────────────────────────────

DEFAULT_MEMORY_LIMIT = 50000
DEFAULT_USER_LIMIT = 50000

PROFILE_DIR = Path(os.path.expanduser(
    "~/AppData/Local/hermes/profiles/reymen"
))
MEMORY_FILE = PROFILE_DIR / "MEMORY.md"
USER_FILE = PROFILE_DIR / "USER.md"


# ── Yardımcılar ─────────────────────────────────────────────────────────────

def _profil_yukle(dosya: Path) -> list:
    """MEMORY.md / USER.md'yi satır listesi olarak yükle."""
    if not dosya.exists():
        return []
    try:
        with open(dosya, "r", encoding="utf-8") as f:
            return f.read().split("\n")
    except Exception:
        return []


def _profil_kaydet(dosya: Path, satirlar: list):
    """Satır listesini dosyaya yaz."""
    dosya.parent.mkdir(parents=True, exist_ok=True)
    with open(dosya, "w", encoding="utf-8") as f:
        f.write("\n".join(satirlar))


def _config_oku() -> Dict[str, int]:
    """config.yaml'den memory limitlerini oku."""
    limit = DEFAULT_MEMORY_LIMIT
    try:
        import yaml
        cf = PROFILE_DIR / "config.yaml"
        if cf.exists():
            with open(cf, encoding="utf-8") as f:
                d = yaml.safe_load(f)
            limit = d.get("memory_char_limit", DEFAULT_MEMORY_LIMIT)
    except Exception:
        pass
    return {"memory": limit, "user": limit}


# ── Ana Sınıf ────────────────────────────────────────────────────────────────

class ReYMeNMemoryProvider:
    """
    ReYMeN memory yöneticisi.

    Hermes built-in memory tool API'si ile uyumlu:
    - action: add, replace, remove (tekli)
    - operations: batch (çoklu)
    - target: memory, user

    Limit: 50.000 karakter (config override edilebilir)
    """

    def __init__(self):
        self._limits = _config_oku()
        self._cache: Dict[str, list] = {}

    # ── Dosya Yönetimi ──────────────────────────────────────────────────

    def _dosya(self, target: str) -> Path:
        return MEMORY_FILE if target == "memory" else USER_FILE

    def _yukle(self, target: str) -> list:
        if target not in self._cache:
            self._cache[target] = _profil_yukle(self._dosya(target))
        return self._cache[target]

    def _kaydet(self, target: str):
        _profil_kaydet(self._dosya(target), self._cache.get(target, []))

    def _toplam_char(self, target: str) -> int:
        satirlar = self._yukle(target)
        return sum(len(s) + 1 for s in satirlar)  # +1 for newline

    def _limit_as(self, target: str) -> int:
        return self._limits.get(target, DEFAULT_MEMORY_LIMIT)

    # ── Entry İşlemleri ─────────────────────────────────────────────────

    def _entry_bul(self, target: str, old_text: str) -> Optional[int]:
        """old_text içeren entry'in index'ini bul."""
        satirlar = self._yukle(target)
        for i, satir in enumerate(satirlar):
            if old_text in satir:
                return i
        return None

    def ekle(self, target: str, content: str) -> dict:
        """Yeni entry ekle."""
        satirlar = self._yukle(target)
        mevcut = self._toplam_char(target)
        limit = self._limit_as(target)

        if mevcut + len(content) + 1 > limit:
            return {
                "success": False,
                "error": f"Memory at {mevcut}/{limit} chars. "
                         f"Adding this entry ({len(content)} chars) would exceed the limit. "
                         f"Use replace/remove to free space first.",
                "usage": f"{mevcut}/{limit}",
                "entries": satirlar[:],
            }

        satirlar.append(content)
        self._kaydet(target)
        yeni = self._toplam_char(target)
        return {
            "success": True,
            "usage": f"{yeni}/{limit}",
            "entry_count": len(satirlar),
        }

    def degistir(self, target: str, old_text: str, content: str) -> dict:
        """Eski entry'i yenisiyle değiştir."""
        idx = self._entry_bul(target, old_text)
        if idx is None:
            matches = [s for s in self._yukle(target) if old_text in s]
            if len(matches) > 1:
                return {
                    "success": False,
                    "error": f"Multiple entries matched '{old_text[:50]}'. Be more specific.",
                    "matches": matches[:5],
                }
            return {
                "success": False,
                "error": f"No entry matched '{old_text[:50]}'.",
            }

        satirlar = self._yukle(target)
        satirlar[idx] = content
        self._kaydet(target)
        yeni = self._toplam_char(target)
        return {
            "success": True,
            "usage": f"{yeni}/{self._limit_as(target)}",
            "entry_count": len(satirlar),
        }

    def sil(self, target: str, old_text: str) -> dict:
        """Entry sil."""
        idx = self._entry_bul(target, old_text)
        if idx is None:
            matches = [s for s in self._yukle(target) if old_text in s]
            if len(matches) > 1:
                return {
                    "success": False,
                    "error": f"Multiple entries matched '{old_text[:50]}'.",
                    "matches": matches[:5],
                }
            return {
                "success": False,
                "error": f"No entry matched '{old_text[:50]}'.",
            }

        satirlar = self._yukle(target)
        silinen = satirlar.pop(idx)
        self._kaydet(target)
        yeni = self._toplam_char(target)
        return {
            "success": True,
            "usage": f"{yeni}/{self._limit_as(target)}",
            "entry_count": len(satirlar),
            "removed": silinen[:80],
        }

    # ── Batch İşlem ─────────────────────────────────────────────────────

    def batch(self, target: str, operations: list) -> dict:
        """Atomik batch işlem."""
        for op in operations:
            action = op.get("action")
            if action == "add":
                r = self.ekle(target, op.get("content", ""))
            elif action == "replace":
                r = self.degistir(target, op.get("old_text", ""), op.get("content", ""))
            elif action == "remove":
                r = self.sil(target, op.get("old_text", ""))
            else:
                continue
            if not r.get("success"):
                return r
        return {"success": True, "message": "Batch completed."}

    # ── Durum ───────────────────────────────────────────────────────────

    def durum(self, target: Optional[str] = None) -> dict:
        """Memory durumunu döndür."""
        if target:
            t = self._toplam_char(target)
            l = self._limit_as(target)
            return {
                "target": target,
                "usage": f"{t}/{l}",
                "percent": round(t / l * 100),
                "entries": len(self._yukle(target)),
            }

        return {
            "memory": self.durum("memory"),
            "user": self.durum("user"),
        }

    def inject_prompt(self) -> str:
        """Sistem prompt'una eklenecek memory metnini üret."""
        mem = self._yukle("memory")
        usr = self._yukle("user")
        m_usage = self.durum("memory")
        u_usage = self.durum("user")

        parcalar = []
        if mem:
            mem_text = "\n".join(mem)
            pct = m_usage["percent"]
            parcalar.append(
                f"MEMORY (your personal notes) [{pct}% — {m_usage['usage']} chars]\n"
                f"{'─' * 50}\n{mem_text}\n{'─' * 50}"
            )
        if usr:
            usr_text = "\n".join(usr)
            pct = u_usage["percent"]
            parcalar.append(
                f"USER PROFILE (who the user is) [{pct}% — {u_usage['usage']} chars]\n"
                f"{'─' * 50}\n{usr_text}\n{'─' * 50}"
            )

        return "\n\n".join(parcalar)


# ── Global Singleton ─────────────────────────────────────────────────────────

_provider: Optional[ReYMeNMemoryProvider] = None


def get_provider() -> ReYMeNMemoryProvider:
    global _provider
    if _provider is None:
        _provider = ReYMeNMemoryProvider()
    # Her çağrıda config'i yeniden oku (dynamic override)
    _provider._limits = _config_oku()
    return _provider


# ── Motor Kayıt Fonksiyonu ───────────────────────────────────────────────────

def motor_kaydet(motor):
    """
    motor.py'ye kaydetmek için.
    MEMORY_GENISLET, USER_GENISLET, HAFIZA_DURUMU araçlarını ekler.
    """
    provider = get_provider()

    def memory_ekle(icerik: str = "", hedef: str = "memory"):
        r = provider.ekle(hedef, icerik)
        if r.get("success"):
            return f"✅ Memory kaydedildi ({r['usage']})"
        return f"❌ {r.get('error', 'Bilinmeyen hata')}"

    def memory_sil(eski: str = "", hedef: str = "memory"):
        r = provider.sil(hedef, eski)
        if r.get("success"):
            return f"✅ Silindi ({r['usage']})"
        return f"❌ {r.get('error', 'Bilinmeyen hata')}"

    def memory_durum():
        d = provider.durum()
        m = d.get("memory", {})
        u = d.get("user", {})
        return (f"📦 Memory: {m.get('usage', '?')} ({m.get('entries', 0)} entry)\n"
                f"👤 User:   {u.get('usage', '?')} ({u.get('entries', 0)} entry)")

    motor._plugin_arac_kaydet(
        "MEMORY_EKLE", memory_ekle,
        "Hafızaya yeni bilgi ekle. Kullanım: MEMORY_EKLE(\"icerik\", \"memory|user\")"
    )
    motor._plugin_arac_kaydet(
        "MEMORY_SIL", memory_sil,
        "Hafızadan entry sil. Kullanım: MEMORY_SIL(\"eski metin\", \"memory|user\")"
    )
    motor._plugin_arac_kaydet(
        "MEMORY_DURUM", memory_durum,
        "Hafıza durumunu göster"
    )


def memory_tool_run(action: str = "add", target: str = "memory",
                    content: str = "", old_text: str = "",
                    operations: list = None) -> str:
    """
    Hermes memory tool API'si ile uyumlu fonksiyon.

    Doğrudan ToolRegistry'den çağrılabilir.
    Hermes built-in memory tool'unu override eder.
    """
    provider = get_provider()

    if operations:
        r = provider.batch(target, operations)
        return json.dumps(r, ensure_ascii=False)

    if action == "add":
        r = provider.ekle(target, content)
    elif action == "replace":
        r = provider.degistir(target, old_text, content)
    elif action == "remove":
        r = provider.sil(target, old_text)
    elif action == "status" or action == "durum":
        return json.dumps(provider.durum(target), ensure_ascii=False)
    else:
        return json.dumps({"success": False, "error": f"Unknown action: {action}"},
                         ensure_ascii=False)

    # Hermes formatında döndür
    if r.get("success"):
        if action == "add":
            return json.dumps({
                "success": True, "done": True,
                "target": target,
                "usage": r["usage"],
                "entry_count": r.get("entry_count", 0),
                "message": "Entry added."
            }, ensure_ascii=False)
        elif action == "remove":
            return json.dumps({
                "success": True, "done": True,
                "target": target,
                "usage": r["usage"],
                "entry_count": r.get("entry_count", 0),
                "message": "Entry removed.",
                "removed": r.get("removed", "")
            }, ensure_ascii=False)
        else:
            return json.dumps({
                "success": True, "done": True,
                "target": target,
                "usage": r["usage"],
                "entry_count": r.get("entry_count", 0),
                "message": "Entry updated."
            }, ensure_ascii=False)
    else:
        return json.dumps(r, ensure_ascii=False)
