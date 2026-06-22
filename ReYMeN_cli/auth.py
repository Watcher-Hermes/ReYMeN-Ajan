# -*- coding: utf-8 -*-
"""ReYMeN_cli/auth.py — Kimlik dogrulama CLI.

Login, logout, status, list, token_refresh islemleri.
"""

import base64
import json
import os
import sys
import threading
from datetime import datetime, timezone
from pathlib import Path


class AuthError(Exception):
    """Kimlik doğrulama hatası — ReYMeN CLI uyumluluğu için."""
    pass


# ReYMeN API sabitleri — uyumluluk için
DEFAULT_NOUS_INFERENCE_URL = "https://inference-api.nousresearch.com/v1"
DEFAULT_NOUS_PORTAL_URL = "https://portal.nousresearch.com"
DEFAULT_NOUS_CLIENT_ID = "ReYMeN-cli"
NOUS_INFERENCE_INVOKE_SCOPE = "inference:invoke"
DEFAULT_NOUS_SCOPE = NOUS_INFERENCE_INVOKE_SCOPE
DEFAULT_CODEX_BASE_URL = "https://chatgpt.com/backend-api/codex"
CODEX_ACCESS_TOKEN_REFRESH_SKEW_SECONDS = 300
PROVIDER_REGISTRY = {}
DEFAULT_XAI_OAUTH_BASE_URL = "https://api.x.ai/v1"
DEFAULT_QWEN_BASE_URL = "https://portal.qwen.ai/v1"
DEFAULT_GITHUB_MODELS_BASE_URL = "https://api.githubcopilot.com"
DEFAULT_COPILOT_ACP_BASE_URL = "acp://copilot"

PROJE_KOK = Path(__file__).parent.parent

# _auth_store_lock: hem `with _auth_store_lock:` hem `with _auth_store_lock():` calismali.
# credential_pool.py `with _auth_store_lock():` seklinde kullanir (callable).
# Ic fonksiyonlar ise `with _auth_store_lock:` seklinde kullanir.
# RLock (reentrant) gerekli: ayni thread lock icinde _save_auth_store cagirir.
_auth_store_rlock = threading.RLock()


class _AuthStoreLockProxy:
    """threading.RLock'u hem dogrudan context manager hem callable olarak sunar."""

    def __call__(self):
        return _auth_store_rlock

    def __enter__(self):
        _auth_store_rlock.__enter__()
        return _auth_store_rlock

    def __exit__(self, *args):
        return _auth_store_rlock.__exit__(*args)


_auth_store_lock = _AuthStoreLockProxy()


def _token_dosyasi() -> Path:
    """Token bilgilerinin saklandigi dosya yolu."""
    return PROJE_KOK / ".ReYMeN" / "auth" / "tokens.json"


def _tokenlari_oku() -> dict:
    """Kayitli tokenlari oku."""
    dosya = _token_dosyasi()
    if not dosya.exists():
        return {}
    try:
        with open(str(dosya), "r", encoding="utf-8") as f:
            icerik = f.read().strip()
            return json.loads(icerik) if icerik else {}
    except (json.JSONDecodeError, Exception):
        return {}


def _tokenlari_yaz(tokenlar: dict):
    """Tokenlari dosyaya yaz."""
    dosya = _token_dosyasi()
    dosya.parent.mkdir(parents=True, exist_ok=True)
    with open(str(dosya), "w", encoding="utf-8") as f:
        json.dump(tokenlar, f, indent=2, ensure_ascii=False)


def kaydet(alt_parser):
    """Auth CLI alt komutlarini argparse alt ayristiricisina kaydet.

    Alt komutlar: login, logout, status, list, token_refresh
    """
    alt_parser.add_argument("islem", type=str, nargs="?",
                            choices=["login", "logout", "status", "list", "token_refresh"],
                            help="Yapilacak islem (login|logout|status|list|token_refresh)")
    alt_parser.add_argument("--provider", type=str, default=None,
                            help="Kimlik saglayici (ornek: telegram, github)")
    alt_parser.add_argument("--token", type=str, default=None,
                            help="Token degeri (login/token_refresh icin)")


def calistir(args):
    """Auth komutunu calistir."""
    try:
        islem = args.islem or "status"

        if islem == "login":
            provider = args.provider or "default"
            token = args.token
            if not token:
                print("[Auth] Lutfen --token parametresini belirtin.")
                return
            tokenlar = _tokenlari_oku()
            tokenlar[provider] = {
                "token": token,
                "giris": datetime.now().isoformat(),
                "aktif": True,
            }
            _tokenlari_yaz(tokenlar)
            print(f"[Auth] '{provider}' saglayicisina giris yapildi.")

        elif islem == "logout":
            provider = args.provider
            if not provider:
                print("[Auth] Lutfen --provider parametresini belirtin.")
                return
            tokenlar = _tokenlari_oku()
            if provider not in tokenlar:
                print(f"[Auth] '{provider}' icin aktif oturum bulunamadi.")
                return
            del tokenlar[provider]
            _tokenlari_yaz(tokenlar)
            print(f"[Auth] '{provider}' oturumu kapatildi.")

        elif islem == "status":
            tokenlar = _tokenlari_oku()
            if not tokenlar:
                print("[Auth] Aktif oturum yok.")
            else:
                print("[Auth] Aktif oturumlar:")
                for saglayici, bilgi in tokenlar.items():
                    aktif = bilgi.get("aktif", False)
                    giris = bilgi.get("giris", "?")
                    durum = "Aktif" if aktif else "Pasif"
                    print(f"  + {saglayici}: {durum} (giris: {giris})")

        elif islem == "list":
            tokenlar = _tokenlari_oku()
            if not tokenlar:
                print("[Auth] Kayitli token yok.")
            else:
                print(f"[Auth] Kayitli tokenlar ({len(tokenlar)} adet):")
                for saglayici, bilgi in tokenlar.items():
                    gizli = bilgi.get("token", "")[:8] + "..." if bilgi.get("token") else "?"
                    print(f"  + {saglayici}: {gizli}")

        elif islem == "token_refresh":
            provider = args.provider or "default"
            token = args.token
            if not token:
                print("[Auth] Lutfen --token (yeni token) parametresini belirtin.")
                return
            tokenlar = _tokenlari_oku()
            if provider not in tokenlar:
                print(f"[Auth] '{provider}' bulunamadi. Once login yapin.")
                return
            tokenlar[provider]["token"] = token
            tokenlar[provider]["giris"] = datetime.now().isoformat()
            _tokenlari_yaz(tokenlar)
            print(f"[Auth] '{provider}' tokeni yenilendi.")

    except Exception as e:
        print(f"[Auth] Beklenmeyen hata: {e}")


# ============================================================
# ReYMeN uyumluluk fonksiyonlari (agent/ modulu icin)
# ============================================================

def _decode_jwt_claims(token: str) -> dict:
    """JWT payload base64 decode et — imza dogrulama YAPMAZ."""
    if not token or "." not in token:
        return {}
    try:
        payload = token.split(".")[1]
        padding = 4 - len(payload) % 4
        if padding != 4:
            payload += "=" * padding
        return json.loads(base64.urlsafe_b64decode(payload))
    except Exception:
        return {}


def _codex_access_token_is_expiring(
    token: str,
    skew_seconds: int = CODEX_ACCESS_TOKEN_REFRESH_SKEW_SECONDS,
) -> bool:
    """Codex access token suresinin dolmak uzere olup olmadigini kontrol et."""
    claims = _decode_jwt_claims(token)
    exp = claims.get("exp")
    if not isinstance(exp, (int, float)):
        return True
    return datetime.now(timezone.utc).timestamp() + skew_seconds >= exp


AUTH_STORE_PATH = PROJE_KOK / ".ReYMeN" / "auth" / "store.json"


def _load_auth_store() -> dict:
    """Auth store JSON'u oku (caller zaten lock tutar; RLock reentrant'tir)."""
    with _auth_store_lock:
        if not AUTH_STORE_PATH.exists():
            return {}
        try:
            return json.loads(AUTH_STORE_PATH.read_text(encoding="utf-8"))
        except Exception:
            return {}


def _save_auth_store(store: dict) -> None:
    """Auth store JSON'u atomik yaz (RLock reentrant — caller lock tutabilir)."""
    with _auth_store_lock:
        AUTH_STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
        tmp = AUTH_STORE_PATH.with_suffix(".tmp")
        tmp.write_text(json.dumps(store, indent=2, ensure_ascii=False), encoding="utf-8")
        os.replace(str(tmp), str(AUTH_STORE_PATH))


def _load_provider_state(store: dict, provider: str):
    """Belirtilen provider'in state'ini store dict'ten oku."""
    return store.get("providers", {}).get(provider)


def _save_provider_state(
    store: dict,
    provider: str,
    state: dict,
    set_active: bool = True,
) -> None:
    """Provider state'ini store dict'te guncelle (SADECE bellek — caller _save_auth_store cagirir)."""
    store.setdefault("providers", {})[provider] = state
    if set_active:
        store["active_provider"] = provider


def _store_provider_state(
    store: dict,
    provider: str,
    state: dict,
    set_active: bool = True,
) -> None:
    """_save_provider_state icin uyumluluk alias'i."""
    _save_provider_state(store, provider, state, set_active=set_active)


def _resolve_kimi_base_url() -> str:
    """Kimi/Moonshot API base URL'ini dondur."""
    return "https://kimi.moonshot.cn/api"


def _resolve_zai_base_url() -> str:
    """Z.ai base URL'ini dondur."""
    return "https://api.zai.chat/v1"


CREDENTIAL_POOL_PATH = PROJE_KOK / ".ReYMeN" / "auth" / "credential_pool.json"


def read_credential_pool(provider=None):
    """Credential pool'u oku.

    provider=None → tum havuz dict'ini dondur.
    provider=str  → o provider'in listesini dondur.
    """
    with _auth_store_lock:
        if not CREDENTIAL_POOL_PATH.exists():
            return {} if provider is None else []
        try:
            data = json.loads(CREDENTIAL_POOL_PATH.read_text(encoding="utf-8"))
        except Exception:
            data = {}
    if not isinstance(data, dict):
        data = {}
    if provider is None:
        return data
    return data.get(provider, [])


def write_credential_pool(provider: str, pool: list) -> None:
    """Provider'in credential listesini credential_pool.json'a atomik yaz."""
    with _auth_store_lock:
        if CREDENTIAL_POOL_PATH.exists():
            try:
                data = json.loads(CREDENTIAL_POOL_PATH.read_text(encoding="utf-8"))
                if not isinstance(data, dict):
                    data = {}
            except Exception:
                data = {}
        else:
            data = {}
        data[provider] = pool
        CREDENTIAL_POOL_PATH.parent.mkdir(parents=True, exist_ok=True)
        tmp = CREDENTIAL_POOL_PATH.with_suffix(".tmp")
        tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        os.replace(str(tmp), str(CREDENTIAL_POOL_PATH))


CODEX_TOKENS_PATH = PROJE_KOK / ".ReYMeN" / "auth" / "codex_tokens.json"


def _read_codex_tokens() -> dict:
    """Codex token dosyasini oku (tokens, account_id iceren dict)."""
    with _auth_store_lock:
        if not CODEX_TOKENS_PATH.exists():
            return {}
        try:
            return json.loads(CODEX_TOKENS_PATH.read_text(encoding="utf-8"))
        except Exception:
            return {}


def resolve_codex_runtime_credentials(refresh_if_expiring: bool = False) -> dict:
    """Codex runtime kimlik bilgilerini coz.

    Returns:
        dict: {'api_key': str, 'base_url': str}
    """
    token_data = _read_codex_tokens()
    tokens = token_data.get("tokens") or {}
    api_key = (tokens.get("access_token") or "").strip()
    if not api_key:
        api_key = os.environ.get("OPENAI_API_KEY", "")
    if refresh_if_expiring and api_key and _codex_access_token_is_expiring(api_key):
        pass
    return {
        "api_key": api_key,
        "base_url": DEFAULT_CODEX_BASE_URL,
    }


def resolve_spotify_runtime_credentials() -> dict:
    """Spotify çalışma zamanı kimlik bilgilerini çöz.

    Önce auth store'a, sonra ortam değişkenlerine bakar.

    Returns:
        dict: {
            "access_token": str,
            "client_id": str,
            "client_secret": str,
        }
    """
    try:
        store = _load_auth_store()
        state = _load_provider_state(store, "spotify")
        if state and state.get("access_token"):
            return {
                "access_token": state.get("access_token", ""),
                "client_id": state.get("client_id", os.environ.get("SPOTIFY_CLIENT_ID", "")),
                "client_secret": state.get("client_secret", os.environ.get("SPOTIFY_CLIENT_SECRET", "")),
            }
    except Exception:
        pass

    return {
        "access_token": os.environ.get("SPOTIFY_ACCESS_TOKEN", ""),
        "client_id": os.environ.get("SPOTIFY_CLIENT_ID", ""),
        "client_secret": os.environ.get("SPOTIFY_CLIENT_SECRET", ""),
    }


def get_auth_status(provider: str) -> dict:
    """Belirtilen provider için kimlik doğrulama durumunu döndür.

    Spotify, GitHub vb. OAuth provider'ları için login durumu sorgular.
    Plugin'ler bu fonksiyonu `from ReYMeN_cli.auth import get_auth_status`
    ile içe aktarır.

    Args:
        provider: Provider adı (ör. "spotify", "github", "notion").

    Returns:
        dict: {
            "logged_in": bool,
            "provider": str,
            "account": str | None,  # kullanıcı adı/e-posta (varsa)
            "expires_at": str | None,
        }
    """
    try:
        store = _load_auth_store()
        state = _load_provider_state(store, provider)
        if not state:
            return {"logged_in": False, "provider": provider, "account": None, "expires_at": None}

        token = state.get("access_token") or state.get("api_key") or state.get("token", "")
        account = state.get("account") or state.get("email") or state.get("username")
        expires_at = state.get("expires_at") or state.get("expiry")

        logged_in = bool(token)
        return {
            "logged_in": logged_in,
            "provider": provider,
            "account": account,
            "expires_at": str(expires_at) if expires_at else None,
        }
    except Exception:
        return {"logged_in": False, "provider": provider, "account": None, "expires_at": None}


if __name__ == "__main__":
    print("[Auth] Modul testi baslatiliyor...")
    print(f"  AUTH_STORE_PATH     : {AUTH_STORE_PATH}")
    print(f"  CREDENTIAL_POOL_PATH: {CREDENTIAL_POOL_PATH}")
    print(f"  _decode_jwt_claims  : {_decode_jwt_claims('a.eyJleHAiOiAxfQ.c')}")
    print(f"  _resolve_kimi_base_url: {_resolve_kimi_base_url()}")
    print(f"  _resolve_zai_base_url : {_resolve_zai_base_url()}")
    store = {}
    _save_provider_state(store, "test", {"foo": "bar"}, set_active=False)
    assert _load_provider_state(store, "test") == {"foo": "bar"}
    _store_provider_state(store, "test2", {"x": 1}, set_active=True)
    assert store.get("active_provider") == "test2"
    print("  _save/_store_provider_state: OK")
    pool_data = read_credential_pool()
    print(f"  read_credential_pool(): {pool_data}")
    print("[Auth] Modul testi tamamlandi.")
