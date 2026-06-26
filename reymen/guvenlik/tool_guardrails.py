# -*- coding: utf-8 -*-
"""
tool_guardrails.py — Arac guvenlik modulu.

Tehlikeli islemleri engeller, parametre dogrulama
ve izin kontrolu yapar.
"""

import re
import json
import logging
import time as _time
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

logger = logging.getLogger(__name__)


class ToolGuardrails:
    """
    Arac guvenlik yoneticisi.

    Tehlikeli islemleri tespit eder, parametre
    dogrulama ve izin kontrolu yapar.
    """

    # Varsayilan tehlikeli araclar
    VARSAYILAN_RISKLI = {
        "KOMUT_CALISTIR",
        "PYTHON_CALISTIR",
        "TARAYICI_AC",
        "EKRAN_TIKLA",
        "MAKRO_OYNAT",
        "SIL",
        "SISTEM_DEGISTIR",
        "DOSYA_YAZ",
        "VERI_TABANI_SIL",
        "AG_YONET",
    }

    # Varsayilan yasakli parametreler
    VARSAYILAN_YASAKLI = {
        "rm -rf",
        "format",
        "del /f",
        "drop table",
        "drop database",
        "shutdown",
        "reboot",
        "mkfs",
        "dd if=",
    }

    def __init__(
        self,
        riskli_araclar: Optional[Set[str]] = None,
        yasakli_parametreler: Optional[Set[str]] = None
    ):
        """
        ToolGuardrails baslatici.

        Args:
            riskli_araclar: Riskli arac adlari
            yasakli_parametreler: Yasakli parametre icerikleri
        """
        self._riskli_araclar = set(riskli_araclar) if riskli_araclar else set(self.VARSAYILAN_RISKLI)
        self._yasakli_parametreler = set(yasakli_parametreler) if yasakli_parametreler else set(self.VARSAYILAN_YASAKLI)
        self._izinli_araclar: Set[str] = set()
        self._engellenen_islemler: List[Dict[str, Any]] = []
        self._guvenlik_seviyesi: int = 3  # 1: dusuk, 5: yuksek

    def __repr__(self) -> str:
        """ToolGuardrails debug representation."""
        istatistik = self.istatistik()
        return (
            f"<ToolGuardrails seviye={istatistik['guvenlik_seviyesi']} "
            f"izinli={istatistik['izinli_arac_sayisi']} "
            f"engellenen={istatistik['engellenen_islem']} "
            f"riskli={istatistik['riskli_arac_sayisi']}>"
        )

    def __str__(self) -> str:
        """ToolGuardrails kisa string."""
        sinif = self.__class__.__name__
        seviye = self._guvenlik_seviyesi
        izinli = len(self._izinli_araclar)
        engel = len(self._engellenen_islemler)
        return f"{sinif}[seviye={seviye}, izinli={izinli}, engel={engel}]"

    def reset(self) -> None:
        """Tum durumu sifirlar — izinler, engel listesi, seviye."""
        self._izinli_araclar = set()
        self._engellenen_islemler = []
        self._guvenlik_seviyesi = 3
        logger.info("ToolGuardrails sifirlandi")

    def riskli_arac_ekle(self, arac_adi: str) -> bool:
        """Riskli araclar kumesine yeni bir arac ekler.

        Args:
            arac_adi: Eklenecek arac adi

        Returns:
            bool: Basarili ise True
        """
        try:
            self._riskli_araclar.add(arac_adi.upper())
            logger.info(f"Riskli arac eklendi: {arac_adi}")
            return True
        except Exception as e:
            logger.error(f"Riskli arac ekleme hatasi: {e}")
            return False

    def riskli_arac_cikar(self, arac_adi: str) -> bool:
        """Riskli araclar kumesinden bir arac cikarir.

        Args:
            arac_adi: Cikarilacak arac adi

        Returns:
            bool: Basarili ise True
        """
        try:
            self._riskli_araclar.discard(arac_adi.upper())
            logger.info(f"Riskli arac cikarildi: {arac_adi}")
            return True
        except Exception as e:
            logger.error(f"Riskli arac cikarma hatasi: {e}")
            return False

    def kontrolet(
        self,
        arac: Any,
        **params
    ) -> Dict[str, Any]:
        """
        Bir arac ve parametrelerini guvenlik kontrolunden gecirir.

        Args:
            arac: Kontrol edilecek arac (fonksiyon veya ad)
            **params: Arac parametreleri

        Returns:
            dict: Kontrol sonucu
        """
        try:
            arac_adi = self._arac_adi_al(arac)

            # 1. Arac adi kontrolu
            arac_kontrol = self._arac_kontrol(arac_adi)
            if not arac_kontrol["guvenli"]:
                self._engellenen_islemler.append({
                    "arac": arac_adi,
                    "parametreler": params,
                    "sebep": arac_kontrol["sebep"],
                    "zaman": _time.time(),
                })
                return arac_kontrol

            # 2. Parametre kontrolu
            parametre_kontrol = self._parametre_kontrol(params)
            if not parametre_kontrol["guvenli"]:
                self._engellenen_islemler.append({
                    "arac": arac_adi,
                    "parametreler": params,
                    "sebep": parametre_kontrol["sebep"],
                    "zaman": _time.time(),
                })
                return parametre_kontrol

            # 3. Seviye kontrolu
            if self._guvenlik_seviyesi >= 4:
                for param_ad, param_val in params.items():
                    param_str = str(param_val).lower()
                    for yasak in self._yasakli_parametreler:
                        if yasak.lower() in param_str:
                            self._engellenen_islemler.append({
                                "arac": arac_adi,
                                "parametreler": params,
                                "sebep": f"Yuksek guvenlik: {yasak} tespit edildi",
                                "zaman": _time.time(),
                            })
                            return {"guvenli": False, "sebep": f"Yasakli icerik: {yasak}"}

            return {"guvenli": True, "arac": arac_adi, "seviye": self._guvenlik_seviyesi}

        except Exception as e:
            logger.error(f"Guvenlik kontrol hatasi: {e}")
            return {"guvenli": False, "sebep": f"Kontrol hatasi: {e}"}

    def _arac_adi_al(self, arac: Any) -> str:
        """Aracin adini alir."""
        if isinstance(arac, str):
            return arac.upper()
        if hasattr(arac, "__name__"):
            return arac.__name__.upper()
        if hasattr(arac, "__class__"):
            return arac.__class__.__name__.upper()
        return str(arac).upper()

    def _arac_kontrol(self, arac_adi: str) -> Dict[str, Any]:
        """Arac adi guvenlik kontrolu."""
        if arac_adi in self._riskli_araclar:
            if arac_adi not in self._izinli_araclar:
                return {
                    "guvenli": False,
                    "sebep": f"Riskli arac izni yok: {arac_adi}",
                    "riskli": True,
                }
            return {
                "guvenli": True,
                "sebep": f"Riskli arac izinli: {arac_adi}",
                "riskli": True,
            }
        return {"guvenli": True, "sebep": "Guvenli arac", "riskli": False}

    def _parametre_kontrol(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Parametre guvenlik kontrolu."""
        for param_ad, param_val in params.items():
            param_str = str(param_val).lower()

            for yasak in self._yasakli_parametreler:
                if yasak.lower() in param_str:
                    return {
                        "guvenli": False,
                        "sebep": f"Yasakli parametre: {yasak} ({param_ad})",
                    }

            # Shell injection kontrolu
            if self._shell_injection_kontrol(param_str):
                return {
                    "guvenli": False,
                    "sebep": f"Shell injection tespit edildi: {param_ad}",
                }

            # Path traversal kontrolu (Windows ve Unix)
            if ".." in param_str and ("/" in param_str or "\\" in param_str):
                return {
                    "guvenli": False,
                    "sebep": f"Path traversal tespit edildi: {param_ad}",
                }

        return {"guvenli": True, "sebep": "Parametreler guvenli"}

    def _shell_injection_kontrol(self, metin: str) -> bool:
        """Shell injection pattern'lerini kontrol eder."""
        injection_patterns = [
            r'[|;&$`\n]',
            r'\$\{',
            r'\$\(.*\)',
        ]
        try:
            for pattern in injection_patterns:
                if re.search(pattern, metin):
                    return True
            return False
        except Exception:
            return False

    def guvenli_mi(self, arac: Any) -> bool:
        """
        Bir aracin guvenli olup olmadigini kontrol eder.

        Args:
            arac: Kontrol edilecek arac

        Returns:
            bool: Guvenli ise True
        """
        try:
            sonuc = self.kontrolet(arac)
            return sonuc.get("guvenli", False)
        except Exception as e:
            logger.error(f"Guvenlik sorgu hatasi: {e}")
            return False

    def izin_verilen_araclar(self) -> List[str]:
        """
        Izni verilen araclari listeler.

        Returns:
            list: Izinli arac adlari
        """
        return sorted(self._izinli_araclar)

    def izin_ver(self, arac_adi: str) -> bool:
        """
        Bir araca izin verir.

        Args:
            arac_adi: Arac adi

        Returns:
            bool: Basarili ise True
        """
        try:
            self._izinli_araclar.add(arac_adi.upper())
            logger.info(f"Izin verildi: {arac_adi}")
            return True
        except Exception as e:
            logger.error(f"Izin verme hatasi: {e}")
            return False

    def izin_kaldir(self, arac_adi: str) -> bool:
        """
        Bir aracin iznini kaldirir.

        Args:
            arac_adi: Arac adi

        Returns:
            bool: Basarili ise True
        """
        try:
            self._izinli_araclar.discard(arac_adi.upper())
            logger.info(f"Izin kaldirildi: {arac_adi}")
            return True
        except Exception as e:
            logger.error(f"Izin kaldirma hatasi: {e}")
            return False

    def guvenlik_seviyesi_ayarla(self, seviye: int) -> None:
        """
        Guvenlik seviyesini ayarlar.

        Args:
            seviye: Guvenlik seviyesi (1-5)
        """
        self._guvenlik_seviyesi = max(1, min(5, seviye))
        logger.info(f"Guvenlik seviyesi: {self._guvenlik_seviyesi}")

    def engellenen_islemler(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Engellenen islemleri dondurur."""
        return self._engellenen_islemler[-limit:]

    def istatistik(self) -> Dict[str, Any]:
        """Guvenlik istatistiklerini dondurur."""
        return {
            "guvenlik_seviyesi": self._guvenlik_seviyesi,
            "izinli_arac_sayisi": len(self._izinli_araclar),
            "engellenen_islem": len(self._engellenen_islemler),
            "riskli_arac_sayisi": len(self._riskli_araclar),
        }


def run(**kwargs) -> str:
    """
    ToolGuardrails'i calistirir.

    Args:
        **kwargs: Test parametreleri

    Returns:
        str: Test sonucu
    """
    try:
        guardrails = ToolGuardrails()

        # Guvenli arac kontrol
        sonuc1 = guardrails.kontrolet("test_tool", parametre="guvenli deger")

        # Riskli arac kontrol (izinsiz)
        sonuc2 = guardrails.kontrolet("KOMUT_CALISTIR", komut="ls")

        # Riskli araca izin ver
        guardrails.izin_ver("KOMUT_CALISTIR")
        sonuc3 = guardrails.kontrolet("KOMUT_CALISTIR", komut="ls")

        # Yasakli parametre kontrolu
        sonuc4 = guardrails.kontrolet("test_tool", komut="rm -rf /")

        return json.dumps({
            "guvenli_arac": sonuc1,
            "riskli_izinsiz": sonuc2,
            "riskli_izinli": sonuc3,
            "yasakli_parametre": sonuc4,
            "istatistik": guardrails.istatistik(),
        }, ensure_ascii=False, indent=2)

    except Exception as e:
        return f"Tool guardrails hatasi: {e}"
