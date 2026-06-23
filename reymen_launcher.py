# -*- coding: utf-8 -*-
"""
reymen_launcher.py — ReYMeN özel REPL. Hermes UI açılmaz, sadece motor kullanılır.
"""
import os
import sys
import shutil
import subprocess
from pathlib import Path
from datetime import datetime

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

_KOK = Path(__file__).parent.resolve()
os.chdir(_KOK)
sys.path.insert(0, str(_KOK))

_HERMES_HOME  = Path(os.environ.get("LOCALAPPDATA", "")) / "hermes"
_PROFILE_CFG  = _HERMES_HOME / "profiles" / "reymen" / "config.yaml"

try:
    from dotenv import load_dotenv
    load_dotenv(_KOK / ".env", override=True)
    load_dotenv(_HERMES_HOME / ".env", override=True)
    load_dotenv(_HERMES_HOME / "profiles" / "reymen" / ".env", override=True)
except Exception:
    pass

# ── ANSI ─────────────────────────────────────────────────────────────────────
_R   = "\033[0m"
_B   = "\033[1m"
_C   = "\033[96m"   # cyan
_G   = "\033[92m"   # green
_Y   = "\033[93m"   # yellow
_M   = "\033[95m"   # magenta
_D   = "\033[2m"    # dim
_W   = "\033[97m"   # white
_RED = "\033[91m"   # kırmızı

def _c(t):   return f"{_C}{t}{_R}"
def _g(t):   return f"{_G}{t}{_R}"
def _y(t):   return f"{_Y}{t}{_R}"
def _b(t):   return f"{_B}{t}{_R}"
def _d(t):   return f"{_D}{t}{_R}"
def _r(t):   return f"{_RED}{t}{_R}"
def _gb(t):  return f"{_G}{_B}{t}{_R}"
def _cb(t):  return f"{_C}{_B}{t}{_R}"
def _wb(t):  return f"{_W}{_B}{t}{_R}"

# ── Logo ─────────────────────────────────────────────────────────────────────
_LOGO = [
    r"██████╗ ███████╗██╗   ██╗███╗   ███╗███████╗███╗   ██╗",
    r"██╔══██╗██╔════╝╚██╗ ██╔╝████╗ ████║██╔════╝████╗  ██║",
    r"██████╔╝█████╗   ╚████╔╝ ██╔████╔██║█████╗  ██╔██╗ ██║",
    r"██╔══██╗██╔══╝    ╚██╔╝  ██║╚██╔╝██║██╔══╝  ██║╚██╗██║",
    r"██║  ██║███████╗   ██║   ██║ ╚═╝ ██║███████╗██║ ╚████║",
    r"╚═╝  ╚═╝╚══════╝   ╚═╝   ╚═╝     ╚═╝╚══════╝╚═╝  ╚═══╝",
]

# ── Config helpers ────────────────────────────────────────────────────────────
def _mevcut_model():
    try:
        import yaml
        cfg = yaml.safe_load(_PROFILE_CFG.read_text(encoding="utf-8"))
        return cfg.get("model", {}).get("default", "deepseek-chat"), \
               cfg.get("model", {}).get("provider", "deepseek")
    except Exception:
        return "deepseek-chat", "deepseek"

def _gateway_hazir_mi(deneme=10, aralik=0.7):
    """hermes gateway list çıktısında reymen ✓ görünene kadar bekle."""
    hermes = shutil.which("hermes") or "hermes"
    import time as _t
    for _ in range(deneme):
        try:
            r = subprocess.run(
                [hermes, "gateway", "list"],
                capture_output=True, text=True, timeout=5
            )
            satirlar = r.stdout.splitlines()
            for s in satirlar:
                if "reymen" in s and s.strip().startswith("✓"):
                    return True
        except Exception:
            pass
        _t.sleep(aralik)
    return False

def _model_guncelle(provider, model, base_url=""):
    global _ilk_tur
    try:
        import yaml
        cfg = yaml.safe_load(_PROFILE_CFG.read_text(encoding="utf-8"))
        # Model key'ini her zaman dict olarak yaz (string → dict dönüşümü)
        cfg["model"] = {
            "api_mode": "chat_completions",
            "base_url": base_url,
            "default":  model,
            "provider": provider,
        }
        _PROFILE_CFG.write_text(
            yaml.dump(cfg, allow_unicode=True, default_flow_style=False),
            encoding="utf-8"
        )
    except Exception:
        pass
    try:
        subprocess.run(
            [shutil.which("hermes") or "hermes", "gateway", "restart", "-p", "reymen"],
            capture_output=True, timeout=15
        )
    except Exception:
        pass
    # Gateway hazır olana kadar bekle; sonra session'ı sıfırla
    _gateway_hazir_mi()
    _ilk_tur = True  # Model değişti → --continue kullanma, yeni session başlat

def _skill_sayisi():
    d = _KOK / "skills"
    if not d.exists():
        return 0
    _skip_names = {"README.md", "DESCRIPTION.md", "readme-template.md"}
    _skip_parts = {"ecc", "references", "_kok_copluk_backup", "_ecc_hermes_builtin_backup"}
    return sum(
        1 for p in d.rglob("*.md")
        if p.name not in _skip_names
        and not any(part in _skip_parts for part in p.parts)
    )

def _mem_kayit():
    mem = _HERMES_HOME / "profiles" / "reymen" / "memories" / "MEMORY.md"
    try:
        return mem.read_text(encoding="utf-8", errors="replace").count("§") + 1
    except Exception:
        return 0

# ── API Key Durum Kontrolü ────────────────────────────────────────────────────
import urllib.request, urllib.error, json, time as _time

_API_CACHE     = {}   # {provider: (True/False/None, timestamp)}
_API_CACHE_TTL = 300  # 5 dakika

_API_KONTROL_ENDPOINTS = [
    ("deepseek",   "https://api.deepseek.com/user/balance",   "DEEPSEEK_API_KEY"),
    ("xai",        "https://api.x.ai/v1/models",              "XAI_API_KEY"),
    ("openrouter", "https://openrouter.ai/api/v1/auth/key",   "OPENROUTER_API_KEY"),
]

def _tek_kontrol(prov, url, env_var, sonuclar, kilid):
    key = os.environ.get(env_var, "").strip()
    if not key:
        with kilid:
            sonuclar[prov] = None
        return
    try:
        req = urllib.request.Request(
            url,
            headers={"Authorization": f"Bearer {key}", "Accept": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=6) as r:
            if prov == "deepseek":
                data = json.loads(r.read().decode())
                ok = data.get("is_available", True)
            else:
                ok = True
    except urllib.error.HTTPError as e:
        # 401 = kesinlikle geçersiz/kredi bitti
        # 402 = ödeme gerekli (kredi bitti)
        # Diğer (403, 404, 429...) = belirsiz (key var ama endpoint erişilemez)
        if e.code in (401, 402):
            ok = False
        else:
            ok = None
    except Exception:
        ok = None
    with kilid:
        sonuclar[prov] = ok

def _api_kontrol(yenile=False):
    simdi = _time.time()
    provlar = [p for p,_,__ in _API_KONTROL_ENDPOINTS]
    if not yenile and all(
        p in _API_CACHE and (simdi - _API_CACHE[p][1]) < _API_CACHE_TTL
        for p in provlar
    ):
        return {p: _API_CACHE[p][0] for p in provlar}

    import threading as _th
    sonuclar, kilid = {}, _th.Lock()
    threadler = [
        _th.Thread(target=_tek_kontrol, args=(p, u, e, sonuclar, kilid), daemon=True)
        for p, u, e in _API_KONTROL_ENDPOINTS
    ]
    for t in threadler: t.start()
    for t in threadler: t.join(timeout=7)

    for p in provlar:
        _API_CACHE[p] = (sonuclar.get(p), _time.time())
    return sonuclar

def _api_ikon(prov, api_d):
    if prov == "lmstudio":
        return _d("--")
    d = api_d.get(prov)
    if d is True:  return _g("✓")
    if d is False: return _r("✗")
    return _y("?")

def _model_adi(prov, model):
    for p, m, ad, _env, _url in _MODELLER:
        if p == prov and m == model:
            return ad
    return model

# ── Açılış ekranı ─────────────────────────────────────────────────────────────
def _ekran(api_d=None):
    import subprocess; subprocess.run("cls" if os.name == "nt" else "clear", shell=True)
    for s in _LOGO:
        print(f"  {_cb(s)}")
    print()

    tarih   = datetime.now().strftime("%Y-%m-%d %H:%M")
    model, prov = _mevcut_model()
    skill_n = _skill_sayisi()
    mem_n   = _mem_kayit()
    W = 60

    # Model satırı: "DeepSeek V4 Flash  (deepseek-v4-flash)"  + durum ikonu
    try:
        ad = _model_adi(prov, model)
    except Exception:
        ad = model
    if api_d is not None:
        ikon = " " + _api_ikon(prov, api_d)
        ikon_len = 2
    else:
        ikon = ""
        ikon_len = 0

    def _row(lbl, val, fn=_g, extra="", extra_len=0):
        pad = W - len(lbl) - len(val) - 5 - extra_len
        print(f"  {_c('║')}  {_d(lbl + ':')} {fn(val)}{extra}{' ' * max(0, pad)}{_c('║')}")

    print(f"  {_c('╔' + '═'*W + '╗')}")
    print(f"  {_c('║')}  {_gb('ReYMeN Otonom Ajan')}{' '*(W-22)}{_c('║')}")
    print(f"  {_c('║')}  {_d('Cave Modu · Türkçe · Otonom REPL')}{' '*(W-36)}{_c('║')}")
    print(f"  {_c('╠' + '═'*W + '╣')}")
    _row("Tarih  ", tarih)
    _row("Model  ", f"{ad}  ({model})", _y, ikon, ikon_len)
    _row("Skill  ", f"{skill_n} adet")
    _row("Hafiza ", f"{mem_n} kayit")
    print(f"  {_c('╚' + '═'*W + '╝')}")
    print()

# ── Model seçimi ──────────────────────────────────────────────────────────────
# (provider, model_id, görünen_ad, env_var, base_url)
_MODELLER = [
    ("deepseek",   "deepseek-v4-flash",        "DeepSeek V4 Flash",      "DEEPSEEK_API_KEY",   ""),
    ("deepseek",   "deepseek-chat",             "DeepSeek V3",            "DEEPSEEK_API_KEY",   ""),
    ("deepseek",   "deepseek-reasoner",         "DeepSeek R1",            "DEEPSEEK_API_KEY",   ""),
    ("xai",        "grok-3",                    "xAI Grok 3",             "XAI_API_KEY",        ""),
    ("xai",        "grok-3-mini",               "xAI Grok 3 Mini",        "XAI_API_KEY",        ""),
    ("xai",        "grok-beta",                 "xAI Grok Beta",          "XAI_API_KEY",        ""),
    ("openrouter", "deepseek/deepseek-chat",    "OpenRouter / DeepSeek",  "OPENROUTER_API_KEY", "https://openrouter.ai/api/v1"),
    ("lmstudio",   "local",                     "LM Studio (Yerel)",      "",                   "http://localhost:1234/v1"),
]

def _model_sec(api_d=None):
    if api_d is None:
        api_d = {}
    cur_m, cur_p = _mevcut_model()
    liste = [(p,m,a,url) for p,m,a,env,url in _MODELLER
             if not env or os.environ.get(env,"").strip()]
    if not liste:
        return

    print(f"  {_b('Model Sec:')}")
    print()
    for i,(prov,mod,ad,url) in enumerate(liste, 1):
        aktif = (mod == cur_m and prov == cur_p)
        isk   = _gb("→") if aktif else _d(" ")
        ikon  = _api_ikon(prov, api_d)
        print(f"  {isk} [{_cb(str(i))}] {ikon} {_g(ad):<26} {_d(mod)}")
    print()
    try:
        y = input(f"  {_d('[ENTER: mevcut koru]')}: ").strip()
    except (EOFError, KeyboardInterrupt):
        print(); return

    if y.isdigit():
        idx = int(y) - 1
        if 0 <= idx < len(liste):
            prov, mod, ad, url = liste[idx]
            durum = api_d.get(prov)
            if durum is False:
                print(f"\n  {_r('✗')} {_b(ad)} — API kredisi yetersiz veya key geçersiz.")
                print(f"  {_d('Hesabına bakiye yükle, sonra yeniden başlat.')}")
                print()
                return
            print(f"  {_y('◌')} {_d('gateway yeniden baslatiliyor...')}", end="", flush=True)
            _model_guncelle(prov, mod, url)
            print(f"\r  {_g('✓')} {_b(ad)} aktif.                        ")
    print()

# ── Cevap kutusu ──────────────────────────────────────────────────────────────
def _kutu(metin: str):
    """Cevabı rich ile render edip ReYMeN kutusunda göster."""
    try:
        from rich.console import Console
        from rich.markdown import Markdown
        from rich.panel import Panel
        from rich.theme import Theme

        tema = Theme({
            "markdown.h1": "bold cyan",
            "markdown.h2": "bold cyan",
            "markdown.h3": "cyan",
            "markdown.bold": "bold white",
            "markdown.code": "green",
            "markdown.code_block": "green",
            "markdown.link": "cyan underline",
        })
        console = Console(theme=tema, highlight=False)
        md = Markdown(metin, justify="left")
        console.print(Panel(
            md,
            title="[bold cyan]◈ ReYMeN[/bold cyan]",
            border_style="cyan",
            padding=(0, 1),
        ))
    except Exception:
        # rich yoksa düz metin
        print()
        print(f"  {_c('┌─')}{_cb(' ReYMeN ')}{_c('─'*50)}{_c('┐')}")
        for satir in metin.strip().split("\n"):
            print(f"  {_c('│')} {satir}")
        print(f"  {_c('└' + '─'*60 + '┘')}")
        print()

# ── Spinner ───────────────────────────────────────────────────────────────────
import threading, itertools, time

def _spinner(stop_evt):
    frames = ["◈", "◉", "◎", "⊙", "○"]
    verbs  = ["analiz", "düşün", "işlem", "araştır", "hesapla"]
    cyc_f  = itertools.cycle(frames)
    cyc_v  = itertools.cycle(verbs)
    verb   = next(cyc_v)
    count  = 0
    while not stop_evt.is_set():
        frame = next(cyc_f)
        print(f"\r  {_c(frame)} {_d(verb)}...   ", end="", flush=True)
        time.sleep(0.12)
        count += 1
        if count % 10 == 0:
            verb = next(cyc_v)
    print(f"\r{' '*30}\r", end="", flush=True)

# ── Hermes çağrısı ────────────────────────────────────────────────────────────
_HERMES = shutil.which("hermes")
_ilk_tur = True

_KREDI_SINYALLER = (
    "insufficient_quota", "insufficient balance", "insufficient funds",
    "out of credits", "no credits", "quota exceeded", "exceeded your current quota",
    "billing", "payment required", "402", "topup", "recharge",
    "account balance", "credits remaining", "credit limit",
)
_BRANDING_FILTRE = (
    "hermes", "nous research", "© nous", "hermes agent",
    "update available", "upgrade available", "version",
)

def _sor(soru: str) -> str:
    global _ilk_tur
    if not _HERMES:
        return "HATA: hermes komutu bulunamadi."

    cmd = [_HERMES, "-p", "reymen", "-z", soru]
    if not _ilk_tur:
        cmd.append("--continue")
    _ilk_tur = False

    stop = threading.Event()
    t = threading.Thread(target=_spinner, args=(stop,), daemon=True)
    t.start()

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=180
        )
        cevap  = result.stdout.strip()
        stderr = result.stderr.strip()
        birlesik = (cevap + " " + stderr).lower()

        # Kredi / kota hatası tespiti
        if any(s in birlesik for s in _KREDI_SINYALLER):
            model, prov = _mevcut_model()
            return f"⚠ API kredisi yetersiz — {prov} / {model} hesabını kontrol et ve bakiye yükle."

        if not cevap and stderr:
            satirlar = [s for s in stderr.splitlines()
                        if not any(f in s.lower() for f in _BRANDING_FILTRE)]
            cevap = "\n".join(satirlar).strip()

        return cevap or "(boş cevap)"
    except subprocess.TimeoutExpired:
        return "HATA: Zaman asimi (180s)."
    except Exception as e:
        return f"HATA: {e}"
    finally:
        stop.set()
        t.join(timeout=1)

# ── Komut yardımı ─────────────────────────────────────────────────────────────
_YARDIM = f"""
  {_cb('ReYMeN Komutlar')}

  {_c('/yardim')}        Bu menüyü göster
  {_c('/model')}         Model değiştir
  {_c('/temizle')}       Ekranı temizle
  {_c('/skill')} {_d('<ara>')}  Skill ara
  {_c('/cik')}           Çıkış

  {_d('Herhangi bir metin yaz → ReYMeN cevaplar.')}
"""

# ── Ana REPL ──────────────────────────────────────────────────────────────────
def _repl():
    print(f"  {_d('ReYMeN hazır. Komut ver. (/yardim için /yardim yaz)')}")
    print()

    while True:
        try:
            girdi = input(f"  {_c('◈')} ").strip()
        except (EOFError, KeyboardInterrupt):
            print(f"\n  {_d('ReYMeN kapanıyor.')}")
            break

        if not girdi:
            continue

        # Komutlar
        if girdi.lower() in ("/cik", "/çık", "exit", "quit", "q"):
            print(f"  {_d('ReYMeN kapanıyor.')}")
            break
        if girdi.lower() in ("/yardim", "/help", "/?"):
            print(_YARDIM)
            continue
        if girdi.lower() in ("/temizle", "/cls", "/clear"):
            _ekran()
            print(f"  {_d('ReYMeN hazır.')}\n")
            continue
        if girdi.lower().startswith("/model"):
            _model_sec()
            continue
        if girdi.lower().startswith("/skill "):
            ara = girdi[7:].strip()
            cevap = _sor(f"skill ara: {ara}")
            _kutu(cevap)
            continue

        # Normal soru
        cevap = _sor(girdi)
        _kutu(cevap)

# ── Giriş noktası ────────────────────────────────────────────────────────────
def main():
    import threading as _th

    # Logo + ekranı göster (API kontrol arka planda başlasın)
    _api_sonuc = {}
    def _kontrol_yap():
        _api_sonuc.update(_api_kontrol())

    kontrol_t = _th.Thread(target=_kontrol_yap, daemon=True)
    kontrol_t.start()

    _ekran()   # logo göster, API kontrol henüz bitmemiş olabilir

    print(f"  {_d('API key durumu kontrol ediliyor...')}", end="", flush=True)
    kontrol_t.join(timeout=8)
    print(f"\r{' '*50}\r", end="", flush=True)

    # Ekranı API durumu ile yenile
    _ekran(_api_sonuc)
    _model_sec(_api_sonuc)
    _repl()

if __name__ == "__main__":
    main()
