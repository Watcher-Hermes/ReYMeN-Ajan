"""
Playwright MCP entegrasyon testi — ReYMeN Ajan

Baska bilgisayarda calistirmak icin:
  - Node.js v18+ gerekli  (https://nodejs.org)
  - npx PATH'te olmali
  - Ilk calistirmada @playwright/mcp paketi otomatik indirilir (~50 MB)

Kullanim:
  python test_playwright_mcp.py
"""

import json
import shutil
import subprocess
import sys
import time

# ── Komut ────────────────────────────────────────────────────────────────────
def build_cmd() -> list[str] | None:
    """
    Oncelik sirasi:
      1. PowerShell uzerinden npx (Windows'ta en guvenilir)
      2. node dogrudan (fallback)
    """
    node = shutil.which("node") or shutil.which("node.exe")
    if not node:
        return None

    if sys.platform == "win32":
        ps = shutil.which("powershell") or shutil.which("pwsh")
        if ps:
            return [
                ps, "-NoProfile", "-NonInteractive", "-Command",
                "npx -y '@playwright/mcp@latest' --headless"
            ]

    # Unix / fallback
    npx = shutil.which("npx")
    if npx:
        return [npx, "-y", "@playwright/mcp@latest", "--headless"]

    return None


CMD = build_cmd()


def _send(proc, msg: dict) -> None:
    data = (json.dumps(msg) + "\n").encode()
    proc.stdin.write(data)
    proc.stdin.flush()


def run_test(name: str, url: str) -> dict:
    print(f"\n[TEST] {name}")
    print(f"  URL : {url}")

    if not CMD:
        return {"ok": False, "error": "node/npx bulunamadi"}

    flags = 0
    if sys.platform == "win32":
        flags = subprocess.CREATE_NO_WINDOW

    proc = subprocess.Popen(
        CMD,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        creationflags=flags,
    )

    try:
        time.sleep(8)   # MCP sunucu + Chromium baslatma suresi

        _send(proc, {
            "jsonrpc": "2.0", "id": 1, "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "reymen-test", "version": "1.0"},
            },
        })
        time.sleep(2)

        _send(proc, {
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
            "params": {},
        })
        time.sleep(1)

        _send(proc, {
            "jsonrpc": "2.0", "id": 2, "method": "tools/call",
            "params": {
                "name": "browser_navigate",
                "arguments": {"url": url},
            },
        })
        time.sleep(12)  # navigasyon + cevap icin bekle

    except Exception as exc:
        proc.kill()
        return {"ok": False, "error": f"Mesaj gonderilemedi: {exc}"}

    # Prose buffer'i okumak icin once kill et
    proc.kill()
    raw = proc.stdout.read().decode(errors="replace")
    proc.wait()

    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            data = json.loads(line)
            content = data.get("result", {}).get("content", [])
            text = content[0].get("text", "") if content else ""
            ok = "Page URL:" in text or "Page Title:" in text
            preview = text[:130].replace("\n", " ")
            status = "OK  " if ok else "FAIL"
            print(f"  {status} -- {preview}")
            return {"ok": ok, "text": text, "url": url}
        except (json.JSONDecodeError, IndexError, KeyError):
            continue

    print(f"  FAIL -- yanit alinamadi")
    if raw:
        print(f"  Ham cikti: {raw[:200].replace(chr(10), ' ')}")
    return {"ok": False, "error": "Yanit parse edilemedi"}


def main():
    print("=" * 60)
    print("ReYMeN Ajan -- Playwright MCP Entegrasyon Testi")
    print("=" * 60)

    if not CMD:
        print("\nHATA: node/npx bulunamadi.")
        print("Cozum: https://nodejs.org adresinden Node.js kur.")
        sys.exit(1)

    print(f"Komut: {' '.join(CMD[:3])} ...")
    print(f"node : {shutil.which('node') or '(bulunamadi)'}")

    tests = [
        ("Temel gezinme", "https://example.com"),
        ("HTTPS endpoint", "https://httpbin.org/get"),
        ("GitHub", "https://github.com"),
    ]

    results = []
    for name, url in tests:
        r = run_test(name, url)
        results.append(r)

    print("\n" + "=" * 60)
    passed = sum(1 for r in results if r.get("ok"))
    print(f"SONUC: {passed}/{len(results)} test gecti")
    print("=" * 60)

    if passed == len(results):
        print("\nPLAYWRIGHT MCP CALISIYOR -- ReYMeN ajana hazir!")
        print("  Baska bilgisayarda da calisir (Node.js 18+ gerekli).")
    elif passed > 0:
        print(f"\nKismi basari ({passed}/{len(results)})")
    else:
        print("\nBasarisiz -- sorun giderme:")
        print("  skills/playwright-mcp/references/troubleshooting.md")

    sys.exit(0 if passed > 0 else 1)


if __name__ == "__main__":
    main()
