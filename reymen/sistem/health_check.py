# -*- coding: utf-8 -*-
"""
health_check.py — Sistem sağlık kontrolü.

ReYMeN'in tüm bileşenlerini kontrol eder: modüller, araçlar,
hafıza, güvenlik, konfigürasyon, bağımlılıklar.

Kullanım:
    from reymen.sistem.health_check import HealthChecker
    checker = HealthChecker()
    rapor = checker.tam_kontrol()
"""

import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime


class HealthChecker:
    """Sistem sağlık kontrolcüsü."""

    # Bellek limitleri (karakter) — sağlıklı doluluk <%95
    MEMORY_LIMIT_CHARS = 6000   # MEMORY.md
    USER_LIMIT_CHARS = 7000     # USER.md

    def __init__(self):
        self._checks: List[Dict] = []
        self._baslama = time.time()

    def _kontrol(self, ad: str, durum: bool, mesaj: str,
                 kategori: str = "genel", onem: str = "orta") -> Dict:
        """Tek bir kontrolü kaydeder."""
        kayit = {
            "ad": ad,
            "durum": durum,
            "mesaj": mesaj,
            "kategori": kategori,
            "onem": onem,
            "zaman": datetime.now().isoformat(),
        }
        self._checks.append(kayit)
        return kayit

    # ── Modül Kontrolleri ────────────────────────────────────────────────────

    def modul_kontrol(self) -> List[Dict]:
        """Tüm kritik modülleri kontrol eder."""
        sonuclar = []

        moduller = [
            ("reymen.cereyan.motor", "Motor", "kritik"),
            ("reymen.cereyan.conversation_loop", "Konuşma Döngüsü", "kritik"),
            ("reymen.cereyan.closed_learning_loop", "Öğrenme Döngüsü", "orta"),
            ("reymen.cereyan.prompt_assembly", "Prompt Assembly", "orta"),
            ("reymen.hafiza.session_db", "Session DB", "orta"),
            ("reymen.hafiza.bounded_memory", "Bounded Memory", "orta"),
            ("reymen.sistem.ReYMeN_logging", "Logging", "orta"),
            ("reymen.sistem.config_manager", "Config Manager", "orta"),
            ("reymen.sistem.lazy_loader", "Lazy Loader", "orta"),
            ("reymen.guvenlik.security_hardened", "Security", "kritik"),
        ]

        for modul_ad, aciklama, onem in moduller:
            try:
                __import__(modul_ad)
                sonuclar.append(self._kontrol(
                    aciklama, True, f"{modul_ad} yüklendi", "modul", onem
                ))
            except ImportError as e:
                sonuclar.append(self._kontrol(
                    aciklama, False, f"{modul_ad} yüklenemedi: {e}", "modul", onem
                ))

        return sonuclar

    # ── Araç Kontrolleri ─────────────────────────────────────────────────────

    def arac_kontrol(self) -> List[Dict]:
        """Tüm araçları kontrol eder."""
        sonuclar = []

        araclar = [
            ("reymen.arac.web_extract_tool", "Web Extract"),
            ("reymen.arac.vision_analyze_tool", "Vision Analyze"),
            ("reymen.arac.image_generate_tool", "Image Generate"),
            ("reymen.arac.todo_tool", "Todo"),
            ("reymen.arac.process_tool", "Process"),
            ("reymen.arac.file_ops_tool", "File Ops"),
            ("reymen.arac.cron_tool", "Cron"),
            ("reymen.arac.memory_batch_tool", "Memory Batch"),
            ("reymen.arac.profile_tool", "Profile"),
            ("reymen.arac.approval_tool", "Approval"),
            ("reymen.arac.multi_platform_tool", "Multi Platform"),
            ("reymen.arac.browser_mcp_tool", "Browser MCP"),
            ("reymen.arac.powershell_tool", "PowerShell"),
        ]

        for modul_ad, aciklama in araclar:
            try:
                mod = __import__(modul_ad, fromlist=["run"])
                if hasattr(mod, "run"):
                    sonuclar.append(self._kontrol(
                        aciklama, True, "run() fonksiyonu mevcut", "arac", "orta"
                    ))
                else:
                    sonuclar.append(self._kontrol(
                        aciklama, False, "run() fonksiyonu bulunamadı", "arac", "orta"
                    ))
            except ImportError as e:
                sonuclar.append(self._kontrol(
                    aciklama, False, f"Yüklenemedi: {e}", "arac", "orta"
                ))

        return sonuclar

    # ── Bağımlılık Kontrolleri ───────────────────────────────────────────────

    def bagimlilik_kontrol(self) -> List[Dict]:
        """Kritik bağımlılıkları kontrol eder."""
        sonuclar = []

        bagimliliklar = [
            ("requests", "HTTP İstekleri", True),
            ("dotenv", "Ortam Değişkenleri", True),
            ("PIL", "Görsel İşleme", False),
            ("playwright", "Tarayıcı Otomasyonu", False),
            ("easyocr", "OCR", False),
            ("bs4", "HTML Parsing", False),
            ("lxml", "XML/HTML Parsing", False),
            ("fal_client", "FAL.ai Görsel Üretme", False),
            ("openai", "OpenAI API", False),
            ("numpy", "Sayısal Hesaplama", False),
        ]

        for modul_ad, aciklama, zorunlu in bagimliliklar:
            try:
                __import__(modul_ad)
                sonuclar.append(self._kontrol(
                    aciklama, True, "Yüklü", "bagimlilik", "kritik" if zorunlu else "dusuk"
                ))
            except ImportError:
                durum = not zorunlu  # Zorunlu değilse True (sorun yok)
                mesaj = "Yüklü değil (opsiyonel)" if not zorunlu else "Yüklü değil (ZORUNLU)"
                sonuclar.append(self._kontrol(
                    aciklama, durum, mesaj, "bagimlilik", "kritik" if zorunlu else "dusuk"
                ))

        return sonuclar

    # ── Hafıza Kontrolleri ───────────────────────────────────────────────────

    def hafiza_kontrol(self) -> List[Dict]:
        """Hafıza sistemini kontrol eder."""
        sonuclar = []

        # MEMORY.md
        memory_path = Path.home() / "AppData" / "Local" / "hermes" / "profiles" / "reymen" / "memories" / "MEMORY.md"
        if memory_path.exists():
            boyut = memory_path.stat().st_size
            limit = self.MEMORY_LIMIT_CHARS
            doluluk = boyut / limit * 100
            durum = doluluk < 95
            sonuclar.append(self._kontrol(
                "MEMORY.md", durum,
                f"{boyut}/{limit} karakter ({doluluk:.0f}%)",
                "hafiza", "orta"
            ))
        else:
            sonuclar.append(self._kontrol(
                "MEMORY.md", False, "Bulunamadı", "hafiza", "orta"
            ))

        # USER.md
        user_path = Path.home() / "AppData" / "Local" / "hermes" / "profiles" / "reymen" / "memories" / "USER.md"
        if user_path.exists():
            boyut = user_path.stat().st_size
            limit = self.USER_LIMIT_CHARS
            doluluk = boyut / limit * 100
            durum = doluluk < 95
            sonuclar.append(self._kontrol(
                "USER.md", durum,
                f"{boyut}/{limit} karakter ({doluluk:.0f}%)",
                "hafiza", "orta"
            ))
        else:
            sonuclar.append(self._kontrol(
                "USER.md", False, "Bulunamadı", "hafiza", "orta"
            ))

        # decisions.md
        decisions_path = Path.home() / "AppData" / "Local" / "hermes" / "profiles" / "reymen" / ".ReYMeN" / "decisions.md"
        if decisions_path.exists():
            sonuclar.append(self._kontrol(
                "decisions.md", True, "Mevcut", "hafiza", "dusuk"
            ))
        else:
            sonuclar.append(self._kontrol(
                "decisions.md", False, "Bulunamadı (oluşturulacak)", "hafiza", "dusuk"
            ))

        return sonuclar

    # ── Yapılandırma Kontrolleri ─────────────────────────────────────────────

    def config_kontrol(self) -> List[Dict]:
        """Yapılandırma dosyasını kontrol eder."""
        sonuclar = []

        config_path = Path.home() / "AppData" / "Local" / "hermes" / "profiles" / "reymen" / "config.json"
        if config_path.exists():
            try:
                import json
                data = json.loads(config_path.read_text(encoding="utf-8"))
                sonuclar.append(self._kontrol(
                    "config.json", True,
                    f"{len(data)} anahtar yüklendi",
                    "config", "orta"
                ))
            except Exception as e:
                sonuclar.append(self._kontrol(
                    "config.json", False, f"Bozuk: {e}", "config", "orta"
                ))
        else:
            sonuclar.append(self._kontrol(
                "config.json", False, "Bulunamadı (varsayılan kullanılacak)", "config", "orta"
            ))

        # .env kontrolü
        env_path = Path.home() / "Desktop" / "Reymen Proje" / "hermes_projesi" / ".env"
        if env_path.exists():
            sonuclar.append(self._kontrol(
                ".env", True, "Mevcut", "config", "orta"
            ))
        else:
            sonuclar.append(self._kontrol(
                ".env", False, "Bulunamadı", "config", "orta"
            ))

        return sonuclar

    # ── Tam Kontrol ──────────────────────────────────────────────────────────

    def tam_kontrol(self) -> Dict[str, Any]:
        """Tüm kontrolleri çalıştırır."""
        self._checks = []
        self._baslama = time.time()

        # Kontrolleri çalıştır
        self.modul_kontrol()
        self.arac_kontrol()
        self.bagimlilik_kontrol()
        self.hafiza_kontrol()
        self.config_kontrol()

        # İstatistikler
        toplam = len(self._checks)
        basarili = sum(1 for c in self._checks if c["durum"])
        basarisiz = toplam - basarili
        sure = time.time() - self._baslama

        # Kategorilere göre grupla
        kategoriler = {}
        for c in self._checks:
            kat = c["kategori"]
            if kat not in kategoriler:
                kategoriler[kat] = {"basarili": 0, "basarisiz": 0, "kontroller": []}
            if c["durum"]:
                kategoriler[kat]["basarili"] += 1
            else:
                kategoriler[kat]["basarisiz"] += 1
            kategoriler[kat]["kontroller"].append(c)

        return {
            "toplam": toplam,
            "basarili": basarili,
            "basarisiz": basarisiz,
            "saglik_orani": f"{basarili / max(1, toplam) * 100:.0f}%",
            "sure_saniye": round(sure, 2),
            "kategoriler": kategoriler,
            "kontroller": self._checks,
        }

    def formatla(self, rapor: Optional[Dict] = None) -> str:
        """Raporu okunabilir format döner."""
        if rapor is None:
            rapor = self.tam_kontrol()

        satirlar = [
            f"🏥 ReYMeN Sağlık Raporu",
            f"{'=' * 50}",
            f"📊 Toplam: {rapor['toplam']} | ✅ {rapor['basarili']} | ❌ {rapor['basarisiz']} | 🏥 {rapor['saglik_orani']}",
            f"⏱️ Süre: {rapor['sure_saniye']}s",
            "",
        ]

        for kat, bilgi in rapor["kategoriler"].items():
            emoji = "✅" if bilgi["basarisiz"] == 0 else "⚠️"
            satirlar.append(f"{emoji} {kat.upper()} ({bilgi['basarili']}/{bilgi['basarili'] + bilgi['basarisiz']}):")
            for c in bilgi["kontroller"]:
                durum = "✅" if c["durum"] else "❌"
                onem = {"kritik": "🔴", "orta": "🟡", "dusuk": "🟢"}.get(c["onem"], "")
                satirlar.append(f"  {durum} {onem} {c['ad']}: {c['mesaj']}")
            satirlar.append("")

        return "\n".join(satirlar)


# ── Motor Entegrasyonu ───────────────────────────────────────────────────────

_checker = None

def _get_checker() -> HealthChecker:
    global _checker
    if _checker is None:
        _checker = HealthChecker()
    return _checker


def run(islem: str = "tam", kategori: str = "") -> str:
    """Motor entegrasyonu."""
    checker = _get_checker()

    if islem == "tam":
        return checker.formatla()

    elif islem == "kategori":
        if not kategori:
            return "[Hata]: kategori gerekli."
        rapor = checker.tam_kontrol()
        kat = rapor["kategoriler"].get(kategori)
        if not kat:
            return f"[Hata]: Kategori bulunamadı: {kategori}"
        return f"{kategori}: {kat['basarili']}✅ {kat['basarisiz']}❌"

    return f"[Hata]: Bilinmeyen islem: {islem}"


if __name__ == "__main__":
    checker = HealthChecker()
    print(checker.formatla())
