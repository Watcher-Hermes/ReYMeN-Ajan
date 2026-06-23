# ReYMeN Agent — SINIRLAR ve BOŞLUKLAR Analizi

> Tarih: 2026-06-23
> Kaynak: conversation_loop.py, iteration_budget.py, config.yaml, motor.py, approval.py, alt_ajan.py, tools/

---

## 1. RATE / CYCLE LIMITLERİ

| Sabit / Parametre | Değer | Kaynak | Açıklama |
|---|---|---|---|
| `general.max_turns` | **15** | `config.yaml` | Genel konuşma tur limiti (varsayılan) |
| `ConversationLoop.max_tur` | **30** | `conversation_loop.py:279` | Loop constructor default'u (max_tur=30) |
| `IterationBudget.max_total` (ana ajan) | **90** | `iteration_budget.py:34` | Thread-safe iterasyon limiti |
| `IterationBudget.max_total` (alt ajan) | **50** | `alt_ajan.py` (delegasyon) | Alt ajan butçesi |
| `MAX_RETRY` (mekanik retry) | **3** | `conversation_loop.py:250` | Env: `MAX_RETRY` |
| `MAX_API_RETRY` (exponential backoff) | **3** | `conversation_loop.py:254` | API çağrısı başına max deneme |
| `CIRCUIT_BREAKER_MAX_HATA` | **3** | `conversation_loop.py:245` | Env: `CB_MAX_HATA`, 3 ardışık hata → kalıcı durdurma |
| `CIRCUIT_BREAKER_KALICI` | **True** | `conversation_loop.py:247` | Kullanıcı müdahalesi olmadan otomatik açılmaz |
| `TAKILMA_ESIĞI` | **3** | `conversation_loop.py:256` | Aynı eylem 3x tekrar = takılma tespiti |
| `CONTEXT_SIKISTIRMA_ESIGI` | %50 | `conversation_loop.py:178` | Env: `CONTEXT_ESIK`, %50 dolarsa sıkıştır |
| Provider token limit | **128K–200K** | `conversation_loop.py:182-194` | DeepSeek 128K, Claude 200K, GPT4 128K, vb. |
| `auto_recovery.max_restart_attempts` | **3** | `config.yaml` | Bileşen yeniden başlatma limiti |
| `auto_recovery.max_concurrent_failures` | **5** | `config.yaml` | Genel sistem çökme eşiği |
| `auto_recovery.cooldown_sec` | **60s** | `config.yaml` | Aynı bileşen için bekleme süresi |
| `memory.max_records` | **2000** | `config.yaml` | Hafıza kayıt limiti |

### ❌ EKSİKLİK: Günlük/haftalık limit yok
Projede **günlük veya haftalık API tüketim limiti, token kotası veya dönemsel bütçe** tanımlı değildir. Tüm limitler tek bir oturuma/konuşmaya aittir.

---

## 2. HUMAN-IN-THE-LOOP (HITL)

| Özellik | Durum | Detay |
|---|---|---|
| `approvals.mode` | **`smart`** (off değil) | `config.yaml:215` — mod: smart |
| `approvals.timeout` | **60s** | `config.yaml:216` |
| `approvals.command_allowlist` | **boş []** | `config.yaml:217` |
| Otomatik onay bypass | **Var** | `REYMEN_OTOMATIK_ONAY=true` env var ile tam otomatik (approval.py:80) |
| Hardline pattern'ler | **Her zaman aktif** | `rm -rf /`, fork bomb, dd, curl|bash — mod=off olsa bile engellenir (test_approvals.py:32-48) |
| Hassas dosya yazma onayı | **Var** | `tools/write_approval.py`: .env, config, secret, credential, .key, .pem, .netrc, .gitconfig |
| Onay mekanizması | **Dosya tabanlı** | `.ReYMeN/pending/*.json` ile çalışır |
| `ApprovalManager` singleton | **Var** | 3 mod: manual (default), smart, off |
| Test kapsamı | **Var** | `tests/test_approvals.py` — 155 satır, hardline + mod testleri |

### Değerlendirme
- `mode=off` olsa bile **hardline** (tehlikeli) komutlar engellenir — bu bir HITL noktasıdır
- `REYMEN_OTOMATIK_ONAY` env var ile tamamen devre dışı bırakılabilir
- **approvals.mode="off" tam anlamıyla "onaysız" değildir** — güvenlik katmanı hardline üzerinde kalır

---

## 3. SANDBOX / İZOLASYON

| Bileşen | Durum | Detay |
|---|---|---|
| `izole_laboratuvar.py` | ❌ **YOK** | `motor.py:84` import ediyor ama dosya mevcut değil (`ImportError` ile sessizce geçilir) |
| Docker sandbox | ⚠️ **Kısmi** | `tools/environments/docker.py` (pycache var) ama kullanımda değil, Dockerfile yok |
| Docker-compose | ❌ **YOK** | Projede Dockerfile veya docker-compose bulunmuyor |
| Modal sandbox | ⚠️ **Kısmi** | `tools/environments/modal.py` mevcut, aktif kullanımda değil |
| Alt ajan izolasyonu | ✅ **Kısmi** | `alt_ajan.py`: kendi thread'i, sınırlı araç seti (`_ALT_AJAN_IZINLI_ARACLAR`), ana context'e dokunmaz |
| Terminal backend | **`local` (default)** | `config.yaml:184` — doğrudan sistem erişimi |
| WSL backend | **Mevcut** | `config.yaml:191` — Windows WSL desteği |
| CUA (Computer Use) | **Mevcut** | `cua_motor_araci.py` — sandbox'suz ekran erişimi |
| Sistem prompt güvenliği | **`secure_binding: true`** | `config.yaml:11` |

### Değerlendirme
- **Gerçek bir sandbox/izolasyon katmanı YOKTUR.** `terminal_backends.default=local` olduğu için tüm araç çağrıları doğrudan host sisteme erişir.
- `izole_laboratuvar.py` tanımlanmış ama implemente edilmemiştir.
- Docker ve Modal altyapısı kod olarak mevcuttur ancak aktifleştirilmemiştir.

---

## 4. TANIMLI AMA İMPLEMENTE EDİLMEMİŞ ÖZELLİKLER

| Özellik / Fonksiyon | Durum | Etkilenen Kod |
|---|---|---|
| `standart_budget(hedef)` fonksiyonu | ❌ **Yok** | `conversation_loop.py:48,905` — import edilir ama `iteration_budget.py`'de tanımlı değil. Fallback: `_SimpleBudget` |
| `izole_laboratuvar.izole_python_calistir` | ❌ **Yok** | `motor.py:84` — `ImportError` ile degrade |
| `turn_retry_state.py` / `TurnRetryState` | ❌ **Yok** | `conversation_loop.py:35` — ImportError ile degrade |
| `turn_context.py` / `TurnYoneticisi` + `TurnContext` | ❌ **Yok** | `conversation_loop.py:42` — ImportError ile degrade |
| `prompt_builder.py` / `PromptBuilder` | ❌ **Yok** | `conversation_loop.py:57` — ImportError ile degrade |
| `session_db.py` / `AdvancedSessionStorage` | ❌ **Yok** | `conversation_loop.py:90` — ImportError ile degrade |
| `gorev_hafiza` modülü | ❌ **Yok** | `conversation_loop.py:845` — ImportError ile degrade |
| `reymen.hafiza.hata_analiz` modülü | ❌ **Yok** | `conversation_loop.py:866` — ImportError ile degrade |
| `PriorityTaskQueue` | ❌ **Projede hiç yok** | Ne tanım ne kullanım var |
| `SpacedRepetition` | ❌ **Projede hiç yok** | Ne tanım ne kullanım var |
| `TaskStateMachine` | ❌ **Projede hiç yok** | Ne tanım ne kullanım var |
| `reymen.cereyan.hook_dispatcher.py` | ❌ **Yok** | `conversation_loop.py:130` — ImportError ile degrade |
| `reymen.cereyan.stream_diagnostics.py` | ❌ **Yok** | `conversation_loop.py:151` — ImportError ile degrade |
| `reymen.cereyan.hata_siniflandirici.py` | ❌ **Yok** | `conversation_loop.py:98` — ImportError ile degrade |
| `reymen.cereyan.mesaj_tamirci.py` | ❌ **Yok** | `conversation_loop.py:113` — ImportError ile degrade |
| `acp_server` | ❌ **Yok** | `conversation_loop.py:886` — ImportError ile degrade |
| `context_compressor.py` (kök) | ❌ **Yok** | `conversation_loop.py:63` — ImportError ile degrade |

### Kritik Notlar
1. **`standart_budget()`**: ConversationLoop'un budget oluşturma mekanizması her zaman fallback'e düşer (`_SimpleBudget`). Bu, IterationBudget'un sunduğu thread-safe consume/refund/görev karmaşıklığı analizi özelliklerini kullanılamaz hale getirir.
2. **Tüm eksik modüller `ImportError` ile graceful degrade edilir** — sistem çalışır ama özellikler eksiktir.
3. **PriorityTaskQueue, SpacedRepetition, TaskStateMachine**: Projede **hiçbir yerde tanımlı değildir**. Bunlar planlanmış ancak hiç kodlanmamış özelliklerdir.

---

## 5. 4 MODÜL: github_tools, obsidian_watcher, onboarding, reymen.py

| Modül | Projede Var mı? | Durum / Açıklama |
|---|---|---|
| `github_tools.py` | ❌ **YOK** | GitHub işlemleri: `motor.py`'de GIT_COMMIT, GIT_PUSH, GIT_PULL, GIT_DURUM, GIT_EKLE araç adları var ama ayrı bir `github_tools.py` modülü yok. Ayrıca MCP üzerinden GitHub server bağlantısı yapılandırılmış (`config.yaml:272`). |
| `obsidian_watcher.py` | ❌ **YOK** | Obsidian izleme / not alma modülü projede mevcut değil. Obsidian ile ilgili hiçbir kod bulunamadı. |
| `onboarding.py` | ❌ **YOK** | Kullanıcı onboarding/ilk kurulum modülü yok. Projede yeni kullanıcıyı karşılama, yapılandırma sihirbazı gibi bir mekanizma bulunmamaktadır. |
| `reymen.py` | ❌ **YOK (dizin)** | `reymen/` bir Python paket dizinidir, dosya değildir. İçinde: `cereyan/` (çekirdek loop), `sistem/` (CLI, main), `hafiza/` (bellek), `arac/` (Windows araçları) alt modülleri vardır. |

### Mevcut Test Dosyaları (17 adet)
- `test_main_orchestrator.py`, `test_reymen_core.py`, `test_reymen_agent.py`
- `test_beyin.py`, `test_motor.py`, `test_mcp.py`, `test_cli.py`
- `test_approvals.py`, `test_fc_loop.py`, `test_cua_motor_araci.py`
- `test_alt_ajan.py`, `test_closed_learning_loop.py`
- `test_vektorel_hafiza.py`, `test_stream_diagnostics.py`
- `test_deepseek_plugin.py`, `test_hook_dispatcher.py`
- `test_hata_siniflandirici.py`, `test_mesaj_tamirci.py`
- `test_native_function_calling.py`, `test_agent_prompt_builder.py`
- `tools/test_execute_code_tool.py`, `tools/test_xai_http.py`, `tools/test_web_search_tool.py`, `tools/test_web_search.py`, `tools/test_tool_cache.py`, `tools/test_thread_context.py`, `tools/test_sistem_bilgisi.py`, `tools/test_screen.py`, `tools/test_read_terminal_tool.py`, `tools/test_python_exec.py`, `tools/test_path_security.py`, `tools/test_openrouter_client.py`

---

## ÖZET: KRİTİK BULGULAR

### 🔴 Yüksek Öncelikli
1. **Sandbox yok** — `izole_laboratuvar.py` implemente edilmemiş, local sistem erişimi default
2. **`standart_budget()` implemente edilmemiş** — IterationBudget'un gelişmiş özellikleri kullanılamaz, her zaman `_SimpleBudget` fallback'ine düşer
3. **Sınırsız dönemsel tüketim** — Günlük/haftalık API limiti, token kotası, maliyet sınırı yok

### 🟡 Orta Öncelikli
4. **Onay modu "off" olsa bile hardline pattern'ler engellenir** — gerçek "onaysız" mod mümkün değil (güvenlik amaçlı, bilinçli tasarım)
5. **3 ana modül (github_tools, obsidian_watcher, onboarding, reymen.py) projede yok** — bunların test edilmemesi normal çünkü hiç yazılmamışlar
6. **PriorityTaskQueue, SpacedRepetition, TaskStateMachine** — projede hiç tanımlı değil, konsept aşamasında kalmış

### 🟢 Düşük Öncelikli
7. **14 adet "yok modül" ImportError ile graceful degrade** — sistem çalışır, ilgili özellikler pasif kalır
8. **Test kapsamı: 17 test dosyası mevcut** — eksik modüller için test olmaması beklenir
