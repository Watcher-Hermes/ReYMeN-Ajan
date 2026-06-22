## Komutlar

### Tek satir yazma
```bash
"C:\Program Files/Oracle/VirtualBox/VBoxManage.exe" controlvm "kal" keyboardputstring "komut buraya"
```

### Enter tusu gonderme
```bash
"C:\Program Files/Oracle/VirtualBox/VBoxManage.exe" controlvm "kal" keyboardputstring $'\n'
```

### Zincirleme (birden fazla satir)
```bash
"VBoxManage.exe" controlvm "kal" keyboardputstring "komut1" && sleep 1 && "VBoxManage.exe" controlvm "kal" keyboardputstring $'\n'
```

### Ekrani temizleme
```bash
"VBoxManage.exe" controlvm "kal" keyboardputstring "clear" && "VBoxManage.exe" controlvm "kal" keyboardputstring $'\n'
```