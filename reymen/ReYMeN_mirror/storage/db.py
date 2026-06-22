"""
db.py — SQLite veritabani (SQLAlchemy async).

Raporlari ve ham icerikleri kalici olarak saklar.
"""

import json
from datetime import datetime
from typing import Optional

from sqlalchemy import String, Text, DateTime, Integer, select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped
from sqlalchemy.ext.asyncio import async_sessionmaker
from loguru import logger

DATABASE_URL = "sqlite+aiosqlite:///reymen.db"

engine = create_async_engine(DATABASE_URL, echo=False)
SessionFactory = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


class Report(Base):
    """Arastirma raporu tablosu."""
    __tablename__ = "reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    query: Mapped[str] = mapped_column(String(500))
    summary: Mapped[str] = mapped_column(Text)
    sources: Mapped[str] = mapped_column(Text)  # JSON list
    source_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    job_name: Mapped[str] = mapped_column(String(200), nullable=True)


class RawContent(Base):
    """Ham URL icerigi tablosu."""
    __tablename__ = "raw_contents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    url: Mapped[str] = mapped_column(String(2000))
    content: Mapped[str] = mapped_column(Text)
    method: Mapped[str] = mapped_column(String(20))  # curl / browser
    length: Mapped[int] = mapped_column(Integer)
    fetched_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


async def init_db() -> None:
    """Tablolari olustur."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("DB hazir: hermes.db")


async def save_result(query: str, result: dict, job_name: Optional[str] = None) -> None:
    """Raporu kaydet."""
    async with SessionFactory() as session:
        report = Report(
            query=query,
            summary=result.get("summary", ""),
            sources=json.dumps(result.get("sources", [])),
            source_count=result.get("source_count", 0),
            job_name=job_name,
        )
        session.add(report)
        await session.commit()
        logger.info(f"Kaydedildi: '{query}' -> ID:{report.id}")


async def save_raw(item: dict) -> None:
    """Ham icerigi kaydet."""
    async with SessionFactory() as session:
        raw = RawContent(
            url=item["url"],
            content=item.get("content", "")[:50000],  # max 50k karakter
            method=item.get("method", "curl"),
            length=item.get("length", 0),
        )
        session.add(raw)
        await session.commit()


async def get_recent_reports(limit: int = 20) -> list[dict]:
    """Son raporlari getir."""
    async with SessionFactory() as session:
        result = await session.execute(
            select(Report)
            .order_by(Report.created_at.desc())
            .limit(limit)
        )
        reports = result.scalars().all()
        return [
            {
                "id": r.id,
                "query": r.query,
                "summary": r.summary,
                "sources": json.loads(r.sources),
                "created_at": str(r.created_at),
                "job_name": r.job_name,
            }
            for r in reports
        ]


async def search_reports(keyword: str) -> list[dict]:
    """Keyword ile rapor ara."""
    async with SessionFactory() as session:
        result = await session.execute(
            select(Report).where(
                Report.summary.contains(keyword) |
                Report.query.contains(keyword)
            ).order_by(Report.created_at.desc())
        )
        return result.scalars().all()
