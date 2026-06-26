# -*- coding: utf-8 -*-
"""
swarm_tool.py — ReYMeN Multi-Agent Swarm Tool

Çoklu ajan koordinasyonu: task dağıtımı, paralel çalıştırma, sonuç birleştirme.
Sub-agent'ları yönetir, bağımsız task'ları paralel işletir.

Kullanım:
    from reymen.hermes.tools.swarm_tool import SwarmTool
    swarm = SwarmTool()
    sonuc = swarm.run_parallel([
        {"name": "arama", "prompt": "Python nedir?", "provider": "deepseek"},
        {"name": "arama2", "prompt": "JavaScript nedir?", "provider": "deepseek"},
    ])
    print(sonuc)
"""

import json
import logging
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)


@dataclass
class SwarmTask:
    """Swarm task tanımı."""
    name: str
    prompt: str
    provider: str = "deepseek"
    model: str = "deepseek-v4-flash"
    context: Optional[dict] = None
    timeout: int = 60


@dataclass
class SwarmResult:
    """Swarm task sonucu."""
    name: str
    success: bool
    output: str = ""
    error: str = ""
    duration: float = 0.0
    task: Optional[SwarmTask] = None


class SwarmTool:
    """
    Multi-agent swarm — paralel task dağıtım ve koordinasyon.

    Örnek:
        swarm = SwarmTool()
        sonuc = swarm.run_parallel([
            SwarmTask(name="soru1", prompt="Türkiye'nin başkenti?"),
            SwarmTask(name="soru2", prompt="Python'da decorator nedir?"),
        ])
        for r in sonuc:
            print(f"{r.name}: {'✅' if r.success else '❌'} {r.output[:100]}")
    """

    def __init__(self, max_workers: int = 3):
        self._max_workers = max_workers
        self._executor = ThreadPoolExecutor(max_workers=max_workers)
        self._results: list[SwarmResult] = []
        self._lock = threading.Lock()

    # ── Paralel Çalıştırma ──────────────────────────────────────────────────

    def run_parallel(self, tasks: list[SwarmTask]) -> list[SwarmResult]:
        """Task'ları paralel çalıştır.

        Args:
            tasks: SwarmTask listesi

        Returns:
            list[SwarmResult]: Sonuç listesi
        """
        self._results = []
        futures = {}

        for task in tasks:
            future = self._executor.submit(self._run_single, task)
            futures[future] = task

        for future in as_completed(futures):
            task = futures[future]
            try:
                result = future.result()
            except Exception as e:
                result = SwarmResult(
                    name=task.name,
                    success=False,
                    error=f"Future hatasi: {e}",
                    task=task,
                )
            with self._lock:
                self._results.append(result)

        # Sırala (giriş sırasına göre)
        task_names = [t.name for t in tasks]
        self._results.sort(
            key=lambda r: task_names.index(r.name) if r.name in task_names else 999
        )
        return self._results

    def run_sequential(self, tasks: list[SwarmTask]) -> list[SwarmResult]:
        """Task'ları sıralı çalıştır (birbirine bağımlı task'lar için).

        Args:
            tasks: SwarmTask listesi

        Returns:
            list[SwarmResult]: Sonuç listesi
        """
        self._results = []
        for task in tasks:
            result = self._run_single(task)
            self._results.append(result)
            if not result.success:
                logger.warning(
                    "Task '%s' basarisiz. Sonraki task'lar iptal.",
                    task.name
                )
                break
        return self._results

    def run_pipeline(
        self, tasks: list[SwarmTask],
        context_field: str = "previous_output"
    ) -> list[SwarmResult]:
        """Pipeline modu: her task bir öncekinin çıktısını alır.

        Args:
            tasks: SwarmTask listesi
            context_field: Önceki çıktının hangi alana yazılacağı

        Returns:
            list[SwarmResult]: Pipeline sonuçları
        """
        self._results = []
        previous_output = ""

        for i, task in enumerate(tasks):
            # Önceki çıktıyı context'e ekle
            enriched = SwarmTask(
                name=task.name,
                prompt=(
                    f"{task.prompt}\n\n---\n"
                    f"Onceki adim ciktisi:\n{previous_output[:2000]}"
                    if previous_output else task.prompt
                ),
                provider=task.provider,
                model=task.model,
                context=task.context,
                timeout=task.timeout,
            )
            result = self._run_single(enriched)
            self._results.append(result)

            if result.success:
                previous_output = result.output
            else:
                logger.warning(
                    "Pipeline adim %d basarisiz (%s). Durduruluyor.",
                    i + 1, task.name
                )
                break

        return self._results

    # ── Tek Task Çalıştırma ──────────────────────────────────────────────────

    def _run_single(self, task: SwarmTask) -> SwarmResult:
        """Tek task çalıştır (LLM çağrısı simülasyonu).

        Gerçek LLM entegrasyonu için bu metodu provider çağrısıyla değiştirin.

        Args:
            task: SwarmTask

        Returns:
            SwarmResult
        """
        baslangic = time.time()
        try:
            # LLM çağrısı (simülasyon)
            # Gerçek implementasyonda burada provider çağrısı yapılır
            output = self._simulate_llm(task.prompt)
            sure = time.time() - baslangic

            return SwarmResult(
                name=task.name,
                success=True,
                output=output,
                duration=round(sure, 2),
                task=task,
            )
        except Exception as e:
            sure = time.time() - baslangic
            return SwarmResult(
                name=task.name,
                success=False,
                error=str(e),
                duration=round(sure, 2),
                task=task,
            )

    @staticmethod
    def _simulate_llm(prompt: str) -> str:
        """LLM çağrısı simülasyonu.

        Notes:
            Gerçek kullanımda bu metod provider API'sini çağırmalı.
            Şu an mock olarak prompt'u aynen döndürür.
        """
        return f"[Swarm] Isleme alindi ({len(prompt)} karakter)"

    # ── Sonuç İşleme ────────────────────────────────────────────────────────

    def get_summary(self, results: list[SwarmResult]) -> dict:
        """Swarm sonuçlarını özetle.

        Args:
            results: SwarmResult listesi

        Returns:
            dict: Özet istatistikler
        """
        total = len(results)
        basarili = sum(1 for r in results if r.success)
        basarisiz = total - basarili
        toplam_sure = sum(r.duration for r in results)

        return {
            "total": total,
            "success": basarili,
            "failed": basarisiz,
            "total_duration": round(toplam_sure, 2),
            "avg_duration": round(toplam_sure / total, 2) if total else 0,
            "success_rate": round(basarili / total * 100, 1) if total else 0,
        }

    def shutdown(self):
        """Thread pool'u kapat."""
        self._executor.shutdown(wait=True)


# ── CLI Giriş Noktası ─────────────────────────────────────────────────────────

def run(
    islem: str = "demo",
    tasks_json: str = "",
    mode: str = "parallel"
) -> str:
    """Swarm Tool CLI giriş noktası.

    Args:
        islem: "demo" (ornek), "run" (task calistir), "pipeline"
        tasks_json: JSON formatında task listesi
            [{"name": "...", "prompt": "...", "provider": "deepseek"}, ...]
        mode: "parallel" veya "sequential"

    Returns:
        str: JSON formatında sonuç
    """
    swarm = SwarmTool()

    if islem == "demo":
        # Demo task'lar
        tasks = [
            SwarmTask(name="gorev-1", prompt="ReYMeN nedir?"),
            SwarmTask(name="gorev-2", prompt="Hermes Agent nedir?"),
            SwarmTask(name="gorev-3", prompt="Farklari nelerdir?"),
        ]

        if mode == "parallel":
            sonuc = swarm.run_parallel(tasks)
        else:
            sonuc = swarm.run_sequential(tasks)

        ozet = swarm.get_summary(sonuc)
        return json.dumps(
            {
                "summary": ozet,
                "results": [
                    {
                        "name": r.name,
                        "success": r.success,
                        "output": r.output[:100],
                        "duration": r.duration,
                    }
                    for r in sonuc
                ],
            },
            ensure_ascii=False, indent=2
        )

    elif islem == "run" and tasks_json:
        try:
            task_list = json.loads(tasks_json)
            tasks = []
            for t in task_list:
                tasks.append(SwarmTask(
                    name=t.get("name", "isimsiz"),
                    prompt=t.get("prompt", ""),
                    provider=t.get("provider", "deepseek"),
                    model=t.get("model", "deepseek-v4-flash"),
                    timeout=t.get("timeout", 60),
                ))

            if mode == "parallel":
                sonuc = swarm.run_parallel(tasks)
            else:
                sonuc = swarm.run_sequential(tasks)

            ozet = swarm.get_summary(sonuc)
            return json.dumps(
                {
                    "summary": ozet,
                    "results": [
                        {
                            "name": r.name,
                            "success": r.success,
                            "duration": r.duration,
                        }
                        for r in sonuc
                    ],
                },
                ensure_ascii=False, indent=2
            )
        except json.JSONDecodeError as e:
            return json.dumps(
                {"success": False, "error": f"JSON cozulemedi: {e}"},
                ensure_ascii=False
            )

    else:
        return json.dumps(
            {
                "success": False,
                "error": f"Bilinmeyen islem: {islem}. "
                         f"Secenekler: demo, run (--tasks_json '[...]')",
                "usage": {
                    "demo": "Ornek paralel/sequential calistirma",
                    "run": "JSON task listesi ile calistirma",
                },
            },
            ensure_ascii=False
        )


if __name__ == "__main__":
    import sys
    args = sys.argv[1:]
    islem = args[0] if args else "demo"
    tj = args[1] if len(args) > 1 else ""
    mod = args[2] if len(args) > 2 else "parallel"
    print(run(islem, tj, mod))
