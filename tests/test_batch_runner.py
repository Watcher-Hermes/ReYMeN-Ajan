"""Tests for reymen/sistem/batch_runner.py — parallel batch task runner."""
import json
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


class TestSonucYoneticisi:
    """SonucYoneticisi class tests."""

    def setup_method(self):
        from reymen.sistem.batch_runner import SonucYoneticisi
        self.tmpdir = tempfile.mkdtemp()
        self.cikti = Path(self.tmpdir) / "batch.jsonl"

    def test_init_creates_empty_state(self):
        from reymen.sistem.batch_runner import SonucYoneticisi
        sy = SonucYoneticisi(self.cikti)
        ozet = sy.ozet()
        assert ozet["toplam"] == 0
        assert ozet["basarili"] == 0
        assert ozet["basarisiz"] == 0

    def test_kaydet_basarili(self):
        from reymen.sistem.batch_runner import SonucYoneticisi
        sy = SonucYoneticisi(self.cikti)
        sy.kaydet("g1", "hedef1", "sonuc1", 1.5)
        ozet = sy.ozet()
        assert ozet["toplam"] == 1
        assert ozet["basarili"] == 1

    def test_kaydet_basarisiz(self):
        from reymen.sistem.batch_runner import SonucYoneticisi
        sy = SonucYoneticisi(self.cikti)
        sy.kaydet("g2", "hedef2", None, 0.5)
        ozet = sy.ozet()
        assert ozet["toplam"] == 1
        assert ozet["basarisiz"] == 1
        assert ozet["basarili"] == 0

    def test_jsonl_yazma(self):
        from reymen.sistem.batch_runner import SonucYoneticisi
        sy = SonucYoneticisi(self.cikti)
        sy.kaydet("g3", "h3", "ok", 1.0)
        lines = self.cikti.read_text(encoding="utf-8").strip().split("\n")
        assert len(lines) == 1
        data = json.loads(lines[0])
        assert data["id"] == "g3"
        assert data["basarili"] is True

    def test_tamamlanan_ids_takip(self):
        from reymen.sistem.batch_runner import SonucYoneticisi
        sy = SonucYoneticisi(self.cikti)
        sy.kaydet("g4", "h4", "ok", 1.0)
        sy.kaydet("g5", "h5", None, 2.0)
        assert sy.zaten_tamamlandi_mi("g4") is True
        assert sy.zaten_tamamlandi_mi("g5") is False

    def test_checkpoint_kaydetve_yukle(self):
        from reymen.sistem.batch_runner import SonucYoneticisi
        sy1 = SonucYoneticisi(self.cikti)
        sy1.kaydet("g6", "h6", "ok", 1.0)
        # Create new instance — should load checkpoint
        sy2 = SonucYoneticisi(self.cikti)
        assert sy2.zaten_tamamlandi_mi("g6") is True

    def test_coklu_kayit(self):
        from reymen.sistem.batch_runner import SonucYoneticisi
        sy = SonucYoneticisi(self.cikti)
        for i in range(10):
            sy.kaydet(f"g{i}", f"h{i}", "ok" if i % 2 == 0 else None, 0.1)
        ozet = sy.ozet()
        assert ozet["toplam"] == 10
        assert ozet["basarili"] == 5
        assert ozet["basarisiz"] == 5


class TestHedefleriYukle:
    """hedefleri_yukle() function tests."""

    def setup_method(self):
        self.tmpdir = tempfile.mkdtemp()

    def test_txt_basit(self):
        from reymen.sistem.batch_runner import hedefleri_yukle
        p = Path(self.tmpdir) / "hedefler.txt"
        p.write_text("hedef1\nhedef2\nhedef3\n", encoding="utf-8")
        result = hedefleri_yukle(p)
        assert len(result) == 3
        assert result[0]["hedef"] == "hedef1"

    def test_txt_bos_satir_comment(self):
        from reymen.sistem.batch_runner import hedefleri_yukle
        p = Path(self.tmpdir) / "hedefler.txt"
        p.write_text("hedef1\n\n# yorum\nhedef2\n", encoding="utf-8")
        result = hedefleri_yukle(p)
        assert len(result) == 2

    def test_jsonl_format(self):
        from reymen.sistem.batch_runner import hedefleri_yukle
        p = Path(self.tmpdir) / "hedefler.jsonl"
        p.write_text(
            '{"id": "j1", "hedef": "gorev1"}\n'
            '{"id": "j2", "hedef": "gorev2"}\n',
            encoding="utf-8"
        )
        result = hedefleri_yukle(p)
        assert len(result) == 2
        assert result[0]["id"] == "j1"
        assert result[1]["hedef"] == "gorev2"

    def test_jsonl_goal_field(self):
        from reymen.sistem.batch_runner import hedefleri_yukle
        p = Path(self.tmpdir) / "hedefler.jsonl"
        p.write_text('{"goal": "yap"}\n', encoding="utf-8")
        result = hedefleri_yukle(p)
        assert result[0]["hedef"] == "yap"

    def test_txt_id_otomatik(self):
        from reymen.sistem.batch_runner import hedefleri_yukle
        p = Path(self.tmpdir) / "hedefler.txt"
        p.write_text("bir\niki\n", encoding="utf-8")
        result = hedefleri_yukle(p)
        assert result[0]["id"] == "gorev-0"
        assert result[1]["id"] == "gorev-1"
