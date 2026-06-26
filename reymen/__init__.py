# -*- coding: utf-8 -*-
"""
reymen — ReYMeN Otonom Windows Otomasyon Asistani

Tum import'lar lazy loading ile yapilir. Startup'ta sadece __getattr__
proxy'si import edilir. Moduller ilk erisimde yuklenir.

Kullanim:
    from reymen import Motor, ClosedLearningLoop
    # AIAgentOrchestrator: reymen.sistem.main'den import et
    # (sirkuler yuklenme olusur)

Not: __all__'daki her sey __getattr__ ile lazy import edilir.
Hicbiri startup'ta yuklenmez.
"""

import sys
import types
from typing import Any

__version__ = "2.0.0"

# ── Lazy Import Haritasi ─────────────────────────────────────────────────────
# { isim: (paket_yolu, sinif_adi) }
_LAZY_IMPORTS = {
    # Core
    "Motor": ("reymen.cereyan.motor", "Motor"),
    "ClosedLearningLoop": ("reymen.cereyan.closed_learning_loop", "ClosedLearningLoop"),
    "YetenekFabrikasi": ("reymen.cereyan.yetenek_fabrikasi", "YetenekFabrikasi"),
    "SignalHandler": ("reymen.sistem.sistem_sinyalleri", "SignalHandler"),
    "InsanArayuzu": ("reymen.cereyan.insan_arayuzu", "InsanArayuzu"),
    "Planlayici": ("reymen.cereyan.planlayici", "Planlayici"),
    "UygulamaHafizasi": ("reymen.hafiza.uygulama_hafizasi", "UygulamaHafizasi"),

    # Hafiza fonksiyonlari
    "vektorel_hafiza_sistemini_kur": ("reymen.hafiza.vektorel_hafiza", "vektorel_hafiza_sistemini_kur"),
    "tecrube_kaydet": ("reymen.hafiza.vektorel_hafiza", "tecrube_kaydet"),
    "anlamsal_hafiza_ara": ("reymen.hafiza.vektorel_hafiza", "anlamsal_hafiza_ara"),
    "izole_python_calistir": ("reymen.cereyan.izole_laboratuvar", "izole_python_calistir"),

    # Altyapi
    "AdvancedSessionStorage": ("reymen.hafiza.session_db", "AdvancedSessionStorage"),
    "RuntimeProviderEngine": ("reymen.sistem.provider_transport", "RuntimeProviderEngine"),
    "AdvancedContextCompressor": ("reymen.hafiza.context_manager", "AdvancedContextCompressor"),
    "PromptAssemblyEngine": ("reymen.cereyan.prompt_assembly", "PromptAssemblyEngine"),
    "BoundedMemory": ("reymen.hafiza.bounded_memory", "BoundedMemory"),

    # Tool sistemi
    "registry": ("tools.registry", "registry"),
    "tool_error": ("tools.registry", "tool_error"),
}

# ── __all__ ──────────────────────────────────────────────────────────────────
__all__ = list(_LAZY_IMPORTS.keys())


# ── Lazy Import Proxy ────────────────────────────────────────────────────────

class _LazyReymenLoader(types.ModuleType):
    """reymen paketi icin lazy import proxy'si."""

    def __getattr__(self, name: str) -> Any:
        if name in _LAZY_IMPORTS:
            paket, sinif = _LAZY_IMPORTS[name]
            try:
                mod = __import__(paket, fromlist=[sinif])
                obj = getattr(mod, sinif)
                # Cache: modül seviyesinde ata
                setattr(sys.modules[__name__], name, obj)
                return obj
            except ImportError as e:
                raise AttributeError(
                    f"'{name}' yuklenemedi: {e}. "
                    f"Eksik modul: {paket}"
                ) from e
        raise AttributeError(
            f"module '{__name__}' has no attribute '{name}'. "
            f"Mevcut: {', '.join(_LAZY_IMPORTS.keys())}"
        )


# Mevcut modülü lazy loader ile değiştir
sys.modules[__name__].__class__ = _LazyReymenLoader
