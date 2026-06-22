# -*- coding: utf-8 -*-
"""ReYMeN_cli/subcommands/version.py — version alt komutu."""
from __future__ import annotations
import argparse


def build_version_parser(subparsers=None) -> argparse.ArgumentParser:
    """'version' alt komut parser'ını oluştur."""
    if subparsers is not None:
        p = subparsers.add_parser('version', help='version komutu')
    else:
        p = argparse.ArgumentParser(prog='ReYMeN version')
    return p


def run_version(args=None) -> None:
    """'version' komutunu çalıştır."""
    pass


if __name__ == '__main__':
    p = build_version_parser()
    print(f'{p.prog} hazır.')
