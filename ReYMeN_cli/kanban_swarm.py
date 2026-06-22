# -*- coding: utf-8 -*-
"""ReYMeN_cli/kanban_swarm.py — Kanban Swarm Topolojisi CLI.

Swarm (kume) calisma duzenini olusturur: plan koku -> paralel isciler ->
dogrulayici -> birlestirici. SQLite kanban uzerinde bagimsiz calisir,
KanbanOrchestrator'a ihtiyac duymaz.
ReYMeN'e ozgu paralel gorev zinciri yonetimi.
"""

import random
import string
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Optional


class Renk:
    """ReYMeN Renk sinifi — kanban_swarm ciktisi icin."""
    YESIL = "\033[92m"
    SARI = "\033[93m"
    KIRMIZI = "\033[91m"
    MAVI = "\033[94m"
    CYAN = "\033[96m"
    MOR = "\033[95m"
    KALIN = "\033[1m"
    SOLUK = "\033[2m"
    SON = "\033[0m"

    @classmethod
    def boya(cls, metin: str, kod: str) -> str:
        return f"{kod}{metin}{cls.SON}"

    @classmethod
    def yesil(cls, metin: str) -> str:
        return cls.boya(metin, cls.YESIL)

    @classmethod
    def sari(cls, metin: str) -> str:
        return cls.boya(metin, cls.SARI)

    @classmethod
    def kirmizi(cls, metin: str) -> str:
        return cls.boya(metin, cls.KIRMIZI)

    @classmethod
    def mavi(cls, metin: str) -> str:
        return cls.boya(metin, cls.MAVI)

    @classmethod
    def cyan(cls, metin: str) -> str:
        return cls.boya(metin, cls.CYAN)

    @classmethod
    def mor(cls, metin: str) -> str:
        return cls.boya(metin, cls.MOR)

    @classmethod
    def kalin(cls, metin: str) -> str:
        return cls.boya(metin, cls.KALIN)


def _baglan(db_path: str):
    """SQLite baglantisi olustur."""
    import sqlite3
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def _swarm_id_olustur() -> str:
    """Benzersiz swarm ID'si olustur (swarm_<timestamp>_<random>)."""
    try:
        zaman = datetime.now().strftime("%Y%m%d_%H%M%S")
        rastgele = "".join(random.choices(string.ascii_lowercase + string.digits, k=6))
        return f"swarm_{zaman}_{rastgele}"
    except Exception:
        return f"swarm_{datetime.now().timestamp():.0f}_{random.randint(1000, 9999)}"


def swarm_olustur(db_path: str, baslik: str,
                  worker_specs: list[dict],
                  profile: str = "default") -> dict:
    """Swarm gorev grafigi olustur.

    Root task -> N adet worker (paralel, ready) -> verifier (todo) -> synthesizer (todo).

    Args:
        db_path: Kanban veritabani yolu.
        baslik: Swarm basligi.
        worker_specs: Isci tanimlari listesi.
            Her biri: {"ad": str, "gorev": str, "baglam": str}
        profile: Kullanilacak profil adi.

    Returns:
        dict: Swarm ID ve tum task ID'lerini iceren sozluk.
    """
    try:
        import kanban_db
    except ImportError:
        sys.path.insert(0, str(Path(__file__).parent.parent))
        import kanban_db  # type: ignore

    try:
        conn = _baglan(db_path)
        cursor = conn.cursor()

        # Tablolarin var oldugundan emin ol
        kanban_db.init_db(db_path)

        swarm_id = _swarm_id_olustur()
        ids = {"swarm_id": swarm_id, "root_id": -1, "workers": [],
               "verifier_id": -1, "synthesizer_id": -1}

        # 1. Root task (ana plan)
        kok_aciklama = f"[Swarm: {swarm_id}] Ana plan: {baslik}\nProfil: {profile}\nIsci sayisi: {len(worker_specs)}"
        root_id = kanban_db.task_ekle(db_path, f"[Root] {baslik}", kok_aciklama, "doing", "swarm,root")
        if root_id <= 0:
            return {"hata": "Root task olusturulamadi."}
        ids["root_id"] = root_id

        # Root task'i swarm tablosuna kaydet
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS swarms ("
            "id TEXT PRIMARY KEY, root_id INTEGER, baslik TEXT, "
            "olusturma_zamani TEXT, profil TEXT, durum TEXT DEFAULT 'active')"
        )
        cursor.execute(
            "INSERT OR REPLACE INTO swarms (id, root_id, baslik, olusturma_zamani, profil) "
            "VALUES (?, ?, ?, datetime('now','localtime'), ?)",
            (swarm_id, root_id, baslik, profile),
        )

        # 2. Worker tasks (paralel, todo -> hemen ready)
        for i, spec in enumerate(worker_specs):
            ad = spec.get("ad", f"Isci-{i+1}")
            gorev = spec.get("gorev", "")
            baglam = spec.get("baglam", "")
            aciklama = (
                f"[Swarm: {swarm_id}] Worker: {ad}\n"
                f"Gorev: {gorev}\nBaglam: {baglam}\nKok ID: {root_id}"
            )
            wid = kanban_db.task_ekle(
                db_path, f"[Worker] {ad}", aciklama, "todo", "swarm,worker"
            )
            if wid > 0:
                ids["workers"].append(wid)
                # Worker'lari otomatik doing yap (paralel calismaya hazir)
                kanban_db.task_tasi(db_path, wid, "doing")

        # 3. Verifier task (todo, worker'lar tamamlanincaya kadar bekler)
        ver_aciklama = (
            f"[Swarm: {swarm_id}] Dogrulayici\n"
            f"Worker ID'leri: {ids['workers']}\n"
            f"Bekleniyor: workers -> done"
        )
        ver_id = kanban_db.task_ekle(
            db_path, f"[Verifier] Dogrula: {baslik}", ver_aciklama, "todo", "swarm,verifier"
        )
        if ver_id > 0:
            ids["verifier_id"] = ver_id

        # 4. Synthesizer task (todo, verifier tamamlanincaya kadar bekler)
        syn_aciklama = (
            f"[Swarm: {swarm_id}] Birlestirici\n"
            f"Verifier ID: {ver_id}\n"
            f"Bekleniyor: verifier -> done"
        )
        syn_id = kanban_db.task_ekle(
            db_path, f"[Synthesizer] Birlestir: {baslik}", syn_aciklama, "todo", "swarm,synthesizer"
        )
        if syn_id > 0:
            ids["synthesizer_id"] = syn_id

        conn.commit()
        conn.close()

        print(f"{Renk.yesil('[Swarm]')} Swarm olusturuldu: {swarm_id}")
        print(f"  Root: {root_id} | Workers: {ids['workers']} "
              f"| Verifier: {ver_id} | Synthesizer: {syn_id}")

        # Root task tamamlandi
        kanban_db.task_tasi(db_path, root_id, "done")

        return ids
    except Exception as e:
        return {"hata": f"Swarm olusturma hatasi: {e}"}


def swarm_durum_kontrol(db_path: str, root_id: int) -> str:
    """Swarm durumunu kontrol et.

    Args:
        db_path: Veritabani yolu.
        root_id: Root task ID'si.

    Returns:
        str: Renkli durum raporu.
    """
    try:
        import kanban_db
    except ImportError:
        sys.path.insert(0, str(Path(__file__).parent.parent))
        import kanban_db  # type: ignore

    try:
        conn = _baglan(db_path)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM swarms WHERE root_id = ?", (root_id,)
        )
        swarm = cursor.fetchone()
        if not swarm:
            conn.close()
            return f"{Renk.kirmizi('[Swarm]')} Swarm bulunamadi (Root ID: {root_id})."

        swarm = dict(swarm)

        cursor.execute(
            "SELECT id, baslik, durum FROM tasks WHERE baslik LIKE ? "
            "ORDER BY id",
            (f"%{swarm['id']}%",),
        )
        tasks = [dict(r) for r in cursor.fetchall()]
        conn.close()

        if not tasks:
            # Root ID'den bulmaya calis
            conn = _baglan(db_path)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, baslik, durum, etiketler FROM tasks "
                "WHERE id >= ? AND etiketler LIKE '%swarm%' "
                "ORDER BY id LIMIT 20",
                (root_id,),
            )
            tasks = [dict(r) for r in cursor.fetchall()]
            conn.close()

        satirlar = [
            Renk.kalin(f"[Swarm] {swarm['baslik']}"),
            f"  ID: {swarm['id']} | Profil: {swarm['profil']}",
            f"  Olusturma: {swarm['olusturma_zamani']}",
            f"  {Renk.cyan('Gorevler:')}",
        ]

        worker_durumlari = {"todo": 0, "doing": 0, "done": 0}
        for t in tasks:
            ikon = {"todo": "📋", "doing": "🔧", "done": "✅"}.get(t["durum"], "❓")
            renk = {"todo": Renk.mavi, "doing": Renk.sari, "done": Renk.yesil}.get(
                t["durum"], Renk.kirmizi
            )
            satirlar.append(f"    {ikon} ID:{t['id']} {renk(t['baslik'][:60])}")
            if "worker" in t.get("etiketler", "").lower():
                worker_durumlari[t["durum"]] = worker_durumlari.get(t["durum"], 0) + 1

        bekleyen = worker_durumlari.get("todo", 0) + worker_durumlari.get("doing", 0)
        tamam = worker_durumlari.get("done", 0)
        satirlar.append(
            f"  {Renk.kalin('Ozet:')} {tamam} tamam, {bekleyen} bekleyen worker"
        )

        return "\n".join(satirlar)
    except Exception as e:
        return f"{Renk.kirmizi('[Swarm]')} Durum kontrol hatasi: {e}"


def swarm_listele(db_path: str) -> str:
    """Tum swarm'lari listele.

    Args:
        db_path: Veritabani yolu.

    Returns:
        str: Renkli swarm listesi.
    """
    try:
        conn = _baglan(db_path)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM swarms ORDER BY olusturma_zamani DESC"
        )
        swarms = [dict(r) for r in cursor.fetchall()]
        conn.close()

        if not swarms:
            return f"{Renk.sari('[Swarm]')} Henuz swarm olusturulmamis."

        satirlar = [f"{Renk.kalin(f'[Swarm] Toplam {len(swarms)} swarm:')}"]
        for s in swarms:
            durum_ikon = "✅" if s.get("durum") == "completed" else "🔄"
            satirlar.append(
                f"  {durum_ikon} {Renk.cyan(s['baslik'][:50])}\n"
                f"    ID: {s['id']} | Root: {s['root_id']} | "
                f"Profil: {s['profil']} | {s['olusturma_zamani']}"
            )

        return "\n".join(satirlar)
    except Exception as e:
        return f"{Renk.kirmizi('[Swarm]')} Liste hatasi: {e}"
