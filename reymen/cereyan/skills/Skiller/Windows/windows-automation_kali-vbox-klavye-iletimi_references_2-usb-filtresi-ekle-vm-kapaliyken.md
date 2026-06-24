# 2. USB filtresi ekle (VM KAPALIYKEN)
"C:\Program Files/Oracle/VirtualBox/VBoxManage.exe" usbfilter add 0 \
  --target "kal" \
  --name "Ralink WiFi" \
  --vendorid 148f \
  --productid 2573