# Motor.py Mimarisi — Yeni Dosya Yapısı

## Klasör Yapısı

```
reymen/cereyan/motor/              ← YENİ KLASÖR
├── __init__.py                    → Motor class + public API export
├── config.py                      → Sabitler, regex'ler, ROOT path
├── utils.py                       → file_safety, path_security, gateway_state
├── providers.py                   → Provider yönetimi, setup.json
├── tool_registry.py               → CORE_TOOLS, OPTIONAL_TOOLS, get_active_tools
├── context.py                     → ContextCompressor, PromptCache wrapper
├── plugins.py                     → Plugin yönetimi, skill araç kaydı
└── main.py                        → Motor class (calistir, eylemi_ayristir)
```

## Bağımlılık Yönü

```
utils → config → providers → tool_registry → plugins → context → main
```

Her modül kendinden öncekine bağımlı olabilir, tersi DEĞİL.

## Dosya Sorumlulukları

| Dosya | Yaklaşık Satır | İçerik |
|-------|---------------|--------|
| `__init__.py` | 10 | Motor import + public API |
| `config.py` | 100 | ROOT, _BILINEN, TOOLSET_GRUPLARI, _DURUM_MESAJLARI, _RISKLI_ARACLAR |
| `utils.py` | 100 | file_safety wrapper, path_security wrapper, _gateway_durum_yaz, import helpers |
| `providers.py` | 250 | _setup_oku, aktif_provider_listele, provider_test_et, provider_degistir |
| `tool_registry.py` | 120 | CORE_TOOLS, OPTIONAL_TOOLS, get_active_tools |
| `plugins.py` | 200 | _skill_araclari_kaydet, _skill_v2_araclari_kaydet, _hafiza_araclari_kaydet |
| `context.py` | 80 | _cevabi_temizle, _context_sikistir, _cache_kontrol, _cache_kaydet |
| `main.py` | ~500 | Motor class (init, calistir, _fallback_calistir, eylemi_ayristir) |

## Modüllere Taşınacak Kodlar

### config.py
- ROOT = Path(__file__).parent
- _BILINEN set (eylemi_ayristir için)
- TOOLSET_GRUPLARI
- _DURUM_MESAJLARI  
- _RISKLI_ARACLAR
- _TERCIH_DOSYASI

### utils.py
- _dosya_guvenli wrapper
- _yol_dogrula wrapper
- _gateway_durum_yaz()
- _CUA_MEVCUT, _CUA fonksiyonları
- _SAGLIK_MEVCUT, _HealthChecker
- Genel yardımcı fonksiyonlar

### providers.py
- Tüm provider sabitleri (9 provider)
- _setup_oku()
- aktif_provider_listele()
- provider_test_et()  
- provider_degistir() (Motor method)
- provider_degistir() (module-level function)

### tool_registry.py
- CORE_TOOLS listesi
- OPTIONAL_TOOLS dict
- get_active_tools()
- _REGISTRY, _REGISTRY import helper

### plugins.py
- _PLUGIN_MGR, _PLUGIN_YUKLEYICI
- _PluginYukleyici import
- PluginManager import
- _skill_araclari_kaydet()
- _skill_v2_araclari_kaydet()
- _hafiza_araclari_kaydet()

### context.py
- _COMPRESSOR, _CACHE
- _agent_temizle, _pii_temizle
- _cevabi_temizle()
- _context_sikistir()
- _cache_kontrol() / _cache_kaydet()

### main.py (küçültülmüş Motor class)
- Motor class
- __init__(), _lazy_*, hook_kaydet()
- calistir_fc(), tools_schema_al(), _plugin_araclar
- eylemi_ayristir(), _parametreleri_coz()
- calistir(), _paralel_calistir(), _hook_tetikle()
- _fallback_calistir()
- check_fn_kaydet(), musait_araclar(), toolset_tanimi_al(), tum_arac_tanimini_al()
- _durum_goster()
- __main__ test kodu

### __init__.py
- from reymen.cereyan.motor.main import Motor
