"""motor/main.py — Motor class (eylem çözümleyici, araç yönlendirici).

Core Motor class. Fallback yardımcıları motor/fallback.py'de.
"""
import json
import logging
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Optional, Dict, List, Tuple, Union

from reymen.cereyan.motor.config import (
    ROOT, BILINEN_ARACLAR, DURUM_MESAJLARI, RISKLI_ARACLAR,
    RE_EYLEM, RE_ARAC_CAGRI, RE_ARAC_CAGRI_COK, RE_PARAM,
    TOOLSET_GRUPLARI, GECERLI_PROVIDERLER, VARSAYILAN_MODELLER,
    MAX_PARALLEL_WORKERS, PARALLEL_TIMEOUT_VARSAYILAN,
)
from reymen.cereyan.motor.context import (
    cevabi_temizle as _cevabi_temizle,
    context_sikistir as _context_sikistir,
    cache_kontrol as _cache_kontrol,
    cache_kaydet as _cache_kaydet,
    gateway_durum_yaz as _gateway_durum_yaz,
)
from reymen.cereyan.motor.plugins import (
    _REGISTRY, _PLUGIN_MGR, _PLUGIN_YUKLEYICI,
    plugin_arac_kaydet, lazy_module_listesi,
    skill_araclari_kaydet, skill_v2_araclari_kaydet,
    hafiza_araclari_kaydet, hook_tetikle as _hook_tetikle,
)
from reymen.cereyan.motor.providers import (
    setup_oku as _setup_oku,
    tum_providerlar_listele as _tum_providerlar_listele,
    provider_test_et as _provider_test_et,
    provider_degistir as _provider_degistir_basit,
)

log = logging.getLogger("motor")

try:
    from terminal_backends import TerminalBackendDispatcher
except ImportError:
    TerminalBackendDispatcher = None
try:
    from izole_laboratuvar import izole_python_calistir
except ImportError:
    izole_python_calistir = None


class Motor:
    """Motor — Eylem çözümleyici ve araç yönlendirici."""
    _ARAC_CHECK_FNS: dict = {}

    def __init__(
        self,
        backend_mode: str = "local",
        hafiza_collection: Any = None,
        config: Optional[dict] = None,
        basit_mod: bool = False,
    ) -> None:
        self.terminal = TerminalBackendDispatcher(mode=backend_mode) if TerminalBackendDispatcher else None
        self.hafiza = hafiza_collection
        self.config = config or {}
        self.basit_mod = basit_mod
        self._ekran = None
        self._provider_ref = None
        self.ekstra_izin_araclar: set = set()
        try:
            from hook_dispatcher import AsynchronousHookDispatcher
            self._hooks = AsynchronousHookDispatcher()
        except ImportError:
            self._hooks = None
        self._skill_araclari_cache = None
        self._provider_cache = None
        self._lazy_batch = None
        self._lazy_yuklendi = False
        self._lazy_plugin_kaydet()
        try:
            from dinamik_arac_uretici import mevcut_dinamik_araclari_yukle
            mevcut_dinamik_araclari_yukle(self)
        except ImportError:
            pass
        self._hata_watchdog = None
        self._hata_kod = None
        self._hata_terminal = None
        self._hata_cozum = None
        self._tor_browser = None
        self._tor_akislar = None
        self._gateway_runner = None
        self._alt_ajan = None

    # ── Lazy ─────────────────────────────────────────────────────────────────
    def _lazy_araclari_yukle(self) -> None:
        if self._lazy_yuklendi or self._lazy_batch is None:
            return
        self._lazy_yuklendi = True
        log.debug("Lazy modüller yükleniyor...")
        self._lazy_batch.hepsini_yukle(self)
        if self._skill_araclari_cache is None:
            skill_araclari_kaydet(self)
            skill_v2_araclari_kaydet(self)
            self._skill_araclari_cache = True
        hafiza_araclari_kaydet(self)
        try:
            from plugin_loader import PluginYukleyici
            _py = PluginYukleyici(dizin=ROOT / "plugins")
            _py.hepsini_yukle()
            _py.motora_kaydet(self)
        except ImportError:
            pass
        try:
            from reymen.sistem.lazy_loader import MCPToolBridge
            _mcp = MCPToolBridge()
            _mcp.motora_kaydet(self)
        except ImportError:
            pass
        log.debug("Lazy yükleme tamam (%s modül)", len(self._lazy_batch._entries))

    def hook_kaydet(self, olay: str, fn: Any) -> None:
        if self._hooks:
            self._hooks.kaydet(olay, fn)

    def _temel_araclari_yukle(self) -> None:
        self.aktif_toolsetler = {"temel", "web"}

    def _lazy_plugin_kaydet(self) -> None:
        if self.basit_mod:
            self._temel_araclari_yukle()
            return
        from reymen.sistem.lazy_loader import LazyModuleBatch
        batch = LazyModuleBatch()
        for mod_adi in lazy_module_listesi():
            batch.ekle(mod_adi)
        self._lazy_batch = batch
        log.debug("%s modül lazy batch'e kaydedildi", len(lazy_module_listesi()))

    def _plugin_moduller_yukle(self) -> None:
        self._lazy_araclari_yukle()

    def _plugin_arac_kaydet(self, ad: str, fonk: Any, aciklama: str = "") -> None:
        plugin_arac_kaydet(ad, fonk, aciklama)

    # ── FC API ──────────────────────────────────────────────────────────────
    def calistir_fc(self, arac: str, args: dict) -> str:
        if not args:
            return self.calistir(arac, "")
        parts = []
        for v in args.values():
            v_str = str(v)
            escaped = v_str.replace("\\", "\\\\").replace('"', '\\"')
            parts.append(f'"{escaped}"')
        return self.calistir(arac, " ".join(parts))

    # ── Tools schema ─────────────────────────────────────────────────────────
    def tools_schema_al(self, maks: int = 64) -> list:
        schema: list = [{
            "type": "function",
            "function": {
                "name": "GOREV_BITTI",
                "description": "Görevi başarıyla tamamladığında çağır.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "ozet": {"type": "string", "description": "Yapılanların özeti (2–5 cümle)"}
                    },
                    "required": ["ozet"],
                },
            },
        }]
        if not _REGISTRY:
            return schema
        for ad, _ in list(_REGISTRY._tools.items())[:maks]:
            if ad == "GOREV_BITTI":
                continue
            meta = _REGISTRY._meta.get(ad)
            aciklama = ""
            if isinstance(meta, dict):
                aciklama = meta.get("aciklama", "") or meta.get("description", "")
            if not aciklama:
                aciklama = ad.replace("_", " ").title()
            schema.append({
                "type": "function",
                "function": {
                    "name": ad,
                    "description": aciklama[:200],
                    "parameters": {
                        "type": "object",
                        "properties": {"param": {"type": "string", "description": f"{ad} için parametre"}},
                        "required": [],
                    },
                },
            })
        return schema

    @property
    def _plugin_araclar(self) -> dict:
        return dict(_REGISTRY._tools) if _REGISTRY else {}

    # ── Eylem çözümleme ─────────────────────────────────────────────────────
    def eylemi_ayristir(self, llm_cikti: str) -> Tuple[Optional[str], Optional[str]]:
        m = RE_EYLEM.search(llm_cikti)
        if m:
            return m.group(1).strip().upper(), m.group(2).strip()
        for satir in llm_cikti.splitlines():
            satir_s = satir.strip()
            m2 = RE_ARAC_CAGRI.match(satir_s)
            if m2 and m2.group(1) in BILINEN_ARACLAR:
                return m2.group(1), m2.group(2).strip()
            m3 = RE_ARAC_CAGRI_COK.match(satir_s)
            if m3 and m3.group(1) in BILINEN_ARACLAR:
                idx = llm_cikti.find(satir_s)
                m4 = re.search(r'([A-Z][A-Z_0-9]+)\s*\(((?:[^()]*|\([^()]*\))*)\)', llm_cikti[idx:], re.DOTALL)
                if m4:
                    return m4.group(1), m4.group(2).strip()
        return None, None

    def _parametreleri_coz(self, ham: str) -> List[str]:
        return RE_PARAM.findall(ham)

    # ── Araç kullanılabilirliği ──────────────────────────────────────────────
    @classmethod
    def check_fn_kaydet(cls, arac_adi: str, fn: Any) -> None:
        cls._ARAC_CHECK_FNS[arac_adi] = fn

    def musait_araclar(self, toolset: Optional[str] = None) -> set:
        if toolset:
            aday = TOOLSET_GRUPLARI.get(toolset, set())
        else:
            aday = {a for g in TOOLSET_GRUPLARI.values() for a in g}
        sonuc = set()
        for ad in aday:
            fn = self._ARAC_CHECK_FNS.get(ad)
            if fn is not None and not fn():
                continue
            try:
                from tool_registry import tool_registry as _reg
                if not _reg.check_fn_kontrol_et(ad):
                    continue
            except (ImportError, AttributeError):
                pass
            sonuc.add(ad)
        return sonuc

    def toolset_tanimi_al(self, araclar: Optional[set] = None) -> str:
        if araclar is None:
            araclar = self.musait_araclar()
        satirlar = []
        for grup, uyeler in TOOLSET_GRUPLARI.items():
            aktif = araclar & uyeler
            if aktif:
                satirlar.append(f"[{grup.upper()}] {', '.join(sorted(aktif))}")
        return "\n".join(satirlar)

    def tum_arac_tanimini_al(self) -> str:
        tanim = self.toolset_tanimi_al()
        if _REGISTRY and hasattr(_REGISTRY, '_tools'):
            toolset_araclari = {a for g in TOOLSET_GRUPLARI.values() for a in g}
            ek = set(_REGISTRY._tools.keys()) - toolset_araclari
            if ek:
                if tanim:
                    tanim += "\n"
                tanim += "[DINAMIK] " + ", ".join(sorted(ek))
        return tanim

    def _durum_goster(self, arac: str, params: List[str]) -> None:
        mesaj = DURUM_MESAJLARI.get(arac)
        if mesaj:
            ozet = (params[0] if params else "")[:60]
            log.info("[*] %s%s", mesaj, f" [{ozet}]" if ozet else "")

    # ── Ana çalıştırma ──────────────────────────────────────────────────────
    def calistir(self, arac: str, ham_param: str) -> str:
        if self._lazy_batch is not None and not self._lazy_yuklendi:
            self._lazy_araclari_yukle()
        params = self._parametreleri_coz(ham_param)
        log.info("calistir: %s | param_sayisi=%s", arac, len(params))
        self._durum_goster(arac, params)
        try:
            from reymen.hermes.tools.achievements import _listeye_ekle
            _listeye_ekle("tools_used.json", arac)
        except Exception:
            pass
        _check = self._ARAC_CHECK_FNS.get(arac)
        if _check is not None and not _check():
            log.warning("[Motor] %s kullanilamaz (check_fn engelledi)", arac)
            return f"[{arac}]: Bu araç bu ortamda kullanılamıyor."
        _izinli = arac in getattr(self, "ekstra_izin_araclar", set())
        if arac in RISKLI_ARACLAR and not _izinli and getattr(self, "onay_fonksiyonu", None):
            ozet = (params[0] if params else "")[:120]
            if not self.onay_fonksiyonu(arac, ozet):
                log.info("[Motor] %s HITL onayi reddedildi", arac)
                return f"[İptal]: Kullanıcı '{arac}' eylemini reddetti."
        from reymen.cereyan.motor.fallback import ozel_arac_calistir
        ozel_sonuc = ozel_arac_calistir(self, arac, ham_param, params)
        if ozel_sonuc is not None:
            _hook_tetikle(self, arac, params, ozel_sonuc)
            return ozel_sonuc
        if _REGISTRY:
            _registry_sonuc = _REGISTRY.calistir(arac, *params)
            if not _registry_sonuc.startswith("[Bilinmeyen arac]"):
                _hook_tetikle(self, arac, params, _registry_sonuc)
                log.debug("[Motor] %s -> Registry basarili (%s krk)", arac, len(_registry_sonuc))
                return _registry_sonuc
        if _PLUGIN_MGR:
            try:
                plugin_sonuc = _PLUGIN_MGR.run(arac.lower())
                _hook_tetikle(self, arac, params, plugin_sonuc)
                log.debug("[Motor] %s -> Plugin basarili", arac)
                return str(plugin_sonuc)
            except KeyError:
                pass
        from reymen.cereyan.motor.fallback import fallback_calistir as _fb
        sonuc = _fb(self, arac, params)
        _hook_tetikle(self, arac, params, sonuc)
        if "[Hata]" in sonuc:
            log.warning("[Motor] %s -> Fallback hata: %s", arac, sonuc[:150])
        else:
            log.debug("[Motor] %s -> Fallback basarili (%s krk)", arac, len(sonuc))
        return sonuc

    # ── Provider yönetimi (wrapper) ──────────────────────────────────────────
    def aktif_provider_listele(self) -> list[dict]:
        return _tum_providerlar_listele()

    def provider_test_et(self, provider_adi: str) -> dict:
        return _provider_test_et(provider_adi)

    def provider_degistir(self, provider_adi: str, model: str = "") -> dict:
        sonuc = _provider_degistir_basit(provider_adi, model)
        if sonuc.get("success"):
            self._provider_cache = None
        return sonuc

    def _setup_oku(self) -> dict:
        return _setup_oku()

    # ── Context/Cache (wrapper) ────────────────────────────────────────────
    def _cevabi_temizle(self, cevap: str) -> str:
        return _cevabi_temizle(cevap)

    def _context_sikistir(self, gecmis: list) -> list:
        return _context_sikistir(gecmis)

    def _cache_kontrol(self, prompt: str, sistem: str = "") -> Optional[str]:
        return _cache_kontrol(prompt, sistem)

    def _cache_kaydet(self, prompt: str, yanit: str, sistem: str = "") -> None:
        _cache_kaydet(prompt, yanit, sistem)


# ── Module-level ──────────────────────────────────────────────────────────────
def provider_degistir(saglayici: str, model: str = "") -> dict:
    """Aktif provider/model'i setup.json'dan degistirir (Motor gerektirmez)."""
    from reymen.cereyan.motor.providers import provider_degistir_basit
    return provider_degistir_basit(saglayici, model)
