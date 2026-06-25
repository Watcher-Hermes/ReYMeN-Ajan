# -*- coding: utf-8 -*-
"""test_checkpoint_manager.py — CheckpointManager testleri."""

import json
import os
import sys
import tempfile
import time
from pathlib import Path
from unittest.mock import patch

import pytest

# Project root
_root = str(Path(__file__).resolve().parent.parent)
if _root not in sys.path:
    sys.path.insert(0, _root)

from reymen.sistem.checkpoint_manager import CheckpointManager


@pytest.fixture
def tmp_ckpt_dir(tmp_path):
    """Use a temporary checkpoint directory."""
    with patch("reymen.sistem.checkpoint_manager.CHECKPOINT_DIR", tmp_path):
        yield tmp_path


@pytest.fixture
def mgr(tmp_ckpt_dir):
    return CheckpointManager()


class TestKaydet:
    def test_returns_ckpt_id(self, mgr):
        cid = mgr.kaydet("gorev-1", 1, {"adim": "a"})
        assert cid.startswith("ckpt_")

    def test_creates_json_file(self, mgr, tmp_ckpt_dir):
        cid = mgr.kaydet("gorev-2", 3, {"x": 1})
        f = tmp_ckpt_dir / f"{cid}.json"
        assert f.exists()
        data = json.loads(f.read_text(encoding="utf-8"))
        assert data["hedef"] == "gorev-2"
        assert data["tur"] == 3
        assert data["durum"] == {"x": 1}

    def test_son_kayit_guncellenir(self, mgr):
        cid = mgr.kaydet("hedef", 1, {})
        assert mgr._son_kayit == cid


class TestYukle:
    def test_var_olan_checkpoint(self, mgr):
        cid = mgr.kaydet("test", 5, {"k": "v"})
        veri = mgr.yukle(cid)
        assert veri is not None
        assert veri["tur"] == 5

    def test_olmayan_checkpoint(self, mgr):
        assert mgr.yukle("ckpt_9999999999") is None

    def test_bozuk_json(self, mgr, tmp_ckpt_dir):
        f = tmp_ckpt_dir / "ckpt_broken.json"
        f.write_text("{bad json", encoding="utf-8")
        assert mgr.yukle("ckpt_broken") is None


class TestSonCheckpoint:
    def test_son_kayit_varsa_o_doner(self, mgr):
        cid1 = mgr.kaydet("birinci", 1, {})
        cid2 = mgr.kaydet("ikinci", 2, {})
        son = mgr.son_chekpoint()
        assert son["hedef"] == "ikinci"
        assert son["tur"] == 2

    def test_son_kayit_yoksa_dosyalardan(self, mgr):
        mgr2 = CheckpointManager()
        mgr2.kaydet("dosyadan", 7, {"a": 1})
        son = mgr2.son_chekpoint()
        assert son is not None
        assert son["tur"] == 7

    def test_bos_klasor(self, mgr):
        assert mgr.son_chekpoint() is None


class TestListele:
    def test_bos_liste(self, mgr):
        assert mgr.listele() == []

    def test_coklu_liste(self, mgr):
        mgr.kaydet("h1", 1, {})
        time.sleep(1.1)  # Farkli checkpoint_id icin farkli saniye gerekli
        mgr.kaydet("h2", 2, {})
        lst = mgr.listele()
        assert len(lst) == 2
        assert lst[0]["hedef"] == "h1"
        assert lst[1]["hedef"] == "h2"

    def test_bozuk_dosya_atlanir(self, mgr, tmp_ckpt_dir):
        mgr.kaydet("iyi", 1, {})
        bozuk = tmp_ckpt_dir / "ckpt_bozuk.json"
        bozuk.write_text("NOT JSON", encoding="utf-8")
        lst = mgr.listele()
        assert len(lst) == 1


class TestTemizle:
    def test_eski_dosya_silinir(self, mgr, tmp_ckpt_dir):
        cid = mgr.kaydet("eski", 1, {})
        f = tmp_ckpt_dir / f"{cid}.json"
        # Eski olarak işaretle (mtime'ı 25 saat geri kaydır)
        eski = time.time() - 25 * 3600
        os.utime(f, (eski, eski))
        mgr.temizle(saatten_eski=24)
        assert not f.exists()

    def test_yeni_dosya_kalir(self, mgr, tmp_ckpt_dir):
        cid = mgr.kaydet("yeni", 1, {})
        f = tmp_ckpt_dir / f"{cid}.json"
        mgr.temizle(saatten_eski=24)
        assert f.exists()


class TestDevamEdebilirMi:
    def test_ayni_hedef_var(self, mgr):
        mgr.kaydet("hedef-x", 5, {"devam": True})
        result = mgr.devam_edebilir_mi("hedef-x")
        assert result is not None
        assert result["tur"] == 5

    def test_farkli_hedef(self, mgr):
        mgr.kaydet("hedef-a", 1, {})
        assert mgr.devam_edebilir_mi("hedef-b") is None

    def test_tur_sifir(self, mgr):
        mgr.kaydet("hedef-y", 0, {})
        assert mgr.devam_edebilir_mi("hedef-y") is None
