# -*- coding: utf-8 -*-
"""ReYMeN_cli/subcommands/skills.py — skills alt komutu."""
from __future__ import annotations
import argparse


def build_skills_parser(subparsers=None) -> argparse.ArgumentParser:
    """'skills' alt komut parser'ını oluştur."""
    if subparsers is not None:
        p = subparsers.add_parser('skills', help='skills komutu')
    else:
        p = argparse.ArgumentParser(prog='ReYMeN skills')
    return p


def run_skills(args=None) -> None:
    """'skills' komutunu çalıştır."""
    pass


if __name__ == '__main__':
    p = build_skills_parser()
    print(f'{p.prog} hazır.')
