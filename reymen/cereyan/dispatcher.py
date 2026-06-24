# -*- coding: utf-8 -*-
"""dispatcher.py — Tool dispatch orkestratoru.

Akis:
  dispatch(name) -> registry.resolve(name)
                 -> callable=='run' ? executor.calistir_tool(...) : _execute_function(...)
"""

from __future__ import annotations

import importlib
import logging
from typing import Any, Dict, Optional

from tool_registry import ToolRegistry
from tool_executor import ToolExecutor

try:
    from tool_guardrails import ToolGuardrails
except ImportError:
    ToolGuardrails = None

logger = logging.getLogger(__name__)


class ToolDispatcher:
    """Registry + executor uzerinden tool cagrilarini yonetir."""

    def __init__(self, varsayilan_timeout: int = 30):
        self.registry = ToolRegistry()
        self.executor = ToolExecutor()
        self.guardrails = ToolGuardrails() if ToolGuardrails is not None else None
        self._varsayilan_timeout = varsayilan_timeout

    def dispatch(
        self,
        name: str,
        args: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None,
        timeout: int = 30,
    ) -> Dict[str, Any]:
        args = args or {}

        kayit = self.registry.resolve(name)
        if not kayit:
            return {"ok": False, "tool": name, "error": f"Bilinmeyen tool: {name}"}

        module_name = kayit["module"]
        callable_adi = kayit["callable"]

        # Guardrails kontrolü
        if self.guardrails is not None:
            guard = self.guardrails.kontrolet(module_name)
            if isinstance(guard, dict) and not guard.get("guvenli", True):
                return {
                    "ok": False,
                    "tool": name,
                    "error": guard.get("sebep", "Guardrails reddetti"),
                    "guard": guard,
                }

        if callable_adi == "run":
            return self.executor.calistir_tool(module_name, timeout=timeout, **args)
        return self._execute_function(module_name, callable_adi, args, timeout)

    def _execute_function(
        self,
        module_name: str,
        fonksiyon_adi: str,
        args: Dict[str, Any],
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        try:
            mod = importlib.import_module(f"tools.{module_name}")
        except Exception as exc:
            return {"ok": False, "error": f"Modul yuklenemedi (tools.{module_name}): {exc}"}

        fn = getattr(mod, fonksiyon_adi, None)
        if not callable(fn):
            return {"ok": False, "error": f"Fonksiyon bulunamadi: tools.{module_name}.{fonksiyon_adi}"}

        return self.executor.calistir_guvenli(fn, timeout=timeout, **(args or {}))

    def list_tools(self) -> Any:
        return self.registry.liste()

    def tool_schema(self, name: str) -> Dict[str, Any]:
        kayit = self.registry.resolve(name)
        if not kayit:
            return {"error": f"Bilinmeyen tool: {name}"}

        module_name = kayit["module"]
        try:
            mod = importlib.import_module(f"tools.{module_name}")
        except Exception as exc:
            return {"error": f"Modul yuklenemedi (tools.{module_name}): {exc}"}

        schema = getattr(mod, "SCHEMA", None)
        return {"tool": name, "schema": schema if schema is not None else "yok"}


if __name__ == "__main__":
    d = ToolDispatcher()
    print(d.dispatch("shell", {"komut": "echo merhaba"}))
