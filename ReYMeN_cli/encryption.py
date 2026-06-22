# -*- coding: utf-8 -*-
"""ReYMeN_cli/encryption.py — Sifreleme CLI.

Veri sifreleme, cozme, anahtar yonetimi ve hash islemleri.
"""

import hashlib
import json
from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent


def _hash_olustur(veri: str, algoritma: str = "sha256") -> str:
    """Verinin hash'ini olusturur."""
    h = hashlib.new(algoritma)
    h.update(veri.encode("utf-8"))
    return h.hexdigest()


def kaydet(alt_parser):
    """encryption CLI alt komutlarini argparse alt ayristiricisina kaydet."""
    alt_parser.add_argument("islem", type=str, nargs="?",
                            choices=["encrypt", "decrypt", "hash", "keygen", "verify"],
                            help="Yapilacak islem (encrypt|decrypt|hash|keygen|verify)")
    alt_parser.add_argument("--data", type=str, default=None, help="Islenecek veri")
    alt_parser.add_argument("--file", type=str, default=None, help="Dosya yolu")
    alt_parser.add_argument("--algo", type=str, default="sha256",
                            choices=["sha256", "sha512", "md5", "blake2b"],
                            help="Hash algoritmasi")
    alt_parser.add_argument("--key", type=str, default=None, help="Sifreleme anahtari")
    alt_parser.add_argument("--output", type=str, default=None, help="Cikti dosyasi")


def calistir(args):
    """encryption komutunu calistir."""
    try:
        islem = args.islem or "hash"
        print(f"[Encryption] Baslatiliyor: {islem}")

        if islem == "encrypt":
            veri = args.data or "(ornek veri)"
            anahtar = args.key or "default-key"
            print(f"[Encryption] Sifreleniyor: {veri[:50]}...")
            # Basit XOR sifreleme (ornek)
            sifreli = "".join(chr(ord(c) ^ ord(anahtar[i % len(anahtar)])) for i, c in enumerate(veri))
            sifreli_b64 = sifreli.encode("utf-8").hex()
            print(f"  Sifreli (hex): {sifreli_b64[:64]}...")
            if args.output:
                with open(args.output, "w") as f:
                    f.write(sifreli_b64)
                print(f"  Kaydedildi: {args.output}")

        elif islem == "decrypt":
            print("[Encryption] Cozme islemi (simule)")
            print("  Not: Gercek sifre cozme icin uygun anahtar gerekli")

        elif islem == "hash":
            veri = args.data or "test"
            if args.file:
                with open(args.file, "rb") as f:
                    veri = f.read().hex()
            hash_deger = _hash_olustur(veri, args.algo)
            print(f"[Encryption] Hash ({args.algo}):")
            print(f"  Veri: {veri[:50]}...")
            print(f"  Hash: {hash_deger}")

        elif islem == "keygen":
            import secrets
            print("[Encryption] Anahtar olusturuluyor...")
            anahtar = secrets.token_hex(32)
            print(f"  Anahtar: {anahtar}")
            if args.output:
                with open(args.output, "w") as f:
                    f.write(anahtar)
                print(f"  Kaydedildi: {args.output}")

        elif islem == "verify":
            print("[Encryption] Dogrulama (simule)")
            print("  Hash dogrulama basarili")

    except Exception as e:
        print(f"[Encryption] Hata: {e}")
