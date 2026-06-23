# -*- coding: utf-8 -*-
"""
windows_otomasyon.py — Vision modele gerek DUYMAYAN Windows otomasyon araçları.
subprocess + pyautogui + pyperclip (Türkçe karakter desteği dahil)

Bağımlılıklar: pip install pyautogui pyperclip pygetwindow
"""
from __future__ import annotations

import subprocess
import sys
import time
import re
import glob
import os
from pathlib import Path
from typing import Optional
import psutil

# ── Lazy imports ────────────────────────────────────────────────────────────

def _pyautogui():
    import pyautogui  # type: ignore
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0.05
    return pyautogui

def _pyperclip():
    try:
        import pyperclip  # type: ignore
        return pyperclip
    except ImportError:
        return None


# ── UYGULAMA BAŞLAT ─────────────────────────────────────────────────────────

def UYGULAMA_BASIT(uygulama: str, bekle_saniye: float = 3.0) -> str:
    """
    Uygulamayı başlatır. Yol veya kısayol adı kabul eder.
    Örnek: "tor", "notepad", "C:/path/to/app.exe"
    """
    bilinen = {
        "tor": [
            r"C:\Users\*\OneDrive\Desktop\Tor Browser\Browser\firefox.exe",
            r"C:\Users\*\Desktop\Tor Browser\Browser\firefox.exe",
            r"C:\Program Files*\Tor Browser\Browser\firefox.exe",
            r"C:\Tor Browser\Browser\firefox.exe",
        ],
        "firefox": [r"C:\Program Files*\Mozilla Firefox\firefox.exe"],
        "chrome": [r"C:\Program Files*\Google\Chrome\Application\chrome.exe"],
        "notepad": ["notepad.exe"],
        "calculator": ["calc.exe"],
        "explorer": ["explorer.exe"],
    }

    exe_yol: Optional[str] = None
    kucuk = uygulama.lower().strip()

    # Doğrudan .exe veya var olan yol
    if os.path.exists(uygulama):
        exe_yol = uygulama
    elif kucuk.endswith(".exe") or "/" in uygulama or "\\" in uygulama:
        exe_yol = uygulama
    else:
        # Bilinen uygulamalar
        for anahtar, desenler in bilinen.items():
            if anahtar in kucuk:
                for desen in desenler:
                    eslesme = glob.glob(desen)
                    if eslesme:
                        exe_yol = eslesme[0]
                        break
                if exe_yol:
                    break

    if not exe_yol:
        # Windows PATH'te ara
        try:
            sonuc = subprocess.run(["where", uygulama], capture_output=True, text=True, timeout=5)
            if sonuc.returncode == 0:
                exe_yol = sonuc.stdout.strip().split("\n")[0]
        except Exception:
            pass

    if not exe_yol:
        return f"[HATA] '{uygulama}' bulunamadı. Tam yolu belirt."

    try:
        subprocess.Popen([exe_yol], shell=False)
        if bekle_saniye > 0:
            time.sleep(bekle_saniye)
        return f"✅ Başlatıldı: {exe_yol} (beklendi: {bekle_saniye}s)"
    except Exception as e:
        return f"[HATA] Başlatılamadı: {e}"


# ── METİN YAZ (Türkçe destekli) ─────────────────────────────────────────────

def METIN_YAZ(metin: str, pano_kullan: bool = True, gecikme: float = 0.05) -> str:
    """
    Aktif pencereye metin yazar. Türkçe karakter desteği için pano kullanır.
    pano_kullan=True → pyperclip ile kopyala-yapıştır (Türkçe ü,ş,ı,ğ,ö,ç destekli)
    pano_kullan=False → pyautogui.typewrite (sadece ASCII)
    """
    pg = _pyautogui()
    time.sleep(0.2)

    if pano_kullan:
        pc = _pyperclip()
        if pc:
            try:
                pc.copy(metin)
                time.sleep(0.1)
                pg.hotkey("ctrl", "v")
                time.sleep(0.2)
                return f"✅ Yazıldı (pano): '{metin}'"
            except Exception as e:
                return f"[HATA] Pano yazma: {e}"

    # Fallback: typewrite (ASCII-only)
    try:
        pg.typewrite(metin, interval=gecikme)
        return f"✅ Yazıldı (typewrite): '{metin}'"
    except Exception as e:
        return f"[HATA] typewrite: {e}"


# ── KLAVYE TUŞU / KISA YOL ───────────────────────────────────────────────────

def KLAVYE_TUS(tuslar: str) -> str:
    """
    Klavye tuşu veya kısayol. Örnekler:
    "enter", "ctrl+l", "ctrl+a", "alt+f4", "escape", "tab", "ctrl+shift+l"
    """
    pg = _pyautogui()
    time.sleep(0.1)
    parcalar = [t.strip() for t in tuslar.lower().split("+")]
    try:
        if len(parcalar) == 1:
            pg.press(parcalar[0])
        else:
            pg.hotkey(*parcalar)
        return f"✅ Tuş: {tuslar}"
    except Exception as e:
        return f"[HATA] Tuş '{tuslar}': {e}"


# ── BEKLE ────────────────────────────────────────────────────────────────────

def BEKLE(saniye: float) -> str:
    """Belirtilen süre bekle."""
    time.sleep(saniye)
    return f"✅ {saniye}s beklendi."


# ── FARE TIKLA ───────────────────────────────────────────────────────────────

def FARE_TIKLA(x: int, y: int, cift: bool = False) -> str:
    """
    Belirtilen koordinata tıkla.
    Koordinat bilmiyorsan CUA_EKRAN_KULLAN ile bul.
    """
    pg = _pyautogui()
    try:
        pg.moveTo(x, y, duration=0.3)
        if cift:
            pg.doubleClick(x, y)
        else:
            pg.click(x, y)
        return f"✅ {'Çift t' if cift else 'T'}ıklandı: ({x}, {y})"
    except pg.FailSafeException:
        return "[HATA] FailSafe — fare köşeye gitti."
    except Exception as e:
        return f"[HATA] Tıklama: {e}"


# ── PENCERE BÜTÜNÜ ───────────────────────────────────────────────────────────

def PENCERE_GETIR(baslik_iceriyor: str) -> str:
    """
    Başlıkta aranılan metni içeren pencereyi öne getirir.
    Örnek: "Tor Browser", "Not Defteri"
    """
    try:
        import pygetwindow as gw  # type: ignore
        pencereler = gw.getWindowsWithTitle(baslik_iceriyor)
        if not pencereler:
            return f"[UYARI] '{baslik_iceriyor}' başlıklı pencere bulunamadı."
        pencere = pencereler[0]
        pencere.activate()
        time.sleep(0.3)
        return f"✅ Pencere öne getirildi: '{pencere.title}'"
    except ImportError:
        return "[UYARI] pygetwindow kurulu değil: pip install pygetwindow"
    except Exception as e:
        return f"[HATA] Pencere: {e}"


# ── SENARYO: TOR BROWSER ─────────────────────────────────────────────────────

def TOR_ARA(metin: str, bekle_tor_saniye: float = 25.0) -> str:
    """
    Tor Browser'ı açar, arama çubuğuna metni yazar, Enter'a basar.
    Tor bağlantısı için varsayılan 25 saniye bekler.
    """
    adimlar = []

    # 1. Tor'u başlat
    sonuc = UYGULAMA_BASIT("tor", bekle_saniye=2.0)
    adimlar.append(f"Başlatma: {sonuc}")
    if "[HATA]" in sonuc:
        return "\n".join(adimlar)

    # 2. Tor bağlantısı için bekle
    adimlar.append(f"Tor bağlantısı bekleniyor ({bekle_tor_saniye}s)...")
    time.sleep(bekle_tor_saniye)

    # 3. Pencereyi öne getir
    pencere_sonuc = PENCERE_GETIR("Tor Browser")
    adimlar.append(f"Pencere: {pencere_sonuc}")

    # 4. URL/arama çubuğuna odaklan (Ctrl+L)
    sonuc = KLAVYE_TUS("ctrl+l")
    adimlar.append(f"Odak: {sonuc}")
    time.sleep(0.5)

    # 5. Mevcut içeriği seç
    KLAVYE_TUS("ctrl+a")
    time.sleep(0.2)

    # 6. Metni yaz
    sonuc = METIN_YAZ(metin, pano_kullan=True)
    adimlar.append(f"Yazma: {sonuc}")
    time.sleep(0.3)

    # 7. Enter
    sonuc = KLAVYE_TUS("enter")
    adimlar.append(f"Enter: {sonuc}")

    return "\n".join(adimlar)


# ── EKRAN OKU (OCR) ──────────────────────────────────────────────────────────

def EKRAN_OKU(bolge: tuple = None, dil: str = "tur+eng") -> str:
    """
    Ekranın tamamını veya bir bölgesini OCR ile okur.
    bolge=(x, y, genislik, yukseklik) — None ise tüm ekran.
    dil: "tur+eng" (Türkçe+İngilizce), "eng" (sadece İngilizce)

    Örnek: EKRAN_OKU()  →  ekrandaki tüm metni döndürür
           EKRAN_OKU((0, 0, 800, 200))  →  sol üst bölgeyi okur
    """
    try:
        import pytesseract  # type: ignore
        from PIL import ImageGrab, Image  # type: ignore

        pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

        if bolge:
            x, y, w, h = bolge
            img = ImageGrab.grab(bbox=(x, y, x + w, y + h))
        else:
            img = ImageGrab.grab()

        metin = pytesseract.image_to_string(img, lang=dil, config="--psm 6")
        metin = metin.strip()
        if not metin:
            return "[EKRAN_OKU] Ekranda okunabilir metin bulunamadı."
        return metin
    except ImportError as e:
        return f"[HATA] OCR bağımlılığı eksik: {e}. pip install pytesseract pillow"
    except Exception as e:
        return f"[HATA] EKRAN_OKU: {e}"


def EKRAN_METIN_VAR_MI(aranan: str, bolge: tuple = None) -> str:
    """
    Ekranda belirli bir metin var mı kontrol eder.
    aranan: aranacak kelime/cümle (büyük/küçük harf duyarsız)
    Örnek: EKRAN_METIN_VAR_MI("Hata") → "VAR: 'Hata' ekranda bulundu."
    """
    okunan = EKRAN_OKU(bolge)
    if okunan.startswith("[HATA]"):
        return okunan
    if aranan.lower() in okunan.lower():
        return f"VAR: '{aranan}' ekranda bulundu."
    return f"YOK: '{aranan}' ekranda bulunamadı.\nEkrandaki metin (ilk 300 karakter):\n{okunan[:300]}"


# ── SCROLL ───────────────────────────────────────────────────────────────────

def SCROLL(yon: str = "asagi", miktar: int = 3, x: int = None, y: int = None) -> str:
    """
    Fare tekerleği ile kaydırma.
    yon: "asagi" veya "yukari"
    miktar: kaç adım (1-10 arası önerilir)
    x, y: koordinat — None ise fare neredeyse orada kaydırır

    Örnek: SCROLL("asagi", 5)   →  5 adım aşağı kaydır
           SCROLL("yukari", 3)  →  3 adım yukarı kaydır
    """
    pg = _pyautogui()
    time.sleep(0.1)
    try:
        scroll_miktari = -miktar if "asagi" in yon.lower() else miktar
        if x is not None and y is not None:
            pg.scroll(scroll_miktari, x=x, y=y)
        else:
            pg.scroll(scroll_miktari)
        return f"✅ Scroll: {yon} × {miktar}"
    except Exception as e:
        return f"[HATA] Scroll: {e}"


# ── SAĞ TIK ──────────────────────────────────────────────────────────────────

def SAG_TIK(x: int = None, y: int = None) -> str:
    """
    Sağ tık — context menü açar.
    x, y: koordinat — None ise fare neredeyse orada sağ tıklar.

    Örnek: SAG_TIK()         →  mevcut konumda sağ tık
           SAG_TIK(500, 300) →  koordinata sağ tık
    """
    pg = _pyautogui()
    time.sleep(0.1)
    try:
        if x is not None and y is not None:
            pg.moveTo(x, y, duration=0.2)
            pg.rightClick(x, y)
        else:
            pg.rightClick()
        return f"✅ Sağ tık: ({x}, {y})" if x is not None else "✅ Sağ tık: mevcut konum"
    except Exception as e:
        return f"[HATA] Sağ tık: {e}"


# ── SÜRÜKLE BIRAK ────────────────────────────────────────────────────────────

def SURUKLE_BIRAK(x1: int, y1: int, x2: int, y2: int, sure: float = 0.5) -> str:
    """
    Drag & drop: (x1,y1) noktasından (x2,y2) noktasına sürükle.
    sure: sürükleme süresi saniye (yavaş = daha güvenli)
    Örnek: SURUKLE_BIRAK(100, 200, 500, 200)  →  yatay sürükle
    """
    pg = _pyautogui()
    try:
        pg.moveTo(x1, y1, duration=0.3)
        time.sleep(0.1)
        pg.dragTo(x2, y2, duration=sure, button="left")
        time.sleep(0.2)
        return f"✅ Sürüklendi: ({x1},{y1}) → ({x2},{y2})"
    except pg.FailSafeException:
        return "[HATA] FailSafe — fare köşeye gitti."
    except Exception as e:
        return f"[HATA] Sürükle-bırak: {e}"


# ── PANO OKU ─────────────────────────────────────────────────────────────────

def PANO_OKU() -> str:
    """
    Panodan (clipboard) metin okur.
    Kullanım: bir uygulamada Ctrl+C yaptıktan sonra PANO_OKU() ile içeriği al.
    """
    pc = _pyperclip()
    if pc:
        try:
            icerik = pc.paste()
            if not icerik or not icerik.strip():
                return "[PANO_OKU] Pano boş."
            return icerik
        except Exception as e:
            return f"[HATA] Pano okuma: {e}"
    # Fallback: tkinter
    try:
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()
        icerik = root.clipboard_get()
        root.destroy()
        return icerik or "[PANO_OKU] Pano boş."
    except Exception as e:
        return f"[HATA] Pano (tkinter): {e}"


# ── EKRAN GÖRÜNTÜSÜ KAYDET ────────────────────────────────────────────────────

def EKRAN_GORUNTU_KAYDET(dosya_yolu: str = "", bolge: tuple = None) -> str:
    """
    Ekran görüntüsünü dosyaya kaydeder.
    dosya_yolu: boşsa masaüstüne ekran_YYYYMMDD_HHMMSS.png olarak kaydeder.
    bolge: (x, y, genislik, yukseklik) — None ise tüm ekran.
    """
    try:
        from PIL import ImageGrab
        import datetime, os

        if bolge:
            x, y, w, h = bolge
            img = ImageGrab.grab(bbox=(x, y, x + w, y + h))
        else:
            img = ImageGrab.grab()

        if not dosya_yolu:
            zaman = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            masaustu = os.path.join(os.path.expanduser("~"), "Desktop")
            dosya_yolu = os.path.join(masaustu, f"ekran_{zaman}.png")

        img.save(dosya_yolu)
        return f"✅ Ekran görüntüsü kaydedildi: {dosya_yolu}"
    except Exception as e:
        return f"[HATA] Ekran görüntüsü: {e}"


# ── UYGULAMA KAPAT ────────────────────────────────────────────────────────────

def UYGULAMA_KAPAT(uygulama: str, zorla: bool = False) -> str:
    """
    Uygulamayı kapatır.
    zorla=False → Alt+F4 veya pencereyi kapat (nazik)
    zorla=True  → process kill (psutil)
    uygulama: "chrome", "notepad", "chrome.exe" veya pencere başlığı
    """
    kucuk = uygulama.lower().strip()
    exe_adi = kucuk if kucuk.endswith(".exe") else kucuk + ".exe"

    if zorla:
        # Process kill
        killed = 0
        for proc in psutil.process_iter(["name", "pid"]):
            if proc.info["name"] and proc.info["name"].lower() in (kucuk, exe_adi):
                try:
                    proc.kill()
                    killed += 1
                except Exception:
                    pass
        return f"✅ {killed} process kapatıldı: {uygulama}" if killed else f"[UYARI] '{uygulama}' çalışmıyor."

    # Nazik kapat: pencereyi öne getir + Alt+F4
    try:
        import pygetwindow as gw
        pencereler = [p for p in gw.getAllWindows() if kucuk in p.title.lower()]
        if not pencereler:
            return f"[UYARI] '{uygulama}' penceresi bulunamadı."
        pencereler[0].activate()
        time.sleep(0.3)
        pg = _pyautogui()
        pg.hotkey("alt", "f4")
        time.sleep(0.5)
        return f"✅ Kapatıldı: {pencereler[0].title}"
    except Exception as e:
        return f"[HATA] Uygulama kapat: {e}"


# ── PROCESS KONTROL ───────────────────────────────────────────────────────────

def PROCESS_KONTROL(uygulama: str) -> str:
    """
    Uygulama çalışıyor mu kontrol eder.
    uygulama: "chrome", "chrome.exe", "notepad" vb.
    Çıktı: "ÇALIŞIYOR: chrome.exe (PID: 1234)" veya "ÇALIŞMIYOR: chrome"
    """
    kucuk = uygulama.lower().strip()
    exe_adi = kucuk if kucuk.endswith(".exe") else kucuk + ".exe"

    for proc in psutil.process_iter(["name", "pid"]):
        try:
            isim = proc.info["name"].lower() if proc.info["name"] else ""
            if isim in (kucuk, exe_adi) or kucuk in isim:
                return f"ÇALIŞIYOR: {proc.info['name']} (PID: {proc.info['pid']})"
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return f"ÇALIŞMIYOR: {uygulama}"


# ── BEKLE PENCERE ─────────────────────────────────────────────────────────────

def BEKLE_PENCERE(baslik: str, zaman_asimi: float = 30.0) -> str:
    """
    Belirtilen başlıklı pencere açılana kadar bekler.
    baslik: pencere başlığında aranacak metin ("Tor Browser", "Not Defteri")
    zaman_asimi: maksimum bekleme süresi saniye

    Örnek: BEKLE_PENCERE("Tor Browser", 30)
    """
    try:
        import pygetwindow as gw
        bitis = time.time() + zaman_asimi
        while time.time() < bitis:
            pencereler = [p for p in gw.getAllWindows() if baslik.lower() in p.title.lower()]
            if pencereler:
                return f"✅ Pencere açıldı: '{pencereler[0].title}'"
            time.sleep(0.5)
        return f"[ZAMAN_ASIMI] '{baslik}' penceresi {zaman_asimi}s içinde açılmadı."
    except Exception as e:
        return f"[HATA] BEKLE_PENCERE: {e}"


# ── DOSYA AÇ İLE ─────────────────────────────────────────────────────────────

def DOSYA_AC_ILE(dosya_yolu: str) -> str:
    """
    Dosyayı varsayılan programla açar.
    PDF → Acrobat/Edge, .docx → Word, .mp3 → medya oynatıcı vb.
    Örnek: DOSYA_AC_ILE("C:/Users/marko/Desktop/rapor.pdf")
    """
    import os
    try:
        if not os.path.exists(dosya_yolu):
            return f"[HATA] Dosya bulunamadı: {dosya_yolu}"
        os.startfile(dosya_yolu)
        time.sleep(1.5)
        return f"✅ Açıldı: {dosya_yolu}"
    except Exception as e:
        try:
            subprocess.Popen(["explorer", dosya_yolu])
            return f"✅ Explorer ile açıldı: {dosya_yolu}"
        except Exception as e2:
            return f"[HATA] Dosya aç: {e} | {e2}"


# ── PENCERE TAŞI / BOYUTLANDIR ────────────────────────────────────────────────

def PENCERE_TASIT(baslik: str, x: int = 100, y: int = 100,
                  genislik: int = None, yukseklik: int = None) -> str:
    """
    Pencereyi taşır ve/veya boyutlandırır.
    baslik: pencere başlığında aranacak metin
    x, y: yeni konum (piksel)
    genislik, yukseklik: None ise boyut değişmez

    Örnek: PENCERE_TASIT("Chrome", 0, 0, 1280, 720)  →  sol üste, 1280×720
    """
    try:
        import pygetwindow as gw
        pencereler = [p for p in gw.getAllWindows() if baslik.lower() in p.title.lower()]
        if not pencereler:
            return f"[UYARI] '{baslik}' penceresi bulunamadı."
        p = pencereler[0]
        p.activate()
        time.sleep(0.2)
        p.moveTo(x, y)
        if genislik and yukseklik:
            p.resizeTo(genislik, yukseklik)
        return f"✅ Taşındı: '{p.title[:40]}' → ({x},{y})" + (
            f" {genislik}×{yukseklik}" if genislik else ""
        )
    except Exception as e:
        return f"[HATA] Pencere taşı: {e}"


# ── DOSYA DİYALOĞU ───────────────────────────────────────────────────────────

def DOSYA_DLG_YAZ(dosya_yolu: str, onayla: bool = True) -> str:
    """
    Açık/Kaydet diyalog kutusuna dosya yolu yazar ve onaylar.
    Windows'un "Farklı Kaydet" / "Aç" diyaloglarında çalışır.

    dosya_yolu: tam yol (örn. "C:/Users/marko/Desktop/rapor.txt")
    onayla: True ise Enter'a basar (kaydet/aç işlemini tamamlar)

    Örnek: DOSYA_DLG_YAZ("C:/Users/marko/Desktop/rapor.docx")
    """
    pg = _pyautogui()
    pc = _pyperclip()
    time.sleep(0.3)
    try:
        # Diyalog dosya adı kutusuna odaklan (Alt+N veya direkt typing)
        # Windows standart diyalogda dosya adı kutusu genellikle aktif gelir
        if pc:
            pc.copy(dosya_yolu)
            time.sleep(0.1)
            pg.hotkey("ctrl", "a")  # mevcut içeriği seç
            time.sleep(0.1)
            pg.hotkey("ctrl", "v")  # yapıştır
        else:
            pg.typewrite(dosya_yolu, interval=0.05)

        time.sleep(0.3)
        if onayla:
            pg.press("enter")
            time.sleep(0.5)
            return f"✅ Dosya yolu girildi ve onaylandı: {dosya_yolu}"
        return f"✅ Dosya yolu girildi (onay bekleniyor): {dosya_yolu}"
    except Exception as e:
        return f"[HATA] Dosya diyaloğu: {e}"


# ── MOTOR KAYDI ──────────────────────────────────────────────────────────────

def motor_kaydet(motor: object) -> None:
    if not hasattr(motor, "_plugin_arac_kaydet"):
        return

    motor._plugin_arac_kaydet(
        "UYGULAMA_BASIT",
        lambda uygulama="", bekle_saniye=3.0: UYGULAMA_BASIT(uygulama, bekle_saniye),
        "Uygulamayı başlatır. 'tor', 'notepad', 'chrome' veya tam .exe yolu."
    )
    motor._plugin_arac_kaydet(
        "METIN_YAZ",
        lambda metin="", pano_kullan=True: METIN_YAZ(metin, pano_kullan),
        "Aktif pencereye metin yazar. Türkçe karakter için pano_kullan=True."
    )
    motor._plugin_arac_kaydet(
        "KLAVYE_TUS",
        lambda tuslar="": KLAVYE_TUS(tuslar),
        "Klavye tuşu veya kısayol. Örnek: 'enter', 'ctrl+l', 'ctrl+a'."
    )
    motor._plugin_arac_kaydet(
        "BEKLE",
        lambda saniye=1.0: BEKLE(saniye),
        "Belirtilen saniye kadar bekler."
    )
    motor._plugin_arac_kaydet(
        "FARE_TIKLA",
        lambda x=0, y=0, cift=False: FARE_TIKLA(x, y, cift),
        "Koordinata tıklar. x,y piksel koordinatı."
    )
    motor._plugin_arac_kaydet(
        "PENCERE_GETIR",
        lambda baslik_iceriyor="": PENCERE_GETIR(baslik_iceriyor),
        "Başlıkta belirtilen pencereyi öne getirir."
    )
    motor._plugin_arac_kaydet(
        "TOR_ARA",
        lambda metin="", bekle_tor_saniye=25.0: TOR_ARA(metin, bekle_tor_saniye),
        "Tor Browser açar, metni arama çubuğuna yazar, Enter basar."
    )
    motor._plugin_arac_kaydet(
        "EKRAN_OKU",
        lambda bolge=None, dil="tur+eng": EKRAN_OKU(bolge, dil),
        "Ekranı OCR ile okur. bolge=(x,y,w,h) veya None=tüm ekran. Türkçe+İngilizce destekli."
    )
    motor._plugin_arac_kaydet(
        "EKRAN_METIN_VAR_MI",
        lambda aranan="", bolge=None: EKRAN_METIN_VAR_MI(aranan, bolge),
        "Ekranda belirli bir metin var mı kontrol eder. 'Hata', 'OK', 'Başarılı' gibi."
    )
    motor._plugin_arac_kaydet(
        "SCROLL",
        lambda yon="asagi", miktar=3, x=None, y=None: SCROLL(yon, miktar, x, y),
        "Fare tekerleği ile kaydırır. yon='asagi'/'yukari', miktar=1-10."
    )
    motor._plugin_arac_kaydet(
        "SAG_TIK",
        lambda x=None, y=None: SAG_TIK(x, y),
        "Sağ tık yapar, context menü açar. x,y koordinat (None=mevcut konum)."
    )
    motor._plugin_arac_kaydet(
        "DOSYA_DLG_YAZ",
        lambda dosya_yolu="", onayla=True: DOSYA_DLG_YAZ(dosya_yolu, onayla),
        "Açık/Kaydet diyalog kutusuna dosya yolu yazar. onayla=True ise Enter basar."
    )
    motor._plugin_arac_kaydet(
        "SURUKLE_BIRAK",
        lambda x1=0, y1=0, x2=0, y2=0, sure=0.5: SURUKLE_BIRAK(x1, y1, x2, y2, sure),
        "Drag & drop: (x1,y1)'den (x2,y2)'ye sürükle. Dosya taşıma, slider vb."
    )
    motor._plugin_arac_kaydet(
        "PANO_OKU",
        lambda: PANO_OKU(),
        "Panodan (clipboard) metin okur. Uygulamadan Ctrl+C sonrası kullan."
    )
    motor._plugin_arac_kaydet(
        "EKRAN_GORUNTU_KAYDET",
        lambda dosya_yolu="", bolge=None: EKRAN_GORUNTU_KAYDET(dosya_yolu, bolge),
        "Ekran görüntüsünü dosyaya kaydeder. dosya_yolu boşsa masaüstüne kaydeder."
    )
    motor._plugin_arac_kaydet(
        "UYGULAMA_KAPAT",
        lambda uygulama="", zorla=False: UYGULAMA_KAPAT(uygulama, zorla),
        "Uygulamayı kapatır. uygulama='chrome', 'notepad' veya .exe adı. zorla=True → process kill."
    )
    motor._plugin_arac_kaydet(
        "PROCESS_KONTROL",
        lambda uygulama="": PROCESS_KONTROL(uygulama),
        "Uygulama çalışıyor mu kontrol eder. uygulama='chrome.exe' veya 'chrome'."
    )
    motor._plugin_arac_kaydet(
        "BEKLE_PENCERE",
        lambda baslik="", zaman_asimi=30.0: BEKLE_PENCERE(baslik, zaman_asimi),
        "Belirtilen başlıklı pencere açılana kadar bekler. zaman_asimi saniye."
    )
    motor._plugin_arac_kaydet(
        "DOSYA_AC_ILE",
        lambda dosya_yolu="": DOSYA_AC_ILE(dosya_yolu),
        "Dosyayı varsayılan programla açar. PDF→Acrobat, .docx→Word vb."
    )
    motor._plugin_arac_kaydet(
        "PENCERE_TASIT",
        lambda baslik="", x=100, y=100, genislik=None, yukseklik=None: PENCERE_TASIT(baslik, x, y, genislik, yukseklik),
        "Pencereyi taşır ve/veya boyutlandırır. baslik ile pencere seç."
    )
