# Stub Analiz Rehberi

8 stub örneği üzerinden öğrenilen dersler.

## 3-Kademeli Doğrulama

Her `NotImplementedError` veya `pass` bulgusu için:

### 1. ABC Kontrolü
Dosyada `class X(ABC):` veya `@abstractmethod` var mı?
- Varsa NotImplementedError **bilinçli tasarım**
- `plugins/` dizininde alt sınıfları tara

### 2. Template Method Kontrolü
Temel sınıfta NotImplementedError + alt sınıflarda override var mı?
- Ör: ChannelHandler.send() NotImplementedError, TerminalChannel/TelegramChannel override eder

### 3. Test Mock/Re-export Kontrolü
Fonksiyon `__all__` içinde export edilmiş ve sadece raise NotImplementedError mı?
- Asıl implementasyon başka yerde (upstream, cli.py)

## Bu Oturumdaki 8 Örnek

| # | Dosya | Fonksiyon | Gerçek Stub? | Sebep |
|---|-------|-----------|-------------|-------|
| 1 | agent/web_search_provider.py | search/extract | ❌ | ABC, 23 plugin var |
| 2 | agent/tts_provider.py | stream | ❌ | ABC, dispatcher fallback |
| 3 | agent/memory_provider.py | handle_tool_call | ❌ | ABC, 24 plugin var |
| 4 | reymen/ag/gateway_runner.py | send | ❌ | Template Method |
| 5 | reymen/sistem/model_tools.py | handle_function_call | ❌ | Re-export stub |
| 6 | acp_adapter/events.py | _build_plan_update | ❌ | Tam implemente |
| 7 | agent/agent_runtime_helpers.py | invoke_tool/repair | ❌ | Tam implemente |
| 8 | agent/nous_rate_guard.py | rate_guard_basla/bitir | ✅ | Fix uygulandı |

## Öğrenilen Ders
Naif stub taraması %87.5 yanlış pozitif üretir (7/8). Doğrulama olmadan raporlama anlamsız.
