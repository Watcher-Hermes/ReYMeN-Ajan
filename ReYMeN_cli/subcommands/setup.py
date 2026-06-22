# -*- coding: utf-8 -*-
"""ReYMeN_cli/subcommands/setup.py — setup alt komutu."""
from __future__ import annotations
import argparse


def build_setup_parser(subparsers=None) -> argparse.ArgumentParser:
    """'setup' alt komut parser'ını oluştur."""
    if subparsers is not None:
        p = subparsers.add_parser('setup', help='setup komutu')
    else:
        p = argparse.ArgumentParser(prog='ReYMeN setup')
    return p


def run_setup(args=None) -> None:
    """'setup' komutunu çalıştır."""
    pass


if __name__ == '__main__':
    p = build_setup_parser()
    print(f'{p.prog} hazır.')
