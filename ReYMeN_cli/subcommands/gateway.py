# -*- coding: utf-8 -*-
"""ReYMeN_cli/subcommands/gateway.py — gateway alt komutu."""
from __future__ import annotations
import argparse


def build_gateway_parser(subparsers=None) -> argparse.ArgumentParser:
    """'gateway' alt komut parser'ını oluştur."""
    if subparsers is not None:
        p = subparsers.add_parser('gateway', help='gateway komutu')
    else:
        p = argparse.ArgumentParser(prog='ReYMeN gateway')
    return p


def run_gateway(args=None) -> None:
    """'gateway' komutunu çalıştır."""
    pass


if __name__ == '__main__':
    p = build_gateway_parser()
    print(f'{p.prog} hazır.')
