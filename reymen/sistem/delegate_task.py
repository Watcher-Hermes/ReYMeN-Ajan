# -*- coding: utf-8 -*-
"""
delegate_task.py — Alt ajana görev dağıtma.
Hermes Agent delegate_task karşılığı.

Kullanım:
    from reymen.sistem.delegate_task import delegate_task
    sonuc = delegate_task("Bu testleri çalıştır", toolsets=["terminal"])
"""

from __future__ import annotations
import os
import sys
import json
import time
import uuid
import subprocess
import threading
from pathlib import Path
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, field


@dataclass
class DelegateTask:
    """Dağıtılan görev tanımı."""
    goal: str
    context: Optional[str] = None
    toolsets: List[str] = field(default_factory=lambda: ["terminal", "file"])
    role: str = "leaf"  # leaf veya orchestrator


@dataclass
class DelegateResult:
    """Görev sonucu."""
    delegation_id: str
    goal: str
    summary: str
    success: bool
    duration: float
    error: Optional[str] = None


class DelegateTaskRunner:
    """Alt ajana görev dağıtma motoru."""

    def __init__(self, max_concurrent: int = 3):
        self.max_concurrent = max_concurrent
        self._aktif_gorevler: Dict[str, threading.Thread] = {}
        self._sonuclar: Dict[str, DelegateResult] = {}

    def delegate_task(self, goal: str, context: str = None,
                      toolsets: List[str] = None) -> DelegateResult:
        """Senkron olarak bir görevi çalıştır."""
        delegation_id = str(uuid.uuid4())[:8]
        start_time = time.time()

        # Basit mod: subprocess ile çalıştır
        try:
            # Python script oluştur
            script_content = self._create_worker_script(goal, context, toolsets)
            script_path = Path(__file__).parent / f"_delegate_worker_{delegation_id}.py"
            script_path.write_text(script_content, encoding="utf-8")

            # Çalıştır
            result = subprocess.run(
                [sys.executable, str(script_path)],
                capture_output=True,
                text=True,
                timeout=300,  # 5 dakika timeout
                encoding="utf-8",
                errors="replace",
            )

            # Temizle
            script_path.unlink(missing_ok=True)

            duration = time.time() - start_time

            if result.returncode == 0:
                return DelegateResult(
                    delegation_id=delegation_id,
                    goal=goal,
                    summary=result.stdout.strip()[:2000],
                    success=True,
                    duration=round(duration, 2),
                )
            else:
                return DelegateResult(
                    delegation_id=delegation_id,
                    goal=goal,
                    summary=result.stdout.strip()[:1000],
                    success=False,
                    duration=round(duration, 2),
                    error=result.stderr.strip()[:500],
                )

        except subprocess.TimeoutExpired:
            return DelegateResult(
                delegation_id=delegation_id,
                goal=goal,
                summary="Zaman aşımı (300s)",
                success=False,
                duration=300,
                error="Timeout",
            )
        except Exception as e:
            return DelegateResult(
                delegation_id=delegation_id,
                goal=goal,
                summary=f"Hata: {e}",
                success=False,
                duration=round(time.time() - start_time, 2),
                error=str(e),
            )

    def delegate_task_async(self, goal: str, context: str = None,
                            toolsets: List[str] = None) -> str:
        """Asenkron olarak görevi arka planda çalıştır."""
        delegation_id = str(uuid.uuid4())[:8]

        def worker():
            result = self.delegate_task(goal, context, toolsets)
            self._sonuclar[delegation_id] = result

        thread = threading.Thread(target=worker, daemon=True)
        self._aktif_gorevler[delegation_id] = thread
        thread.start()

        return delegation_id

    def get_result(self, delegation_id: str) -> Optional[DelegateResult]:
        """Görev sonucunu al."""
        return self._sonuclar.get(delegation_id)

    def _create_worker_script(self, goal: str, context: str = None,
                              toolsets: List[str] = None) -> str:
        """Worker script oluştur."""
        toolsets_str = json.dumps(toolsets or ["terminal", "file"])
        context_str = json.dumps(context or "")

        return f'''# -*- coding: utf-8 -*-
"""Delegate worker — otomatik oluşturuldu."""
import sys
import os

# ReYMeN proje yolunu ekle
proje_yolu = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, proje_yolu)

goal = {json.dumps(goal)}
context = {context_str}
toolsets = {toolsets_str}

print(f"[DelegateWorker] Görev: {{goal}}")
print(f"[DelegateWorker] Toolsets: {{toolsets}}")

# Basit görev yürütme
try:
    # Terminal komutu mu?
    if any(k in goal.lower() for k in ["calistir", "run", "test", "kur", "install"]):
        import subprocess, shlex
        # shell=False ile guvenli calistir
        komut_parts = shlex.split(goal)
        sonuc = subprocess.run(
            komut_parts, shell=False, capture_output=True, text=True, timeout=120
        )
        print(f"ÇIKTI:\\n{{sonuc.stdout}}")
        if sonuc.stderr:
            print(f"HATA:\\n{{sonuc.stderr}}")
    else:
        print(f"[DelegateWorker] Görev tamamlandı: {{goal}}")

except Exception as e:
    print(f"[DelegateWorker] Hata: {{e}}")
    sys.exit(1)
'''


# ── Global instance ──────────────────────────────────────────────────────
_runner: Optional[DelegateTaskRunner] = None

def get_runner() -> DelegateTaskRunner:
    global _runner
    if _runner is None:
        _runner = DelegateTaskRunner()
    return _runner

def delegate_task(goal: str, context: str = None,
                  toolsets: List[str] = None) -> DelegateResult:
    """Kısa yol: görevi çalıştır."""
    return get_runner().delegate_task(goal, context, toolsets)

def delegate_task_async(goal: str, context: str = None,
                        toolsets: List[str] = None) -> str:
    """Kısa yol: asenkron görev başlat."""
    return get_runner().delegate_task_async(goal, context, toolsets)
