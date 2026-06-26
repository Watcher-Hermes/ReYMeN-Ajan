"""motor/providers.py — Provider yönetimi (setup.json, .env, test, değiştirme)."""
import json
import os
import time
import logging

import requests

from reymen.cereyan.motor.config import (
    ROOT, PROVIDER_ENV, PROVIDER_TEST_MAP, PROVIDER_URL,
    VARSAYILAN_MODELLER, GECERLI_PROVIDERLER,
)

log = logging.getLogger("motor")


def setup_oku() -> dict:
    """.ReYMeN/setup.json dosyasını oku. Yoksa varsayılan döndür."""
    setup_yolu = ROOT / ".ReYMeN" / "setup.json"
    try:
        if setup_yolu.exists():
            with open(setup_yolu, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return {"tercih_provider": "deepseek", "tercih_model": "deepseek-v4-flash"}


def tum_providerlar_listele() -> list[dict]:
    """Tüm olası provider'ları ve durumlarını listele."""
    sonuc = []
    setup = setup_oku()
    aktif_provider = setup.get("tercih_provider", "deepseek")

    for ad in GECERLI_PROVIDERLER:
        env_key = PROVIDER_ENV.get(ad, "")
        key_mevcut = bool(env_key and os.environ.get(env_key))
        aktif = ad == aktif_provider
        durum = "bilinmiyor"
        try:
            if key_mevcut or not env_key:
                r = requests.get(f"{PROVIDER_URL.get(ad, '')}/models", timeout=5)
                durum = "acik" if r.status_code == 200 else f"HTTP {r.status_code}"
            else:
                durum = "anahtar yok"
        except requests.ConnectionError:
            durum = "kapali"
        except Exception:
            durum = "hata"
        sonuc.append({
            "ad": ad,
            "model": VARSAYILAN_MODELLER.get(ad, ""),
            "aktif": aktif, "durum": durum,
            "anahtar_var": key_mevcut,
            "url": PROVIDER_URL.get(ad, ""),
        })
    return sonuc


def provider_test_et(provider_adi: str) -> dict:
    """Belirtilen provider'ı test et."""
    if provider_adi not in PROVIDER_TEST_MAP:
        return {"success": False, "error": f"Bilinmeyen provider: {provider_adi}"}
    env_key, url, model = PROVIDER_TEST_MAP[provider_adi]
    api_key = os.environ.get(env_key, "") if env_key else ""
    if env_key and not api_key:
        return {"success": False, "error": f"{env_key} .env'de tanimli degil."}
    basla = time.time()
    try:
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        payload = {"model": model, "messages": [{"role": "user", "content": "test"}], "max_tokens": 5}
        r = requests.post(url, json=payload, headers=headers, timeout=10)
        sure = round((time.time() - basla) * 1000)
        if r.status_code == 200:
            return {"success": True, "model": model, "latency_ms": sure, "provider": provider_adi}
        return {"success": False, "error": f"HTTP {r.status_code}: {r.text[:200]}", "latency_ms": sure}
    except requests.ConnectionError:
        return {"success": False, "error": f"Baglanti reddedildi: {url}"}
    except requests.Timeout:
        return {"success": False, "error": "Zaman asimi (10sn)"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def provider_degistir(provider_adi: str, model: str = "") -> dict:
    """Aktif provider'ı değiştir (setup.json)."""
    if provider_adi not in GECERLI_PROVIDERLER:
        return {"success": False, "error": f"Gecersiz provider. Secenekler: {GECERLI_PROVIDERLER}"}
    yeni_model = model or VARSAYILAN_MODELLER.get(provider_adi, "")
    if not yeni_model:
        return {"success": False, "error": "Model adi gerekli."}
    setup_yolu = ROOT / ".ReYMeN" / "setup.json"
    try:
        with open(setup_yolu, "w", encoding="utf-8") as f:
            json.dump({"tercih_provider": provider_adi, "tercih_model": yeni_model, "SETUP_COMPLETED": True}, f, indent=2)
    except Exception as e:
        return {"success": False, "error": f"setup.json yazilamadi: {e}"}
    return {"success": True, "provider": provider_adi, "model": yeni_model,
            "mesaj": f"Provider '{provider_adi}' / model '{yeni_model}' olarak degistirildi."}


def provider_degistir_basit(saglayici: str, model: str = "") -> dict:
    """Module-level provider değiştirme (setup.json parent/ altında)."""
    saglayici = saglayici.strip().lower()
    if saglayici not in GECERLI_PROVIDERLER:
        return {"durum": "hata", "mesaj": f"Gecersiz provider: {saglayici}"}
    tercih_dosyasi = ROOT.parent / "setup.json"
    try:
        if tercih_dosyasi.exists():
            with open(tercih_dosyasi, "r", encoding="utf-8") as f:
                setup = json.load(f)
        else:
            setup = {}
        setup["tercih_provider"] = saglayici
        if model:
            setup["tercih_model"] = model
        with open(tercih_dosyasi, "w", encoding="utf-8") as f:
            json.dump(setup, f, indent=2, ensure_ascii=False)
        log.info("Provider degisti: %s / %s", saglayici, model or "(varsayilan)")
        return {"durum": "basarili", "mesaj": f"Provider {saglayici} aktif edildi." + (f" Model: {model}" if model else "")}
    except Exception as e:
        return {"durum": "hata", "mesaj": str(e)}
