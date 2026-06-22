# -*- coding: utf-8 -*-
"""ReYMeN_cli/subcommands/insights.py — insights alt komutu."""
from __future__ import annotations
import argparse


def build_insights_parser(subparsers=None) -> argparse.ArgumentParser:
    """'insights' alt komut parser'ını oluştur."""
    if subparsers is not None:
        p = subparsers.add_parser('insights', help='insights komutu')
    else:
        p = argparse.ArgumentParser(prog='ReYMeN insights')
    return p


def run_insights(args=None) -> None:
    """'insights' komutunu çalıştır."""
    pass


if __name__ == '__main__':
    p = build_insights_parser()
    print(f'{p.prog} hazır.')
