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
    from reymen.core.logging_config import get_logger
    log = get_logger("auto_web_search")
except Exception:
    import logging
    log = logging.getLogger("auto_web_search")


class AutoWebSearch:
    """Otomatik web arama tetikleyicisi."""
    _CACHE_TTL = 300  # 5 dakika cache TTL

    # Güncel bilgi tetikleyici kelimeler
    GUNCEL_KELIMELER = [
        # Zaman belirteçleri
        "bugün", "bugun", "şu an", "su an", "şimdi", "simdi",
        "güncel", "guncel", "son", "latest", "today", "now",
        # Finans
        "fiyat", "fiyatı", "fiyati", "kur", "dolar", "euro",
        "hava", "durumu",
        "ne kadar", "kaç tl", "kac tl", "kaç dolar",
        "döviz", "doviz", "borsa", "bist", "bitcoin",
        "altın", "altin", "gümüş", "gumus",
        "ons", "değer", "değeri", "degeri", "gram",
        "çeyrek", "ceyrek", "yarım", "yarim",
        "cumhuriyet", "ziynet", "canlı", "canli",
        "endeks", "faiz", "enflasyon", "hisse", "para",
        "kripto", "coin", "eth", "bnb",
        # Spor
        "spor", "maç", "mac", "skor", "futbol", "basketbol",
        "galatasaray", "fenerbahçe", "beşiktaş", "trabzon",
        "lig", "transfer", "şampiyon", "sampiyon", "nba",
        # Siyaset
        "siyaset", "seçim", "secim", "cumhurbaşkanı", "cumhurbaskani",
        "parti", "meclis", "bakan", "muhalefet",
        # Ekonomi
        "ekonomi", "işsizlik", "issizlik", "büyüme", "buyume",
        "merkez bankası", "asgari ücret", "asgari ucret",
        "maaş", "maas", "vergi", "bütçe", "butce",
        "emtia", "petrol",
        # Dünya
        "dünya", "dunya", "uluslararası", "uluslararasi",
        "küresel", "kuresel", "savaş", "savas",
        "abd", "rusya", "çin", "cin", "avrupa",
        "ukrayna", "filistin", "israil",
        # Teknoloji / Yapay Zeka
        "yapay zeka", "teknoloji", "yazılım", "yazilim",
        "siber", "güvenlik", "guvenlik",
        "chatgpt", "openai", "ai", "robot",
        # Haber / Genel
        "haber", "haberler", "news",
        "gündem", "gundem", "son dakika", "flaş", "flash",
        # Sağlık
        "sağlık", "saglik", "hastalık", "hastalik",
        "ilaç", "ilac", "aşı", "asi", "virüs", "virus",
        # Bilim
        "bilim", "uzay", "nasa", "araştırma", "arastirma",
        "iklim", "çevre", "cevre",
        # Kültür / Sanat
        "kültür", "kultur", "sanat", "sinema", "film",
        "kitap", "müzik", "muzik", "tarih",
        # Tarih / Bugün
        "tarihte bugün", "tarihte bu gün",
        # Hava / Doğa
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
        self._sonuc_cache: Dict[str, tuple] = {}  # sorgu → (sonuc, timestamp)
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
        Web araması yapar — cache TTL ile (5 dk).

        Args:
            sorgu: Arama sorgusu
            limit: Max sonuç

        Returns:
            {"sonuclar": [...], "kaynak": "...", "error": None}
        """
        # Cache kontrol: 5 dakika içinde aynı sorgu varsa kullan
        cache_key = sorgu.lower().strip()
        if cache_key in self._sonuc_cache:
            sonuc, cache_zamani = self._sonuc_cache[cache_key]
            if time.time() - cache_zamani < self._CACHE_TTL:
                log.info(f"Cache hit (TTL {self._CACHE_TTL}s): {sorgu[:50]}")
                return sonuc

        try:
            from reymen.arac.haber_kaynaklari import kaynakli_web_ara
            sonuc_metin = kaynakli_web_ara(sorgu, limit=limit)
            sonuc = {"sonuclar": [{"baslik": sonuc_metin[:80], "ozet": sonuc_metin}],
                     "kaynak": "kaynakli_web_ara", "error": None}

            # Cache'e kaydet
            self._sonuc_cache[cache_key] = (sonuc, time.time())

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
            log.warning(f"kaynakli_web_ara basarisiz, fallback: {e}")
            try:
                from reymen.arac.web_search_tool import web_search
                sonuc = web_search(sorgu, limit=limit)

                # Cache'e kaydet
                self._sonuc_cache[cache_key] = (sonuc, time.time())

                # Arama geçmişine ekle
                self._son_aramalar[sorgu.lower()] = time.time()
                self._arama_gecmisi.append({
                    "sorgu": sorgu,
                    "zaman": datetime.now().isoformat(),
                    "kaynak": sonuc.get("kaynak", ""),
                    "sonuc_sayisi": len(sonuc.get("results", [])),
                })

                return sonuc
            except Exception as e2:
                log.error(f"Web arama hatasi (fallback da basarisiz): {e2}")
                return {"sonuclar": [], "kaynak": "", "error": str(e2)}

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
        from reymen.arac.haber_kaynaklari import kaynakli_web_ara
        return kaynakli_web_ara(mesaj, limit=3)

    def verifiye_et(self, sorgu: str, web_sonucu: str) -> Tuple[bool, str, str]:
        """
        Web arama sonucunun güncel olup olmadığını doğrular.

        Kontroller:
        1. Bugünün tarihi/yılı sonuçta geçiyor mu?
        2. "güncel", "canlı", "anlık", "bugün" gibi tazelik ifadeleri var mı?
        3. Eski tarih bilgisi var mı? (geçen yıl vs.)
        4. Sonuç çok mu kısa/boş?

        Args:
            sorgu: Orijinal arama sorgusu
            web_sonucu: Web aramasından dönen metin

        Returns:
            (guncel_mi, durum_aciklamasi, duzeltilmis_sonuc)
        """
        if not web_sonucu or len(web_sonucu.strip()) < 20:
            return False, "Sonuç çok kısa veya boş", web_sonucu

        simdi = datetime.now()
        bugunun_yili = simdi.year
        bugunun_tarihi = simdi.strftime("%d.%m.%Y")
        bugunun_ayi = simdi.strftime("%B").lower()  # "january", "february"...

        sonuc_lower = web_sonucu.lower()
        puan = 0
        kontroller = []

        # ── Kontrol 1: Bugünün yılı geçiyor mu? ──
        if str(bugunun_yili) in web_sonucu:
            puan += 30
            kontroller.append(f"✅ Yıl {bugunun_yili} mevcut")
        elif str(bugunun_yili - 1) in web_sonucu and str(bugunun_yili) not in web_sonucu:
            puan -= 20
            kontroller.append(f"⚠️ Sadece {bugunun_yili-1} yılı geçiyor (eski?)")

        # ── Kontrol 2: Tazelik ifadeleri ──
        tazelik_kelimeleri = [
            "canlı", "anlık", "bugün", "güncel", "şu an",
            "live", "real-time", "realtime", "latest", "today",
            "son fiyat", "güncel fiyat", "anlık fiyat",
            simdi.strftime("%Y-%m"),  # "2026-06" gibi
        ]
        tazelik_bulunan = [k for k in tazelik_kelimeleri if k in sonuc_lower]
        if tazelik_bulunan:
            puan += 25
            kontroller.append(f"✅ Tazelik ifadeleri: {', '.join(tazelik_bulunan[:3])}")

        # ── Kontrol 3: Bugünün tarihi var mı? ──
        if bugunun_tarihi in web_sonucu:
            puan += 30
            kontroller.append(f"✅ Bugün tarihi ({bugunun_tarihi}) mevcut")
        # Farklı formatlar
        for fmt in ["%Y-%m-%d", "%d/%m/%Y", "%d %B %Y"]:
            if simdi.strftime(fmt).lower() in sonuc_lower:
                puan += 20
                kontroller.append(f"✅ Tarih formatı ({fmt}) bulundu")
                break

        # ── Kontrol 4: Sayısal veri var mı? (fiyat, kur vs.) ──
        sayilar = re.findall(r'[\d.,]+\s*(?:TL|USD|EUR|₺|\$|€)', web_sonucu)
        if sayilar:
            puan += 15
            kontroller.append(f"✅ Sayısal veri: {sayilar[0]}")

        # ── Kontrol 5: Eski tarih kontrolü ──
        eski_yillar = [str(y) for y in range(2020, bugunun_yili - 1)]
        eski_bulunan = [y for y in eski_yillar if y in web_sonucu]
        if eski_bulunan and str(bugunun_yili) not in web_sonucu:
            puan -= 15
            kontroller.append(f"⚠️ Eski yıllar: {', '.join(eski_bulunan[:3])}")

        # ── Kontrol 6: "2024", "2023" gibi yakın ama eski yıllar ──
        yakin_eski = [str(y) for y in range(bugunun_yili - 2, bugunun_yili)]
        yakin_bulunan = [y for y in yakin_eski if y in web_sonucu]
        if yakin_bulunan and str(bugunun_yili) not in web_sonucu:
            puan -= 10
            kontroller.append(f"⚠️ Yakın eski yıl: {', '.join(yakin_bulunan)}")

        # ── Karar ──
        guncel_mi = puan >= 30
        if guncel_mi:
            durum = f"✅ DOĞRULANDI (puan: {puan})"
        elif puan >= 15:
            durum = f"⚠️ ŞÜPHELİ (puan: {puan}) — tekrar deneniyor"
            # Farklı sorguyla tekrar dene
            yeniden_sonuc = self._yeniden_ara(sorgu)
            if yeniden_sonuc:
                return True, f"✅ Yeniden doğrulandı (puan: {puan}→yeniden)", yeniden_sonuc
        else:
            durum = f"❌ GÜNCEL DEĞİL (puan: {puan}) — farklı kaynak deneniyor"
            yeniden_sonuc = self._yeniden_ara(sorgu)
            if yeniden_sonuc:
                return True, f"✅ Farklı kaynak doğrulandı (puan: {puan}→yeniden)", yeniden_sonuc

        detay = " | ".join(kontroller)
        log.info(f"Doğrulama: {durum} | {detay}")
        return guncel_mi, f"{durum}\n  Kontroller: {detay}", web_sonucu

    def _yeniden_ara(self, sorgu: str) -> Optional[str]:
        """Farklı sorguyla tekrar arar."""
        try:
            from reymen.arac.haber_kaynaklari import kaynakli_web_ara
            # Sorguyu zenginleştir
            zengin_sorgular = [
                f"{sorgu} 2026",
                f"{sorgu} güncel",
                f"bugün {sorgu}",
            ]
            for z_sorgu in zengin_sorgular:
                try:
                    sonuc = kaynakli_web_ara(z_sorgu, limit=3)
                    if sonuc and len(sonuc) > 50:
                        # Bu sonucu da doğrula
                        guncel, durum, _ = self.verifiye_et(sorgu, sonuc)
                        if guncel:
                            return sonuc
                except Exception:
                    continue
        except Exception as e:
            log.warning(f"Yeniden arama hatası: {e}")
        return None

    def dogrulanmis_ara(self, sorgu: str, limit: int = 3) -> Tuple[str, bool, str]:
        """
        Web araması yapar + sonucu doğrular — cache TTL ile.

        Args:
            sorgu: Arama sorgusu
            limit: Max sonuç

        Returns:
            (sonuc_metni, guncel_mi, dogrulama_detayi)
        """
        # Cache kontrol: 5 dakika içinde aynı sorgu varsa kullan
        cache_key = f"dogr:{sorgu.lower().strip()}"
        if cache_key in self._sonuc_cache:
            sonuc, cache_zamani = self._sonuc_cache[cache_key]
            if time.time() - cache_zamani < self._CACHE_TTL:
                log.info(f"Cache hit (dogrulanmis_ara): {sorgu[:50]}")
                return sonuc

        # 1. İlk arama — kaynak öncelikli
        from reymen.arac.haber_kaynaklari import kaynakli_web_ara
        sonuc = kaynakli_web_ara(sorgu, limit=limit)

        if not sonuc or "Hata" in sonuc:
            return sonuc or "Arama yapılamadı", False, "Arama hatası"

        # 2. Doğrula
        guncel_mi, durum, duzeltilmis = self.verifiye_et(sorgu, sonuc)

        # 3. Sonucu formatla
        if guncel_mi:
            baslik = f"🔍 Doğrulanmış sonuç ({durum.split('(')[0].strip()}):\n\n"
        else:
            baslik = f"⚠️ Doğrulanamadı — dikkatli kullanın:\n\n"

        son_formatli = baslik + duzeltilmis

        # Cache'e kaydet
        self._sonuc_cache[cache_key] = (son_formatli, guncel_mi, durum), time.time()

        return son_formatli, guncel_mi, durum

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
        from reymen.arac.haber_kaynaklari import kaynakli_web_ara
        return kaynakli_web_ara(mesaj)

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
        from reymen.arac.haber_kaynaklari import kaynakli_web_ara
        print(kaynakli_web_ara(mesaj))
