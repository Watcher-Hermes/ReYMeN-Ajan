# -*- coding: utf-8 -*-
"""
output_validator.py — LLM çıktı validasyonu.

Guardrails'ten farkı:
  - guardrails.py sadece UYARI üretir, çıktıyı değiştirmez
  - output_validator.py kurallara göre DOĞRULAR, geçemezse ENGINEING yapar

İki validasyon modu:
  1. Kurallı (rules): regex/kural seti ile hızlı geç/kal
  2. Yapısal (structural): JSON şema, kod bloğu sayısı, uzunluk vb.

Kullanım:
    from output_validator import OutputValidator

    v = OutputValidator()
    ok, mesaj = v.dogrula("ls -la", "Cikti metni burada...")
    if not ok:
        cikti = v.engine("ls -la", "Cikti metni burada...")
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from typing import Optional

logger = logging.getLogger(__name__)


# ── Regex kalıpları ──────────────────────────────────────────────────────────

# Hassas bilgi kaçağı: çıktıda görünmemesi gereken pattern'ler
_HASSAS_KALIPLAR: list[str] = [
    r"(?:sk-[A-Za-z0-9]{20,}|sk-[A-Za-z0-9]{32,})",  # OpenAI API key
    r"(?:ghp_|gho_|ghu_|ghs_|ghr_)[A-Za-z0-9]{36,}",  # GitHub token
    r"(?:AKIA[0-9A-Z]{16})",  # AWS access key
    r"(?:-----BEGIN (?:RSA |EC )?PRIVATE KEY-----)",  # Private key
    r"(?:xox[bpras]-[0-9A-Za-z-]{24,})",  # Slack token
    r"(?:eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,})",  # JWT
]

# Çıktıda olmaması gereken hata kalıpları
_HATA_KALIPLARI: list[str] = [
    r"\b(?:hata|error|exception)\s*:?\s*(?:oluştu|meydana|alındı|oldu)",
    r"\b(?:timeout|timed?\s*out)\b",
    r"\b(?:permission\s*denied|access\s*denied|yetki\s*yok)\b",
    r"\b(?:not\s*found|bulunamadı)\b.*\b(?:dosya|file|klasör|directory)\b",
    r"\b(?:connection\s*refused|bağlantı\s*reddedildi)\b",
]

# Boş / anlamsız çıktı kalıpları
_BOS_CIKTI_KALIPLARI: list[str] = [
    r"^\s*$",
    r"^\s*(?:\.|ok|done|tamam|bitti)\s*$",
    r"^\s*(?:\[\s*\]|{}\s*|None\s*|null\s*|undefined)\s*$",
    r"^(?:\s*\n\s*)+$",
]

# Beklenen kod bloğu sayısı alt limiti (0=devre dışı)
_MIN_KOD_BLOGU = 0

# Maksimum çıktı uzunluğu (karakter, 0=devre dışı)
_MAKS_UZUNLUK = 0

# Çıktı minimum karakter sayısı (0=devre dışı)
_MIN_UZUNLUK = 0


@dataclass
class ValidationResult:
    """Tek bir validasyon kuralının sonucu."""
    kural_adi: str
    gecti: bool
    mesaj: str = ""

    def __repr__(self) -> str:
        isaret = "+" if self.gecti else "-"
        return f"[{isaret}] {self.kural_adi}: {self.mesaj}"


@dataclass
class ValidationReport:
    """Tüm validasyon kurallarının toplu raporu."""
    gecti: bool
    sonuclar: list[ValidationResult] = field(default_factory=list)
    hedef: str = ""

    @property
    def basarisizlar(self) -> list[ValidationResult]:
        return [s for s in self.sonuclar if not s.gecti]

    def ozet(self) -> str:
        toplam = len(self.sonuclar)
        gecen = len([s for s in self.sonuclar if s.gecti])
        if self.gecti:
            return f"[+] {gecen}/{toplam} kural gecti"
        return f"[-] {gecen}/{toplam} gecti, {toplam - gecen} basarisiz"

    def __repr__(self) -> str:
        return f"ValidationReport(gecti={self.gecti}, sonuclar={len(self.sonuclar)}, hedef={self.hedef!r})"


class OutputValidator:
    """
    LLM çıktılarını kurallara göre doğrular.

    Özellikler:
      - Hassas bilgi kaçağı tespiti
      - Hata kalıpları taraması
      - Boş/anlamsız çıktı kontrolü
      - Yapısal kontroller (kod bloğu sayısı, uzunluk)
      - Engine (düzelt) fonksiyonu
    """

    def __init__(self, min_kod: int = 0, maks_uzunluk: int = 0, min_uzunluk: int = 0):
        self._hassas_re = [re.compile(p, re.IGNORECASE) for p in _HASSAS_KALIPLAR]
        self._hata_re = [re.compile(p, re.IGNORECASE) for p in _HATA_KALIPLARI]
        self._bos_re = [re.compile(p) for p in _BOS_CIKTI_KALIPLARI]
        self._min_kod = min_kod
        self._maks_uzunluk = maks_uzunluk
        self._min_uzunluk = min_uzunluk

    def dogrula(self, hedef: str, cikti: str) -> ValidationReport:
        """
        Çıktıyı tüm kurallara göre doğrula.

        Args:
            hedef: Yapılması istenen işlem (bağlam için)
            cikti: LLM'den gelen ham çıktı

        Returns:
            ValidationReport: Geçti/Kaldı + her kuralın sonucu
        """
        rapor = ValidationReport(gecti=True, hedef=hedef)

        # 1. Hassas bilgi kaçağı
        self._kontrol_hassas(cikti, rapor)

        # 2. Hata kalıpları
        self._kontrol_hata(cikti, rapor)

        # 3. Boş/anlamsız çıktı
        self._kontrol_bos(cikti, rapor)

        # 4. Uzunluk kontrolü
        self._kontrol_uzunluk(cikti, rapor)

        # 5. Kod bloğu sayısı (eğer hedef kod yazmayı içeriyorsa)
        self._kontrol_kod_bloku(hedef, cikti, rapor)

        # 6. Eski inline uzunluk kontrolü (sıfır karakter)
        if not cikti or len(cikti.strip()) == 0:
            rapor.sonuclar.append(ValidationResult(
                kural_adi="uzunluk",
                gecti=False,
                mesaj="Cikti tamamen bos"
            ))

        # Genel geçti/kaldı
        rapor.gecti = len(rapor.basarisizlar) == 0
        return rapor

    def engine(self, hedef: str, cikti: str) -> str:
        """
        Ciktiyi duzelt (engine): hassas bilgileri maskele,
        bos ciktiysa uyari mesaji ekle, asiri uzun ciktilari kes.

        Bu fonksiyon ciktiyi dogrudan duzeltir, tekrar LLM cagirmaz.
        """
        if not cikti:
            return "[VALIDASYON: Bos cikti -- lutfen islemi tekrar dene]"

        # Hassas bilgileri maskele
        for r in self._hassas_re:
            cikti = r.sub("[REDACTED]", cikti)

        # Maksimum uzunluk siniri
        if self._maks_uzunluk > 0 and len(cikti) > self._maks_uzunluk:
            cikti = cikti[:self._maks_uzunluk] + "\n...[VALIDASYON: Cikti kesildi, maks " + str(self._maks_uzunluk) + " karakter]"

        return cikti

    def _kontrol_hassas(self, cikti: str, rapor: ValidationReport) -> None:
        """Hassas bilgi kaçağı kontrolü."""
        bulunanlar = []
        for r in self._hassas_re:
            m = r.search(cikti)
            if m:
                tip = self._hassas_tip_etiket(r)
                bulunanlar.append(tip)

        if bulunanlar:
            rapor.sonuclar.append(ValidationResult(
                kural_adi="hassas_bilgi",
                gecti=False,
                mesaj=f"Hassas bilgi tespit edildi: {', '.join(set(bulunanlar))}"
            ))
        else:
            rapor.sonuclar.append(ValidationResult(
                kural_adi="hassas_bilgi",
                gecti=True,
                mesaj="Hassas bilgi tespit edilmedi"
            ))

    def _kontrol_hata(self, cikti: str, rapor: ValidationReport) -> None:
        """Hata kalıpları kontrolü."""
        for r in self._hata_re:
            m = r.search(cikti)
            if m:
                rapor.sonuclar.append(ValidationResult(
                    kural_adi="hata_kalibi",
                    gecti=False,
                    mesaj=f"Hata kalıbı tespit edildi: '{m.group()}'"
                ))
                return
        rapor.sonuclar.append(ValidationResult(
            kural_adi="hata_kalibi",
            gecti=True,
            mesaj="Hata kalıbı tespit edilmedi"
        ))

    def _kontrol_bos(self, cikti: str, rapor: ValidationReport) -> None:
        """Bos/anlamsiz cikti kontrolu."""
        for r in self._bos_re:
            if r.match(cikti):
                rapor.sonuclar.append(ValidationResult(
                    kural_adi="bos_cikti",
                    gecti=False,
                    mesaj="Cikti bos veya anlamsiz"
                ))
                return
        rapor.sonuclar.append(ValidationResult(
            kural_adi="bos_cikti",
            gecti=True,
            mesaj="Cikti anlamli"
        ))

    def _kontrol_uzunluk(self, cikti: str, rapor: ValidationReport) -> None:
        """Minimum ve maksimum uzunluk kontrolu."""
        if not cikti:
            return
        uzunluk = len(cikti)

        if self._min_uzunluk > 0:
            if uzunluk < self._min_uzunluk:
                rapor.sonuclar.append(ValidationResult(
                    kural_adi="min_uzunluk",
                    gecti=False,
                    mesaj=f"Cikti {uzunluk} karakter, minimum {self._min_uzunluk} gerekli"
                ))
            else:
                rapor.sonuclar.append(ValidationResult(
                    kural_adi="min_uzunluk",
                    gecti=True,
                    mesaj=f"Cikti {uzunluk} karakter, minimum saglandi"
                ))

        if self._maks_uzunluk > 0:
            if uzunluk > self._maks_uzunluk:
                rapor.sonuclar.append(ValidationResult(
                    kural_adi="maks_uzunluk",
                    gecti=False,
                    mesaj=f"Cikti {uzunluk} karakter, maksimum {self._maks_uzunluk} asildi"
                ))
            else:
                rapor.sonuclar.append(ValidationResult(
                    kural_adi="maks_uzunluk",
                    gecti=True,
                    mesaj=f"Cikti {uzunluk} karakter, maksimum icinde"
                ))

    def _kontrol_kod_bloku(self, hedef: str, cikti: str, rapor: ValidationReport) -> None:
        """Kod blogu sayisi kontrolu -- sadece hedef kod yazma iceriyorsa."""
        kod_hedefleri = ["kod", "yaz", "olustur", "fonksiyon", "sinif",
                         "script", "betik", "program", "implement"]
        kod_isteniyor = any(k in hedef.lower() for k in kod_hedefleri)

        if not kod_isteniyor:
            rapor.sonuclar.append(ValidationResult(
                kural_adi="kod_bloku",
                gecti=True,
                mesaj="Hedef kod yazma gerektirmiyor, atlandi"
            ))
            return

        if self._min_kod <= 0:
            rapor.sonuclar.append(ValidationResult(
                kural_adi="kod_bloku",
                gecti=True,
                mesaj="Kod blogu kontrolu devre disi"
            ))
            return

        # Kod bloklarini say
        kod_bloklari = re.findall(r"```\w*\n", cikti)
        sayi = len(kod_bloklari)

        if sayi < self._min_kod:
            rapor.sonuclar.append(ValidationResult(
                kural_adi="kod_bloku",
                gecti=False,
                mesaj=f"Beklenen minimum {self._min_kod} kod blogu, bulunan: {sayi}"
            ))
        else:
            rapor.sonuclar.append(ValidationResult(
                kural_adi="kod_bloku",
                gecti=True,
                mesaj=f"Kod bloklari yeterli: {sayi}"
            ))

    def _hassas_tip_etiket(self, regex: re.Pattern) -> str:
        """Regex pattern'ine göre hassas bilgi tipini döndür."""
        p = regex.pattern
        if "sk-" in p:
            return "API_KEY"
        if "ghp_" in p or "gho_" in p:
            return "GITHUB_TOKEN"
        if "AKIA" in p:
            return "AWS_KEY"
        if "PRIVATE KEY" in p:
            return "PRIVATE_KEY"
        if "xox" in p:
            return "SLACK_TOKEN"
        if "eyJ" in p:
            return "JWT"
        return "UNKNOWN"
