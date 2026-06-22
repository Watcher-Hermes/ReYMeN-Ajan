# Tekrar imzala (birleştirme imzayı bozar)
apksigner sign --ks my.keystore --ks-key-alias myalias monolithic.apk
```

Veya manifest'ten split referanslarını temizle, `apktool b` ile yeniden build et.

#### 8. Doğrula
```bash