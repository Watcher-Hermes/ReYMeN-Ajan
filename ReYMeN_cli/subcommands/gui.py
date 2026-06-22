# -*- coding: utf-8 -*-
"""ReYMeN_cli/subcommands/gui.py — gui alt komutu."""
from __future__ import annotations
import argparse


def build_gui_parser(subparsers=None) -> argparse.ArgumentParser:
    """'gui' alt komut parser'ını oluştur."""
    if subparsers is not None:
        p = subparsers.add_parser('gui', help='gui komutu')
    else:
        p = argparse.ArgumentParser(prog='ReYMeN gui')
    return p


def run_gui(args=None) -> None:
    """'gui' komutunu çalıştır."""
    pass


if __name__ == '__main__':
    p = build_gui_parser()
    print(f'{p.prog} hazır.')
