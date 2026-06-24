# -*- coding: utf-8 -*-
"""
session_search_fts5.py — FTS5 destekli session arama.
Hermes Agent session_search karşılığı.

Kullanım:
    from reymen.sistem.session_search_fts5 import session_search
    sonuclar = session_search(query="intent recognition", limit=5)
"""

from __future__ import annotations
import os
import re
import sqlite3
from pathlib import Path
from typing import Optional, Dict, List
from dataclasses import dataclass, field


@dataclass
class SearchResult:
    """Arama sonucu."""
    session_id: str
    title: str
    when: str
    source: str
    snippet: str
    messages: List[Dict] = field(default_factory=list)


class SessionSearchFTS5:
    """FTS5 destekli session arama motoru."""

    def __init__(self, db_path: str = None):
        if db_path is None:
            proje_kok = Path(__file__).parent.parent.parent
            self.db_path = str(proje_kok / ".ReYMeN" / "session.db")
        else:
            self.db_path = db_path

    def session_search(self, query: str = None, session_id: str = None,
                       limit: int = 3, sort: str = "relevance") -> List[SearchResult]:
        """Session ara veya belirli bir session'ı oku."""
        if session_id:
            return self._read_session(session_id)
        if query:
            return self._search_fts5(query, limit, sort)
        return self._browse_recent(limit)

    def _search_fts5(self, query: str, limit: int, sort: str) -> List[SearchResult]:
        """FTS5 ile full-text search."""
        if not os.path.exists(self.db_path):
            return []

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # FTS5 tablosu var mı kontrol et
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='messages_fts'"
            )
            if not cursor.fetchone():
                # FTS5 tablosu yoksa normal search
                return self._search_like(query, limit)

            # FTS5 search
            if sort == "newest":
                sql = """
                    SELECT m.session_id, s.title, s.created_at, s.source,
                           snippet(messages_fts, 0, '<b>', '</b>', '...', 30)
                    FROM messages_fts f
                    JOIN messages m ON m.rowid = f.rowid
                    JOIN sessions s ON s.id = m.session_id
                    WHERE messages_fts MATCH ?
                    ORDER BY m.created_at DESC
                    LIMIT ?
                """
            else:
                sql = """
                    SELECT m.session_id, s.title, s.created_at, s.source,
                           snippet(messages_fts, 0, '<b>', '</b>', '...', 30)
                    FROM messages_fts f
                    JOIN messages m ON m.rowid = f.rowid
                    JOIN sessions s ON s.id = m.session_id
                    WHERE messages_fts MATCH ?
                    ORDER BY rank
                    LIMIT ?
                """

            cursor.execute(sql, (query, limit))
            results = []
            for row in cursor.fetchall():
                results.append(SearchResult(
                    session_id=row[0],
                    title=row[1] or "Untitled",
                    when=row[2] or "",
                    source=row[3] or "",
                    snippet=row[4] or "",
                ))
            conn.close()
            return results

        except Exception as e:
            print(f"[SessionSearch] Hata: {e}")
            return []

    def _search_like(self, query: str, limit: int) -> List[SearchResult]:
        """LIKE ile basit search (FTS5 yoksa)."""
        if not os.path.exists(self.db_path):
            return []

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            sql = """
                SELECT m.session_id, s.title, s.created_at, s.source, m.content
                FROM messages m
                JOIN sessions s ON s.id = m.session_id
                WHERE m.content LIKE ?
                ORDER BY m.created_at DESC
                LIMIT ?
            """
            cursor.execute(sql, (f"%{query}%", limit))
            results = []
            for row in cursor.fetchall():
                # Snippet oluştur
                content = row[4] or ""
                idx = content.lower().find(query.lower())
                if idx >= 0:
                    start = max(0, idx - 50)
                    end = min(len(content), idx + len(query) + 50)
                    snippet = f"...{content[start:end]}..."
                else:
                    snippet = content[:100]

                results.append(SearchResult(
                    session_id=row[0],
                    title=row[1] or "Untitled",
                    when=row[2] or "",
                    source=row[3] or "",
                    snippet=snippet,
                ))
            conn.close()
            return results

        except Exception as e:
            print(f"[SessionSearch] Hata: {e}")
            return []

    def _browse_recent(self, limit: int) -> List[SearchResult]:
        """Son session'ları listele."""
        if not os.path.exists(self.db_path):
            return []

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            sql = """
                SELECT id, title, created_at, source
                FROM sessions
                ORDER BY created_at DESC
                LIMIT ?
            """
            cursor.execute(sql, (limit,))
            results = []
            for row in cursor.fetchall():
                results.append(SearchResult(
                    session_id=row[0],
                    title=row[1] or "Untitled",
                    when=row[2] or "",
                    source=row[3] or "",
                    snippet="",
                ))
            conn.close()
            return results

        except Exception as e:
            print(f"[SessionSearch] Hata: {e}")
            return []

    def _read_session(self, session_id: str) -> List[SearchResult]:
        """Belirli bir session'ın mesajlarını oku."""
        if not os.path.exists(self.db_path):
            return []

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Session bilgisi
            cursor.execute("SELECT title, created_at, source FROM sessions WHERE id=?",
                           (session_id,))
            row = cursor.fetchone()
            if not row:
                conn.close()
                return []

            # Mesajlar
            cursor.execute("""
                SELECT role, content, created_at
                FROM messages
                WHERE session_id=?
                ORDER BY created_at
            """, (session_id,))
            messages = []
            for msg in cursor.fetchall():
                messages.append({
                    "role": msg[0],
                    "content": (msg[1] or "")[:500],
                    "when": msg[2] or "",
                })

            conn.close()
            return [SearchResult(
                session_id=session_id,
                title=row[0] or "Untitled",
                when=row[1] or "",
                source=row[2] or "",
                snippet=f"{len(messages)} mesaj",
                messages=messages,
            )]

        except Exception as e:
            print(f"[SessionSearch] Hata: {e}")
            return []


# ── Global instance ──────────────────────────────────────────────────────
_searcher: Optional[SessionSearchFTS5] = None

def get_searcher() -> SessionSearchFTS5:
    global _searcher
    if _searcher is None:
        _searcher = SessionSearchFTS5()
    return _searcher

def session_search(query: str = None, session_id: str = None,
                   limit: int = 3, sort: str = "relevance") -> List[SearchResult]:
    """Kısa yol: session ara."""
    return get_searcher().session_search(query, session_id, limit, sort)
