# -*- coding: utf-8 -*-
"""ReYMeN_cli/subcommands/postinstall.py — postinstall alt komutu."""
from __future__ import annotations
import argparse


def build_postinstall_parser(subparsers=None) -> argparse.ArgumentParser:
    """'postinstall' alt komut parser'ını oluştur."""
    if subparsers is not None:
        p = subparsers.add_parser('postinstall', help='postinstall komutu')
    else:
        p = argparse.ArgumentParser(prog='ReYMeN postinstall')
    return p


def run_postinstall(args=None) -> None:
    """'postinstall' komutunu çalıştır."""
    pass


if __name__ == '__main__':
    p = build_postinstall_parser()
    print(f'{p.prog} hazır.')
