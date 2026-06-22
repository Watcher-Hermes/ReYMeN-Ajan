# -*- coding: utf-8 -*-
"""ReYMeN_cli/subcommands/prompt_size.py — prompt_size alt komutu."""
from __future__ import annotations
import argparse


def build_prompt_size_parser(subparsers=None) -> argparse.ArgumentParser:
    """'prompt_size' alt komut parser'ını oluştur."""
    if subparsers is not None:
        p = subparsers.add_parser('prompt_size', help='prompt_size komutu')
    else:
        p = argparse.ArgumentParser(prog='ReYMeN prompt_size')
    return p


def run_prompt_size(args=None) -> None:
    """'prompt_size' komutunu çalıştır."""
    pass


if __name__ == '__main__':
    p = build_prompt_size_parser()
    print(f'{p.prog} hazır.')
