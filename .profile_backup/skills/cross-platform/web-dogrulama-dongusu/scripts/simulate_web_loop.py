# -*- coding: utf-8 -*-
"""
WEB -> UYGULA -> PUANLA -> KARAR Dongusu Simulasyonu
5 tetikleyici testi + nmap UDP tarama karsilastirmasi
"""
import sqlite3, json, time

sayac = {'llm': 0, 'web': 0, 'sandbox': 0}
db_path = 'reymen/hafiza/.reymen_hafiza/hafiza.db'

def web_ara(sorgu, hedef_kaynak=3):
    sayac['web'] += 1
    kaynaklar = [
        ("nmap.org docs", 0.9, "nmap -sU --top-ports 100 " + sorgu),
        ("stackoverflow", 0.7, "nmap -sU -p 1-1000 --max-retries 1 " + sorgu),
        ("blog", 0.5, "nmap -sU -T5 -p 53,67,123,161 " + sorgu),
    ]
    return kaynaklar[:hedef_kaynak]

def sandbox_test(yontem, yontem_adi):
    sayac['sandbox'] += 1
    sonuclar = {
        "--top-ports 100": {"hiz": 0.9, "basari": 1.0, "cikti": 1.0, "guvenlik": 0.8, "kaynak": 0.9, "sure": "2.3sn"},
        "-sU -p 1-1000":   {"hiz": 0.5, "basari": 0.8, "cikti": 0.7, "guvenlik": 1.0, "kaynak": 0.9, "sure": "15.1sn"},
        "--max-retries 1": {"hiz": 0.7, "basari": 0.9, "cikti": 0.8, "guvenlik": 0.7, "kaynak": 0.7, "sure": "8.5sn"},
        "-T5":             {"hiz": 0.8, "basari": 0.7, "cikti": 0.6, "guvenlik": 0.6, "kaynak": 0.5, "sure": "5.2sn"},
    }
    return sonuclar.get(yontem, {"hiz": 0, "basari": 0, "cikti": 0, "guvenlik": 0, "kaynak": 0, "sure": "?"})

def puanla(sonuc):
    return sonuc['hiz']*0.15 + sonuc['basari']*0.3 + sonuc['cikti']*0.25 + sonuc['guvenlik']*0.2 + sonuc['kaynak']*0.1

def karar_ver(yeni_puan, eski_puan, yeni_basarili, eski_basarili):
    if not yeni_basarili and not eski_basarili:
        return "KULLANICIYA_SOR", "Ikisi de basarisiz"
    if not yeni_basarili:
        return "ESKI_KORUN", "Yeni basarisiz -> eski devrede"
    if yeni_puan - eski_puan > 0.2:
        return "YENIYE_GEC", "Fark {:.2f} > 0.2".format(yeni_puan-eski_puan)
    else:
        return "ESKI_KORUN", "Fark {:.2f} < 0.2".format(yeni_puan-eski_puan)

def turkce_duzelt(s):
    return s.lower().replace("c","c").replace("s","s").replace("g","g").replace("u","u").replace("o","o").replace("i","i")

# ----------------------------------------------------------
print("")
print("=== WEB -> UYGULA -> PUANLA -> KARAR DONGUSU ===")
print("===== 5 Tetikleyici Testi + nmap UDP Tarama =====")
print("")

# -- 5 TETIKLEYICI TESTI ---------------------------------
print("====== 5 TETIKLEYICI TESTI ======")
print("")

tetikleyiciler = [
    ("T1: Hafiza Bos", "hafiza_bos",
     "once_hafiza.ara('nmap UDP tarama') -> bulunamadi",
     "ANINDA WEB", "ATESLENDI"),
    ("T2: Guven Dusuk", "guven_dusuk",
     "once_hafiza.ara(...) -> guven=0.25 < 0.5",
     "WEB DOGRULA", "ATESLENDI"),
    ("T3: Gorev Basarisiz", "gorev_basarisiz",
     "Deneme 1 -> HATA, Retry 1 -> HATA (2. hata)",
     "2. HATADA WEB", "ATESLENDI"),
    ("T4: Gecerlilik Suresi", "gecerlilik_suresi",
     "son_kullanim = 2025-12-18 < bugun (2026-06-21)",
     "ARKA PLANDA WEB", "ATESLENDI"),
    ("T5: Celiski", "celiski",
     "Video: -sU --top-ports, Hafiza: -sU -p 1-1000",
     "HAKEM WEB", "ATESLENDI"),
]

print("| {:<5s} {:<20s} {:<45s} {:<20s} {:<15s} |".format("#", "Ad", "Kosul", "Aksiyon", "Sonuc"))
print("|{:-<5s}|{:-<20s}|{:-<45s}|{:-<20s}|{:-<15s}|".format("","","","",""))
for i, (ad, _, kosul, aksiyon, sonuc) in enumerate(tetikleyiciler, 1):
    print("| {:<5d} {:<20s} {:<45s} {:<20s} {:<15s} |".format(i, ad, kosul[:45], aksiyon, sonuc))
print("")

print("ONCELIK SIRASI:")
print("  1. Hafiza bos       -> ANINDA web (bekleme yok)")
print("  2. Gorev basarisiz  -> 2. hatada web (hizli)")
print("  3. Guven < 0.5      -> web (oncelikli)")
print("  4. Gecerlilik gecmis -> ARKA PLANDA web")
print("  5. Celiski          -> web (hakem karar)")
print("")

# -- SENARYO: nmap UDP tarama ---------------------------
print("=== SENARYO: nmap icin en hizli UDP tarama yontemi ===")
print("")

print("ADIM 1: TETIKLEYICI KONTROL")
print("  Sorgu: once_hafiza.ara('nmap UDP tarama')")
print("  Sonuc: BULUNAMADI (hafizada nmap UDP kaydi yok)")
print("  -> TETIKLEYICI 1: Hafiza Bos -> ANINDA WEB")
print("")

print("ADIM 2: WEB'DEN ARA")
kaynaklar = web_ara("127.0.0.1", 3)
print("| {:<25s} {:<10s} {:<45s} |".format("Kaynak", "Guven", "Yontem"))
print("|{:-<25s}|{:-<10s}|{:-<45s}|".format("","",""))
for kaynak, guven, yontem in kaynaklar:
    print("| {:<25s} {:<10.1f} {:<45s} |".format(kaynak, guven, yontem))
print("  WEB cagrisi: {} (3 kaynak tarandi)".format(sayac['web']))
print("")

print("ADIM 3: UYGULA (Sandbox)")
eski_yontem = "-sU -p 1-1000"
eski_sonuc = sandbox_test(eski_yontem, "ESKI")
eski_puan = puanla(eski_sonuc)

print("  ESKI YONTEM (hafizada mevcut):")
print("  nmap {} 127.0.0.1".format(eski_yontem))
print("  -> Hiz: {}, Basari: {}, Cikti: {}, Guv: {}, Kaynak: {}".format(
    eski_sonuc['hiz'], eski_sonuc['basari'], eski_sonuc['cikti'],
    eski_sonuc['guvenlik'], eski_sonuc['kaynak']))
print("  -> Sure: {}".format(eski_sonuc['sure']))
print("")

yeni_yontem = "--top-ports 100"
yeni_sonuc = sandbox_test(yeni_yontem, "YENI")
yeni_puan = puanla(yeni_sonuc)

print("  YENI YONTEM (web'den: nmap.org docs):")
print("  nmap -sU {} 127.0.0.1".format(yeni_yontem))
print("  -> Hiz: {}, Basari: {}, Cikti: {}, Guv: {}, Kaynak: {}".format(
    yeni_sonuc['hiz'], yeni_sonuc['basari'], yeni_sonuc['cikti'],
    yeni_sonuc['guvenlik'], yeni_sonuc['kaynak']))
print("  -> Sure: {}".format(yeni_sonuc['sure']))
print("  Sandbox testleri: {}".format(sayac['sandbox']))
print("")

print("ADIM 4: PUANLA")
print("  FORMUL: PUAN = hiz*0.15 + basari*0.3 + cikti*0.25 + guvenlik*0.2 + kaynak*0.1")
print("")
kriter_isim = {"hiz": "Hiz", "basari": "Basari", "cikti": "Cikti", "guvenlik": "Guvenlik", "kaynak": "Kaynak"}
print("| {:<12s} {:<10s} {:<12s} {:<12s} |".format("Kriter", "Agirlik", "ESKI", "YENI"))
print("|{:-<12s}|{:-<10s}|{:-<12s}|{:-<12s}|".format("","","",""))
for anahtar, agirlik in [("hiz",0.15),("basari",0.3),("cikti",0.25),("guvenlik",0.2),("kaynak",0.1)]:
    print("| {:<12s} {:<10.2f} {:<12.2f} {:<12.2f} |".format(kriter_isim[anahtar], agirlik, eski_sonuc[anahtar], yeni_sonuc[anahtar]))
print("|{:-<12s}|{:-<10s}|{:-<12s}|{:-<12s}|".format("","","",""))
print("| {:<12s} {:<10s} {:<12.2f} {:<12.2f} |".format("TOPLAM", "", eski_puan, yeni_puan))
print("")

print("ADIM 5: KARAR")
karar, gerekce = karar_ver(yeni_puan, eski_puan, True, True)
print("  ESKI PUAN: {:.2f}".format(eski_puan))
print("  YENI PUAN: {:.2f}".format(yeni_puan))
print("  FARK:     {:.2f}".format(yeni_puan-eski_puan))
print("  ESIK:     0.20")
print("  KARAR: {}".format(karar))
print("  GEREKCE: {}".format(gerekce))
if karar == "YENIYE_GEC":
    print("  -> Yeni yontem kazandi. Hafizaya ekleniyor...")
    print("  -> Eski yontem arsive tasiniyor (flag_udp=1)...")
elif karar == "ESKI_KORUN":
    print("  -> Eski yontem korunuyor.")
    print("  -> Yeni yontem de ekleniyor (alternatif olarak)...")
print("")

# -- WEB ARAMA SEBEBI ----------------------------------
print("====== WEB ARAMA SEBEBI (metadata) ======")
sebepler = {
    "hafiza_bos": "once_hafiza.ara() -> bulunamadi, aninda web'e gidildi",
    "guven_dusuk": "guven_skoru=0.25 < 0.5, web'den dogrulama yapildi",
    "gorev_basarisiz": "Deneme 1 hata + Retry 1 hata, 2. hatada web'e gidildi",
    "gecerlilik_suresi": "son_kullanim=2025-12-18 < 2026-06-21, arka planda tazeleme",
    "celiski": "Video farkli yontem gosterdi, hafizadakiyle uyusmazlik, hakem web karari",
}
print("| {:<20s} {:<60s} |".format("Sebep", "Aciklama"))
print("|{:-<20s}|{:-<60s}|".format("",""))
for sebep, aciklama in sebepler.items():
    print("| {:<20s} {:<60s} |".format(sebep, aciklama))
print("")

# -- OZET ----------------------------------------------
print("========================================")
print("                OZET")
print("========================================")
print("")
print("  5 TETIKLEYICI: 5/5 ATESLENDI")
print("")
print("  | # | Tetikleyici      | Sonuc    |")
print("  |---|------------------|----------|")
print("  | 1 | Hafiza Bos      | ANINDA   |")
print("  | 2 | Gorev Basarisiz | 2.hata   |")
print("  | 3 | Guven < 0.5     | ONCELIKLI|")
print("  | 4 | Gecerlilik      | ARKA PLAN|")
print("  | 5 | Celiski         | HAKEM    |")
print("")
print("  SENARYO: nmap UDP tarama")
print("  | ESKI: -sU -p 1-1000              -> {:.2f} puan".format(eski_puan))
print("  | YENI: --top-ports 100 (nmap.org) -> {:.2f} puan".format(yeni_puan))
print("  | KARAR: {} ({})".format(karar, gerekce))
print("")
print("  LLM: {} | WEB: {} | Sandbox: {}".format(sayac['llm'], sayac['web'], sayac['sandbox']))
print("  Maliyet: 0 TL (tumu tool/formul bazli)")
print("")
print("  SKILL: cross-platform/web-dogrulama-dongusu")
print("")
print("  HAFIZA KAYIT FORMATI:")
print("  {")
print('    "web_arama_sebebi": "hafiza_bos",')
print('    "arama_detayi": "once_hafiza.ara() -> bulunamadi",')
print('    "kaynak_sayisi": 3,')
print('    "en_iyi_kaynak": "nmap.org docs (guven=0.9)",')
print('    "puanlar": {...}')
print("  }")
print("")
print("Simulasyon tamamlandi.")
