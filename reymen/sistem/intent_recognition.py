# -*- coding: utf-8 -*-
"""
intent_recognition.py — Niyet (intent) tanıma motoru.
4 katmanlı approach:
  1. Pattern Matching (regex kalıpları)
  2. Synonym Mapping (eş anlamlı kelimeler)
  3. Context Window (önceki konuşmayı hatırla)
  4. Embedding Search (anlamsal benzerlik)
"""

from __future__ import annotations
import re
import math
from collections import deque
from dataclasses import dataclass, field
from typing import Optional, Dict, List, Tuple


@dataclass
class Intent:
    """Tanınan niyet."""
    tip: str
    guven: float
    hedef: Optional[str] = None
    alt_tip: Optional[str] = None
    context: dict = field(default_factory=dict)


# ══════════════════════════════════════════════════════════════════════════
# KATMAN 1: Pattern Matching
# ══════════════════════════════════════════════════════════════════════════

KALIPLAR = {
    "hata_analizi": [
        (r"(hata|error|bug|crash|bozul|çök|patla|kırıl)", 1.0, "hata_bildirimi"),
        (r"(neden|sebep|niye|why|nasıl oldu)", 0.9, "kok_neden"),
        (r"(düzelt|fix|solve|çöz|onar|tamir)", 0.85, "cozum_isteme"),
        (r"(traceback|NameError|SyntaxError|ImportError)", 1.0, "teknik_hata"),
        (r"(çalışmıyor|calışmıyor|bozuk|kırık|working)", 0.8, "calismama"),
    ],
    "bilgi_isteme": [
        (r"(nedir|ne|what|tanım|açıkla|explain)", 0.85, "tanim"),
        (r"(kaç|ne kadar|how many|how much|miktar)", 0.8, "miktar"),
        (r"(hangi|which|nerede|where)", 0.8, "konum"),
        (r"(fark|farklı|difference|vs|versus|karşılaştır)", 0.85, "karsilastirma"),
        (r"(listele|göster|show|list|yazdır)", 0.75, "listeleme"),
    ],
    "islem_yapma": [
        (r"(yap|çalıştır|run|execute|başlat|start|git)", 0.9, "calistirma"),
        (r"(kur|install|yükle|setup)", 0.85, "kurulum"),
        (r"(sil|delete|kaldır|remove)", 0.8, "silme"),
        (r"(güncelle|update|yenile|refresh)", 0.8, "güncelleme"),
        (r"(kaydet|save|git push|commit|yükle)", 0.85, "kaydetme"),
        (r"(test|doğrula|verify|kontrol et)", 0.8, "test"),
    ],
    "guvenlik": [
        (r"(güvenli|secure|safe|koruma|protect)", 0.85, "guvenlik_kontrol"),
        (r"(tarama|scan|sweep|audit)", 0.8, "tarama"),
        (r"(şifre|password|key|token|secret)", 0.75, "kimlik"),
    ],
    "otomasyon": [
        (r"(otomatik|automatic|self|kendi kendine)", 0.85, "otomatik_islem"),
        (r"(cron|zamanlanmış|scheduled|periyodik)", 0.8, "zamanlanmis"),
        (r"(bot|agent|ajan|otonom)", 0.75, "bot_yonetimi"),
    ],
    "performans": [
        (r"(hız|fast|slow|yavaş|hızlı|performans)", 0.85, "hiz_analiz"),
        (r"(bellek|memory|ram|disk|cpu)", 0.8, "kaynak_kullanimi"),
        (r"(maliyet|cost|ucuz|pahalı|kredi)", 0.85, "maliyet_analiz"),
    ],
    "gui": [
        (r"(aç|open|göster|show|ekran|screen)", 0.7, "ekran_acma"),
        (r"(kapat|close|dur|stop|durdur)", 0.75, "durdurma"),
        (r"(tıklık|click|bas|press|seç|select)", 0.7, "etkilesim"),
    ],
}

# ══════════════════════════════════════════════════════════════════════════
# KATMAN 2: Synonym Mapping
# ══════════════════════════════════════════════════════════════════════════

SYNONYMS = {
    "hata": ["error", "bug", "fault", "issue", "problem", "sorun", "ariza"],
    "düzelt": ["fix", "solve", "repair", "resolve", "patch", "duzelt", "tamir"],
    "çalıştır": ["run", "execute", "start", "launch", "initiate", "baslat"],
    "göster": ["show", "display", "list", "print", "yazdır", "goster"],
    "kaldır": ["remove", "delete", "uninstall", "purge", "kaldir", "sil"],
    "güncelle": ["update", "upgrade", "refresh", "yenile", "guncelle"],
    "kontrol": ["check", "verify", "validate", "audit", "tarama", "bak"],
    "kur": ["install", "setup", "configure", "yapılandır", "kur"],
    "hız": ["speed", "fast", "quick", "performance", "hiz"],
    "bellek": ["memory", "ram", "storage", "disk", "bellek"],
    "maliyet": ["cost", "price", "fee", "credit", "kredi", "ucret"],
    "güvenli": ["secure", "safe", "protected", "guvenli", "emniyetli"],
    "hazırla": ["prepare", "setup", "ready", "hazırla", "hazirla"],
    "bul": ["find", "search", "locate", "ara", "bul"],
    "oku": ["read", "open", "view", "göster", "oku"],
    "yaz": ["write", "create", "edit", "oluştur", "yaz"],
}

# ══════════════════════════════════════════════════════════════════════════
# KATMAN 3: Context Window
# ══════════════════════════════════════════════════════════════════════════

class ContextWindow:
    """Son N konuşmayı hatırla, intent bağımlılıklarını tespit et."""

    def __init__(self, max_boyut: int = 10):
        self.gecmis: deque = deque(maxlen=max_boyut)
        self.son_intent: Optional[Intent] = None
        self.aktif_konu: Optional[str] = None

    def ekle(self, metin: str, intent: Intent):
        """Yeni konuşmayı geçmişe ekle."""
        self.gecmis.append({"metin": metin, "intent": intent})
        self.son_intent = intent

        # Konu takibi: ardışık aynı intent varsa konu sabit kalır
        if len(self.gecmis) >= 2:
            son_2 = [g["intent"].tip for g in list(self.gecmis)[-2:]]
            if son_2[0] == son_2[1]:
                self.aktif_konu = son_2[0]
            else:
                self.aktif_konu = intent.tip

    def referans_var_mi(self, metin: str) -> bool:
        """Metinde önceki konuşmaya referans var mı?"""
        referans_kalıpları = [
            r"(o|bu|şu|the|that|this)\s+(dosya|modül|servis|hata|konu)",
            r"(yukarıdaki|aşağıdaki|önceki|sonraki)",
            r"(aynı|benzer|farklı|karşılaştır)",
            r"(devam|bitir|tamamla|düzelt)",  # Önceki göreve devam
        ]
        for kalip in referans_kalıpları:
            if re.search(kalip, metin.lower()):
                return True
        return False

    def baglam_bilgisi_al(self) -> Optional[str]:
        """Aktif konu hakkında bilgi döndür."""
        if self.aktif_konu and len(self.gecmis) >= 2:
            return f"Önceki konu: {self.aktif_konu}"
        return None


# ══════════════════════════════════════════════════════════════════════════
# KATMAN 4: Embedding benzerlik (basit TF-IDF yaklaşımı)
# ══════════════════════════════════════════════════════════════════════════

class EmbeddingEngine:
    """Basit anlamsal benzerlik motoru — harici kütüphane gerektirmez."""

    # Intent'lere karşılık gelen temsili metinler
    INTENT_VEKORLERI = {
        "hata_analizi": [
            "hata düzeltme sorun giderme crash crash fix bug error",
            "traceback exception NameError TypeError Import hata",
            "çalışmıyor bozuldu kırıldı patladı sorun var",
        ],
        "bilgi_isteme": [
            "nedir ne nasıl nerede hangi bilgi açıklama",
            "kaç tane ne kadar miktar fiyat maliyet",
            "fark karşılaştırma benzerlik karşılaştır",
            "listele göster gösteri dosya",
        ],
        "islem_yapma": [
            "yap çalıştır başlat git execute run start",
            "kur yükle setup install configure",
            "sil kaldır delete remove uninstall",
            "güncelle yenile update upgrade refresh",
            "kaydet commit push save",
            "test et doğrula kontrol verify",
        ],
        "guvenlik": [
            "güvenli koruma emniyet secure safe protect",
            "tarama audit sweep vulnerability",
            "şifre password key token secret credential",
        ],
        "otomasyon": [
            "otomatik self autonomous bot agent",
            "cron scheduled zamanlanmış periyodik",
            "kendi kendineработает automatic",
        ],
        "performans": [
            "hız hızlı yavaş performans speed fast slow",
            "bellek ram disk cpu kaynak",
            "maliyet ucuz pahalı kredi cost cheap expensive",
        ],
        "gui": [
            "aç göster ekran open show screen",
            "kapat durdur close stop",
            "tıkla bas seç click press select",
        ],
    }

    def __init__(self):
        # Her kelimeyi IDF ağırlığıyla temsili vektöre çevir
        self._kelime_setleri: Dict[str, set] = {}
        self._idf: Dict[str, float] = {}
        self._hesapla_idf()

    def _kelime_ayir(self, metin: str) -> List[str]:
        """Metni kelimelere ayır (stopword hariç)."""
        stopword = {"bir", "bu", "o", "ve", "ile", "için", "ne", "mi", "mu",
                    "mı", "mü", "da", "de", "ki", "olan", "gibi", "daha",
                    "the", "a", "an", "is", "are", "was", "in", "on", "at",
                    "to", "for", "of", "with", "by", "it", "this", "that"}
        kelimeler = re.findall(r'\b\w+\b', metin.lower())
        return [k for k in kelimeler if k not in stopword and len(k) > 1]

    def _hesapla_idf(self):
        """IDF hesapla: nadir kelimelere yüksek ağırlık ver."""
        import math
        tum_kelimeler: Dict[str, int] = {}
        dokuman_sayisi = 0

        for intent, metinler in self.INTENT_VEKORLERI.items():
            for metin in metinler:
                dokuman_sayisi += 1
                kelimeler = set(self._kelime_ayir(metin))
                for k in kelimeler:
                    tum_kelimeler[k] = tum_kelimeler.get(k, 0) + 1

        for kelime, sayi in tum_kelimeler.items():
            self._idf[kelime] = math.log(dokuman_sayisi / (1 + sayi))

    def _vektor_olustur(self, metin: str) -> Dict[str, float]:
        """Metinden TF-IDF vektörü oluştur."""
        kelimeler = self._kelime_ayir(metin)
        if not kelimeler:
            return {}

        tf: Dict[str, int] = {}
        for k in kelimeler:
            tf[k] = tf.get(k, 0) + 1

        vektor = {}
        for kelime, sayi in tf.items():
            tf_deger = sayi / len(kelimeler)
            idf_deger = self._idf.get(kelime, 1.0)
            vektor[kelime] = tf_deger * idf_deger
        return vektor

    def _kosinus_benzerlik(self, v1: Dict[str, float], v2: Dict[str, float]) -> float:
        """İki vektör arasındaki kosinüs benzerliği."""
        ortak = set(v1.keys()) & set(v2.keys())
        if not ortak:
            return 0.0

        dot = sum(v1[k] * v2[k] for k in ortak)
        norm1 = math.sqrt(sum(v ** 2 for v in v1.values()))
        norm2 = math.sqrt(sum(v ** 2 for v in v2.values()))

        if norm1 == 0 or norm2 == 0:
            return 0.0
        return dot / (norm1 * norm2)

    def intent_bul(self, metin: str) -> Tuple[str, float]:
        """Metne en yakın intent'i bul."""
        metin_vektor = self._vektor_olustur(metin)
        if not metin_vektor:
            return "bilinmiyor", 0.0

        en_iyi_intent = "bilinmiyor"
        en_iyi_skor = 0.0

        for intent, metinler in self.INTENT_VEKORLERI.items():
            for referans in metinler:
                ref_vektor = self._vektor_olustur(referans)
                skor = self._kosinus_benzerlik(metin_vektor, ref_vektor)
                if skor > en_iyi_skor:
                    en_iyi_skor = skor
                    en_iyi_intent = intent

        return en_iyi_intent, round(min(en_iyi_skor * 2, 1.0), 2)  # 2x scale


# ══════════════════════════════════════════════════════════════════════════
# ANA MOTOR: 4 Katmanlı Intent Recognition
# ══════════════════════════════════════════════════════════════════════════

class IntentRecognizer:
    """4 katmanlı niyet tanıma motoru."""

    def __init__(self):
        # Katman 1: Pattern matching
        self._compiled = {}
        for intent, kalip_listesi in KALIPLAR.items():
            self._compiled[intent] = [
                (re.compile(kalip, re.IGNORECASE), agirlik, alt)
                for kalip, agirlik, alt in kalip_listesi
            ]

        # Katman 3: Context window
        self.context = ContextWindow(max_boyut=10)

        # Katman 4: Embedding
        self.embedding = EmbeddingEngine()

        # Nesne tespiti desenleri
        self._obje_desenleri = {
            "dosya": [r"\.py$", r"\.js$", r"\.ts$", r"\.json$", r"\.yaml$", r"\.md$"],
            "modul": [r"modül|module|dosya|file"],
            "servis": [r"servis|service|gateway|bot|cron"],
            "api": [r"api|endpoint|url|bağlantı"],
            "veritabani": [r"db|database|veritabanı|sqlite|sql"],
            "config": [r"config|yapılandırma|ayar|setting"],
        }

    def tanila(self, metin: str) -> Intent:
        """Metni analiz et ve niyeti tanı (4 katmanlı)."""
        metin_lower = metin.lower().strip()

        # ── Katman 1: Pattern Matching ────────────────────────────────────
        skorlar = {}
        for intent, kalip_listesi in self._compiled.items():
            toplam_skor = 0.0
            eslesenler = []
            for compiled, agirlik, alt in kalip_listesi:
                if compiled.search(metin_lower):
                    toplam_skor += agirlik
                    eslesenler.append(alt)
            if toplam_skor > 0:
                skorlar[intent] = (min(toplam_skor, 1.0), eslesenler)

        # ── Katman 2: Synonym Mapping ────────────────────────────────────
        synonym_skorlar = {}
        for kelime, esler in SYNONYMS.items():
            if metin_lower in esler or kelime in metin_lower:
                # Bu kelimenin ait olduğu intent'i bul
                for intent, kalip_listesi in KALIPLAR.items():
                    for kalip, agirlik, alt in kalip_listesi:
                        for es in esler:
                            if re.search(es, kalip):
                                synonym_skorlar.setdefault(intent, 0.0)
                                synonym_skorlar[intent] += 0.3  # synonym bonus

        # Synonym skorlarını ana skorlara ekle
        for intent, skor in synonym_skorlar.items():
            if intent in skorlar:
                eski_skor = skorlar[intent][0]
                skorlar[intent] = (min(eski_skor + skor, 1.0), skorlar[intent][1])
            else:
                skorlar[intent] = (min(skor, 1.0), ["synonym"])

        # ── Katman 4: Embedding Search ───────────────────────────────────
        embedding_intent, embedding_skor = self.embedding.intent_bul(metin)
        if embedding_skor > 0.3:
            if embedding_intent in skorlar:
                eski_skor = skorlar[embedding_intent][0]
                skorlar[embedding_intent] = (min(eski_skor + embedding_skor * 0.5, 1.0),
                                             skorlar[embedding_intent][1])
            else:
                skorlar[embedding_intent] = (embedding_skor * 0.5, ["embedding"])

        # ── Sonuç ────────────────────────────────────────────────────────
        if not skorlar:
            intent = Intent(tip="bilinmiyor", guven=0.0)
        else:
            en_iyi = max(skorlar.items(), key=lambda x: x[1][0])
            tip, (guven, altlar) = en_iyi
            hedef = self._hedef_bul(metin_lower)
            alt_tip = altlar[0] if altlar else None
            intent = Intent(
                tip=tip,
                guven=round(guven, 2),
                hedef=hedef,
                alt_tip=alt_tip,
                context={"eslesenler": altlar, "tum_skorlar": skorlar},
            )

        # ── Katman 3: Context Window'a kaydet ────────────────────────────
        self.context.ekle(metin, intent)

        return intent

    def _hedef_bul(self, metin: str) -> Optional[str]:
        """Metindeki nesne/dosya/servis ipuçlarını tespit et."""
        for tur, desenler in self._obje_desenleri.items():
            for desen in desenler:
                if re.search(desen, metin):
                    return tur
        return None

    def es_anlamlilar(self, kelime: str) -> List[str]:
        """Bir kelimenin eş anlamlılarını döndür."""
        kelime_lower = kelime.lower()
        for temel, esler in SYNONYMS.items():
            if kelime_lower == temel or kelime_lower in esler:
                return [temel] + esler
        return [kelime]

    def kalip_ekle(self, intent: str, kalip: str, agirlik: float = 0.8, alt_tip: str = "ozel"):
        """Yeni kalıp ekle (dinamik genişletme)."""
        if intent not in KALIPLAR:
            KALIPLAR[intent] = []
        KALIPLAR[intent].append((kalip, agirlik, alt_tip))
        self._compiled.setdefault(intent, []).append(
            (re.compile(kalip, re.IGNORECASE), agirlik, alt_tip)
        )


# ══════════════════════════════════════════════════════════════════════════
# Global instance
# ══════════════════════════════════════════════════════════════════════════

_recognizer: Optional[IntentRecognizer] = None

def get_recognizer() -> IntentRecognizer:
    global _recognizer
    if _recognizer is None:
        _recognizer = IntentRecognizer()
    return _recognizer

def tanila(metin: str) -> Intent:
    """Kısa yol: metni niyete çevir."""
    return get_recognizer().tanila(metin)
