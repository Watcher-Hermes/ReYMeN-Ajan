# -*- coding: utf-8 -*-
"""
profile_tool.py — Çoklu profil yönetimi.

Hermes Agent profile system karşılığı.
Profiller arası geçiş, profil bilgileri, profil izolasyonu.

Dosya: .ReYMeN/profiles.json

Kullanım:
    from reymen.arac.profile_tool import ProfileManager
    mgr = ProfileManager()
    mgr.aktif_profil()
    mgr.gecis("kiral38")
"""

import json
import os
from pathlib import Path
from typing import Optional, Dict, List, Any


class Profile:
    """Tek bir profil tanımı."""

    def __init__(self, ad: str, aciklama: str = "", bot_token: str = "",
                 model: str = "xiaomi", provider: str = "xiaomi",
                 renk: str = "🔵", aktif: bool = False, ozel: Optional[Dict] = None):
        self.ad = ad
        self.aciklama = aciklama
        self.bot_token = bot_token
        self.model = model
        self.provider = provider
        self.renk = renk
        self.aktif = aktif
        self.ozel = ozel or {}

    def to_dict(self) -> Dict:
        return {
            "ad": self.ad,
            "aciklama": self.aciklama,
            "bot_token": self.bot_token,
            "model": self.model,
            "provider": self.provider,
            "renk": self.renk,
            "aktif": self.aktif,
            "ozel": self.ozel,
        }


class ProfileManager:
    """Profil yöneticisi."""

    # Varsayılan profiller
    VARSAYILAN_PROFILLER = [
        Profile("reymen", "Ana ReYMeN botu", renk="🔵", model="mimo-v2.5-pro", provider="xiaomi"),
        Profile("kiral38", "Kiral38 botu", renk="🟢", model="mimo-v2.5-pro", provider="xiaomi"),
        Profile("root", "Root/Paşa botu", renk="🔴", model="mimo-v2.5-pro", provider="xiaomi"),
    ]

    def __init__(self, dosya: Optional[str] = None):
        self._dosya = Path(dosya) if dosya else (
            Path.home() / "AppData" / "Local" / "hermes" / "profiles" / "reymen" / ".ReYMeN" / "profiles.json"
        )
        self._dosya.parent.mkdir(parents=True, exist_ok=True)
        self._profiller: Dict[str, Profile] = {}
        self._aktif: str = "reymen"
        self._yukle()

    def _yukle(self):
        """Profilleri yükler."""
        if self._dosya.exists():
            try:
                data = json.loads(self._dosya.read_text(encoding="utf-8"))
                for p in data.get("profiller", []):
                    prof = Profile(**p)
                    self._profiller[prof.ad] = prof
                self._aktif = data.get("aktif", "reymen")
            except Exception:
                self._varsayilan_olustur()
        else:
            self._varsayilan_olustur()

    def _varsayilan_olustur(self):
        """Varsayılan profilleri oluşturur."""
        for p in self.VARSAYILAN_PROFILLER:
            self._profiller[p.ad] = p
        self._profiller[self._aktif].aktif = True
        self._kaydet()

    def _kaydet(self):
        """Profilleri kaydeder."""
        data = {
            "aktif": self._aktif,
            "profiller": [p.to_dict() for p in self._profiller.values()]
        }
        self._dosya.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    def aktif_profil(self) -> Dict:
        """Aktif profil bilgisini döner."""
        if self._aktif in self._profiller:
            return self._profiller[self._aktif].to_dict()
        return {"ad": self._aktif, "aciklama": "Bilinmeyen profil"}

    def listele(self) -> List[Dict]:
        """Tüm profilleri listeler."""
        return [p.to_dict() for p in self._profiller.values()]

    def gecis(self, profil_ad: str) -> Dict:
        """Profil değiştirir."""
        if profil_ad not in self._profiller:
            return {"ok": False, "error": f"Profil bulunamadı: {profil_ad}"}

        # Eski profili pasif yap
        if self._aktif in self._profiller:
            self._profiller[self._aktif].aktif = False

        self._aktif = profil_ad
        self._profiller[profil_ad].aktif = True
        self._kaydet()

        return {"ok": True, "aktif": profil_ad, "profil": self._profiller[profil_ad].to_dict()}

    def ekle(self, ad: str, aciklama: str = "", model: str = "mimo-v2.5-pro",
             provider: str = "xiaomi", renk: str = "⚪", bot_token: str = "") -> Dict:
        """Yeni profil ekler."""
        if ad in self._profiller:
            return {"ok": False, "error": f"Profil zaten var: {ad}"}

        prof = Profile(ad=ad, aciklama=aciklama, model=model, provider=provider,
                       renk=renk, bot_token=bot_token)
        self._profiller[ad] = prof
        self._kaydet()
        return {"ok": True, "profil": prof.to_dict()}

    def guncelle(self, ad: str, **kwargs) -> Dict:
        """Profil bilgilerini günceller."""
        if ad not in self._profiller:
            return {"ok": False, "error": f"Profil bulunamadı: {ad}"}

        prof = self._profiller[ad]
        for k, v in kwargs.items():
            if hasattr(prof, k):
                setattr(prof, k, v)

        self._kaydet()
        return {"ok": True, "profil": prof.to_dict()}

    def sil(self, ad: str) -> Dict:
        """Profil siler."""
        if ad not in self._profiller:
            return {"ok": False, "error": f"Profil bulunamadı: {ad}"}
        if ad == self._aktif:
            return {"ok": False, "error": "Aktif profil silinemez."}

        del self._profiller[ad]
        self._kaydet()
        return {"ok": True, "silinen": ad}

    def profil_yolu(self, ad: Optional[str] = None) -> str:
        """Profil dizin yolunu döner."""
        ad = ad or self._aktif
        return str(Path.home() / "AppData" / "Local" / "hermes" / "profiles" / ad)

    def formatla(self) -> str:
        """Profilleri okunabilir format döner."""
        if not self._profiller:
            return "📋 Profil yok."

        satirlar = []
        for ad, prof in self._profiller.items():
            aktif_str = " ← AKTİF" if ad == self._aktif else ""
            satirlar.append(f"{prof.renk} {prof.ad} | {prof.aciklama} | Model: {prof.model}{aktif_str}")

        return f"📋 Profiller ({len(self._profiller)}):\n" + "\n".join(satirlar)


# ── Motor Entegrasyonu ───────────────────────────────────────────────────────

_mgr = None

def _get_mgr() -> ProfileManager:
    global _mgr
    if _mgr is None:
        _mgr = ProfileManager()
    return _mgr


def run(islem: str = "listele", profil_ad: str = "", aciklama: str = "",
        model: str = "", provider: str = "", renk: str = "") -> str:
    """
    Motor entegrasyonu için run fonksiyonu.

    islem: aktif/listele/gecis/ekle/guncelle/sil/yol
    """
    mgr = _get_mgr()

    if islem == "aktif":
        p = mgr.aktif_profil()
        return f"{p.get('renk', '🔵')} Aktif Profil: {p['ad']} | {p.get('aciklama', '')} | Model: {p.get('model', '?')}"

    elif islem == "gecis":
        if not profil_ad:
            return "[Hata]: profil_ad gerekli."
        r = mgr.gecis(profil_ad)
        return f"✅ Profil değiştirildi: {r['aktif']}" if r["ok"] else f"[Hata]: {r['error']}"

    elif islem == "ekle":
        if not profil_ad:
            return "[Hata]: profil_ad gerekli."
        r = mgr.ekle(profil_ad, aciklama=aciklama, model=model or "mimo-v2.5-pro",
                     provider=provider or "xiaomi", renk=renk or "⚪")
        return f"✅ Profil eklendi: {profil_ad}" if r["ok"] else f"[Hata]: {r['error']}"

    elif islem == "sil":
        if not profil_ad:
            return "[Hata]: profil_ad gerekli."
        r = mgr.sil(profil_ad)
        return f"🗑️ Profil silindi: {profil_ad}" if r["ok"] else f"[Hata]: {r['error']}"

    elif islem == "yol":
        return mgr.profil_yolu(profil_ad or None)

    else:  # listele
        return mgr.formatla()


if __name__ == "__main__":
    import sys
    print(run(islem=sys.argv[1] if len(sys.argv) > 1 else "listele"))
