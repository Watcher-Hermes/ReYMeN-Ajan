# -*- coding: utf-8 -*-
"""ReYMeN_cli/subcommands/import_cmd.py — import_cmd alt komutu."""
from __future__ import annotations
import argparse


def build_import_cmd_parser(subparsers=None) -> argparse.ArgumentParser:
    """'import_cmd' alt komut parser'ını oluştur."""
    if subparsers is not None:
        p = subparsers.add_parser('import_cmd', help='import_cmd komutu')
    else:
        p = argparse.ArgumentParser(prog='ReYMeN import_cmd')
    return p


def run_import_cmd(args=None) -> None:
    """'import_cmd' komutunu çalıştır."""
    pass


if __name__ == '__main__':
    p = build_import_cmd_parser()
    print(f'{p.prog} hazır.')
