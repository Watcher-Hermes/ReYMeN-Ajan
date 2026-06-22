# -*- coding: utf-8 -*-
"""
reymen — ReYMeN Otonom Windows Otomasyon Asistani

Kullanim:
    from reymen import Motor, ClosedLearningLoop, YetenekFabrikasi
    # AIAgentOrchestrator: dogrudan reymen.sistem.main'den import et
    # (reymen/__init__.py'den import etme — sirkuler yuklenme olusur)
"""

# Reymen 11 ozel dosya - sinif ve fonksiyonlar
# DOGRUDAN paket ici yollardan import et (root seviyesindeki shim'ler
# cirkuler import'a sebep olur). Shim'ler sadece dogrudan `python -c "from motor import Motor"`
# gibi kullanimlar icindir.
from reymen.cereyan.motor import Motor
# AIAgentOrchestrator burada import edilmez — reymen.sistem.main entry-point
# olup kendi modulu icerisinde tanimlanir. Buradan import etmek cift yuklenmeye
# (ve stdout buffer kapatilmasina) yol acar.
from reymen.cereyan.closed_learning_loop import ClosedLearningLoop
from reymen.cereyan.yetenek_fabrikasi import YetenekFabrikasi
from reymen.sistem.sistem_sinyalleri import SignalHandler
from reymen.cereyan.insan_arayuzu import InsanArayuzu
from reymen.cereyan.planlayici import Planlayici
from reymen.hafiza.uygulama_hafizasi import UygulamaHafizasi
from reymen.hafiza.vektorel_hafiza import vektorel_hafiza_sistemini_kur, tecrube_kaydet, anlamsal_hafiza_ara
from reymen.cereyan.izole_laboratuvar import izole_python_calistir

# Altyapi modulleri
from reymen.hafiza.session_db import AdvancedSessionStorage
from reymen.sistem.provider_transport import RuntimeProviderEngine
from reymen.hafiza.context_manager import AdvancedContextCompressor
from reymen.cereyan.prompt_assembly import PromptAssemblyEngine
from reymen.hafiza.bounded_memory import BoundedMemory

# Tool sistemi (root-level tools paketi, shim degil — degismiyor)
from tools.registry import registry, tool_error

__all__ = [
    "Motor", "ClosedLearningLoop",
    "YetenekFabrikasi", "SignalHandler", "InsanArayuzu",
    "Planlayici", "UygulamaHafizasi",
    "vektorel_hafiza_sistemini_kur", "tecrube_kaydet", "anlamsal_hafiza_ara",
    "izole_python_calistir",
    "AdvancedSessionStorage", "RuntimeProviderEngine",
    "AdvancedContextCompressor", "PromptAssemblyEngine", "BoundedMemory",
    "registry", "tool_error",
]

__version__ = "2.0.0"
