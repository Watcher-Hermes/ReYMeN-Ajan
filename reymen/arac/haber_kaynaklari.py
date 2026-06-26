# -*- coding: utf-8 -*-
"""
haber_kaynaklari.py — Güncel haber/bilgi kaynak yönlendirici.

ReYMeN'in hangi konuda hangi siteyi kullanacağını belirler.
Web araması yaparken bu kaynakları öncelikli kullan.

KULLANIM:
    from reymen.arac.haber_kaynaklari import kaynak_sec, KAYNAK_OZETI

    # Sorguya uygun kaynağı bul
    kaynak = kaynak_sec("gram altın ne kadar")
    # → "https://www.haremaltin.com"

    # Sistem prompt'una eklemek için özet
    ozet = KAYNAK_OZETI  # tüm kaynakların listesi
"""

# ── Kategori → Kaynak haritası ──────────────────────────────────────────────
# Her kategori için: (anahtar_kelimeler, öncelikli_siteler, açıklama)

KAYNAK_HARITASI = {
    "altin_finans": {
        "tetikleyiciler": [
            "altın", "altin", "ons", "gram", "çeyrek", "ceyrek",
            "yarım", "yarim", "cumhuriyet", "ziynet", "has altın",
            "döviz", "doviz", "dolar", "euro", "kur", "kuru",
            "borsa", "bist",
            "bitcoin", "kripto", "coin",
            "gümüş", "gumus", "platinum", "paladyum",
        ],
        "birincil": "https://www.haremaltin.com",
        "yedek": "https://tr.investing.com",
        "aciklama": "Canlı altın/döviz fiyatları",
    },
    "spor": {
        "tetikleyiciler": [
            "spor", "maç", "mac", "skor", "sonuç", "sonuc",
            "futbol", "basketbol", "voleybol", "tenis",
            "lig", "şampiyon", "sampiyon", "transfer",
            "galatasaray", "fenerbahçe", "beşiktaş", "trabzon",
            "milli", "takım", "takim", "puan", "durumu",
            "NBA", "nba", "uefa", "süper lig", "super lig",
        ],
        "birincil": "https://www.ntvspor.net",
        "yedek": "https://www.beinsports.com.tr",
        "aciklama": "Spor haberleri, maç sonuçları",
    },
    "siyaset": {
        "tetikleyiciler": [
            "siyaset", "politika", "seçim", "secim",
            "cumhurbaşkanı", "cumhurbaskani", "başbakan", "bakan",
            "meclis", "parti", "muhalefet", "iktidar",
            "oylama", "kanun", "yasa", "karar",
            "ankara", "genelkurmay",
        ],
        "birincil": "https://www.bbc.com/turkce",
        "yedekler": [
            "https://www.dw.com/tr",
            "https://tr.euronews.com",
        ],
        "aciklama": "Siyaset haberleri (BBC Türkçe + DW + Euronews)",
    },
    "ekonomi": {
        "tetikleyiciler": [
            "ekonomi", "enflasyon", "işsizlik", "issizlik",
            "büyüme", "buyume", "gsyh", "gsyih",
            "merkez bankası", "mb", "ticaret", "faiz",
            "ithalat", "ihracat", "vergi", "bütçe", "butce",
            "asgari ücret", "asgari ucret", "maaş", "maas",
            "emtia", "petrol", "altın fiyat",
        ],
        "birincil": "https://www.bloomberght.com",
        "yedek": "https://www.ekonomim.com",
        "aciklama": "Ekonomi ve finans haberleri",
    },
    "dunya": {
        "tetikleyiciler": [
            "dünya", "dunya", "uluslararası", "uluslararasi",
            "küresel", "kuresel", "global", "dış politika",
            "savaş", "savas", "barış", "baris",
            "abd", "amerika", "rusya", "çin", "cin",
            "avrupa", "almanya", "fransa", "ingiltere",
            "ortadoğu", "ortadogu", "filistin", "israil",
            "ukrayna", "bm", "nato", "birleşmiş milletler",
        ],
        "birincil": "https://www.reuters.com",
        "yedekler": [
            "https://www.bbc.com/news",
            "https://www.aljazeera.com",
            "https://www.bbc.com/turkce",
            "https://www.dw.com/tr",
            "https://tr.euronews.com",
        ],
        "aciklama": "Dünya haberleri (Reuters + BBC + Al Jazeera)",
    },
    "teknoloji_yapay_zeka": {
        "tetikleyiciler": [
            "yapay zeka", "yapay-zeka", "ai", "artificial intelligence",
            "derin öğrenme", "makine öğrenmesi",
            "chatgpt", "gpt", "claude", "gemini", "copilot",
            "llm", "dil modeli", "büyük dil modeli",
            "teknoloji", "yazılım", "yazilim", "uygulama",
            "siber", "güvenlik", "guvenlik", "hack",
            "robot", "otomasyon", "donanım", "donanim",
            "yapay-zeka haber", "yapay zeka gelişme",
            "openai", "anthropic", "deepseek", "meta ai",
            "yapay zeka son", "yapay zeka güncel",
        ],
        "birincil": "https://techcrunch.com",
        "yedek": "https://www.theverge.com/ai-artificial-intelligence",
        "aciklama": "Teknoloji ve yapay zeka haberleri",
    },
    "saglik": {
        "tetikleyiciler": [
            "sağlık", "saglik", "hastalık", "hastalik",
            "ilaç", "ilac", "aşı", "asi", "tedavi",
            "virüs", "virus", "salgın", "salgin",
            "korona", "covid", "obezite", "diyabet",
            "kanser", "kalp", "beyin", "psikoloji",
        ],
        "birincil": "https://www.medicalnewstoday.com",
        "yedek": "https://www.webmd.com",
        "aciklama": "Sağlık haberleri",
    },
    "bilim_teknoloji": {
        "tetikleyiciler": [
            "bilim", "science", "uzay", "nasa", "spacex",
            "keşif", "kesif", "araştırma", "arastirma",
            "fizik", "kimya", "biyoloji", "genetik",
            "iklim", "çevre", "cevre", "doğa", "doga",
            "enerji", "nükleer", "nukleer", "yenilenebilir",
        ],
        "birincil": "https://www.nature.com",
        "yedek": "https://www.science.org",
        "aciklama": "Bilim ve araştırma haberleri",
    },
    "kultur_sanat": {
        "tetikleyiciler": [
            "kültür", "kultur", "sanat", "sinema", "film",
            "dizi", "tiyatro", "konser", "müzik", "muzik",
            "kitap", "edebiyat", "şiir", "siir", "ressam",
            "sergi", "heykel", "fotoğraf", "fotograf",
            "tarih", "arkeoloji",
        ],
        "birincil": "https://www.sozcu.com.tr/kultur-sanat",
        "yedek": "https://www.bbc.com/culture",
        "aciklama": "Kültür ve sanat haberleri",
    },
    "genel_haber": {
        "tetikleyiciler": [
            "haber", "haberler", "gündem", "gundem",
            "son dakika", "flaş", "flash", "breaking",
            "manşet", "manset", "gazete", "medya",
            "bugün ne oldu", "bugun ne oldu",
        ],
        "birincil": "https://www.bbc.com/turkce",
        "yedekler": [
            "https://www.ntv.com.tr",
            "https://tr.euronews.com",
        ],
        "aciklama": "Genel güncel haberler",
    },
}

# ── Öncelik sırası (en sık kullanılandan en seyrek) ─────────────────────────
KATEGORI_SIRASI = [
    "ekonomi", "altin_finans", "spor", "dunya", "siyaset",
    "teknoloji_yapay_zeka", "bilim_teknoloji", "saglik",
    "kultur_sanat", "genel_haber",
]

# ── Sistem prompt özeti (LLM'e verilecek) ────────────────────────────────────
KAYNAK_OZETI = """GÜNCEL BİLGİ KAYNAKLARI:
- Altın/Döviz → haremaltin.com
- Spor → ntvspor.net
- Dünya Haberleri → reuters.com / bbc.com/news / aljazeera.com
- Türkçe Dünya/Siyaset → bbc.com/turkce / dw.com/tr / tr.euronews.com
- Ekonomi → bloomberght.com
- Yapay Zeka/Teknoloji → techcrunch.com / theverge.com
- Genel Haber → bbc.com/turkce / ntv.com.tr
Güncel bilgi sorularında WEB_ARA aracını kullan."""


def kaynak_sec(sorgu: str) -> dict:
    """
    Sorguya en uygun kaynağı seçer.

    Args:
        sorgu: Kullanıcı sorusu

    Returns:
        {"kategori": "...", "birincil": "...", "yedek": "...", "aciklama": "..."}
        veya boş dict (eşleşme yoksa)
    """
    if not sorgu:
        return {}

    sorgu_lower = sorgu.lower()

    # En spesifikten en genele doğru tara
    for kategori_adi in KATEGORI_SIRASI:
        kategori = KAYNAK_HARITASI.get(kategori_adi)
        if not kategori:
            continue
        for kelime in kategori["tetikleyiciler"]:
            if kelime in sorgu_lower:
                # Yedekleri normalize et
                yedekler = kategori.get("yedekler") or (
                    [kategori["yedek"]] if kategori.get("yedek") else []
                )
                return {
                    "kategori": kategori_adi,
                    "birincil": kategori["birincil"],
                    "yedekler": yedekler,
                    "aciklama": kategori["aciklama"],
                }

    return {}


def kaynakli_web_ara(sorgu: str, limit: int = 5) -> str:
    """
    Kaynak öncelikli web araması yapar.

    1. Sorguya uygun kaynak bul
    2. Varsa o kaynağı doğrudan web_icerik_al ile oku
    3. Birincil başarısızsa sırayla yedekleri dene
    4. Hiçbiri çalışmazsa genel web_ara kullan

    Args:
        sorgu: Arama sorgusu
        limit: Max sonuç sayısı

    Returns:
        Web arama sonucu metni
    """
    from reymen.arac.araclar_web import web_ara, web_icerik_al

    kaynak = kaynak_sec(sorgu)

    if kaynak and kaynak.get("birincil"):
        # Önce birincil kaynağı dene
        birincil_url = kaynak["birincil"]
        try:
            icerik = web_icerik_al(birincil_url, max_karakter=4000)
            if icerik and "Icerik alinamadi" not in icerik:
                return f"[{kaynak['aciklama']} ({birincil_url})]\n\n{icerik}"
        except Exception:
            pass

        # Birincil başarısız → sırayla yedekleri dene
        for yedek_url in kaynak.get("yedekler", []):
            try:
                icerik = web_icerik_al(yedek_url, max_karakter=4000)
                if icerik and "Icerik alinamadi" not in icerik:
                    return f"[{kaynak['aciklama']} → yedek ({yedek_url})]\n\n{icerik}"
            except Exception:
                continue

        # Tüm kaynaklar başarısız → genel arama
        try:
            genel_sonuc = web_ara(f"{sorgu} {kaynak['aciklama']}", adet=limit)
            if genel_sonuc:
                return genel_sonuc
        except Exception:
            pass

    # Hiçbir kaynak eşleşmedi → genel web araması
    return web_ara(sorgu, adet=limit)


def kaynak_tavsiyesi(sorgu: str) -> str:
    """Sorgu için önerilen kaynağı döndürür (tek satır)."""
    kaynak = kaynak_sec(sorgu)
    if kaynak:
        return f"🔍 {kaynak['aciklama']}: {kaynak['birincil']}"
    return "🔍 Genel web araması"


if __name__ == "__main__":
    # Test
    test_sorgular = [
        "gram altın ne kadar",
        "bugünkü maç sonuçları",
        "son dakika siyaset haberi",
        "enflasyon oranı ne kadar",
        "dünya gündemi",
        "yapay zeka son gelişmeler",
        "bugün haberler",
    ]
    for s in test_sorgular:
        k = kaynak_sec(s)
        if k:
            print(f"{s:40s} → {k['aciklama']}: {k['birincil']}")
        else:
            print(f"{s:40s} → Genel web araması")
