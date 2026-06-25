# -*- coding: utf-8 -*-
"""
auto_web_search.py — Otomatik web arama tetikleyicisi.

ReYMeN'in sorulan sorulara otomatik web araması yapmasını sağlar.
Hafızada yoksa veya güncel bilgi gerekiyorsa web'e gider.

5 Tetikleyici:
1. Hafıza boş → anında web
2. Güven düşük (< 0.5) → web
3. Görev başarısız (2. hata) → web
4. Geçerlilik süresi geçmiş → arka planda web
5. "bugün", "güncel", "şu an" gibi güncel bilgi kelimeleri → web

Kullanım:
    from reymen.cereyan.auto_web_search import AutoWebSearch
    aws = AutoWebSearch()
    if aws.web_arasi_mi("altın ons fiyatı"):
        sonuc = aws.ara("altın ons fiyatı")
"""

import re
import time
from typing import Optional, Dict, List, Tuple
from datetime import datetime

try:
    from reymen.sistem.reymen_logging import get_logger
    log = get_logger("auto_web_search")
except Exception:
    import logging
    log = logging.getLogger("auto_web_search")


class AutoWebSearch:
    """Otomatik web arama tetikleyicisi."""

    # Güncel bilgi tetikleyici kelimeler
    GUNCEL_KELIMELER = [
        "bugün", "bugun", "şu an", "su an", "şimdi", "simdi",
        "güncel", "guncel", "son", "latest", "today", "now",
        "fiyat", "fiyatı", "fiyati", "kur", "dolar", "euro",
        "hava", "durumu", "haber", "haberler", "news",
        "ne kadar", "kaç tl", "kac tl", "kaç dolar",
        "tarihte bugün", "tarihte bu gün",
        "maç", "mac", "skor", "sonuç", "sonuc",
        "döviz", "doviz", "borsa", "bist", "bitcoin",
        "altın", "altin", "gümüş", "gumus",
        "deprem", "earthquake", "weather",
    ]

    # Soru kelimeleri (bilgi gerektiren)
    SORU_KELIMELERI = [
        "nedir", "ne demek", "kimdir", "nerede", "ne zaman",
        "nasıl", "nasil", "niçin", "nicin", "neden",
        "kaç", "kac", "hangi", "kim", "what", "who", "where",
        "when", "how", "why", "which",
    ]

    # Web araması GEREKTİRMEYEN konular
    WEB_GEREKMEYEN = [
        "merhaba", "selam", "nasılsın", "teşekkür", "teşekkürler",
        "tamam", "evet", "hayır", "olur", "peki",
        "python", "kod", "program", "script", "dosya",
        "hafıza", "bellek", "ayar", "config",
    ]

    def __init__(self, once_hafiza=None):
        """
        Args:
            once_hafiza: OnceHafiza instance'ı (hafıza kontrolü için)
        """
        self._hafiza = once_hafiza
        self._son_aramalar: Dict[str, float] = {}  # sorgu → timestamp
        self._arama_gecmisi: List[Dict] = []

    def web_arasi_mi(self, mesaj: str, guven_skoru: float = 0.5) -> Tuple[bool, str]:
        """
        Mesaj için web araması gerekip gerekmediğini kontrol eder.

        Args:
            mesaj: Kullanıcı mesajı
            guven_skoru: Hafıza güven skoru (0-1)

        Returns:
            (web_gerekli, sebep)
        """
        if not mesaj or not mesaj.strip():
            return False, "Boş mesaj"

        mesaj_lower = mesaj.lower().strip()

        # 1. Web gerektirmeyen konular
        for kelime in self.WEB_GEREKMEYEN:
            if mesaj_lower == kelime or mesaj_lower.startswith(kelime + " "):
                return False, f"Web gerektirmeyen konu: {kelime}"

        # 2. Güncel bilgi tetikleyici
        for kelime in self.GUNCEL_KELIMELER:
            if kelime in mesaj_lower:
                return True, f"Güncel bilgi tetikleyici: {kelime}"

        # 3. Soru kelimeleri + bilgi gerektiren konu
        soru_var = any(k in mesaj_lower for k in self.SORU_KELIMELERI)
        if soru_var and len(mesaj) > 15:  # Kısa sorular web gerektirmez
            # Hafızada var mı kontrol et
            if self._hafiza:
                try:
                    sonuc = self._hafiza.ara(mesaj_lower)
                    if sonuc and len(sonuc) > 0:
                        return False, "Hafızada mevcut"
                except Exception:
                    pass
            return True, "Soru + hafızada yok"

        # 4. Güven skoru düşük
        if guven_skoru < 0.3:
            return True, f"Düşük güven: {guven_skoru:.2f}"

        # 5. Son arama çok eskiyse (24 saatten fazla)
        if mesaj_lower in self._son_aramalar:
            son_arama = self._son_aramalar[mesaj_lower]
            if time.time() - son_arama > 86400:  # 24 saat
                return True, "Son arama 24 saatten eski"

        return False, "Web gerekmez"

    def ara(self, sorgu: str, limit: int = 3) -> Dict:
        """
        Web araması yapar.

        Args:
            sorgu: Arama sorgusu
            limit: Max sonuç

        Returns:
            {"sonuclar": [...], "kaynak": "...", "error": None}
        """
        try:
            from reymen.arac.web_search_tool import web_search
            sonuc = web_search(sorgu, limit=limit)

            # Arama geçmişine ekle
            self._son_aramalar[sorgu.lower()] = time.time()
            self._arama_gecmisi.append({
                "sorgu": sorgu,
                "zaman": datetime.now().isoformat(),
                "kaynak": sonuc.get("kaynak", ""),
                "sonuc_sayisi": len(sonuc.get("results", [])),
            })

            return sonuc

        except Exception as e:
            log.error(f"Web arama hatası: {e}")
            return {"sonuclar": [], "kaynak": "", "error": str(e)}

    def otomatik_cevap_uret(self, mesaj: str, guven_skoru: float = 0.5) -> Optional[str]:
        """
        Eğer web araması gerekiyorsa, otomatik cevap üretir.

        Args:
            mesaj: Kullanıcı mesajı
            guven_skoru: Hafıza güven skoru

        Returns:
            Cevap metni veya None (web gerekmez)
        """
        web_gerekli, sebep = self.web_arasi_mi(mesaj, guven_skoru)

        if not web_gerekli:
            return None

        log.info(f"Otomatik web araması: {mesaj} (sebep: {sebep})")

        # Web araması yap
        sonuc = self.ara(mesaj)

        if sonuc.get("error"):
            return None

        if not sonuc.get("results"):
            return None

        # Sonuçları formatla
        from reymen.arac.web_search_tool import web_search_ve_ozetle
        return web_search_ve_ozetle(mesaj, limit=3)

    def istatistik(self) -> Dict:
        """Arama istatistikleri."""
        return {
            "toplam_arama": len(self._arama_gecmisi),
            "benzersiz_sorgu": len(self._son_aramalar),
            "son_arama": self._arama_gecmisi[-1] if self._arama_gecmisi else None,
        }


# ── Global Instance ──────────────────────────────────────────────────────────

_auto_search = None

def get_auto_search() -> AutoWebSearch:
    """Global auto search instance'ı döner."""
    global _auto_search
    if _auto_search is None:
        _auto_search = AutoWebSearch()
    return _auto_search


# ── Motor Entegrasyonu ───────────────────────────────────────────────────────

def run(mesaj: str = "", islem: str = "kontrol") -> str:
    """Motor entegrasyonu."""
    aws = get_auto_search()

    if islem == "kontrol":
        if not mesaj:
            return "[Hata]: mesaj gerekli."
        web_gerekli, sebep = aws.web_arasi_mi(mesaj)
        return f"{'🔍 Web gerekli' if web_gerekli else '✅ Web gerekmez'}: {sebep}"

    elif islem == "ara":
        if not mesaj:
            return "[Hata]: mesaj gerekli."
        from reymen.arac.web_search_tool import web_search_ve_ozetle
        return web_search_ve_ozetle(mesaj)

    elif islem == "otomatik":
        if not mesaj:
            return "[Hata]: mesaj gerekli."
        cevap = aws.otomatik_cevap_uret(mesaj)
        return cevap if cevap else "Web araması gerekmedi."

    elif islem == "istatistik":
        ist = aws.istatistik()
        return f"📊 Toplam: {ist['toplam_arama']} arama, {ist['benzersiz_sorgu']} benzersiz sorgu"

    return f"[Hata]: Bilinmeyen islem: {islem}"


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Kullanım: python auto_web_search.py <mesaj>")
        sys.exit(1)

    mesaj = " ".join(sys.argv[1:])
    aws = AutoWebSearch()
    web_gerekli, sebep = aws.web_arasi_mi(mesaj)
    print(f"Web gerekli: {web_gerekli} ({sebep})")

    if web_gerekli:
        from reymen.arac.web_search_tool import web_search_ve_ozetle
        print(web_search_ve_ozetle(mesaj))
