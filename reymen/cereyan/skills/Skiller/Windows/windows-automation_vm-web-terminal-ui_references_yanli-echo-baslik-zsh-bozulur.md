# YANLIŞ: echo "=== $BASLIK ===" && ... (zsh bozulur)
```

**Timeout ayarı:** Ağ taraması gibi uzun komutlar için `timeout=60` veya daha yüksek ayarla. Paramiko varsayılanı 15sn.

**Bağlantı koptuğunda:** `/status` endpoint'ini kontrol et:
```python
urllib.request.urlopen("http://localhost:5050/status").read()