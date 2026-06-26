# -*- coding: utf-8 -*-
"""cikti_dogrulayici.py — LLM çıktısını doğrula, bozuk/tekrarlayan yanıtları yakala.

Tespit edilen sorunlar:
1. Tekrarlayan karakter/kelime (因为, because, bilmiyorum)
2. Anlamsız kısa yanıt (< 10 karakter)
3. Konu dışı yanıt (alerji sorusuna fiyat cevabı vb.)
4. Aşırı uzun tekrar blokları
"""

import re
from collections import Counter

try:
    from reymen.core.logging_config import get_logger
    log = get_logger("cikti_dogrulayici")
except Exception:
    import logging
    log = logging.getLogger("cikti_dogrulayici")


class CiktiDogrulayici:
    """LLM çıktısını doğrula."""

    # Minimum kabul edilebilir yanıt uzunluğu
    MIN_YANIT = 10

    # Tekrar eşiği: aynı kelime/blok bu kadar tekrar ediyorsa bozuk
    TEKRAR_ESIGI = 10

    # Maksimum tekrar bloğu uzunluğu (karakter)
    MAX_TEKRAR_BLOK = 200

    def dogrula(self, yanit: str, hedef: str = "") -> dict:
        """
        Yanıtı doğrula.

        Returns:
            {
                "gecerli": bool,
                "sorun": str veya None,
                "duzeltilmis": str veya None (düzeltilmiş yanıt)
            }
        """
        if not yanit or not yanit.strip():
            return {"gecerli": False, "sorun": "Boş yanıt", "duzeltilmis": None}

        yanit = yanit.strip()

        # 1. Çok kısa yanıt
        if len(yanit) < self.MIN_YANIT:
            return {"gecerli": False, "sorun": f"Çok kısa ({len(yanit)} karakter)", "duzeltilmis": None}

        # 2. Tekrarlayan karakter tespiti
        tekrar_sorun = self._tekrar_kontrol(yanit)
        if tekrar_sorun:
            return {"gecerli": False, "sorun": tekrar_sorun, "duzeltilmis": self._tekrari_temizle(yanit)}

        # 3. Anlamsız yanıt kontrolü (çok fazla yabancı karakter)
        anlamsiz_sorun = self._anlamsiz_kontrol(yanit)
        if anlamsiz_sorun:
            return {"gecerli": False, "sorun": anlamsiz_sorun, "duzeltilmis": None}

        return {"gecerli": True, "sorun": None, "duzeltilmis": None}

    def _tekrar_kontrol(self, yanit: str) -> str:
        """Tekrarlayan blokları tespit et."""
        # Aynı kelime/cümle çok tekrar ediyor mu?
        kelimeler = yanit.split()
        if len(kelimeler) > 20:
            sayac = Counter(kelimeler)
            for kelime, adet in sayac.most_common(5):
                if adet > self.TEKRAR_ESIGI and adet / len(kelimeler) > 0.3:
                    return f"Tekrar: '{kelime}' {adet} kez tekrar ediyor ({adet/len(kelimeler)*100:.0f}%)"

        # Aynı karakter bloğu tekrar ediyor mu? (因为, aaa, vb.)
        for uzunluk in [2, 3, 4, 5, 6]:
            for i in range(len(yanit) - uzunluk * 3):
                blok = yanit[i:i+uzunluk]
                if len(blok.strip()) < 2:
                    continue
                # Bloğun kaç kez tekrar ettiğini say
                tekrar = 1
                pos = i + uzunluk
                while pos + uzunluk <= len(yanit) and yanit[pos:pos+uzunluk] == blok:
                    tekrar += 1
                    pos += uzunluk
                if tekrar >= self.TEKRAR_ESIGI:
                    return f"Tekrar bloğu: '{blok}' {tekrar} kez tekrar ediyor"

        # Toplam karakterlerin %30'undan fazlası aynı karakter mi?
        if len(yanit) > 50:
            sayac = Counter(yanit)
            for char, adet in sayac.most_common(3):
                if adet / len(yanit) > 0.3 and char.strip():
                    return f"Tekrar karakter: '{char}' {adet} kez ({adet/len(yanit)*100:.0f}%)"

        return ""

    def _anlamsiz_kontrol(self, yanit: str) -> str:
        """Anlamsız yanıt tespit et."""
        # Çok fazla farklı dil karakteri karışımı
        turkce_karakter = len(re.findall(r'[a-zA-ZçğıöşüÇĞİÖŞÜ0-9\s.,;:!?()\[\]{}\-+*/=<>@#$%^&|~`\'"]', yanit))
        toplam = len(yanit.replace(' ', '').replace('\n', ''))
        if toplam > 0 and turkce_karakter / toplam < 0.5:
            return f"Anlamsız karışım: %{turkce_karakter/toplam*100:.0f} normal karakter"

        return ""

    def _tekrari_temizle(self, yanit: str) -> str:
        """Tekrarlayan blokları temizle, anlamlı kısmı koru."""
        # İlk tekrar bloğundan önceki kısmı al
        for uzunluk in [2, 3, 4, 5, 6]:
            for i in range(len(yanit) - uzunluk * 3):
                blok = yanit[i:i+uzunluk]
                if len(blok.strip()) < 2:
                    continue
                tekrar = 1
                pos = i + uzunluk
                while pos + uzunluk <= len(yanit) and yanit[pos:pos+uzunluk] == blok:
                    tekrar += 1
                    pos += uzunluk
                if tekrar >= self.TEKRAR_ESIGI:
                    # Tekrar bloğundan önceki kısmı döndür
                    on_kisim = yanit[:i].strip()
                    if len(on_kisim) > 20:
                        return on_kisim
                    return ""

        return ""


# Global instance
_dogrulayici = None

def dogrula(yanit: str, hedef: str = "") -> dict:
    """Global doğrulayıcı ile yanıtı doğrula."""
    global _dogrulayici
    if _dogrulayici is None:
        _dogrulayici = CiktiDogrulayici()
    return _dogrulayici.dogrula(yanit, hedef)
