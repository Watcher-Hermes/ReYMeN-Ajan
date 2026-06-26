# -*- coding: utf-8 -*-
"""
path_security.py — Yol Guvenligi.

Dosya yollarini dogrular, path traversal ve sembolik link
saldirilarina karsi korur. Guvenli bolgeleri yapilandirilabilir.
"""

import os
from pathlib import Path
from typing import List, Optional, Set, Tuple

# Proje kok dizini (guvenli bolge)
PROJE_KOK = Path(__file__).parent.resolve()

# Varsayilan izinli ozel dizinler
VARSAYILAN_OZEL_DIZINLER = [
    Path.home() / ".ReYMeN",
    Path.home() / "AppData/Local/ReYMeN",
]


class GuvenliBolgeYoneticisi:
    """Guvenli bolge yoneticisi — yol dogrulama ve izin yonetimi."""

    def __init__(self, kok: Optional[Path] = None, ozel_dizinler: Optional[List[Path]] = None):
        """
        Args:
            kok: Guvenli bolge kok dizini (varsayilan: PROJE_KOK)
            ozel_dizinler: Ek izinli dizinler (None=varsayilan, []=hicbiri)
        """
        self._kok = kok.resolve() if kok else PROJE_KOK
        if ozel_dizinler is None:
            self._ozel = list(VARSAYILAN_OZEL_DIZINLER)
        else:
            self._ozel = list(ozel_dizinler)
        self._ek_izinler: Set[Path] = set()

    @property
    def kok(self) -> Path:
        return self._kok

    def izin_ekle(self, yol: str) -> bool:
        """Guvenli bolgelere yeni bir izinli yol ekler.

        Args:
            yol: Eklenecek yol

        Returns:
            bool: Basarili ise True
        """
        try:
            p = Path(yol).resolve()
            self._ek_izinler.add(p)
            return True
        except Exception:
            return False

    def izin_cikar(self, yol: str) -> bool:
        """Izinli yollardan bir yolu cikarir.

        Args:
            yol: Cikarilacak yol

        Returns:
            bool: Bulunup cikarildiysa True
        """
        try:
            p = Path(yol).resolve()
            self._ek_izinler.discard(p)
            return True
        except Exception:
            return False

    def izinli_yollar(self) -> List[str]:
        """Tum izinli yollari listeler."""
        return sorted(str(p) for p in self._ek_izinler)

    def yol_guvenli_mi(self, hedef_yol: str) -> Tuple[bool, str]:
        """Bir yolun guvenli bolgeler icinde olup olmadigini kontrol eder.

        Args:
            hedef_yol: Kontrol edilecek yol

        Returns:
            (guvenli_mi, normalize_edilmis_yol_veya_hata_mesaji)
        """
        try:
            if not hedef_yol or not isinstance(hedef_yol, str):
                return False, "Gecersiz yol parametresi"
            yol = Path(hedef_yol).resolve()
        except Exception as e:
            return False, f"Gecersiz yol cozulemedi: {e}"

        # Kok dizin icinde mi?
        try:
            yol.relative_to(self._kok)
            return True, str(yol)
        except ValueError:
            pass

        # Ozel dizinler icinde mi?
        for izin in self._ozel:
            try:
                yol.relative_to(izin)
                return True, str(yol)
            except ValueError:
                continue

        # Ek izinler icinde mi?
        for ek in self._ek_izinler:
            try:
                yol.relative_to(ek)
                return True, str(yol)
            except ValueError:
                continue

        return False, f"Guvenli bolge disi: {yol}"

    def sembolik_link_guvenli_mi(self, yol: str) -> Tuple[bool, str]:
        """Sembolik link kontrolu — hedef guvenli bolgede mi?

        Args:
            yol: Kontrol edilecek yol

        Returns:
            (guvenli_mi, gercek_yol_veya_hata)
        """
        try:
            p = Path(yol)
        except Exception as e:
            return False, f"Gecersiz yol: {e}"

        if not p.is_symlink():
            return True, str(p)

        gercek = p.resolve()
        guvenli, mesaj = self.yol_guvenli_mi(str(gercek))
        if not guvenli:
            return False, f"Symlink guvenli bolge disina isaret ediyor: {gercek}"
        return True, str(gercek)

    def siniflandir(self, hedef_yol: str) -> dict:
        """Bir yolu siniflandirir: guvenli bolge, izinli bolge, tehlikeli.

        Args:
            hedef_yol: Siniflandirilacak yol

        Returns:
            dict: {"bolge": str, "yol": str, "guvenli": bool}
        """
        guvenli, mesaj = self.yol_guvenli_mi(hedef_yol)
        if guvenli:
            yol = mesaj
            p = Path(yol)
            try:
                p.relative_to(self._kok)
                return {"bolge": "proje_koku", "yol": yol, "guvenli": True}
            except ValueError:
                return {"bolge": "izinli_bolge", "yol": yol, "guvenli": True}
        return {"bolge": "tehlikeli", "yol": hedef_yol, "guvenli": False, "sebep": mesaj}

    def istatistik(self) -> dict:
        """Guvenli bolge istatistiklerini dondurur."""
        return {
            "kok": str(self._kok),
            "ozel_dizin_sayisi": len(self._ozel),
            "ek_izin_sayisi": len(self._ek_izinler),
            "ek_izinler": sorted(str(p) for p in self._ek_izinler),
        }

    def sifirla(self) -> None:
        """Ek izinleri ve durumu sifirlar."""
        self._ek_izinler.clear()


# ---- Eski API uyumlu fonksiyonlar (kaldirma yok) ----

_yonetici = GuvenliBolgeYoneticisi()


def yol_dogrula(hedef_yol: str) -> Tuple[bool, str]:
    """(Eski API) Bir yolun guvenli bolge icinde olup olmadigini dogrula.

    Args:
        hedef_yol: Dogrulanacak yol

    Returns:
        (gecerli_mi, normalize_edilmis_yol_veya_hata)
    """
    return _yonetici.yol_guvenli_mi(hedef_yol)


def sembolik_link_kontrol(yol: str) -> Tuple[bool, str]:
    """(Eski API) Sembolik link kontrolu.

    Args:
        yol: Kontrol edilecek yol

    Returns:
        (guvenli_mi, gercek_yol)
    """
    return _yonetici.sembolik_link_guvenli_mi(yol)


# ---- Yeni yardimci fonksiyon ----

def normalize_ve_dogrula(hedef_yol: str, genislet: bool = True) -> Tuple[bool, str]:
    """Yolu normalize eder, ev dizinini genisletir ve dogrular.

    Args:
        hedef_yol: Dogrulanacak yol
        genislet: ~ karakterini home'a genislet (varsayilan True)

    Returns:
        (gecerli_mi, normalize_edilmis_yol_veya_hata)
    """
    try:
        if not hedef_yol or not isinstance(hedef_yol, str):
            return False, "Gecersiz yol parametresi"
        yol = hedef_yol.strip()
        if genislet:
            yol = os.path.expanduser(yol)
            yol = os.path.expandvars(yol)
        return yol_dogrula(yol)
    except Exception as e:
        return False, f"Normalize hatasi: {e}"


if __name__ == "__main__":
    testler = ["test.txt", "../disari.txt", __file__, "~/.ReYMeN/test", "C:/Windows/System32"]
    for t in testler:
        gecerli, mesaj = normalize_ve_dogrula(t)
        print(f"  {t}: {'Gecerli' if gecerli else 'Gecersiz'} -> {mesaj}")
