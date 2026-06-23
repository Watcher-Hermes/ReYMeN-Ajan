"""
duplicate_module_detector_basic.py — Hafif sürüm (106 satır).
Sadece aynı isimli dosyaları bulur, fonksiyon farklarını raporlar.
"""

import ast, os, sys
from collections import defaultdict


def extract_names(filepath: str) -> set[str]:
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=filepath)
    except (SyntaxError, UnicodeDecodeError) as e:
        return {f"HATA:{e}"}
    n = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            n.add(node.name)
    return n


def find_dupes(root_dir: str, ignore: set[str] = None) -> dict[str, list[str]]:
    ignore = ignore or {".git", "__pycache__", "venv", ".venv", "node_modules"}
    g = defaultdict(list)
    for dp, dn, fn in os.walk(root_dir):
        dn[:] = [d for d in dn if d not in ignore]
        for f in fn:
            if f.endswith(".py"):
                g[f].append(os.path.join(dp, f))
    return {n: p for n, p in g.items() if len(p) > 1}


def live_import(hint: str, paths: list[str]) -> str:
    """Canlı yol tahmini: en kısa path veya belirtilen hint."""
    if hint:
        for p in paths:
            if hint in p:
                return p
    return min(paths, key=len)


def main():
    root = sys.argv[1] if len(sys.argv) > 1 else "."
    hint = sys.argv[2] if len(sys.argv) > 2 else "reymen"
    dupes = find_dupes(root)
    findings = 0
    for name, paths in dupes.items():
        funcs = {p: extract_names(p) for p in paths}
        if len({frozenset(f) for f in funcs.values()}) <= 1:
            continue
        findings += 1
        live = live_import(hint, paths)
        all_f = set().union(*funcs.values())
        print(f"🎯 {name}")
        for p in paths:
            tag = " ← CANLI" if p == live else ""
            miss = sorted(all_f - funcs[p])
            print(f"   {p}{tag}")
            if miss:
                print(f"      eksik: {', '.join(miss[:8])}")
                if len(miss) > 8:
                    print(f"      ...ve {len(miss)-8} daha")
        print()
    print(f"📊 {findings} drift bulundu.")
    sys.exit(1 if findings else 0)


if __name__ == "__main__":
    main()
