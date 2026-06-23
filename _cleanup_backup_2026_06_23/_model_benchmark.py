# -*- coding: utf-8 -*-
"""
_model_benchmark.py — Tüm modelleri test et, puanla, raporla.
"""
import os, sys, shutil, subprocess, time, json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

try:
    from dotenv import load_dotenv
    _HH = Path(os.environ.get("LOCALAPPDATA","")) / "hermes"
    load_dotenv(Path(__file__).parent / ".env", override=True)
    load_dotenv(_HH / ".env", override=True)
    load_dotenv(_HH / "profiles" / "reymen" / ".env", override=True)
except Exception:
    _HH = Path(os.environ.get("LOCALAPPDATA","")) / "hermes"

_HERMES   = shutil.which("hermes")
_CFG_PATH = _HH / "profiles" / "reymen" / "config.yaml"

# ── Test modelleri ─────────────────────────────────────────────────────────────
MODELLER = [
    ("deepseek",   "deepseek-v4-flash",      "DeepSeek V4 Flash",   "DEEPSEEK_API_KEY",   ""),
    ("deepseek",   "deepseek-chat",           "DeepSeek V3",         "DEEPSEEK_API_KEY",   ""),
    ("deepseek",   "deepseek-reasoner",       "DeepSeek R1",         "DEEPSEEK_API_KEY",   ""),
    ("xai",        "grok-3",                  "xAI Grok 3",          "XAI_API_KEY",        ""),
    ("xai",        "grok-3-mini",             "xAI Grok 3 Mini",     "XAI_API_KEY",        ""),
    ("xai",        "grok-beta",               "xAI Grok Beta",       "XAI_API_KEY",        ""),
    ("openrouter", "deepseek/deepseek-chat",  "OpenRouter/DeepSeek", "OPENROUTER_API_KEY", "https://openrouter.ai/api/v1"),
]

SORULAR = [
    ("skill",   "Kaç adet skill var? Sadece sayıyı söyle, tek satır."),
    ("hafiza",  "Hafızanda kaç kayıt var? Sadece sayıyı söyle, tek satır."),
    ("hakkinda","Hangi modeli kullanıyorsun ve ne yaparsın? Kısa cevap."),
]

TIMEOUT   = 55
BOŞ_SINIR = 8

# ── Config yönetimi ────────────────────────────────────────────────────────────
def _cfg_yedekle():
    return _CFG_PATH.read_bytes()

def _cfg_geri_yukle(yedek_bytes):
    _CFG_PATH.write_bytes(yedek_bytes)

def _cfg_yaz(provider, model, base_url=""):
    try:
        import yaml
        cfg = yaml.safe_load(_CFG_PATH.read_text(encoding="utf-8"))
        # model key'i her zaman dict olarak yaz
        cfg["model"] = {
            "api_mode": "chat_completions",
            "base_url": base_url,
            "default":  model,
            "provider": provider,
        }
        _CFG_PATH.write_text(
            yaml.dump(cfg, allow_unicode=True, default_flow_style=False),
            encoding="utf-8"
        )
        return True
    except Exception as e:
        print(f"    [cfg_yaz hata]: {e}")
        return False

def _gateway_yenile():
    try:
        subprocess.run(
            [_HERMES, "gateway", "restart", "-p", "reymen"],
            capture_output=True, timeout=12
        )
    except Exception:
        pass
    # hermes gateway list'te reymen ✓ görünene kadar bekle (maks ~8s)
    for _ in range(10):
        try:
            r = subprocess.run(
                [_HERMES, "gateway", "list"],
                capture_output=True, text=True, timeout=5
            )
            if any("reymen" in s and s.strip().startswith("✓")
                   for s in r.stdout.splitlines()):
                break
        except Exception:
            pass
        time.sleep(0.8)

# ── Tek soru çalıştır ─────────────────────────────────────────────────────────
def _sor(soru, ilk=False):
    if not _HERMES:
        return None, "HATA: hermes yok", True, -1, ""
    cmd = [_HERMES, "-p", "reymen", "-z", soru]
    if not ilk:
        cmd.append("--continue")
    t0 = time.perf_counter()
    try:
        r = subprocess.run(cmd, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=TIMEOUT)
        sure = time.perf_counter() - t0
        cevap  = r.stdout.strip()
        stderr = r.stderr.strip()

        if not cevap and stderr:
            _f = ("hermes","nous research","© nous","update available","upgrade","version","warning")
            satirlar = [s for s in stderr.splitlines()
                        if not any(f in s.lower() for f in _f)]
            cevap = "\n".join(satirlar).strip()

        bos = len(cevap) < BOŞ_SINIR
        return sure, cevap, bos, r.returncode, stderr[:200] if bos else ""
    except subprocess.TimeoutExpired:
        return TIMEOUT, f"TIMEOUT ({TIMEOUT}s aşıldı)", True, -1, ""
    except Exception as e:
        return None, f"EXCEPTION: {e}", True, -1, ""

# ── Puanlama (maks 10) ────────────────────────────────────────────────────────
def _puan(sure, cevap, bos):
    if bos or sure is None:
        return 0
    p = 3  # cevap geldi
    if   sure < 8:  p += 3
    elif sure < 20: p += 2
    elif sure < 40: p += 1
    if len(cevap) > 40:  p += 2
    if len(cevap) > 120: p += 2
    return min(p, 10)

# ── Renkler ───────────────────────────────────────────────────────────────────
R  = "\033[0m";  B  = "\033[1m"
C  = "\033[96m"; D  = "\033[2m"
GR = "\033[92m"; YL = "\033[93m"; RD = "\033[91m"

def _puan_renk(p, maks=30):
    if p >= maks*0.75: return GR
    if p >= maks*0.40: return YL
    return RD

# ══════════════════════════════════════════════════════════════════════════════
def main():
    print(f"\n{C}{B}{'═'*68}{R}")
    print(f"{C}{B}  ReYMeN — Model Benchmark  [{len(MODELLER)} model, {len(SORULAR)} soru]{R}")
    print(f"{C}{B}{'═'*68}{R}\n")

    # Key olan modelleri filtrele
    aktif = [(p,m,ad,env,url) for p,m,ad,env,url in MODELLER
             if not env or os.environ.get(env,"").strip()]
    print(f"  {D}Key bulunan model: {len(aktif)}/{len(MODELLER)}{R}\n")

    # Orijinal config'i yedekle
    yedek = _cfg_yedekle()
    print(f"  {D}Config yedeklendi ({len(yedek)} byte){R}\n")

    sonuclar = []

    for idx, (prov, model, ad, env, url) in enumerate(aktif, 1):
        print(f"\n{C}{'─'*68}{R}")
        print(f"  {B}[{idx}/{len(aktif)}] {ad}{R}  {D}{prov} / {model}{R}")
        print(f"{C}{'─'*68}{R}")

        # Config yaz + gateway restart
        if not _cfg_yaz(prov, model, url):
            sonuclar.append((ad, prov, model, [], 0, ["config yazılamadı"]))
            continue

        print(f"  {D}gateway yenileniyor...{R}", end="", flush=True)
        _gateway_yenile()
        print(f"\r  {GR}✓{R} gateway hazır.              ")

        model_sonuc = []
        toplam_p    = 0
        hatalar     = []

        for s_idx, (soru_id, soru) in enumerate(SORULAR):
            ilk = (s_idx == 0)
            print(f"  {D}► {soru_id}:{R} ", end="", flush=True)
            sure, cevap, bos, retcode, se = _sor(soru, ilk=ilk)

            p = _puan(sure, cevap, bos)
            toplam_p += p

            sure_s = f"{sure:.1f}s" if sure is not None else "—"
            if not bos:
                print(f"{GR}✓{R}  {sure_s}  {D}[{p}p]{R}")
                ozet = cevap.replace("\n"," ")
                print(f"    {D}{ozet[:110]}{'...' if len(ozet)>110 else ''}{R}")
            else:
                print(f"{RD}✗{R}  {sure_s}  {D}[{p}p]{R}")
                print(f"    {RD}BOŞ CEVAP  retcode={retcode}{R}")
                if se:
                    stderr_temiz = se.replace("\n"," ")[:120]
                    print(f"    {D}stderr: {stderr_temiz}{R}")
                hatalar.append(f"{soru_id}: boş (rc={retcode})")

            model_sonuc.append((soru_id, sure, cevap, bos, p))
            time.sleep(0.8)

        puan_renk = _puan_renk(toplam_p)
        print(f"\n  Toplam: {puan_renk}{B}{toplam_p}/30{R}")
        sonuclar.append((ad, prov, model, model_sonuc, toplam_p, hatalar))

    # ── Config geri yükle ─────────────────────────────────────────────────────
    print(f"\n{C}{'═'*68}{R}")
    _cfg_geri_yukle(yedek)
    _gateway_yenile()
    print(f"  {GR}✓{R} Orijinal config geri yüklendi + gateway restart.\n")

    # ── SKOR TABLOSU ──────────────────────────────────────────────────────────
    print(f"{C}{B}{'═'*68}{R}")
    print(f"{C}{B}  SKOR TABLOSU{R}")
    print(f"{C}{B}{'═'*68}{R}\n")

    sirali = sorted(sonuclar, key=lambda x: x[4], reverse=True)
    print(f"  {'#':<3} {'Model':<26} {'Sağlayıcı':<12} {'Puan':>5}  {'Ort Hız':>8}  Durum")
    print(f"  {'─'*65}")

    for rank, (ad, prov, model, ms, puan, hatalar) in enumerate(sirali, 1):
        sureler = [s for _,s,_,bos,_ in ms if s is not None and not bos]
        ort = f"{sum(sureler)/len(sureler):.1f}s" if sureler else "—"
        pr  = _puan_renk(puan)
        bos_s = sum(1 for _,_,_,bos,_ in ms if bos) if ms else 0
        durum = f"{RD}{bos_s} boş cevap{R}" if bos_s else f"{GR}Temiz{R}"
        print(f"  {D}{rank:<3}{R} {pr}{ad:<26}{R} {D}{prov:<12}{R} {pr}{B}{puan:>4}/30{R}  {ort:>8}  {durum}")

    print(f"\n  {D}─────────────────────────────────────────────────────────────{R}")

    # Hız sıralaması
    hizli = [(ad, sum(s for _,s,_,bos,_ in ms if s and not bos)/max(1,len([x for _,x,_,bos,_ in ms if x and not bos])))
             for ad,_,_,ms,p,_ in sirali if ms]
    hizli = [(ad,h) for ad,h in hizli if h > 0]
    if hizli:
        hizli.sort(key=lambda x: x[1])
        print(f"\n  {B}Hız Sıralaması:{R}")
        for ad, ort_sure in hizli:
            bar = "█" * min(20, int(ort_sure/2))
            print(f"    {ad:<26} {ort_sure:>6.1f}s  {D}{bar}{R}")

    # Hata özeti
    hatalı = [(ad, h) for ad,_,_,_,_,h in sirali if h]
    if hatalı:
        print(f"\n  {B}Boş Cevap / Hata Detayı:{R}")
        for ad, hs in hatalı:
            for h in hs:
                print(f"    {RD}✗{R} {ad}: {h}")

    print(f"\n  {D}Puanlama: Cevap=3p · Hız(<8s=3p,<20s=2p,<40s=1p) · İçerik(>40c=2p,>120c=2p) · Maks 10p/soru{R}")
    print(f"\n{C}{B}{'═'*68}{R}\n")

if __name__ == "__main__":
    main()
