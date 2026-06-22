# -*- coding: utf-8 -*-
"""ReYMeN_cli/subcommands/plugins.py — plugins alt komutu."""
from __future__ import annotations
import argparse


def build_plugins_parser(subparsers=None) -> argparse.ArgumentParser:
    """'plugins' alt komut parser'ını oluştur."""
    if subparsers is not None:
        p = subparsers.add_parser('plugins', help='plugins komutu')
    else:
        p = argparse.ArgumentParser(prog='ReYMeN plugins')
    return p


def run_plugins(args=None) -> None:
    """'plugins' komutunu çalıştır."""
    pass


if __name__ == '__main__':
    p = build_plugins_parser()
    print(f'{p.prog} hazır.')
