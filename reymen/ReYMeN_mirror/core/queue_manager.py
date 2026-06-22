"""
queue_manager.py — Gorev kuyrugu yoneticisi.

Buyuk olcekte (100+ kaynak) islerin kuyruga alinip
sirayla islenmesini saglar. Kucuk olcekte dogrudan
Orchestrator kullanilir.
"""

import asyncio
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from loguru import logger


class TaskPriority(Enum):
    """Gorev oncelik seviyeleri."""
    HIGH = 0
    NORMAL = 1
    LOW = 2


@dataclass(order=True)
class Task:
    """Kuyruktaki tek bir gorev."""
    query: str = field(compare=False)
    name: str = field(default="", compare=False)
    priority: TaskPriority = TaskPriority.NORMAL
    created_at: float = field(default_factory=lambda: asyncio.get_event_loop().time(), compare=False)


class QueueManager:
    """Asenkron gorev kuyrugu yoneticisi."""

    def __init__(self, max_workers: int = 5):
        self.queue: asyncio.PriorityQueue = asyncio.PriorityQueue()
        self.max_workers = max_workers
        self._workers: list[asyncio.Task] = []
        self._running = False
        self._handler = None

    def set_handler(self, handler):
        """Gorev isleme fonksiyonunu ata (ornegin orchestrator.process_query)."""
        self._handler = handler

    async def enqueue(self, query: str, name: str = "", priority: TaskPriority = TaskPriority.NORMAL) -> None:
        """Gorevi kuyruga ekle."""
        task = Task(
            query=query,
            name=name,
            priority=priority,
        )
        await self.queue.put(task)
        logger.debug(f"Kuyruga eklendi: [{name}] '{query}' (priority: {priority.name})")

    async def _worker(self, worker_id: int) -> None:
        """Tek bir worker — kuyruktan gorev alir, isler."""
        while self._running:
            try:
                task = await asyncio.wait_for(self.queue.get(), timeout=1.0)
            except asyncio.TimeoutError:
                continue

            if not self._handler:
                logger.warning(f"[Worker {worker_id}] Handler atanmamis")
                self.queue.task_done()
                continue

            try:
                logger.info(f"[Worker {worker_id}] Basliyor: [{task.name}]")
                result = await self._handler(task.query)
                if result:
                    logger.success(f"[Worker {worker_id}] Tamam: [{task.name}]")
                else:
                    logger.warning(f"[Worker {worker_id}] Sonuc yok: [{task.name}]")
            except Exception as e:
                logger.error(f"[Worker {worker_id}] Hata: [{task.name}] -> {e}")
            finally:
                self.queue.task_done()

    def start(self) -> None:
        """Worker'lari baslat."""
        self._running = True
        for i in range(self.max_workers):
            worker = asyncio.create_task(self._worker(i))
            self._workers.append(worker)
        logger.info(f"QueueManager basladi: {self.max_workers} worker")

    async def stop(self) -> None:
        """Worker'lari durdur."""
        self._running = False
        if self._workers:
            await asyncio.gather(*self._workers, return_exceptions=True)
            self._workers.clear()
        logger.info("QueueManager durduruldu")

    @property
    def pending_count(self) -> int:
        """Bekleyen gorev sayisi."""
        return self.queue.qsize()
