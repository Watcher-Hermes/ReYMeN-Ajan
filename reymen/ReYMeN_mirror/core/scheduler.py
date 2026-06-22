"""
scheduler.py — Zamanlama (APScheduler).

Kaynaklari config.yaml'dan okuyarak periyodik
arastirma gorevleri baslatir.
"""

import asyncio
from typing import Optional

import yaml
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from loguru import logger

from core.orchestrator import ReYMeNOrchestrator


class ReYMeNScheduler:
    """Periyodik arama zamanlayicisi."""

    def __init__(self, config_path: str = "config.yaml"):
        self.scheduler = AsyncIOScheduler(timezone="UTC")
        self.agent = ReYMeNOrchestrator()
        self.config_path = config_path
        self.jobs: dict[str, dict] = {}

    def load_config(self) -> dict:
        """config.yaml dosyasindan kaynaklari oku."""
        with open(self.config_path) as f:
            return yaml.safe_load(f)

    def register_jobs(self) -> None:
        """Config'deki tum kaynaklari job olarak kaydet."""
        config = self.load_config()
        sources = config.get("sources", [])

        for source in sources:
            name = source["name"]
            query = source["query"]
            interval = source.get("interval_min", 60)
            priority = source.get("priority", "normal")

            job = self.scheduler.add_job(
                self._run_query,
                trigger=IntervalTrigger(minutes=interval),
                args=[query, name, priority],
                id=name,
                name=f"ReYMeN:{name}",
                replace_existing=True,
                max_instances=1,          # Ayni is ust uste calismasin
                misfire_grace_time=300,   # 5dk gec baslayabilir
            )
            self.jobs[name] = job
            logger.info(f"Job kayit: [{name}] her {interval} dakika")

        logger.info(f"Toplam {len(sources)} kaynak zamanlandi")

    async def _run_query(self, query: str, name: str, priority: str) -> None:
        """Tek bir sorguyu calistir."""
        logger.info(f"Basliyor: [{name}] -> '{query}'")
        try:
            result = await self.agent.process_query(query)
            if result:
                logger.success(f"Tamamlandi: [{name}]")
            else:
                logger.warning(f"Sonuc yok: [{name}]")
        except Exception as e:
            logger.error(f"Job hatasi: [{name}] -> {e}")

    def start(self) -> None:
        """Zamanlayiciyi baslat."""
        self.register_jobs()
        self.scheduler.start()
        logger.info("ReYMeN Scheduler basladi")

    def stop(self) -> None:
        """Zamanlayiciyi durdur."""
        self.scheduler.shutdown(wait=False)
        logger.info("ReYMeN Scheduler durduruldu")

    def pause_job(self, name: str) -> None:
        """Tek bir job'i durdur."""
        self.scheduler.pause_job(name)
        logger.info(f"Durduruldu: [{name}]")

    def resume_job(self, name: str) -> None:
        """Durdurulan job'i devam ettir."""
        self.scheduler.resume_job(name)
        logger.info(f"Devam etti: [{name}]")

    def status(self) -> list[dict]:
        """Aktif job'larin durumunu listele."""
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                "id": job.id,
                "name": job.name,
                "next_run": str(job.next_run_time),
                "active": job.next_run_time is not None,
            })
        return jobs
