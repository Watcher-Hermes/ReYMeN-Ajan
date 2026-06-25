GitHub asdafgf (gh CLI). Repo: Watcher-Hermes/ReYMeN-Ajan (origin) & hermes-memory-backup (backup). Push Protection: API key'leri .gitignore + git rm --cached ile commit'ten çıkar, .env dışında tut.
§
Kredi kartı yasağı: Hiçbir ödeme/satın alma işlemi yapılmaz. Karşılaşılırsa hosts+firewall ile domain engellenir.
§
Kali yasağı: Kali pentest araçları kullanıcı açıkça izin vermedikçe KESİNLİKLE kullanılmaz. İzin verse bile her adımda onay alınır.
§
Dosya yolları: Ana masaüstü C:\Users\marko\OneDrive\Desktop, Obsidian vault C:\Users\marko\OneDrive\Belgeler\Obsidian Vault. .env: C:\Users\marko\AppData\Local\hermes\.env.
§
ReYMeN: ~/Desktop/Reymen Proje/hermes_projesi. REYMEN API KEY FIX: ~/.hermes/profiles/reymen/.env'ye DEEPSEEK_API_KEY eklenmeli yoksa "Provider deepseek is set but no API key" hatası. Ana .env'deki key profile otomatik geçmez. OneDrive dışına taşındı.
§
Paşa (@Pasa_38_bot) token: 8925395268:*** — default profil .env'de, gateway aktif.
§
ReYMeN Telegram bot token (@ReYMeN_ReYMeNbot): 8774151638:*** — reymen profil .env'de, gateway aktif.
§
KONTROL KURALI: 'X yok' demeden 3 yöntem tara: find, tasklist, where. Pes etmeden önce alternatifleri dene. Skill: reymen-kontrol-kurali.
§
Once_hafiza.py: _kademeli_guven() sigmoid (ilk=0.5), kaynak_url kolonu. Skill reymen-hafiza-oncelikli-akis v2.1.0
§
CRON: once cronjob list ile kontrol et, ayni is varsa manuel yapma. Terminal bloke → process kill + gateway restart. Skill: cron-management.md
§
SKILL KONSOLIDASYONU TAMAM (2026-06-21): 1130 skill, 30 kategori, 0 uncategorized. 1079 duplicate budandi. En buyuk: ai/ecc (283), mlops/skills (80), software (64), devops (44), security (36).
§
MEMORY MERKEZI: reymen/cereyan/.ReYMeN/memory.db (18991 kayit, 323 baslik, 0 uncategorized). 10 DB -> 1 DB, FTS5 indeksi aktif. 5N1K ile siniflandirilir, uymazsa yeni baslik acilir. Skills: 1130 dosya, 30 kategori.
§
SESSIZ ONAY: 3dk bekle, cevap gelmezse onay say ve devam et.
§
CLARIFY yasak — asla kullanma. Belirsizse en mantıklı varsayımla devam et.
§
SIRAYLA GIT: sıralı görevlerde sırayla git, her adımda otomatik geç, onay bekleme.
§
Gateway reset KESINLIKLE yapilmaz. Terminal sorunu → delegate_task veya os.walk dene.
§
dummy