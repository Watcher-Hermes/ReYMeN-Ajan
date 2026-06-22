"""
main.py — ReYMeN Bilgi Ajanı giris noktasi.

Tum sistemi baslatir: DB, scheduler, periyodik calisma.
"""

import asyncio
import sys

from loguru import logger

from storage.db import init_db
from core.scheduler import ReYMeNScheduler


async def main() -> None:
    """Ana giris: DB -> Scheduler -> Bekle."""
    # Log ayari
    logger.add(
        "logs/reymen_{time}.log",
        rotation="1 day",
        retention="7 days",
        level="INFO",
        encoding="utf-8",
    )

    logger.info("ReYMeN Ajan baslatiliyor...")

    # DB olustur
    await init_db()

    # Scheduler baslat
    scheduler = ReYMeNScheduler()
    scheduler.start()

    # Surekli calis
    try:
        while True:
            await asyncio.sleep(60)
            jobs = scheduler.status()
            logger.info(f"Aktif job: {len(jobs)}")
    except (KeyboardInterrupt, SystemExit):
        scheduler.stop()
        logger.info("ReYMeN durduruldu")
    except Exception as e:
        logger.error(f"Kritik hata: {e}")
        scheduler.stop()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
