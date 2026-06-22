# -*- coding: utf-8 -*-
"""ReYMeN_cli/subcommands/pairing.py — pairing alt komutu."""
from __future__ import annotations
import argparse


def build_pairing_parser(subparsers=None) -> argparse.ArgumentParser:
    """'pairing' alt komut parser'ını oluştur."""
    if subparsers is not None:
        p = subparsers.add_parser('pairing', help='pairing komutu')
    else:
        p = argparse.ArgumentParser(prog='ReYMeN pairing')
    return p


def run_pairing(args=None) -> None:
    """'pairing' komutunu çalıştır."""
    pass


if __name__ == '__main__':
    p = build_pairing_parser()
    print(f'{p.prog} hazır.')
