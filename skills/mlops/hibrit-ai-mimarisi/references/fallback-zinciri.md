# Fallback Zinciri (DeepSeek → Ollama)

ReYMeN Agent'in model fallback hiyerarşisi ve yaygın yanlış anlamalar.

## Gerçek Fallback Zinciri

```
DeepSeek V4 Flash (uzak, OpenRouter)
  → (API hatası / timeout / kredi yoksa)
    → Ollama dolphin-llama3 (yerel, localhost:11434)
      → (Ollama da yoksa)
        → Sonsuza kadar CLI hatası, kullanıcıya bildir
```

**Xiaomi, Groq, OpenRouter alternatif model YOK.** Fallback sadece Ollama.

## Yanlış Anlamalar

| Yanlış | Doğru | Açıklama |
|:-------|:------|:---------|
| "Fallback Xiaomi" | ❌ | Xiaomi diye bir provider yapılandırması yok |
| "Fallback OpenRouter başka model" | ❌ | OpenRouter sadece DeepSeek için. Düşerse Ollama'ya gider |
| "Birden çok fallback" | ❌ | `fallback_providers: []` boş, tek fallback Ollama |

## config.yaml Fallback Yapılandırması

```yaml
model:
  default: deepseek-v4-flash
  provider: custom
  model: deepseek-v4-flash
  base_url: https://api.deepseek.com/v1

model_aliases:
  deepseek:
    model: deepseek-v4-flash
    provider: custom
    base_url: https://api.deepseek.com/v1
  dolphin:
    model: dolphin-llama3:latest
    provider: custom
    base_url: http://localhost:11434/v1

# DİKKAT: fallback_providers boş — ek bir yedek YOK
fallback_providers: []
```

**Şu anki durum:** fallback_providers boş. DeepSeek + Ollama ikisi de çökerse tam durma olur.

## Önerilen Düzeltme (Güvenli Fallback)

```yaml
fallback_providers:
  - provider: custom
    model: dolphin-llama3:latest
    base_url: http://localhost:11434/v1
```

Bu eklenmezse ve DeepSeek API kapalıyken Ollama da çalışmıyorsa → tam çökme.
