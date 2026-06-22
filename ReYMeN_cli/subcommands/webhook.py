# -*- coding: utf-8 -*-
"""ReYMeN_cli/subcommands/webhook.py — webhook alt komutu."""
from __future__ import annotations
import argparse


def build_webhook_parser(subparsers=None) -> argparse.ArgumentParser:
    """'webhook' alt komut parser'ını oluştur."""
    if subparsers is not None:
        p = subparsers.add_parser('webhook', help='webhook komutu')
    else:
        p = argparse.ArgumentParser(prog='ReYMeN webhook')
    return p


def run_webhook(args=None) -> None:
    """'webhook' komutunu çalıştır."""
    pass


if __name__ == '__main__':
    p = build_webhook_parser()
    print(f'{p.prog} hazır.')
