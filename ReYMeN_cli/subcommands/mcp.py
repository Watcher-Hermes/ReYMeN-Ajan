# -*- coding: utf-8 -*-
"""ReYMeN_cli/subcommands/mcp.py — mcp alt komutu."""
from __future__ import annotations
import argparse


def build_mcp_parser(subparsers=None) -> argparse.ArgumentParser:
    """'mcp' alt komut parser'ını oluştur."""
    if subparsers is not None:
        p = subparsers.add_parser('mcp', help='mcp komutu')
    else:
        p = argparse.ArgumentParser(prog='ReYMeN mcp')
    return p


def run_mcp(args=None) -> None:
    """'mcp' komutunu çalıştır."""
    pass


if __name__ == '__main__':
    p = build_mcp_parser()
    print(f'{p.prog} hazır.')
