# Hermes Profil Yönetimi

## Profil Yapısı
```
~/.hermes/profiles/
├── default/     → Paşa botu (varsayılan)
├── kiral38/     → Kral_38 botu
└── reymen/      → ReYMeN botu
```

Her profil kendi `config.yaml`'ına sahip. Tüm profiller aynı proje dizinini kullanır.

## Profil Eşitleme Kuralları

### Fallback Provider Zinciri
Tüm profiller aynı fallback zincirini kullanmalı:
```yaml
fallback_providers:
- provider: deepseek
  model: deepseek-v4-flash
  base_url: https://api.deepseek.com
  api_mode: chat_completions
- provider: openrouter
  model: deepseek/deepseek-v4-flash
  base_url: https://openrouter.ai/api/v1
  api_mode: chat_completions
- provider: lmstudio
  model: local-model
  base_url: http://127.0.0.1:1234/v1
  api_mode: chat_completions
```

### Pitfall: xAI Silinmiş Ama Profilde Kalmış
xAI provider silindi (9x pahalı) ama reymen profilinde hala fallback olarak kalmış.
Her provider değişikliğinde TÜM profilleri kontrol et.

### Profil Eşitleme Komutu
```bash
# default profilini kiral38 ile eşitle
cp ~/.hermes/profiles/kiral38/config.yaml ~/.hermes/profiles/default/config.yaml
```

## Kod Değişiklikleri
Proje dizinindeki kod değişiklikleri (prompt_builder.py, conversation_loop.py, main.py)
tüm profilleri otomatik etkiler — çünkü hepsi aynı dosyaları kullanır.

## Kontrol Listesi
- [ ] 3 profil de aynı fallback zincirine sahip mi?
- [ ] Silinmiş provider profillerde kalmış mı?
- [ ] Kod değişiklikleri tüm profilleri etkiliyor mu?
- [ ] default profili boş mu? (kiral38 ile eşitle)
