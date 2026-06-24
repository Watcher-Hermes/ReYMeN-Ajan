## SSH Bağlantı Sorunu — Tam Tanı ve Kurtarma

### Medya Kilidi Sorunu — Recovery VM Çakışması

Kali VM başlatılırken `VBOX_E_INVALID_OBJECT_STATE` hatası alınırsa, medya başka bir VM tarafından kilitlenmiştir.

**Belirtiler:**
```bash
VBoxManage startvm "kal" --type headless