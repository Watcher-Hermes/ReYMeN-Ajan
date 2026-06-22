# -*- coding: utf-8 -*-
"""ReYMeN_cli/plugins.py — Plugin Yonetimi CLI (Plugin Management).

Plugin listeleme, etkinlestirme, pasiflestirme, kurma ve kaldirma.
plugin_loader.py ve plugins/ klasoru ile calisir.
Not: plugins_cmd.py (exec/config/log/test/dep) ile karistirilmamali.
"""

import importlib
import json
import logging
import os
import shutil
import sys
import urllib.request
from pathlib import Path
from typing import Any

PROJE_KOK = Path(__file__).parent.parent
PLUGIN_DIR = PROJE_KOK / "plugins"
PLUGIN_KAYIT = PROJE_KOK / ".ReYMeN" / "plugins" / "plugins.json"


class Renk:
    """ReYMeN inline Renk — ANSI renk kodlari."""
    YESIL = "\033[92m"
    SARI = "\033[93m"
    KIRMIZI = "\033[91m"
    MAVI = "\033[94m"
    CYAN = "\033[96m"
    KALIN = "\033[1m"
    SON = "\033[0m"

    @classmethod
    def boya(cls, metin: str, kod: str) -> str:
        return f"{kod}{metin}{cls.SON}"

    @classmethod
    def yesil(cls, metin: str) -> str:
        return cls.boya(metin, cls.YESIL)

    @classmethod
    def sari(cls, metin: str) -> str:
        return cls.boya(metin, cls.SARI)

    @classmethod
    def kirmizi(cls, metin: str) -> str:
        return cls.boya(metin, cls.KIRMIZI)

    @classmethod
    def mavi(cls, metin: str) -> str:
        return cls.boya(metin, cls.MAVI)


def _kayit_oku() -> dict:
    """Plugin kayit dosyasini oku."""
    if not PLUGIN_KAYIT.exists():
        return {"aktif": []}
    try:
        with open(str(PLUGIN_KAYIT), "r", encoding="utf-8") as f:
            icerik = f.read().strip()
            return json.loads(icerik) if icerik else {"aktif": []}
    except (json.JSONDecodeError, Exception):
        return {"aktif": []}


def _kayit_yaz(veri: dict):
    """Plugin kayit dosyasina yaz."""
    PLUGIN_KAYIT.parent.mkdir(parents=True, exist_ok=True)
    with open(str(PLUGIN_KAYIT), "w", encoding="utf-8") as f:
        json.dump(veri, f, indent=2, ensure_ascii=False)


def _plugin_bul(ad: str) -> Path | None:
    """Plugin dizinini bul, yoksa None."""
    for klasor in PLUGIN_DIR.iterdir():
        if klasor.is_dir() and klasor.name == ad:
            return klasor
        if klasor.is_file() and klasor.stem == ad:
            return klasor
    return None


def plugin_listele(durum: str = "") -> str:
    """Pluginleri listele, opsiyonel filtre uygula.

    Args:
        durum: Filtre: 'aktif', 'pasif', '' (tumu)

    Returns:
        str: Plugin listesi metni
    """
    try:
        if not PLUGIN_DIR.exists():
            return f"{Renk.sari('[Plugin]')} plugins/ klasoru bulunamadi."

        kayit = _kayit_oku()
        aktif_liste = kayit.get("aktif", [])
        pluginler = sorted([
            k for k in PLUGIN_DIR.iterdir()
            if k.is_dir() and (k / "__init__.py").exists()
        ], key=lambda x: x.name)

        if not pluginler:
            return f"{Renk.sari('[Plugin]')} Yuklu plugin yok."

        satirlar = [f"{Renk.mavi(f'[Plugin] Pluginler ({len(pluginler)} adet):')}"]
        for p in pluginler:
            aktif = p.name in aktif_liste
            if durum == "aktif" and not aktif:
                continue
            if durum == "pasif" and aktif:
                continue
            isaret = Renk.yesil("\u2713") if aktif else Renk.kirmizi("\u2717")
            etiket = Renk.yesil("Aktif") if aktif else Renk.kirmizi("Pasif")
            satirlar.append(f"  {isaret} {p.name:<25} [{etiket}]")
        return "\n".join(satirlar) if len(satirlar) > 1 else f"{Renk.sari('[Plugin]')} Eslesen plugin yok."

    except Exception as e:
        return f"{Renk.kirmizi('[Plugin]')} Liste hatasi: {e}"


def plugin_aktif_et(ad: str) -> str:
    """Plugin etkinlestir."""
    try:
        klasor = PLUGIN_DIR / ad
        if not klasor.exists() or not (klasor / "__init__.py").exists():
            return f"{Renk.kirmizi('[Plugin]')} Plugin bulunamadi: {ad}"
        kayit = _kayit_oku()
        if ad not in kayit["aktif"]:
            kayit["aktif"].append(ad)
            _kayit_yaz(kayit)
        return f"{Renk.yesil('[Plugin]')} Etkinlestirildi: {ad}"
    except Exception as e:
        return f"{Renk.kirmizi('[Plugin]')} Etkinlestirme hatasi: {e}"


def plugin_pasif_et(ad: str) -> str:
    """Plugin pasiflestir."""
    try:
        kayit = _kayit_oku()
        if ad in kayit["aktif"]:
            kayit["aktif"].remove(ad)
            _kayit_yaz(kayit)
            return f"{Renk.sari('[Plugin]')} Pasiflestirildi: {ad}"
        return f"{Renk.sari('[Plugin]')} Plugin zaten pasif: {ad}"
    except Exception as e:
        return f"{Renk.kirmizi('[Plugin]')} Pasiflestirme hatasi: {e}"


def plugin_kur(kaynak: str) -> str:
    """Plugin kur (yerel yol veya URL).

    Args:
        kaynak: Yerel dizin/dosya yolu veya indirilebilir URL

    Returns:
        str: Islem sonucu
    """
    try:
        PLUGIN_DIR.mkdir(parents=True, exist_ok=True)
        ad = Path(kaynak).stem
        hedef = PLUGIN_DIR / ad

        if hedef.exists():
            return f"{Renk.sari('[Plugin]')} '{ad}' zaten yuklu."

        if kaynak.startswith(("http://", "https://")):
            zip_yol = PLUGIN_DIR / f"{ad}.zip"
            try:
                urllib.request.urlretrieve(kaynak, str(zip_yol))
                import zipfile
                with zipfile.ZipFile(str(zip_yol), "r") as z:
                    z.extractall(str(PLUGIN_DIR))
                zip_yol.unlink()
            except Exception as e:
                if zip_yol.exists():
                    zip_yol.unlink()
                return f"{Renk.kirmizi('[Plugin]')} URL'den kurulum hatasi: {e}"
        elif os.path.exists(kaynak):
            if os.path.isdir(kaynak):
                shutil.copytree(kaynak, hedef)
            else:
                shutil.copy2(kaynak, hedef)
        else:
            return f"{Renk.kirmizi('[Plugin]')} Kaynak bulunamadi: {kaynak}"

        kayit = _kayit_oku()
        if ad not in kayit["aktif"]:
            kayit["aktif"].append(ad)
            _kayit_yaz(kayit)

        return f"{Renk.yesil('[Plugin]')} Kuruldu ve etkinlestirildi: {ad}"

    except Exception as e:
        return f"{Renk.kirmizi('[Plugin]')} Kurulum hatasi: {e}"


def plugin_kaldir(ad: str) -> str:
    """Plugin kaldir."""
    try:
        klasor = PLUGIN_DIR / ad
        if not klasor.exists():
            return f"{Renk.sari('[Plugin]')} Plugin bulunamadi: {ad}"

        if klasor.is_dir():
            shutil.rmtree(str(klasor))
        else:
            klasor.unlink()

        kayit = _kayit_oku()
        if ad in kayit.get("aktif", []):
            kayit["aktif"].remove(ad)
            _kayit_yaz(kayit)

        return f"{Renk.yesil('[Plugin]')} Kaldirildi: {ad}"

    except Exception as e:
        return f"{Renk.kirmizi('[Plugin]')} Kaldirma hatasi: {e}"


def kaydet(alt_parser):
    """Plugin yonetimi CLI alt komutlarini argparse alt ayristiricisina kaydet."""
    alt_parser.add_argument("islem", type=str, nargs="?",
                            choices=["list", "enable", "disable", "install", "remove"],
                            help="Islem (list|enable|disable|install|remove)")
    alt_parser.add_argument("--ad", type=str, default=None,
                            help="Plugin adi (enable/disable/remove icin)")
    alt_parser.add_argument("--kaynak", type=str, default=None,
                            help="Plugin kaynagi (install icin: yol/URL)")
    alt_parser.add_argument("--durum", type=str, default="",
                            choices=["", "aktif", "pasif", "tumu"],
                            help="Filtre (list icin: aktif/pasif/tumu)")


def calistir(args):
    """Plugin yonetimi komutunu calistir."""
    try:
        islem = args.islem or "list"

        if islem == "list":
            durum = args.durum or "tumu"
            if durum == "tumu":
                durum = ""
            print(plugin_listele(durum))

        elif islem == "enable":
            if not args.ad:
                print(f"{Renk.sari('[Plugin]')} Lutfen --ad belirtin.")
                return
            print(plugin_aktif_et(args.ad))

        elif islem == "disable":
            if not args.ad:
                print(f"{Renk.sari('[Plugin]')} Lutfen --ad belirtin.")
                return
            print(plugin_pasif_et(args.ad))

        elif islem == "install":
            if not args.kaynak:
                print(f"{Renk.sari('[Plugin]')} Lutfen --kaynak belirtin.")
                return
            print(plugin_kur(args.kaynak))

        elif islem == "remove":
            if not args.ad:
                print(f"{Renk.sari('[Plugin]')} Lutfen --ad belirtin.")
                return
            print(plugin_kaldir(args.ad))

    except Exception as e:
        print(f"{Renk.kirmizi('[Plugin]')} Komut hatasi: {e}")


def invoke_hook(name: str, **kwargs) -> list:
    """Tum pluginlerde 'hook_<name>' fonksiyonlarini bulur ve cagirir.

    Her plugin alt dizininde __init__.py veya plugin.py dosyasini ara.
    Modulde 'hook_' + name (ornek: hook_on_session_start) fonksiyonu
    varsa kwargs ile cagirir. Bir pluginin basarisizligi digerlerini
    etkilemez.

    Args:
        name: Hook adi (ornek: 'on_session_start' -> 'hook_on_session_start')
        **kwargs: Hook fonksiyonuna iletilecek anahtar/deger parametreler

    Returns:
        list: Tum pluginlerden donen degerlerin listesi
    """
    logger = logging.getLogger(__name__)
    sonuclar: list = []
    hook_adi = f"hook_{name}"

    if not PLUGIN_DIR.exists():
        logger.warning("Plugin dizini bulunamadi: %s", PLUGIN_DIR)
        return sonuclar

    for klasor in sorted(PLUGIN_DIR.iterdir()):
        if not klasor.is_dir():
            continue

        # __init__.py veya plugin.py ara
        modul_dosyasi = klasor / "__init__.py"
        if not modul_dosyasi.exists():
            modul_dosyasi = klasor / "plugin.py"
            if not modul_dosyasi.exists():
                continue

        modul_adi = f"plugins.{klasor.name}"

        try:
            modul = importlib.import_module(modul_adi)
            hook_fonk = getattr(modul, hook_adi, None)
            if hook_fonk is not None and callable(hook_fonk):
                sonuc = hook_fonk(**kwargs)
                sonuclar.append(sonuc)
        except Exception as e:
            logger.warning(
                "Plugin '%s' hook '%s' hatasi: %s", klasor.name, hook_adi, e
            )

    return sonuclar


class PluginManager:
    """Plugin Yoneticisi — upstream Hermes uyumluluk katmani.

    Plugin listeleme, etkinlestirme, pasiflestirme, kurma, kaldirma.
    """

    def __init__(self, config: Any = None):
        self._config = config

    def list_plugins(self) -> list:
        return [{"ad": p.name, "aktif": p.name in _kayit_oku().get("aktif", [])}
                for p in sorted(PLUGIN_DIR.iterdir()) if p.is_dir() and (p / "__init__.py").exists()]

    def enable_plugin(self, ad: str) -> bool:
        return "Etkinlestirildi" in plugin_aktif_et(ad)

    def disable_plugin(self, ad: str) -> bool:
        return "Pasiflestirildi" in plugin_pasif_et(ad)

    def install_plugin(self, kaynak: str) -> bool:
        return "Kuruldu" in plugin_kur(kaynak)

    def remove_plugin(self, ad: str) -> bool:
        return "Kaldirildi" in plugin_kaldir(ad)


class PluginManifest:
    """Plugin manifest — upstream Hermes uyumluluk katmani.

    Plugin meta-bilgilerini tasir.
    """

    def __init__(self, ad: str = "", versiyon: str = "0.1.0", aciklama: str = ""):
        self.ad = ad
        self.versiyon = versiyon
        self.aciklama = aciklama
        self.hooks: list[str] = []


class PluginContext:
    """Plugin Context — upstream Hermes uyumluluk katmani.

    Pluginlerin kayit, hook, auxiliary task yonetimi.
    hermes_cli.plugins.PluginContext ile ayni arayuz.
    """

    def __init__(self, manifest: Any = None):
        self._manifest = manifest or PluginManifest()
        self._commands: dict[str, Any] = {}
        self._hooks: dict[str, list] = {}
        self._aux_tasks: list[Any] = []
        self._browser_providers: list[Any] = []
        self._image_gen_providers: list[Any] = []
        self._transcription_providers: list[Any] = []
        self._tts_providers: list[Any] = []
        self._video_gen_providers: list[Any] = []
        self._web_search_providers: list[Any] = []
        self._context_engines: list[Any] = []
        self._auxiliary_tasks: list[Any] = []
        self._llm_providers: dict[str, Any] = {}

    def register_command(self, name: str, handler: Any) -> None:
        self._commands[name] = handler

    def register_hook(self, name: str, handler: Any) -> None:
        self._hooks.setdefault(name, []).append(handler)

    def register_auxiliary_task(self, task: Any) -> None:
        self._aux_tasks.append(task)

    def register_browser_provider(self, provider: Any) -> None:
        self._browser_providers.append(provider)

    def register_image_gen_provider(self, provider: Any) -> None:
        self._image_gen_providers.append(provider)

    def register_transcription_provider(self, provider: Any) -> None:
        self._transcription_providers.append(provider)

    def register_tts_provider(self, provider: Any) -> None:
        self._tts_providers.append(provider)

    def register_video_gen_provider(self, provider: Any) -> None:
        self._video_gen_providers.append(provider)

    def register_web_search_provider(self, provider: Any) -> None:
        self._web_search_providers.append(provider)

    def register_context_engine(self, engine: Any) -> None:
        self._context_engines.append(engine)

    def register_llm_provider(self, provider_id: str, provider: Any) -> None:
        self._llm_providers[provider_id] = provider

    def get_auxiliary_tasks(self) -> list:
        return list(self._aux_tasks)

    def get_context_engines(self) -> list:
        return list(self._context_engines)

    def get_llm_provider(self, provider_id: str) -> Any | None:
        return self._llm_providers.get(provider_id)


def discover_plugins(config: Any = None) -> list[PluginManifest]:
    """Pluginleri kesfet — upstream Hermes uyumluluk.

    Args:
        config: Opsiyonel yapilandirma

    Returns:
        list[PluginManifest]: Kesfedilen plugin manifestleri
    """
    manifests: list[PluginManifest] = []
    if not PLUGIN_DIR.exists():
        return manifests
    for klasor in sorted(PLUGIN_DIR.iterdir()):
        if not klasor.is_dir():
            continue
        init_file = klasor / "__init__.py"
        if not init_file.exists():
            continue
        manifest = PluginManifest(ad=klasor.name)
        manifests.append(manifest)
    return manifests


def get_plugin_auxiliary_tasks() -> list[Any]:
    """Plugin auxiliary task'lerini topla — upstream Hermes uyumluluk.

    Returns:
        list: Tum pluginlerden toplanan auxiliary task listesi
    """
    tasks: list[Any] = []
    if not PLUGIN_DIR.exists():
        return tasks
    for klasor in sorted(PLUGIN_DIR.iterdir()):
        if not klasor.is_dir():
            continue
        init_file = klasor / "__init__.py"
        if not init_file.exists():
            continue
        try:
            modul = importlib.import_module(f"plugins.{klasor.name}")
            if hasattr(modul, "get_auxiliary_tasks"):
                t = modul.get_auxiliary_tasks()
                if t:
                    tasks.extend(t if isinstance(t, list) else [t])
        except Exception:
            pass
    return tasks


def get_plugin_command_handler(command: str) -> Any | None:
    """Plugin komut yoneticisini bul — upstream Hermes uyumluluk.

    Args:
        command: Komut adi

    Returns:
        Handler fonksiyonu veya None
    """
    if not PLUGIN_DIR.exists():
        return None
    for klasor in sorted(PLUGIN_DIR.iterdir()):
        if not klasor.is_dir():
            continue
        init_file = klasor / "__init__.py"
        if not init_file.exists():
            continue
        try:
            modul = importlib.import_module(f"plugins.{klasor.name}")
            handler = getattr(modul, f"handler_{command}", None)
            if handler is not None and callable(handler):
                return handler
        except Exception:
            pass
    return None


def get_plugin_context_engine(context_id: str = "") -> Any | None:
    """Plugin context engine'ini bul — upstream Hermes uyumluluk.

    Args:
        context_id: Context engine ID'si

    Returns:
        Context engine veya None
    """
    if not PLUGIN_DIR.exists():
        return None
    for klasor in sorted(PLUGIN_DIR.iterdir()):
        if not klasor.is_dir():
            continue
        init_file = klasor / "__init__.py"
        if not init_file.exists():
            continue
        try:
            modul = importlib.import_module(f"plugins.{klasor.name}")
            engine = getattr(modul, "context_engine", None)
            if engine is not None:
                return engine
        except Exception:
            pass
    return None
