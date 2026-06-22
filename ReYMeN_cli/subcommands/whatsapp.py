# -*- coding: utf-8 -*-
"""ReYMeN_cli/subcommands/whatsapp.py — whatsapp alt komutu."""
from __future__ import annotations
import argparse


def build_whatsapp_parser(subparsers=None) -> argparse.ArgumentParser:
    """'whatsapp' alt komut parser'ını oluştur."""
    if subparsers is not None:
        p = subparsers.add_parser('whatsapp', help='whatsapp komutu')
    else:
        p = argparse.ArgumentParser(prog='ReYMeN whatsapp')
    return p


def run_whatsapp(args=None) -> None:
    """'whatsapp' komutunu çalıştır."""
    pass


if __name__ == '__main__':
    p = build_whatsapp_parser()
    print(f'{p.prog} hazır.')
