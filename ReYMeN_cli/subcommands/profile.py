# -*- coding: utf-8 -*-
"""ReYMeN_cli/subcommands/profile.py — profile alt komutu."""
from __future__ import annotations
import argparse


def build_profile_parser(subparsers=None) -> argparse.ArgumentParser:
    """'profile' alt komut parser'ını oluştur."""
    if subparsers is not None:
        p = subparsers.add_parser('profile', help='profile komutu')
    else:
        p = argparse.ArgumentParser(prog='ReYMeN profile')
    return p


def run_profile(args=None) -> None:
    """'profile' komutunu çalıştır."""
    pass


if __name__ == '__main__':
    p = build_profile_parser()
    print(f'{p.prog} hazır.')
