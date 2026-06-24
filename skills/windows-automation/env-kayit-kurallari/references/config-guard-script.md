# Config Guard Script Referansı

## Konum
- Proje: `reymen/sistem/monitoring/config_guard.py`
- Hermes: `~/.hermes/scripts/config_guard.py`

## Kullanım
```bash
# Sadece okuma (güvenli)
python ~/.hermes/scripts/config_guard.py

# Otomatik düzeltme (yedekleme ile)
python ~/.hermes/scripts/config_guard.py --fix

# Detaylı rapor
python ~/.hermes/scripts/config_guard.py --report
```

## Kontrol Edilenler
1. Eski key'ler (sk-syl1..., sk-s5m5e...)
2. Key tutarlılığı (tüm .env'lerde aynı key)
3. Eksik key'ler
4. Model tutarlılığı

## Cron Job
- Job ID: `c2c8d157e4ed`
- Schedule: Her 30 dakika
- Otomatik çalışır

## Güvenlik
- Varsayılan: Sadece okuma
- Değişiklik için `--fix` zorunlu
- Otomatik yedekleme
- Log: `logs/monitoring/config_guard.log`
