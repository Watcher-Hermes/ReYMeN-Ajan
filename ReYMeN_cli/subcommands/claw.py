# -*- coding: utf-8 -*-
"""ReYMeN_cli/subcommands/claw.py — claw alt komutu."""
from __future__ import annotations
import argparse


def build_claw_parser(subparsers=None) -> argparse.ArgumentParser:
    """'claw' alt komut parser'ını oluştur."""
    if subparsers is not None:
        p = subparsers.add_parser('claw', help='claw komutu')
    else:
        p = argparse.ArgumentParser(prog='ReYMeN claw')
    return p


def run_claw(args=None) -> None:
    """'claw' komutunu çalıştır."""
    pass


if __name__ == '__main__':
    p = build_claw_parser()
    print(f'{p.prog} hazır.')
