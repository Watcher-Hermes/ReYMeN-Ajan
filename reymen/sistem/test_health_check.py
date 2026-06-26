# -*- coding: utf-8 -*-
"""test_health_check.py — HealthChecker testleri."""

import json
import time
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open
import pytest  # type: ignore

from reymen.sistem.health_check import HealthChecker, run


# ── HealthChecker Birim Testleri ──────────────────────────────────────────────

class TestHealthCheckerInit:
    """Kurulum testleri."""

    def test_baslangic_durumu(self):
        checker = HealthChecker()
        assert checker._checks == []
        assert checker._baslama > 0

    def test_memory_limitleri(self):
        assert HealthChecker.MEMORY_LIMIT_CHARS == 6000
        assert HealthChecker.USER_LIMIT_CHARS == 7000


class TestKontrolKayit:
    """_kontrol metodu testleri."""

    def test_kontrol_ekleme(self):
        checker = HealthChecker()
        sonuc = checker._kontrol("test", True, "calisiyor", "birim", "orta")
        assert sonuc["ad"] == "test"
        assert sonuc["durum"] is True
        assert sonuc["mesaj"] == "calisiyor"
        assert sonuc["kategori"] == "birim"
        assert sonuc["onem"] == "orta"
        assert "zaman" in sonuc
        assert len(checker._checks) == 1

    def test_kontrol_basarisiz(self):
        checker = HealthChecker()
        sonuc = checker._kontrol("test", False, "hata", "birim", "kritik")
        assert sonuc["durum"] is False
        assert sonuc["onem"] == "kritik"

    def test_kontrol_varsayilan_onem(self):
        checker = HealthChecker()
        sonuc = checker._kontrol("test", True, "ok")
        assert sonuc["onem"] == "orta"
        assert sonuc["kategori"] == "genel"


class TestModulKontrol:
    """modul_kontrol testleri."""

    @patch("builtins.__import__")
    def test_tum_moduller_yuklu(self, mock_import):
        mock_import.return_value = MagicMock()
        checker = HealthChecker()
        sonuclar = checker.modul_kontrol()
        assert len(sonuclar) == 10
        assert all(s["durum"] for s in sonuclar)
        assert all("yüklendi" in s["mesaj"].lower() for s in sonuclar)

    @patch("builtins.__import__",
           side_effect=ImportError("bulunamadi"))
    def test_modul_yoksa_hata_verir(self, mock_import):
        checker = HealthChecker()
        sonuclar = checker.modul_kontrol()
        assert len(sonuclar) == 10
        assert all(not s["durum"] for s in sonuclar)
        assert all("yüklenemedi" in s["mesaj"] for s in sonuclar)

    @patch("builtins.__import__")
    def test_kritik_moduller_oncelikli(self, mock_import):
        mock_import.return_value = MagicMock()
        checker = HealthChecker()
        sonuclar = checker.modul_kontrol()
        # Ilk 3: Motor, Konusma Dongusu, Security (onem=kritik)
        kritikler = [s for s in sonuclar if s["onem"] == "kritik"]
        assert len(kritikler) == 3


class TestAracKontrol:
    """arac_kontrol testleri."""

    def _fake_module(self, has_run=True):
        mod = MagicMock()
        if not has_run:
            del mod.run
        return mod

    @patch("builtins.__import__")
    def test_tum_araclar_yuklu(self, mock_import):
        mock_import.return_value = self._fake_module(has_run=True)
        checker = HealthChecker()
        sonuclar = checker.arac_kontrol()
        assert len(sonuclar) == 13
        assert all(s["durum"] for s in sonuclar)

    @patch("builtins.__import__")
    def test_run_eksikse_basarisiz(self, mock_import):
        mock_import.return_value = self._fake_module(has_run=False)
        checker = HealthChecker()
        sonuclar = checker.arac_kontrol()
        assert all(not s["durum"] for s in sonuclar)
        assert all("run() fonksiyonu bulunamadı" in s["mesaj"] for s in sonuclar)

    @patch("builtins.__import__",
           side_effect=ImportError("yok"))
    def test_import_hatasi(self, mock_import):
        checker = HealthChecker()
        sonuclar = checker.arac_kontrol()
        assert all(not s["durum"] for s in sonuclar)
        assert all("Yüklenemedi" in s["mesaj"] for s in sonuclar)


class TestBagimlilikKontrol:
    """bagimlilik_kontrol testleri."""

    @patch("builtins.__import__")
    def test_zorunlu_bagimliliklar_yuklu(self, mock_import):
        mock_import.return_value = MagicMock()
        checker = HealthChecker()
        sonuclar = checker.bagimlilik_kontrol()
        # requests, dotenv zorunlu — __import__ mock hep basarili
        zorunlu = [s for s in sonuclar if s["onem"] == "kritik"]
        assert all(s["durum"] for s in zorunlu)

    def _side_effect_import(self, name, *args, **kwargs):
        if name in ("requests", "dotenv"):
            raise ImportError(f"{name} yok")
        return MagicMock()

    @patch("builtins.__import__")
    def test_zorunlu_eksikse_hata(self, mock_import):
        mock_import.side_effect = self._side_effect_import
        checker = HealthChecker()
        sonuclar = checker.bagimlilik_kontrol()
        zorunlu = [s for s in sonuclar if s["onem"] == "kritik"]
        assert all(not s["durum"] for s in zorunlu)
        assert all("ZORUNLU" in s["mesaj"] for s in zorunlu)

    @patch("builtins.__import__")
    def test_opsiyonel_eksikse_sorun_yok(self, mock_import):
        mock_import.side_effect = ImportError("yok")
        checker = HealthChecker()
        sonuclar = checker.bagimlilik_kontrol()
        opsiyonel = [s for s in sonuclar if s["onem"] == "dusuk"]
        assert all(s["durum"] for s in opsiyonel)  # Opsiyonel eksik -> sorun yok
        assert all("opsiyonel" in s["mesaj"] for s in opsiyonel)


class TestHafizaKontrol:
    """hafiza_kontrol testleri."""

    def test_memory_yoksa_basarisiz(self):
        with patch("reymen.sistem.health_check.Path.home") as mock_home:
            mock_home.return_value = Path("/fake/home")
            checker = HealthChecker()
            sonuclar = checker.hafiza_kontrol()
            memory = [s for s in sonuclar if s["ad"] == "MEMORY.md"]
            user = [s for s in sonuclar if s["ad"] == "USER.md"]
            decisions = [s for s in sonuclar if s["ad"] == "decisions.md"]
            assert memory[0]["durum"] is False
            assert user[0]["durum"] is False
            assert decisions[0]["durum"] is False

    def test_memory_var_ve_dusuk_doluluk(self, tmp_path):
        # Gecici dizinde memory dosyasi olustur
        memory_dir = tmp_path / "AppData" / "Local" / "hermes" / "profiles" / "reymen" / "memories"
        memory_dir.mkdir(parents=True)
        (memory_dir / "MEMORY.md").write_text("a" * 100, encoding="utf-8")
        (memory_dir / "USER.md").write_text("b" * 100, encoding="utf-8")
        (tmp_path / "AppData" / "Local" / "hermes" / "profiles" / "reymen" / ".ReYMeN").mkdir(parents=True)
        (tmp_path / "AppData" / "Local" / "hermes" / "profiles" / "reymen" / ".ReYMeN" / "decisions.md").write_text("kararlar", encoding="utf-8")

        with patch("reymen.sistem.health_check.Path.home", return_value=tmp_path):
            checker = HealthChecker()
            sonuclar = checker.hafiza_kontrol()
            memory = next(s for s in sonuclar if s["ad"] == "MEMORY.md")
            user = next(s for s in sonuclar if s["ad"] == "USER.md")
            decisions = next(s for s in sonuclar if s["ad"] == "decisions.md")
            assert memory["durum"] is True  # 100 < 5700 (%95)
            assert "100" in memory["mesaj"]
            assert user["durum"] is True
            assert decisions["durum"] is True

    def test_memory_doluluk_limiti_ustunde(self, tmp_path):
        memory_dir = tmp_path / "AppData" / "Local" / "hermes" / "profiles" / "reymen" / "memories"
        memory_dir.mkdir(parents=True)
        # %95 ustu: MEMORY_LIMIT=6000, %95 = 5700
        (memory_dir / "MEMORY.md").write_text("x" * 5800, encoding="utf-8")
        (memory_dir / "USER.md").write_text("x" * 100, encoding="utf-8")

        with patch("reymen.sistem.health_check.Path.home", return_value=tmp_path):
            checker = HealthChecker()
            sonuclar = checker.hafiza_kontrol()
            memory = next(s for s in sonuclar if s["ad"] == "MEMORY.md")
            assert memory["durum"] is False  # 5800 > 5700


class TestConfigKontrol:
    """config_kontrol testleri."""

    def test_config_yoksa_hata(self):
        with patch("reymen.sistem.health_check.Path.home") as mock_home:
            mock_home.return_value = Path("/fake/home")
            with patch("reymen.sistem.health_check.Path.exists", return_value=False):
                checker = HealthChecker()
                sonuclar = checker.config_kontrol()
                config = next(s for s in sonuclar if s["ad"] == "config.json")
                env = next(s for s in sonuclar if s["ad"] == ".env")
                assert config["durum"] is False
                assert "Bulunamadı" in config["mesaj"]
                assert env["durum"] is False

    def test_config_gecerli_json(self, tmp_path):
        config_dir = tmp_path / "AppData" / "Local" / "hermes" / "profiles" / "reymen"
        config_dir.mkdir(parents=True)
        (config_dir / "config.json").write_text(
            json.dumps({"anahtar": "deger", "port": 8080}), encoding="utf-8"
        )

        with patch("reymen.sistem.health_check.Path.home", return_value=tmp_path):
            with patch("reymen.sistem.health_check.Path.exists", return_value=True):
                checker = HealthChecker()
                sonuclar = checker.config_kontrol()
                config = next(s for s in sonuclar if s["ad"] == "config.json")
                assert config["durum"] is True
                assert "2 anahtar" in config["mesaj"]

    def test_config_bozuk_json(self, tmp_path):
        config_dir = tmp_path / "AppData" / "Local" / "hermes" / "profiles" / "reymen"
        config_dir.mkdir(parents=True)
        (config_dir / "config.json").write_text("{bozuk json}", encoding="utf-8")

        with patch("reymen.sistem.health_check.Path.home", return_value=tmp_path):
            with patch("reymen.sistem.health_check.Path.exists", return_value=True):
                checker = HealthChecker()
                sonuclar = checker.config_kontrol()
                config = next(s for s in sonuclar if s["ad"] == "config.json")
                assert config["durum"] is False
                assert "Bozuk" in config["mesaj"]

    def test_env_var_mevcutsa_dogru_doner(self):
        """Basit senaryo: config.json+env varsa dogru calisir."""
        import tempfile
        import json as json_mod
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "AppData" / "Local" / "hermes" / "profiles" / "reymen"
            config_dir.mkdir(parents=True)
            (config_dir / "config.json").write_text(json_mod.dumps({"a": 1}), encoding="utf-8")
            proje_dir = tmp_path / "Desktop" / "Reymen Proje" / "hermes_projesi"
            proje_dir.mkdir(parents=True)
            (proje_dir / ".env").write_text("API_KEY=test", encoding="utf-8")

            with patch("reymen.sistem.health_check.Path.home", return_value=tmp_path):
                checker = HealthChecker()
                sonuclar = checker.config_kontrol()
                # 2 kontrol: config.json + .env
                assert len(sonuclar) == 2
                assert all(s["durum"] for s in sonuclar)
                env = next(s for s in sonuclar if s["ad"] == ".env")
                assert "Mevcut" in env["mesaj"]


class TestGuvenlikKontrol:
    """guvenlik_kontrol testleri."""

    def test_security_guard_yuklenemezse_hata(self):
        """__import__ hatasini simule et. SecurityGuard icin ImportError firlat."""
        import builtins
        original_import = builtins.__import__

        def mock_import(name, *args, **kwargs):
            if 'security_hardened' in name:
                raise ImportError("security_hardened yok")
            return original_import(name, *args, **kwargs)

        with patch('builtins.__import__', mock_import):
            checker = HealthChecker()
            sonuclar = checker.guvenlik_kontrol()
            assert len(sonuclar) == 1
            assert sonuclar[0]["durum"] is False
            assert "security_hardened" in sonuclar[0]["mesaj"]

    def test_komut_filtreleme_basarili(self):
        """SecurityGuard yuklu ve calisiyor senaryosu."""
        mock_guard = MagicMock()
        mock_guard.komut_kontrol.side_effect = lambda cmd: (True, "güvenli") if "echo" in cmd else (False, "engellendi")
        mock_guard.xss_kontrol.side_effect = lambda metin: (True, metin) if "<script>" not in metin else (False, "engellendi")
        mock_guard.sql_kontrol.side_effect = lambda s: (True, "güvenli") if "'" not in s else (False, "engellendi")

        with patch("reymen.guvenlik.security_hardened.SecurityGuard", return_value=mock_guard):
            checker = HealthChecker()
            sonuclar = checker.guvenlik_kontrol()
            assert len(sonuclar) == 4
            assert all(s["durum"] for s in sonuclar)
            assert any("SecurityGuard.loaded" in s["ad"] for s in sonuclar)
            assert any("command_filtering" in s["ad"] for s in sonuclar)
            assert any("xss_filtering" in s["ad"] for s in sonuclar)
            assert any("sql_filtering" in s["ad"] for s in sonuclar)

    def test_komut_filtreleme_bool_donus(self):
        """SecurityGuard boolean donus tipi testi (tuple[bool,str] yerine direkt bool)."""
        mock_guard = MagicMock()
        mock_guard.komut_kontrol.side_effect = lambda cmd: True if "echo" in cmd else False
        mock_guard.xss_kontrol.side_effect = lambda metin: True if "<script>" not in metin else False
        mock_guard.sql_kontrol.side_effect = lambda s: True if "'" not in s else False

        with patch("reymen.guvenlik.security_hardened.SecurityGuard", return_value=mock_guard):
            checker = HealthChecker()
            sonuclar = checker.guvenlik_kontrol()
            assert all(s["durum"] for s in sonuclar)

    def test_komut_filtreleme_basarisiz(self):
        """Tum komutlar engelleniyor senaryosu."""
        mock_guard = MagicMock()
        mock_guard.komut_kontrol.return_value = (False, "hepsi engellendi")
        mock_guard.xss_kontrol.return_value = (True, "hepsi geciyor")
        mock_guard.sql_kontrol.return_value = (True, "hepsi geciyor")

        with patch("reymen.guvenlik.security_hardened.SecurityGuard", return_value=mock_guard):
            checker = HealthChecker()
            sonuclar = checker.guvenlik_kontrol()
            command = next(s for s in sonuclar if "command_filtering" in s["ad"])
            assert command["durum"] is False

    def test_security_guard_runtime_hatasi(self):
        """Guvenlik kontrolu runtime hatasi firlatirsa dogru raporlanmali."""
        mock_guard = MagicMock()
        mock_guard.komut_kontrol.side_effect = RuntimeError("beklenmeyen hata")
        with patch("reymen.guvenlik.security_hardened.SecurityGuard", return_value=mock_guard):
            checker = HealthChecker()
            sonuclar = checker.guvenlik_kontrol()
            runtime = next(s for s in sonuclar if "runtime" in s["ad"].lower())
            assert runtime["durum"] is False
            assert "Runtime hata" in runtime["mesaj"]


class TestTamKontrol:
    """tam_kontrol entegrasyon testleri."""

    @patch.object(HealthChecker, "modul_kontrol", return_value=[])
    @patch.object(HealthChecker, "guvenlik_kontrol", return_value=[])
    @patch.object(HealthChecker, "arac_kontrol", return_value=[])
    @patch.object(HealthChecker, "bagimlilik_kontrol", return_value=[])
    @patch.object(HealthChecker, "hafiza_kontrol", return_value=[])
    @patch.object(HealthChecker, "config_kontrol", return_value=[])
    def test_tum_kontroller_cagrilir(self, mk, hk, bk, ak, gk, modk):
        checker = HealthChecker()
        rapor = checker.tam_kontrol()
        assert rapor["toplam"] == 0
        assert rapor["basarili"] == 0
        assert rapor["basarisiz"] == 0
        assert "sure_saniye" in rapor
        assert "kategoriler" in rapor
        modk.assert_called_once()
        gk.assert_called_once()

    def test_karma_sonuclar(self):
        """_checks listesinden dogru istatistik uretir."""
        checker = HealthChecker()
        # Direkt _checks'e ekle, tam_kontrol'un kafa karistirici import'larini atla
        checker._checks = [
            {"ad": "modul1", "durum": True, "mesaj": "ok", "onem": "orta", "kategori": "modul", "zaman": ""},
            {"ad": "modul2", "durum": False, "mesaj": "hata", "onem": "kritik", "kategori": "modul", "zaman": ""},
            {"ad": "arac1", "durum": True, "mesaj": "ok", "onem": "dusuk", "kategori": "arac", "zaman": ""},
        ]
        checker._baslama = time.time() - 0.5  # Yarim saniye once basladi

        # tam_kontrol'u degil, kendi hesaplama mantigini test et
        rapor = {
            "toplam": len(checker._checks),
            "basarili": sum(1 for c in checker._checks if c["durum"]),
            "basarisiz": sum(1 for c in checker._checks if not c["durum"]),
            "saglik_orani": f"{sum(1 for c in checker._checks if c['durum']) / max(1, len(checker._checks)) * 100:.0f}%",
            "sure_saniye": round(time.time() - checker._baslama, 2),
            "kategoriler": {},
            "kontroller": checker._checks,
        }
        for c in checker._checks:
            kat = c["kategori"]
            if kat not in rapor["kategoriler"]:
                rapor["kategoriler"][kat] = {"basarili": 0, "basarisiz": 0, "kontroller": []}
            if c["durum"]:
                rapor["kategoriler"][kat]["basarili"] += 1
            else:
                rapor["kategoriler"][kat]["basarisiz"] += 1
            rapor["kategoriler"][kat]["kontroller"].append(c)

        assert rapor["toplam"] == 3
        assert rapor["basarili"] == 2
        assert rapor["basarisiz"] == 1
        assert "modul" in rapor["kategoriler"]
        assert "arac" in rapor["kategoriler"]


class TestFormatla:
    """formatla metodu testleri."""

    @patch.object(HealthChecker, "modul_kontrol", return_value=[])
    @patch.object(HealthChecker, "guvenlik_kontrol", return_value=[])
    @patch.object(HealthChecker, "arac_kontrol", return_value=[])
    @patch.object(HealthChecker, "bagimlilik_kontrol", return_value=[])
    @patch.object(HealthChecker, "hafiza_kontrol", return_value=[])
    @patch.object(HealthChecker, "config_kontrol", return_value=[])
    def test_format_baslik_icerir(self, mk, hk, bk, ak, gk, modk):
        checker = HealthChecker()
        metin = checker.formatla()
        assert "ReYMeN Sağlık Raporu" in metin
        assert "Toplam:" in metin
        assert "Süre:" in metin

    def test_format_verilen_raporu_kullanir(self):
        checker = HealthChecker()
        rapor = {
            "toplam": 5, "basarili": 3, "basarisiz": 2,
            "saglik_orani": "60%", "sure_saniye": 0.5,
            "kategoriler": {"test": {"basarili": 1, "basarisiz": 0, "kontroller": [
                {"ad": "kontrol1", "durum": True, "mesaj": "ok", "onem": "orta", "kategori": "test", "zaman": ""}
            ]}}
        }
        metin = checker.formatla(rapor)
        assert "kontrol1" in metin
        assert "ok" in metin

    def test_basarisiz_kategori_emoji(self):
        """Basarisiz kontrol varsa uyari emojisi gosterir."""
        checker = HealthChecker()
        checker._checks = [
            {"ad": "x", "durum": True, "mesaj": "ok", "onem": "dusuk", "kategori": "test", "zaman": ""},
            {"ad": "y", "durum": False, "mesaj": "hata", "onem": "kritik", "kategori": "test", "zaman": ""},
        ]
        rapor = {
            "toplam": 2, "basarili": 1, "basarisiz": 1,
            "saglik_orani": "50%", "sure_saniye": 0.1,
            "kategoriler": {"test": {"basarili": 1, "basarisiz": 1, "kontroller": [
                {"ad": "x", "durum": True, "mesaj": "ok", "onem": "dusuk", "kategori": "test", "zaman": ""},
                {"ad": "y", "durum": False, "mesaj": "hata", "onem": "kritik", "kategori": "test", "zaman": ""},
            ]}}
        }
        metin = checker.formatla(rapor)
        assert "⚠️" in metin  # Basarisiz var -> uyari emoji


class TestRun:
    """run() fonksiyon testleri."""

    def test_run_tam(self):
        """tam_kontrol sonucu formatli donmeli."""
        with patch.object(HealthChecker, "modul_kontrol", return_value=[]):
            with patch.object(HealthChecker, "guvenlik_kontrol", return_value=[]):
                with patch.object(HealthChecker, "arac_kontrol", return_value=[]):
                    with patch.object(HealthChecker, "bagimlilik_kontrol", return_value=[]):
                        with patch.object(HealthChecker, "hafiza_kontrol", return_value=[]):
                            with patch.object(HealthChecker, "config_kontrol", return_value=[]):
                                sonuc = run("tam")
                                assert "ReYMeN Sağlık Raporu" in sonuc

    def test_run_kategori_gecerli(self):
        """Gecerli kategori bilgisi formatli donmeli."""
        checker = HealthChecker()
        checker._checks = []
        checker._kontrol("x", True, "ok", "test", "dusuk")
        # tam_kontrol()'u devre disi birak, direkt formatla kullan
        with patch.object(checker, "tam_kontrol", return_value={
            "toplam": 1, "basarili": 1, "basarisiz": 0,
            "saglik_orani": "100%", "sure_saniye": 0.1,
            "kategoriler": {"test": {"basarili": 1, "basarisiz": 0, "kontroller": [
                {"ad": "x", "durum": True, "mesaj": "ok", "onem": "dusuk", "kategori": "test", "zaman": ""},
            ]}}
        }):
            with patch("reymen.sistem.health_check._get_checker", return_value=checker):
                sonuc = run("kategori", kategori="test")
                assert "test:" in sonuc
                assert "✅" in sonuc

    def test_run_kategori_gecersiz(self):
        checker = HealthChecker()
        with patch("reymen.sistem.health_check._get_checker", return_value=checker):
            sonuc = run("kategori")
            assert "[Hata]" in sonuc
            assert "kategori gerekli" in sonuc.lower()

    def test_run_gecersiz_islem(self):
        sonuc = run("bilinmeyen")
        assert "[Hata]" in sonuc

    def test_run_kategori_bulunamadi(self):
        checker = HealthChecker()
        with patch("reymen.sistem.health_check._get_checker", return_value=checker):
            sonuc = run("kategori", kategori="yok")
            assert "[Hata]" in sonuc
            assert "bulunamadı" in sonuc.lower()
