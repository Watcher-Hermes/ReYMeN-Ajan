# ReYMeN Motor Entegrasyon Kararları

## 2026-06-26: Hermes Tool'larının motor.py'ye Entegrasyonu

### Yapılan Değişiklikler

**Dosya:** `reymen/cereyan/motor.py`

#### 1. try/except Import Blokları (satır ~109)
Aşağıdaki modüller için mevcut pattern takip edilerek try/except import blokları eklendi:
- `reymen.arac.process_tool` → `ProcessManager`, `process_run` (_PROCESS_MEVCUT)
- `reymen.arac.todo_tool` → `TodoManager`, `todo_run` (_TODO_MEVCUT)
- `reymen.arac.clarify_tool` → `clarify_run`, `clarify_check` (_CLARIFY_MEVCUT)
- `reymen.arac.cron_tool` → `CronManager`, `cron_run` (_CRON_MEVCUT)
- `reymen.arac.file_ops_tool` → `FileOps`, `fileops_run` (_FILEOPS_MEVCUT)
- `reymen.arac.x_search_tool` → `tweet_ara`, `kullanici_profili`, `son_tweetler` (_X_SEARCH_MEVCUT)
- `reymen.arac.browser_mcp_tool` → `BrowserMCP`, `browser_run` (_BROWSER_MEVCUT)
- `reymen.arac.homeassistant_tool` → `durum_oku`, `tum_durumlar`, `servis_cagir` (_HA_MEVCUT)
- `reymen.arac.kanban_orchestrator` → `AdvancedKanbanOrchestrator` (_KANBAN_MEVCUT)

#### 2. CORE_TOOLS Listesi (satır ~1893)
Hermes'ten eksik olan core tool'lar eklendi:
- `process` → process_tool.py (islem: baslat/durum/log/durdur/listele)
- `todo` → todo_tool.py (islem: ekle/tamamla/baslat/iptal/sil/listele/istatistik)
- `clarify` → clarify_tool.py (soru sor, seçenek sun)
- `cronjob` → cron_tool.py (islem: ekle/kaldir/duraklat/devam/calistir)
- `patch` → file_ops_tool.py (islem: patch - fuzzy find/replace)
- `search_files` → file_ops_tool.py (islem: search_files - regex content/file search)
- `skill_manage` → skill_utils.py (skill yönetimi - zaten _skill_v2_araclari_kaydet ile kayıtlı)
- `x_search` → x_search_tool.py (X/Twitter API arama)

#### 3. OPTIONAL_TOOLS Listesi (satır ~1913)

**browser** genişletildi (browser_mcp_tool.py'den):
- `browser_scroll` → scroll(direction, amount)
- `browser_press` → press_key(key)
- `browser_snapshot` → snapshot() accessibility tree
- `browser_get_images` → get_images() sayfadaki img URL'leri
- `browser_vision` → screenshot + vision analiz
- `browser_console` → get_console(level) console mesajları
- `browser_cdp` → evaluate(js_code) JS çalıştırma
- `browser_dialog` → handle_dialog(accept) dialog yönetimi

**kanban** eklendi (kanban_orchestrator.py'den):
- `kanban_show` → gorsel_tahta() ASCII kanban gösterimi
- `kanban_list` → liste(durum) görevleri listele
- `kanban_complete` → tamamla(id) görevi tamamla
- `kanban_block` → engelle(id, neden) görevi bloke et

**homeassistant** eklendi (homeassistant_tool.py'den):
- `ha_list_entities` → tum_durumlar(domain) entity listele
- `ha_get_state` → durum_oku(entity_id) entity durumunu oku

#### 4. get_active_tools() Güncellemesi (satır ~1973)
- `kanban_needed` context flag'i → OPTIONAL_TOOLS["kanban"] eklenir
- `ha_needed` context flag'i → OPTIONAL_TOOLS["homeassistant"] eklenir

### Tool Haritası

| Hermes Tool | ReYMeN Aracı | Export |
|-------------|--------------|--------|
| process | process_tool.py | `run(islem, pid, komut, ...)` |
| todo | todo_tool.py | `run(islem, icerik, gorev_id, ...)` |
| clarify | clarify_tool.py | `run(soru, secenekler, varsayilan)` |
| cronjob | cron_tool.py | `run(islem, job_id, ad, zamanlama, komut)` |
| patch | file_ops_tool.py | `run(islem="patch", path, old_string, new_string)` |
| search_files | file_ops_tool.py | `run(islem="search_files", pattern, target, path)` |
| skill_manage | skill_utils.py | Motor._skill_v2_araclari_kaydet() ile plugin olarak |
| x_search | x_search_tool.py | motor_kaydet() ile plugin olarak |

### Notlar
- **skill_utils.py** ve **x_search_tool.py**'nin standart `run()` fonksiyonu yoktur; bunlar motor_kaydet() veya doğrudan Motor sınıfı metodları ile kaydedilir.
- **file_ops_tool.py** hem `patch` hem `search_files` işlemlerini tek `run()` fonksiyonu üzerinden `islem` parametresi ile ayrıştırır.
- **kanban_orchestrator.py**, **homeassistant_tool.py**, **x_search_tool.py**'nin kendi `motor_kaydet()` fonksiyonları vardır, bunlar araçları doğrudan ToolRegistry'e kaydeder.
