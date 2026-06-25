#!/usr/bin/env python3
"""
Skills → OnceHafiza DB senkronizasyonu
reymen/cereyan/skills/ klasöründeki .md dosyalarını tarar, DB'ye kaydeder.
Her 6 saatte bir çalışır.
"""

import os
import re
import sqlite3
from datetime import datetime
from pathlib import Path

# Yollar
SKILLS_DIR = Path(r"C:\Users\marko\Desktop\Reymen Proje\hermes_projesi\reymen\cereyan\skills")
DB_PATH = Path(r"C:\Users\marko\Desktop\Reymen Proje\hermes_projesi\reymen\cereyan\.ReYMeN\ogrenmeler.db")

def parse_frontmatter(content):
    """Markdown frontmatter'ını parse et"""
    match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    if not match:
        return {}
    
    fm_text = match.group(1)
    fm = {}
    current_key = None
    current_value = []
    
    for line in fm_text.split('\n'):
        # Key-value pattern
        kv_match = re.match(r'^(\w+):\s*(.*)', line)
        if kv_match:
            if current_key:
                fm[current_key] = '\n'.join(current_value).strip()
            current_key = kv_match.group(1).lower()
            current_value = [kv_match.group(2).strip()]
        elif current_key:
            # Continuation line
            current_value.append(line.strip())
    
    if current_key:
        fm[current_key] = '\n'.join(current_value).strip()
    
    return fm

def extract_category_from_path(file_path):
    """Dosya yolundan kategori çıkar"""
    # reymen/cereyan/skills/Skiller/tor/... → skills/tor
    parts = file_path.relative_to(SKILLS_DIR).parts
    
    if len(parts) >= 2:
        # İlk klasör (Skiller) atla, sonraki alt kategoriyi al
        category_parts = parts[1:-1]  # son dosya adını hariç tut
        if category_parts:
            return f"skills/{'/'.join(category_parts)}"
    
    return "skills"

def extract_info_from_file(file_path):
    """Dosyadan hedef ve açıklama çıkar"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"HATA okuma: {file_path} - {e}")
        return None
    
    fm = parse_frontmatter(content)
    
    # Hedef (name) - frontmatter'dan veya dosya adından
    name = fm.get('name', '')
    if not name:
        # Dosya adından çıkar
        name = file_path.stem
        # _SKILL sonunu temizle
        name = re.sub(r'_SKILL$', '', name)
    
    # Açıklama
    description = fm.get('description', '')
    if not description:
        # İlk başlık satırından
        for line in content.split('\n'):
            if line.startswith('# ') and not line.startswith('# ---'):
                description = line[2:].strip()
                break
    
    # Kategori
    category = extract_category_from_path(file_path)
    
    # İpuçları (usage_count vb.)
    usage_count = int(fm.get('usage_count', 0))
    
    return {
        'hedef': name,
        'kategori': category,
        'description': description,
        'usage_count': usage_count,
        'file_path': str(file_path)
    }

def sync_to_db():
    """Skills dosyalarını DB'ye senkronize et"""
    print(f"\n{'='*60}")
    print(f"Skills → DB Senkronizasyonu Başladı")
    print(f"Zaman: {datetime.now().isoformat()}")
    print(f"{'='*60}\n")
    
    # DB bağlantısı
    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()
    
    # Stats
    stats = {'new': 0, 'updated': 0, 'skipped': 0, 'error': 0}
    
    # Tüm .md dosyalarını bul
    md_files = list(SKILLS_DIR.rglob('*.md'))
    print(f"Toplam {len(md_files)} .md dosyası bulundu\n")
    
    for file_path in md_files:
        try:
            info = extract_info_from_file(file_path)
            if not info:
                stats['error'] += 1
                continue
            
            hedef = info['hedef']
            kategori = info['kategori']
            description = info['description']
            
            # DB'de var mı kontrol et (hedef + kategori)
            c.execute(
                "SELECT id, icerik FROM ogrenmeler WHERE hedef = ? AND kategori = ?",
                (hedef, kategori)
            )
            existing = c.fetchone()
            
            now = datetime.now().isoformat()
            
            if existing:
                # Güncelle (sadece açıklama değiştiyse)
                old_desc = existing[1] or ''
                if description and description != old_desc:
                    c.execute("""
                        UPDATE ogrenmeler 
                        SET icerik = ?, guncelleme = ?
                        WHERE id = ?
                    """, (description, now, existing[0]))
                    stats['updated'] += 1
                    print(f"  [GÜNCELLENDİ] {hedef} ({kategori})")
                else:
                    stats['skipped'] += 1
            else:
                # Yeni kayıt ekle
                c.execute("""
                    INSERT INTO ogrenmeler (
                        hedef, kategori, icerik, guven_skoru, 
                        basari_sayisi, hata_sayisi, son_kullanim,
                        gecerlilik_tarihi, olusturulma, guncelleme,
                        web_arama_sebebi, kaynak_url,
                        ne, nerede, nasil, neden, kim
                    ) VALUES (?, ?, ?, 0.5, 1, 0, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    hedef,           # 1. hedef
                    kategori,        # 2. kategori
                    description,     # 3. icerik
                    now,             # 4. son_kullanim
                    now,             # 5. gecerlilik_tarihi
                    now,             # 6. olusturulma
                    now,             # 7. guncelleme
                    'skill_md_dosyasindan_otomatik_kayit',  # 8. web_arama_sebebi
                    info['file_path'],  # 9. kaynak_url
                    hedef,           # 10. ne
                    kategori,        # 11. nerede
                    f"Skill dosyasından otomatik çıkarıldı: {file_path.name}",  # 12. nasil
                    'Automated skills sync',  # 13. neden
                    'skills_sync_cron'  # 14. kim
                ))
                stats['new'] += 1
                print(f"  [YENİ] {hedef} ({kategori})")
        
        except Exception as e:
            print(f"  [HATA] {file_path.name}: {e}")
            stats['error'] += 1
    
    conn.commit()
    conn.close()
    
    # Sonuç raporu
    print(f"\n{'='*60}")
    print(f"SENKRONİZASYON TAMAMLANDI")
    print(f"{'='*60}")
    print(f"  Yeni eklenen:     {stats['new']}")
    print(f"  Güncellenen:      {stats['updated']}")
    print(f"  Atlanan (eşleşti): {stats['skipped']}")
    print(f"  Hatalı:           {stats['error']}")
    print(f"  Toplam işlenen:   {sum(stats.values())}")
    print(f"{'='*60}\n")
    
    return stats

if __name__ == "__main__":
    sync_to_db()
