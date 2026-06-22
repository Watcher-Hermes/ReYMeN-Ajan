# -*- coding: utf-8 -*-
"""ReYMeN_cli/subcommands/acp.py — acp alt komutu."""
from __future__ import annotations
import argparse


def build_acp_parser(subparsers=None) -> argparse.ArgumentParser:
    """'acp' alt komut parser'ını oluştur."""
    if subparsers is not None:
        p = subparsers.add_parser('acp', help='acp komutu')
    else:
        p = argparse.ArgumentParser(prog='ReYMeN acp')
    return p


def run_acp(args=None) -> None:
    """'acp' komutunu çalıştır."""
    pass


if __name__ == '__main__':
    p = build_acp_parser()
    print(f'{p.prog} hazır.')
