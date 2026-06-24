# Smali'de lisans/premium ile ilgili tüm referansları tar
grep -r -i "premium\|license\|pro\|unlock\|subscription\|purchase" _audit/smali/ | grep -v ".line" | head -30
```

**SORULAR:**
```
- Premium kararı client'ta mı?    → KIRILGAN
- Sunucu doğrulaması var mı?      → Token replay'e açık mı?
- SharedPreferences mı?           → Tek satır
- root tespiti var mı?            → Atlanabilir mi?
- Integrity API kullanılıyor mu?  → Verdict client'ta mı doğrulanıyor?
```

### 1c — String ve sabitler

```bash