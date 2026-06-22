"""
orchestrator.py — Ana yonetici.

Scheduler -> Orchestrator -> Search -> Extract -> Filter -> Summarize -> Save
zincirini yoneten asenkron orkestrator.
"""

import asyncio
import random
from typing import Optional

from loguru import logger
from collectors.web_search import search
from collectors.web_extract import extract
from processors.filter import quality_filter
from processors.summarizer import summarize
from storage.db import save_result, save_raw
from storage.vector_store import store_report


class ReYMeNOrchestrator:
    """Ana yonetici — tum pipeline'i koordine eder."""

    def __init__(self, max_concurrent: int = 20):
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self._report_counter = 0

    async def process_query(self, query: str, job_name: str = None) -> Optional[dict]:
        """
        Tek sorgu icin tam pipeline:
        1. Ara -> 2. Extract -> 3. Filtrele -> 4. Ozetle -> 5. Kaydet
        """
        async with self.semaphore:
            logger.info(f"Isleniyor: '{query}'")
            try:
                # --- 1. ARAMA ---
                search_results = await search(query, max_results=10)

                if not search_results:
                    logger.warning(f"Arama sonucu yok: '{query}'")
                    return None

                urls = [r["url"] for r in search_results]
                logger.info(f"{len(urls)} URL bulundu")

                # --- 2. PARALEL EXTRACT (bot engeli gecikmesi ile) ---
                async def extract_with_delay(url: str) -> Optional[dict]:
                    await asyncio.sleep(random.uniform(0.5, 2.0))
                    return await extract(url)

                raw_contents = await asyncio.gather(
                    *[extract_with_delay(url) for url in urls[:6]],
                    return_exceptions=True,
                )

                # Exception olanlari filtrele
                valid_contents = [
                    c for c in raw_contents
                    if c and not isinstance(c, Exception)
                ]
                logger.info(f"{len(valid_contents)} sayfa cekildi")

                # --- 3. KALITE FILTRESI ---
                filtered = [c for c in valid_contents if quality_filter(c)]
                logger.info(f"{len(filtered)} icerik kalite filtresini gecti")

                if not filtered:
                    logger.warning(f"Filtre sonrasi icerik kalmadi: '{query}'")
                    return None

                # --- 4. HAM ICERIKLERI KAYDET (arka planda) ---
                asyncio.create_task(self._save_raw_batch(filtered))

                # --- 5. OZETLE ---
                result = await summarize(query, filtered)

                if not result or not result.get("summary"):
                    logger.warning(f"Ozet uretilemedi: '{query}'")
                    return None

                # --- 6. RAPORU DB'YE KAYDET ---
                await save_result(query, result, job_name=job_name)

                # --- 7. VEKTOR DB'YE KAYDET ---
                self._report_counter += 1
                store_report(
                    report_id=self._report_counter,
                    query=query,
                    summary=result["summary"],
                    sources=result.get("sources", []),
                )

                logger.success(
                    f"Pipeline tamamlandi: '{query}' "
                    f"| {result['source_count']} kaynak "
                    f"| {len(result['summary'])} karakter"
                )
                return result

            except Exception as e:
                logger.error(f"Pipeline hatasi: '{query}' -> {e}")
                return None

    async def run_batch(self, queries: list[str], job_name: str = None) -> list[dict]:
        """
        Birden fazla sorguyu paralel calistir.
        Semaphore max_concurrent'i asmayi engeller.
        """
        logger.info(f"Batch basladi: {len(queries)} sorgu")

        tasks = [
            self.process_query(q, job_name=job_name)
            for q in queries
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        successful = [r for r in results if r and not isinstance(r, Exception)]
        failed = len(results) - len(successful)

        logger.info(
            f"Batch tamamlandi: "
            f"{len(successful)} basarili / {failed} basarisiz"
        )
        return successful

    async def _save_raw_batch(self, contents: list[dict]) -> None:
        """Ham icerikleri arka planda toplu kaydet."""
        for item in contents:
            try:
                await save_raw(item)
            except Exception as e:
                logger.warning(f"Raw kayit hatasi: {e}")
