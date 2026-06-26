# Hermes Projelerinde Repo Hijyeni

> ReYMeN/ReYMeN-Ajan gibi Hermes-Agent fork'larında, Hermes runtime dosyaları (`profile_backup/`, `cron/output/`, session dump'ları) kaçınılmaz olarak repo root'unda birikir. Bunlar git status'i kirletir ve merge/push işlemlerini karmaşıklaştırır.

---

## 1. `.profile_backup/` Temizlik Pattern'i

### Sorun
Hermes gateway çalışırken `.profile_backup/` altında sürekli yeni dosyalar oluşur:
- `cron/output/*.md` — cron job çıktıları
- `sessions/request_dump_*.json` — session dump'ları
- `cache/terminal/hermes-*` — terminal snapshot'ları
- `memories/` — memory yedekleri
- `gateway.lock`, `gateway.pid`, `gateway_state.json` — runtime state

Bunlar git'e girmez — sadece local runtime state.

### Çözüm

```bash
# 1. Git'ten çıkar (tracking'i kaldır, dosyaları diskte bırak)
git rm -r --cached .profile_backup/

# 2. .gitignore'a ekle
echo ".profile_backup/" >> .gitignore

# 3. Commit + push
git add .gitignore
git commit -m "chore: .profile_backup gitignore'a eklendi"
git push
```

**Uyarı:** `git rm` silmez — sadece git'in takibini bırakır. Dosyalar diskte kalır, Hermes çalışmaya devam eder.

### Doğrulama
```bash
# Temizlenmiş repo:
git status --short | grep -c ".profile_backup"  # → 0 olmalı
```

---

## 2. Unrelated Histories (Farklı Branch Geçmişleri)

### Sorun
Aynı repo'da iki branch (örn: local `main` ve remote `master`) farklı başlangıç noktalarından fork edilmiş olabilir. `git pull` veya `git merge` şu hatayı verir:
```
fatal: refusing to merge unrelated histories
```

### Tanı
```bash
# Branch'leri kontrol et
git branch -a

# İki branch arasındaki farkı göster
git rev-list --count HEAD..origin/master   # remote'da olup local'de olmayan commit sayısı
git rev-list --count origin/master..HEAD   # local'de olup remote'da olmayan

# Dosya listelerini karşılaştır
git ls-tree --name-only -r HEAD > /tmp/local_files.txt
git ls-tree --name-only -r origin/master > /tmp/remote_files.txt
diff /tmp/local_files.txt /tmp/remote_files.txt | head -40
```

### Karar Ağacı

| Durum | Yapılacak |
|-------|-----------|
| Remote sadece eski konuşma/yedek dosyaları içeriyor | **Merge etme.** Local daha güncel. |
| Remote'da yeni skill/modül dosyaları var | **Cherry-pick veya checkout** ile sadece o dosyaları al |
| İkisi de önemli değişiklikler içeriyor | `--allow-unrelated-histories` ile merge, conflict'leri çöz |

### Sadece Belirli Dosyaları Alma (Unrelated Durumunda)

```bash
# 1. Remote'dan sadece skills/ altındaki yeni dosyaları çek
git checkout origin/master -- skills/error_classifier/

# 2. Stage et ve commit
git add skills/error_classifier/
git commit -m "feat: error_classifier modulu remote master'dan alindi"
```

Bu yöntem, unrelated histories'de bile çalışır çünkü tek tek dosya checkout'u yapar.

### Merge Abort (Çok Fazla Conflict Varsa)

```bash
# Merge'i iptal et
git merge --abort

# Alternatif: sadece dosya bazında al
# (yukarıdaki checkout yöntemi)
```

---

## 3. Runtime Artifact Türleri ve Yönetimi

| Tür | Örnek | Git'te Kalmalı mı? | Çözüm |
|-----|-------|--------------------|-------|
| Cron job çıktıları | `cron/output/*.md` | ❌ | `.gitignore`'a ekle |
| Session dump'ları | `sessions/request_dump_*.json` | ❌ | `.gitignore`'a ekle |
| Terminal cache | `cache/terminal/hermes-*` | ❌ | `.gitignore`'a ekle |
| Gateway state | `gateway.lock`, `gateway.pid` | ❌ | `.gitignore`'a ekle |
| Memory yedekleri | `memories/MEMORY.md`, `memories/USER.md` | ❌ | `.gitignore`'a ekle |
| LSP binary'leri | `lsp/bin/*` | ❌ | `.gitignore`'a ekle |
| Skill yedekleri | `skills/.profile_backup/*` | ❌ | `.gitignore`'a ekle |
| Bandit raporları | `bandit_report.json` | ❌ | `.gitignore`'a ekle |

### Genel Kural
Hermes runtime tarafından oluşturulan her dosya **git'e girmez**. Eğer `git status`'te runtime dosyaları görünüyorsa, `.gitignore` güncellenmeli ve `git rm --cached` ile tracking kaldırılmalıdır.

---

## 4. Periyodik Repo Sağlık Kontrolü

Ayda bir veya büyük değişiklik öncesi:

```bash
# 1. Gereksiz dosyalar birikmiş mi?
git status --short | grep "^?" | wc -l
# → 5+ untracked file varsa .gitignore kontrol et

# 2. GitHub limitine yaklaşıyor muyum?
git count-objects -vH

# 3. Branch'ler senkron mu?
git fetch --all
git log --oneline HEAD..origin/main --count  # behind
git log --oneline origin/main..HEAD --count  # ahead
```
