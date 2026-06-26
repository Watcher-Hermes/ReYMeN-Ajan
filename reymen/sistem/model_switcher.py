# -*- coding: utf-8 -*-
"""
model_switcher.py — Otomatik model/provider geçiş sistemi.

API key bittiğinde veya provider başarısız olduğunda:
1. Fallback zincirinden yeni provider seçer
2. Tüm Telegram botlarını otomatik geçirir
3. Gateway'i yeniden başlatır
4. Bot bağlantısını test eder

KATI KURAL: ReYMeN hangi modelde ise TÜM Telegram botları da aynı modelde.

Kullanım:
    from reymen.sistem.model_switcher import ModelSwitcher
    switcher = ModelSwitcher()
    switcher.kontrol_ve_gec()  # Otomatik kontrol + geçiş
"""

import json
import logging
import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path
from typing import Optional, Dict, List, Any, Tuple
from datetime import datetime

try:
    from reymen.core.logging_config import get_logger
    log = get_logger("model_switcher")
except Exception:
    import logging
    log = logging.getLogger("model_switcher")


class ModelSwitcher:
    """Otomatik model/provider geçiş yöneticisi."""

    # ── Provider Öncelik Sırası ──────────────────────────────────────────────
    # Birinci provider başarısız olursa sırayla dener
    PROVIDER_ZINCIRI = [
        {
            "ad": "xiaomi",
            "model": "mimo-v2.5-pro",
            "api_url": "https://api.xiaomimimo.com/v1",
            "api_key_env": "XIAOMI_API_KEY",
            "maliyet_uygun": True,
            "oncelik": 1,
        },
        {
            "ad": "deepseek",
            "model": "deepseek-chat",
            "api_url": "https://api.deepseek.com/v1",
            "api_key_env": "DEEPSEEK_API_KEY",
            "maliyet_uygun": True,
            "oncelik": 2,
        },
        {
            "ad": "openai",
            "model": "gpt-4o-mini",
            "api_url": "https://api.openai.com/v1",
            "api_key_env": "OPENAI_API_KEY",
            "maliyet_uygun": False,
            "oncelik": 3,
        },
        {
            "ad": "lmstudio",
            "model": "local-model",
            "api_url": "http://127.0.0.1:1234/v1",
            "api_key_env": None,  # Key gerektirmez
            "maliyet_uygun": True,
            "oncelik": 4,
        },
        {
            "ad": "ollama",
            "model": "llama3",
            "api_url": "http://127.0.0.1:11434/v1",
            "api_key_env": None,
            "maliyet_uygun": True,
            "oncelik": 5,
        },
    ]

    def __init__(self, config_path: Optional[str] = None,
                 bot_config_path: Optional[str] = None):
        """
        Args:
            config_path: Ana yapılandırma dosyası
            bot_config_path: Bot yapılandırma dosyası
        """
        base = Path.home() / "AppData" / "Local" / "hermes" / "profiles" / "reymen"
        self._config_path = Path(config_path) if config_path else base / "config.json"
        self._bot_config_path = Path(bot_config_path) if bot_config_path else base / ".ReYMeN" / "bot_config.json"
        self._state_path = base / ".ReYMeN" / "model_state.json"
        self._gateway_path = Path.home() / "Desktop" / "Reymen Proje" / "hermes_projesi"

        for p in [self._config_path.parent, self._bot_config_path.parent, self._state_path.parent]:
            p.mkdir(parents=True, exist_ok=True)

        self._aktif_provider = None
        self._aktif_model = None
        self._gecmis: List[Dict] = []
        self._yukle()

    def _yukle(self):
        """Mevcut durumu yükler."""
        if self._state_path.exists():
            try:
                data = json.loads(self._state_path.read_text(encoding="utf-8"))
                self._aktif_provider = data.get("aktif_provider")
                self._aktif_model = data.get("aktif_model")
                self._gecmis = data.get("gecmis", [])
            except Exception:
                pass

        # Config'den de oku
        if self._config_path.exists():
            try:
                cfg = json.loads(self._config_path.read_text(encoding="utf-8"))
                if not self._aktif_provider:
                    self._aktif_provider = cfg.get("provider", "xiaomi")
                if not self._aktif_model:
                    self._aktif_model = cfg.get("model", "mimo-v2.5-pro")
            except Exception:
                pass

    def _kaydet(self):
        """Durumu kaydeder."""
        data = {
            "aktif_provider": self._aktif_provider,
            "aktif_model": self._aktif_model,
            "son_guncelleme": datetime.now().isoformat(),
            "gecmis": self._gecmis[-50:],  # Son 50 kayıt
        }
        self._state_path.write_text(
            json.dumps(data, indent=2, ensure_ascii=False, default=str),
            encoding="utf-8"
        )

    # ── API Key Kontrolü ─────────────────────────────────────────────────────

    def api_key_kontrol(self, provider: Dict) -> Tuple[bool, str]:
        """
        Provider'ın API key'ini kontrol eder.

        Returns:
            (aktif, mesaj)
        """
        api_key_env = provider.get("api_key_env")

        # Key gerektirmeyen provider (LM Studio, Ollama)
        if not api_key_env:
            return self._servis_kontrol(provider["api_url"])

        api_key = os.getenv(api_key_env, "").strip()
        if not api_key or api_key in ("***", "xxx", "your-key-here"):
            return False, f"{provider['ad']}: API key tanımlı değil ({api_key_env})"

        # Key var ama geçerli mi? (hafif kontrol)
        return True, f"{provider['ad']}: Key mevcut"

    def _servis_kontrol(self, api_url: str) -> Tuple[bool, str]:
        """Yerel servisin çalışıp çalışmadığını kontrol eder."""
        try:
            req = urllib.request.Request(api_url + "/models", method="GET")
            with urllib.request.urlopen(req, timeout=5) as resp:
                if resp.status == 200:
                    return True, f"Servis aktif: {api_url}"
                return False, f"Servis hata: {resp.status}"
        except Exception as e:
            return False, f"Servis erişilemez: {api_url} ({e})"

    def api_key_bitti_mi(self, provider: Dict) -> bool:
        """
        API key'in kredisinin bitip bitmediğini kontrol eder.
        Basit bir test isteği göndererek kontrol eder.
        """
        api_key_env = provider.get("api_key_env")
        if not api_key_env:
            return False  # Yerel servisler kredi bitirmez

        api_key = os.getenv(api_key_env, "").strip()
        if not api_key:
            return True

        # Basit test isteği
        try:
            url = provider["api_url"] + "/chat/completions"
            payload = json.dumps({
                "model": provider["model"],
                "messages": [{"role": "user", "content": "test"}],
                "max_tokens": 5,
            }).encode("utf-8")

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            }

            req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=15) as resp:
                return resp.status != 200

        except urllib.error.HTTPError as e:
            if e.code == 402:  # Payment Required
                return True
            if e.code == 401:  # Unauthorized
                return True
            if e.code == 429:  # Rate limit (geçici)
                return False
            return False
        except Exception:
            return False

    # ── Provider Seçimi ──────────────────────────────────────────────────────

    def en_iyi_provider_bul(self) -> Optional[Dict]:
        """
        Fallback zincirinden en iyi çalışan provider'ı bulur.

        Returns:
            Provider dict veya None
        """
        for provider in sorted(self.PROVIDER_ZINCIRI, key=lambda p: p["oncelik"]):
            aktif, mesaj = self.api_key_kontrol(provider)
            log.info(f"Provider kontrol: {provider['ad']} → {mesaj}")

            if aktif:
                # Kredi bitmiş mi?
                if self.api_key_bitti_mi(provider):
                    log.warning(f"{provider['ad']}: Kredi bitmiş, sonraki...")
                    continue
                return provider

        return None

    # ── Config Güncelleme ────────────────────────────────────────────────────

    def config_guncelle(self, provider: Dict) -> bool:
        """
        Ana config dosyasını günceller.

        Returns:
            Başarılı mı?
        """
        try:
            cfg = {}
            if self._config_path.exists():
                cfg = json.loads(self._config_path.read_text(encoding="utf-8"))

            cfg["provider"] = provider["ad"]
            cfg["model"] = provider["model"]
            cfg["api_url"] = provider["api_url"]
            cfg["son_guncelleme"] = datetime.now().isoformat()

            self._config_path.write_text(
                json.dumps(cfg, indent=2, ensure_ascii=False),
                encoding="utf-8"
            )

            # .env dosyasını da güncelle
            self._env_guncelle(provider)

            log.info(f"Config güncellendi: {provider['ad']}/{provider['model']}")
            return True

        except Exception as e:
            log.error(f"Config güncelleme hatası: {e}")
            return False

    def _env_guncelle(self, provider: Dict):
        """Projedeki .env dosyasını günceller."""
        env_path = self._gateway_path / ".env"
        if not env_path.exists():
            return

        try:
            icerik = env_path.read_text(encoding="utf-8")

            # PROVIDER satırını güncelle veya ekle
            if "PROVIDER=" in icerik:
                import re
                icerik = re.sub(r'PROVIDER=.*', f'PROVIDER={provider["ad"]}', icerik)
            else:
                icerik += f'\nPROVIDER={provider["ad"]}'

            if "MODEL=" in icerik:
                import re
                icerik = re.sub(r'MODEL=.*', f'MODEL={provider["model"]}', icerik)
            else:
                icerik += f'\nMODEL={provider["model"]}'

            env_path.write_text(icerik, encoding="utf-8")
            log.info(f".env güncellendi: PROVIDER={provider['ad']}, MODEL={provider['model']}")

        except Exception as e:
            log.error(f".env güncelleme hatası: {e}")

    # ── Bot Yapılandırması ────────────────────────────────────────────────────

    def bot_config_kaydet(self, provider: Dict):
        """
        Tüm bot'ların yapılandırmasını kaydeder.
        KATI KURAL: Tüm botlar aynı modeli kullanır.
        """
        bot_config = {
            "provider": provider["ad"],
            "model": provider["model"],
            "api_url": provider["api_url"],
            "tum_botlar_ayni_model": True,  # KATI KURAL
            "son_guncelleme": datetime.now().isoformat(),
            "botlar": self._bot_listesi_al(),
        }

        self._bot_config_path.write_text(
            json.dumps(bot_config, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )

        log.info(f"Bot config kaydedildi: {len(bot_config['botlar'])} bot → {provider['ad']}")

    def _bot_listesi_al(self) -> List[Dict]:
        """Kayıtlı tüm Telegram bot'larını listeler."""
        botlar = []

        # .env'den bot token'ları oku
        env_path = self._gateway_path / ".env"
        if env_path.exists():
            try:
                icerik = env_path.read_text(encoding="utf-8")
                import re
                # Tüm TELEGRAM_BOT_TOKEN_* satırlarını bul
                for match in re.finditer(r'(TELEGRAM_\w*BOT\w*TOKEN)\s*=\s*(.+)', icerik):
                    token_var = match.group(1)
                    token = match.group(2).strip()
                    if token and token not in ("", "xxx", "***"):
                        botlar.append({
                            "token_var": token_var,
                            "token_prefix": token[:10] + "...",
                            "provider": None,  # Güncellenecek
                        })
            except Exception:
                pass

        # Ana bot token'ı
        ana_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
        if ana_token and ana_token not in ("", "xxx", "***"):
            botlar.append({
                "token_var": "TELEGRAM_BOT_TOKEN",
                "token_prefix": ana_token[:10] + "...",
                "provider": None,
            })

        # Tekrarları kaldır
        benzersiz = []
        gorulen = set()
        for bot in botlar:
            if bot["token_var"] not in gorulen:
                benzersiz.append(bot)
                gorulen.add(bot["token_var"])

        return benzersiz

    # ── Gateway Yeniden Başlatma ──────────────────────────────────────────────

    def gateway_yeniden_baslat(self) -> Tuple[bool, str]:
        """
        Gateway'i yeniden başlatır.

        Returns:
            (basarili, mesaj)
        """
        try:
            # Önce mevcut gateway'i durdur
            self._gateway_durdur()
            time.sleep(2)

            # Yeni config ile başlat
            self._gateway_baslat()

            # Bağlantı testi
            time.sleep(5)
            baglanti_ok = self._baglanti_testi()

            if baglanti_ok:
                return True, "Gateway yeniden başlatıldı, bağlantı OK"
            else:
                return False, "Gateway başlatıldı ama bağlantı testi başarısız"

        except Exception as e:
            return False, f"Gateway yeniden başlatma hatası: {e}"

    def _gateway_durdur(self):
        """Gateway process'ini durdurur."""
        try:
            if sys.platform == "win32":
                # Windows'ta gateway process'ini bul ve durdur
                result = subprocess.run(
                    ["tasklist", "/FI", "IMAGENAME eq python.exe", "/FO", "CSV"],
                    capture_output=True, text=True, timeout=10
                )
                # Gateway PID'sini bul
                for line in result.stdout.splitlines():
                    if "gateway" in line.lower() or "reymen" in line.lower():
                        parts = line.split(",")
                        if len(parts) >= 2:
                            pid = parts[1].strip('"')
                            subprocess.run(["taskkill", "/F", "/PID", pid],
                                         capture_output=True, timeout=10)
            else:
                subprocess.run(["pkill", "-f", "gateway"],
                             capture_output=True, timeout=10)

            log.info("Gateway durduruldu")

        except Exception as e:
            log.warning(f"Gateway durdurma hatası: {e}")

    def _gateway_baslat(self):
        """Gateway'i başlatır."""
        try:
            gateway_script = self._gateway_path / "gateway" / "run.py"
            if gateway_script.exists():
                subprocess.Popen(
                    [sys.executable, str(gateway_script)],
                    cwd=str(self._gateway_path),
                    creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
                )
                log.info("Gateway başlatıldı")
            else:
                # Ana script ile başlat
                ana_script = self._gateway_path / "main.py"
                if ana_script.exists():
                    subprocess.Popen(
                        [sys.executable, str(ana_script)],
                        cwd=str(self._gateway_path),
                        creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
                    )
                    log.info("Ana script başlatıldı")

        except Exception as e:
            log.error(f"Gateway başlatma hatası: {e}")

    def _baglanti_testi(self) -> bool:
        """Telegram bot bağlantısını test eder."""
        token = os.getenv("TELEGRAM_BOT_TOKEN", "")
        if not token:
            log.warning("TELEGRAM_BOT_TOKEN tanımlı değil, bağlantı testi atlandı")
            return True  # Token yoksa test atla

        try:
            url = f"https://api.telegram.org/bot{token}/getMe"
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read())
                if data.get("ok"):
                    bot_name = data.get("result", {}).get("username", "?")
                    log.info(f"Telegram bot bağlantısı OK: @{bot_name}")
                    return True
                else:
                    log.error(f"Telegram bot bağlantı hatası: {data}")
                    return False

        except Exception as e:
            log.error(f"Telegram bot bağlantı testi hatası: {e}")
            return False

    # ── Ana Geçiş Fonksiyonu ─────────────────────────────────────────────────

    def kontrol_ve_gec(self) -> Dict[str, Any]:
        """
        Mevcut provider'ı kontrol eder, gerekirse geçiş yapar.

        KATI KURAL: ReYMeN hangi modelde ise TÜM Telegram botları da aynı modelde.

        Returns:
            {"gecildi": bool, "eski": {...}, "yeni": {...}, "botlar": [...]}
        """
        sonuc = {
            "gecildi": False,
            "eski": {"provider": self._aktif_provider, "model": self._aktif_model},
            "yeni": None,
            "botlar": [],
            "gateway_yeniden_baslatildi": False,
            "baglanti_ok": False,
        }

        # Mevcut provider'ı kontrol et
        mevcut_provider = None
        for p in self.PROVIDER_ZINCIRI:
            if p["ad"] == self._aktif_provider:
                mevcut_provider = p
                break

        if mevcut_provider:
            aktif, mesaj = self.api_key_kontrol(mevcut_provider)
            kredi_bitti = self.api_key_bitti_mi(mevcut_provider) if aktif else True

            if aktif and not kredi_bitti:
                log.info(f"Mevcut provider OK: {self._aktif_provider}")
                return sonuc

            log.warning(f"Mevcut provider sorunlu: {self._aktif_provider} → {mesaj}")

        # Yeni provider bul
        yeni_provider = self.en_iyi_provider_bul()
        if not yeni_provider:
            log.error("Hiçbir provider çalışır durumda değil!")
            sonuc["hata"] = "Hiçbir provider çalışır durumda değil"
            return sonuc

        # Aynı provider ise geçiş yapma
        if yeni_provider["ad"] == self._aktif_provider:
            log.info(f"Aynı provider, geçiş gerekmez: {self._aktif_provider}")
            return sonuc

        # ── GEÇİŞ YAP ────────────────────────────────────────────────────────
        log.info(f"MODEL GEÇİŞİ: {self._aktif_provider}/{self._aktif_model} → {yeni_provider['ad']}/{yeni_provider['model']}")

        # 1. Config güncelle
        self.config_guncelle(yeni_provider)

        # 2. Bot config kaydet (KATI KURAL: tüm botlar aynı model)
        self.bot_config_kaydet(yeni_provider)

        # 3. State güncelle
        eski_provider = self._aktif_provider
        eski_model = self._aktif_model
        self._aktif_provider = yeni_provider["ad"]
        self._aktif_model = yeni_provider["model"]
        self._gecmis.append({
            "eski": f"{eski_provider}/{eski_model}",
            "yeni": f"{yeni_provider['ad']}/{yeni_provider['model']}",
            "zaman": datetime.now().isoformat(),
            "sebep": "api_key_sorunlu",
        })
        self._kaydet()

        # 4. Gateway yeniden başlat
        gateway_ok, gateway_mesaj = self.gateway_yeniden_baslat()
        sonuc["gateway_yeniden_baslatildi"] = gateway_ok

        # 5. Bağlantı testi
        sonuc["baglanti_ok"] = self._baglanti_testi()

        # Sonuç
        sonuc["gecildi"] = True
        sonuc["yeni"] = {
            "provider": yeni_provider["ad"],
            "model": yeni_provider["model"],
        }
        sonuc["botlar"] = self._bot_listesi_al()
        sonuc["gateway_mesaj"] = gateway_mesaj

        log.info(f"Geçiş tamamlandı: {yeni_provider['ad']}/{yeni_provider['model']} | Gateway: {gateway_ok} | Bağlantı: {sonuc['baglanti_ok']}")

        return sonuc

    # ── Manuel Geçiş ─────────────────────────────────────────────────────────

    def manuel_gec(self, provider_ad: str) -> Dict[str, Any]:
        """
        Manuel olarak belirli bir provider'a geçer.

        Args:
            provider_ad: Hedef provider adı

        Returns:
            Geçiş sonucu
        """
        hedef = None
        for p in self.PROVIDER_ZINCIRI:
            if p["ad"] == provider_ad:
                hedef = p
                break

        if not hedef:
            return {"gecildi": False, "hata": f"Provider bulunamadı: {provider_ad}"}

        # Key kontrolü
        aktif, mesaj = self.api_key_kontrol(hedef)
        if not aktif:
            return {"gecildi": False, "hata": f"Provider kullanılamaz: {mesaj}"}

        # Geçiş yap
        self.config_guncelle(hedef)
        self.bot_config_kaydet(hedef)

        self._aktif_provider = hedef["ad"]
        self._aktif_model = hedef["model"]
        self._gecmis.append({
            "eski": f"{self._aktif_provider}/{self._aktif_model}",
            "yeni": f"{hedef['ad']}/{hedef['model']}",
            "zaman": datetime.now().isoformat(),
            "sebep": "manuel",
        })
        self._kaydet()

        # Gateway yeniden başlat
        gateway_ok, gateway_mesaj = self.gateway_yeniden_baslat()
        baglanti_ok = self._baglanti_testi()

        return {
            "gecildi": True,
            "yeni": {"provider": hedef["ad"], "model": hedef["model"]},
            "gateway_ok": gateway_ok,
            "baglanti_ok": baglanti_ok,
        }

    # ── Durum Raporu ─────────────────────────────────────────────────────────

    def durum(self) -> Dict[str, Any]:
        """Mevcut durum raporu."""
        provider_durumlari = []
        for p in self.PROVIDER_ZINCIRI:
            aktif, mesaj = self.api_key_kontrol(p)
            provider_durumlari.append({
                "ad": p["ad"],
                "model": p["model"],
                "aktif": aktif,
                "mesaj": mesaj,
                "oncelik": p["oncelik"],
            })

        return {
            "aktif_provider": self._aktif_provider,
            "aktif_model": self._aktif_model,
            "provider_durumlari": provider_durumlari,
            "son_gecis": self._gecmis[-1] if self._gecmis else None,
            "toplam_gecis": len(self._gecmis),
        }

    def formatla(self) -> str:
        """Durumu okunabilir format döner."""
        durum = self.durum()
        satirlar = [
            "🔄 Model Switcher Durumu",
            "=" * 40,
            f"Aktif: {durum['aktif_provider']}/{durum['aktif_model']}",
            f"Toplam geçiş: {durum['toplam_gecis']}",
            "",
            "Provider Durumları:",
        ]

        for p in durum["provider_durumlari"]:
            emoji = "✅" if p["aktif"] else "❌"
            aktif_str = " ← AKTİF" if p["ad"] == durum["aktif_provider"] else ""
            satirlar.append(f"  {emoji} {p['ad']} ({p['model']}) — {p['mesaj']}{aktif_str}")

        if durum["son_gecis"]:
            g = durum["son_gecis"]
            satirlar.append(f"\nSon geçiş: {g['eski']} → {g['yeni']} ({g['zaman']})")

        return "\n".join(satirlar)


# ── Global Instance ──────────────────────────────────────────────────────────

_switcher = None

def get_switcher() -> ModelSwitcher:
    """Global switcher instance'ı döner."""
    global _switcher
    if _switcher is None:
        _switcher = ModelSwitcher()
    return _switcher


# ── Motor Entegrasyonu ───────────────────────────────────────────────────────

def run(islem: str = "durum", provider: str = "") -> str:
    """Motor entegrasyonu."""
    switcher = get_switcher()

    if islem == "kontrol":
        sonuc = switcher.kontrol_ve_gec()
        if sonuc["gecildi"]:
            return (
                f"🔄 MODEL GEÇİŞİ YAPILDI!\n"
                f"Eski: {sonuc['eski']['provider']}/{sonuc['eski']['model']}\n"
                f"Yeni: {sonuc['yeni']['provider']}/{sonuc['yeni']['model']}\n"
                f"Botlar: {len(sonuc['botlar'])} adet\n"
                f"Gateway: {'✅' if sonuc['gateway_yeniden_baslatildi'] else '❌'}\n"
                f"Bağlantı: {'✅' if sonuc['baglanti_ok'] else '❌'}"
            )
        return f"✅ Mevcut provider OK: {switcher._aktif_provider}/{switcher._aktif_model}"

    elif islem == "gec":
        if not provider:
            return "[Hata]: provider adı gerekli."
        sonuc = switcher.manuel_gec(provider)
        if sonuc["gecildi"]:
            return f"✅ Geçiş yapıldı: {sonuc['yeni']['provider']}/{sonuc['yeni']['model']}"
        return f"[Hata]: {sonuc.get('hata', 'Bilinmeyen hata')}"

    elif islem == "test":
        # Bağlantı testi
        baglanti_ok = switcher._baglanti_testi()
        return f"{'✅' if baglanti_ok else '❌'} Telegram bot bağlantısı"

    else:  # durum
        return switcher.formatla()


if __name__ == "__main__":
    switcher = ModelSwitcher()
    print(switcher.formatla())
    print()
    print("--- Otomatik Kontrol ---")
    sonuc = switcher.kontrol_ve_gec()
    print(json.dumps(sonuc, indent=2, ensure_ascii=False, default=str))
