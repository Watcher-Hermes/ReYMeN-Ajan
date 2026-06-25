# -*- coding: utf-8 -*-
"""
memory_batch_tool.py — Toplu bellek işlem aracı.

Hermes Agent memory tool (batch operations) karşılığı.
Tek çağrıda birden fazla bellek işlemi yapar.

Kullanım:
    from reymen.arac.memory_batch_tool import MemoryBatch
    mb = MemoryBatch()
    mb.isle([
        {"action": "add", "content": "Kullanıcı Python 3.11 kullanıyor"},
        {"action": "replace", "old_text": "Python 3.10", "content": "Python 3.11"},
    ])
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Optional, Any
from datetime import datetime


class MemoryBatch:
    """Toplu bellek işlem yöneticisi."""

    def __init__(self, memory_path: Optional[str] = None, user_path: Optional[str] = None):
        base = Path.home() / "AppData" / "Local" / "hermes" / "profiles" / "reymen"
        self._memory_path = Path(memory_path) if memory_path else base / "memories" / "MEMORY.md"
        self._user_path = Path(user_path) if user_path else base / "memories" / "USER.md"
        self._decisions_path = base / ".ReYMeN" / "decisions.md"

        for p in [self._memory_path.parent, self._decisions_path.parent]:
            p.mkdir(parents=True, exist_ok=True)

    def _oku(self, target: str) -> str:
        """Belirtilen hedefi okur."""
        path = self._hedef_yolu(target)
        if path.exists():
            return path.read_text(encoding="utf-8")
        return ""

    def _yaz(self, target: str, content: str):
        """Belirtilen hedefe yazar."""
        path = self._hedef_yolu(target)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def _hedef_yolu(self, target: str) -> Path:
        """Hedef adından dosya yolu döner."""
        if target == "user":
            return self._user_path
        elif target == "decisions":
            return self._decisions_path
        else:
            return self._memory_path

    def _char_limit(self, target: str) -> int:
        """Hedef için karakter limiti."""
        return 2200 if target == "memory" else 1375 if target == "user" else 50000

    def add(self, content: str, target: str = "memory") -> Dict:
        """Yeni bellek girdisi ekler."""
        mevcut = self._oku(target)
        limit = self._char_limit(target)

        # § ayıracı ile ekle
        yeni = mevcut.rstrip() + "\n§\n" + content if mevcut else content

        if len(yeni) > limit:
            return {"ok": False, "error": f"Limit aşıldı ({len(yeni)}/{limit} char). Eski girdileri temizleyin.",
                    "current_chars": len(mevcut), "limit": limit}

        self._yaz(target, yeni)
        return {"ok": True, "current_chars": len(yeni), "limit": limit, "target": target}

    def replace(self, old_text: str, new_text: str, target: str = "memory") -> Dict:
        """Mevcut girdiyi değiştirir."""
        mevcut = self._oku(target)
        if old_text not in mevcut:
            return {"ok": False, "error": f"Eşleşme bulunamadı: '{old_text[:50]}...'"}

        yeni = mevcut.replace(old_text, new_text, 1)
        limit = self._char_limit(target)

        if len(yeni) > limit:
            return {"ok": False, "error": f"Limit aşıldı ({len(yeni)}/{limit} char)."}

        self._yaz(target, yeni)
        return {"ok": True, "current_chars": len(yeni), "limit": limit, "target": target}

    def remove(self, old_text: str, target: str = "memory") -> Dict:
        """Girdiyi siler."""
        mevcut = self._oku(target)
        if old_text not in mevcut:
            return {"ok": False, "error": f"Eşleşme bulunamadı: '{old_text[:50]}...'"}

        yeni = mevcut.replace(old_text, "", 1)
        # Boş § satırlarını temizle
        yeni = yeni.replace("\n§\n§\n", "\n§\n").strip()

        self._yaz(target, yeni)
        return {"ok": True, "current_chars": len(yeni), "target": target}

    def isle(self, operations: List[Dict]) -> Dict:
        """
        Toplu bellek işlemi yapar.

        Args:
            operations: [{"action": "add|replace|remove", "content": "...", "old_text": "...", "target": "memory|user"}, ...]

        Returns:
            {"results": [...], "current_chars": N, "limit": N}
        """
        results = []
        son_target = "memory"

        for op in operations:
            action = op.get("action", "")
            target = op.get("target", "memory")
            content = op.get("content", "")
            old_text = op.get("old_text", "")

            son_target = target

            if action == "add":
                if not content:
                    results.append({"action": "add", "ok": False, "error": "content boş."})
                    continue
                results.append({"action": "add", **self.add(content, target)})

            elif action == "replace":
                if not old_text or not content:
                    results.append({"action": "replace", "ok": False, "error": "old_text ve content gerekli."})
                    continue
                results.append({"action": "replace", **self.replace(old_text, content, target)})

            elif action == "remove":
                if not old_text:
                    results.append({"action": "remove", "ok": False, "error": "old_text gerekli."})
                    continue
                results.append({"action": "remove", **self.remove(old_text, target)})

            else:
                results.append({"action": action, "ok": False, "error": f"Bilinmeyen işlem: {action}"})

        # Son durum
        mevcut = self._oku(son_target)
        limit = self._char_limit(son_target)

        return {
            "results": results,
            "current_chars": len(mevcut),
            "limit": limit,
            "percent": f"{len(mevcut)/limit*100:.0f}%",
        }

    def decision_ekle(self, ne_yaptin: str, neden: str, alternatif: str = "") -> Dict:
        """Karar kaydı ekler."""
        mevcut = self._oku("decisions")
        tarih = datetime.now().strftime("%Y-%m-%d %H:%M")

        yeni_kayit = f"\n\n## {tarih}\n"
        yeni_kayit += f"1. **Ne yaptın?** {ne_yaptin}\n"
        yeni_kayit += f"2. **Neden?** {neden}\n"
        if alternatif:
            yeni_kayit += f"3. **Alternatif?** {alternatif}\n"

        self._yaz("decisions", mevcut + yeni_kayit)
        return {"ok": True, "tarih": tarih}


# ── Motor Entegrasyonu ───────────────────────────────────────────────────────

_mb = None

def _get_mb() -> MemoryBatch:
    global _mb
    if _mb is None:
        _mb = MemoryBatch()
    return _mb


def run(islem: str = "okuma", target: str = "memory", content: str = "",
        old_text: str = "", new_text: str = "", operations: str = "",
        ne_yaptin: str = "", neden: str = "", alternatif: str = "") -> str:
    """
    Motor entegrasyonu için run fonksiyonu.

    islem: ekle/degistir/sil/oku/toplu/karar
    """
    mb = _get_mb()

    if islem == "ekle":
        if not content:
            return "[Hata]: content gerekli."
        r = mb.add(content, target)
        return f"✅ Eklendi ({r.get('current_chars', '?')}/{r.get('limit', '?')} char)" if r["ok"] else f"[Hata]: {r['error']}"

    elif islem == "degistir":
        if not old_text or not new_text:
            return "[Hata]: old_text ve new_text gerekli."
        r = mb.replace(old_text, new_text, target)
        return f"✅ Değiştirildi" if r["ok"] else f"[Hata]: {r['error']}"

    elif islem == "sil":
        if not old_text:
            return "[Hata]: old_text gerekli."
        r = mb.remove(old_text, target)
        return f"✅ Silindi" if r["ok"] else f"[Hata]: {r['error']}"

    elif islem == "oku":
        content = mb._oku(target)
        limit = mb._char_limit(target)
        return f"📖 {target} ({len(content)}/{limit} char - {len(content)/limit*100:.0f}%):\n\n{content}"

    elif islem == "toplu":
        if not operations:
            return "[Hata]: operations JSON gerekli."
        try:
            ops = json.loads(operations) if isinstance(operations, str) else operations
        except json.JSONDecodeError:
            return "[Hata]: operations geçerli JSON değil."
        r = mb.isle(ops)
        satirlar = []
        for sonuc in r["results"]:
            emoji = "✅" if sonuc.get("ok") else "❌"
            satirlar.append(f"{emoji} {sonuc['action']}: {sonuc.get('error', 'OK')}")
        return f"📋 Toplu Sonuç ({r['percent']} dolu):\n" + "\n".join(satirlar)

    elif islem == "karar":
        if not ne_yaptin or not neden:
            return "[Hata]: ne_yaptin ve neden gerekli."
        r = mb.decision_ekle(ne_yaptin, neden, alternatif)
        return f"✅ Karar kaydedildi: {r['tarih']}"

    return f"[Hata]: Bilinmeyen islem: {islem}"


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Kullanım: python memory_batch_tool.py <islem> [parametreler]")
        sys.exit(1)
    print(run(islem=sys.argv[1], content=sys.argv[2] if len(sys.argv) > 2 else ""))
