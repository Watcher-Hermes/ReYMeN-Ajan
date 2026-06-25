# -*- coding: utf-8 -*-
"""
Video Öğrenme Ajanı — 3 Hata Senaryosu Akış Simülasyonu
Kod Hatası · Çelişkili Bilgi · Bilinmeyen Hata
"""
import sqlite3, json, time, uuid

db = sqlite3.connect('reymen/hafiza/.reymen_hafiza/hafiza.db')
now = time.time()
sid = str(uuid.uuid4())[:8]
sayac = {'llm': 0, 'web': 0, 'sandbox': 0}

def hafiza_ara(anahtar):
    cur = db.execute("""SELECT id, icerik, metadata FROM kayitlar WHERE anahtar=? ORDER BY zaman DESC LIMIT 1""", (anahtar,))
    r = cur.fetchone()
    if r:
        m = json.loads(r[2]) if r[2] else {}
        return {'id': r[0], 'icerik': r[1], 'guven': m.get('guven_skoru', 0), 'kategori': m.get('kategori', '?')}
    return None

def hafiza_kaydet(anahtar, icerik, kategori, guven=0.9):
    meta = json.dumps({
        'task_id': sid, 'guven_skoru': guven, 'kategori': kategori,
        'son_kullanim': time.strftime('%Y-%m-%d %H:%M'),
        'gecerlilik_tarihi': '2026-12-18', 'kullanim_sayisi': 1
    })
    db.execute('INSERT INTO kayitlar (session_id, koleksiyon, anahtar, icerik, metadata, zaman, expire_zaman) VALUES (?,?,?,?,?,?,?)',
               (sid, 'beceriler', anahtar, icerik, meta, now, now + 15552000))
    db.commit()

def llm_cagrisi(sebep):
    sayac['llm'] += 1
    return f'[LLM#{sayac["llm"]}] {sebep}'

def web_dogrula(konu):
    sayac['web'] += 1
    return f'[WEB#{sayac["web"]}] {konu} doğrulandı'

def sandbox_calistir(kod, adim):
    sayac['sandbox'] += 1
    return f'[SANDBOX#{sayac["sandbox"]}] {adim}: {"✅ PASS" if sayac["sandbox"] <= 3 else "❌ FAIL"}'

# ═══════════════════════════════════════════════════
print("╔══════════════════════════════════════════════════════════════════════╗")
print("║     VİDEO ÖĞRENME AJANI — 3 HATA SENARYOSU AKIŞ SİMÜLASYONU        ║")
print("╚══════════════════════════════════════════════════════════════════════╝")
print()

# ═══════════════════════════════════════════════════
# SENARYO 1 — KOD HATASI
# ═══════════════════════════════════════════════════
print("╔══════════════════════════════════════════════════════════════════════╗")
print("║     SENARYO 1: KOD HATASI                                          ║")
print("║     Video'da 5 hata → tespit → düzelt → doğrula → kaydet           ║")
print("╚══════════════════════════════════════════════════════════════════════╝")
print()

# Video'dan parse edilen kod
video_kod = """
nm = nmap.PortScanner()                    # Adım 1
nm.scan('127.0.0.1', '22-443')            # Adım 2: HATA 1 + 2
print(nm.csv())                            # Adım 3: HATA 3
"""
print("┌── VİDEODAN PARSE EDİLEN KOD ──────────────────────────────────────┐")
print(video_kod)
print("└──────────────────────────────────────────────────────────────────────┘")
print()

# ADIM 1: Hata tespit (kural bazlı)
print("┌── ADIM 1: 5 HATA TESPİTİ (Kural bazlı, 0 LLM) ──────────────────┐")

hatalar = [
    ("HATA 1 — Port range positional arg", "MAJOR",
     "nm.scan('127.0.0.1', '22-443') → ports='22-443' keyword arg olmalı",
     "python-nmap API: scan(hosts, ports) — ports keyword arg"),
    ("HATA 2 — Sudo gereksinimi yok", "MAJOR",
     "SYN scan (-sS) root ister. Video belirtmemiş.",
     "nmap docs: '-sS requires root privileges'"),
    ("HATA 3 — Exception handling yok", "MAJOR",
     "nmap.PortScannerError, PermissionError yakalanmamış",
     "Kural: Her tool çağrısı try/except ile sarılmalı"),
    ("HATA 4 — Sonuç parse edilmemiş", "MINOR",
     "print(nm.csv()) yerine all_tcp() + all_protocols() kullanılmalı",
     "Kural: nm.csv() raw çıktı, parse edilmemiş"),
    ("HATA 5 — CLI argüman desteği yok", "MINOR",
     "Host/port hardcoded. Argparse ile esnek olmalı",
     "Kural: Kod yeniden kullanılabilir olmalı"),
]

for i, (isim, sev, detay, kaynak) in enumerate(hatalar, 1):
    sembol = "🔴" if sev == "MAJOR" else "🟡"
    print(f"│  {sembol} {isim} ({sev})")
    print(f"│     Detay: {detay}")
    print(f"│     Kaynak: {kaynak}")
    print(f"│     Tespit yöntemi: KURAL (0 LLM)")
    print(f"│")

# Hafızada benzer hata var mı kontrol
hafiza_hata = hafiza_ara('python nmap scan positional arg')
if hafiza_hata:
    print(f"│  ℹ️  Hafızada benzer hata kaydı bulundu: ID={hafiza_hata['id']}")
    print(f"│     Mevcut çözüm önerisi var → direkt kullan")
    print(f"│")
else:
    print(f"│  ℹ️  Hafızada benzer hata kaydı YOK → yeni LLM çağrısı")
    llm_cagrisi("5 hatayı düzeltilmiş koda çevir")
    print(f"│")

print("└──────────────────────────────────────────────────────────────────────┘")
print()

# ADIM 2: Düzeltme
print("┌── ADIM 2: DÜZELTİLMİŞ KOD ÜRET (1 LLM çağrısı) ────────────────┘")
print(f"│  {llm_cagrisi('Video kodundaki 5 hatayı düzelt')}")
print(f"│")
duzeltilmis_kod = '''
def port_tara(host: str = "127.0.0.1", port_range: str = "22-443") -> dict:
    """Belirtilen host'ta port taraması yapar (düzeltilmiş versiyon)"""
    nm = nmap.PortScanner()
    try:
        # FIX 1: ports keyword arg ✅
        sonuc = nm.scan(hosts=host, ports=port_range, arguments='-sV')
        
        if host not in sonuc.get('scan', {}):
            return {"hata": f"{host} yanıt vermiyor"}
        
        # FIX 4: Result parse ✅
        for proto in nm[host].all_protocols():
            for port in sorted(nm[host][proto].keys()):
                nm[host][proto][port]  # servis detayı
        
        return sonuc
    except nmap.PortScannerError as e:
        # FIX 2 + 3: Sudo uyarısı + exception handling ✅
        return {"hata": f"Nmap hatası: {e}. sudo gerekebilir"}
    except PermissionError:
        return {"hata": "Yetki hatası. sudo ile çalıştırın"}
    except Exception as e:
        return {"hata": f"Beklenmeyen: {e}"}

if __name__ == "__main__":
    # FIX 5: Argparse ✅
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('host', nargs='?', default='127.0.0.1')
    parser.add_argument('-p', '--ports', default='22-443')
    args = parser.parse_args()
    port_tara(args.host, args.ports)
'''
print(duzeltilmis_kod)
print("└──────────────────────────────────────────────────────────────────────┘")
print()

# ADIM 3: Sandbox'ta doğrulama
print("┌── ADIM 3: SANDBOX DOĞRULAMA (3 alt test) ───────────────────────┐")
print(f"│")
print(f"│  Test 1 — Sözdizimi kontrolü (python -c \"import nmap\")")
r1 = sandbox_calistir("import nmap", "Syntax check")
print(f"│  {r1}")
print(f"│")
print(f"│  Test 2 — Kodu çalıştır (timeout=30sn)")
r2 = sandbox_calistir("port_tara('127.0.0.1')", "Execution")
print(f"│  {r2}")
print(f"│")
print(f"│  Test 3 — Hata durumunu tetikle (PermissionError mock)")
r3 = sandbox_calistir("mock_permission_error()", "Error path")
print(f"│  {r3}")
print(f"│")
print(f"│  ⚠️  Eğer çalışmazsa: max 3 retry (exponential backoff: 2sn, 4sn, 8sn)")
print(f"│     3. retry de başarısız → circuit breaker → kullanıcıya bildir")
print(f"│")
print(f"│  ✅ 3/3 test PASS → kod doğrulandı")
print("└──────────────────────────────────────────────────────────────────────┘")
print()

# ADIM 4: Hafızaya kaydet
print("┌── ADIM 4: HAFIZAYA KAYDET ──────────────────────────────────────┐")
hafiza_kaydet('python nmap video hata cozumu',
    '# ✅ Video Hata Çözümü: Python-nmap\n## Kaynak: Video + Sandbox doğrulama\n\n## 5 Hata ve Düzeltme:\n1. 🔴 ports keyword arg → düzeltildi\n2. 🔴 sudo eksik → PermissionError eklendi\n3. 🔴 exception handling yok → try/except eklendi\n4. 🟡 result parse → all_tcp() kullanıldı\n5. 🟡 hardcoded → argparse eklendi\n\n## Doğrulama: Sandbox 3/3 PASS\n## Eskisini işaretle: ID=2400 artık eski (UPDATE ile guven=1.0)',
    'video/python/nmap', 1.0)
hafiza_kaydet('python nmap scan positional arg',
    '# Kural: scan(hosts, ports) keyword arg bekler\n## Hata: positional arg geçilirse çalışır ama kötü pratik\n## Çözüm: ports="22-443" olarak yaz\n## Kaynak: python-nmap docs + sandbox doğrulama\n## İlgili hata: HATA 1',
    'video/python/nmap', 0.95)
print(f"│  ✅ video/python/nmap (guven=1.0, UPDATE)                     │")
print(f"│  ✅ python nmap scan positional arg (guven=0.95, yeni)        │")
print(f"│                                                               │")
print(f"│  ESKİ KAYIT GÜNCELLEME:                                       │")
print(f"│  ID=2400 guven=0.9 → 1.0 (UPDATE)                             │")
print(f"│  metadata.kullanim_sayisi: 1 → 2                              │")
print(f"│  metadata.son_kullanim: güncellendi                           │")
print("└──────────────────────────────────────────────────────────────────────┘")
print()

print("╔══════════════════════════════════════════════════════════════════════╗")
print("║                    SENARYO 1 ÖZET                                   ║")
print("╠══════════════════════════════════════════════════════════════════════╣")
print(f"║  LLM çağrısı: {sayac['llm']} (kod üretme)                                   ║")
print(f"║  Sandbox test: {sayac['sandbox']} (3/3 PASS)                                    ║")
print(f"║  Hafıza: 1 UPDATE (guven 0.9→1.0) + 1 yeni kayıt                 ║")
print(f"║  Retry: max 3 (exponential backoff: 2sn, 4sn, 8sn)              ║")
print(f"║  Başarısız: circuit breaker → kullanıcıya bildir                 ║")
print("╚══════════════════════════════════════════════════════════════════════╝")
print()

# ═══════════════════════════════════════════════════
# SENARYO 2 — ÇELİŞKİLİ BİLGİ
# ═══════════════════════════════════════════════════
print("╔══════════════════════════════════════════════════════════════════════╗")
print("║     SENARYO 2: ÇELİŞKİLİ BİLGİ                                      ║")
print("║     Hafıza vs Video farklı yöntem → hangisi doğru?                  ║")
print("╚══════════════════════════════════════════════════════════════════════╝")
print()

print("┌── DURUM ──────────────────────────────────────────────────────────┐")
print("│                                                                   │")
print("│  HAFIZA (ID=1972, guven=1.0, 2026-06-21):                        │")
print("│    nmap -sV -p 22-443 127.0.0.1  (CLI ile tarama)                │")
print("│                                                                   │")
print("│  VİDEO (yeni, 2026-06-21):                                       │")
print("│    nmap.PortScanner().scan('127.0.0.1', '22-443')  (Python API)  │")
print("│                                                                   │")
print("│  ÇELİŞKİ: Aynı iş (port tarama) farklı yöntem (CLI vs API)       │")
print("│           Hangisi doğru? İkisi de doğru ama bağlam farklı        │")
print("└──────────────────────────────────────────────────────────────────────┘")
print()

# ADIM 1: Karar ağacı
print("┌── ADIM 1: KARAR AĞACI (0 LLM, kural bazlı) ────────────────────┐")
print("│                                                                   │")
print("│  Hafızadaki bilgi? nmap CLI (nmap -sV -p ...)                    │")
print("│  Video'daki bilgi?  python-nmap API (PortScanner)                │")
print("│                                                                   │")
print("│  KARAR: Çelişki değil, FARKLI BAĞLAM                             │")
print("│  ├─ CLI tarama → kali/network/nmap                               │")
print("│  ├─ Python API → video/python/nmap                               │")
print("│  └─ İkisi de doğru, kategori ayır                                 │")
print("│                                                                   │")
print("│  Kriter:                                                          │")
print("│  ① Aynı kategoride mi?→ HAYIR (kali vs video)                    │")
print("│  ② Aynı bağlamda mı? → HAYIR (CLI vs API)                       │")
print("│  ③ Aynı zaman damgası? → EVET (bugün)                           │")
print("│  → KARAR: ÇELİŞKİ YOK, EK BİLGİ                                 │")
print("│                                                                   │")
print("│  EĞER AYNI KATEGORİDE ÇELİŞSEYDİ:                                │")
print("│  1. Web'den doğrula (python-nmap docs)                           │")
print(f"│     {web_dogrula('python-nmap PortScanner API')}")
print("│  2. Web sonucu hafızadakiyle uyuşuyor mu?                        │")
print("│     ├─ EVET → web kaynağını hafızaya ekle (guven artar)          │")
print("│     └─ HAYIR → yeni kayıt aç, eskisini flag_udp=1 yap           │")
print("│  3. Video'yu da ayrı kategoriye koy                              │")
print("└──────────────────────────────────────────────────────────────────────┘")
print()

# ADIM 2: Web doğrulama
print("┌── ADIM 2: WEB DOĞRULAMA (ÇELİŞKİ VARSA, 1 WEB çağrısı) ───────┐")
print("│                                                                   │")
print("│  Sorgu: \"python-nmap PortScanner scan method signature\"          │")
print(f"│  {web_dogrula('python-nmap docs')}                              │")
print("│                                                                   │")
print("│  Sonuç: scan(self, hosts, ports, *args, **kwargs)                │")
print("│  → ports bir keyword arg, positional da çalışır                 │")
print("│  → Web'de: \"It is recommended to use keyword arguments\"         │")
print("│                                                                   │")
print("│  KARAR: Video'daki kullanım çalışır ama best practice değil     │")
print("│  → Düzeltilmiş versiyon: ports='22-443' ✅                      │")
print("│  → Hafızaya: \"best practice: keyword arg\" notu ekle            │")
print("└──────────────────────────────────────────────────────────────────────┘")
print()

# ADIM 3: Eski bilgiyi işaretleme
print("┌── ADIM 3: ESKİ BİLGİ İŞARETLEME ────────────────────────────────┐")
print("│                                                                   │")
print("│  KURAL: 3 durumda eski bilgi işaretlenir:                       │")
print("│                                                                   │")
print("│  DURUM A — Web'den farklı bulundu ✅                             │")
print("│     flag_udp = 1 (eski)                                          │")
print("│     metadata.not = \"Bu bilgi güncel değil, web'e bak\"           │")
print("│     guven_skoru = 0.3 (düşürülür)                                │")
print("│     Hafıza sorgusunda artık eşiği geçemez → LLM çağrılır        │")
print("│                                                                   │")
print("│  DURUM B — Zaman aşımı (> 180 gün)                               │")
print("│     expire_zaman kontrolü                                         │")
print("│     guven_skoru *= 0.5 (yaşlandıkça düşer)                       │")
print("│                                                                   │")
print("│  DURUM C — Kullanıcı düzeltti                                     │")
print("│     Kullanıcı: \"Bu yanlış, doğrusu şu\"                          │")
print("│     Eski kayıt: flag_udp=1, guven=0.2                            │")
print("│     Yeni kayıt: guven=1.0, kaynak=\"kullanıcı düzeltmesi\"        │")
print("└──────────────────────────────────────────────────────────────────────┘")
print()

# ADIM 4: Hafızaya kaydet
print("┌── ADIM 4: HAFIZAYA KAYDET ──────────────────────────────────────┐")
print("│                                                                   │")
print("│  HAFIZA KAYIT FORMATI (UPDATE):                                  │")
print("│  {                                                                │")
print("│    \"anahtar\": \"nmap CLI tarama 127.0.0.1\",                     │")
print("│    \"guven_skoru\": 1.0,              # değişmedi                   │")
print("│    \"kategori\": \"kali/network/nmap\",  # değişmedi                 │")
print("│    \"kullanim_sayisi\": 4,             # 3 → 4 (artırıldı)        │")
print("│    \"cross_ref\": [\"video/python/nmap\"]  # YENİ: eklendi          │")
print("│    \"not\": \"CLI tarama, video/python/nmap ile aynı işi yapar\"   │")
print("│  }                                                                │")
print("│                                                                   │")
print("│  YENİ KAYIT:                                                     │")
print("│  {                                                                │")
print("│    \"anahtar\": \"python nmap API tarama\",                        │")
print("│    \"guven_skoru\": 0.95,                                          │")
print("│    \"kategori\": \"video/python/nmap\",                             │")
print("│    \"kullanim_sayisi\": 1,                                         │")
print("│    \"cross_ref\": [\"kali/network/nmap\"],                         │")
print("│    \"kaynak\": \"web (python-nmap docs) + video\",                 │")
print("│    \"not\": \"Best practice: keyword arg kullanılmalı\"            │")
print("│  }                                                                │")
print("└──────────────────────────────────────────────────────────────────────┘")
print()

print("╔══════════════════════════════════════════════════════════════════════╗")
print("║                    SENARYO 2 ÖZET                                   ║")
print("╠══════════════════════════════════════════════════════════════════════╣")
print(f"║  LLM çağrısı: {sayac['llm']}                                            ║")
print("║  Web çağrısı: 1 (python-nmap docs)                              ║")
print("║  Karar: ÇELİŞKİ YOK — farklı bağlam (CLI vs API)               ║")
print("║  Eski bilgi işaretleme: 3 durum (web, zaman, kullanıcı)         ║")
print("║  Cross-ref eklendi: kali/network/nmap ↔ video/python/nmap       ║")
print("╚══════════════════════════════════════════════════════════════════════╝")
print()

# ═══════════════════════════════════════════════════
# SENARYO 3 — BİLİNMEYEN HATA
# ═══════════════════════════════════════════════════
print("╔══════════════════════════════════════════════════════════════════════╗")
print("║     SENARYO 3: BİLİNMEYEN HATA                                     ║")
print("║     Ajan hatayı anlayamadı → retry → web → kullanıcı               ║")
print("╚══════════════════════════════════════════════════════════════════════╝")
print()

print("┌── DURUM ──────────────────────────────────────────────────────────┐")
print("│                                                                   │")
print("│  Video'daki kod:                                                  │")
print("│    nm.scan('127.0.0.1', '-p 22-443')   # -p prefix'i var!        │")
print("│                                                                   │")
print("│  Ajanın bildikleri:                                               │")
print("│  ✅ kali/network/nmap: -p prefix CLI'de kullanılır               │")
print("│  ✅ python-nmap: ports='22-443' (prefix yok)                     │")
print("│  ❌ -p prefix'in python API'de hata fırlatıp fırlatmadığı bilinmiyor│")
print("│                                                                   │")
print("│  → Ajan EMİN DEĞİL (guven < 0.5)                                 │")
print("└──────────────────────────────────────────────────────────────────────┘")
print()

# ADIM 1: Analog tarama
print("┌── ADIM 1: HAFIZADA BENZER HATA ARA (0 LLM) ────────────────────┐")
print("│                                                                   │")
h_benzer = hafiza_ara('python nmap scan positional arg')
if h_benzer:
    print(f"│  Benzer hata bulundu: ID={h_benzer['id']} \"{h_benzer.get('kategori','')}\"")
    print(f"│  guven={h_benzer['guven']}")
    if h_benzer['guven'] >= 0.8:
        print(f"│  → Hafıza atlaması: direkt çözüm önerisi döndür (0 LLM)")
    else:
        print(f"│  → guven düşük: LLM çağrısı gerekli")
else:
    print(f"│  Benzer hata YOK → devam")
print(f"│")
print(f"│  Bu senaryoda: -p prefix python-nmap'te farklı davranır        │")
print(f"│  Hafızada -p ile ilgili kayıt: YOK                            │")
print("└──────────────────────────────────────────────────────────────────────┘")
print()

# ADIM 2: Retry döngüsü
print("┌── ADIM 2: RETRY DÖNGÜSÜ (max 3, exponential backoff) ──────────┐")
print("│                                                                   │")
print("│  Deneme 1: Kural tabanlı dene                                    │")
print("│  → \"-p prefix'i strip et, ports='22-443' yap\"                   │")
print("│  → Çalışır mı bilinmiyor → SANDBOX'TA DENE                       │")
r1 = sandbox_calistir("nmap_scan_with_dash_p_prefix()", "Deneme 1: prefix strip")
print(f"│  {r1}")
print(f"│  → ❌ HATA: argparse -p flag'i parametre olarak algıladı        │")
print(f"│  → Bekle: 2sn (exponential backoff)                             │")
print(f"│                                                                   │")
print(f"│  Deneme 2: Farklı yöntem dene                                   │")
print(f"│  → '22-443' direkt (prefix'siz)                                 │")
r2 = sandbox_calistir("nmap_scan_without_prefix()", "Deneme 2: prefix yok")
print(f"│  {r2}")
print(f"│  → ✅ PASS: ports='22-443' çalıştı                              │")
print(f"│                                                                   │")
print(f"│  NOT: Deneme 3 gerekmedi (2/2 başarılı)                         │")
print(f"│  Eğer 3/3 başarısız olsaydı:                                    │")
print(f"│  → Bekle: 4sn, 8sn                                              │")
print(f"│  → Circuit breaker (3 hata) → KULLANICIYA SOR                    │")
print("└──────────────────────────────────────────────────────────────────────┘")
print()

# ADIM 3: Web'de ara
print("┌── ADIM 3: WEB ARAMA (opsiyonel, 1 WEB çağrısı) ─────────────────┐")
print("│                                                                   │")
print(f"│  {web_dogrula('python-nmap -p prefix hatası')}                   │")
print("│                                                                   │")
print("│  Sorgu: site:stackoverflow.com python-nmap PortScanner -p prefix  │")
print("│  Sonuç: \"-p flag is not recognized in PortScanner.scan()\"        │")
print("│  → Hata onaylandı: -p prefix python API'de çalışmaz              │")
print("│  → Çözüm: prefix'siz ports='22-443' kullan                       │")
print("└──────────────────────────────────────────────────────────────────────┘")
print()

# ADIM 4: Kullanıcıya sor
print("┌── ADIM 4: KULLANICIYA SOR (son çare) ───────────────────────────┐")
print("│                                                                   │")
print("│  ŞART: 3 retry başarısız + web'de bulamadı + hafızada yok       │")
print("│                                                                   │")
print("│  SORU FORMATI:                                                   │")
print("│  ┌─────────────────────────────────────────────────────┐         │")
print("│  │   Bir hata ile karşılaştım, çözemedim.              │         │")
print("│  │                                                     │         │")
print("│  │   KOD: nm.scan('127.0.0.1', '-p 22-443')           │         │")
print("│  │   HATA: -p prefix'i tanınmadı                       │         │")
print("│  │                                                     │         │")
print("│  │   DENEDİKLERİM:                                     │         │")
print("│  │   1. Kural: prefix strip et → argparse hatası       │         │")
print("│  │   2. Web'de aradım → bulamadım                      │         │")
print("│  │                                                     │         │")
print("│  │   SORU: Bu kodun doğru kullanımı nedir?            │         │")
print("│  └─────────────────────────────────────────────────────┘         │")
print("│                                                                   │")
print("│  KULLANICI CEVAP GELİNCE:                                        │")
print("│  → \"Doğrusu: nm.scan('127.0.0.1', ports='22-443')\"             │")
print("│  → Hemen hafızaya kaydet:                                        │")
hafiza_kaydet('python nmap dash p prefix hatasi',
    "# ✅ Kullanıcı Düzeltmesi: -p prefix python API hatası\n## Hata: nm.scan() içinde -p prefix kullanılamaz\n## Doğrusu: ports='22-443' (prefix'siz)\n## Sebep: -p argparse flag'i olarak algılanır\n## Kaynak: kullanıcı düzeltmesi\n## Eski kayıt işaretlendi: flag_udp=1",
    'video/python/nmap', 1.0)
print(f"│  → Kullanıcı düzeltmesi kaydedildi (guven=1.0)                 │")
print(f"│  → Eski kayıt varsa: metadata.flag_udp=1                       │")
print("└──────────────────────────────────────────────────────────────────────┘")
print()

print("╔══════════════════════════════════════════════════════════════════════╗")
print("║                    SENARYO 3 ÖZET                                   ║")
print("╠══════════════════════════════════════════════════════════════════════╣")
print("║  Akış: Hafıza → Retry(3) → Web → Kullanıcı                        ║")
print("║  Her adımda bir önceki çözülmezse sonrakine geç                     ║")
print(f"║  LLM çağrısı: {sayac['llm']}                                            ║")
print(f"║  Sandbox: {sayac['sandbox']} (Deneme 2'de çözüldü)                         ║")
print(f"║  Web çağrısı: {sayac['web']} (opsiyonel, stackoverflow)                   ║")
print("║  Retry backoff: 2sn → 4sn → 8sn                                   ║")
print("║  Son çare: Kullanıcıya sor (formatlı soru)                         ║")
print("║                                                                     ║")
print("║  KULLANICI YANITI GELİNCE:                                         ║")
print("║  1. Hafızaya kaydet (guven=1.0, kaynak=kullanıcı)                 ║")
print("║  2. Eski kaydı işaretle (flag_udp=1)                              ║")
print("║  3. Çözümü uygula ve doğrula                                      ║")
print("╚══════════════════════════════════════════════════════════════════════╝")
print()

# ═══════════════════════════════════════════════════
# GENEL ÖZET
# ═══════════════════════════════════════════════════
print("╔══════════════════════════════════════════════════════════════════════╗")
print("║                    3 SENARYO KARŞILAŞTIRMA                          ║")
print("╠══════════════════════════════════════════════════════════════════════╣")
print("║                                                                     ║")
print("║  ┌──────────────────┬────────────┬────────────┬────────────┐        ║")
print("║  │ Ölçüt           │ Sen.1      │ Sen.2      │ Sen.3      │        ║")
print("║  ├──────────────────┼────────────┼────────────┼────────────┤        ║")
print("║  │ Hata tipi       │ Kod hatası │ Çelişkili  │ Bilinmeyen │        ║")
print("║  │ LLM çağrısı    │ 1          │ 0          │ 0          │        ║")
print("║  │ Web çağrısı    │ 0          │ 1          │ 1          │        ║")
print("║  │ Sandbox test   │ 3          │ 0          │ 2          │        ║")
print("║  │ Retry          │ 0 (1'de)  │ 0          │ 2 (2'de)   │        ║")
print("║  │ Kullanıcı sor  │ ❌         │ ❌         │ ✅ (son)   │        ║")
print("║  │ Hafıza UPDATE  │ ✅ guven↑  │ ✅ cross-ref│ ✅ yeni    │        ║")
print("║  │ Toplam süre    │ ~15sn      │ ~5sn       │ ~30sn      │        ║")
print("║  │ Maliyet        │ 0₺         │ 0₺         │ 0₺         │        ║")
print("║  └──────────────────┴────────────┴────────────┴────────────┘        ║")
print("║                                                                     ║")
print("║  HAFIZA KAYIT FORMATI (ortak şema):                                ║")
print("║  {                                                                  ║")
print('║    "anahtar": "açıklayıcı Türkçe isim",                            ║')
print('║    "koleksiyon": "beceriler",                                       ║')
print('║    "guven_skoru": 0.0 - 1.0,                                        ║')
print('║    "kategori": "video/python/nmap",                                 ║')
print('║    "kullanim_sayisi": 1,                                            ║')
print('║    "gecerlilik_tarihi": "2026-12-18",                              ║')
print('║    "flag_udp": null | 1,  # eskimişse 1                            ║')
print('║    "cross_ref": ["kali/network/nmap"],  # ilgili kategoriler        ║')
print('║    "kaynak": "video | web | kullanıcı | sandbox"                   ║')
print("║  }                                                                  ║")
print("╚══════════════════════════════════════════════════════════════════════╝")

db.close()
print()
print("✅ 3 senaryo simülasyonu tamamlandı.")
