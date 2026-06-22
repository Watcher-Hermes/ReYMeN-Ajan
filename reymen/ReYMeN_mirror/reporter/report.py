"""
report.py — Rapor olusturma ve formatlama.

Arastirma raporlarini okunabilir formata cevirir,
gunluk ozet ve semantik arama ciktisi saglar.
"""

from datetime import datetime

from loguru import logger
from storage.db import get_recent_reports
from storage.vector_store import semantic_search


def format_report(data: dict) -> str:
    """Tek raporu okunabilir formata cevir."""
    lines = [
        f"{'=' * 60}",
        "REYMEN RAPORU",
        f"Saat: {data.get('created_at', datetime.utcnow())}",
        f"{'=' * 60}",
        f"Sorgu   : {data['query']}",
        f"Kaynaklar: {data.get('source_count', 0)} adet",
        f"{'-' * 60}",
        f"{data['summary']}",
        f"{'-' * 60}",
        "Kaynaklar:",
    ]
    for url in data.get("sources", []):
        lines.append(f"  - {url}")
    lines.append("=" * 60)
    return "\n".join(lines)


async def daily_report() -> str:
    """Son 24 saatin tum raporlarini birlestir."""
    reports = await get_recent_reports(limit=50)
    if not reports:
        return "Henuz rapor yok."

    output = [
        f"{'=' * 60}",
        f"REYMEN GUNLUK RAPOR — {datetime.utcnow().strftime('%Y-%m-%d')}",
        f"Toplam {len(reports)} rapor",
        f"{'=' * 60}\n",
    ]
    for r in reports:
        output.append(format_report(r))
        output.append("")

    return "\n".join(output)


async def find_related(query: str) -> str:
    """Semantik arama ile ilgili raporlari bul."""
    hits = semantic_search(query, top_k=3)
    if not hits:
        return f"'{query}' icin benzer rapor bulunamadi."

    output = [f"'{query}' ile ilgili raporlar:\n"]
    for i, hit in enumerate(hits, 1):
        output.append(f"{i}. Benzerlik: {hit['score']}")
        output.append(f"   Sorgu: {hit['metadata']['query']}")
        output.append(f"   Ozet: {hit['summary'][:300]}...")
        output.append("")

    return "\n".join(output)
