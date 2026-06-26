# Motor.py Analiz Raporu

## 1. BOYUT

| Metrik | Değer |
|--------|-------|
| Toplam Satır | 2,048 (1,998 değil) |
| Class | 1 (Motor) |
| Motor Method | 28 adet |
| Module-level function | 3 adet |
| Module-level constant | 3 adet |
| Import bloğu | 17 try/except block |
| Dosya boyutu | 93 KB |

## 2. SORUMLULUK KATEGORİLERİ

### A) Imports / Modül Yükleme (line 1–181, ~180 satır)
- 17 adet try/except ile isteğe bağlı modül yükleme
- CUA, file_safety, path_security, context_compressor, prompt_caching, redact, tool_registry, plugin_manager, plugin_loader, health_check, terminal_backends, izole_laboratuvar
- ReYMeN araçları: process_tool, todo_tool, clarify_tool, cron_tool, file_ops_tool, x_search_tool, browser_mcp_tool, homeassistant_tool, kanban_orchestrator

### B) Gateway State (line 184–213, ~30 satır)
- `_gateway_durum_yaz()` — gateway_state.json'a durum yazar

### C) Motor Class — Lazy Loading / Init (line 216–393, ~177 satır)
- `__init__()` — Motor kurulumu, lazy batch hazırlama
- `_lazy_araclari_yukle()` — 100+ modülü ilk kullanımda yükle
- `_lazy_plugin_kaydet()` — modül listesini lazy batch'e kaydet
- `_temel_araclari_yukle()` — basit mod için temel toolset
- `_plugin_moduller_yukle()` — geriye uyumluluk
- `hook_kaydet()` — async hook sistemi

### D) Skill Araçları (line 395–489, ~95 satır)
- `_skill_araclari_kaydet()` — v1 skill araçları
- `_skill_v2_araclari_kaydet()` — v2/v3 skill araçları (aktivasyon, kategori, script, oluşturma)

### E) Plugin API (line 491–496, ~6 satır)
- `_plugin_arac_kaydet()` — ortak araç kaydetme API'si

### F) FC / Schema (line 497–584, ~87 satır)
- `calistir_fc()` — Function Calling dönüşümü
- `tools_schema_al()` — OpenAI-uyumlu tools schema
- `_plugin_araclar` (property) — salt-okunur dict

### G) Eylem Ayrıştırma (line 586–616, ~30 satır)
- `eylemi_ayristir()` — LLM çıktısından Eylem: ARAC(...) yakalar
- `_parametreleri_coz()` — tırnak içi parametreleri regex ile çöz

### H) Hafıza Araçları (line 618–633, ~15 satır)
- `_hafiza_araclari_kaydet()` — HAFIZA_DURUMU, HAFIZA_TEMIZLE, HAFIZA_KAYDET

### I) Toolset Yönetimi (line 635–742, ~107 satır)
- `TOOLSET_GRUPLARI` — 13 grup, ~80 araç tanımı
- `_ARAC_CHECK_FNS` — kullanılabilirlik kontrol fonksiyonları
- `check_fn_kaydet()` — classmethod
- `musait_araclar()` — check_fn filtrelemesi
- `toolset_tanimi_al()` — LLM prompt için formatlı çıktı
- `tum_arac_tanimini_al()` — toolset + registry dinamik araçlar

### J) Durum Mesajları (line 744–809, ~65 satır)
- `_DURUM_MESAJLARI` — 50+ araç için kullanıcı mesajı
- `_durum_goster()` — araç başlamadan önce log yaz
- `_RISKLI_ARACLAR` — HITL gerektiren araçlar

### K) Ana Dispatch — calistir() (line 817–1006, ~190 satır)
- Lazy yükleme tetikleme
- Parametre çözümleme
- Durum mesajı
- Achievement kaydı
- check_fn kontrolü
- HITL onayı
- HATA_COZUCU dispatch
- TOR_OTOMASYONU dispatch
- PARALLEL_CALISTIR dispatch
- ToolRegistry → PluginManager → Fallback zinciri

### L) Paralel Çalıştırma (line 1008–1068, ~60 satır)
- `_paralel_calistir()` — ThreadPoolExecutor ile paralel araç

### M) Hook Tetikleme (line 1070–1081, ~11 satır)
- `_hook_tetikle()` — async hook tetikleme

### N) Fallback Çalıştırma (line 1083–1634, ~550 satır) ★ EN BÜYÜK
- `_fallback_calistir()` — 40+ if/elif zinciri
- KOMUT_CALISTIR, PYTHON_CALISTIR, GUVENLI_CALISTIR, ARAC_URET
- GOREV_BITTI, DURUM_BILDIR, DURUM_RAPOR, WATCHDOG_KONTROL
- GATEWAY_DURUM_YAZ, TELEGRAM_TOKEN_TEST, PROXY_AYARLA
- ACHIEVEMENTS_LISTE, DOSYA_YAZ, DOSYA_OKU, HAFIZA_ARA
- WEB_ARA, TELEGRAM_* (6 araç), ILETISIM_* (3 araç)
- KANBAN_* (7 araç), TARAYICI_AC, EKRAN_* (3 araç)
- MAKRO_OYNAT, UYG_ISLEM_CAGIR, PDF_OKU, EXCEL_OKU, CSV_OKU
- GORUNTU_ANALIZ, DOSYA_ANALIZ, PROJE_TARA
- CUA_* (2 araç), TUI_BASLAT
- GATEWAY_* (4 araç), ALT_AJAN_* (3 araç)
- CLARIFY, EXECUTE_CODE

### O) Çıktı Temizleme & Context (line 1636–1661, ~25 satır)
- `_cevabi_temizle()` — PII/sır temizleme
- `_context_sikistir()` — konuşma geçmişi sıkıştırma
- `_cache_kontrol()` / `_cache_kaydet()` — prompt caching

### P) Provider Yönetimi (line 1663–1881, ~218 satır)
- `aktif_provider_listele()` — 9 provider listeleme
- `provider_test_et()` — provider ping/test
- `provider_degistir()` (method) — provider değiştirme
- `_setup_oku()` — setup.json okuma

### Q) Module-level Tool Registry (line 1889–1997, ~108 satır)
- `CORE_TOOLS` — 16 adet
- `OPTIONAL_TOOLS` — 11 kategori, ~50 araç
- `get_active_tools()` — context bazlı filtreleme

### R) Module-level Provider Değiştirici (line 2000–2048, ~48 satır)
- `provider_degistir()` — bağımsız provider değiştirme fonksiyonu

## 3. BAĞIMLILIKLAR

```
calistir()
  ├── _lazy_araclari_yukle()
  │     ├── _skill_araclari_kaydet()
  │     ├── _skill_v2_araclari_kaydet()
  │     ├── _hafiza_araclari_kaydet()
  │     └── PluginYukleyici / MCPToolBridge
  ├── _parametreleri_coz()
  ├── _durum_goster()
  ├── _ARAC_CHECK_FNS.get()
  ├── _paralel_calistir()
  │     └── calistir() (recursive)
  ├── _REGISTRY.calistir()
  ├── _PLUGIN_MGR.run()
  ├── _fallback_calistir()
  │     └── 40+ farklı modül (terminal, sandbox, gateway, vs.)
  └── _hook_tetikle()

aktif_provider_listele()
  └── _setup_oku()

provider_test_et()
  └── requests.post()

provider_degistir() (method)
  └── _setup_oku()
```

## 4. KALİTE SORUNLARI

| Sorun | Sayı | Örnek |
|-------|------|-------|
| `except: pass` | ~17 | Line 22, 38, 42, 56, 66, 80, etc. |
| `except Exception: pass` | ~9 | Line 415, 489, 633, 833, 1248, etc. |
| Magic Number | ~15 | 4096, 3600, 60, 200, 30, 8, 5, 500, 120, 15, 10, 1.5 |
| Docstring eksik | ~5 | `hook_kaydet()`, `_temel_araclari_yukle()`, `_hafiza_araclari_kaydet()`, `check_fn_kaydet()`, `_parser` |
| Global state | ~12 | `_REGISTRY`, `_PLUGIN_MGR`, `_CACHE`, `_COMPRESSOR`, `_CUA_MEVCUT`, etc. |
| `print()` kullanımı | 0+ | — |
| Karmaşık metod | 1 | `_fallback_calistir()` 550 satır |
| try/except overload | 17 | Tüm importlar try/except ile |

## 5. ENTRY POINT

- `if __name__ == "__main__":` (line 1884) — test amaçlı
- Public API: `Motor.calistir()`, `Motor.eylemi_ayristir()`, `Motor.tools_schema_al()`
- Module-level: `get_active_tools()`, `provider_degistir()`

## PARÇALAMA ACİLİYET SKORU

| Kriter | Skor |
|--------|------|
| 2000+ satır tek dosya | 30/30 |
| Karmaşık _fallback_calistir (550 satır) | 25/25 |
| Global state ve çapraz bağımlılık | 15/20 |
| Dokümantasyon eksikliği | 10/15 |
| try/except overload | 5/10 |
| **TOPLAM** | **85/100** |

**ACİL. Skor 80+ → Refactor zorunlu.**

## ÖNERİLEN AYRIŞTIRMA

1. `providers.py` → Provider listeleme, test, değiştirme, setup.json okuma (~200 satır)
2. `tool_registry.py` → CORE_TOOLS, OPTIONAL_TOOLS, get_active_tools (~100 satır)
3. `context.py` → ContextCompressor, PromptCache wrapper (~80 satır)
4. `plugins.py` → Plugin yönetimi, skill araçları (~120 satır)
5. `utils.py` → file_safety, path_security, gateway state, helpers (~100 satır)
6. `motor.py` (küçültülmüş) → Motor class (~500 satır, fallback kısmı main'de kalır)
