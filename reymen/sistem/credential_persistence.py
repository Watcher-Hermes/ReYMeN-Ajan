# -*- coding: utf-8 -*-
"""credential_persistence.py — Kimlik Kaliciligi.

API anahtarlarini Windows Credential Manager veya
sifrelenmis dosyada kalici olarak saklar.
"""

import os
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

CRED_DOSYASI = Path(__file__).parent / ".ReYMeN" / "credentials.enc"
KEY_DOSYASI = Path(__file__).parent / ".ReYMeN" / ".xor_key"


def _xor_anahtari_oku() -> bytes:
    """XOR sifreleme anahtarini guvenli kaynaktan al.

    Oncelik: environment variable REYMEN_CRED_KEY > .xor_key dosyasi
    Yoksa: rastgele 32 byte uretir, .xor_key dosyasina kaydeder.
    """
    env_key = os.environ.get("REYMEN_CRED_KEY")
    if env_key:
        return env_key.encode("utf-8")

    if KEY_DOSYASI.exists():
        return KEY_DOSYASI.read_bytes()

    import secrets
    yeni_anahtar = secrets.token_bytes(32)
    KEY_DOSYASI.parent.mkdir(parents=True, exist_ok=True)
    KEY_DOSYASI.write_bytes(yeni_anahtar)
    logger.info("Yeni XOR anahtari olusturuldu: %s", KEY_DOSYASI)
    return yeni_anahtar


class CredentialPersistence:
    """Kimlik kalicilik yoneticisi.

    API anahtarlarini Windows Credential Manager'da
    veya sifrelenmis dosyada saklar.
    """

    def __init__(self):
        self._wcm_available = False
        try:
            import win32cred
            self._wcm = win32cred
            self._wcm_available = True
        except ImportError:
            self._wcm_available = False
            logger.debug("win32cred bulunamadi, dosya tabanli depolama kullanilacak")

    def _basit_sifrele(self, veri: str) -> bytes:
        """Basit XOR sifreleme (guclu degil, sadece duz metin korumasi)."""
        anahtar = _xor_anahtari_oku()
        return bytes(
            ord(c) ^ anahtar[i % len(anahtar)]
            for i, c in enumerate(veri)
        )

    def _basit_coz(self, veri: bytes) -> str:
        anahtar = _xor_anahtari_oku()
        return "".join(
            chr(b ^ anahtar[i % len(anahtar)])
            for i, b in enumerate(veri)
        )

    def wcm_kaydet(self, anahtar: str, deger: str) -> bool:
        """Windows Credential Manager'a kaydet.

        Args:
            anahtar: Anahtar adi (ornek: DEEPSEEK_API_KEY)
            deger: Anahtar degeri

        Returns:
            Basarili mi?
        """
        if not self._wcm_available:
            logger.warning("WCM kullanilamiyor, anahtar dosyaya kaydedilecek: %s", anahtar)
            return False
        try:
            import pywintypes
            cred_type = self._wcm.CRED_TYPE_GENERIC
            target = f"ReYMeN_{anahtar}"
            self._wcm.CredWrite(
                {
                    "Type": cred_type,
                    "TargetName": target,
                    "CredentialBlob": deger,
                    "Persist": self._wcm.CRED_PERSIST_LOCAL_MACHINE,
                },
                0,
            )
            logger.info("WCM anahtar kaydedildi: %s", anahtar)
            return True
        except Exception as exc:
            logger.error("WCM kaydetme hatasi (%s): %s", anahtar, exc)
            return False

    def wcm_oku(self, anahtar: str) -> str:
        """Windows Credential Manager'dan oku."""
        if not self._wcm_available:
            logger.warning("WCM kullanilamiyor, dosyadan okunacak: %s", anahtar)
            return ""
        try:
            target = f"ReYMeN_{anahtar}"
            cred = self._wcm.CredRead(target, self._wcm.CRED_TYPE_GENERIC, 0)
            deger = cred["CredentialBlob"].decode("utf-16").strip()
            logger.debug("WCM anahtar okundu: %s", anahtar)
            return deger
        except Exception as exc:
            logger.error("WCM okuma hatasi (%s): %s", anahtar, exc)
            return ""

    def wcm_sil(self, anahtar: str) -> bool:
        """Windows Credential Manager'dan sil."""
        if not self._wcm_available:
            logger.warning("WCM kullanilamiyor, silme basarisiz: %s", anahtar)
            return False
        try:
            target = f"ReYMeN_{anahtar}"
            self._wcm.CredDelete(target, self._wcm.CRED_TYPE_GENERIC, 0)
            logger.info("WCM anahtar silindi: %s", anahtar)
            return True
        except Exception as exc:
            logger.error("WCM silme hatasi (%s): %s", anahtar, exc)
            return False

    def dosya_kaydet(self, anahtarlar: dict[str, str]) -> bool:
        """Anahtarlari sifrelenmis dosyaya kaydet.

        Args:
            anahtarlar: {anahtar_adi: deger} sozlugu

        Returns:
            Basarili mi?
        """
        try:
            import json
            veri = json.dumps(anahtarlar)
            sifreli = self._basit_sifrele(veri)
            CRED_DOSYASI.parent.mkdir(parents=True, exist_ok=True)
            CRED_DOSYASI.write_bytes(sifreli)
            logger.info("Dosyaya kaydedildi: %d anahtar", len(anahtarlar))
            return True
        except Exception as exc:
            logger.error("Dosya kaydetme hatasi: %s", exc)
            return False

    def dosya_oku(self) -> dict[str, str]:
        """Sifrelenmis dosyadan anahtarlari oku."""
        if not CRED_DOSYASI.exists():
            return {}
        try:
            import json
            sifreli = CRED_DOSYASI.read_bytes()
            veri = self._basit_coz(sifreli)
            return json.loads(veri)
        except Exception as exc:
            logger.error("Dosya okuma hatasi: %s", exc)
            return {}

    def durum(self) -> str:
        """Kalicilik durumu."""
        wcm = "VAR" if self._wcm_available else "YOK"
        dosya = "VAR" if CRED_DOSYASI.exists() else "YOK"
        anahtar = "VAR" if (_xor_anahtari_oku() != b"") else "YOK"
        return f"[CredPersistence] WCM: {wcm}, Dosya: {dosya}, XOR Key: {anahtar}"


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    p = CredentialPersistence()
    print(p.durum())
    p.dosya_kaydet({"TEST_KEY": "test_value"})
    print(f"Dosyadan okunan: {p.dosya_oku()}")
