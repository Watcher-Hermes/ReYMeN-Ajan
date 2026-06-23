#!/usr/bin/env python3
"""
duplicate_module_detector.py — Basic version (AST-based)
Aynı isimli ama farklı klasörlerdeki .py dosyalarını bulur,
fonksiyon setlerini AST ile karşılaştırır, drift varsa raporlar.
Ayrıca hangi dosyanın gerçekten import edildiğini (canlı yol) tespit eder.
"""

import ast
import os
import sys
from collections import defaultdict
from pathlib import Path


def extract_function_names(filepath: str) -> set[str]:
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=filepath)
    except (SyntaxError, UnicodeDecodeError) as e:
        return {f"PARSE_ERROR:{e}"}

    names = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            names.add(node.name)
    return names


def find_duplicate_basenames(root_dir: str, ignore_dirs: set[str] = None) -> dict[str, list[str]]:
    ignore_dirs = ignore_dirs or {".git", "__pycache__", "venv", ".venv", "node_modules"}
    groups: dict[str, list[str]] = defaultdict(list)
    for dirpath, dirnames, filenames in os.walk(root_dir):
        dirnames[:] = [d for d in dirnames if d not in ignore_dirs]
        for fname in filenames:
            if fname.endswith(".py"):
                full = os.path.join(dirpath, fname)
                groups[fname].append(full)
    return {name: paths for name, paths in groups.items() if len(paths) > 1}


def find_live_import_path(root_dir: str, module_basename: str, entry_point: str = "main.py") -> str | None:
    entry_path = os.path.join(root_dir, entry_point)
    if not os.path.exists(entry_path):
        return None
    module_name = module_basename.replace(".py", "")
    try:
        with open(entry_path, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read())
    except (SyntaxError, UnicodeDecodeError):
        return None
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module and module_name in node.module:
            return node.module
        if isinstance(node, ast.Import):
            for alias in node.names:
                if module_name in alias.name:
                    return alias.name
    return None


def report_drift(root_dir: str, entry_point: str = "main.py") -> list[dict]:
    duplicates = find_duplicate_basenames(root_dir)
    findings = []
    for basename, paths in duplicates.items():
        func_sets = {p: extract_function_names(p) for p in paths}
        all_funcs = set().union(*func_sets.values())
        if len({frozenset(fs) for fs in func_sets.values()}) <= 1:
            continue
        live_module = find_live_import_path(root_dir, basename, entry_point)
        findings.append({
            "basename": basename,
            "paths": paths,
            "function_diff": {p: sorted(all_funcs - fs) for p, fs in func_sets.items()},
            "live_import_hint": live_module,
            "risk": "YUKSEK" if live_module else "BELIRSIZ",
        })
    return findings


def print_report(findings: list[dict]) -> None:
    if not findings:
        print("✅ Drift tespit edilmedi — ayni isimli dosyalar yok veya hepsi senkron.")
        return
    print(f"⚠️  {len(findings)} drift bulundu:\n")
    for f in findings:
        print(f"🎯 {f['basename']}  (risk: {f['risk']})")
        for path in f["paths"]:
            missing = f["function_diff"].get(path, [])
            tag = ""
            if f["live_import_hint"]:
                hint_last = f["live_import_hint"].split(".")[-1]
                if path.replace("\\", "/").endswith(hint_last + ".py") or f["live_import_hint"] in path.replace("\\", "/"):
                    tag = " ← CANLI YOL"
            print(f"   {path}{tag}")
            if missing:
                print(f"      eksik fonksiyonlar: {', '.join(missing)}")
        print()


if __name__ == "__main__":
    root = sys.argv[1] if len(sys.argv) > 1 else "."
    entry = sys.argv[2] if len(sys.argv) > 2 else "main.py"
    findings = report_drift(root, entry)
    print_report(findings)
    sys.exit(1 if findings else 0)
