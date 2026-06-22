# -*- coding: utf-8 -*-
"""ReYMeN_cli/kanban.py — Kanban CLI Komutlari.

Kanban gorev yonetimi icin CLI komutlari.
"""

from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent


def kanban_list() -> str:
    """Kanban gorevlerini listele."""
    import sys
    sys.path.insert(0, str(PROJE_KOK))
    try:
        from kanban_orchestrator import KanbanOrchestrator
        k = KanbanOrchestrator()
        return k.listele() or "[Kanban] Gorev yok."
    except Exception as e:
        return f"[Kanban] Hata: {e}"


def kanban_add(baslik: str, aciklama: str = "") -> str:
    """Yeni kanban gorevi ekle."""
    import sys
    sys.path.insert(0, str(PROJE_KOK))
    try:
        from kanban_orchestrator import KanbanOrchestrator
        k = KanbanOrchestrator()
        return k.ekle(baslik, aciklama)
    except Exception as e:
        return f"[Kanban] Hata: {e}"


def kanban_move(gorev_id: str, yeni_durum: str) -> str:
    """Gorev durumunu degistir (todo, doing, done)."""
    import sys
    sys.path.insert(0, str(PROJE_KOK))
    try:
        from kanban_orchestrator import KanbanOrchestrator
        k = KanbanOrchestrator()
        return k.tasi(gorev_id, yeni_durum)
    except Exception as e:
        return f"[Kanban] Hata: {e}"


def kanban_remove(gorev_id: str) -> str:
    """Gorev sil."""
    import sys
    sys.path.insert(0, str(PROJE_KOK))
    try:
        from kanban_orchestrator import KanbanOrchestrator
        k = KanbanOrchestrator()
        return k.sil(gorev_id)
    except Exception as e:
        return f"[Kanban] Hata: {e}"


def kanban_stats() -> str:
    """Kanban istatistikleri."""
    import sys
    sys.path.insert(0, str(PROJE_KOK))
    try:
        from kanban_orchestrator import KanbanOrchestrator
        k = KanbanOrchestrator()
        return k.istatistik()
    except Exception as e:
        return f"[Kanban] Hata: {e}"
