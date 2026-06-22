# -*- coding: utf-8 -*-
"""ReYMeN_cli/subcommands/slack.py — slack alt komutu."""
from __future__ import annotations
import argparse


def build_slack_parser(subparsers=None) -> argparse.ArgumentParser:
    """'slack' alt komut parser'ını oluştur."""
    if subparsers is not None:
        p = subparsers.add_parser('slack', help='slack komutu')
    else:
        p = argparse.ArgumentParser(prog='ReYMeN slack')
    return p


def run_slack(args=None) -> None:
    """'slack' komutunu çalıştır."""
    pass


if __name__ == '__main__':
    p = build_slack_parser()
    print(f'{p.prog} hazır.')
