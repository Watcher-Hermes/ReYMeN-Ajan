# -*- coding: utf-8 -*-
"""ReYMeN_cli/telegram_managed_bot.py — Telegram yönetimli bot CLI."""
from __future__ import annotations
import argparse


def build_telegram_parser(subparsers=None) -> argparse.ArgumentParser:
    if subparsers is not None:
        p = subparsers.add_parser('telegram', help='Telegram bot yönetimi')
    else:
        p = argparse.ArgumentParser(prog='ReYMeN telegram')
    return p


def run_telegram(args=None) -> None:
    pass


if __name__ == '__main__':
    print('telegram_managed_bot importlandı.')

DEFAULT_MANAGER_BOT = ""

TELEGRAM_ONBOARDING_URL_ENV = "TELEGRAM_ONBOARDING_URL"

