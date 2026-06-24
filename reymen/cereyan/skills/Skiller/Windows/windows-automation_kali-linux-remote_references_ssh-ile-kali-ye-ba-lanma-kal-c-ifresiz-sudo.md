## SSH ile Kali'ye Bağlanma (Kalıcı şifresiz sudo)
Kali'de şifresiz sudo ayarı yapıldıktan sonra SSH komutlarında `sudo -S` bypass'ına gerek kalmaz:
```python
cmd[-1] = "sudo arp-scan -l 2>&1"
```