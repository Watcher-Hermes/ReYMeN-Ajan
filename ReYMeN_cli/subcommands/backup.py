# -*- coding: utf-8 -*-
"""ReYMeN_cli/subcommands/backup.py — backup alt komutu."""
from __future__ import annotations
import argparse


def build_backup_parser(subparsers=None) -> argparse.ArgumentParser:
    """'backup' alt komut parser'ını oluştur."""
    if subparsers is not None:
        p = subparsers.add_parser('backup', help='backup komutu')
    else:
        p = argparse.ArgumentParser(prog='ReYMeN backup')
    return p


def run_backup(args=None) -> None:
    """'backup' komutunu çalıştır."""
    pass


if __name__ == '__main__':
    p = build_backup_parser()
    print(f'{p.prog} hazır.')
