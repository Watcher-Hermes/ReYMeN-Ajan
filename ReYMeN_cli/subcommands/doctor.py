# -*- coding: utf-8 -*-
"""ReYMeN_cli/subcommands/doctor.py — doctor alt komutu."""
from __future__ import annotations
import argparse


def build_doctor_parser(subparsers=None) -> argparse.ArgumentParser:
    """'doctor' alt komut parser'ını oluştur."""
    if subparsers is not None:
        p = subparsers.add_parser('doctor', help='doctor komutu')
    else:
        p = argparse.ArgumentParser(prog='ReYMeN doctor')
    return p


def run_doctor(args=None) -> None:
    """'doctor' komutunu çalıştır."""
    pass


if __name__ == '__main__':
    p = build_doctor_parser()
    print(f'{p.prog} hazır.')
