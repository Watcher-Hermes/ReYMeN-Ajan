# İmza şemalarını kontrol et
apksigner verify --verbose "orijinal.apk" 2>&1 | grep -E "Verified using|WARNING:"
```

#### 3. Decompile Et
```bash
java -jar apktool.jar d -f orijinal.apk -o decompile_out/