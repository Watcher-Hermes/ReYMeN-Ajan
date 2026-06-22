# -*- coding: utf-8 -*-
"""ReYMeN_cli/subcommands/hooks.py — hooks alt komutu."""
from __future__ import annotations
import argparse


def build_hooks_parser(subparsers=None) -> argparse.ArgumentParser:
    """'hooks' alt komut parser'ını oluştur."""
    if subparsers is not None:
        p = subparsers.add_parser('hooks', help='hooks komutu')
    else:
        p = argparse.ArgumentParser(prog='ReYMeN hooks')
    return p


def run_hooks(args=None) -> None:
    """'hooks' komutunu çalıştır."""
    pass


if __name__ == '__main__':
    p = build_hooks_parser()
    print(f'{p.prog} hazır.')
