# -*- coding: utf-8 -*-
"""ReYMeN_cli/subcommands/logout.py — logout alt komutu."""
from __future__ import annotations
import argparse


def build_logout_parser(subparsers=None) -> argparse.ArgumentParser:
    """'logout' alt komut parser'ını oluştur."""
    if subparsers is not None:
        p = subparsers.add_parser('logout', help='logout komutu')
    else:
        p = argparse.ArgumentParser(prog='ReYMeN logout')
    return p


def run_logout(args=None) -> None:
    """'logout' komutunu çalıştır."""
    pass


if __name__ == '__main__':
    p = build_logout_parser()
    print(f'{p.prog} hazır.')
