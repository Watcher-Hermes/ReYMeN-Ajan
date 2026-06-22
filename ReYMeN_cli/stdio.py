# -*- coding: utf-8 -*-
"""ReYMeN_cli/stdio.py — Stdio Protokol Islecisi.

JSON-RPC 2.0 uzerinden stdin/stdout ile MCP sunucu iletisimi.
ReYMeN'in araclarini MCP uyumlu hale getirmek icin kullanilir.
"""

import json
import sys
import traceback
from typing import Callable


def stdio_istek_parse(raw_line: str) -> dict:
    """Gelen JSON-RPC istegini ayristir.

    Args:
        raw_line: Ham JSON satiri

    Returns:
        dict: Ayristirilmis istek (en azindan jsonrpc, id, method)
              veya hata durumunda {'error': mesaj}
    """
    try:
        if not raw_line or not raw_line.strip():
            return {"error": "Bos satir alindi"}

        veri = json.loads(raw_line.strip())

        if not isinstance(veri, dict):
            return {"error": "JSON bir nesne olmali"}

        if veri.get("jsonrpc") != "2.0":
            veri["jsonrpc"] = "2.0"

        if "method" not in veri:
            return {
                "jsonrpc": "2.0",
                "error": {"code": -32600, "message": "Method eksik"},
                "id": veri.get("id"),
            }

        return veri

    except json.JSONDecodeError as e:
        return {
            "jsonrpc": "2.0",
            "error": {"code": -32700, "message": f"Parse hatasi: {e}"},
            "id": None,
        }
    except Exception as e:
        return {
            "jsonrpc": "2.0",
            "error": {"code": -32603, "message": f"Ic hata: {e}"},
            "id": None,
        }


def stdio_hata_yonet(error: Exception, request_id=None) -> dict:
    """JSON-RPC hata yaniti olustur.

    Args:
        error: Yakalanan istisna
        request_id: Istege ait ID (None ise -1)

    Returns:
        dict: JSON-RPC 2.0 hata yaniti
    """
    try:
        hata_kodu = getattr(error, "code", -32603)
        if not isinstance(hata_kodu, int):
            hata_kodu = -32603

        hata_mesaji = str(error) if str(error) else "Bilinmeyen hata"
        hata_detayi = "".join(
            traceback.format_exception(type(error), error, error.__traceback__)
        )

        return {
            "jsonrpc": "2.0",
            "error": {
                "code": hata_kodu,
                "message": hata_mesaji,
                "data": hata_detayi if hata_detayi else None,
            },
            "id": request_id if request_id is not None else -1,
        }
    except Exception:
        return {
            "jsonrpc": "2.0",
            "error": {"code": -32603, "message": "Hata yonetimi basarisiz"},
            "id": None,
        }


def stdio_gonder(response: dict):
    """JSON-RPC yanitini stdout'a yaz.

    Yanit JSON formatinda stdout'a yazilir ve ardindan yeni satir
    eklenir. MCP sunucu protokolu bu formati bekler.

    Args:
        response: JSON-RPC yanit字典
    """
    try:
        yanit_json = json.dumps(response, ensure_ascii=False)
        sys.stdout.write(yanit_json + "\n")
        sys.stdout.flush()
    except Exception as e:
        hata_yanit = {
            "jsonrpc": "2.0",
            "error": {"code": -32603, "message": f"Yanit yazma hatasi: {e}"},
            "id": response.get("id") if isinstance(response, dict) else None,
        }
        try:
            sys.stderr.write(json.dumps(hata_yanit, ensure_ascii=False) + "\n")
            sys.stderr.flush()
        except Exception:
            pass


def stdio_dinle(handler_func: Callable, raw: bool = False):
    """stdin'den JSON-RPC isteklerini dinle ve isle.

    Sonsuz dongude stdin okur, her satiri ayristirir ve handler_func'a
    iletir. Handler_func bir istek alir ve bir yanit dondurur.

    Args:
        handler_func: Istek isleyici fonksiyon
                      (dict -> dict, istek alir, yanit dondurur)
        raw: True ise ham string olarak ilet, False ise ayristirilmis dict
    """
    try:
        for satir in sys.stdin:
            if not satir or not satir.strip():
                continue

            satir = satir.strip()

            if raw:
                try:
                    yanit = handler_func(satir)
                    if yanit is not None:
                        if isinstance(yanit, str):
                            try:
                                yanit_dict = json.loads(yanit)
                                stdio_gonder(yanit_dict)
                            except json.JSONDecodeError:
                                sys.stdout.write(yanit + "\n")
                                sys.stdout.flush()
                        else:
                            stdio_gonder(yanit)
                except Exception as e:
                    hata = stdio_hata_yonet(e)
                    stdio_gonder(hata)
            else:
                istek = stdio_istek_parse(satir)
                if "error" in istek and "method" not in istek:
                    stdio_gonder(istek)
                    continue

                try:
                    yanit = handler_func(istek)
                    if yanit is not None:
                        if isinstance(yanit, str):
                            try:
                                yanit_dict = json.loads(yanit)
                                if "jsonrpc" not in yanit_dict:
                                    yanit_dict["jsonrpc"] = "2.0"
                                stdio_gonder(yanit_dict)
                            except json.JSONDecodeError:
                                string_yanit = {
                                    "jsonrpc": "2.0",
                                    "result": yanit,
                                    "id": istek.get("id", -1),
                                }
                                stdio_gonder(string_yanit)
                        elif isinstance(yanit, dict):
                            if "jsonrpc" not in yanit:
                                yanit["jsonrpc"] = "2.0"
                            stdio_gonder(yanit)
                except Exception as e:
                    hata = stdio_hata_yonet(e, istek.get("id"))
                    stdio_gonder(hata)

    except KeyboardInterrupt:
        sys.stderr.write("[Stdio] Dinleme sonlandirildi.\n")
        sys.stderr.flush()
    except EOFError:
        pass
    except Exception as e:
        sys.stderr.write(f"[Stdio] Dinleyici hatasi: {e}\n")
        sys.stderr.flush()


class Renk:
    """ReYMeN inline Renk — ANSI renk kodlari."""
    YESIL = "\033[92m"
    SARI = "\033[93m"
    KIRMIZI = "\033[91m"
    MAVI = "\033[94m"
    CYAN = "\033[96m"
    KALIN = "\033[1m"
    SON = "\033[0m"

    @classmethod
    def boya(cls, metin: str, kod: str) -> str:
        return f"{kod}{metin}{cls.SON}"

    @classmethod
    def yesil(cls, metin: str) -> str:
        return cls.boya(metin, cls.YESIL)

    @classmethod
    def sari(cls, metin: str) -> str:
        return cls.boya(metin, cls.SARI)

    @classmethod
    def kirmizi(cls, metin: str) -> str:
        return cls.boya(metin, cls.KIRMIZI)

    @classmethod
    def mavi(cls, metin: str) -> str:
        return cls.boya(metin, cls.MAVI)


def kaydet(alt_parser):
    """Stdio CLI alt komutlarini argparse alt ayristiricisina kaydet.

    Alt komutlar: listen, send (test icin)
    """
    alt_parser.add_argument("islem", type=str, nargs="?",
                            choices=["listen", "send", "test"],
                            help="Islem (listen|send|test)")
    alt_parser.add_argument("--raw", action="store_true",
                            help="Ham mod (ayristirma yapma)")
    alt_parser.add_argument("--json", type=str, default=None,
                            help="Gonderilecek JSON (send/test icin)")


def calistir(args):
    """Stdio komutunu calistir."""
    try:
        islem = args.islem or "test"

        if islem == "listen":

            def basit_handler(istek: dict) -> dict:
                method = istek.get("method", "bilinmeyen")
                params = istek.get("params", {})
                return {
                    "jsonrpc": "2.0",
                    "result": {
                        "status": "ok",
                        "method": method,
                        "params": params,
                        "server": "ReYMeN MCP",
                    },
                    "id": istek.get("id", -1),
                }

            print(f"{Renk.yesil('[Stdio]')} JSON-RPC dinleyici baslatildi. Ctrl+C ile durdurun.")
            stdio_dinle(basit_handler, raw=args.raw)

        elif islem == "send":
            if not args.json:
                print(f"{Renk.sari('[Stdio]')} Lutfen --json parametresini belirtin.")
                return
            try:
                veri = json.loads(args.json)
                stdio_gonder(veri)
                print(f"{Renk.yesil('[Stdio]')} Yanit gonderildi.")
            except json.JSONDecodeError as e:
                print(f"{Renk.kirmizi('[Stdio]')} Gecersiz JSON: {e}")

        elif islem == "test":
            test_istek = '{"jsonrpc":"2.0","method":"ping","id":1}'
            parsed = stdio_istek_parse(test_istek)
            print(f"{Renk.mavi('[Stdio]')} Test — Parse:")
            print(f"  Girdi: {test_istek}")
            print(f"  Sonuc: {json.dumps(parsed, indent=2, ensure_ascii=False)}")

            test_hata = ValueError("Test hatasi")
            hata_yanit = stdio_hata_yonet(test_hata, 1)
            print(f"{Renk.mavi('[Stdio]')} Test — Hata yaniti:")
            print(f"  {json.dumps(hata_yanit, indent=2, ensure_ascii=False)}")

    except Exception as e:
        print(f"{Renk.kirmizi('[Stdio]')} Komut hatasi: {e}")
