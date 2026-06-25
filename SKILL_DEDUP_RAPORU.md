# Skill Deduplikasyon Raporu
**Tarih:** 2026-06-25
**Kapsam:** `skills/` (kök) ↔ `reymen/hafiza/.ReYMeN/skills/` (11 dosya) + `skills/` içi

---

## Özet

| Kategori | Adet |
|----------|------|
| **Mükerrer çiftler (kesin)** | **3** |
| **Cross-dir mükerrer** | **0** |
| **Benzer ama farklı (tamamlayıcı)** | **3** |
| **Benzersiz (sorun yok)** | Geri kalan ~200 dosya |
| **Toplam mükerrer dosya sayısı** | **6 dosya (3 çift)** |

---

## BÖLÜM 1: Cross-Directory Karşılaştırması (skills/ vs .ReYMeN/skills/)

### Sonuç: MÜKERRER YOK

`.ReYMeN/skills/` altındaki 11 dosya **skill tanımı değil**, tamamlanmış görev kayıtlarıdır (task execution log). Her biri aynı şablonda: `# Beceri: ... # ✅ Başarılı: ... - Süre: ... Tur: ... - Task Id: ...` formatında, içeriksiz kayıtlardır.

| .ReYMeN/skills/ Dosyası | Tip | skills/ Karşılığı |
|--------------------------|-----|-------------------|
| yeni_hedef.md | Görev kaydı | Yok |
| bir_rapor_yaz.md | Görev kaydı | Yok |
| bitis_durumu_testi.md | Görev kaydı | Yok |
| baglamli_hedef.md | Görev kaydı | Yok |
| hizli_gorev.md | Görev kaydı | Yok |
| windows_terminal_komut_rehberi.md | Görev kaydı | Yok |
| windows_ipconfig_netstat_egzersizi.md | Görev kaydı | Yok |
| solidworks_cizim.md | Görev kaydı | Yok |
| localhost_127001_servis_versiyon_taramasi.md | Görev kaydı | Yok |
| test_kaydet_islemi.md | Görev kaydı | Yok |
| xyz_bu_gorev_yok_99999.md | Görev kaydı | Yok |

**Öneri:** Bu dosyalar task log formatında olduğu için skill olarak ele alınmamalı. İstersen `.ReYMeN/task_logs/` gibi ayrı bir klasöre taşınabilir.

---

## BÖLÜM 2: skills/ İçi Mükerrerler

### ✅ MÜKERRER #1: `windows-file-ops` ↔ `windows-file-operations`

| Özellik | `windows-file-ops` | `windows-file-operations` |
|---------|-------------------|--------------------------|
| **Yol** | `skills/windows-automation/windows-file-ops/SKILL.md` | `skills/windows-automation/windows-file-operations/SKILL.md` |
| **Amaç** | Windows dosya işlemleri | Windows dosya işlemleri |
| **Satır** | 115 | 102 |
| **Yazar** | marko | hermes |
| **İçerik** | Detaylı: uzantı kuralları + oluşturma yöntemleri (touch/echo/PowerShell) + dosya açma + klasör + silme + yol formatları + pitfall'lar + checklist | Daha kısa: benzer kurallar + Notepad + Tor Browser + Obsidian + pitfall'lar + checklist |
| **Versiyon** | 1.0.0 | 1.0.0 |
| **Son Güncelleme** | ~2026-06-20 | ~2026-06-20 |

**Durum:** ✅ KESİN MÜKERRER — aynı amaca hizmet ediyor.

**Tavsiye:** `windows-file-ops` daha kapsamlı. Birleştirme sonrası `windows-file-operations` silinebilir.

---

### ✅ MÜKERRER #2: `windows-automation/vscode-control` ↔ `skills/vscode-control`

| Özellik | `windows-automation/vscode-control` | `skills/vscode-control` |
|---------|-------------------------------------|------------------------|
| **Yol** | `skills/windows-automation/vscode-control/SKILL.md` | `skills/vscode-control/SKILL.md` |
| **Amaç** | VS Code Remote Control (Telegram) | VS Code Remote Control (Telegram) |
| **İçerik** | **BİREBİR AYNI** | **BİREBİR AYNI** |
| **Kategori** | `windows-automation` | `vscode-control` |
| **Etiketler** | `[automation, windows]` + `[]` | `[general]` + `[]` |

**Durum:** ✅ KESİN MÜKERRER — birebir aynı içerik, iki farklı lokasyon.

**Tavsiye:** `windows-automation/vscode-control` daha doğru kategorize edilmiş (windows-automation). `skills/vscode-control` birleştirilip silinebilir.

---

### ✅ MÜKERRER #3: `windows-automation/vscode-agent-control` ↔ `skills/vscode-agent-control`

| Özellik | `windows-automation/vscode-agent-control` | `skills/vscode-agent-control` |
|---------|------------------------------------------|-------------------------------|
| **Yol** | `skills/windows-automation/vscode-agent-control/SKILL.md` | `skills/vscode-agent-control/SKILL.md` |
| **Amaç** | VS Code Claude Terminal workflow | VS Code Claude Terminal workflow |
| **İçerik** | **BİREBİR AYNI** | **BİREBİR AYNI** |
| **Kategori** | `windows-automation` | `vscode-agent-control` |
| **Etiketler** | `[automation, windows]` + `[]` | `[general]` + `[]` |

**Durum:** ✅ KESİN MÜKERRER — birebir aynı içerik, iki farklı lokasyon.

**Tavsiye:** `windows-automation/vscode-agent-control` daha doğru kategorize edilmiş. `skills/vscode-agent-control` birleştirilip silinebilir.

---

## BÖLÜM 3: Benzer Ama FARKLI (Mükerrer Değil)

Bunlar aynı aile içinde ama farklı amaçlara hizmet ediyor:

| Çift | Fark |
|------|------|
| `structured-output-picker` ↔ `structured-output-designer` | **Picker** yaklaşım seçer (Phase 5), **Designer** şema oluşturur (Phase 13). Farklı fazlar, tamamlayıcı. |
| `transformer-review` ↔ `transformer-block-reviewer` | **Review** tüm transformer'ı dener (13 ders), **Block Reviewer** tek bloku denetler. Farklı kapsam. |
| `hersona` + `hersona-initializer` + `hersona-recommend-quiz` | **hersona**=çekirdek, **initializer**=ilk kurulum, **recommend-quiz**=tanı testi. Ekosistemin 3 farklı bileşeni. |

**Öneri:** Dokümantasyonda `related_skills` ile birbirlerine referans vermeleri yeterli. Ayrı tutulmalı.

---

## BÖLÜM 4: PROJE_DURUMU.md'de Bahsedilen "kaç_skill_var.md / kac_skl_var.md"

Sadece `kaç_skill_var.md` bulundu. `kac_skl_var.md` (**yok**). Muhtemelen PROJE_DURUMU.md'de varsayımsal bir örnekti.

---

## BÖLÜM 5: Yapılması Önerilen Birleştirme İşlemleri

### Adım 1: `windows-file-ops` + `windows-file-operations` → `windows-file-ops`

1. `windows-file-ops/SKILL.md` korunsun (daha kapsamlı, 115 satır)
2. `windows-file-operations/SKILL.md`'den benzersiz içerik ekle:
   - "Obsidian'da Not Açma" bölümü
   - "Tor Browser / Firefox ile aç" bölümü
   - "Varsayılan programla aç" (`start ""`) bölümü
3. `windows-file-operations/SKILL.md`'nin frontmatter'ına not ekle: `# merged into windows-automation/windows-file-ops`
4. Kullanıcıya onay sor → sil

### Adım 2: `windows-automation/vscode-control` korunsun → `skills/vscode-control` notlansın

1. `windows-automation/vscode-control/SKILL.md` korunsun
2. `skills/vscode-control/SKILL.md` frontmatter'ına not ekle: `# merged into windows-automation/vscode-control`
3. Onay sonrası `skills/vscode-control/` silinsin

### Adım 3: `windows-automation/vscode-agent-control` korunsun → `skills/vscode-agent-control` notlansın

1. `windows-automation/vscode-agent-control/SKILL.md` korunsun
2. `skills/vscode-agent-control/SKILL.md` frontmatter'ına not ekle: `# merged into windows-automation/vscode-agent-control`
3. Onay sonrası `skills/vscode-agent-control/` silinsin

---

## EK: skills/ Kök Dizini Dosya Sayımı

skills/ içindeki tüm SKILL.md'ler: ~100 adet (çeşitli kategorilerde)
skills/ içindeki flat/düz dosyalar: `kaç_skill_var.md`, `reymen-egitim-test-104.md` (bunlar task log/not niteliğinde)
