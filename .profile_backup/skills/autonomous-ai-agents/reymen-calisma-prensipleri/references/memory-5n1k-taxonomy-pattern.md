# Memory 5N1K Taxonomy Classification Pattern

> **Amaç:** Binlerce DB kaydını (örn: 1773) 5N1K (Ne? Nerede? Nasıl? Neden? Kim?) şemasına göre sınıflandırma.  
> **Gerçek dünya (2026-06-21):** 1773 kayıt → 55 ana başlık, 25 alt başlık, 0 uncategorized  
> **İlgili skill:** `reymen-calisma-prensipleri` bölüm 9b

---

## 1. Keşif Aşaması

```python
import sqlite3
conn = sqlite3.connect("ogrenmeler.db")
c = conn.cursor()

# Mevcut kategori dağılımı
c.execute("SELECT kategori, COUNT(*) FROM ogrenmeler GROUP BY kategori ORDER BY COUNT(*) DESC")
for r in c.fetchall():
    print(f"  {r[0]:40s} {r[1]:4d}")

# Toplam kayıt
c.execute("SELECT COUNT(*) FROM ogrenmeler")
print(f"Toplam: {c.fetchone()[0]}")
```

## 2. DB Şemasına 5N1K Kolonları Ekle

```sql
ALTER TABLE ogrenmeler ADD COLUMN ne TEXT DEFAULT '';
ALTER TABLE ogrenmeler ADD COLUMN nerede TEXT DEFAULT '';
ALTER TABLE ogrenmeler ADD COLUMN nasil TEXT DEFAULT '';
ALTER TABLE ogrenmeler ADD COLUMN neden TEXT DEFAULT '';
ALTER TABLE ogrenmeler ADD COLUMN kim TEXT DEFAULT '';
```

## 3. Keyword Tabanlı Sınıflandırma

```python
NE_RULES = {
    "ecc": ["ecc", "ecc---", "ecc_", "edge case", "agentic",
            "benchmark", "blueprint", "canary", "config-gc",
            "content-engine", "context-budget", "continuous"],
    "AI/ML": ["mlops", "ai", "machine-learning", "deep-learning"],
    "Ağ": ["network", "ag", "nmap", "netstat", "ipconfig", "port", "wifi"],
    "Kod": ["software-development", "code", "yazilim", "kod", "python"],
    "Windows": ["windows", "windows-automation", "windows/terminal"],
    "Yaratıcı": ["creative", "ascii", "excalidraw", "p5js", "sketch"],
    "Medya": ["media", "video", "audio", "voice", "gif", "youtube"],
    "Test": ["test", "benchmark", "evaluation", "pytest"],
    "DevOps": ["devops", "backup", "cron", "deploy", "git-push"],
    "Güvenlik": ["security", "pentest", "firewall", "safety"],
}

def classify(text):
    for key, keywords in NE_RULES.items():
        if any(kw in text for kw in keywords):
            return key
    return None
```

## 4. İkinci Aşama: Misc/Prompt Kategorilendirme

İlk aşamada sınıflandırılamayanlar için daha spesifik keyword listesi:

```python
P2_RULES = {
    "ai/ecc": ["ecc_access", "ecc_agent", "ecc_android", "ecc_api",
               "ecc_python", "ecc_react", "ecc_django", "ecc_rust"],
    "ai/prompt": ["prompt-", "prompt_", "structured-output"],
    "ai/nlp": ["ner", "nli", "sentiment", "tokenizer", "seq2seq",
               "summary", "text-encoder", "topic", "chunker", "grammar"],
    "ai/inference": ["inference", "vllm", "runtime", "sampling",
                     "spec-decode", "radix", "trtllm"],
    "ai/training": ["training", "finetuning", "lora", "rlhf", "ppo",
                    "dqn", "gan", "vae", "diffusion"],
    "ai/agents": ["a2a", "agents-sdk", "consensus", "debate",
                  "marl", "swarm", "orchestration"],
    "ai/mcp": ["mcp-apps", "mcp-auth", "mcp-client", "mcp-server",
               "mcp-handshake", "gateway"],
}
```

## 5. Alt Başlık → Ana Başlık Promosyonu

10+ kaydı olan alt başlıklar ana başlığa yükseltilir:

```python
PROMOTE = {
    "ai/ecc": "ecc",              # 392
    "ai/prompt": "prompt",        # 51
    "ai/nlp": "nlp",              # 49
    "ai/inference": "inference",  # 42
    "ai/training": "training",    # 41
    "ai/agents": "ajan",          # 32
    "ai/architecture": "mimari",  # 30
    "ai/evaluation": "degerlendirme", # 66
    "devops/cicd": "cicd",        # 25
    "security/audit": "denetim",  # 19
}

for old, new in PROMOTE.items():
    c.execute("UPDATE ogrenmeler SET ne=? WHERE ne=?", (new, old))
```

## 6. "Diğer" Avı (Art Arda Keyword Ekleyerek Sıfırla)

Her turda hedef: kalan "Diğer" kayıt sayısını azalt.

| Tur | Başlangıç | Bitiş | Strateji |
|:----|:---------|:-----|:---------|
| 1 | 930 | 149 | Ana keyword listesi |
| 2 | 149 | 103 | Spesifik dosya adı eşlemesi |
| 3 | 103 | 39 | NLP kategorileri + skill-* kalıpları |
| 4 | 39 | 6 | Son kırıntılar |
| 5 | 6 | 0 | Türkçe normalize + son manuel |

## 7. Türkçe Karakter Normalleştirme

```python
import unicodedata

def norm(s):
    """Türkçe karakterleri ASCII'ye çevir (ı,ş,ü,ö,ğ,İ)"""
    nfkd = unicodedata.normalize('NFKD', s)
    return nfkd.encode('ASCII', 'ignore').decode().lower()

# Dosya adı eşlemesinde kullan
target = MAP.get(f) or MAP.get(norm(f))
```

## 8. Çıktı Ağacı Formatı

```python
# Ana başlık dağılımı
c.execute("""
SELECT 
  CASE WHEN ne LIKE '%/%' THEN SUBSTR(ne, 1, INSTR(ne, '/')-1) ELSE ne END as ana,
  COUNT(*) 
FROM ogrenmeler 
WHERE ne!='' 
GROUP BY ana 
ORDER BY COUNT(*) DESC
""")

for ana, cnt in c.fetchall():
    # Alt başlıkları getir
    c.execute("SELECT ne, COUNT(*) FROM ogrenmeler WHERE ... LIKE ...")
    subs = c.fetchall()
    if subs:
        parts = [f"{s[0].rsplit('/',1)[-1]}:{s[1]}" for s in subs]
        print(f"├── {emoji} {ana:20s} {cnt:4d}  ({', '.join(parts)})")
    else:
        print(f"├── {emoji} {ana:20s} {cnt:4d}")
```

## 9. Nihai Kontrol

```python
c.execute("SELECT COUNT(*) FROM ogrenmeler WHERE ne='Diğer'")
assert c.fetchone()[0] == 0, "Hala sınıflandırılamayan kayıt var!"
```
