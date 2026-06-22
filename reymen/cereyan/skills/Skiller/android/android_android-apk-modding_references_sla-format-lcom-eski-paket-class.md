# Slaş format (Lcom/eski/paket/Class;)
grep -rl "com/eski/paket/yolu" smali/ smali_classes2/ | \
  xargs sed -i 's|com/eski/paket/yolu|com/yeni/paket/yolu|g'