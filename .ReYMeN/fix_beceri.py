import json

with open("beceri_kutuphanesi.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Eski hatali beceriyi sil
eski_key = "bilgisayar_da_ekran_foto\u011fraf\u0131_cek_at_bana"
if eski_key in data:
    del data[eski_key]
    print(f"Silindi: {eski_key}")

# Dogru beceriyi ekle
data["ekran_fotografi_cek_gonder"] = {
    "ad": "Ekran fotografi cek ve gonder",
    "aciklama": "Bilgisayar ekraninin fotografini cekip kullaniciya Telegram'dan gonderir. Once EKRAN_FOTOGRAF_CEK() ile cek, sonra TELEGRAM_RESIM_GONDER(\"ekran.png\") ile gonder.",
    "tetikleyiciler": ["ekran", "fotograf", "foto", "screen", "screenshot", "goruntu", "cek"],
    "adimlar": [
        "EKRAN_FOTOGRAF_CEK",
        "TELEGRAM_RESIM_GONDER"
    ],
    "basari_kriteri": "Fotograf cekilip gonderildi",
    "kullanim_sayisi": 1,
    "basari_orani": 1.0,
    "olusturma": "2026-06-18",
    "son_basari": "2026-06-18"
}
print("Eklendi: ekran_fotografi_cek_gonder")

with open("beceri_kutuphanesi.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print("Kaydedildi")
