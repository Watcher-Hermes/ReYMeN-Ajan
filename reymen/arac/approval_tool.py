# -*- coding: utf-8 -*-
"""
approval_tool.py — Onay sistemi aracı.

Hermes Agent approval_policy karşılığı.
Tehlikeli işlemler için kullanıcı onayı ister.
Auto-approve kuralları tanımlanabilir.

Dosya: .ReYMeN/approval_rules.json

Kullanım:
    from reymen.arac.approval_tool import ApprovalManager
    mgr = ApprovalManager()
    mgr.kontrol("terminal", "rm -rf /tmp/test")  # onay gerekli mi?
    mgr.onay_iste("terminal", "rm -rf /tmp/test")  # onay iste
"""

import json
import re
import time
from pathlib import Path
from typing import Optional, Dict, List, Any
from datetime import datetime


class ApprovalManager:
    """Onay sistemi yöneticisi."""

    # Varsayılan tehlike seviyeleri
    TEHLIKE_YUKSEK = "yuksek"
    TEHLIKE_ORTA = "orta"
    TEHLIKE_DUSUK = "dusuk"
    TEHLIKE_GUVENLI = "guvenli"

    # Varsayılan kurallar
    VARSAYILAN_KURALLAR = {
        "auto_approve": {
            "description": "Otomatik onay verilen işlemler",
            "rules": [
                {"tool": "read_file", "pattern": ".*"},
                {"tool": "search_files", "pattern": ".*"},
                {"tool": "web_extract", "pattern": ".*"},
                {"tool": "session_search", "pattern": ".*"},
                {"tool": "skills_list", "pattern": ".*"},
                {"tool": "skill_view", "pattern": ".*"},
                {"tool": "todo", "pattern": ".*"},
                {"tool": "memory", "pattern": ".*"},
                {"tool": "clarify", "pattern": ".*"},
            ]
        },
        "require_approval": {
            "description": "Onay gerektiren işlemler",
            "rules": [
                {"tool": "terminal", "pattern": r"rm\s+-rf", "reason": "Destructive file deletion"},
                {"tool": "terminal", "pattern": r"format\s+[a-zA-Z]:", "reason": "Disk format"},
                {"tool": "terminal", "pattern": r"del\s+/[sS]\s+/[qQ]", "reason": "Recursive delete"},
                {"tool": "terminal", "pattern": r"shutdown|reboot|restart", "reason": "System shutdown"},
                {"tool": "terminal", "pattern": r"net\s+user\s+.+\s+/delete", "reason": "User deletion"},
                {"tool": "terminal", "pattern": r"reg\s+delete", "reason": "Registry deletion"},
                {"tool": "image_generate", "pattern": ".*", "reason": "Image generation costs credits"},
                {"tool": "delegate_task", "pattern": ".*", "reason": "Sub-agent spawning"},
            ]
        },
        "block": {
            "description": "Engellenen işlemler",
            "rules": [
                {"tool": "terminal", "pattern": r"format\s+c:", "reason": "System drive format blocked"},
                {"tool": "terminal", "pattern": r"rd\s+/s\s+c:\\", "reason": "System root delete blocked"},
            ]
        }
    }

    def __init__(self, dosya: Optional[str] = None):
        self._dosya = Path(dosya) if dosya else (
            Path.home() / "AppData" / "Local" / "hermes" / "profiles" / "reymen" / ".ReYMeN" / "approval_rules.json"
        )
        self._dosya.parent.mkdir(parents=True, exist_ok=True)
        self._kurallar = {}
        self._gecmis: List[Dict] = []
        self._yukle()

    def _yukle(self):
        """Kuralları yükler."""
        if self._dosya.exists():
            try:
                data = json.loads(self._dosya.read_text(encoding="utf-8"))
                self._kurallar = data.get("kurallar", self.VARSAYILAN_KURALLAR)
                self._gecmis = data.get("gecmis", [])
            except Exception:
                self._kurallar = self.VARSAYILAN_KURALLAR
        else:
            self._kurallar = self.VARSAYILAN_KURALLAR
            self._kaydet()

    def _kaydet(self):
        """Kuralları kaydeder."""
        # Geçmişi son 1000 ile sınırla
        self._gecmis = self._gecmis[-1000:]
        data = {"kurallar": self._kurallar, "gecmis": self._gecmis}
        self._dosya.write_text(json.dumps(data, indent=2, ensure_ascii=False, default=str),
                               encoding="utf-8")

    def kontrol(self, tool: str, args: str = "") -> Dict:
        """
        İşlemin onay gerekip gerekmediğini kontrol eder.

        Returns:
            {"durum": "auto_approve|require_approval|block", "reason": "...", "tehlike": "..."}
        """
        # Block kontrolü
        for rule in self._kurallar.get("block", {}).get("rules", []):
            if rule["tool"] == tool and re.search(rule["pattern"], args, re.I):
                return {"durum": "block", "reason": rule.get("reason", "Engellendi"),
                        "tehlike": self.TEHLIKE_YUKSEK}

        # Auto-approve kontrolü
        for rule in self._kurallar.get("auto_approve", {}).get("rules", []):
            if rule["tool"] == tool and re.search(rule["pattern"], args, re.I):
                return {"durum": "auto_approve", "reason": "Otomatik onay",
                        "tehlike": self.TEHLIKE_GUVENLI}

        # Require approval kontrolü
        for rule in self._kurallar.get("require_approval", {}).get("rules", []):
            if rule["tool"] == tool and re.search(rule["pattern"], args, re.I):
                return {"durum": "require_approval", "reason": rule.get("reason", "Onay gerekli"),
                        "tehlike": self.TEHLIKE_ORTA}

        # Varsayılan: onay gerekli (güvenlik için)
        return {"durum": "require_approval", "reason": "Bilinmeyen işlem",
                "tehlike": self.TEHLIKE_DUSUK}

    def onay_iste(self, tool: str, args: str = "", timeout: int = 120) -> Dict:
        """
        Kullanıcıdan onay ister.

        Args:
            tool: Araç adı
            args: İşlem argümanları
            timeout: Zaman aşımı (saniye)

        Returns:
            {"onay": True/False, "reason": "...", "timeout": True/False}
        """
        kontrol = self.kontrol(tool, args)

        if kontrol["durum"] == "auto_approve":
            self._gecmis_ekle(tool, args, "auto_approve", True)
            return {"onay": True, "reason": "Otomatik onay", "timeout": False}

        if kontrol["durum"] == "block":
            self._gecmis_ekle(tool, args, "block", False)
            return {"onay": False, "reason": kontrol["reason"], "timeout": False}

        # Onay gerektiren durum — terminal modunda otomatik onay (2dk bekle)
        self._gecmis_ekle(tool, args, "require_approval", None)
        return {"onay": None, "reason": kontrol["reason"], "timeout": False,
                "mesaj": f"⚠️ Onay gerekli: {tool}({args[:100]}) — {kontrol['reason']}"}

    def _gecmis_ekle(self, tool: str, args: str, durum: str, onay: Optional[bool]):
        """Onay geçmişine kayıt ekler."""
        self._gecmis.append({
            "tool": tool,
            "args": args[:200],
            "durum": durum,
            "onay": onay,
            "zaman": datetime.now().isoformat(),
        })
        self._kaydet()

    def kural_ekle(self, kategori: str, tool: str, pattern: str,
                   reason: str = "") -> Dict:
        """Yeni kural ekler."""
        if kategori not in self._kurallar:
            self._kurallar[kategori] = {"description": "", "rules": []}

        self._kurallar[kategori]["rules"].append({
            "tool": tool,
            "pattern": pattern,
            "reason": reason,
        })
        self._kaydet()
        return {"ok": True, "kategori": kategori, "tool": tool}

    def kural_sil(self, kategori: str, tool: str, pattern: str) -> Dict:
        """Kural siler."""
        if kategori not in self._kurallar:
            return {"ok": False, "error": f"Kategori bulunamadı: {kategori}"}

        rules = self._kurallar[kategori]["rules"]
        onceki = len(rules)
        self._kurallar[kategori]["rules"] = [
            r for r in rules
            if not (r["tool"] == tool and r["pattern"] == pattern)
        ]

        if len(self._kurallar[kategori]["rules"]) < onceki:
            self._kaydet()
            return {"ok": True, "silinen": f"{tool}:{pattern}"}
        return {"ok": False, "error": "Kural bulunamadı."}

    def gecmis(self, limit: int = 20) -> List[Dict]:
        """Onay geçmişini döner."""
        return self._gecmis[-limit:]

    def formatla(self) -> str:
        """Kuralları okunabilir format döner."""
        satirlar = ["📋 Onay Kuralları:\n"]

        for kategori, data in self._kurallar.items():
            emoji = {"auto_approve": "✅", "require_approval": "⚠️", "block": "🚫"}.get(kategori, "❓")
            satirlar.append(f"\n{emoji} {kategori.upper()} ({len(data.get('rules', []))} kural):")
            for rule in data.get("rules", []):
                satirlar.append(f"  • {rule['tool']} / {rule['pattern']} — {rule.get('reason', '')}")

        return "\n".join(satirlar)


# ── Motor Entegrasyonu ───────────────────────────────────────────────────────

_mgr = None

def _get_mgr() -> ApprovalManager:
    global _mgr
    if _mgr is None:
        _mgr = ApprovalManager()
    return _mgr


def run(islem: str = "kontrol", tool: str = "", args: str = "",
        kategori: str = "", pattern: str = "", reason: str = "") -> str:
    """
    Motor entegrasyonu için run fonksiyonu.

    islem: kontrol/onay_iste/kural_ekle/kural_sil/gecmis/listele
    """
    mgr = _get_mgr()

    if islem == "kontrol":
        if not tool:
            return "[Hata]: tool parametresi gerekli."
        r = mgr.kontrol(tool, args)
        emoji = {"auto_approve": "✅", "require_approval": "⚠️", "block": "🚫"}.get(r["durum"], "❓")
        return f"{emoji} {r['durum']} — {r['reason']} (tehlike: {r['tehlike']})"

    elif islem == "onay_iste":
        if not tool:
            return "[Hata]: tool parametresi gerekli."
        r = mgr.onay_iste(tool, args)
        if r.get("mesaj"):
            return r["mesaj"]
        return f"{'✅ Onaylandı' if r['onay'] else '🚫 Reddedildi'} — {r['reason']}"

    elif islem == "kural_ekle":
        if not kategori or not tool or not pattern:
            return "[Hata]: kategori, tool ve pattern gerekli."
        r = mgr.kural_ekle(kategori, tool, pattern, reason)
        return f"✅ Kural eklendi: {kategori}/{tool}/{pattern}"

    elif islem == "kural_sil":
        if not kategori or not tool or not pattern:
            return "[Hata]: kategori, tool ve pattern gerekli."
        r = mgr.kural_sil(kategori, tool, pattern)
        return f"✅ Kural silindi" if r["ok"] else f"[Hata]: {r['error']}"

    elif islem == "gecmis":
        gecmis = mgr.gecmis()
        if not gecmis:
            return "📋 Onay geçmişi boş."
        satirlar = []
        for g in gecmis[-10:]:
            emoji = {"auto_approve": "✅", "require_approval": "⚠️", "block": "🚫"}.get(g["durum"], "❓")
            onay_str = "✓" if g.get("onay") else "✗" if g.get("onay") is False else "?"
            satirlar.append(f"{emoji} {onay_str} {g['tool']}({g['args'][:40]}) — {g['zaman']}")
        return "📋 Onay Geçmişi:\n" + "\n".join(satirlar)

    else:  # listele
        return mgr.formatla()


if __name__ == "__main__":
    import sys
    print(run(islem=sys.argv[1] if len(sys.argv) > 1 else "listele"))
