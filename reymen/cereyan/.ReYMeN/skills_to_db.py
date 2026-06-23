#!/usr/bin/env python3
"""Skills → OnceHafiza DB sync script.
Scans reymen/cereyan/skills/*.md, inserts new, updates changed.
Runs every 6 hours as cron job.
"""

import hashlib
import os
import re
import sqlite3
import sys
from datetime import datetime, date, timedelta
from pathlib import Path

# ── Paths ──
REPO_ROOT = Path.cwd().resolve()  # hermes_projesi
SKILLS_DIR = REPO_ROOT / "reymen" / "cereyan" / "skills"
DB_PATH = REPO_ROOT / "reymen" / "cereyan" / ".ReYMeN" / "ogrenmeler.db"
LOG_PATH = REPO_ROOT / "reymen" / "cereyan" / ".ReYMeN" / "skills_sync.log"

sys.path.insert(0, str(REPO_ROOT))
from reymen.cereyan.once_hafiza import kaydet

# ── Helpers ──

def parse_frontmatter(content: str) -> dict:
    """Extract YAML frontmatter from markdown file."""
    fm = {}
    m = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if not m:
        return fm
    yaml_block = m.group(1)
    for line in yaml_block.strip().split('\n'):
        line = line.strip()
        if ':' in line:
            key, _, val = line.partition(':')
            key = key.strip()
            val = val.strip().strip('"').strip("'")
            # Handle multi-line values like >-
            if val in ('>-', '|', '>', '|-', '>-\n'):
                fm[key] = ''
                continue
            if val.startswith('[') and val.endswith(']'):
                fm[key] = [t.strip().strip('"').strip("'") for t in val[1:-1].split(',')]
            else:
                fm[key] = val
    return fm


def derive_category(filepath: Path, fm: dict) -> str:
    """Derive a category from file path, tags, or default."""
    rel = filepath.relative_to(SKILLS_DIR)
    parts = list(rel.parts)
    
    # Try tags first
    tags = fm.get('tags', [])
    if isinstance(tags, list) and tags:
        for t in tags:
            t = t.strip().lower()
            if t not in ('reymen', 'skill', 'windows', 'linux', 'macos'):
                return f"skill/{t}"
    
    # Use subdirectory structure
    if len(parts) > 1:
        dir_parts = [p.lower() for p in parts[:-1]]
        return "/".join(["skill"] + dir_parts)
    
    return "skill"


def content_hash(content: str) -> str:
    return hashlib.sha256(content.encode('utf-8')).hexdigest()


def get_db_entry(cursor, hedef: str, kategori: str):
    cursor.execute(
        "SELECT id, icerik, guncelleme FROM ogrenmeler WHERE hedef = ? AND kategori = ? LIMIT 1",
        (hedef, kategori)
    )
    return cursor.fetchone()


# ── Main ──

def main():
    start = datetime.now()
    new_count = 0
    update_count = 0
    error_count = 0
    unchanged_count = 0
    skipped_count = 0
    results = []

    conn = sqlite3.connect(str(DB_PATH), timeout=15)
    conn.execute("PRAGMA journal_mode=WAL")

    # Get all .md files recursively
    md_files = sorted(SKILLS_DIR.rglob("*.md"))
    
    print(f"[{start}] Scanning {len(md_files)} .md files in {SKILLS_DIR}", flush=True)

    for fpath in md_files:
        rel_path = fpath.relative_to(SKILLS_DIR)
        try:
            content = fpath.read_text(encoding='utf-8', errors='replace')
        except Exception as e:
            error_count += 1
            results.append(f"  ❌ OKUNAMADI: {rel_path} — {e}")
            continue

        if not content.strip():
            skipped_count += 1
            results.append(f"  ⏭️ BOŞ: {rel_path}")
            continue

        fm = parse_frontmatter(content)

        # Determine hedef (name from frontmatter > filename base)
        hedef = fm.get('name', '').strip()
        if not hedef:
            hedef = fpath.stem.lower().replace('_', ' ').strip()
            hedef = re.sub(r'[^\w\s\-/]', '', hedef).strip()
        
        if not hedef:
            skipped_count += 1
            results.append(f"  ⏭️ İSİMSİZ: {rel_path}")
            continue

        kategori = derive_category(fpath, fm)
        
        # Truncate content to 5000 chars
        icerik = content[:5000]

        # Check existing
        cur = conn.cursor()
        existing = get_db_entry(cur, hedef, kategori)
        
        if existing:
            db_id, db_content, db_updated = existing
            new_hash = content_hash(icerik)
            old_hash = content_hash(db_content[:5000] if db_content else '')
            
            if new_hash != old_hash:
                try:
                    kaydet(
                        hedef=hedef,
                        kategori=kategori,
                        icerik=icerik,
                        basari=True,
                        kaynak_url=f"file:///{rel_path.as_posix()}"
                    )
                    update_count += 1
                    results.append(f"  🔄 GÜNCELLENDİ: {rel_path} → {kategori}/{hedef[:60]}")
                except Exception as e:
                    error_count += 1
                    results.append(f"  ❌ GÜNCELLEME HATASI: {rel_path} — {e}")
            else:
                unchanged_count += 1
        else:
            try:
                kaydet(
                    hedef=hedef,
                    kategori=kategori,
                    icerik=icerik,
                    basari=True,
                    kaynak_url=f"file:///{rel_path.as_posix()}"
                )
                new_count += 1
                results.append(f"  ✅ YENİ: {rel_path} → {kategori}/{hedef[:60]}")
            except Exception as e:
                error_count += 1
                results.append(f"  ❌ EKLEME HATASI: {rel_path} — {e}")

    conn.close()
    elapsed = (datetime.now() - start).total_seconds()

    # ── Rapor ──
    summary = f"""
╔══════════════════════════════════════════╗
║   SKILLS → ONCEHAFIZA DB SENKRONİZASYON ║
╚══════════════════════════════════════════╝

📂 Skills dizini: {SKILLS_DIR}
🗄️  DB: {DB_PATH}
⏱️  Süre: {elapsed:.1f}s
📅  Çalışma: {start.isoformat()}

📊 ÖZET:
  • Toplam .md dosyası: {len(md_files)}
  • ✅ Yeni eklenen: {new_count}
  • 🔄 Güncellenen: {update_count}
  • ⏭️ Değişmeyen: {unchanged_count}
  • ⏭️ Atlanan (boş/isimsiz): {skipped_count}
  • ❌ Hata: {error_count}
"""
    if results:
        summary += "\n📋 DETAYLAR:\n" + "\n".join(results[:80])
        if len(results) > 80:
            summary += f"\n  ... ve {len(results) - 80} satır daha"

    print(summary, flush=True)
    
    # Write log
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_PATH, 'a', encoding='utf-8') as f:
        f.write(f"\n--- {start.isoformat()} ---\n")
        f.write(summary)
        f.write("\n")

    return new_count, update_count, error_count


if __name__ == "__main__":
    main()
