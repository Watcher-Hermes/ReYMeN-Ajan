# Kazanımlar — 2026-06-21

## 1. Windows Terminal Ajanı (Karar #10)
- **Skill:** `windows/windows-terminal-ajani` (SKILL.md + live-test-output.md)
- **Kategori:** `windows/terminal/network`, `windows/terminal/system`
- **Komutlar:** ipconfig, netstat, systeminfo, tasklist, dir, copy, move, del, sc, net start/stop
- **Test:** ipconfig /all + netstat -an çalıştırıldı
- **Cross-ref:** Kali vs Windows karşılaştırma tablosu skill içinde

## 2. Kali + Windows Inter-Agent Koordinasyonu
- **Protokol:** ReYMEN Inter-Agent v1 (JSON: from/to/payload)
- **Skill:** `cross-platform/inter-agent-coordination`
- **Kategori:** `cross-platform/security`
- **Orkestratör:** Kali (tespit) → Windows (engelle) → Kali (onay)
- **Hata yönetimi:** 4 senaryo (Kali hata, Windows hata, ikisi hata, timeout)
- **Test:** Telegram üzerinden canlı çalıştırıldı — 0 LLM, 0₺

## 3. Video Öğrenme Ajanı (Karar #11)
- **Skill:** `video/video-ogrenme-ajani` (SKILL.md + python-nmap-api.md + 3 script)
- **Kategori:** `video/learning`, `video/python/nmap`, `video/general`
- **Mimari:** yt-dlp → Whisper → Bölümle → Hafıza karşılaştır → Hata tespit → Düzelt → Kaydet
- **Test:** "Python ile nmap kullanımı" videosu simüle edildi, 5 hata tespit

### Video Ajani — 3 Hata Senaryosu (Karar #12)
| Senaryo | Tespit | Doğrulama | LLM |
|:--------|:-------|:----------|:---:|
| Kod Hatası | 5 kural (kural bazlı) | Sandbox 3 test | 1 |
| Çelişkili Bilgi | Karar ağacı | Web + cross-ref | 0 |
| Bilinmeyen Hata | Hafıza + Retry(3) + Web | Sandbox → kullanıcı | 0 |

### Video Ajani — WUPS Döngüsü (Karar #13)
- **Döngü:** Web → Uygula → Puanla → Karar → Kaydet
- **5 Tetikleyici:**
  - T1: Hafıza boş → anında web
  - T2: Görev başarısız (2. hata) → web
  - T3: Güven < 0.5 → web
  - T4: Süre geçmiş → arka plan web
  - T5: Çelişki → web hakem
- **Puanlama:** hiz(0.2)+basari(0.3)+cikti(0.2)+guvenlik(0.15)+kaynak(0.15)
- **Karar:** yeni > eski + 0.2 → geç, fark < 0.2 → stable
- **Test:** nmap UDP — `--min-rate=1000` (0.95 puan) kazandı

## 4. H9+H10+H16 Fix — Kademeli Güven (Karar #14)
- **Dosya:** `reymen/sistem/once_hafiza.py`
- **Değişiklikler:**
  - `_kademeli_guven()` fonksiyonu eklendi (sigmoid)
  - `kaydet()`: lineer `basari/(basari+hata)` → `_kademeli_guven()`
  - `hata_kaydet()`: lineer → `_kademeli_guven()`
  - İlk kayıt: `guven=1.0` → `0.5` (kademeli başlangıç)
  - CREATE TABLE: `DEFAULT 1.0` → `DEFAULT 0.5`
  - `kaynak_url TEXT DEFAULT NULL` kolonu eklendi
  - Modül-level `kaydet()` fonksiyonuna `kaynak_url` parametresi eklendi
- **Formül:** `guven = 1 / (1 + e^(-0.5 * (basari - hata - 1)))`
  - 1baş+0hata=0.50, 3baş+0hata=0.73, 10baş+0hata=0.99

## 5. Cron Sistemi
| Job | Zaman | Durum |
|:----|:------|:------|
| reymen-hourly-check | Her saat | 🔴 devre dışı |
| reymen-daily-full-push | 03:00 | ✅ aktif |
| reymen-daily-memory-push | 00:30 | ✅ aktif |
| reymen-weekly-report | 28.06 | ✅ aktif |
| reymen-test-runner | Her 15dk | ✅ aktif (55/55 PASS) |

### 🔴 Kritik Pitfall — `pytest --collect-only`
- **Sorun:** Cron prompt'unda `--collect-only` test import'larını çalıştırır, bloke olursa 3dk timeout
- **Çözüm:** `compile()` ile syntax kontrolü (import çalıştırmaz, 0.1sn)
- **Skill:** `reymen-calisma-prensipleri` → references/test-runner-cron-pattern.md
- **Aksiyon:** Cron prompt'u güncellendi (Kral_38)

## 6. 5 Kategori Hata Analizi (11 hata tespit)
| Kat | Hata | Durum |
|:----|:-----|:------|
| K1-Tetikleyici | İçerik eski ama tarih gelmemiş, versiyon farkı görünmez | 📝 not edildi |
| K2-Puanlama | Ağırlıklar sabit, başarı binary | 📝 not edildi |
| K3-Hafıza | URL kolon yok, guven=1.0 çok yüksek, temizlik yok | ✅ H9/H10/H16 fix |
| K4-İletişim | Heartbeat yok, timeout sabit, ACK yok | 📝 not edildi |
| K5-Öğrenme | Yanlış kayıt, zehirli kaynak, hızlı güven artışı | ✅ H10/H16 fix |

## 7. Push — hermes-memory-backup
- **15 yeni dosya, 4067 satır** eklendi
- Skills: cross-platform-coordination, web-dogrulama-dongusu, video-ogrenme-ajani, windows-terminal-ajani
- once_hafiza.py (sistem + cereyan)
- decisions.md (Karar #13, #14)
- Cron: `reymen-daily-memory-push` 00:30'da otomatik push yapar

## 8. Skill Yapısı (Hermes profiles/reymen/skills/)
```
cross-platform/
  inter-agent-coordination/      ← Kali+Windows koordinasyon
  web-dogrulama-dongusu/         ← WUPS döngüsü
video/
  video-ogrenme-ajani/           ← Video öğrenme ajanı
windows/
  windows-terminal-ajani/        ← Windows terminal ajanı
autonomous-ai-agents/
  reymen-calisma-prensipleri/    ← Çalışma prensipleri (güncellendi)
```

## 9. Hafıza DB (ogrenmeler.db)
- **2391 kayıt** (önceki: 2295)
- **231 beceri** kategorisinde
- **Kategoriler:** cad, cross-platform/security, genel, kali, kali/network/nmap,
  powerbi, test, video/learning, video/python/nmap, windows,
  windows/terminal/network, windows/terminal/system
- **Guven skorlu kayıt:** %93
- **Hafıza öncelikli akış aktif:** guven>0.8 → direkt döndür (0 LLM)
