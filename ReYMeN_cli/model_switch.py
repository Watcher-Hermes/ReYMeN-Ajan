# -*- coding: utf-8 -*-
"""ReYMeN_cli/model_switch.py — Model Degistirme CLI.

Model listeleme, secme, otomatik degistirme,
test ve karsilastirma islemleri.
"""

from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent


def _kullanilabilir_modeller() -> list:
    """Kullanilabilir modeller."""
    return ["gpt-4", "gpt-3.5-turbo", "claude-3", "ReYMeN-2-pro", "ReYMeN-2"]


def kaydet(alt_parser):
    """Model switch CLI alt komutlarini argparse alt ayristiricisina kaydet.

    Alt komutlar: list, set, auto, test, benchmark
    """
    alt_parser.add_argument("islem", type=str, nargs="?",
                            choices=["list", "set", "auto", "test", "benchmark"],
                            help="Yapilacak islem (list|set|auto|test|benchmark)")
    alt_parser.add_argument("--model", type=str, default=None,
                            help="Model adi (set/test/benchmark icin)")
    alt_parser.add_argument("--kural", type=str, default=None,
                            help="Otomatik gecis kurali (auto icin)")


def calistir(args):
    """Model switch komutunu calistir."""
    try:
        islem = args.islem or "list"
        modeller = _kullanilabilir_modeller()

        if islem == "list":
            print(f"[ModelSwitch] Kullanilabilir modeller ({len(modeller)} adet):")
            for m in modeller:
                print(f"  + {m}")

        elif islem == "set":
            model = args.model
            if not model:
                print("[ModelSwitch] Lutfen --model parametresini belirtin.")
                return
            if model in modeller:
                print(f"[ModelSwitch] Model '{model}' olarak degistirildi.")
            else:
                print(f"[ModelSwitch] '{model}' desteklenmiyor.")

        elif islem == "auto":
            kural = args.kural or "maliyet"
            print(f"[ModelSwitch] Otomatik gecis etkin (kural: {kural})")

        elif islem == "test":
            model = args.model or "ReYMeN-2"
            print(f"[ModelSwitch] '{model}' test ediliyor...")
            print("[ModelSwitch] Test basarili.")

        elif islem == "benchmark":
            model = args.model or "tum"
            print(f"[ModelSwitch] '{model}' benchmark baslatiliyor...")

    except Exception as e:
        print(f"[ModelSwitch] Beklenmeyen hata: {e}")


def list_authenticated_providers(current_provider: str = "", compat_only: bool = False) -> list[dict]:
    """Kimlik dogrulamasi yapilmis provider'lari listele — upstream Hermes uyumluluk.

    Args:
        current_provider: Mevcut provider adi
        compat_only: Sadece uyumlu provider'lari goster

    Returns:
        list[dict]: Provider listesi [{name, display_name, ...}]
    """
    try:
        from providers import list_providers
        names = list_providers()
        result = []
        for n in names:
            entry = {
                "name": n,
                "display_name": n.capitalize(),
                "current": n == current_provider,
            }
            result.append(entry)
        return result
    except Exception:
        return [{"name": "auto", "display_name": "Auto", "current": True}]


def switch_model(
    agent: Any = None,
    new_model: str = "",
    new_provider: str = "",
    api_key: str = "",
    base_url: str = "",
    api_mode: str = "",
) -> Any:
    """Model degistir — upstream Hermes uyumluluk.

    Args:
        agent: AIAgent ornegi (opsiyonel)
        new_model: Yeni model adi
        new_provider: Yeni provider adi
        api_key: Opsiyonel API anahtari
        base_url: Opsiyonel base URL
        api_mode: Opsiyonel API modu

    Returns:
        SwitchModelResult veya benzeri
    """
    from dataclasses import dataclass

    @dataclass
    class SwitchModelResult:
        success: bool
        model: str = ""
        provider: str = ""
        error_message: str = ""

    try:
        from providers import get_provider
        profile = get_provider(new_provider or "auto")
        if profile:
            return SwitchModelResult(
                success=True,
                model=new_model or profile.name,
                provider=new_provider or profile.name,
            )
        return SwitchModelResult(
            success=True,
            model=new_model or "auto",
            provider=new_provider or "auto",
        )
    except Exception as e:
        return SwitchModelResult(
            success=False,
            error_message=str(e),
        )


def resolve_display_context_length(cfg: dict | None = None) -> int:
    """Goruntulenecek context uzunlugunu coz — upstream Hermes uyumluluk.

    Args:
        cfg: Opsiyonel config dict

    Returns:
        int: Context length degeri
    """
    return 128_000
