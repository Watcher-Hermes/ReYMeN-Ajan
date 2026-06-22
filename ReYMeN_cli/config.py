# -*- coding: utf-8 -*-
"""ReYMeN_cli/config.py — Config yonetimi CLI.

Yapilandirma ayarlarini goruntuleme, degistirme, listeleme,
iceri/disi aktarma islemleri.
"""

import json
import os
import re
import sys
from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent

# Default configuration used by the CLI and cron scheduler.
DEFAULT_CONFIG = {
    "auxiliary": {
        "monitor": {
            "provider": "auto",
        }
    },
    "agent": {
        "disabled_toolsets": [],
    },
}


def _normalize_root_model_keys(cfg: dict) -> dict:
    """Normalise old-style config keys ('model' as string/dict) to new.

    Handles:
      - model: string -> {default: string}
      - model: {model: ...} -> {default: ...}
    """
    if not isinstance(cfg, dict):
        return cfg
    result = dict(cfg)
    if "model" in result:
        m = result["model"]
        if isinstance(m, str):
            result["model"] = {"default": m}
        elif isinstance(m, dict) and "model" in m and "default" not in m:
            m["default"] = m.pop("model")
    return result


def print_config_warnings(warnings: list[str]) -> None:
    """Print configuration warnings in a standard format."""
    for w in warnings:
        print(f"[Config] Warning: {w}")


def _expand_env_vars(cfg):
    """Expand ``${VAR}`` references in config dict/list/string values.

    Unresolved references are kept verbatim so callers can detect them.
    """
    if isinstance(cfg, dict):
        return {k: _expand_env_vars(v) for k, v in cfg.items()}
    if isinstance(cfg, list):
        return [_expand_env_vars(item) for item in cfg]
    if isinstance(cfg, str):
        def _replace(m):
            return os.environ.get(m.group(1), m.group(0))
        return re.sub(r'\$\{([^}]+)\}', _replace, cfg)
    return cfg


def get_ReYMeN_home() -> Path:
    """ReYMeN ana dizini döndür — ReYMeN CLI uyumluluğu."""
    override = os.environ.get("ReYMeN_HOME")
    if override:
        return Path(override)
    return Path.home() / ".ReYMeN"


def load_env() -> dict:
    """.env dosyasini oku, dict olarak dondur (ReYMeN uyumluluk)."""
    env_yolu = PROJE_KOK / ".env"
    sonuc = {}
    if not env_yolu.exists():
        return sonuc
    with open(str(env_yolu), "r", encoding="utf-8") as f:
        for satir in f:
            s = satir.strip()
            if s.startswith("#") or "=" not in s:
                continue
            k, v = s.split("=", 1)
            sonuc[k.strip()] = v.strip().strip("\"'")
    return sonuc


def load_config() -> dict:
    """Config dosyasini oku (ReYMeN uyumluluk)."""
    return {"env": load_env(), "ReYMeN_home": str(get_ReYMeN_home())}


def save_config(cfg: dict, path: str = "") -> bool:
    """Config dosyasina yaz — upstream Hermes uyumluluk katmani.

    Args:
        cfg: Kaydedilecek config dict
        path: Kayit yolu (opsiyonel)

    Returns:
        bool: Basarili mi
    """
    try:
        if not path:
            path = str(get_ReYMeN_home() / "config.json")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2, ensure_ascii=False)
        return True
    except Exception:
        return False


def cfg_get(cfg: dict, *keys: str, default=None):
    """Config'ten ic ice anahtar oku (ReYMeN uyumluluk)."""
    for k in keys:
        try:
            cfg = cfg[k]
        except (KeyError, TypeError, IndexError):
            return default
    return cfg


def read_raw_config() -> dict:
    """Ham config dosyasını oku — ReYMeN CLI uyumluluğu."""
    config_yolu = get_ReYMeN_home() / "config.json"
    if config_yolu.exists():
        try:
            with open(str(config_yolu), encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def _env_oku(anahtar: str, varsayilan: str = "") -> str:
    """.env dosyasindan anahtar degerini oku."""
    env_yolu = PROJE_KOK / ".env"
    if not env_yolu.exists():
        return varsayilan
    with open(str(env_yolu), "r", encoding="utf-8") as f:
        for satir in f:
            satir_stripped = satir.strip()
            if satir_stripped.startswith("#") or "=" not in satir_stripped:
                continue
            k, v = satir_stripped.split("=", 1)
            if k.strip() == anahtar:
                return v.strip().strip('"').strip("'")
    return varsayilan


def _env_yaz(anahtar: str, deger: str) -> bool:
    """.env dosyasina anahtar=deger yaz."""
    env_yolu = PROJE_KOK / ".env"
    satirlar = []
    bulundu = False
    if env_yolu.exists():
        with open(str(env_yolu), "r", encoding="utf-8") as f:
            for satir in f:
                satir_stripped = satir.strip()
                if satir_stripped.startswith("#") or "=" not in satir_stripped:
                    satirlar.append(satir)
                    continue
                k, v = satir_stripped.split("=", 1)
                if k.strip() == anahtar:
                    satirlar.append(f"{anahtar}={deger}\n")
                    bulundu = True
                else:
                    satirlar.append(satir)
    if not bulundu:
        satirlar.append(f"{anahtar}={deger}\n")
    with open(str(env_yolu), "w", encoding="utf-8") as f:
        f.writelines(satirlar)
    return True


# ── Upstream Hermes-compatible env helpers ─────────────────────────────

_invalidated = False


def invalidate_env_cache() -> None:
    """Env cache'ini sifirla — upstream Hermes uyumluluk."""
    global _invalidated
    _invalidated = True


def get_env_value(key: str, default: str = "") -> str:
    """.env'den anahtar degerini oku (upstream Hermes uyumluluk)."""
    return _env_oku(key, default)


def save_env_value(key: str, value: str) -> bool:
    """.env'ye anahtar=deger yaz (upstream Hermes uyumluluk)."""
    return _env_yaz(key, value)


def kaydet(alt_parser):
    """Config CLI alt komutlarini argparse alt ayristiricisina kaydet.

    Alt komutlar: get, set, list, import, export
    """
    alt_parser.add_argument("islem", type=str, nargs="?",
                            choices=["get", "set", "list", "import", "export"],
                            help="Yapilacak islem (get|set|list|import|export)")
    alt_parser.add_argument("--key", type=str, default=None,
                            help="Config anahtari")
    alt_parser.add_argument("--value", type=str, default=None,
                            help="Config degeri")
    alt_parser.add_argument("--file", type=str, default=None,
                            help="Dis dosya yolu (import/export)")


def calistir(args):
    """Config komutunu calistir."""
    try:
        islem = args.islem or "list"

        if islem == "get":
            key = args.key
            if not key:
                print("[Config] Lutfen --key parametresini belirtin.")
                return
            deger = _env_oku(key, None)
            if deger is not None:
                hassas = any(h in key.upper() for h in ["API_KEY", "TOKEN", "SECRET", "PASSWORD"])
                if hassas and deger:
                    deger = deger[:4] + "*" * (len(deger) - 4) if len(deger) > 4 else "***"
                print(f"[Config] {key} = {deger}")
            else:
                print(f"[Config] {key} bulunamadi.")

        elif islem == "set":
            key = args.key
            value = args.value
            if not key or value is None:
                print("[Config] Lutfen --key ve --value parametrelerini belirtin.")
                return
            _env_yaz(str(key), str(value))
            print(f"[Config] {key} = {value} olarak ayarlandi.")

        elif islem == "list":
            env_yolu = PROJE_KOK / ".env"
            if not env_yolu.exists():
                print("[Config] .env dosyasi bulunamadi.")
                return
            hassas_anahtarlar = ["API_KEY", "TOKEN", "SECRET", "PASSWORD"]
            print(f"[Config] Yapilandirma ayarlari:")
            with open(str(env_yolu), "r", encoding="utf-8") as f:
                for satir in f:
                    satir_stripped = satir.strip()
                    if not satir_stripped or satir_stripped.startswith("#"):
                        continue
                    if "=" in satir_stripped:
                        k, v = satir_stripped.split("=", 1)
                        gizli = any(h in k.upper() for h in hassas_anahtarlar)
                        goruntu = (v[:4] + "****") if gizli and v else (v or "(bos)")
                        print(f"  {k.strip()} = {goruntu}")

        elif islem == "export":
            cikti_yolu = args.file or str(PROJE_KOK / "config_export.json")
            env_yolu = PROJE_KOK / ".env"
            config_data = {}
            if env_yolu.exists():
                with open(str(env_yolu), "r", encoding="utf-8") as f:
                    for satir in f:
                        satir_stripped = satir.strip()
                        if satir_stripped.startswith("#") or "=" not in satir_stripped:
                            continue
                        k, v = satir_stripped.split("=", 1)
                        config_data[k.strip()] = v.strip().strip('"').strip("'")
            with open(cikti_yolu, "w", encoding="utf-8") as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            print(f"[Config] Ayarlar export edildi: {cikti_yolu}")

        elif islem == "import":
            kaynak = args.file
            if not kaynak:
                print("[Config] Lutfen --file parametresini belirtin.")
                return
            if not os.path.exists(kaynak):
                print(f"[Config] Dosya bulunamadi: {kaynak}")
                return
            with open(kaynak, "r", encoding="utf-8") as f:
                config_data = json.load(f)
            sayac = 0
            for k, v in config_data.items():
                _env_yaz(str(k), str(v))
                sayac += 1
            print(f"[Config] {sayac} ayar import edildi: {kaynak}")

    except Exception as e:
        print(f"[Config] Beklenmeyen hata: {e}")
