# -*- coding: utf-8 -*-
"""ReYMeN_cli/subcommands/logs.py — logs alt komutu."""
from __future__ import annotations
import argparse


def build_logs_parser(subparsers=None) -> argparse.ArgumentParser:
    """'logs' alt komut parser'ını oluştur."""
    if subparsers is not None:
        p = subparsers.add_parser('logs', help='logs komutu')
    else:
        p = argparse.ArgumentParser(prog='ReYMeN logs')
    return p


def run_logs(args=None) -> None:
    """'logs' komutunu çalıştır."""
    pass


if __name__ == '__main__':
    p = build_logs_parser()
    print(f'{p.prog} hazır.')
