# sonra yeni zip yarat, imzalı APK'yı bu binary manifest ile replace et
```

Kurallar:
- Yeni isim **kesinlikle aynı uzunlukta** olmalı
- Google paket isimlerini (`com.google.*`, `com.android.*`) kullanma — Samsung bloklar
- `manifest.count(orig_utf16)` ile kaç yerde geçtiğini kontrol et

---