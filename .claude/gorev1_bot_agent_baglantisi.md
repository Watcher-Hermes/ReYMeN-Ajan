# GÖREV 1: Telegram Bot'unu ReYMeN Agent Loop'una Bağla

## Hedef
telegram_bot/bot.py'deki `_deepseek_istek()` fonksiyonu şu anda `reymen_agent.isleyen_gorev()`'i çağırıyor ama bu fonksiyon `run_conversation()`'ı stdout capture ile çalıştırmaya çalışıyor ve başarısız oluyor, sonra direkt DeepSeek API fallback'e düşüyor. Yani bot ASLA ReYMeN araçlarını (PROJE_TARA, EKRAN_FOTOGRAF_CEK, hafıza, motor.py tool'ları) kullanmıyor.

## Yapılacaklar

### A) reymen_agent.py'yi yeniden yaz

Şu anki dosya: `/c/Users/marko/OneDrive/Desktop/Reymen Proje/hermes_projesi/reymen_agent.py`

Sorun: `isleyen_gorev()` fonksiyonu `agent.run_conversation(gorev_metni)` çağırıp stdout capture ile sonucu almaya çalışıyor. `run_conversation()` print tabanlı çalıştığı için bu yöntem güvenilmez.

Çözüm: `AIAgentOrchestrator`'ın `run_conversation()` metodunu incele. Eğer `run()` metodu varsa ve return değeri döndürüyorsa onu kullan. Yoksa motor.py'nin `calistir()` metodunu kullanarak doğrudan agent loop'u çalıştır.

Gerekli değişiklikler:
1. `isleyen_gorev()` — stdout capture KALDIR, doğrudan return al
2. Agent'ın son mesajını (assistant yanıtı) döndür
3. Başarısız olursa `_deepseek_fallback()`'a düş (şu anki gibi)

### B) Köprü watcher'ı düzelt

`bot.py` satır 42-83: `_kopru_dinle()` fonksiyonu direkt `requests.post("https://api.deepseek.com/...")` çağırıyor.

Değiştir: `import reymen_agent` kullanarak `reymen_agent.kopru_deepseek_istek()` veya `reymen_agent.isleyen_gorev()` çağır.

### C) Handle message'ı güncelle

`bot.py` satır 303-342: `handle_message()` fonksiyonu `_deepseek_istek(gecmis)` çağırıyor. Bu fonksiyon zaten `reymen_agent`'ı kullanıyor — A adımında düzeltince otomatik çalışır.

## Test
```python
cd /c/Users/marko/OneDrive/Desktop/Reymen\ Proje/hermes_projesi
python -c "
from reymen_agent import isleyen_gorev
sonuc = isleyen_gorev('merhaba, nasilsin?')
print('SONUC:', sonuc[:200])
assert 'merhaba' in sonuc.lower() or 'Merhaba' in sonuc or 'nasıl' in sonuc
print('TEST GECTI')
"
```
