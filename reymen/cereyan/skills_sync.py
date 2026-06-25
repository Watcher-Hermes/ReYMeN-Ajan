# -*- coding: utf-8 -*-
"""Skills -> OnceHafiza DB sync. Her 6 saatte bir calisir.
Sadece yeni veya degismis dosyalari isler.

Kullanim: python reymen/cereyan/skills_sync.py (proje root'tan)
"""
import os, sys, re, hashlib, sqlite3
from pathlib import Path
from datetime import datetime

# Script'in bulundugu yer ~/hermes_projesi/reymen/cereyan/skills_sync.py
SCRIPT_DIR = Path(__file__).resolve().parent  # reymen/cereyan/
PROJE_ROOT = SCRIPT_DIR.parent.parent.resolve()  # hermes_projesi/
os.chdir(str(PROJE_ROOT))  # proje root'a git
sys.path.insert(0, str(PROJE_ROOT))

from reymen.cereyan.once_hafiza import kaydet, _db_kur

CEREYAN_DIR = PROJE_ROOT / "reymen" / "cereyan"
SKILLS_DIR = CEREYAN_DIR / "skills"
EXCLUDE = {"_corrupted_backup"}

# Marker dosyasi: son calisma zamanini sakla
MARKER = SCRIPT_DIR / ".skills_sync_marker"

def get_last_run() -> datetime | None:
    if MARKER.exists():
        try:
            ts = MARKER.read_text().strip()
            return datetime.fromisoformat(ts) if ts else None
        except:
            pass
    return None

def save_last_run():
    MARKER.write_text(datetime.now().isoformat())

def hash_content(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]

def norm_kategori(rel: Path) -> str:
    parts = rel.parts
    if len(parts) <= 1:
        return "skills"
    return "skills/" + "/".join(parts[:-1])

def norm_hedef(fname: str, parent: str, content: str) -> str:
    """Dosya adindan veya ilk # basligindan hedef cikar."""
    name = fname
    if name.endswith(".md"):
        name = name[:-3]
    if name.upper() == "SKILL":
        return parent.replace("_", " ").replace("-", " ").strip()
    return name.replace("_", " ").replace("-", " ").strip()[:100]

def get_first_heading(content: str) -> str | None:
    in_fm = False
    for line in content.splitlines():
        s = line.strip()
        if s == "---":
            in_fm = not in_fm
            continue
        if not in_fm and re.match(r"^#+\s", s):
            return re.sub(r"^#+\s*", "", s).strip()
    return None

def get_content_snippet(content: str, maxlen=800) -> str:
    lines = content.splitlines()
    out = []
    in_fm = False
    for line in lines:
        if line.strip() == "---":
            in_fm = not in_fm
            continue
        if not in_fm:
            out.append(line)
    text = "\n".join(out).strip()
    return text[:maxlen] + ("..." if len(text) > maxlen else "")

def main():
    last_run = get_last_run()
    now = datetime.now()
    print(f"[SKILLS SYNC] Baslangic: {now.isoformat()}")
    print(f"[SKILLS SYNC] Son calisma: {last_run.isoformat() if last_run else 'ILK CALISMA'}")

    # Tum .md dosyalari
    all_files = sorted(SKILLS_DIR.rglob("*.md"))
    all_files = [f for f in all_files if not any(ex in f.parts for ex in EXCLUDE)]

    if not all_files:
        print("[SKILLS SYNC] skills/ klasorunde .md dosyasi bulunamadi!")
        save_last_run()
        return

    print(f"[SKILLS SYNC] {len(all_files)} .md dosyasi taranacak")

    # DB baglantisi (okuma)
    _db_kur()
    db_path = CEREYAN_DIR / ".ReYMeN" / "ogrenmeler.db"
    con = sqlite3.connect(str(db_path))
    cur = con.cursor()

    yeni = 0
    guncellenen = 0
    atlanan = 0
    hata = 0
    islenen = 0

    for fpath in all_files:
        rel = fpath.relative_to(SKILLS_DIR)
        rel_str = str(rel).replace("\\", "/")
        mtime = datetime.fromtimestamp(fpath.stat().st_mtime)

        # Sadece son calismadan sonra degisen/yeni dosyalar
        if last_run and mtime <= last_run:
            atlanan += 1
            continue

        kategori = norm_kategori(rel)
        parent_folder = fpath.parent.name
        try:
            content = fpath.read_text(encoding="utf-8", errors="replace")
        except Exception as e:
            print(f"  [HATA] Okunamadi: {rel_str}: {e}")
            hata += 1
            continue

        if not content.strip():
            atlanan += 1
            continue

        hedef = norm_hedef(fpath.name, parent_folder, content)
        heading = get_first_heading(content)
        if heading and len(heading) > 5:
            hedef = heading[:100]

        snippet = get_content_snippet(content)
        snippet_hash = hash_content(snippet)

        # DB'de var mi, guncel mi kontrol
        var = cur.execute(
            "SELECT id, icerik FROM ogrenmeler WHERE hedef = ? AND kategori = ? LIMIT 1",
            (hedef, kategori)
        ).fetchone()

        is_new = False
        if var:
            existing_hash = hash_content(var[1] or "")
            if existing_hash == snippet_hash:
                atlanan += 1
                continue
        else:
            is_new = True

        # Kaydet/upsert
        try:
            kaydet(
                hedef=hedef,
                kategori=kategori,
                icerik=snippet,
                basari=True,
                kaynak_url=None
            )
            if is_new:
                yeni += 1
            else:
                guncellenen += 1
            islenen += 1
            if islenen % 100 == 0:
                print(f"  [ILERLEME] {yeni} yeni + {guncellenen} guncel = {islenen} islendi / {len(all_files)} dosya")
        except Exception as e:
            print(f"  [HATA] DB: {rel_str}: {e}")
            hata += 1

    con.close()

    # Rapor
    print(f"\n{'='*60}")
    print(f"SKILLS -> HAFIZA SENKRONIZASYONU TAMAM")
    print(f"  Tarih              : {now.isoformat()}")
    print(f"  Toplam .md dosyasi : {len(all_files)}")
    print(f"  Yeni eklenen       : {yeni}")
    print(f"  Guncellenen        : {guncellenen}")
    print(f"  Degismeyen(atlanan): {atlanan}")
    print(f"  Hata               : {hata}")
    print(f"  Bir sonraki adim   : marker kaydedildi, sadece yeni degisiklikler islenecek")
    print(f"{'='*60}")

    save_last_run()

if __name__ == "__main__":
    main()
