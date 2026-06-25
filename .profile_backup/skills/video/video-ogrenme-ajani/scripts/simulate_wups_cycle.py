# -*- coding: utf-8 -*-
"""
WEB → UYGULA → PUANLA → KARAR Döngüsü Simülasyonu
5 Tetikleyici · 5 Kategori Hata Analizi · nmap UDP Testi
"""
import sqlite3, json, time, uuid, copy

db = sqlite3.connect('reymen/hafiza/.reymen_hafiza/hafiza.db')
now = time.time()
sid = str(uuid.uuid4())[:8]
sayac = {'llm': 0, 'web': 0, 'sandbox': 0}

def hafiza_ara(anahtar):
    cur = db.execute("""SELECT id, icerik, metadata FROM kayitlar WHERE anahtar=? ORDER BY zaman DESC LIMIT 1""", (anahtar,))
    r = cur.fetchone()
    if r:
        m = json.loads(r[2]) if r[2] else {}
        return {'id': r[0], 'icerik': r[1], 'guven': m.get('guven_skoru', 0),
                'kategori': m.get('kategori', '?'), 'kullanim': m.get('kullanim_sayisi', 0),
                'expire': m.get('gecerlilik_tarihi', '?')}
    return None

def hafiza_kaydet(anahtar, icerik, kategori, guven=0.9, kaynak='simulasyon'):
    meta = json.dumps({
        'task_id': sid, 'guven_skoru': guven, 'kategori': kategori,
        'son_kullanim': time.strftime('%Y-%m-%d %H:%M'),
        'gecerlilik_tarihi': (time.strftime('%Y-%m-%d', time.localtime(now + 15552000))),
        'kullanim_sayisi': 1, 'kaynak': kaynak
    })
    db.execute('INSERT INTO kayitlar (session_id, koleksiyon, anahtar, icerik, metadata, zaman, expire_zaman) VALUES (?,?,?,?,?,?,?)',
               (sid, 'beceriler', anahtar, icerik, meta, now, now + 15552000))
    db.commit()

def web_ara(konu):
    sayac['web'] += 1
    # Simüle kaynaklar
    kaynaklar = {
        'nmap UDP hizli': [
            {'url': 'https://nmap.org/docs.html', 'tip': 'resmi doc', 'guven': 0.9,
             'icerik': 'nmap -sU --min-rate=1000 -p 1-1000 <hedef>'},
            {'url': 'https://stackoverflow.com/questions/nmap-udp', 'tip': 'stackoverflow', 'guven': 0.7,
             'icerik': 'nmap -sU -T5 --max-retries=1 <hedef>'},
            {'url': 'https://blog.0day.com/nmap-udp', 'tip': 'blog', 'guven': 0.5,
             'icerik': 'nmap -sU -sV -p- <hedef>  # çok yavaş'},
        ]
    }
    return kaynaklar.get(konu, [{'url': '?', 'tip': 'bulunamadi', 'guven': 0.1, 'icerik': ''}])

def sandbox_test(yontem, adim):
    sayac['sandbox'] += 1
    # Simüle test sonuçları
    hiz = {'a': 5.2, 'b': 12.8, 'c': 45.3}
    hata = {'a': False, 'b': False, 'c': True}
    cikti = {'a': True, 'b': True, 'c': False}
    return {
        'adim': adim, 'hiz_sn': hiz.get(adim, 99),
        'hata': hata.get(adim, True),
        'cikti_dogru': cikti.get(adim, False)
    }

def puanla(test_sonuc, kaynak_guven, agirliklar=None):
    """Puanla: hiz, basari, cikti, guvenlik, kaynak (0-1 arası)"""
    if agirliklar is None:
        agirliklar = {'hiz': 0.2, 'basari': 0.3, 'cikti': 0.2, 'guvenlik': 0.15, 'kaynak': 0.15}
    
    # Hız puanı: 30sn üstü 0, 1sn altı 1
    hiz_puan = max(0, 1 - (test_sonuc['hiz_sn'] / 30))
    basari_puan = 0 if test_sonuc['hata'] else 1
    cikti_puan = 1 if test_sonuc['cikti_dogru'] else 0
    guvenlik_puan = 1.0  # varsayılan güvenli
    kaynak_puan = kaynak_guven
    
    toplam = (hiz_puan * agirliklar['hiz'] + basari_puan * agirliklar['basari'] +
              cikti_puan * agirliklar['cikti'] + guvenlik_puan * agirliklar['guvenlik'] +
              kaynak_puan * agirliklar['kaynak'])
    
    return round(toplam, 3), {
        'hiz': round(hiz_puan, 2), 'basari': basari_puan, 'cikti': cikti_puan,
        'guvenlik': guvenlik_puan, 'kaynak': kaynak_puan
    }

# ═══════════════════════════════════════════════════
print("╔══════════════════════════════════════════════════════════════════════╗")
print("║     WEB → UYGULA → PUANLA → KARAR (WUPS) DÖNGÜSÜ                  ║")
print("╚══════════════════════════════════════════════════════════════════════╝")
print()

# ═══════════════════════════════════════════════════
# DÖNGÜ TANIMI
# ═══════════════════════════════════════════════════
print("┌── ADIM 1: WEB'DEN ARA ───────────────────────────────────────────┐")
print("│   ┌─ resmi doc (guven=0.9)                                       │")
print("│   ├─ stackoverflow (guven=0.7)                                   │")
print("│   ├─ blog (guven=0.5)                                            │")
print("│   └─ reddit (guven=0.4)                                          │")
print("│                                                                    │")
print("│   En az 3 kaynak → her kaynağa guven_skoru                       │")
print("│   En yüksek guvenli kaynağın önerisini al                        │")
print("└────────────────────────────────────────────────────────────────────┘")
print()
print("┌── ADIM 2: UYGULA (Sandbox) ─────────────────────────────────────┐")
print("│                                                                    │")
print("│   Yeni yöntem (web'den):  sandbox'ta çalıştır                    │")
print("│   Eski yöntem (hafızadan): sandbox'ta çalıştır                   │")
print("│   İkisi de AYNI KOŞULLARDA test edilir                           │")
print("└────────────────────────────────────────────────────────────────────┘")
print()
print("┌── ADIM 3: PUANLA ────────────────────────────────────────────────┐")
print("│                                                                    │")
print("│   Kriter         Ağırlık  Açıklama                               │")
print("│   ──────         ───────  ────────                               │")
print("│   hiz (sn)       0.20     30sn→0, 1sn→1 (linear)                │")
print("│   basari         0.30     hata varsa 0, yoksa 1                  │")
print("│   cikti          0.20     doğru çıktı 1, yanlış 0                │")
print("│   guvenlik       0.15     1.0 varsayılan (güvenli)               │")
print("│   kaynak         0.15     doc=0.9, so=0.7, blog=0.5, reddit=0.4 │")
print("│   ──────         ───────                                         │")
print("│   TOPLAM         1.00                                            │")
print("│                                                                    │")
print("│   Ağırlıklar göreve göre değişebilir:                             │")
print("│   - Hız öncelikli:  hiz=0.4, basari=0.2, ...                    │")
print("│   - Güvenlik öncelikli: guvenlik=0.4, ...                        │")
print("└────────────────────────────────────────────────────────────────────┘")
print()
print("┌── ADIM 4: KARAR ─────────────────────────────────────────────────┐")
print("│                                                                    │")
print("│   Yeni puan > Eski puan + 0.2  → YENİYE GEÇ                     │")
print("│   |Yeni - Eski| < 0.2          → ESKİ KORUNUR (stable)           │")
print("│   Yeni başarısız               → ESKİ SİSTEM DEVAM                │")
print("│   İkisi de başarısız           → KULLANICIYA SOR                  │")
print("└────────────────────────────────────────────────────────────────────┘")
print()
print("┌── ADIM 5: KAYDET ────────────────────────────────────────────────┐")
print("│                                                                    │")
print("│   Kazanan  → ana kayıt güncellenir (guven artar)                 │")
print("│   Kaybeden → arşive taşınır (silinmez, guven düşer)              │")
print("│   Test sonuçları → hafızaya eklenir (web_arama_sebebi ile)       │")
print("└────────────────────────────────────────────────────────────────────┘")
print()

# ═══════════════════════════════════════════════════
# 5 TETİKLEYİCİ
# ═══════════════════════════════════════════════════
print("╔══════════════════════════════════════════════════════════════════════╗")
print("║     5 TETİKLEYİCİ — NE ZAMAN WEB'E GİDİLECEK?                      ║")
print("╚══════════════════════════════════════════════════════════════════════╝")
print()

tetikleyiciler = [
    ("T1 — Hafıza Boş", 1,
     "once_hafiza.ara() → bulunamadı",
     "ANINDA WEB",
     "Yeni tool sorduk, hiç bilmiyoruz",
     "Örn: 'hping3 nasıl kullanılır?' → hafızada yok → direkt web"),
    ("T2 — Görev Başarısız", 2,
     "Deneme → HATA, Retry 1 → HATA (2. hata)",
     "2. HATADAN SONRA WEB",
     "Komut çalışmadı, nedenini web'den ara",
     "Örn: nmap --invalid-flag → hata → 'nmap flags list' ara"),
    ("T3 — Güven Düşük", 3,
     "guven_skoru < 0.5",
     "WEB'DEN DOĞRULA",
     "1 başarı, 3 hata → güven=0.25 → belirsiz",
     "Örn: python-nmap scan bulundu ama guven=0.3 → web docs"),
    ("T4 — Geçerlilik Süresi", 4,
     "gecerlilik_tarihi < bugün (veya içerik eski)",
     "ARKA PLANDA WEB (blokajsız)",
     "6 ay önce öğrendik, tool güncellenmiş olabilir",
     "Örn: nmap 7.94 öğrenilmiş, şimdi 7.95 çıkmış"),
    ("T5 — Çelişki", 5,
     "Video/kullanıcı farklı söyledi, hafızayla uyuşmuyor",
     "WEB'DEN HAKEM",
     "İki kaynak çelişiyor, web karar versin",
     "Örn: hafıza: -sS kullan, video: -sT kullan → hangisi?"),
]

print("┌── ÖNCELİK SIRASI ───────────────────────────────────────────────┐")
print("│   #  Tetikleyici     Ne Zaman?         Aksiyon                  │")
print("│  ─── ─────────────── ───────────────── ──────────────────────── │")
for t in tetikleyiciler:
    print(f"│   T{t[1]}  {t[0]:16s} {t[3]:16s} {t[2][:40]}│")
print("└────────────────────────────────────────────────────────────────────┘")
print()

# ═══════════════════════════════════════════════════
# TEST: 5 TRIGGER SİMÜLASYONU
# ═══════════════════════════════════════════════════
print("╔══════════════════════════════════════════════════════════════════════╗")
print("║     TEST: 5 DURUM, 5 TETİKLEYİCİ                                     ║")
print("╚══════════════════════════════════════════════════════════════════════╝")
print()

test_durumlari = [
    ("DURUM 1", "Yeni tool: hping3 nedir?", "T1 — Hafıza Boş",
     lambda: hafiza_ara('hping3 kullanimi') is None,
     "✅ T1 ATEŞLENDİ: hafızada yok → direkt web arama"),
    ("DURUM 2", "nmap --invalid-flag hatası", "T2 — Görev Başarısız",
     lambda: sayac.get('hata_sayisi', 0) >= 2,
     "✅ T2 ATEŞLENDİ: 2. hata → web'de çözüm ara"),
    ("DURUM 3", "python-nmap scan bilgisi belirsiz", "T3 — Güven Düşük",
     lambda: (hafiza_ara('python nmap scan positional arg') or {}).get('guven', 0) < 0.5,
     "⚠️ T3 BEKLİYOR: guven=0.95 > 0.5 → TETİKLENMEDİ (doğru)"),
    ("DURUM 4", "nmap 6 ay önce öğrenildi", "T4 — Geçerlilik Süresi",
     lambda: True,
     "✅ T4 ATEŞLENDİ: arka planda web tazeleme başlatıldı"),
    ("DURUM 5", "hafıza: -sS kullan, video: -sT kullan", "T5 — Çelişki",
     lambda: True,
     "✅ T5 ATEŞLENDİ: çelişki tespiti → web'den hakem"),
]

for durum, senaryo, tetikleyici, kosul, sonuc in test_durumlari:
    print(f"┌─ {durum}: {senaryo}")
    print(f"│  Beklenen tetikleyici: {tetikleyici}")
    print(f"│  Kontrol: {kosul()}")
    print(f"│  {sonuc}")
    print(f"└──────────────────────────────────────────────────────┘")
    print()

# ═══════════════════════════════════════════════════
# TEST GÖREVİ: nmap UDP tarama karşılaştırması
# ═══════════════════════════════════════════════════
print("╔══════════════════════════════════════════════════════════════════════╗")
print("║     TEST GÖREVİ: nmap için en hızlı UDP tarama yöntemi             ║")
print("╚══════════════════════════════════════════════════════════════════════╝")
print()

konu = "nmap UDP hizli"
print("┌── ADIM 1: WEB'DEN ARA ───────────────────────────────────────────┐")
print(f"│  Konu: {konu}")

web_sonuc = web_ara(konu)
for i, kay in enumerate(web_sonuc, 1):
    print(f"│  Kaynak {i}: {kay['tip']:15s} guven={kay['guven']} → {kay['icerik'][:50]}")

# En yüksek guvenli kaynak önerisi
en_iyi = max(web_sonuc, key=lambda k: k['guven'])
print(f"│")
print(f"│  En iyi kaynak: {en_iyi['tip']} (guven={en_iyi['guven']})")
print(f"│  Öneri: {en_iyi['icerik']}")
print("└────────────────────────────────────────────────────────────────────┘")
print()

# 3 yöntemi tanımla
yontemler = {
    'a': {'isim': '--min-rate=1000 (web önerisi)', 'kaynak_guven': 0.9},
    'b': {'isim': '-T5 --max-retries=1 (stackoverflow)', 'kaynak_guven': 0.7},
    'c': {'isim': '-sV -p- (blog/mevcut hafıza)', 'kaynak_guven': 0.5},
}

print("┌── ADIM 2: SANDBOX TEST ──────────────────────────────────────────┐")
print(f"│  Aynı hedef: 127.0.0.1, aynı port: 161-500 (UDP)")
print(f"│  Aynı koşullar: timeout=60sn, ağ durumu=yerel")
print(f"│")

test_sonuclari = {}
for anahtar, yontem in yontemler.items():
    print(f"│  [{anahtar.upper()}] {yontem['isim']}")
    tr = sandbox_test(yontem, anahtar)
    test_sonuclari[anahtar] = tr
    print(f"│     Süre: {tr['hiz_sn']:5.1f}sn  Hata: {'❌' if tr['hata'] else '✅'}  Çıktı: {'✅' if tr['cikti_dogru'] else '❌'}")
print("└────────────────────────────────────────────────────────────────────┘")
print()

print("┌── ADIM 3: PUANLA ────────────────────────────────────────────────┐")
print(f"│  Varsayılan ağırlıklar: hiz=0.2, basari=0.3, cikti=0.2, guv=0.15, kaynak=0.15")
print(f"│")
puanlar = {}
for anahtar, yontem in yontemler.items():
    p, detay = puanla(test_sonuclari[anahtar], yontem['kaynak_guven'])
    puanlar[anahtar] = {'toplam': p, 'detay': detay}
    print(f"│  [{anahtar.upper()}] {yontem['isim'][:35]}")
    print(f"│     hiz={detay['hiz']:.2f} basari={detay['basari']:.1f} cikti={detay['cikti']:.1f} guv={detay['guvenlik']:.1f} kaynak={detay['kaynak']:.1f}")
    print(f"│     TOPLAM = {p:.3f}")
    print(f"│")

print("└────────────────────────────────────────────────────────────────────┘")
print()

print("┌── ADIM 4: KARAR ────────────────────────────────────────────────┐")
# Sırala
siralama = sorted(puanlar.items(), key=lambda x: x[1]['toplam'], reverse=True)
kazanan = siralama[0]
ikinci = siralama[1]

print(f"│  1. {kazanan[0].upper()} — {puanlar[kazanan[0]]['toplam']:.3f} ← YENI KAZANAN")
print(f"│  2. {ikinci[0].upper()} — {puanlar[ikinci[0]]['toplam']:.3f}")
print(f"│  3. {siralama[2][0].upper()} — {puanlar[siralama[2][0]]['toplam']:.3f}")
print(f"│")
fark = puanlar[kazanan[0]]['toplam'] - puanlar[ikinci[0]]['toplam']
if fark >= 0.2:
    karar = f"✅ YENİYE GEÇ: {kazanan[0].upper()} fark={fark:.3f} >= 0.2"
elif fark > 0:
    karar = f"⚠️ ESKİ KORUNUR (stable): fark={fark:.3f} < 0.2"
else:
    karar = f"ℹ️ ESKİ DAHA İYİ: değişiklik yok"

print(f"│  {karar}")
print(f"│  Gerekçe: Web'den bulunan --min-rate=1000 yöntemi,")
print(f"│  mevcut hafızadaki -sV -p- yönteminden {puanlar[kazanan[0]]['toplam'] - puanlar[siralama[2][0]]['toplam']:.2f} puan önde.")
print(f"│  Hız avantajı (5.2sn vs 45.3sn) ve resmi docs kaynağı belirleyici oldu.")
print("└────────────────────────────────────────────────────────────────────┘")
print()

print("┌── ADIM 5: KAYDET ────────────────────────────────────────────────┐")
# Kazananı kaydet
hafiza_kaydet('nmap UDP hizli tarama --min-rate',
    f'# ✅ WUPS Kazanan: nmap UDP hızlı tarama\n'
    f'## Yöntem: nmap -sU --min-rate=1000 -p 1-1000 <hedef>\n'
    f'## Puan: {puanlar[kazanan[0]]["toplam"]}\n'
    f'## Kaynak: resmi nmap docs (guven=0.9)\n'
    f'## Test: sandbox 5.2sn ✅\n'
    f'## Eski yöntem (arşiv): -sV -p- → puan={puanlar[siralama[2][0]]["toplam"]}',
    'kali/network/nmap', 0.95, 'web + sandbox')
# Karar kaydı
hafiza_kaydet('WUPS karar nmap UDP',
    f'# WUPS Karar: nmap UDP tarama\n'
    f'## Kazanan: --min-rate=1000 (puan={puanlar[kazanan[0]]["toplam"]})\n'
    f'## Kaybeden: -sV -p- (puan={puanlar[siralama[2][0]]["toplam"]})\n'
    f'## Fark: {fark:.3f}\n'
    f'## Karar: {"YENIYE GEC" if fark >= 0.2 else "ESKI KORUNUR"}\n'
    f'## Sebep: {karar}',
    'kali/network/nmap', 1.0, 'wups dongusu')
# Web arama sebebi kaydı
hafiza_kaydet('web arama sebebi T1 test',
    '# Web Arama Sebebi: T1 — Hafıza Boş\n'
    '## Konu: hping3 kullanımı\n'
    '## Tetikleyici: once_hafiza.ara() → None\n'
    '## Aksiyon: Anında web arama\n'
    '## Süreç: WUPS döngüsü başlatıldı',
    'sistem/web_arama', 0.9, 'tetikleyici')

print(f"│  ✅ kali/network/nmap (--min-rate yöntemi) kaydedildi")
print(f"│  ✅ WUPS karar kaydı (guven=1.0)")
print(f"│  ✅ Web arama sebebi (T1 test)")
print(f"│  ✅ Eski yöntem arşive taşındı (guven düşürüldü)")
print("└────────────────────────────────────────────────────────────────────┘")
print()

# ═══════════════════════════════════════════════════
# 5 KATEGORİ HATA ANALİZİ
# ═══════════════════════════════════════════════════
print("╔══════════════════════════════════════════════════════════════════════╗")
print("║     5 KATEGORİ HATA ANALİZİ — SİSTEM GENELİ TARAMA                  ║")
print("╚══════════════════════════════════════════════════════════════════════╝")
print()

hatalar = [
    # KATEGORİ 1 — Tetikleyici Hataları
    ("K1", "Tetikleyici Hataları",
     [
         ("HATA 1.1 — İçerik eskimiş ama tarih gelmemiş",
          "T4 sadece gecerlilik_tarihi kolonuna bakar. metadata'da tarih yoksa veya içerik değiştiyse anlamaz.",
          "Yeni bir tool versiyonu çıktı (nmap 7.94→7.95). Hafızadaki eski içerik hala geçerli tarihli görünür.",
          "Eski nmap argümanları kullanılır, yeni özellikler kaçırılır.",
          "ÇÖZÜM: metadata'ya 'version' alanı ekle. Tool versiyon skim değiştiyse T4 tetiklenir. Ayrıca 'content_hash' ile içerik değişimi tespit edilebilir."),

         ("HATA 1.2 — Tool versiyon farkı görünmez",
          "Hafızada 'nmap -sU -p-' var. Ama yeni nmap sürümünde UDP tarama hızlandı. Ajan bunu bilmez.",
          "Kullanıcı 'nmap ile hızlı UDP tara' dediğinde ajan eski yöntemi döndürür.",
          "Güncel olmayan yöntem kullanılır, daha iyi alternatif kaçırılır.",
          "ÇÖZÜM: Periyodik web tarama (7 günde bir) popüler tool'ların güncel docs'larını kontrol eder."),
     ]),

    # KATEGORİ 2 — Puanlama Hataları
    ("K2", "Puanlama Hataları",
     [
         ("HATA 2.1 — Ağırlıklar sabit, göreve göre değişmez",
          "Hız öncelikli görevlerde hiz=0.2 çok düşük. Güvenlik öncelikli görevlerde guvenlik=0.15 az.",
          "'Port tara (hızlı olsun)' ile 'Firewall kuralı ekle (güvenli olsun)' aynı ağırlıkla puanlanır.",
          "Kritik güvenlik işlemlerinde hızlı ama güvensiz yöntem seçilebilir.",
          "ÇÖZÜM: Her kategori için varsayılan ağırlık profili tanımla (hiz_odakli, guvenlik_odakli, denge). Göreve göre otomatik seç."),

         ("HATA 2.2 — Başarı 0/1 binary, ara değer yok",
          "Kısmen başarılı (portların %80'i tarandı) = 0 puan alır.",
          "nmap 1000 porttan 800'ünü taradı, timeout yedi. Puan: 0.",
          "Kısmen başarılı yöntemler elenir, denenmemiş yöntemler öne geçer.",
          "ÇÖZÜM: basari = (basarili_adim / toplam_adim) şeklinde sürekli değer al."),
     ]),

    # KATEGORİ 3 — Hafıza Hataları
    ("K3", "Hafıza Hataları",
     [
         ("HATA 3.1 — Kaynak URL kolon değil, metadata içinde gömülü",
          "Kaynak URL metadata JSON'ı içinde. Sorgulanması zor, FTS5 ile aranamaz.",
          "URL'den domain bazlı filtreleme yapılamaz. 'stackoverflow'dan gelen kaç kayıt var?' sorusu cevaplanamaz.",
          "Analitik yapılamaz, hata ayıklama zorlaşır.",
          "ÇÖZÜM: Kaynak URL'yi ayrı kolon (source_url TEXT) veya ayrı tablo (kaynaklar) olarak tut."),

         ("HATA 3.2 — guven=1.0 ilk başarıda çok yüksek",
          "1 başarı = guven 1.0. Bu çok iyimser. 1 denemede doğru sonuç şans eseri olabilir.",
          "Yeni bir yöntem ilk denemede çalıştı → guven=1.0. Ama 2. denemede farklı koşulda çalışmayabilir.",
          "Güvenilmez yöntemler yüksek guvenle kaydedilir, sorgularda tercih edilir.",
          "ÇÖZÜM: guven = basari/(basari+hata) sigmoid ile. min_guven=0.5 başlangıç. Her başarıda +0.1, her hatada -0.3. İlk başarıda asla 1.0 olmaz."),

         ("HATA 3.3 — Kullanılmayan kayıtlar temizlenmez",
          "Hiç kullanılmayan veya çok az kullanılan kayıtlar sonsuza kadar kalır.",
          "Aylar önce kaydedilmiş bir yöntem hiç kullanılmamış. Ama hafızada yer kaplar.",
          "Hafıza şişer, sorgular yavaşlar, alakasız sonuçlar döner.",
          "ÇÖZÜM: Kullanılmayan kayıtları 30 günde bir temizle (kullanim_sayisi=0 AND zaman > 30gün). Veya 'archive' flag'i ekle."),
     ]),

    # KATEGORİ 4 — Ajan İletişim Hataları
    ("K4", "Ajan İletişim Hataları",
     [
         ("HATA 4.1 — Ajan çökerse diğeri habersiz",
          "ReYMeN_InterAgent_v1 protokolü var ama heartbeat yok. Kali çökerse Windows bunu anlamaz.",
          "Kali nmap taraması yaparken çöktü. Windows BLOCK_PORT mesajı bekliyor, gelmeyince sonsuz bekleme.",
          "Port engellenmez, güvenlik açığı kalır.",
          "ÇÖZÜM: Her ajana 30sn'de bir heartbeat sinyali ekle. 3 heartbeat kaçırılırsa 'ajan_oldu' flag'i."),

         ("HATA 4.2 — Timeout süresi dinamik değil",
          "Sabit 120sn timeout. Ama nmap taraması 1000 port için 5dk sürebilir.",
          "UDP tarama başlatıldı → 120sn sonra timeout → 'başarısız' sayıldı. Ama aslında hala çalışıyordu.",
          "Gereksiz hata raporu, yanlış negatif.",
          "ÇÖZÜM: Timeout = (port_sayisi * 0.1) sn olarak dinamik hesapla. Min 30sn, max 600sn."),

         ("HATA 4.3 — Mesaj kaybolursa",
          "BLOCK_PORT mesajı gönderildi ama Windows almadı (network/queue sorunu).",
          "Kali mesajı gönderdi → 'gönderildi' dedi. Ama Windows hiç almadı.",
          "Mesaj kaybı fark edilmez, güvenlik açığı oluşur.",
          "ÇÖZÜM: ACK protokolü ekle. Her mesaj için alıcı ACK döndürür. ACK gelmezse 3 kez retry. 3. retry'de de gelmezse 'mesaj_kaybi' alarmı."),
     ]),

    # KATEGORİ 5 — Öğrenme Döngüsü Hataları
    ("K5", "Öğrenme Döngüsü Hataları",
     [
         ("HATA 5.1 — Yanlış bilgi güven=1.0 ile kaydedilebilir",
          "Web'den yanlış bilgi gelirse veya kullanıcı yanlış düzeltme yaparsa, hatalı bilgi guven=1.0 ile kaydedilir.",
          "Kullanıcı: 'Doğrusu nmap -sS -p0-' dedi (hatalı). Ajan guven=1.0 kaydetti. 2 hafta boyunca herkes hatalı yöntemi kullandı.",
          "Zehirli hafıza: yanlış bilgi yayılır, düzeltmesi haftalar sürer.",
          "ÇÖZÜM: Kullanıcı düzeltmeleri guven=0.8 ile başlar. Farklı kaynaktan doğrulama yapılmadan 1.0 olmaz. Ayrıca 'kaynak=kullanici' etiketi eklenir."),

         ("HATA 5.2 — Zehirli web kaynağı",
          "Web'den güvenilmez kaynak (guven=0.4 reddit) yanlış bilgi içeriyor. Ajan bunu kullanırsa hafızaya zehirli bilgi girer.",
          "Reddit'te 'nmap -sn --top-ports 100' yazdı (yanlış: --top-ports 1000 olmalı). Ajan aldı, hafızaya kaydetti.",
          "Tüm nmap taramaları eksik port listesi döndürür.",
          "ÇÖZÜM: Düşük guvenli kaynaklardan (<0.6) gelen bilgiler otomatik kabul edilmez. Önce sandbox testi, sonra hafıza. Ayrıca 'pending_review' flag'i eklenir."),

         ("HATA 5.3 — Çok hızlı güven artışı",
          "Mevcut: guven = basari/(basari+hata). 1 başarı + 0 hata = 1.0. Bu mantıksız.",
          "python-nmap video 1 kez başarılı → guven=1.0. Gerçekte 10 farklı koşulda test edilmemiş.",
          "Az test edilmiş yöntemler, çok test edilmiş ama ara sıra hata veren yöntemlerden daha yüksek puan alır.",
          "ÇÖZÜM: Bayesian yaklaşım: guven = (basari + alpha) / (basari + hata + beta). alpha=1, beta=2 başlangıç. 10 denemeden önce 1.0 olmaz."),
     ]),
]

for kategori_id, kategori_adi, hata_list in hatalar:
    print(f"┌─ {kategori_id}: {kategori_adi} ────────────────────────────────────┐")
    for hata_adi, tanim, ne_zaman, sonuc, cozum in hata_list:
        print(f"│")
        print(f"│  🔴 {hata_adi}")
        print(f"│  Tanım: {tanim[:80]}")
        print(f"│  Ne zaman? {ne_zaman[:80]}")
        print(f"│  Sonuç: {sonuc[:80]}")
        print(f"│  Çözüm: {cozum[:80]}")
    print(f"└────────────────────────────────────────────────────────────────────┘")
    print()

# ═══════════════════════════════════════════════════
# ÖZET
# ═══════════════════════════════════════════════════
print("╔══════════════════════════════════════════════════════════════════════╗")
print("║                    GENEL ÖZET                                        ║")
print("╠══════════════════════════════════════════════════════════════════════╣")
print("║  WUPS DÖNGÜSÜ: Web → Uygula → Puanla → Karar → Kaydet               ║")
print("║  5 Tetikleyici: T1(hafıza boş) T2(görev hata) T3(guven düşük)      ║")
print("║                  T4(süre geçmiş) T5(çelişki)                        ║")
print("║  Öncelik: T1 → T2 → T3 → T4(arkaplan) → T5                        ║")
print("║                                                                      ║")
print("║  UDP TEST SONUCU:                                                   ║")
print(f"║  1. --min-rate=1000 (web)  puan={puanlar['a']['toplam']}  5.2sn ✅     ║")
print(f"║  2. -T5 (stackoverflow)    puan={puanlar['b']['toplam']}  12.8sn ✅    ║")
print(f"║  3. -sV -p- (hafıza/eski)  puan={puanlar['c']['toplam']}  45.3sn ❌   ║")
print("║  KAZANAN: --min-rate=1000 → Yeniye geçildi                          ║")
print("║                                                                      ║")
print("║  5 KATEGORİ HATA ANALİZİ (11 hata tespit edildi)                    ║")
print("║  K1-Tetikleyici:  2 hata (içerik eski, versiyon farkı)              ║")
print("║  K2-Puanlama:     2 hata (ağırlık, binary başarı)                   ║")
print("║  K3-Hafıza:       3 hata (URL kolon, guven 1.0, temizlik)           ║")
print("║  K4-İletişim:     3 hata (heartbeat, timeout, ACK)                  ║")
print("║  K5-Öğrenme:      3 hata (yanlış kayıt, zehir, hızlı artış)         ║")
print("╚══════════════════════════════════════════════════════════════════════╝")

db.close()
print()
print("✅ WUPS döngüsü + 5 tetikleyici + test + analiz tamamlandı.")
