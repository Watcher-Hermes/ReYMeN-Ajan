# -*- coding: utf-8 -*-
"""ReYMeN_cli/docs.py — Dokumantasyon CLI.

Dokumantasyon olusturma, sunucu baslatma, arama ve acma islemleri.
"""

import os
import subprocess
import sys
from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent
DOCS_DIR = PROJE_KOK / "docs"


def kaydet(alt_parser):
    """Docs CLI alt komutlarini argparse alt ayristiricisina kaydet.

    Alt komutlar: generate, serve, search, open
    """
    alt_parser.add_argument("islem", type=str, nargs="?",
                            choices=["generate", "serve", "search", "open"],
                            help="Yapilacak islem (generate|serve|search|open)")
    alt_parser.add_argument("--query", type=str, default=None,
                            help="Arama sorgusu")
    alt_parser.add_argument("--port", type=int, default=8000,
                            help="Dokumantasyon sunucu portu")


def calistir(args):
    """Docs komutunu calistir."""
    try:
        islem = args.islem or "open"
        DOCS_DIR.mkdir(exist_ok=True)

        if islem == "generate":
            print("[Docs] Dokumantasyon olusturuluyor...")
            kaynaklar = list(PROJE_KOK.glob("*.py")) + list((PROJE_KOK / "ReYMeN_cli").glob("*.py"))
            dokuman_icerik = f"# ReYMeN Dokumantasyon\n\n"
            dokuman_icerik += f"_Olusturma: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_\n\n"
            dokuman_icerik += f"## Modul Listesi\n\n"
            for py_dosya in sorted(kaynaklar):
                ad = py_dosya.name
                if ad.startswith("__"):
                    continue
                dokuman_icerik += f"- [{ad}]({ad}.md)\n"
            dokuman_yolu = DOCS_DIR / "README.md"
            with open(str(dokuman_yolu), "w", encoding="utf-8") as f:
                f.write(dokuman_icerik)

            for py_dosya in sorted(kaynaklar):
                if py_dosya.name.startswith("__"):
                    continue
                modul_dok = f"# {py_dosya.name}\n\n"
                modul_dok += f"_Kaynak: {py_dosya.relative_to(PROJE_KOK)}_\n\n"
                try:
                    with open(str(py_dosya), "r", encoding="utf-8") as f:
                        icerik = f.read()
                    for satir in icerik.split("\n"):
                        if satir.strip().startswith("def ") or satir.strip().startswith("class "):
                            modul_dok += f"- `{satir.strip()}`\n"
                except Exception:
                    modul_dok += "_Icindekiler okunamadi._\n"
                modul_yolu = DOCS_DIR / f"{py_dosya.name}.md"
                with open(str(modul_yolu), "w", encoding="utf-8") as f:
                    f.write(modul_dok)
            print(f"[Docs] Dokumantasyon olusturuldu: {DOCS_DIR}")

        elif islem == "serve":
            port = args.port
            print(f"[Docs] Dokumantasyon sunucusu baslatiliyor (port {port})...")
            index_yolu = DOCS_DIR / "README.md"
            if not index_yolu.exists():
                print("[Docs] Henuz dokumantasyon yok. Once 'docs generate' calistirin.")
                return
            try:
                import http.server
                import socketserver
                os.chdir(str(DOCS_DIR))
                Handler = http.server.SimpleHTTPRequestHandler
                with socketserver.TCPServer(("0.0.0.0", port), Handler) as httpd:
                    print(f"[Docs] Sunucu: http://localhost:{port}")
                    print("[Docs] Cikmak icin Ctrl+C")
                    httpd.serve_forever()
            except KeyboardInterrupt:
                print("\n[Docs] Sunucu durduruldu.")
            except ImportError:
                print("[Docs] http.server yuklenemedi.")

        elif islem == "search":
            query = args.query
            if not query:
                print("[Docs] Lutfen --query parametresini belirtin.")
                return
            print(f"[Docs] Araniyor: {query}")
            bulunan = 0
            for md_dosya in sorted(DOCS_DIR.rglob("*.md")):
                try:
                    with open(str(md_dosya), "r", encoding="utf-8") as f:
                        icerik = f.read()
                    if query.lower() in icerik.lower():
                        print(f"  + {md_dosya.relative_to(DOCS_DIR)}")
                        bulunan += 1
                except Exception:
                    continue
            if bulunan == 0:
                print(f"  Sonuc bulunamadi: {query}")
            else:
                print(f"  {bulunan} dosyada eslesme bulundu.")

        elif islem == "open":
            index_yolu = DOCS_DIR / "README.md"
            if index_yolu.exists():
                if sys.platform == "win32":
                    os.startfile(str(index_yolu))
                elif sys.platform == "darwin":
                    subprocess.run(["open", str(index_yolu)])
                else:
                    subprocess.run(["xdg-open", str(index_yolu)])
                print(f"[Docs] Dokumantasyon acildi: {index_yolu}")
            else:
                print("[Docs] Henuz dokumantasyon yok. Once 'docs generate' calistirin.")

    except Exception as e:
        print(f"[Docs] Beklenmeyen hata: {e}")
