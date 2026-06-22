# -*- coding: utf-8 -*-
"""ReYMeN_cli/subcommands/uninstall.py — uninstall alt komutu."""
from __future__ import annotations
import argparse


def build_uninstall_parser(subparsers=None) -> argparse.ArgumentParser:
    """'uninstall' alt komut parser'ını oluştur."""
    if subparsers is not None:
        p = subparsers.add_parser('uninstall', help='uninstall komutu')
    else:
        p = argparse.ArgumentParser(prog='ReYMeN uninstall')
    return p


def run_uninstall(args=None) -> None:
    """'uninstall' komutunu çalıştır."""
    pass


if __name__ == '__main__':
    p = build_uninstall_parser()
    print(f'{p.prog} hazır.')
