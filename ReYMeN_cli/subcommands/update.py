# -*- coding: utf-8 -*-
"""ReYMeN_cli/subcommands/update.py — update alt komutu."""
from __future__ import annotations
import argparse


def build_update_parser(subparsers=None) -> argparse.ArgumentParser:
    """'update' alt komut parser'ını oluştur."""
    if subparsers is not None:
        p = subparsers.add_parser('update', help='update komutu')
    else:
        p = argparse.ArgumentParser(prog='ReYMeN update')
    return p


def run_update(args=None) -> None:
    """'update' komutunu çalıştır."""
    pass


if __name__ == '__main__':
    p = build_update_parser()
    print(f'{p.prog} hazır.')
