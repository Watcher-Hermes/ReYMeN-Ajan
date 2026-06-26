# -*- coding: utf-8 -*-
"""skills_yeni -> Skiller/ toplu tasima + alt basliklara bolme"""

import os, shutil
from pathlib import Path

PROJE = Path(r"C:\Users\marko\Desktop\Reymen Proje\hermes_projesi")
KAYNAK = PROJE / "reymen" / "cereyan" / "skills_yeni"
HEDEF = PROJE / "reymen" / "cereyan" / "skills" / "Skiller"

# skills_yeni'ndeki kategorileri Skiller/ altina tasi
tasinan = 0
atlanan = 0

for kat in sorted(os.listdir(KAYNAK)):
    kat_yolu = KAYNAK / kat
    if not kat_yolu.is_dir():
        if kat.endswith(".md") and kat != "INDEX.md":
            # Kokteki .md dosyalari -> Kodu kategorisine
            hedef_kat = HEDEF / "Kod"
            hedef_dosya = hedef_kat / kat
            os.makedirs(hedef_kat, exist_ok=True)
            if not hedef_dosya.exists():
                shutil.copy2(kat_yolu, hedef_dosya)
                tasinan += 1
            else:
                atlanan += 1
        continue
    
    # Hedef kategori
    hedef_kat = HEDEF / kat
    os.makedirs(hedef_kat, exist_ok=True)
    
    for md_dosya in sorted(kat_yolu.glob("*.md")):
        hedef = hedef_kat / md_dosya.name
        if hedef.exists():
            atlanan += 1
            continue
        shutil.copy2(md_dosya, hedef)
        tasinan += 1

print(f"Tasinan: {tasinan}")
print(f"Atlanan: {atlanan}")

# Son durum
print("\n=== Skiller/ alti kategori detay ===")
for kat in sorted(os.listdir(HEDEF)):
    kat_yolu = HEDEF / kat
    if not kat_yolu.is_dir():
        continue
    md_sayisi = len(list(kat_yolu.glob("*.md")))
    alt_kategori = len([d for d in kat_yolu.iterdir() if d.is_dir()])
    print(f"  {kat:20s} | {md_sayisi:4d} .md | {alt_kategori} alt klasor")
