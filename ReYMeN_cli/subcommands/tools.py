# -*- coding: utf-8 -*-
"""ReYMeN_cli/subcommands/tools.py — tools alt komutu."""
from __future__ import annotations
import argparse


def build_tools_parser(subparsers=None) -> argparse.ArgumentParser:
    """'tools' alt komut parser'ını oluştur."""
    if subparsers is not None:
        p = subparsers.add_parser('tools', help='tools komutu')
    else:
        p = argparse.ArgumentParser(prog='ReYMeN tools')
    return p


def run_tools(args=None) -> None:
    """'tools' komutunu çalıştır."""
    pass


if __name__ == '__main__':
    p = build_tools_parser()
    print(f'{p.prog} hazır.')
