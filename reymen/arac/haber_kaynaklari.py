# -*- coding: utf-8 -*-
"""
haber_kaynaklari.py — Güncel haber/bilgi kaynak yönlendirici.

ReYMeN'in hangi konuda hangi siteyi kullanacağını belirler.
Web araması yaparken bu kaynakları öncelikli kullan.

Strateji: Reuters/AP ile başla (ham bilgi), Ground News ile karşılaştır (bias),
Foreign Affairs ile haftalık perspektif al, bölgesel kaynaklarla derinleş.

KULLANIM:
    from reymen.arac.haber_kaynaklari import kaynak_sec, KAYNAK_OZETI

    kaynak = kaynak_sec("ukrayna savaşı analiz")
    # → {"birincil": "https://www.reuters.com", ...}

    ozet = KAYNAK_OZETI  # sistem prompt'una eklemek için
"""

# ── Kategori → Kaynak haritası ──────────────────────────────────────────────
# Tetikleyici = sorguda bu kelime varsa bu kategori seçilir
# Birincil = ilk denenir, yedekler = sırayla denenir

KAYNAK_HARITASI = {
    "altin_finans": {
        "tetikleyiciler": [
            "altın", "altin", "ons", "gram", "çeyrek", "ceyrek",
            "yarım", "yarim", "cumhuriyet", "ziynet", "has altın",
            "döviz", "doviz", "dolar", "euro", "kur", "kuru",
            "borsa", "bist",
            "gümüş", "gumus", "platinum", "paladyum",
        ],
        "birincil": "https://www.haremaltin.com",
        "yedek": "https://tr.investing.com",
        "aciklama": "Canlı altın/döviz fiyatları",
    },
    "kripto": {
        "tetikleyiciler": [
            "bitcoin", "kripto", "kripto para", "kriptopara",
            "coin", "ethereum", "eth", "bnb", "solana",
            "blockchain", "blokzincir", "defi", "nft",
            "coindesk", "cointelegraph",
            "kripto borsa", "kripto para haber",
            "btc", "altcoin", "madenci", "mining",
        ],
        "birincil": "https://www.coindesk.com",
        "yedekler": [
            "https://cointelegraph.com",
            "https://decrypt.co",
            "https://bitcoinmagazine.com",
        ],
        "finans_icinde": [
            "https://www.bloomberg.com/crypto",
            "https://www.investing.com/crypto",
            "https://tr.investing.com/crypto",
        ],
        "aciklama": "Kripto para haberleri (CoinDesk + CoinTelegraph + Decrypt)",
    },
    "spor": {
        "tetikleyiciler": [
            "spor", "maç", "mac", "skor",
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
            "oylama", "kanun", "yasa", "kararname",
            "ankara", "genelkurmay", "hükümet", "hukumet",
            "milletvekili", "belediye", "anayasa",
            # Siyasi bağlam
            "siyasi analiz", "seçim anketi", "anket sonucu",
            "muhalefet lideri", "iktidar partisi",
        ],
        "birincil": "https://www.reuters.com/world",
        "yedekler": [
            "https://apnews.com/hub/politics",
            "https://www.bbc.com/news/world",
            "https://www.bbc.com/turkce",
            "https://www.dw.com/tr",
            "https://tr.euronews.com",
        ],
        "aciklama": "Siyaset haberleri (Reuters + AP + BBC + Ground News)",
        "bias_karsilastir": "https://ground.news",
    },
    "analiz_siyaset": {
        "tetikleyiciler": [
            "analiz", "jeopolitik", "jeopolitika",
            "strateji", "stratejik", "küresel politika",
            "dış politika analiz", "uluslararası ilişkiler",
            "foreign affairs", "foreign policy", "economist",
            "derin analiz", "büyük resim", "haftalık değerlendirme",
            "savaş analizi", "kriz analizi",
        ],
        "birincil": "https://www.foreignaffairs.com",
        "yedekler": [
            "https://foreignpolicy.com",
            "https://www.economist.com",
        ],
        "aciklama": "Derin siyasi analiz (Foreign Affairs + FP + Economist)",
    },
    "bolgesel_haber": {
        "tetikleyiciler": [
            "orta doğu", "ortadogu", "middle east",
            "balkan", "balkanlar", "doğu avrupa",
            "afrika", "kuzey afrika",
            "asya pasifik", "güney asya",
            "latin amerika", "orta asya",
            "kafkasya", "körfez",
        ],
        "birincil": "https://www.middleeasteye.net",
        "yedekler": [
            "https://balkaninsight.com",
            "https://www.theafricareport.com",
        ],
        "aciklama": "Bölgesel haberler (Middle East Eye + Balkan Insight + Africa Report)",
    },
    "ekonomi": {
        "tetikleyiciler": [
            "ekonomi", "enflasyon", "işsizlik", "issizlik",
            "büyüme", "buyume", "gsyh", "gsyih",
            "merkez bankası", "mb", "ticaret", "faiz",
            "ithalat", "ihracat", "vergi", "bütçe", "butce",
            "asgari ücret", "asgari ucret", "maaş", "maas",
            "emtia", "petrol",
        ],
        "birincil": "https://www.bloomberg.com/markets",
        "yedekler": [
            "https://www.ft.com",
            "https://www.investing.com",
            "https://tradingeconomics.com",
        ],
        "turkce_kaynaklar": [
            "https://tr.investing.com",
            "https://www.bloomberght.com",
            "https://www.ekonomim.com",
        ],
        "aciklama": "Ekonomi ve finans haberleri (Bloomberg + FT + Investing + TradingEcon)",
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
    "teknoloji_genel": {
        "tetikleyiciler": [
            "teknoloji", "startup", "girişim", "donanım", "donanim",
            "yazılım", "yazilim", "uygulama", "mobil", "ios", "android",
            "bilgisayar", "laptop", "telefon", "ekran", "işlemci",
            "sosyal medya", "instagram", "twitter", "tiktok",
            "webtekno", "chip online",
            "iphone", "ipad", "macbook", "apple", "samsung", "xiaomi",
        ],
        "birincil": "https://www.theverge.com",
        "yedekler": [
            "https://arstechnica.com",
            "https://techcrunch.com",
            "https://www.wired.com",
        ],
        "aciklama": "Genel teknoloji haberleri (The Verge + Ars + TechCrunch + Wired)",
    },
    "yapay_zeka": {
        "tetikleyiciler": [
            "yapay zeka", "yapay-zeka", "ai", "artificial intelligence",
            "derin öğrenme", "makine öğrenmesi",
            "chatgpt", "gpt", "claude", "gemini", "copilot",
            "llm", "dil modeli", "büyük dil modeli",
            "yapay-zeka haber", "yapay zeka gelişme",
            "openai", "anthropic", "deepseek", "meta ai",
            "yapay zeka son", "yapay zeka güncel",
            "mit technology review",
            "import ai", "hugging face",
        ],
        "birincil": "https://www.technologyreview.com",
        "yedekler": [
            "https://huggingface.co/blog",
            "https://arstechnica.com/ai",
        ],
        "aciklama": "Yapay zeka haberleri (MIT Tech Review + Hugging Face)",
        "ek_kaynaklar": {
            "bulten": "Import AI (Jack Clark) — haftalık AI sektör bülteni",
            "turkce": "Şifre Çözücü (Barış Erkol) — AI ve teknoloji bülteni",
        },
    },
    "siber_guvenlik": {
        "tetikleyiciler": [
            "siber", "güvenlik", "guvenlik",
            "saldırı", "saldiri", "virüs", "virus", "zararlı",
            "güvenlik açığı", "guvenlik acigi", "zero day",
            "veri sızıntısı", "veri ihlali",
            "firewall", "antivirüs", "şifreleme", "sifreleme",
            "exploit", "botnet", "ddos", "malware",
            "ransomware", "fidye", "phishing", "oltalama",
        ],
        "birincil": "https://krebsonsecurity.com",
        "yedekler": [
            "https://www.darkreading.com",
        ],
        "aciklama": "Siber güvenlik haberleri (Krebs + Dark Reading)",
    },
    "teknoloji_haber": {
        "tetikleyiciler": [
            "teknoloji haber", "teknoloji gündem",
            "big tech", "google", "apple", "microsoft", "meta",
            "amazon", "nvidia", "intel", "samsung",
            "hacker news", "techmeme",
            "bloomberg teknoloji",
            "hacker",
        ],
        "birincil": "https://news.ycombinator.com",
        "yedekler": [
            "https://techmeme.com",
            "https://www.bloomberg.com/technology",
            "https://www.theinformation.com",
        ],
        "aciklama": "Teknoloji gündemi (Hacker News + Techmeme + Bloomberg Tech)",
    },
    "saglik": {
        "tetikleyiciler": [
            "sağlık", "saglik", "hastalık", "hastalik",
            "ilaç", "ilac", "aşı", "asi", "tedavi",
            "virüs", "virus", "salgın", "salgin",
            "korona", "covid", "obezite", "diyabet",
            "kanser", "kalp", "beyin", "psikoloji",
            "pandemi", "biyoteknoloji", "gen",
            "elektronik sigara", "vaping",
            "biyolojik yaşlanma", "yaşlanma",
        ],
        "birincil": "https://www.statnews.com",
        "yedekler": [
            "https://www.who.int/news-room",
            "https://www.nejm.org",
            "https://www.thelancet.com",
        ],
        "turkce_kaynaklar": [
            "https://www.gazeteoksijen.com/saglik",
            "https://www.medimagazin.com.tr",
            "https://www.aa.com.tr/tr/saglik",
        ],
        "aciklama": "Sağlık haberleri (Stat News + WHO + NEJM + Lancet + Oksijen)",
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

# ── Öncelik sırası ───────────────────────────────────────────────────────────
KATEGORI_SIRASI = [
    "analiz_siyaset", "bolgesel_haber",
    "kripto", "ekonomi", "altin_finans", "spor", "dunya", "siyaset",
    "saglik", "siber_guvenlik",
    "yapay_zeka", "teknoloji_genel", "teknoloji_haber",
    "bilim_teknoloji", "kultur_sanat", "genel_haber",
]

# ── Sistem prompt özeti (LLM'e verilecek) ────────────────────────────────────
KAYNAK_OZETI = """GÜNCEL BİLGİ KAYNAKLARI:
- Altın/Döviz → haremaltin.com
- Kripto → coindesk.com / cointelegraph.com / decrypt.co
- Spor → ntvspor.net
- Dünya Haberleri → reuters.com / apnews.com / bbc.com/news / aljazeera.com
- Siyaset (Türkçe) → bbc.com/turkce / dw.com/tr / tr.euronews.com
- Derin Analiz → foreignaffairs.com / foreignpolicy.com / economist.com
- Bölgesel → middleeasteye.net / balkaninsight.com / theafricareport.com
- Ekonomi → bloomberght.com
- Genel Teknoloji → theverge.com / arstechnica.com / techcrunch.com / wired.com
- Yapay Zeka → technologyreview.com / huggingface.co/blog
- Siber Güvenlik → krebsonsecurity.com / darkreading.com
- Teknoloji Gündemi → news.ycombinator.com / techmeme.com
- Sağlık → statnews.com / who.int / nejm.org / thelancet.com
- Sağlık (Türkçe) → gazeteoksijen.com/saglik / medimagazin.com.tr / aa.com.tr
- Bilim → nature.com / science.org
- Genel Haber → ntv.com.tr
Bias karşılaştırma için: ground.news
Güncel bilgi sorularında WEB_ARA aracını kullan."""


def kaynak_sec(sorgu: str) -> dict:
    """
    Sorguya en uygun kaynağı seçer.

    Args:
        sorgu: Kullanıcı sorusu

    Returns:
        {"kategori": "...", "birincil": "...", "yedekler": [...],
         "aciklama": "...", "bias_karsilastir": "..."}
        veya boş dict (eşleşme yoksa)
    """
    if not sorgu:
        return {}

    sorgu_lower = sorgu.lower()

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
                sonuc = {
                    "kategori": kategori_adi,
                    "birincil": kategori["birincil"],
                    "yedekler": yedekler,
                    "aciklama": kategori["aciklama"],
                }
                bias = kategori.get("bias_karsilastir")
                if bias:
                    sonuc["bias_karsilastir"] = bias
                turkce = kategori.get("turkce_kaynaklar")
                if turkce:
                    sonuc["turkce_kaynaklar"] = turkce
                finans = kategori.get("finans_icinde")
                if finans:
                    sonuc["finans_icinde"] = finans
                return sonuc

    return {}


def kaynakli_web_ara(sorgu: str, limit: int = 5) -> str:
    """
    Kaynak öncelikli web araması — 5 aşamalı strateji.

    SIRA:
    1. BİRİNCİL — direkt içerik çek (en hızlı, en güncel)
    2. YEDEKLER — sırayla dene (birincil aynı kategorideki diğer kaynaklar)
    3. TÜRKÇE — varsa Türkçe kaynakları dene
    4. FİNANS ALT — kripto gibi alt sayfalar (bloomberg/investing crypto)
    5. HAYALET — direkt erişilemeyen kaynaklar için site: ile DuckDuckGo
    6. GENEL — son çare DuckDuckGo

    Args:
        sorgu: Arama sorgusu
        limit: Max sonuç sayısı

    Returns:
        Web arama sonucu metni
    """
    from reymen.arac.araclar_web import web_ara, web_icerik_al

    kaynak = kaynak_sec(sorgu)

    if not (kaynak and kaynak.get("birincil")):
        return web_ara(sorgu, adet=limit)

    # ADIM 1-4: Doğrudan içerik çekme (hızlı yol)
    _tum_urls = []

    # 1. Birincil
    _tum_urls.append(("birincil", kaynak["birincil"]))

    # 2. Yedekler
    for yedek in kaynak.get("yedekler", []):
        _tum_urls.append(("yedek", yedek))

    # 3. Türkçe
    for tr in kaynak.get("turkce_kaynaklar", []):
        _tum_urls.append(("türkçe", tr))

    # 4. Finans alt
    for fi in kaynak.get("finans_icinde", []):
        _tum_urls.append(("finans", fi))

    for etiket, url in _tum_urls:
        try:
            icerik = web_icerik_al(url, max_karakter=4000)
            if icerik and "Icerik alinamadi" not in icerik:
                return f"[{kaynak['aciklama']} — {etiket} ({url})]\n\n{icerik}"
        except Exception:
            continue

    # ADIM 5: Hayalet arama — site: ile DuckDuckGo
    # (paywall/bot engeli olan kaynaklar için)
    _kaynak_siteler = [
        kaynak["birincil"].replace("https://www.", "").replace("https://", "").rstrip("/").split("/")[0]
    ]
    for yedek in kaynak.get("yedekler", []):
        site = yedek.replace("https://www.", "").replace("https://", "").rstrip("/").split("/")[0]
        if site not in _kaynak_siteler:
            _kaynak_siteler.append(site)

    for site in _kaynak_siteler[:3]:  # en fazla 3 site
        try:
            hayalet_sonuc = web_ara(f"site:{site} {sorgu}", adet=3)
            if hayalet_sonuc and len(hayalet_sonuc) > 50:
                return f"[{kaynak['aciklama']} — site:{site} araması]\n\n{hayalet_sonuc}"
        except Exception:
            continue

    # ADIM 6: Genel DuckDuckGo (son çare)
    return web_ara(sorgu, adet=limit)


def bias_karsilastir(sorgu: str) -> dict:
    """
    Aynı haberi farklı siyasi perspektiflerden karşılaştırmak için
    Ground News linki üretir.

    Args:
        sorgu: Haber sorgusu

    Returns:
        {"ground_news": "https://ground.news/search/...",
         "kategori": "...", "birincil": "..."}
    """
    from urllib.parse import quote

    kaynak = kaynak_sec(sorgu)
    ground_url = f"https://ground.news/search/{quote(sorgu)}"

    sonuc = {"ground_news": ground_url}
    if kaynak:
        sonuc["kategori"] = kaynak["kategori"]
        sonuc["birincil"] = kaynak["birincil"]
        bias = kaynak.get("bias_karsilastir")
        if bias:
            sonuc["bias_karsilastir"] = bias

    return sonuc


def kaynak_tavsiyesi(sorgu: str) -> str:
    """Sorgu için önerilen kaynağı döndürür (tek satır)."""
    kaynak = kaynak_sec(sorgu)
    if kaynak:
        base = f"🔍 {kaynak['aciklama']}: {kaynak['birincil']}"
        bias = kaynak.get("bias_karsilastir")
        if bias:
            base += f" | Bias karşılaştırma: {bias}"
        return base
    return "🔍 Genel web araması"


if __name__ == "__main__":
    test_sorgular = [
        "gram altın ne kadar",
        "galatasaray maçı",
        "ukrayna savaşı analiz",
        "son dakika siyaset haberi",
        "orta doğu haberleri",
        "enflasyon oranı",
        "dünya gündemi",
        "yapay zeka son gelişmeler",
        "foreign affairs analiz",
        "balkan haberleri",
        "bugün haberler",
    ]
    print(f"{'SORGU':40s} {'KATEGORI':25s} KAYNAK")
    print("-" * 100)
    for s in test_sorgular:
        k = kaynak_sec(s)
        if k:
            yedek_sayisi = len(k.get("yedekler", []))
            bias = " [bias karşılaştırma]" if k.get("bias_karsilastir") else ""
            print(f"{s:40s} {k['kategori']:25s} {k['birincil']}{bias}")
            if yedek_sayisi > 0:
                print(f"{'':40s} {'':25s} 🔄 {yedek_sayisi} yedek")
        else:
            print(f"{s:40s} {'(eslesme yok)':25s}")
