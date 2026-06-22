# APK yapısını kontrol et
aapt2 dump badging "orijinal.apk" | grep -E "package:|minSdkVersion:|targetSdkVersion:|native-code:|split:"