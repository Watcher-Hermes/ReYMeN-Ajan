# -*- coding: utf-8 -*-
"""ReYMeN_cli/subcommands/status.py — status alt komutu."""
from __future__ import annotations
import argparse


def build_status_parser(subparsers=None) -> argparse.ArgumentParser:
    """'status' alt komut parser'ını oluştur."""
    if subparsers is not None:
        p = subparsers.add_parser('status', help='status komutu')
    else:
        p = argparse.ArgumentParser(prog='ReYMeN status')
    return p


def run_status(args=None) -> None:
    """'status' komutunu çalıştır."""
    pass


if __name__ == '__main__':
    p = build_status_parser()
    print(f'{p.prog} hazır.')
