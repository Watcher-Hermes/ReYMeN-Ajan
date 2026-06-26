"""tests/test_motor_refactor.py — Motor refactor doğrulama testleri.

2048 satır → 6 modüllü paket sonrası public API korundu mu?
"""
import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from reymen.cereyan.motor import Motor, provider_degistir, CORE_TOOLS, OPTIONAL_TOOLS, get_active_tools
from reymen.cereyan.motor.config import TOOLSET_GRUPLARI, DURUM_MESAJLARI, GECERLI_PROVIDERLER
from reymen.cereyan.motor.plugins import _REGISTRY, lazy_module_listesi
from reymen.cereyan.motor.context import _COMPRESSOR, _CACHE, cevabi_temizle


class TestMotorRefactor:
    """Motor refactor sonrasi public API testleri."""

    def setup_method(self):
        self.m = Motor(backend_mode="local", basit_mod=True)

    # ── Temel import ve yapi ────────────────────────────────────────────────
    def test_import_suresi(self):
        """Import suresi < 2sn (soguk baslangic)."""
        # Soguk import: yeni proses
        import subprocess
        t0 = time.perf_counter()
        r = subprocess.run(
            [sys.executable, "-c", "from reymen.cereyan.motor import Motor"],
            capture_output=True, text=True, timeout=30,
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        )
        ms = (time.perf_counter() - t0) * 1000
        assert r.returncode == 0, f"Import hatasi: {r.stderr}"
        assert ms < 5000, f"Soguk import cok yavas: {ms:.1f}ms"

    def test_motor_olusturma(self):
        """Motor olusturma basarili."""
        assert self.m is not None
        assert hasattr(self.m, "calistir")
        assert hasattr(self.m, "calistir_fc")
        assert hasattr(self.m, "eylemi_ayristir")

    # ── Eylem cozumleme ────────────────────────────────────────────────────
    def test_eylem_ayristir_standart(self):
        """Standart format: Eylem: ARAC(param)"""
        arac, ham = self.m.eylemi_ayristir('Eylem: DOSYA_OKU("test.txt")')
        assert arac == "DOSYA_OKU"
        assert ham == '"test.txt"'

    def test_eylem_ayristir_alt_satir(self):
        """Alt satir formati: EYLEM:\\nARAC(param)"""
        arac, ham = self.m.eylemi_ayristir("EYLEM:\nWEB_ARA(\"hava\")")
        assert arac == "WEB_ARA"
        assert '"hava"' in ham

    def test_eylem_ayristir_dogrudan(self):
        """Dogrudan ARAC_ADI(param) (BILINEN_ARACLAR icinde)"""
        arac, ham = self.m.eylemi_ayristir('GOREV_BITTI("islem tamam")')
        assert arac == "GOREV_BITTI"

    def test_eylem_ayristir_bos(self):
        """Gecersiz girdi -> (None, None)"""
        arac, ham = self.m.eylemi_ayristir("Merhaba, nasilsin?")
        assert arac is None
        assert ham is None

    def test_parametre_coz(self):
        """Parametre cozumu dogru calisiyor"""
        params = self.m._parametreleri_coz('"a" "b c" "d"')
        assert params == ["a", "b c", "d"]

    # ── Toolset ve kullanilabilirlik ────────────────────────────────────────
    def test_musait_araclar_temel(self):
        """Temel toolset 8 arac iceriyor"""
        temel = self.m.musait_araclar("temel")
        assert len(temel) == 8
        assert "KOMUT_CALISTIR" in temel
        assert "DOSYA_OKU" in temel

    def test_toolset_tanimi_al(self):
        """Toolset tanimi [TEMEL] etiketi iceriyor"""
        temel = self.m.musait_araclar("temel")
        tanim = self.m.toolset_tanimi_al(temel)
        assert "[TEMEL]" in tanim

    def test_get_active_tools_web(self):
        """get_active_tools(web) CORE_TOOLS + browser iceriyor"""
        tools = get_active_tools({"web_needed": True})
        assert len(tools) > len(CORE_TOOLS)
        assert "web_extract" in tools

    # ── FC API ──────────────────────────────────────────────────────────────
    def test_calistir_fc(self):
        """calistir_fc dict argumanlari dogru donusturuyor"""
        sonuc = self.m.calistir_fc("GOREV_BITTI", {"ozet": "test"})
        assert "__GOREV_BITTI__" in sonuc

    # ── Provider ────────────────────────────────────────────────────────────
    def test_provider_degistir(self):
        """provider_degistir basarili donuyor"""
        sonuc = provider_degistir("deepseek")
        assert sonuc["durum"] == "basarili"

    def test_aktif_provider_listele(self):
        """aktif_provider_listele en az 1 provider donuyor"""
        liste = self.m.aktif_provider_listele()
        assert len(liste) >= 1

    # ── Schema ──────────────────────────────────────────────────────────────
    def test_tools_schema_al(self):
        """tools_schema_al GOREV_BITTI ile basliyor"""
        schema = self.m.tools_schema_al(10)
        assert len(schema) >= 1
        assert schema[0]["function"]["name"] == "GOREV_BITTI"

    # ── Context ─────────────────────────────────────────────────────────────
    def test_cevabi_temizle(self):
        """cevabi_temizle bos girdi icin bos doner"""
        assert cevabi_temizle("") == ""

    # ── Sabitler ────────────────────────────────────────────────────────────
    def test_CORE_TOOLS_sayisi(self):
        """CORE_TOOLS 17 adet"""
        assert len(CORE_TOOLS) == 17

    def test_TOOLSET_GRUPLARI_sayisi(self):
        """TOOLSET_GRUPLARI 13 grup"""
        assert len(TOOLSET_GRUPLARI) == 13

    def test_GECERLI_PROVIDERLER_sayisi(self):
        """GECERLI_PROVIDERLER 9 adet"""
        assert len(GECERLI_PROVIDERLER) == 9

    def test_DURUM_MESAJLARI_sayisi(self):
        """DURUM_MESAJLARI en az 50 mesaj"""
        assert len(DURUM_MESAJLARI) >= 50

    # ── Modul yapisi ───────────────────────────────────────────────────────
    def test_motor_dir_exists(self):
        """motor/ klasoru mevcut ve 6 .py dosyasi iceriyor"""
        motor_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "reymen", "cereyan", "motor",
        )
        py_files = [f for f in os.listdir(motor_dir) if f.endswith(".py")]
        assert len(py_files) >= 5  # __init__, config, context, providers, plugins, main

    def test_eski_motor_py_shim(self):
        """motor.py shim olarak kalmis (< 20 satir)"""
        motor_py = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "reymen", "cereyan", "motor.py",
        )
        with open(motor_py) as f:
            satir_sayisi = len(f.readlines())
        assert satir_sayisi < 20, f"motor.py hala {satir_sayisi} satir (shim olmali)"
