# -*- coding: utf-8 -*-
"""
test_hizli.py — 100 soruyu hızlı test et, sonuçları JSON'a yaz
Fix mekanizması yok, sadece pass/fail raporu
"""
import re
import subprocess
import sys
import json
import time
from pathlib import Path

DOSYA = Path(__file__).parent / "100_soru_cevap.txt"
HERMES = "hermes"
PROFIL = "reymen"
GECME_ESIGI = 0.5
TIMEOUT = 90  # saniye

def reymen_sor(soru):
    try:
        r = subprocess.run(
            [HERMES, "-p", PROFIL, "-z", soru],
            capture_output=True, text=True, encoding="utf-8",
            errors="replace", timeout=TIMEOUT
        )
        return (r.stdout or "").strip()
    except subprocess.TimeoutExpired:
        return "[TIMEOUT]"
    except Exception as e:
        return f"[HATA: {e}]"

def anahtar_kelimeler_al(metin):
    kelimeler = set()
    for m in re.finditer(r"`([^`]+)`", metin):
        k = m.group(1).strip()
        if 3 < len(k) < 50:
            kelimeler.add(k.lower())
    for m in re.finditer(r"\*\*([^*]+)\*\*", metin):
        for kelime in m.group(1).split():
            kelime = kelime.strip(".,():").lower()
            if len(kelime) > 3:
                kelimeler.add(kelime)
    for kelime in re.findall(r"\b[A-Za-zÀ-ÿğüşıöçĞÜŞİÖÇ_]{9,}\b", metin):
        kelimeler.add(kelime.lower())
    return list(kelimeler)[:12]

def eslesme_orani(anahtarlar, cevap):
    if not anahtarlar:
        return 1.0
    cevap_kucuk = cevap.lower()
    eslesen = sum(1 for k in anahtarlar if k in cevap_kucuk)
    return eslesen / len(anahtarlar)

def parse_sorular():
    metin = DOSYA.read_text(encoding="utf-8")
    sorular = []
    bolumler = re.split(r"### SORU \d+:", metin)
    for bolum in bolumler[1:]:
        satirlar = bolum.strip().split("\n")
        soru = satirlar[0].strip().rstrip("?").strip() + "?"
        cevap_match = re.search(r"\*\*CEVAP:\*\*\s*(.*?)(?:\*\*İŞ AKIŞI|\Z)", bolum, re.DOTALL)
        cevap = cevap_match.group(1).strip()[:600] if cevap_match else ""
        sorular.append({"soru": soru, "cevap": cevap, "anahtarlar": anahtar_kelimeler_al(cevap)})
    return sorular

def main():
    sorular = parse_sorular()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace") if hasattr(sys.stdout, "reconfigure") else None

    print(f"\n{'='*60}")
    print(f"  HIZLI TEST — {len(sorular)} soru, timeout={TIMEOUT}s")
    print(f"{'='*60}\n", flush=True)

    sonuclar = []
    gecti = kaldi = timeout_sayisi = 0

    for i, s in enumerate(sorular, 1):
        soru = s["soru"]
        anahtarlar = s["anahtarlar"]
        beklenen = s["cevap"]

        print(f"[Q{i:03d}] {soru[:75]}", flush=True)

        cevap = reymen_sor(soru)

        if "[TIMEOUT]" in cevap or "[HATA:" in cevap:
            durum = "TIMEOUT" if "[TIMEOUT]" in cevap else "HATA"
            print(f"       ⚠️  {durum}", flush=True)
            timeout_sayisi += 1
            kaldi += 1
            oran = 0.0
        else:
            oran = eslesme_orani(anahtarlar, cevap)
            if oran >= GECME_ESIGI:
                print(f"       ✅ GEÇTİ ({oran:.0%})", flush=True)
                gecti += 1
                durum = "GECTI"
            else:
                print(f"       ❌ KALDI ({oran:.0%})", flush=True)
                print(f"          Beklenen: {beklenen[:80].strip()}", flush=True)
                print(f"          ReYMeN:   {cevap[:80].strip()}", flush=True)
                kaldi += 1
                durum = "KALDI"

        sonuclar.append({
            "no": i, "soru": soru[:100], "durum": durum,
            "oran": round(oran, 2), "cevap": cevap[:200],
            "beklenen": beklenen[:150]
        })

        # Anlık skoru her 10 soruda göster
        if i % 10 == 0:
            print(f"\n  --- Q{i} itibarıyla: ✅{gecti} ❌{kaldi-timeout_sayisi} ⚠️{timeout_sayisi} ---\n", flush=True)

        print("", flush=True)

    # Sonuçları kaydet
    rapor_yolu = Path(__file__).parent / "test_sonuclari.json"
    rapor_yolu.write_text(json.dumps(sonuclar, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\n{'='*60}")
    print(f"  FINAL RAPOR")
    print(f"{'='*60}")
    print(f"  ✅ GEÇTİ  : {gecti}")
    print(f"  ❌ KALDI  : {kaldi - timeout_sayisi}")
    print(f"  ⚠️  TIMEOUT: {timeout_sayisi}")
    print(f"  📊 Başarı : {gecti/len(sorular)*100:.1f}%")
    print(f"\n  KALAN SORULAR:")
    for s in sonuclar:
        if s["durum"] != "GECTI":
            print(f"    Q{s['no']:03d} [{s['durum']}] {s['soru'][:55]}")
    print(f"{'='*60}\n")
    print(f"  Sonuçlar kaydedildi: {rapor_yolu}")

if __name__ == "__main__":
    main()
