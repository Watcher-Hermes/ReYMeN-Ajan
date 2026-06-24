# -*- coding: utf-8 -*-
"""iteration_budget.py — ReYMeN thread-safe iterasyon butcesi.

Hermes Agent IterationBudget pattern'i ile ayni.
Her ajan (ana veya alt) kendi butcesine sahiptir.
Thread-safe consume/refund sayaci.

Kullanim:
    budget = IterationBudget(max_total=90)
    if budget.consume():
        # islem yap
        pass
    budget.refund()  # execute_code gibi durumlarda iade
"""

import threading


class IterationBudget:
    """Thread-safe iterasyon sayaci.

    Her ajan kendi butcesine sahip olur.
    Ana ajan: max_iterations (varsayilan 90)
    Alt ajan: delegation.max_iterations (varsayilan 50)

    Geriye uyumluluk: max_tur parametresi de calisir (max_total ile ayni).
    """

    def __init__(self, max_total: int = None, max_tur: int = None, max_hata: int = None):
        # max_tur eski API uyumlulugu
        if max_total is None and max_tur is not None:
            max_total = max_tur
        if max_total is None:
            max_total = 90
        self.max_total = max_total
        self.max_hata = max_hata  # circuit breaker: None = sınırsız
        self._used = 0
        self._hata_sayisi = 0
        self._lock = threading.Lock()

    def consume(self) -> bool:
        """Bir iterasyon harca. True: izin var, False: butce doldu."""
        with self._lock:
            if self._used >= self.max_total:
                return False
            self._used += 1
            return True

    def refund(self) -> None:
        """Bir iterasyonu iade et (ornek: execute_code icin)."""
        with self._lock:
            if self._used > 0:
                self._used -= 1

    @property
    def used(self) -> int:
        with self._lock:
            return self._used

    @property
    def remaining(self) -> int:
        with self._lock:
            return max(0, self.max_total - self._used)

    def reset(self) -> None:
        """Butceyi sifirla."""
        with self._lock:
            self._used = 0

    def analiz_et(self, hedef: str) -> dict:
        """Hedefin karmasikligini analiz et.

        Gercekci puanlama:
        - Basit sohbet/selam → 1
        - Tek islemli gorev → 2
        - 2-3 adimli gorev → 3
        - Cok adimli gorev → 4
        - Coklu araclar/karmaşik → 5
        """
        hedef_lower = hedef.lower()
        kelime_sayisi = len(hedef.split())
        satir_sayisi = len(hedef.splitlines())

        # Selam/sohbet kontrolu
        selam_kelimeler = {"selam", "merhaba", "hey", "hi", "hello", "sa", "nasılsın", "naber", "nbr"}
        if hedef_lower.strip().rstrip("!?.,") in selam_kelimeler:
            return {"karmasiklik": 1, "ipuclari": ["selam"], "aciklama": "Basit selam"}

        # Kisa sorular
        if kelime_sayisi < 5 and satir_sayisi == 1:
            return {"karmasiklik": 1, "ipuclari": ["kisa_soru"], "aciklama": "Kisa soru"}

        # Uzun mesaj / cok satirli → otomatik olarak karmasik
        if satir_sayisi > 10 or kelime_sayisi > 100:
            return {"karmasiklik": 4, "ipuclari": ["uzun_mesaj"], "aciklama": "Uzun mesaj — parcalanmali"}

        # Ipucu bazli puanlama
        ipuclari = []
        puan = 1

        # Her ek ipucu puani artirir
        kontroller = {
            "kod": ["kod", "python", "script", "calistir", "debug", "hata"],
            "dosya": ["dosya", "yaz", "oku", "kaydet", "olustur", "sil", "klasör"],
            "web": ["web", "ara", "internet", "indir", "site"],
            "sistem": ["terminal", "komut", "powershell", "sistem", "kontrol"],
            "analiz": ["analiz", "karsilastir", "incele", "rapor", "özet"],
            "kurulum": ["kur", "yukle", "install", "setup", "docker"],
        }

        for ipucu_adi, kelimeler in kontroller.items():
            if any(k in hedef_lower for k in kelimeler):
                ipuclari.append(ipucu_adi)
                puan += 1

        # Karmaşıklık 1-5 arası
        puan = min(5, max(1, puan))

        return {
            "karmasiklik": puan,
            "ipuclari": ipuclari,
            "kelime_sayisi": kelime_sayisi,
            "satir_sayisi": satir_sayisi,
            "aciklama": f"{len(ipuclari)} ipucu bulundu"
        }

    def __repr__(self) -> str:
        return f"IterationBudget({self.used}/{self.max_total})"

    # ══════════════════════════════════════════════════════════════════
    # GERIYE UYUMLULUK — eski API
    # ══════════════════════════════════════════════════════════════════

    @property
    def tur(self) -> int:
        """Eski API: tur sayisi = used ile ayni."""
        return self._used

    @property
    def max_tur(self) -> int:
        """Eski API alias: max_total ile ayni."""
        return self.max_total

    def tur_basla(self) -> None:
        """Eski API: consume ile ayni."""
        self.consume()

    def tur_bitir(self, basarili: bool = True, sonuc: str = "",
                  hata_tipi: str = "") -> bool:
        """Eski API: tur sonu kontrolu. True = devam et, False = dur."""
        if not basarili:
            with self._lock:
                self._hata_sayisi += 1
        return self.devam_etmeli_mi()

    def devam_etmeli_mi(self) -> bool:
        """Kalan bütçe var mı VE hata sınırı aşılmadı mı?"""
        with self._lock:
            if self.max_hata is not None and self._hata_sayisi >= self.max_hata:
                return False
            return self._used < self.max_total

    def durum_raporu(self) -> str:
        """Eski API: butce durumunu okunabilir string olarak dondur."""
        return f"Tur {self._used}/{self.max_total} (kalan: {self.remaining})"

    def gorev_tamamla(self) -> None:
        """Eski API: reset ile ayni."""
        self.reset()

    # Takma adlar
    gorev_tamami = gorev_tamamla
