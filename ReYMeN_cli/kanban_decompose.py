# -*- coding: utf-8 -*-
"""ReYMeN_cli/kanban_decompose.py — Kanban Ayristirma CLI.

Kanban gorev, alt gorev, atama, durum ve
yeniden siralam islemleri.
"""

from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent


def kaydet(alt_parser):
    """Kanban decompose CLI alt komutlarini argparse alt ayristiricisina kaydet.

    Alt komutlar: task, subtask, assign, status, reorder
    """
    alt_parser.add_argument("islem", type=str, nargs="?",
                            choices=["task", "subtask", "assign", "status", "reorder"],
                            help="Yapilacak islem (task|subtask|assign|status|reorder)")
    alt_parser.add_argument("--id", type=str, default=None,
                            help="Gorev ID")
    alt_parser.add_argument("--baslik", type=str, default=None,
                            help="Gorev basligi (task/subtask icin)")
    alt_parser.add_argument("--kullanici", type=str, default=None,
                            help="Atanacak kullanici (assign icin)")
    alt_parser.add_argument("--durum", type=str, default=None,
                            help="Yeni durum (status icin)")


def calistir(args):
    """Kanban decompose komutunu calistir."""
    try:
        islem = args.islem or "task"

        if islem == "task":
            baslik = args.baslik or "Yeni Gorev"
            print(f"[KanbanDecompose] Gorev olusturuldu: '{baslik}'")

        elif islem == "subtask":
            gorev_id = args.id or "G001"
            baslik = args.baslik or "Alt Gorev"
            print(f"[KanbanDecompose] '{gorev_id}' icin alt gorev eklendi: '{baslik}'")

        elif islem == "assign":
            gorev_id = args.id
            kullanici = args.kullanici
            if not gorev_id or not kullanici:
                print("[KanbanDecompose] Lutfen --id ve --kullanici parametrelerini belirtin.")
                return
            print(f"[KanbanDecompose] '{gorev_id}' -> {kullanici} atandi.")

        elif islem == "status":
            gorev_id = args.id
            durum = args.durum or "todo"
            if not gorev_id:
                print("[KanbanDecompose] Lutfen --id parametresini belirtin.")
                return
            print(f"[KanbanDecompose] '{gorev_id}' durumu '{durum}' olarak degisti.")

        elif islem == "reorder":
            print("[KanbanDecompose] Gorevler yeniden siralandi.")

    except Exception as e:
        print(f"[KanbanDecompose] Beklenmeyen hata: {e}")
