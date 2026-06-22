# -*- coding: utf-8 -*-
"""ReYMeN_cli/subcommands/memory.py — memory alt komutu."""
from __future__ import annotations
import argparse


def build_memory_parser(subparsers=None) -> argparse.ArgumentParser:
    """'memory' alt komut parser'ını oluştur."""
    if subparsers is not None:
        p = subparsers.add_parser('memory', help='memory komutu')
    else:
        p = argparse.ArgumentParser(prog='ReYMeN memory')
    return p


def run_memory(args=None) -> None:
    """'memory' komutunu çalıştır."""
    pass


if __name__ == '__main__':
    p = build_memory_parser()
    print(f'{p.prog} hazır.')
