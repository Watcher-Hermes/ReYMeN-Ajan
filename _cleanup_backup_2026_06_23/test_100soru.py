# -*- coding: utf-8 -*-
"""
test_100soru.py — 100_soru_cevap.txt dosyasından soruları okur,
ReYMeN'e sorar, beklenen cevapla karşılaştırır, fail olursa fix önerir.
"""
import re
import subprocess
import sys
import time
from pathlib import Path

DOSYA = Path(__file__).parent / "100_soru_cevap.txt"
HERMES = "hermes"
PROFIL = "reymen"
GECME_ESIGI = 0.5  # anahtar kelimelerin en az %50'si eşleşmeli

def reymen_sor(soru, yeni_oturum=True):
    komut = [HERMES, "-p", PROFIL, "-z", soru]
    if not yeni_oturum:
        komut.append("--continue")
    try:
        r = subprocess.run(komut, capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=120)
        return (r.stdout or "").strip()
    except subprocess.TimeoutExpired:
        return "[TIMEOUT]"
    except Exception as e:
        return f"[HATA: {e}]"

def anahtar_kelimeler_al(cevap_metni):
    """CEVAP: bloğundan önemli teknik kelimeleri çıkar."""
    kelimeler = set()
    # Backtick içindeki dosya/sınıf adları
    for m in re.finditer(r"`([^`]+)`", cevap_metni):
        k = m.group(1).strip()
        if 3 < len(k) < 50:
            kelimeler.add(k.lower())
    # **Kalın** kelimeler (kavramlar)
    for m in re.finditer(r"\*\*([^*]+)\*\*", cevap_metni):
        for kelime in m.group(1).split():
            kelime = kelime.strip(".,():").lower()
            if len(kelime) > 3:
                kelimeler.add(kelime)
    # Numaralı liste başlıkları
    for m in re.finditer(r"\d\.\s+([A-Za-zÀ-ÿğüşıöçĞÜŞİÖÇ]+)", cevap_metni):
        kelimeler.add(m.group(1).lower())
    # Uzun teknik kelimeler (9+ karakter, genellikle dosya/sınıf adı)
    for kelime in re.findall(r"\b[A-Za-zÀ-ÿğüşıöçĞÜŞİÖÇ_]{9,}\b", cevap_metni):
        kelimeler.add(kelime.lower())
    return list(kelimeler)[:12]  # max 12 anahtar kelime

def eslesme_orani(anahtarlar, reymen_cevabi):
    if not anahtarlar:
        return 1.0
    cevap_kucuk = reymen_cevabi.lower()
    eslesen = sum(1 for k in anahtarlar if k in cevap_kucuk)
    return eslesen / len(anahtarlar)

def parse_sorular(dosya_yolu):
    """SORU + CEVAP + İŞ AKIŞI bloklarını ayrıştır."""
    metin = dosya_yolu.read_text(encoding="utf-8")
    sorular = []
    # Her ### SORU N: satırı bir soru başlatır
    bolumler = re.split(r"### SORU \d+:", metin)
    for bolum in bolumler[1:]:  # ilk boşu atla
        satirlar = bolum.strip().split("\n")
        soru_metni = satirlar[0].strip().rstrip("?").strip() + "?"
        cevap_match = re.search(r"\*\*CEVAP:\*\*\s*(.*?)(?:\*\*İŞ AKIŞI|\Z)", bolum,
                                re.DOTALL)
        cevap_ozet = cevap_match.group(1).strip()[:800] if cevap_match else ""
        sorular.append({
            "soru": soru_metni,
            "cevap": cevap_ozet,
            "anahtarlar": anahtar_kelimeler_al(cevap_ozet)
        })
    return sorular

def fix_dene(soru, beklenen, reymen_cevabi):
    """Hermes'e danışarak fix öner — SOUL.md'ye not ekle."""
    fix_prompt = (
        f"ReYMeN agent bir soruyu yanlış yanıtladı.\n"
        f"SORU: {soru}\n"
        f"BEKLENEN (özet): {beklenen[:300]}\n"
        f"REYMEN'İN CEVABI: {reymen_cevabi[:300]}\n\n"
        f"Bu bilgiyi ReYMeN'e öğretmek için 1-2 cümlelik kısa bir kural yaz. "
        f"Sadece kuralı yaz, başka şey ekleme."
    )
    komut = [HERMES, "-p", "default", "-z", fix_prompt]
    try:
        r = subprocess.run(komut, capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=60)
        return (r.stdout or "").strip()
    except Exception:
        return ""

def main():
    if not DOSYA.exists():
        print(f"[HATA] Dosya bulunamadı: {DOSYA}")
        sys.exit(1)

    sorular = parse_sorular(DOSYA)
    sys.stdout.reconfigure(encoding="utf-8", errors="replace") if hasattr(sys.stdout, "reconfigure") else None
    print(f"\n{'='*65}")
    print(f"  ReYMeN 100 SORU TESTI -- {len(sorular)} soru yuklendi")
    print(f"{'='*65}\n")

    gecti = 0
    kaldi = 0
    kalan_sorular = []

    for i, s in enumerate(sorular, 1):
        soru = s["soru"]
        beklenen = s["cevap"]
        anahtarlar = s["anahtarlar"]

        print(f"[Q{i:03d}] {soru[:80]}")
        sys.stdout.flush()

        # ReYMeN'e sor (her soru yeni session)
        cevap = reymen_sor(soru, yeni_oturum=True)
        if not cevap or cevap.startswith("["):
            print(f"       ⚠️  Cevap alınamadı: {cevap[:60]}")
            kaldi += 1
            kalan_sorular.append({"no": i, "soru": soru, "reymen": cevap,
                                   "beklenen": beklenen[:150]})
            print()
            continue

        oran = eslesme_orani(anahtarlar, cevap)

        if oran >= GECME_ESIGI:
            print(f"       ✅ GEÇTİ  (eşleşme: {oran:.0%})")
            gecti += 1
        else:
            print(f"       ❌ KALDI  (eşleşme: {oran:.0%})")
            print(f"       📌 Beklenen (özet): {beklenen[:120].strip()}")
            print(f"       🤖 ReYMeN: {cevap[:120].strip()}")
            kaldi += 1
            kalan_sorular.append({"no": i, "soru": soru, "reymen": cevap[:200],
                                   "beklenen": beklenen[:200],
                                   "anahtarlar": anahtarlar})

            # Hermes'e danış, fix öner
            print(f"       🔧 Hermes'e danışılıyor...")
            sys.stdout.flush()
            fix = fix_dene(soru, beklenen, cevap)
            if fix:
                print(f"       💡 Öneri: {fix[:150]}")
                # SOUL.md'ye not ekle
                soul_path = Path(r"C:\Users\marko\AppData\Local\hermes\profiles\reymen\SOUL.md")
                if soul_path.exists():
                    mevcut = soul_path.read_text(encoding="utf-8")
                    if fix[:50] not in mevcut:  # duplicate ekleme
                        with soul_path.open("a", encoding="utf-8") as f:
                            f.write(f"\n<!-- Q{i:03d}-fix: {fix[:200]} -->\n")
                        print(f"       📝 SOUL.md'ye eklendi.")

            # Aynı soruyu tekrar sor (yeni session = fix aktif)
            print(f"       🔄 Tekrar soruluyor...")
            sys.stdout.flush()
            time.sleep(1)
            cevap2 = reymen_sor(soru, yeni_oturum=True)
            oran2 = eslesme_orani(anahtarlar, cevap2)
            if oran2 >= GECME_ESIGI:
                print(f"       ✅ YENİDEN GEÇTİ ({oran2:.0%})")
                gecti += 1
                kaldi -= 1
            else:
                print(f"       ❌ HÂLÂ KALDI ({oran2:.0%}) → Skill güncellemesi gerekebilir")
        print()
        sys.stdout.flush()

    # Final rapor
    print(f"\n{'='*65}")
    print(f"  FINAL RAPOR — {len(sorular)} soru")
    print(f"{'='*65}")
    print(f"  ✅ GEÇTİ : {gecti}")
    print(f"  ❌ KALDI : {kaldi}")
    print(f"  📊 Başarı: {gecti/len(sorular)*100:.1f}%")
    if kalan_sorular:
        print(f"\n  KALAN SORULAR:")
        for s in kalan_sorular:
            print(f"    Q{s['no']:03d}: {s['soru'][:60]}")
    print(f"{'='*65}\n")

if __name__ == "__main__":
    main()
