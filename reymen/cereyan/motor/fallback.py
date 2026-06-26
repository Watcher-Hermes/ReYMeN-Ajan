"""motor/fallback.py — Motor fallback yardımcıları (self yerine motor parametresi).

_main.py'deki Motor class'ı bu modüldeki fonksiyonlara delegasyon yapar.
"""
import json
import logging
import os
import re
import subprocess
import threading
import time as _time
from pathlib import Path

from reymen.cereyan.motor.config import ROOT, DURUM_MESAJLARI, TOOLSET_GRUPLARI
from reymen.cereyan.motor.context import gateway_durum_yaz as _gateway_durum_yaz
from reymen.cereyan.motor.plugins import _REGISTRY, _PLUGIN_MGR, _CUA_MEVCUT, CUA_EKRAN_KULLAN, CUA_ARACLARI_TARA

log = logging.getLogger("motor")

# Modül seviyesi sabitler (try/except ile fail-open)
try:
    from file_safety import guvenli_mi as _dosya_guvenli
except ImportError:
    _dosya_guvenli = lambda p: (True, "")
try:
    from path_security import yol_dogrula as _yol_dogrula
except ImportError:
    _yol_dogrula = lambda p: (True, p)


# ── HATA_COZUCU ──────────────────────────────────────────────────────────────
def hata_cozucu_calistir(motor, arac: str, params: list) -> str:
    try:
        from hata_cozucu import HataWatchdog, HataKoduUretici, TerminalHataParser, CozumUygulayici
        if motor._hata_watchdog is None:
            motor._hata_watchdog = HataWatchdog()
            motor._hata_kod = HataKoduUretici()
            motor._hata_terminal = TerminalHataParser()
            motor._hata_cozum = CozumUygulayici(motor._hata_kod)
        if arac == "HATA_WATCH_BASLAT":
            motor._hata_watchdog.baslat()
            return "[HataWatchdog] Baslatildi."
        if arac == "HATA_WATCH_DURDUR":
            motor._hata_watchdog.durdur()
            return "[HataWatchdog] Durduruldu."
        if arac == "HATA_KOD_AL":
            kayit = motor._hata_kod.kaydet(params[0] if params else "Bilinmeyen hata")
            return f"[HataKod] {kayit.kod}: [{kayit.kategori}] {kayit.ozet}\nClaude'a yapistir: {kayit.kod}"
        if arac == "TERMINAL_HATA_PARSE":
            sonuc = motor._hata_terminal.parse(params[0] if params else "")
            if sonuc["hata_var"]:
                return f"[Terminal] {sonuc['hata_sayisi']} hata.\nIlki: {sonuc['ozet']}"
            return "[Terminal] Hata bulunamadi."
        if arac == "COZUM_UYGULA":
            sonuc = motor._hata_cozum.uygula(params[0] if params else "")
            if sonuc["basarili"]:
                return f"[Cozum] Basarili: {sonuc['patch_sonuc']}"
            return f"[Cozum] Basarisiz: {sonuc['mesaj']}"
    except Exception as e:
        return f"[Hata]: hata_cozucu: {e}"
    return "[Hata]: Bilinmeyen hata_cozucu araci."


# ── TOR_OTOMASYONU ───────────────────────────────────────────────────────────
def tor_otomasyonu_calistir(motor, arac: str, ham_param: str, params: list) -> str:
    try:
        from tor_otomasyonu import (
            TorBrowserKontrol, FormDoldurucu, OtomasyonAkislari,
            tor_baslat, tor_kapat,
        )
        if arac == "TOR_AC":
            sonuc = tor_baslat(ham_param.strip() or None)
            if "[Tor] Browser baslatildi" in sonuc:
                from tor_otomasyonu import _aktif_tor, _aktif_akislar
                motor._tor_browser = _aktif_tor
                motor._tor_akislar = _aktif_akislar
            return sonuc
        if arac == "TOR_KAPAT":
            sonuc = tor_kapat()
            motor._tor_browser = None
            motor._tor_akislar = None
            return sonuc
        if not motor._tor_browser:
            return "[Tor]: Once TOR_AC ile baslatin."
        if arac == "TOR_FORM_DOLDUR":
            alanlar = json.loads(ham_param) if ham_param.startswith("{") else {}
            if alanlar and motor._tor_browser.driver:
                sonuc = FormDoldurucu.doldur(motor._tor_browser.driver, alanlar)
                if sonuc.get("basarisiz"):
                    try:
                        from araclar_nisan import NisanBulucu
                        nisan = NisanBulucu()
                        for alan_adi in sonuc["basarisiz"]:
                            deger = alanlar.get(alan_adi, "")
                            if deger:
                                nisan_bul = nisan.bul(alan_adi, driver=motor._tor_browser.driver, metin_alternatif=deger) if motor._tor_browser.driver else nisan.bul(alan_adi, metin_alternatif=deger)
                                if nisan_bul.get("asama", 0) > 0:
                                    log.info("[Tor] Nisan asama %s ile '%s' bulundu", nisan_bul["asama"], alan_adi)
                    except Exception as ocr_e:
                        log.warning("[Tor] Nisan fallback hatasi: %s", ocr_e)
                return f"[Form] Basarili: {sonuc.get('basarili', [])}, Basarisiz: {sonuc.get('basarisiz', [])}"
            return "[Tor]: JSON formatinda alanlar gonderin."
        if arac == "TOR_LOGIN":
            data = json.loads(ham_param) if ham_param.startswith("{") else {}
            if data:
                s = motor._tor_akislar.login(data.get("url", ""), data.get("kullanici", ""), data.get("sifre", ""))
                return "[Login] Basarili." if s["basarili"] else f"[Login] Basarisiz: {s['hata']}"
            return "[Tor]: JSON gonderin."
        if arac == "TOR_KAYIT":
            try:
                from insan_arayuzu import onay_iste
                if not onay_iste("TOR_KAYIT", "Yeni uyelik olusturma talebi. Onayliyor musun?"):
                    return "[Kayit] REDDEDILDI: Kullanici onay vermedi."
            except ImportError:
                pass
            data = json.loads(ham_param) if ham_param.startswith("{") else {}
            if data:
                s = motor._tor_akislar.kayit_ol(data.get("url", ""), data.get("bilgiler", {}))
                return "[Kayit] Basarili." if s["basarili"] else f"[Kayit] Basarisiz: {s['hata']}"
            return "[Tor]: JSON gonderin."
        if arac == "TOR_SIPARIS":
            try:
                from insan_arayuzu import onay_iste
                if not onay_iste("TOR_SIPARIS", "Siparis verme talebi. Onayliyor musun?"):
                    return "[Siparis] REDDEDILDI: Kullanici onay vermedi."
            except ImportError:
                pass
            data = json.loads(ham_param) if ham_param.startswith("{") else {}
            if data:
                s = motor._tor_akislar.siparis_ver(data.get("url", ""), data.get("urun", ""), data.get("adres", {}))
                return "[Siparis] Basarili." if s["basarili"] else f"[Siparis] Basarisiz: {s['hata']}"
            return "[Tor]: JSON gonderin."
    except Exception as e:
        return f"[Hata]: tor_otomasyonu: {e}"
    return "[Hata]: Bilinmeyen tor araci."


# ── Durum ────────────────────────────────────────────────────────────────────
def durum_fallback(motor, arac: str, params: list) -> str:
    if arac == "DURUM_BILDIR":
        durum = params[0] if params else "idle"
        mesaj = params[1] if len(params) >= 2 else ""
        return f"[Durum] {durum}" + (f": {mesaj}" if mesaj else "")
    satirlar = [
        "[Durum Raporu]",
        f"  Zaman: {_time.strftime('%Y-%m-%d %H:%M:%S')}",
        "  Motor: calisiyor",
    ]
    if getattr(motor, '_provider_ref', None):
        satirlar.append("  Provider: bagli")
    else:
        satirlar.append("  Provider: bagli degil")
    from reymen.cereyan.motor.plugins import _PLUGIN_MGR
    satirlar.append(f"  Plugin: {'aktif' if _PLUGIN_MGR else 'yok'}")
    return "\n".join(satirlar)


def watchdog_calistir(motor, params: list) -> str:
    try:
        sonuc = subprocess.run(
            ["powershell.exe", "-NoProfile", "-Command",
             "Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -match 'bot\\.py' } | "
             "Select-Object ProcessId | ConvertTo-Json -Compress"],
            capture_output=True, text=True, timeout=15,
        )
        cikti = sonuc.stdout.strip()
        if cikti and cikti != "null":
            try:
                data = json.loads(cikti)
                if isinstance(data, dict):
                    data = [data]
                pidler = [str(p.get("ProcessId")) for p in data if p.get("ProcessId")]
                if pidler:
                    return f"__WATCHDOG__ Bot calisiyor. PID: {', '.join(pidler)}"
            except json.JSONDecodeError:
                pass
        _py = r"C:\Users\marko\AppData\Local\Python\PythonCore-3.14-64\python.exe"
        _bot = ROOT / "bot.py"
        subprocess.Popen(
            [_py, str(_bot)], cwd=str(ROOT),
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
        return "__WATCHDOG__ Bot calismiyordu, yeniden baslatildi."
    except Exception as e:
        return f"__WATCHDOG__ Hata: {e}"


def telegram_token_test(motor) -> str:
    import urllib.request as _ur
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    if not token:
        return "[TOKEN] TELEGRAM_BOT_TOKEN .env'de bulunamadi"
    try:
        resp = _ur.urlopen(f"https://api.telegram.org/bot{token}/getMe", timeout=10)
        data = json.loads(resp.read().decode())
        if data.get("ok"):
            bot = data["result"]
            return f"[TOKEN] ✅ {bot['first_name']} (@{bot['username']}) — gecerli"
        return f"[TOKEN] ❌ {data.get('description', 'bilinmeyen hata')}"
    except Exception as e:
        return f"[TOKEN] ❌ Baglanti hatasi: {e}"


def proxy_ayarla(motor, params: list) -> str:
    try:
        from proxy import ProxyEngine, ProxyConfig
        _proxy_engine = ProxyEngine(ProxyConfig())
        komut = (params[0] if params else "status").lower()
        if komut == "start":
            sonuc = _proxy_engine.start()
        elif komut == "stop":
            sonuc = _proxy_engine.stop()
        elif komut == "status":
            sonuc = _proxy_engine.status()
        else:
            sonuc = {"hata": f"Bilinmeyen komut: {komut}"}
        return str(sonuc)
    except Exception as e:
        return f"[Proxy] Hata: {e}"


# ── Dosya ────────────────────────────────────────────────────────────────────
def dosya_yaz(motor, params: list) -> str:
    if len(params) < 2:
        return "[Hata]: DOSYA_YAZ iki parametre ister."
    ad, icerik = params[0], params[1].replace("\\n", "\n")
    guvenli, mesaj = _dosya_guvenli(ad)
    if not guvenli:
        return f"[Guvenlik]: {mesaj}"
    gecerli, yol = _yol_dogrula(ad)
    if not gecerli:
        return f"[Guvenlik]: {yol}"
    try:
        from reymen.hermes.agent.lsp.file_operations_lsp import lsp_diagnostics_before_write, lsp_diagnostics_after_write, format_diagnostics
        lsp_diagnostics_before_write(ad)
    except ImportError:
        pass
    with open(ad, "w", encoding="utf-8") as f:
        f.write(icerik)
    lsp_notu = ""
    try:
        diags = lsp_diagnostics_after_write(ad)
        if diags:
            lsp_notu = "\n" + format_diagnostics(diags)
    except Exception:
        pass
    return f"[Tamam]: {ad} yazildi ({len(icerik)} karakter).{lsp_notu}"


def dosya_oku(motor, params: list) -> str:
    dosya = params[0] if params else ""
    if not os.path.exists(dosya):
        return f"[Hata]: {dosya} bulunamadi."
    gecerli, mesaj = _yol_dogrula(dosya)
    if not gecerli:
        return f"[Guvenlik]: {mesaj}"
    with open(dosya, "r", encoding="utf-8") as f:
        return f"[Dosya icerigi]:\n{f.read()}"


# ── Telegram ─────────────────────────────────────────────────────────────────
def telegram_araclari(motor, arac: str, params: list) -> str:
    if arac == "TELEGRAM_GONDER":
        try:
            from reymen_iletisim import iletisim_hazir, iletisim_al
            if iletisim_hazir():
                ileti = iletisim_al()
                ileti.gonder(params[0] if params else "", kanal="telegram")
                return "[TELEGRAM_GONDER]: Iletisim katmani uzerinden gonderildi."
        except Exception:
            pass
        from reymen.hermes.tools.send_message_tool import telegram_gonder
        tg = motor.config.get("telegram", {})
        return telegram_gonder(params[0] if params else "", tg.get("token", ""), tg.get("chat_id", "6328823909"))

    if arac == "TELEGRAM_STREAM_GONDER":
        try:
            from reymen.hermes.gateway.platforms.telegram import send_stream as _send_stream
            chat_id = params[1] if len(params) > 1 else os.environ.get("TELEGRAM_CHAT_ID", "6328823909")
            sonuc = _send_stream(chat_id, params[0] if params else "", parse_mode="HTML")
            if sonuc.get("durum") == "basarili":
                return f"[TELEGRAM_STREAM_GONDER]: Stream mesaj gonderildi ({sonuc.get('chunk_sayisi', 1)} chunk)"
            return f"[TELEGRAM_STREAM_GONDER]: Hata — {sonuc.get('hata', 'bilinmiyor')}"
        except Exception as e:
            return f"[TELEGRAM_STREAM_GONDER]: Hata — {e}"

    if arac == "TELEGRAM_REACTION_EKLE":
        try:
            from reymen.hermes.gateway.platforms.telegram import set_reaction as _set_reaction
            chat_id = params[1] if len(params) > 1 else os.environ.get("TELEGRAM_CHAT_ID", "6328823909")
            mesaj_id = int(params[0]) if params else 0
            emoji = params[2] if len(params) > 2 else "\U0001f44d"
            sonuc = _set_reaction(chat_id, mesaj_id, emoji)
            if sonuc.get("durum") == "basarili":
                return f"[TELEGRAM_REACTION_EKLE]: Reaction eklendi: {emoji}"
            return f"[TELEGRAM_REACTION_EKLE]: Hata — {sonuc.get('hata', 'bilinmiyor')}"
        except Exception as e:
            return f"[TELEGRAM_REACTION_EKLE]: Hata — {e}"

    if arac == "TELEGRAM_PING":
        try:
            from reymen.hermes.gateway.platforms.telegram import ping as _ping
            canli = _ping()
            return f"[TELEGRAM_PING]: {'Baglanti basarili' if canli else 'Baglanti basarisiz'}"
        except Exception as e:
            return f"[TELEGRAM_PING]: Hata — {e}"

    if arac == "TELEGRAM_RESIM_GONDER":
        from reymen.hermes.tools.send_message_tool import telegram_resim_gonder
        tg = motor.config.get("telegram", {})
        return telegram_resim_gonder(params[0] if params else "", tg.get("token", ""), tg.get("chat_id", "6328823909"))

    return "[Hata]: Bilinmeyen telegram araci."


def iletisim_araclari(motor, arac: str, params: list) -> str:
    try:
        from reymen_iletisim import iletisim_kur, iletisim_hazir, iletisim_durdur, iletisim_al
        if arac == "ILETISIM_BASLAT":
            iletisim_kur()
            return "[ILETISIM] Baslatildi." if iletisim_hazir() else "[ILETISIM] Baslatma basarisiz."
        if arac == "ILETISIM_DURDUR":
            iletisim_durdur()
            return "[ILETISIM] Durduruldu."
        if arac == "ILETISIM_DURUM":
            if not iletisim_hazir():
                return "[ILETISIM] Calismiyor."
            ileti = iletisim_al()
            return ileti.durum_text()
    except Exception as e:
        return f"[ILETISIM] Hata: {e}"
    return "[Hata]: Bilinmeyen iletisim araci."


# ── Kanban ───────────────────────────────────────────────────────────────────
def kanban_araclari(motor, arac: str, params: list) -> str:
    from ReYMeN_cli.kanban import (
        kanban_add, kanban_list, kanban_claim, kanban_complete,
        kanban_heartbeat, kanban_fail, kanban_update, kanban_move, kanban_stats,
    )
    if arac == "KANBAN_EKLE":
        return kanban_add(params[0] if len(params) > 0 else "", params[1] if len(params) > 1 else "")
    if arac == "KANBAN_LISTE":
        return kanban_list()
    if arac == "KANBAN_CLAIM":
        return kanban_claim(params[0] if len(params) > 0 else "", params[1] if len(params) > 1 else "ajan")
    if arac == "KANBAN_COMPLETE":
        return kanban_complete(params[0] if len(params) > 0 else "", params[1] if len(params) > 1 else "")
    if arac == "KANBAN_HEARTBEAT":
        return kanban_heartbeat(params[0] if len(params) > 0 else "")
    if arac == "KANBAN_FAIL":
        return kanban_fail(params[0] if len(params) > 0 else "", params[1] if len(params) > 1 else "belirtilmedi")
    if arac == "KANBAN_GUNCELLE":
        if len(params) >= 3:
            return kanban_update(params[0], params[1], params[2])
        elif len(params) >= 2:
            return kanban_move(params[0], params[1])
        return "[Kanban] KANBAN_GUNCELLE icin en az 2 parametre gerekli."
    if arac == "KANBAN_OZET":
        return kanban_stats()
    return "[Hata]: Bilinmeyen kanban araci."


# ── Ekran ────────────────────────────────────────────────────────────────────
def ekran_araclari(motor, arac: str, params: list) -> str:
    if not motor._ekran:
        from araclar_ekran import EkranOCRTikla
        motor._ekran = EkranOCRTikla()
    if arac == "EKRAN_TIKLA":
        yazi = params[0] if params else ""
        hangi = int(params[1]) if len(params) >= 2 and params[1].lstrip("-").isdigit() else 0
        return motor._ekran.yaziyi_bul_ve_tikla(yazi, hangi=hangi)
    if arac == "EKRAN_OKU":
        return motor._ekran.ekran_metnini_oku()
    if arac == "EKRAN_FOTOGRAF_CEK":
        py3 = r"C:\Users\marko\AppData\Local\Python\PythonCore-3.14-64\python.exe"
        script = os.path.join(os.path.dirname(__file__), "..", "screenshot_bot.py")
        if os.path.exists(script):
            r = subprocess.run([py3, script], capture_output=True, text=True, timeout=30)
            if r.returncode == 0:
                return "[EKRAN_FOTOGRAF_CEK]: " + r.stdout.strip()
            return f"[EKRAN_FOTOGRAF_CEK]: Hata: {r.stderr[:300]}"
        return "[EKRAN_FOTOGRAF_CEK]: screenshot_bot.py bulunamadi."
    return "[Hata]: Bilinmeyen ekran araci."


def dosya_analiz_araclari(motor, arac: str, params: list) -> str:
    from araclar_dosya_analiz import pdf_oku, excel_oku, csv_oku, goruntu_analiz, dosya_analiz
    if arac == "PDF_OKU":
        return pdf_oku(params[0] if params else "")
    if arac == "EXCEL_OKU":
        return excel_oku(params[0] if params else "", sayfa=params[1] if len(params) >= 2 else "")
    if arac == "CSV_OKU":
        return csv_oku(params[0] if params else "", ayirici=params[1] if len(params) >= 2 else ",")
    if arac == "GORUNTU_ANALIZ":
        return goruntu_analiz(params[0] if params else "", soru=params[1] if len(params) >= 2 else "")
    if arac == "DOSYA_ANALIZ":
        return dosya_analiz(params[0] if params else "", ek_parametre=params[1] if len(params) >= 2 else "")
    return "[Hata]: Bilinmeyen dosya analiz araci."


def proje_tara(motor) -> str:
    import os as _os, json as _js
    kok = _os.path.dirname(_os.path.abspath(__file__))
    py_dosyalar = []
    toplam_boyut = 0
    for kokdizini, altklasorler, dosyalar in _os.walk(kok):
        altklasorler[:] = [d for d in altklasorler if not d.startswith('.') and d != '__pycache__']
        for f in dosyalar:
            if f.endswith('.py'):
                tam = _os.path.join(kokdizini, f)
                boyut = _os.path.getsize(tam)
                py_dosyalar.append((_os.path.relpath(tam, kok), boyut))
                toplam_boyut += boyut
    py_dosyalar.sort()
    ozet = {"toplam_py": len(py_dosyalar), "toplam_boyut_kb": round(toplam_boyut / 1024, 1), "dosyalar": py_dosyalar[:100]}
    return f"[PROJE_TARA]: {_js.dumps(ozet, ensure_ascii=False, indent=2)}"


def cua_araclari(motor, arac: str, params: list) -> str:
    if not _CUA_MEVCUT:
        return "[Hata]: cua_motor_araci modulu yuklu degil."
    if arac == "CUA_EKRAN_KULLAN":
        return CUA_EKRAN_KULLAN(params[0] if params else "")
    return CUA_ARACLARI_TARA(params[0] if params else ".")


def tui_baslat(motor, params: list) -> str:
    try:
        reymentui_path = Path(__file__).parent.parent / "reymentui"
        if not reymentui_path.exists():
            return "[TUI] reymentui/ dizini bulunamadi."
        npm_script = params[0] if params else ""
        cmd = ["npm", "run", "build"] if npm_script == "build" else ["npm", "start"]
        subprocess.Popen(cmd, cwd=str(reymentui_path), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return f"[TUI] reymentui baslatildi (npm {'start' if not npm_script else npm_script})"
    except Exception as e:
        return f"[TUI] Baslatma hatasi: {e}"


def gateway_araclari(motor, arac: str, params: list) -> str:
    if arac == "GATEWAY_BASLAT":
        try:
            from reymen.hermes.gateway.run import GatewayRunner
            filtre = params[0].split(",") if params and params[0] else None
            motor._gateway_runner = GatewayRunner(polling_interval=5.0)
            threading.Thread(
                target=motor._gateway_runner.calistir,
                args=(filtre,),
                daemon=True,
                name="gateway-thread",
            ).start()
            _time.sleep(1.5)
            ozet = motor._gateway_runner.durum_ozeti()
            return f"[GATEWAY_BASLAT] Gateway baslatildi. Platform: {ozet['aktif_platform']}/{ozet['platform_sayisi']} aktif"
        except Exception as e:
            return f"[GATEWAY_BASLAT] Hata: {e}"

    if arac == "GATEWAY_DURDUR":
        if motor._gateway_runner:
            sebep = params[0] if params else "komut"
            motor._gateway_runner.durdur(sebep=sebep)
            motor._gateway_runner = None
            return "[GATEWAY_DURDUR] Gateway durduruldu."
        return "[GATEWAY_DURDUR] Gateway calismiyor."

    if arac == "GATEWAY_RESTART":
        try:
            from reymen.hermes.gateway.restart import platform_kaydet, restart_all
            from reymen.hermes.gateway.platforms import platform_listele, platform_al
            for ad in platform_listele():
                bilgi = platform_al(ad)
                if bilgi:
                    platform_kaydet(ad, bilgi.get("baslat", lambda: None), bilgi.get("durdur", lambda: None))
            bekleme = float(params[0]) if params and params[0].replace(".", "").isdigit() else 1.0
            sonuclar = restart_all(bekleme=bekleme)
            basarili = sum(1 for v in sonuclar.values() if v)
            return f"[GATEWAY_RESTART] {basarili}/{len(sonuclar)} platform yeniden baslatildi."
        except Exception as e:
            return f"[GATEWAY_RESTART] Hata: {e}"

    if arac == "GATEWAY_DURUM":
        try:
            from reymen.hermes.gateway.status import read_runtime_status
            durum = read_runtime_status()
            if not durum:
                return "[GATEWAY_DURUM] Gateway calismiyor (durum dosyasi yok)."
            satirlar = [
                "[Gateway Durumu]",
                f"  Durum: {durum.get('gateway_state', '?')}",
                f"  PID: {durum.get('pid', '?')}",
                f"  Baslangic: {durum.get('updated_at', '?')[:19]}",
            ]
            platformlar = durum.get("platforms", {})
            if platformlar:
                satirlar.append(f"  Platformlar ({len(platformlar)}):")
                for p_ad, p_bilgi in platformlar.items():
                    satirlar.append(f"    - {p_ad}: {p_bilgi.get('state', '?')}")
            if motor._gateway_runner:
                runner_ozet = motor._gateway_runner.durum_ozeti()
                satirlar.append(f"  Aktif: {runner_ozet['aktif_platform']}/{runner_ozet['platform_sayisi']}")
                satirlar.append(f"  Hata: {runner_ozet['hata_sayisi']}")
            return "\n".join(satirlar)
        except Exception as e:
            return f"[GATEWAY_DURUM] Hata: {e}"

    return "[Hata]: Bilinmeyen gateway araci."


def alt_ajan_araclari(motor, arac: str, params: list, ham_param: str = "") -> str:
    try:
        from alt_ajan import AltAjanKoordinatörü
        if motor._alt_ajan is None:
            motor._alt_ajan = AltAjanKoordinatörü()
        if arac == "ALT_AJAN_GOREVLENDIR":
            try:
                gorev_data = json.loads(ham_param) if isinstance(ham_param, str) and ham_param.strip().startswith("{") else {"hedef": ham_param}
            except json.JSONDecodeError:
                gorev_data = {"hedef": ham_param}
            hedef = gorev_data.get("hedef", ham_param)
            tip = gorev_data.get("tip", "decorator")
            return f"[ALT_AJAN] Gorev baslatildi: {motor._alt_ajan.gorevlendir(hedef, tip=tip)}"
        if arac == "ALT_AJAN_DURUM":
            durum = motor._alt_ajan.durum_raporu() if hasattr(motor._alt_ajan, "durum_raporu") else "Durum bilgisi alinamadi"
            return f"[ALT_AJAN] {durum}"
        if arac == "ALT_AJAN_IPTAL":
            motor._alt_ajan.iptal_et()
            return "[ALT_AJAN] Tum gorevler iptal edildi."
    except Exception as e:
        return f"[ALT_AJAN] Hata: {e}"
    return "[Hata]: Bilinmeyen alt_ajan araci."


# ── Dispatch fonksiyonlari (main.py calistir() tarafindan cagrilir) ─────────

def ozel_arac_calistir(motor, arac: str, ham_param: str, params: list):
    """Ozel arac kategorilerini fallback oncesi calistirir.
    None donerse normal akis (registry -> plugin -> fallback) devam eder.
    """
    if arac in ("HATA_WATCH_BASLAT", "HATA_WATCH_DURDUR", "HATA_KOD_AL",
                 "TERMINAL_HATA_PARSE", "COZUM_UYGULA"):
        return hata_cozucu_calistir(motor, arac, params)
    if arac in ("TOR_AC", "TOR_KAPAT", "TOR_FORM_DOLDUR",
                 "TOR_LOGIN", "TOR_KAYIT", "TOR_SIPARIS"):
        return tor_otomasyonu_calistir(motor, arac, ham_param, params)
    if arac == "PARALLEL_CALISTIR":
        return paralel_calistir(motor, params[0] if params else "")
    return None


def paralel_calistir(motor, tanim: str) -> str:
    """PARALLEL_CALISTIR(...) - araclari paralel calistirir."""
    import re as _re
    from concurrent.futures import ThreadPoolExecutor, as_completed
    from typing import Tuple
    cagrilar = _re.findall(r"([A-Z_]+)\s*\(((?:[^()]*|\([^()]*\))*)\)", tanim)
    if not cagrilar:
        parcalar = [p.strip() for p in tanim.split("|") if p.strip()]
        cagrilar = []
        for parca in parcalar:
            m = _re.match(r"([A-Z_]+)\s*\((.*)\)", parca.strip(), _re.DOTALL)
            if m:
                cagrilar.append((m.group(1).strip(), m.group(2).strip()))
    if not cagrilar:
        return "[PARALLEL_CALISTIR] Hicbir gecerli arac cagrisi bulunamadi."
    sonuclar = {}
    hata_sayisi = 0
    arac_timeout = int(getattr(motor, "config", {}).get("parallel_timeout", 30))
    max_isci = min(len(cagrilar), 8)
    def _cagri_yap(idx, arac_adi, ham):
        try:
            return idx, arac_adi, motor.calistir(arac_adi, ham)
        except Exception as e:
            return idx, arac_adi, f"[Hata]: {e}"
    try:
        with ThreadPoolExecutor(max_workers=max_isci) as executor:
            gelecekler = {executor.submit(_cagri_yap, i, a, h): (i, a) for i, (a, h) in enumerate(cagrilar)}
            for gelecek in as_completed(gelecekler, timeout=arac_timeout * len(cagrilar)):
                i_ref, arac_ref = gelecekler[gelecek]
                try:
                    idx, arac_adi, sonuc = gelecek.result(timeout=arac_timeout)
                except TimeoutError:
                    idx, arac_adi, sonuc = i_ref, arac_ref, f"[Hata]: {arac_ref} zaman asimi ({arac_timeout}s)."
                except Exception as _e:
                    idx, arac_adi, sonuc = i_ref, arac_ref, f"[Hata]: {_e}"
                sonuclar[idx] = (arac_adi, sonuc)
                if "[Hata]" in sonuc:
                    hata_sayisi += 1
    except TimeoutError:
        eksik = set(range(len(cagrilar))) - set(sonuclar.keys())
        for i in eksik:
            a_adi = cagrilar[i][0] if i < len(cagrilar) else "?"
            sonuclar[i] = (a_adi, "[Hata]: Zaman asimi - tamamlanamadi.")
            hata_sayisi += 1
    satirlar = [f"[PARALLEL_CALISTIR] {len(cagrilar)} arac, {hata_sayisi} hata:"]
    for i in range(len(cagrilar)):
        arac_adi, sonuc = sonuclar.get(i, ("?", "[Sonuc yok]"))
        satirlar.append(f"\n--- {arac_adi} ---\n{sonuc[:500]}")
    return "\n".join(satirlar)


def fallback_calistir(motor, arac: str, params: list) -> str:
    """Ana fallback zinciri - registry/plugin calismazsa kullanilir."""
    if arac == "KOMUT_CALISTIR":
        return motor.terminal.calistir(params[0] if params else "") if motor.terminal else "[Hata]: Terminal yok"
    if arac == "PYTHON_CALISTIR":
        try:
            from guvenli_sandbox import guvenli_calistir
            return guvenli_calistir(params[0] if params else "", timeout=30)
        except ImportError:
            pass
        if izole_python_calistir:
            return izole_python_calistir(params[0] if params else "")
        return "[Hata]: Sandbox yok"
    if arac == "GUVENLI_CALISTIR":
        try:
            from guvenli_sandbox import guvenli_calistir
            mod = params[1] if len(params) >= 2 else "oto"
            return guvenli_calistir(params[0] if params else "", mod=mod, timeout=30)
        except ImportError:
            return "[Hata]: guvenli_sandbox modulu yuklu degil."
    if arac == "ARAC_URET":
        try:
            from dinamik_arac_uretici import arac_uret_ve_calistir
            problem = params[0] if params else ""
            test_girdisi = params[1] if len(params) >= 2 else ""
            provider = getattr(motor, "_provider_ref", None)
            return arac_uret_ve_calistir(problem, motor=motor, provider=provider, test_girdisi=test_girdisi, max_deneme=2)
        except ImportError:
            return "[Hata]: dinamik_arac_uretici modulu yuklu degil."
    if arac == "GOREV_BITTI":
        try:
            from reymen.hermes.tools.achievements import check_achievements
            yeni = check_achievements(gorev_tamamlandi=True)
            if yeni:
                return "__GOREV_BITTI__\n" + "\n".join(f"{r['emoji']} {r['name']} kazanildi!" for r in yeni)
        except Exception:
            pass
        return "__GOREV_BITTI__"
    if arac in ("DURUM_BILDIR", "DURUM_RAPOR"):
        return durum_fallback(motor, arac, params)
    if arac == "WATCHDOG_KONTROL":
        return watchdog_calistir(motor, params)
    if arac == "GATEWAY_DURUM_YAZ":
        durum = params[0] if params else "running"
        hata = params[1] if len(params) >= 2 else ""
        _gateway_durum_yaz(durum, hata)
        return f"__GATEWAY_DURUM_YAZ: {durum}__"
    if arac == "TELEGRAM_TOKEN_TEST":
        return telegram_token_test(motor)
    if arac == "PROXY_AYARLA":
        return proxy_ayarla(motor, params)
    if arac == "ACHIEVEMENTS_LISTE":
        from reymen.hermes.tools.achievements import rozet_listele
        return rozet_listele()
    if arac == "DOSYA_YAZ":
        return dosya_yaz(motor, params)
    if arac == "DOSYA_OKU":
        return dosya_oku(motor, params)
    if arac == "HAFIZA_ARA":
        if motor.hafiza is None:
            return "[Hafiza]: Bagli degil."
        from vektorel_hafiza import anlamsal_hafiza_ara
        return anlamsal_hafiza_ara(motor.hafiza, params[0] if params else "")
    if arac == "WEB_ARA":
        from araclar_web import web_ara
        return web_ara(params[0] if params else "")
    if arac in ("TELEGRAM_GONDER", "TELEGRAM_STREAM_GONDER", "TELEGRAM_REACTION_EKLE", "TELEGRAM_PING", "TELEGRAM_RESIM_GONDER"):
        return telegram_araclari(motor, arac, params)
    if arac in ("ILETISIM_BASLAT", "ILETISIM_DURDUR", "ILETISIM_DURUM"):
        return iletisim_araclari(motor, arac, params)
    if arac in ("KANBAN_EKLE", "KANBAN_LISTE", "KANBAN_CLAIM", "KANBAN_COMPLETE",
                 "KANBAN_HEARTBEAT", "KANBAN_FAIL", "KANBAN_GUNCELLE", "KANBAN_OZET"):
        return kanban_araclari(motor, arac, params)
    if arac == "TARAYICI_AC":
        from araclar_tarayici import TarayiciKontrol
        return TarayiciKontrol().sayfa_ac_ve_oku(params[0] if params else "")
    if arac in ("EKRAN_TIKLA", "EKRAN_OKU", "EKRAN_FOTOGRAF_CEK"):
        return ekran_araclari(motor, arac, params)
    if arac == "MAKRO_OYNAT":
        from reymen.hermes.tools.macro import oynat
        return oynat(params[0] if params else "")
    if arac == "UYG_ISLEM_CAGIR":
        from uygulama_hafizasi import UygulamaHafizasi
        uh = UygulamaHafizasi()
        if len(params) < 2:
            return "[Hata]: UYG_ISLEM_CAGIR iki parametre ister."
        adimlar = uh.islem_cagir(params[0], params[1])
        if adimlar:
            return f"[UygHafiza]: {params[0]} - {params[1]}\n" + "\n".join(adimlar)
        return f"[UygHafiza]: '{params[1]}' kaydi yok."
    if arac in ("PDF_OKU", "EXCEL_OKU", "CSV_OKU", "GORUNTU_ANALIZ", "DOSYA_ANALIZ"):
        return dosya_analiz_araclari(motor, arac, params)
    if arac == "PROJE_TARA":
        return proje_tara(motor)
    if arac in ("CUA_EKRAN_KULLAN", "CUA_ARACLARI_TARA"):
        return cua_araclari(motor, arac, params)
    if arac == "TUI_BASLAT":
        return tui_baslat(motor, params)
    if arac in ("GATEWAY_BASLAT", "GATEWAY_DURDUR", "GATEWAY_RESTART", "GATEWAY_DURUM"):
        return gateway_araclari(motor, arac, params)
    if arac in ("ALT_AJAN_GOREVLENDIR", "ALT_AJAN_DURUM", "ALT_AJAN_IPTAL"):
        return alt_ajan_araclari(motor, arac, params, ham_param="")
    if arac == "CLARIFY":
        try:
            from reymen.hermes.tools.clarify_tool import run as clarify_run
            soru = params[0] if len(params) > 0 else ""
            sec_str = params[1] if len(params) > 1 and params[1] else ""
            varsayilan = params[2] if len(params) > 2 else ""
            secenekler = [s.strip() for s in sec_str.split("|") if s.strip()] if sec_str else None
            return clarify_run(soru=soru, secenekler=secenekler, varsayilan=varsayilan)
        except Exception as e:
            return f"[CLARIFY HATASI] {e}"
    if arac == "EXECUTE_CODE":
        try:
            from reymen.hermes.tools.execute_code_tool import run as exec_run
            kod = params[0] if len(params) > 0 else ""
            timeout = int(params[1]) if len(params) > 1 and params[1].strip().isdigit() else 30
            calisma_dizini = params[2] if len(params) > 2 else ""
            return exec_run(kod=kod, timeout=timeout, calisma_dizini=calisma_dizini)
        except Exception as e:
            return f"[EXECUTE_CODE HATASI] {e}"
    return f"[Hata]: Bilinmeyen arac '{arac}'."
