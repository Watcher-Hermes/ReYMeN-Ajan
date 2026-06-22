# -*- coding: utf-8 -*-
"""ReYMeN_cli/subcommands/dashboard.py — dashboard alt komutu."""
from __future__ import annotations
import argparse


def build_dashboard_parser(subparsers=None) -> argparse.ArgumentParser:
    """'dashboard' alt komut parser'ını oluştur."""
    if subparsers is not None:
        p = subparsers.add_parser('dashboard', help='dashboard komutu')
    else:
        p = argparse.ArgumentParser(prog='ReYMeN dashboard')
    return p


def run_dashboard(args=None) -> None:
    """'dashboard' komutunu çalıştır."""
    pass


if __name__ == '__main__':
    p = build_dashboard_parser()
    print(f'{p.prog} hazır.')
