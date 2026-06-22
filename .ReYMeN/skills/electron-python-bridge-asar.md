# Electron + Python Bridge — .asar Hatası Beş Neden Analizi

## Belirti
Python `[Errno 2] No such file or directory` — `resources/app.asar/python_bridge.py` yolunu bulamıyor.

## Beş Neden

| Seviye | Neden |
|--------|-------|
| Neden 1 | Python `resources/app.asar/python_bridge.py` yolunu açamıyor — `.asar` sanal arşiv |
| Neden 2 | `python_bridge.py` `"asarUnpack"` olmadığı için `.asar` içine gömülüyor |
| Neden 3 | `package.json` build config'inde `asarUnpack` veya `extraResources` yok |
| Neden 4 | `main.js`'de `path.join(__dirname, 'python_bridge.py')` sadece `.asar` içini kontrol ediyor |
| Kök Neden | `.py` dosyaları `.asar` dışında tutulmalı — arşiv yalnızca JS modülleri için güvenli |

## Çözüm

### Seçenek A — asarUnpack
```json
"asarUnpack": ["python_bridge.py", "*.py"]
```

### Seçenek B — extraResources
```json
"extraResources": [{"from": "python_bridge.py", "to": "python_bridge.py"}]
```

### main.js 3 kademeli fallback
```js
let bridgePath = path.join(__dirname, 'python_bridge.py');
if (!fs.existsSync(bridgePath))
  bridgePath = path.join(process.resourcesPath, 'python_bridge.py');
if (!fs.existsSync(bridgePath))
  bridgePath = path.join(__dirname.replace('app.asar', 'app.asar.unpacked'), 'python_bridge.py');
```

## Uygulanan Dosyalar
- `desktop/package.json` — asarUnpack + extraResources
- `desktop/main.js` — 3 kademeli fallback
- `desktop/python_bridge.py` — WEB_UI_PATH fallback
