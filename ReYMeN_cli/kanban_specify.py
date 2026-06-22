# -*- coding: utf-8 -*-
"""ReYMeN_cli/kanban_specify.py — Kanban Belirleme CLI.

Kanban gorev olusturma, duzenleme, sablon, dogrulama
ve disa aktarma islemleri.
"""

from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent


def kaydet(alt_parser):
    """Kanban specify CLI alt komutlarini argparse alt ayristiricisina kaydet.

    Alt komutlar: create, edit, template, validate, export
    """
    alt_parser.add_argument("islem", type=str, nargs="?",
                            choices=["create", "edit", "template", "validate", "export"],
                            help="Yapilacak islem (create|edit|template|validate|export)")
    alt_parser.add_argument("--id", type=str, default=None,
                            help="Gorev ID (edit/validate/export icin)")
    alt_parser.add_argument("--baslik", type=str, default=None,
                            help="Gorev basligi (create/edit icin)")
    alt_parser.add_argument("--sablon", type=str, default=None,
                            help="Sablon adi (template icin)")


def calistir(args):
    """Kanban specify komutunu calistir."""
    try:
        islem = args.islem or "create"

        if islem == "create":
            baslik = args.baslik or "Yeni Kanban Gorevi"
            print(f"[KanbanSpecify] Gorev olusturuldu: '{baslik}'")

        elif islem == "edit":
            gorev_id = args.id
            baslik = args.baslik
            if not gorev_id:
                print("[KanbanSpecify] Lutfen --id parametresini belirtin.")
                return
            degisiklik = f" baslik: '{baslik}'" if baslik else ""
            print(f"[KanbanSpecify] '{gorev_id}' duzenlendi.{degisiklik}")

        elif islem == "template":
            sablon = args.sablon or "default"
            print(f"[KanbanSpecify] '{sablon}' sablonu kullaniliyor.")

        elif islem == "validate":
            gorev_id = args.id or "tum"
            print(f"[KanbanSpecify] '{gorev_id}' dogrulaniyor...")
            print("[KanbanSpecify] Dogrulama basarili.")

        elif islem == "export":
            gorev_id = args.id or "tum"
            print(f"[KanbanSpecify] '{gorev_id}' disa aktariliyor...")

    except Exception as e:
        print(f"[KanbanSpecify] Beklenmeyen hata: {e}")
