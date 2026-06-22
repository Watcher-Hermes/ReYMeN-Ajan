# -*- coding: utf-8 -*-
"""ReYMeN_cli/subcommands/debug.py — debug alt komutu."""
from __future__ import annotations
import argparse


def build_debug_parser(subparsers=None) -> argparse.ArgumentParser:
    """'debug' alt komut parser'ını oluştur."""
    if subparsers is not None:
        p = subparsers.add_parser('debug', help='debug komutu')
    else:
        p = argparse.ArgumentParser(prog='ReYMeN debug')
    return p


def run_debug(args=None) -> None:
    """'debug' komutunu çalıştır."""
    pass


if __name__ == '__main__':
    p = build_debug_parser()
    print(f'{p.prog} hazır.')
