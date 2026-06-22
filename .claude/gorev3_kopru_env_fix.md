# GÖREV 3: Köprü Watcher Env Sorununu Düzelt

## Hedef
`telegram_bot/bot.py`'deki `_kopru_dinle()` thread'i `.env` dosyasını doğru yüklemiyor. Thread içinde `os.environ.get("DEEPSEEK_API_KEY")` boş dönüyor çünkü thread başlamadan önce `.env` yüklenmiş olsa bile, thread kendi ortamında görmeyebilir.

## Yapılacaklar

Dosya: `/c/Users/marko/OneDrive/Desktop/Reymen Proje/hermes_projesi/telegram_bot/bot.py`

### A) Köprü watcher'ı reymen_agent üzerinden çalıştır

`_kopru_dinle()` fonksiyonundaki direkt DeepSeek API çağrısını (satır 55-73) kaldır, yerine `reymen_agent.isleyen_gorev()` kullan:

```python
import reymen_agent as _ra
# ...
sonuc = _ra.isleyen_gorev(gorev_metni, chat_id="kopru")
```

### B) Global env kontrolü ekle

Bot başlangıcında `main()` fonksiyonunda env değişkenlerini doğrula:
```python
# .env'nin gerçekten yüklendiğini doğrula
if not os.getenv("DEEPSEEK_API_KEY"):
    # Tekrar dene
    load_dotenv(dotenv_path, override=True)
```

### C) Thread-safe env erişimi

Köprü watcher thread'i için env değişkenlerini thread başlamadan önce oku, thread'e argüman olarak geç:

```python
_deepseek_key = os.getenv("DEEPSEEK_API_KEY", "")

def _kopru_dinle(api_key: str):
    # api_key parametresini kullan, os.environ'ı değil
    ...
```

## Test
```python
cd /c/Users/marko/OneDrive/Desktop/Reymen\ Proje/hermes_projesi
python -c "
from dotenv import load_dotenv
from pathlib import Path
import os

# .env'nin dogru yuklendigini kontrol et
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path, override=True)
key = os.getenv('DEEPSEEK_API_KEY', '')
print(f'API Key var: {bool(key)}')
assert key, 'DEEPSEEK_API_KEY .env\'de bulunamadi!'
print('TEST GECTI')
"
```
