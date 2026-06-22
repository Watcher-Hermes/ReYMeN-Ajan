# -*- coding: utf-8 -*-
"""ReYMeN_cli/kanban_db.py — SQLite Kanban Veritabani CLI.

SQLite arkaplanli bagimsiz kanban board yonetimi.
KanbanOrchestrator'dan bagimsiz calisir, kendi
veritabanini olusturur ve yonetir.
ReYMeN'e ozgu gorev takibi icin dogrudan SQLite kullanir.
"""

import sqlite3
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Optional


class Renk:
    """ReYMeN Renk sinifi — kanban_db ciktisi icin."""
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
    def kalin(cls, metin: str) -> str:
        return cls.boya(metin, cls.KALIN)


def _baglan(db_path: str) -> sqlite3.Connection:
    """SQLite veritabanina baglan ve row factory ayarla."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn


def init_db(db_path: str) -> bool:
    """SQLite kanban veritabanini baslat.

    tasks ve task_events tablolarini olusturur (yoksa).

    Args:
        db_path: Veritabani dosya yolu.

    Returns:
        bool: Basarili ise True.
    """
    try:
        conn = _baglan(db_path)
        cursor = conn.cursor()

        cursor.executescript("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                baslik TEXT NOT NULL,
                aciklama TEXT DEFAULT '',
                durum TEXT DEFAULT 'todo',
                etiketler TEXT DEFAULT '',
                olusturma_zamani TEXT DEFAULT (datetime('now','localtime')),
                guncelleme_zamani TEXT DEFAULT (datetime('now','localtime'))
            );

            CREATE TABLE IF NOT EXISTS task_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER NOT NULL,
                olay TEXT NOT NULL,
                eski_deger TEXT,
                yeni_deger TEXT,
                zaman TEXT DEFAULT (datetime('now','localtime')),
                FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
            );

            CREATE INDEX IF NOT EXISTS idx_tasks_durum ON tasks(durum);
            CREATE INDEX IF NOT EXISTS idx_events_task ON task_events(task_id);
        """)

        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"{Renk.kirmizi('[DB]')} Baslatma hatasi: {e}")
        return False


def task_ekle(db_path: str, baslik: str, aciklama: str = "",
              durum: str = "todo", etiketler: str = "") -> int:
    """Yeni bir kanban gorevi ekle.

    Args:
        db_path: Veritabani yolu.
        baslik: Gorev basligi.
        aciklama: Gorev aciklamasi (opsiyonel).
        durum: Baslangic durumu (todo/doing/done).
        etiketler: Etiketler (virgulle ayrilmis).

    Returns:
        int: Eklenen gorevin ID'si, hata durumunda -1.
    """
    try:
        conn = _baglan(db_path)
        cursor = conn.cursor()

        if durum not in ("todo", "doing", "done"):
            durum = "todo"

        cursor.execute(
            "INSERT INTO tasks (baslik, aciklama, durum, etiketler) VALUES (?, ?, ?, ?)",
            (baslik, aciklama, durum, etiketler),
        )
        task_id = cursor.lastrowid

        cursor.execute(
            "INSERT INTO task_events (task_id, olay, yeni_deger) VALUES (?, 'olusturuldu', ?)",
            (task_id, durum),
        )

        conn.commit()
        conn.close()
        print(f"{Renk.yesil('[DB]')} Gorev eklendi (ID: {task_id}): {baslik}")
        return task_id
    except Exception as e:
        print(f"{Renk.kirmizi('[DB]')} Gorev ekleme hatasi: {e}")
        return -1


def task_listele(db_path: str, durum: Optional[str] = None) -> str:
    """Kanban gorevlerini listele.

    Args:
        db_path: Veritabani yolu.
        durum: Filtre durumu (None=tumu, todo/doing/done).

    Returns:
        str: Renkli, formatli gorev listesi.
    """
    try:
        conn = _baglan(db_path)
        cursor = conn.cursor()

        if durum and durum in ("todo", "doing", "done"):
            cursor.execute(
                "SELECT * FROM tasks WHERE durum = ? ORDER BY guncelleme_zamani DESC",
                (durum,),
            )
        else:
            cursor.execute(
                "SELECT * FROM tasks ORDER BY durum, guncelleme_zamani DESC"
            )

        satirlar = []
        rows = cursor.fetchall()
        if not rows:
            conn.close()
            return f"{Renk.sari('[DB]')} Henuz gorev yok."

        durum_ikon = {"todo": "📋", "doing": "🔧", "done": "✅"}
        baslik_renk = {"todo": Renk.mavi, "doing": Renk.sari, "done": Renk.yesil}

        for row in rows:
            r = dict(row)
            ikon = durum_ikon.get(r["durum"], "📋")
            renk = baslik_renk.get(r["durum"], Renk.cyan)
            etiket = f" [{r['etiketler']}]" if r["etiketler"] else ""
            satirlar.append(
                f"  {ikon} {renk(r['baslik'])}{etiket}\n"
                f"    ID: {r['id']} | Durum: {r['durum']} | "
                f"Olusturma: {r['olusturma_zamani']}"
            )

        conn.close()
        return "\n".join(satirlar)
    except Exception as e:
        return f"{Renk.kirmizi('[DB]')} Listeleme hatasi: {e}"


def task_guncelle(db_path: str, task_id: int, **kwargs) -> bool:
    """Gorev alanlarini guncelle.

    Args:
        db_path: Veritabani yolu.
        task_id: Gorev ID'si.
        **kwargs: Guncellenecek alanlar (baslik, aciklama, etiketler).

    Returns:
        bool: Basarili ise True.
    """
    try:
        if not kwargs:
            print(f"{Renk.sari('[DB]')} Guncellenecek alan belirtilmedi.")
            return False

        conn = _baglan(db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        eski = cursor.fetchone()
        if not eski:
            print(f"{Renk.kirmizi('[DB]')} Gorev bulunamadi (ID: {task_id}).")
            conn.close()
            return False

        izinli = {"baslik", "aciklama", "etiketler"}
        guncelle = {k: v for k, v in kwargs.items() if k in izinli and v is not None}
        if not guncelle:
            print(f"{Renk.sari('[DB]')} Guncellenecek gecerli alan yok.")
            conn.close()
            return False

        guncelle["guncelleme_zamani"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        set_ifade = ", ".join(f"{k} = ?" for k in guncelle)
        degerler = list(guncelle.values()) + [task_id]

        cursor.execute(f"UPDATE tasks SET {set_ifade} WHERE id = ?", degerler)

        for anahtar, yeni_deger in guncelle.items():
            if anahtar != "guncelleme_zamani":
                eski_deger = dict(eski).get(anahtar, "")
                cursor.execute(
                    "INSERT INTO task_events (task_id, olay, eski_deger, yeni_deger) "
                    "VALUES (?, 'guncellendi', ?, ?)",
                    (task_id, str(eski_deger), str(yeni_deger)),
                )

        conn.commit()
        conn.close()
        print(f"{Renk.yesil('[DB]')} Gorev guncellendi (ID: {task_id}).")
        return True
    except Exception as e:
        print(f"{Renk.kirmizi('[DB]')} Guncelleme hatasi: {e}")
        return False


def task_tasi(db_path: str, task_id: int, yeni_durum: str) -> bool:
    """Gorevi baska bir duruma tasi (todo/doing/done).

    Args:
        db_path: Veritabani yolu.
        task_id: Gorev ID'si.
        yeni_durum: Hedef durum (todo/doing/done).

    Returns:
        bool: Basarili ise True.
    """
    try:
        if yeni_durum not in ("todo", "doing", "done"):
            print(f"{Renk.kirmizi('[DB]')} Gecersiz durum: {yeni_durum}")
            return False

        conn = _baglan(db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT durum FROM tasks WHERE id = ?", (task_id,))
        eski = cursor.fetchone()
        if not eski:
            print(f"{Renk.kirmizi('[DB]')} Gorev bulunamadi (ID: {task_id}).")
            conn.close()
            return False

        eski_durum = eski["durum"]
        if eski_durum == yeni_durum:
            print(f"{Renk.sari('[DB]')} Gorev zaten '{yeni_durum}' durumunda.")
            conn.close()
            return False

        zaman = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            "UPDATE tasks SET durum = ?, guncelleme_zamani = ? WHERE id = ?",
            (yeni_durum, zaman, task_id),
        )
        cursor.execute(
            "INSERT INTO task_events (task_id, olay, eski_deger, yeni_deger) "
            "VALUES (?, 'tasi', ?, ?)",
            (task_id, eski_durum, yeni_durum),
        )

        conn.commit()
        conn.close()
        print(f"{Renk.yesil('[DB]')} Gorev tasindi: {eski_durum} -> {yeni_durum}")
        return True
    except Exception as e:
        print(f"{Renk.kirmizi('[DB]')} Tasima hatasi: {e}")
        return False


def task_sil(db_path: str, task_id: int) -> bool:
    """Gorevi veritabanindan sil.

    Args:
        db_path: Veritabani yolu.
        task_id: Silinecek gorev ID'si.

    Returns:
        bool: Basarili ise True.
    """
    try:
        conn = _baglan(db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT baslik FROM tasks WHERE id = ?", (task_id,))
        gorev = cursor.fetchone()
        if not gorev:
            print(f"{Renk.kirmizi('[DB]')} Gorev bulunamadi (ID: {task_id}).")
            conn.close()
            return False

        cursor.execute("DELETE FROM task_events WHERE task_id = ?", (task_id,))
        cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))

        conn.commit()
        conn.close()
        print(f"{Renk.yesil('[DB]')} Gorev silindi (ID: {task_id}): {gorev['baslik']}")
        return True
    except Exception as e:
        print(f"{Renk.kirmizi('[DB]')} Silme hatasi: {e}")
        return False


def task_istatistik(db_path: str) -> str:
    """Kanban durum istatistiklerini goster.

    Args:
        db_path: Veritabani yolu.

    Returns:
        str: Renkli istatistik raporu.
    """
    try:
        conn = _baglan(db_path)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT durum, COUNT(*) as adet FROM tasks GROUP BY durum"
        )
        sayim = {row["durum"]: row["adet"] for row in cursor.fetchall()}

        cursor.execute("SELECT COUNT(*) as toplam FROM tasks")
        toplam = cursor.fetchone()["toplam"]

        cursor.execute("SELECT COUNT(*) as olay_sayisi FROM task_events")
        olay_sayisi = cursor.fetchone()["olay_sayisi"]

        conn.close()

        satirlar = [
            f"{Renk.kalin('[DB] Kanban Istatistikleri')}",
            f"  {Renk.mavi('📋')} Todo:  {sayim.get('todo', 0)}",
            f"  {Renk.sari('🔧')} Doing: {sayim.get('doing', 0)}",
            f"  {Renk.yesil('✅')} Done:  {sayim.get('done', 0)}",
            f"  {Renk.cyan('Toplam')}: {toplam} gorev",
            f"  {Renk.soluk(f'Toplam {olay_sayisi} olay kaydedildi.')}",
        ]
        return "\n".join(satirlar)
    except Exception as e:
        return f"{Renk.kirmizi('[DB]')} Istatistik hatasi: {e}"
