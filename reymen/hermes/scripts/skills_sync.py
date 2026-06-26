#!/usr/bin/env python3
"""
Skills → OnceHafiza Senkronizasyonu
reymen/cereyan/skills/ klasöründeki .md dosyalarını DB'ye kaydet/güncelle.
"""
import os, sys, glob, hashlib, sqlite3
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from reymen.cereyan.once_hafiza import kaydet, DB_YOLU

SKILLS_DIR = os.path.join(ROOT, 'reymen', 'cereyan', 'skills')


def dosya_oku(path):
    """Skill .md dosyasını oku, metadata çıkar."""
    with open(path, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()
    
    lines = content.strip().split('\n')
    name = None
    description = None
    
    if lines and lines[0].strip() == '---':
        for i, line in enumerate(lines[1:], 1):
            if line.strip() == '---':
                break
            if line.lower().startswith('name:'):
                name = line.split(':', 1)[1].strip()
            elif line.lower().startswith('description:'):
                description = line.split(':', 1)[1].strip()
    
    return {
        'name': name or os.path.basename(path).replace('.md', ''),
        'description': description or '',
        'content': content,
        'hash': hashlib.md5(content.encode('utf-8')).hexdigest(),
        'size': len(content),
    }


def hedef_uret(rel_path):
    """Dosya yolundan hedef adı üret."""
    hedef = rel_path.replace('\\', '/').replace('.md', '').replace('/', '_')
    return hedef


def kategori_uret(rel_path):
    """Dosya yolundan kategori üret."""
    parts = rel_path.replace('\\', '/').replace('.md', '').split('/')
    if len(parts) >= 2:
        return 'skills/' + '/'.join(parts[:min(2, len(parts))])
    return 'skills/' + parts[0]


def mevcut_kayitlari_oku():
    """DB'deki mevcut skill kayıtlarını oku."""
    db_path = str(DB_YOLU)
    mevcut = {}
    try:
        con = sqlite3.connect(db_path, timeout=10)
        cursor = con.cursor()
        cursor.execute("""
            SELECT hedef, kategori, icerik, guncelleme
            FROM ogrenmeler
            WHERE kategori LIKE 'skills/%' OR hedef LIKE 'skills_%' OR hedef LIKE 'onay%'
        """)
        for row in cursor.fetchall():
            mevcut[row[0]] = {
                'kategori': row[1],
                'icerik': row[2],
                'guncelleme': row[3],
            }
        con.close()
    except Exception as e:
        print(f"DB okuma hatası: {e}")
    return mevcut


def main():
    print(f"=== Skills → OnceHafiza Senkronizasyonu ===")
    print(f"Zaman: {datetime.now().isoformat()}")
    print(f"Skills dizini: {SKILLS_DIR}")
    
    # DB'deki mevcut kayıtları al
    mevcut = mevcut_kayitlari_oku()
    print(f"DB'de mevcut skill kaydı: {len(mevcut)}")
    
    # Skills klasöründeki tüm .md dosyalarını tara
    md_files = glob.glob(os.path.join(SKILLS_DIR, '**/*.md'), recursive=True)
    print(f"Klasördeki .md dosyası: {len(md_files)}")
    
    yeni = 0
    guncellenen = 0
    ayni = 0
    hata = 0
    bos = 0
    
    for i, fpath in enumerate(md_files):
        rel_path = os.path.relpath(fpath, SKILLS_DIR)
        hedef = hedef_uret(rel_path)
        
        try:
            meta = dosya_oku(fpath)
        except Exception as e:
            hata += 1
            if hata <= 5:
                print(f"  HATA: {rel_path} → {e}")
            continue
        
        if not meta['content'].strip():
            bos += 1
            continue  # Boş dosyaları atla
        
        kategori = kategori_uret(rel_path)
        icerik = meta['content']
        
        try:
            if hedef in mevcut:
                eski_icerik = mevcut[hedef]['icerik'] or ''
                eski_hash = hashlib.md5(eski_icerik.encode('utf-8')).hexdigest()
                
                if eski_hash != meta['hash']:
                    kaydet(
                        hedef=hedef,
                        kategori=kategori,
                        icerik=icerik,
                        basari=True,
                        kaynak_url=f"file://skills/{rel_path}"
                    )
                    guncellenen += 1
                else:
                    ayni += 1
            else:
                kaydet(
                    hedef=hedef,
                    kategori=kategori,
                    icerik=icerik,
                    basari=True,
                    kaynak_url=f"file://skills/{rel_path}"
                )
                yeni += 1
        except Exception as e:
            hata += 1
            if hata <= 5:
                print(f"  KAYDET HATASI: {hedef} → {e}")
        
        if (i + 1) % 1000 == 0:
            print(f"  [{i+1}/{len(md_files)}] yeni={yeni} günc={guncellenen} ayni={ayni} hata={hata}")
    
    print(f"\n{'='*40}")
    print(f"TOPLAM DOSYA:     {len(md_files)}")
    print(f"YENİ EKLENEN:     {yeni}")
    print(f"GÜNCELLENEN:      {guncellenen}")
    print(f"AYNI KALAN:       {ayni}")
    print(f"BOŞ DOSYA:        {bos}")
    print(f"HATA:             {hata}")
    print(f"{'='*40}")
    print(f"Bitiş: {datetime.now().isoformat()}")


if __name__ == '__main__':
    main()
