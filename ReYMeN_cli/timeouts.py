# -*- coding: utf-8 -*-
"""ReYMeN_cli/timeouts.py — Zaman asimi CLI.

List, set, get, reset, test islemleri.
"""

import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

try:
    import yaml as _yaml
except ImportError:
    _yaml = None  # type: ignore[assignment]

PROJE_KOK = Path(__file__).parent.parent


def _load_config_yaml() -> dict:
    """ReYMeN_HOME/config.yaml dosyasini oku; hata veya yoksa bos dict donder."""
    if _yaml is None:
        return {}
    home = os.environ.get("ReYMeN_HOME") or str(PROJE_KOK)
    cfg_path = Path(home) / "config.yaml"
    if not cfg_path.exists():
        return {}
    try:
        with open(str(cfg_path), "r", encoding="utf-8") as fh:
            return _yaml.safe_load(fh) or {}
    except Exception:
        return {}


def _positive_float(value) -> Optional[float]:
    """Deger pozitif sayiysa float dondur, degilse None."""
    try:
        v = float(value)
        return v if v > 0 else None
    except (TypeError, ValueError):
        return None


def get_provider_request_timeout(
    provider: str, model: Optional[str] = None
) -> Optional[float]:
    """config.yaml'dan provider/model icin request_timeout_seconds oku.

    Once model seviyesinde timeout_seconds, sonra provider seviyesinde
    request_timeout_seconds dener. Bulamazsa veya gecersizse None doner.
    """
    cfg = _load_config_yaml()
    providers = cfg.get("providers") or {}
    p_cfg = providers.get(provider) or {}

    if model:
        model_cfg = (p_cfg.get("models") or {}).get(model) or {}
        result = _positive_float(model_cfg.get("timeout_seconds"))
        if result is not None:
            return result

    return _positive_float(p_cfg.get("request_timeout_seconds"))


def get_provider_stale_timeout(
    provider: str, model: Optional[str] = None
) -> Optional[float]:
    """config.yaml'dan provider/model icin stale_timeout_seconds oku.

    Once model seviyesinde stale_timeout_seconds, sonra provider seviyesinde
    dener. Bulamazsa veya gecersizse None doner.
    """
    cfg = _load_config_yaml()
    providers = cfg.get("providers") or {}
    p_cfg = providers.get(provider) or {}

    if model:
        model_cfg = (p_cfg.get("models") or {}).get(model) or {}
        result = _positive_float(model_cfg.get("stale_timeout_seconds"))
        if result is not None:
            return result

    return _positive_float(p_cfg.get("stale_timeout_seconds"))


def _timeout_dosyasi() -> Path:
    """Timeout konfigurasyon dosyasi."""
    return PROJE_KOK / ".ReYMeN" / "timeouts" / "timeouts.json"


def _timeoutlari_oku() -> dict:
    """Timeout ayarlarini oku."""
    dosya = _timeout_dosyasi()
    if not dosya.exists():
        return {"varsayilan": 30, "ozel": {}}
    try:
        with open(str(dosya), "r", encoding="utf-8") as f:
            icerik = f.read().strip()
            return json.loads(icerik) if icerik else {"varsayilan": 30, "ozel": {}}
    except (json.JSONDecodeError, Exception):
        return {"varsayilan": 30, "ozel": {}}


def _timeoutlari_yaz(veri: dict):
    """Timeout ayarlarini yaz."""
    dosya = _timeout_dosyasi()
    dosya.parent.mkdir(parents=True, exist_ok=True)
    with open(str(dosya), "w", encoding="utf-8") as f:
        json.dump(veri, f, indent=2, ensure_ascii=False)


def kaydet(alt_parser):
    """Timeouts CLI alt komutlarini argparse alt ayristiricisina kaydet.

    Alt komutlar: list, set, get, reset, test
    """
    alt_parser.add_argument("islem", type=str, nargs="?",
                            choices=["list", "set", "get", "reset", "test"],
                            help="Yapilacak islem (list|set|get|reset|test)")
    alt_parser.add_argument("--name", type=str, default=None,
                            help="Islem adi")
    alt_parser.add_argument("--value", type=int, default=None,
                            help="Timeout degeri (saniye)")


def calistir(args):
    """Timeouts komutunu calistir."""
    try:
        islem = args.islem or "list"

        if islem == "list":
            timeouts = _timeoutlari_oku()
            print("[Timeouts] Zaman asimi ayarlari:")
            print(f"  + Varsayilan: {timeouts.get('varsayilan', 30)}s")
            ozel = timeouts.get("ozel", {})
            if ozel:
                print(f"  + Ozel ayarlar ({len(ozel)} adet):")
                for ad, sure in sorted(ozel.items()):
                    print(f"    - {ad}: {sure}s")

        elif islem == "set":
            name = args.name
            value = args.value
            if not name or value is None:
                print("[Timeouts] Lutfen --name ve --value parametrelerini belirtin.")
                return
            timeouts = _timeoutlari_oku()
            if name == "varsayilan":
                timeouts["varsayilan"] = value
            else:
                if "ozel" not in timeouts:
                    timeouts["ozel"] = {}
                timeouts["ozel"][name] = value
            _timeoutlari_yaz(timeouts)
            print(f"[Timeouts] '{name}' timeoutu: {value}s")

        elif islem == "get":
            name = args.name
            if not name:
                print("[Timeouts] Lutfen --name parametresini belirtin.")
                return
            timeouts = _timeoutlari_oku()
            if name == "varsayilan":
                print(f"[Timeouts] Varsayilan: {timeouts.get('varsayilan', 30)}s")
            elif name in timeouts.get("ozel", {}):
                print(f"[Timeouts] '{name}': {timeouts['ozel'][name]}s")
            else:
                print(f"[Timeouts] '{name}' icin ozel timeout yok, varsayilan: {timeouts.get('varsayilan', 30)}s")

        elif islem == "reset":
            timeouts = _timeoutlari_oku()
            timeouts["varsayilan"] = 30
            timeouts["ozel"] = {}
            _timeoutlari_yaz(timeouts)
            print("[Timeouts] Tum timeoutlar sifirlandi (varsayilan: 30s).")

        elif islem == "test":
            sure = args.value or 1
            print(f"[Timeouts] {sure}s timeout testi basliyor...")
            basla = time.time()
            time.sleep(min(sure, 3))
            gecen = time.time() - basla
            print(f"[Timeouts] Test tamam: {gecen:.2f}s gecti.")

    except Exception as e:
        print(f"[Timeouts] Beklenmeyen hata: {e}")
