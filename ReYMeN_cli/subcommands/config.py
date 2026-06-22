# -*- coding: utf-8 -*-
"""ReYMeN_cli/subcommands/config.py — config alt komutu."""
from __future__ import annotations
import argparse


def build_config_parser(subparsers=None) -> argparse.ArgumentParser:
    """'config' alt komut parser'ını oluştur."""
    if subparsers is not None:
        p = subparsers.add_parser('config', help='config komutu')
    else:
        p = argparse.ArgumentParser(prog='ReYMeN config')
    return p


def run_config(args=None) -> None:
    """'config' komutunu çalıştır."""
    pass


if __name__ == '__main__':
    p = build_config_parser()
    print(f'{p.prog} hazır.')
