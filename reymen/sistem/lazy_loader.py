# -*- coding: utf-8 -*-
"""
lazy_loader.py — Lazy module loading + MCP tool bridge.

100+ modülü startup'ta import etmek yerine, sadece ihtiyaç olduğunda yükler.
Startup süresini 100-500ms'den 5-10ms'ye düşürür.
MCP server araçlarını gateway üzerinden lazy bridge ile sunar.

Kullanım:
    from reymen.sistem.lazy_loader import LazyModule
    playwright = LazyModule("playwright")
    playwright.sync_api.sync_playwright()
"""

import importlib
import json
import os
import sys
from pathlib import Path
from typing import Any, Optional, Dict, Callable, List, Union


# ── Lazy Module ──────────────────────────────────────────────────────────────

class LazyModule:
    """Lazy loading modül wrapper'ı.

    Modül ilk erişimde yüklenir. Yüklenemezse AttributeError yerine
    anlamlı hata mesajı döner.
    """

    def __init__(self, module_name: str, package: Optional[str] = None,
                 install_hint: Optional[str] = None):
        self._module_name = module_name
        self._package = package
        self._install_hint = install_hint or f"pip install {module_name}"
        self._module = None
        self._loaded = False
        self._error = None

    def _load(self) -> Any:
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
            self._loaded = True
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
        return self._load() is not None

    def get_error(self) -> Optional[str]:
        self._load()
        return self._error


# ── Lazy Tool (for motor.py plugin tools) ─────────────────────────────────────

class LazyTool:
    """Lazy loading tool wrapper'ı.

    Tool fonksiyonunu ilk çağrıldığında yükler.
    motor.py'ye kaydedilmek üzere tasarlandı.
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


# ── Lazy Module Batch (for motor.py _plugin_modulleri_yukle replacement) ──────

class LazyModuleBatch:
    """
    100+ modülü startup'ta tek tek import etmek yerine lazy registry'de tutar.

    Her modül:
    - İlk motor_kaydet() çağrısına kadar yüklenmez
    - ImportError sessiz, Exception loglanır
    """

    def __init__(self):
        self._entries: Dict[str, Dict] = {}
        self._loaded: Dict[str, Any] = {}

    def ekle(self, mod_adi: str, kayit_fn: Optional[str] = None):
        """Modülü lazy kuyruğa ekle.

        Args:
            mod_adi: Import edilecek modül adı
            kayit_fn: motor_kaydet() çağıracak fonksiyon adı (None=varsayılan)
        """
        self._entries[mod_adi] = {
            "kayit_fn": kayit_fn or "motor_kaydet",
            "yuklendi": False,
        }

    def yukle(self, mod_adi: str, motor: Any) -> bool:
        """Tek bir modülü yükle ve motor'a kaydet."""
        if mod_adi in self._loaded:
            return True
        if mod_adi not in self._entries:
            return False

        kayit = self._entries[mod_adi]
        try:
            mod = importlib.import_module(mod_adi)
            kayit_fn = getattr(mod, kayit["kayit_fn"], None)
            if kayit_fn:
                kayit_fn(motor)
            kayit["yuklendi"] = True
            self._loaded[mod_adi] = mod
            return True
        except ImportError:
            return False  # Sessiz
        except Exception as e:
            import logging
            logging.getLogger("motor").warning(
                f"Modül yükleme hatası: {mod_adi}: {type(e).__name__}: {e}"
            )
            return False

    def hepsini_yukle(self, motor: Any) -> List[str]:
        """Tüm modülleri yükle (arkaplan çağrısı için)."""
        hatalar = []
        for mod_adi in self._entries:
            if not self.yukle(mod_adi, motor):
                pass  # ImportError normal
        return hatalar

    def durum(self) -> Dict[str, str]:
        """Modül durumlarını döndür."""
        return {
            mod_adi: "✅" if kayit["yuklendi"] else "⏳"
            for mod_adi, kayit in self._entries.items()
        }


# ── MCP Tool Bridge ──────────────────────────────────────────────────────────

class MCPToolBridge:
    """
    config.yaml'deki mcp_servers araçlarına lazy bridge.

    Gateway üzerinden MCP araçlarını motor.py seviyesinde kullanılabilir yapar.
    """

    def __init__(self, config_yolu: Optional[str] = None):
        self._config_yolu = config_yolu or self._varsayilan_config_yolu()
        self._mcp_servers: Dict[str, Dict] = {}
        self._tools: Dict[str, Callable] = {}
        self._yuklendi = False

    @staticmethod
    def _varsayilan_config_yolu() -> str:
        """Varsayılan config.yaml yolunu döndür."""
        home = os.path.expanduser("~")
        return os.path.join(
            home, "AppData", "Local", "hermes", "profiles", "reymen", "config.yaml"
        )

    def _yukle_config(self):
        """config.yaml'den MCP server'ları oku."""
        if self._yuklendi:
            return
        try:
            import yaml
            with open(self._config_yolu, encoding="utf-8") as f:
                config = yaml.safe_load(f)
            mcp = config.get("mcp_servers", {})
            for name, srv in mcp.items():
                self._mcp_servers[name] = {
                    "command": srv.get("command"),
                    "args": srv.get("args", []),
                    "timeout": srv.get("timeout", 30),
                }
            self._yuklendi = True
        except Exception as e:
            import logging
            logging.getLogger("motor").warning(f"MCP config yüklenemedi: {e}")

    def server_list(self) -> List[str]:
        """MCP server listesini döndür."""
        self._yukle_config()
        return list(self._mcp_servers.keys())

    def tool_list(self, server: str) -> List[str]:
        """MCP server'ın tool listesini döndür (şema olarak)."""
        return [f"mcp_{server}"]

    def server_calistir(self, server: str, tool: str,
                         parametreler: dict = None) -> Any:
        """
        MCP server üzerinden tool çalıştır.

        Not: Bu bir bridge'dir — gerçek MCP execution gateway'den geçer.
        Bu fonksiyon motor.py entegrasyonu için placeholder görevi görür.
        """
        self._yukle_config()
        if server not in self._mcp_servers:
            return f"[Hata]: MCP server '{server}' bulunamadı. Mevcut: {list(self._mcp_servers.keys())}"

        # Gateway üzerinden çağrı — subprocess ile npx çalıştır
        srv = self._mcp_servers[server]
        cmd = [srv["command"]] + [str(a) for a in srv["args"]]

        import subprocess
        try:
            r = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=srv["timeout"],
            )
            return {
                "stdout": r.stdout[:2000],
                "stderr": r.stderr[:500],
                "exit_code": r.returncode,
            }
        except subprocess.TimeoutExpired:
            return f"[Hata]: MCP server '{server}' timeout ({srv['timeout']}s)"
        except Exception as e:
            return f"[Hata]: MCP server '{server}' hatası: {e}"

    def motora_kaydet(self, motor):
        """
        Tüm MCP tool'larını motor.py'ye lazy olarak kaydet.

        Her server için bir MCP_TOOL_{SERVER} aracı oluşturur.
        """
        self._yukle_config()
        for server in self._mcp_servers:
            # Closure ile server adını yakala
            server_adi = server
            tool_adi = f"MCP_{server_adi.upper()}"
            tool_fn = lambda *a, s=server_adi, **kw: self.server_calistir(s, "", kw)
            motor._plugin_arac_kaydet(tool_adi, tool_fn, f"MCP: {server_adi}")


# ── Module Registry ──────────────────────────────────────────────────────────

class ModuleRegistry:
    """Modül kayıt ve lazy loading merkezi."""

    def __init__(self):
        self._modules: Dict[str, LazyModule] = {}
        self._tools: Dict[str, LazyTool] = {}

    def register_module(self, name: str, module_name: str,
                        package: Optional[str] = None,
                        install_hint: Optional[str] = None) -> None:
        self._modules[name] = LazyModule(module_name, package, install_hint)

    def register_tool(self, name: str, module_path: str,
                      function_name: str = "run") -> None:
        self._tools[name] = LazyTool(module_path, function_name)

    def get_module(self, name: str) -> Optional[LazyModule]:
        return self._modules.get(name)

    def get_tool(self, name: str) -> Optional[LazyTool]:
        return self._tools.get(name)

    def is_available(self, name: str) -> bool:
        if name in self._modules:
            return self._modules[name].is_available()
        if name in self._tools:
            return self._tools[name].is_available()
        return False

    def status(self) -> Dict[str, bool]:
        durum = {}
        for name, mod in self._modules.items():
            durum[name] = mod.is_available()
        for name, tool in self._tools.items():
            durum[f"tool:{name}"] = tool.is_available()
        return durum

    def formatla(self) -> str:
        durum = self.status()
        satirlar = [f"📦 Modül Registry ({len(durum)} modül):\n"]
        for name, available in sorted(durum.items()):
            emoji = "✅" if available else "❌"
            satirlar.append(f"  {emoji} {name}")
        return "\n".join(satirlar)


# ── Global Registry ──────────────────────────────────────────────────────────

_registry = None

def get_registry() -> ModuleRegistry:
    global _registry
    if _registry is None:
        _registry = ModuleRegistry()
        _varsayilan_kaydet(_registry)
    return _registry


def _varsayilan_kaydet(reg: ModuleRegistry):
    """Varsayılan modülleri/tool'ları kaydeder."""
    # ReYMeN Memory Provider (Hermes built-in'i override eder)
    reg.register_tool("memory", "reymen.hafiza.reymen_memory_provider", "memory_tool_run")

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


# ── API ──────────────────────────────────────────────────────────────────────

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
