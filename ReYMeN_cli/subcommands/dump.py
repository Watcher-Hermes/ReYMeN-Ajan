# -*- coding: utf-8 -*-
"""ReYMeN_cli/subcommands/dump.py — dump alt komutu."""
from __future__ import annotations
import argparse


def build_dump_parser(subparsers=None) -> argparse.ArgumentParser:
    """'dump' alt komut parser'ını oluştur."""
    if subparsers is not None:
        p = subparsers.add_parser('dump', help='dump komutu')
    else:
        p = argparse.ArgumentParser(prog='ReYMeN dump')
    return p


def run_dump(args=None) -> None:
    """'dump' komutunu çalıştır."""
    pass


if __name__ == '__main__':
    p = build_dump_parser()
    print(f'{p.prog} hazır.')
