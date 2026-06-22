# -*- coding: utf-8 -*-
"""ReYMeN_cli/subcommands/login.py — login alt komutu."""
from __future__ import annotations
import argparse


def build_login_parser(subparsers=None) -> argparse.ArgumentParser:
    """'login' alt komut parser'ını oluştur."""
    if subparsers is not None:
        p = subparsers.add_parser('login', help='login komutu')
    else:
        p = argparse.ArgumentParser(prog='ReYMeN login')
    return p


def run_login(args=None) -> None:
    """'login' komutunu çalıştır."""
    pass


if __name__ == '__main__':
    p = build_login_parser()
    print(f'{p.prog} hazır.')
