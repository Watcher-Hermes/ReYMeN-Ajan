# -*- coding: utf-8 -*-
"""ReYMeN_cli/subcommands/cron.py — cron alt komutu."""
from __future__ import annotations
import argparse


def build_cron_parser(subparsers=None) -> argparse.ArgumentParser:
    """'cron' alt komut parser'ını oluştur."""
    if subparsers is not None:
        p = subparsers.add_parser('cron', help='cron komutu')
    else:
        p = argparse.ArgumentParser(prog='ReYMeN cron')
    return p


def run_cron(args=None) -> None:
    """'cron' komutunu çalıştır."""
    pass


if __name__ == '__main__':
    p = build_cron_parser()
    print(f'{p.prog} hazır.')
