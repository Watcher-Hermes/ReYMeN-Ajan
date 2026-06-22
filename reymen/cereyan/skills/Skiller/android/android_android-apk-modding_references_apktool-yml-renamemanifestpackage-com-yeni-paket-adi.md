# apktool.yml → renameManifestPackage: com.yeni.paket.adi
```

**3) Smali class referanslarını değiştir (EN ÖNEMLİ)**
Sadece manifest rename YETMEZ — DEX içinde `Lcom/eski/paket/Class;` referansları eski kalır:
```bash