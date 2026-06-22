# -*- coding: utf-8 -*-
"""ReYMeN_cli/subcommands/model.py — model alt komutu."""
from __future__ import annotations
import argparse


def build_model_parser(subparsers=None) -> argparse.ArgumentParser:
    """'model' alt komut parser'ını oluştur."""
    if subparsers is not None:
        p = subparsers.add_parser('model', help='model komutu')
    else:
        p = argparse.ArgumentParser(prog='ReYMeN model')
    return p


def run_model(args=None) -> None:
    """'model' komutunu çalıştır."""
    pass


if __name__ == '__main__':
    p = build_model_parser()
    print(f'{p.prog} hazır.')
