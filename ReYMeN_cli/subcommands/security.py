# -*- coding: utf-8 -*-
"""ReYMeN_cli/subcommands/security.py — security alt komutu."""
from __future__ import annotations
import argparse


def build_security_parser(subparsers=None) -> argparse.ArgumentParser:
    """'security' alt komut parser'ını oluştur."""
    if subparsers is not None:
        p = subparsers.add_parser('security', help='security komutu')
    else:
        p = argparse.ArgumentParser(prog='ReYMeN security')
    return p


def run_security(args=None) -> None:
    """'security' komutunu çalıştır."""
    pass


if __name__ == '__main__':
    p = build_security_parser()
    print(f'{p.prog} hazır.')
