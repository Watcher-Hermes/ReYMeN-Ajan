# -*- coding: utf-8 -*-
"""
lazy_loader.py — Lazy module loading.

100+ modülü tek tek import etmek yerine, sadece ihtiyaç olduğunda yükler.
Startup süresini 100-500ms'den 5-10ms'ye düşürür.

Kullanım:
    from reymen.sistem.lazy_loader import LazyModule
    playwright = LazyModule("playwright")
    # İlk kullanımda yüklenir:
    playwright.sync_api.sync_playwright()
"""

import importlib
import sys
from typing import Any, Optional, Dict, Callable


class LazyModule:
    """
    Lazy loading modül wrapper'ı.

    Modül ilk erişimde yüklenir. Yüklenemezse AttributeError yerine
    anlamlı hata mesajı döner.
    """

    def __init__(self, module_name: str, package: Optional[str] = None,
                 install_hint: Optional[str] = None):
        """
        Args:
            module_name: Modül adı (örn: "playwright")
            package: Paket adı (örn: "playwright.sync_api")
            install_hint: Kurulum ipucu (örn: "pip install playwright")
        """
        self._module_name = module_name
        self._package = package
        self._install_hint = install_hint or f"pip install {module_name}"
        self._module = None
        self._loaded = False
        self._error = None

    def _load(self) -> Any:
        """Modülü yükler."""
        if self._loaded:
            return self._module

        try:
            if self._package:
                self._module = importlib.import_module(self._package)
            else:
                self._module = importlib.import_module(self._module_name)
            self._loaded = True
            return self._module
        except ImportError as e:
            self._error = str(e)
            self._loaded = True  # Tekrar deneme
            return None

    def __getattr__(self, name: str) -> Any:
        mod = self._load()
        if mod is None:
            raise ImportError(
                f"'{self._module_name}' modülü yüklenemedi. "
                f"Kurulum: {self._install_hint}"
            )
        return getattr(mod, name)

    def __bool__(self) -> bool:
        return self._load() is not None

    def is_available(self) -> bool:
        """Modül mevcut mu?"""
        return self._load() is not None

    def get_error(self) -> Optional[str]:
        """Yükleme hatası varsa döner."""
        self._load()
        return self._error


class LazyTool:
    """
    Lazy loading tool wrapper'ı.

    Tool fonksiyonunu ilk çağrıldığında yükler.
    """

    def __init__(self, module_path: str, function_name: str = "run",
                 install_hint: Optional[str] = None):
        self._module_path = module_path
        self._function_name = function_name
        self._install_hint = install_hint
        self._func = None
        self._loaded = False
        self._error = None

    def _load(self) -> Optional[Callable]:
        if self._loaded:
            return self._func

        try:
            mod = importlib.import_module(self._module_path)
            self._func = getattr(mod, self._function_name)
            self._loaded = True
            return self._func
        except (ImportError, AttributeError) as e:
            self._error = str(e)
            self._loaded = True
            return None

    def __call__(self, *args, **kwargs) -> Any:
        func = self._load()
        if func is None:
            return f"[Hata]: Tool yüklenemedi: {self._module_path} ({self._error})"
        return func(*args, **kwargs)

    def is_available(self) -> bool:
        return self._load() is not None


class ModuleRegistry:
    """
    Modül kayıt ve lazy loading merkezi.

    Tüm modülleri kaydeder, sadece ihtiyaç olduğunda yükler.
    """

    def __init__(self):
        self._modules: Dict[str, LazyModule] = {}
        self._tools: Dict[str, LazyTool] = {}

    def register_module(self, name: str, module_name: str,
                        package: Optional[str] = None,
                        install_hint: Optional[str] = None) -> None:
        """Modül kaydeder."""
        self._modules[name] = LazyModule(module_name, package, install_hint)

    def register_tool(self, name: str, module_path: str,
                      function_name: str = "run") -> None:
        """Tool kaydeder."""
        self._tools[name] = LazyTool(module_path, function_name)

    def get_module(self, name: str) -> Optional[LazyModule]:
        """Modül döner."""
        return self._modules.get(name)

    def get_tool(self, name: str) -> Optional[LazyTool]:
        """Tool döner."""
        return self._tools.get(name)

    def is_available(self, name: str) -> bool:
        """Modül/tool mevcut mu?"""
        if name in self._modules:
            return self._modules[name].is_available()
        if name in self._tools:
            return self._tools[name].is_available()
        return False

    def status(self) -> Dict[str, bool]:
        """Tüm modüllerin durumunu döner."""
        durum = {}
        for name, mod in self._modules.items():
            durum[name] = mod.is_available()
        for name, tool in self._tools.items():
            durum[f"tool:{name}"] = tool.is_available()
        return durum

    def formatla(self) -> str:
        """Durumu okunabilir format döner."""
        durum = self.status()
        satirlar = [f"📦 Modül Registry ({len(durum)} modül):\n"]
        for name, available in sorted(durum.items()):
            emoji = "✅" if available else "❌"
            satirlar.append(f"  {emoji} {name}")
        return "\n".join(satirlar)


# ── Global Registry ──────────────────────────────────────────────────────────

_registry = None

def get_registry() -> ModuleRegistry:
    """Global modül registry'si döner."""
    global _registry
    if _registry is None:
        _registry = ModuleRegistry()
        # Varsayılan modülleri kaydet
        _varsayilan_kaydet(_registry)
    return _registry


def _varsayilan_kaydet(reg: ModuleRegistry):
    """Varsayılan modülleri kaydeder."""
    # Web araçları
    reg.register_tool("web_extract", "reymen.arac.web_extract_tool")
    reg.register_tool("web_search", "reymen.arac.araclar_web")

    # Görsel araçları
    reg.register_tool("vision_analyze", "reymen.arac.vision_analyze_tool")
    reg.register_tool("image_generate", "reymen.arac.image_generate_tool")

    # Tarayıcı
    reg.register_tool("browser", "reymen.arac.browser_mcp_tool")

    # Dosya araçları
    reg.register_tool("file_ops", "reymen.arac.file_ops_tool")
    reg.register_tool("patch", "reymen.arac.file_ops_tool")

    # Yönetim araçları
    reg.register_tool("todo", "reymen.arac.todo_tool")
    reg.register_tool("process", "reymen.arac.process_tool")
    reg.register_tool("cron", "reymen.arac.cron_tool")
    reg.register_tool("memory_batch", "reymen.arac.memory_batch_tool")
    reg.register_tool("profile", "reymen.arac.profile_tool")
    reg.register_tool("approval", "reymen.arac.approval_tool")
    reg.register_tool("multi_platform", "reymen.arac.multi_platform_tool")
    reg.register_tool("powershell", "reymen.arac.powershell_tool")

    # Güvenlik
    reg.register_tool("security", "reymen.guvenlik.security_hardened")

    # Konfigürasyon
    reg.register_tool("config", "reymen.sistem.config_manager")

    # Opsiyonel modüller
    reg.register_module("playwright", "playwright", install_hint="pip install playwright")
    reg.register_module("easyocr", "easyocr", install_hint="pip install easyocr")
    reg.register_module("bs4", "bs4", install_hint="pip install beautifulsoup4")
    reg.register_module("lxml", "lxml", install_hint="pip install lxml")
    reg.register_module("fal_client", "fal_client", install_hint="pip install fal-client")
    reg.register_module("openai", "openai", install_hint="pip install openai")
    reg.register_module("PIL", "PIL", install_hint="pip install pillow")
    reg.register_module("numpy", "numpy", install_hint="pip install numpy")


# ── Motor Entegrasyonu ───────────────────────────────────────────────────────

def run(islem: str = "durum", ad: str = "") -> str:
    """Motor entegrasyonu."""
    reg = get_registry()

    if islem == "durum":
        return reg.formatla()

    elif islem == "kontrol":
        if not ad:
            return "[Hata]: ad gerekli."
        mevcut = reg.is_available(ad)
        return f"✅ {ad} mevcut" if mevcut else f"❌ {ad} mevcut değil"

    return f"[Hata]: Bilinmeyen islem: {islem}"


if __name__ == "__main__":
    reg = get_registry()
    print(reg.formatla())
