# Skill Kategorizasyon Deseni — Gerçek Dünya Uygulaması

> 2026-06-21 · 2176 ham skill → 1130 organize · 30 kategori · 0 uncategorized

## 1. Keşif Aşaması

```bash
# Dosya sayısı ve ön ek analizi
python3 -c "
import os
from collections import Counter
files = [f for f in os.listdir(skills_dir) if f.endswith('.md')]
prefixes = Counter()
for f in files:
    if '_' in f:
        p = f.split('_')[0]
    else:
        p = f.split('-')[0]
    prefixes[p] += 1
"
```

**Gerçek dünya sonucu:** 2176 ham dosya, 1079 duplicate, 1097 benzersiz skill.

## 2. full_ Duplicate Stratejisi

| Durum | Karar |
|:------|:------|
| `full_X.md` + `X.md` var | → `full_X.md` korunur, `X.md` silinir |
| Sadece `full_X.md` var | → `full_` öneki kaldırılır, `X.md` olur |
| Sadece `X.md` var | → olduğu gibi kalır |

**Gerçek dünya:** 1079 duplicate silindi (`full_` 1079, eşsiz 1097).

```python
# Batch move + dedup
by_basename = defaultdict(list)
for f in files:
    base = f.replace('.md','')
    name = base[5:] if base.startswith('full_') else base
    by_basename[name].append(f)

for basename, variants in by_basename.items():
    has_full = any('full_' in v for v in variants)
    has_normal = any('full_' not in v for v in variants)
    
    if has_full and has_normal:
        # Keep full, delete normal
        full_v = [v for v in variants if v.startswith('full_')][0]
        shutil.move(full_v, target / f'{basename}.md')
        os.remove(normal_v)
```

## 3. Kategori Atama Desenleri

### Ön Ek Tablosu (gerçek dünya verisi)

| Ön Ek / Desen | Kategori | Adet |
|:---------------|:---------|:----:|
| `ecc_*` | ai/ecc | 261 |
| `creative_*` | creative | 22 |
| `devops_*` | devops | 23 |
| `software-development_*` | software-development | 54 |
| `windows-automation_*` | windows/automation | 46 |
| `autonomous-ai-agents_*` | autonomous-ai-agents | 28 |
| `user-preferences_*` | user/preferences | 17 |
| `mlops_*` | mlops | 26 |
| `productivity_*` | productivity | 27 |
| `note-taking_*` | note-taking | 12 |
| `research_*` | research | 8 |
| `media_*` | media | 11 |
| `github_*` | github | 6 |
| `apple_*` | apple | 5 |
| `security_*` | security | 28 |
| `data-science_*` | data-science | 3 |

### İsim bazlı kategori eşleme

```python
rules = [
    (lambda n: any(n==x for x in ['ascii-art','excalidraw','sketch','p5js']), 'creative'),
    (lambda n: any(n==x for x in ['cron-job-bakimi','fork-sync','virtualbox']), 'devops'),
    (lambda n: 'voice' in n or 'speech' in n or 'tts' in n, 'voice'),
    # ... 30+ kural
]
```

## 4. Misc Alt Kategori Ayırma

İlk turda sınıflandırılamayanlar (bu oturumda 411 dosya) ikinci aşamada alt kategorilere ayrılır:

| Alt Kategori | Desen | Adet |
|:-------------|:------|:----:|
| prompt-engineering | prompt, function-calling | 92 |
| agent-systems | agent, swarm, multi, handoff | 45 |
| mcp-integration | mcp, gateway, oauth | 14 |
| llm-inference | llm, inference, vllm | 11 |
| architecture | transformer, attention, moe | 8 |
| vision | vision, vlm, vit, clip | 8 |
| evaluation | eval, benchmark, lm-eval | 5 |
| training | training, finetuning, rlhf | 5 |
| infrastructure | distributed, gpu, quantization | 4 |
| rag-search | rag, embedding, search | 4 |
| gaming | gaming | 6 |
| safety-security | safety, jailbreak, red-team | 3 |
| video | video, remotion | 1 |
| hermes-integration | hermes, reymen | 1 |

## 5. Türkçe Karakter Normalleştirme

Windows'da dosya isimlerinde Türkçe karakter (ı,ş,ü,ö,ğ) olabilir. Python'un `os.listdir()` bu karakterleri doğru verir ama elle yazılan string'ler eşleşmeyebilir.

```python
import unicodedata

def norm(s):
    """Normalize Turkish characters for matching"""
    nfkd = unicodedata.normalize('NFKD', s)
    return nfkd.encode('ASCII', 'ignore').decode().lower()

# Kullanım:
target = MAP.get(f) or MAP.get(norm(f))
```

**Pitfall:** `os.listdir()` çıktısındaki karakterler elle yazılandan farklı olabilir. Her zaman normalizasyon fonksiyonu kullan.

## 6. Çakışma Çözümü (_2 Suffix)

Aynı hedef dosya adı varsa `_2` suffix'i eklenir:

```python
if os.path.exists(dst):
    dst = dst.replace('.md', '_2.md')
```

Bunlar sonradan elle temizlenmelidir — otomatik temizlik tehlikelidir.

## 7. Final Doğrulama

```python
# Her kategorideki dosya sayısı
for root, dirs, files in os.walk(skills_dir):
    for f in files:
        if f.endswith('.md'):
            total += 1

# Düzeltilemeyenler (elle müdahale gerek)
flat = [f for f in os.listdir(skills_dir) if f.endswith('.md')]
```

**Hedef:** 0 flat, 0 uncategorized, tüm dosyalar kategorili klasörlerde.
