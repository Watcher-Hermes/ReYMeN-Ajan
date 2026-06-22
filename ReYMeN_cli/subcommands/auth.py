# -*- coding: utf-8 -*-
"""ReYMeN_cli/subcommands/auth.py — auth alt komutu."""
from __future__ import annotations
import argparse


def build_auth_parser(subparsers=None) -> argparse.ArgumentParser:
    """'auth' alt komut parser'ını oluştur."""
    if subparsers is not None:
        p = subparsers.add_parser('auth', help='auth komutu')
    else:
        p = argparse.ArgumentParser(prog='ReYMeN auth')
    return p


def run_auth(args=None) -> None:
    """'auth' komutunu çalıştır."""
    pass


if __name__ == '__main__':
    p = build_auth_parser()
    print(f'{p.prog} hazır.')
