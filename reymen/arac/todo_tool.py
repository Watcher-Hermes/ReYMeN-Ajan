# -*- coding: utf-8 -*-
"""
todo_tool.py — Görev listesi yönetimi.

Hermes Agent todo_tool karşılığı.
Görevleri oluştur, güncelle, durum değiştir, sırala.

Dosya: .ReYMeN/todos.json

Kullanım:
    from reymen.arac.todo_tool import TodoManager
    mgr = TodoManager()
    mgr.ekle("Motor entegrasyonu", oncelik=1)
    mgr.tamamla("Motor entegrasyonu")
    print(mgr.listele())
"""

import json
import os
import time
from pathlib import Path
from typing import List, Dict, Optional, Any
from datetime import datetime


class TodoManager:
    """Görev listesi yöneticisi."""

    DURUM_BEKLIYOR = "bekliyor"
    DURUM_DEVAM = "devam"
    DURUM_TAMAM = "tamam"
    DURUM_IPTAL = "iptal"

    def __init__(self, dosya: Optional[str] = None):
        if dosya:
            self._dosya = Path(dosya)
        else:
            self._dosya = Path.home() / "AppData" / "Local" / "hermes" / "profiles" / "reymen" / ".ReYMeN" / "todos.json"
        self._dosya.parent.mkdir(parents=True, exist_ok=True)
        self._gorevler = self._yukle()

    def _yukle(self) -> List[Dict]:
        """Görevleri dosyadan yükler."""
        if self._dosya.exists():
            try:
                return json.loads(self._dosya.read_text(encoding="utf-8"))
            except Exception:
                return []
        return []

    def _kaydet(self):
        """Görevleri dosyaya kaydeder."""
        self._dosya.write_text(
            json.dumps(self._gorevler, indent=2, ensure_ascii=False, default=str),
            encoding="utf-8"
        )

    def _id_uret(self) -> str:
        """Benzersiz ID üretir."""
        return f"t_{int(time.time()*1000) % 10000000}"

    def ekle(self, icerik: str, oncelik: int = 0, etiketler: Optional[List[str]] = None,
             son_tarih: Optional[str] = None) -> Dict:
        """Yeni görev ekler."""
        gorev = {
            "id": self._id_uret(),
            "icerik": icerik,
            "durum": self.DURUM_BEKLIYOR,
            "oncelik": oncelik,
            "etiketler": etiketler or [],
            "son_tarih": son_tarih,
            "olusturma": datetime.now().isoformat(),
            "guncelleme": datetime.now().isoformat(),
        }
        self._gorevler.append(gorev)
        self._kaydet()
        return gorev

    def guncelle(self, gorev_id: str, **kwargs) -> Optional[Dict]:
        """Görevi günceller."""
        for g in self._gorevler:
            if g["id"] == gorev_id:
                for k, v in kwargs.items():
                    if k in g:
                        g[k] = v
                g["guncelleme"] = datetime.now().isoformat()
                self._kaydet()
                return g
        return None

    def tamamla(self, gorev_id: str) -> Optional[Dict]:
        """Görevi tamamlanmış olarak işaretler."""
        return self.guncelle(gorev_id, durum=self.DURUM_TAMAM)

    def iptal(self, gorev_id: str) -> Optional[Dict]:
        """Görevi iptal eder."""
        return self.guncelle(gorev_id, durum=self.DURUM_IPTAL)

    def baslat(self, gorev_id: str) -> Optional[Dict]:
        """Görevi devam ediyor olarak işaretler."""
        return self.guncelle(gorev_id, durum=self.DURUM_DEVAM)

    def sil(self, gorev_id: str) -> bool:
        """Görevi siler."""
        onceki = len(self._gorevler)
        self._gorevler = [g for g in self._gorevler if g["id"] != gorev_id]
        if len(self._gorevler) < onceki:
            self._kaydet()
            return True
        return False

    def listele(self, durum: Optional[str] = None, etiket: Optional[str] = None,
                limit: int = 50) -> List[Dict]:
        """Görevleri listeler."""
        sonuc = self._gorevler

        if durum:
            sonuc = [g for g in sonuc if g["durum"] == durum]
        if etiket:
            sonuc = [g for g in sonuc if etiket in g.get("etiketler", [])]

        # Öncelik sırası (yüksek önce), sonra tarih
        sonuc.sort(key=lambda g: (-g.get("oncelik", 0), g.get("olusturma", "")))

        return sonuc[:limit]

    def getir(self, gorev_id: str) -> Optional[Dict]:
        """Tekil görev getirir."""
        for g in self._gorevler:
            if g["id"] == gorev_id:
                return g
        return None

    def istatistik(self) -> Dict:
        """İstatistik döner."""
        toplam = len(self._gorevler)
        durumlar = {}
        for g in self._gorevler:
            d = g["durum"]
            durumlar[d] = durumlar.get(d, 0) + 1

        return {
            "toplam": toplam,
            "bekliyor": durumlar.get(self.DURUM_BEKLIYOR, 0),
            "devam": durumlar.get(self.DURUM_DEVAM, 0),
            "tamam": durumlar.get(self.DURUM_TAMAM, 0),
            "iptal": durumlar.get(self.DURUM_IPTAL, 0),
        }

    def temizle(self, sadece_tamamlanan: bool = True) -> int:
        """Tamamlanan/iptal görevleri temizler."""
        onceki = len(self._gorevler)
        if sadece_tamamlanan:
            self._gorevler = [g for g in self._gorevler
                              if g["durum"] not in (self.DURUM_TAMAM, self.DURUM_IPTAL)]
        else:
            self._gorevler = []
        silinen = onceki - len(self._gorevler)
        self._kaydet()
        return silinen

    def formatla(self, gorevler: Optional[List[Dict]] = None) -> str:
        """Görevleri okunabilir metin formatına çevirir."""
        gorevler = gorevler or self._gorevler
        if not gorevler:
            return "📋 Görev listesi boş."

        durum_emoji = {
            self.DURUM_BEKLIYOR: "⏳",
            self.DURUM_DEVAM: "🔄",
            self.DURUM_TAMAM: "✅",
            self.DURUM_IPTAL: "❌",
        }

        satirlar = []
        for g in gorevler:
            emoji = durum_emoji.get(g["durum"], "❓")
            oncelik = "🔴" if g.get("oncelik", 0) >= 2 else "🟡" if g.get("oncelik", 0) == 1 else ""
            etiketler = " ".join(f"#{e}" for e in g.get("etiketler", []))
            satir = f"{emoji} {oncelik} [{g['id']}] {g['icerik']}"
            if etiketler:
                satir += f" {etiketler}"
            satirlar.append(satir)

        ist = self.istatistik()
        baslik = f"📋 Görevler ({ist['toplam']} toplam: ⏳{ist['bekliyor']} 🔄{ist['devam']} ✅{ist['tamam']} ❌{ist['iptal']})\n"

        return baslik + "\n".join(satirlar)


# ── Motor Entegrasyonu ───────────────────────────────────────────────────────

_mgr = None

def _get_mgr() -> TodoManager:
    global _mgr
    if _mgr is None:
        _mgr = TodoManager()
    return _mgr


def run(islem: str = "listele", icerik: str = "", gorev_id: str = "",
        durum: str = "", oncelik: int = 0, etiketler: str = "") -> str:
    """
    Motor entegrasyonu için run fonksiyonu.

    islem: ekle/tamamla/baslat/iptal/sil/listele/istatistik/temizle
    """
    mgr = _get_mgr()

    if islem == "ekle":
        if not icerik:
            return "[Hata]: icerik parametresi gerekli."
        etk = [e.strip() for e in etiketler.split(",") if e.strip()] if etiketler else []
        g = mgr.ekle(icerik, oncelik=oncelik, etiketler=etk)
        return f"✅ Görev eklendi: [{g['id']}] {g['icerik']}"

    elif islem == "tamamla":
        if not gorev_id:
            return "[Hata]: gorev_id gerekli."
        g = mgr.tamamla(gorev_id)
        return f"✅ Görev tamamlandı: {g['icerik']}" if g else f"[Hata]: Görev bulunamadı: {gorev_id}"

    elif islem == "baslat":
        if not gorev_id:
            return "[Hata]: gorev_id gerekli."
        g = mgr.baslat(gorev_id)
        return f"🔄 Görev başlatıldı: {g['icerik']}" if g else f"[Hata]: Görev bulunamadı: {gorev_id}"

    elif islem == "iptal":
        if not gorev_id:
            return "[Hata]: gorev_id gerekli."
        g = mgr.iptal(gorev_id)
        return f"❌ Görev iptal edildi: {g['icerik']}" if g else f"[Hata]: Görev bulunamadı: {gorev_id}"

    elif islem == "sil":
        if not gorev_id:
            return "[Hata]: gorev_id gerekli."
        mgr.sil(gorev_id)
        return f"🗑️ Görev silindi: {gorev_id}"

    elif islem == "istatistik":
        ist = mgr.istatistik()
        return f"📊 Toplam: {ist['toplam']} | ⏳ Bekliyor: {ist['bekliyor']} | 🔄 Devam: {ist['devam']} | ✅ Tamam: {ist['tamam']} | ❌ İptal: {ist['iptal']}"

    elif islem == "temizle":
        silinen = mgr.temizle()
        return f"🧹 {silinen} tamamlanan/iptal görev temizlendi."

    else:  # listele
        durum_f = durum if durum else None
        gorevler = mgr.listele(durum=durum_f)
        return mgr.formatla(gorevler)


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Kullanım: python todo_tool.py <islem> [parametreler]")
        print("İşlemler: ekle, tamamla, baslat, iptal, sil, listele, istatistik, temizle")
        sys.exit(1)

    islem = sys.argv[1]
    icerik = sys.argv[2] if len(sys.argv) > 2 else ""
    print(run(islem=islem, icerik=icerik))
