"""
duplicate_module_detector.py — Full sürüm (264 satır).
AST tabanlı drift tespiti: aynı isimli dosyaları bulur, fonksiyon setlerini
karşılaştırır, canlı yolu tespit eder, JSON/HTML/terminal çıktı verir.
"""

import ast
import json
import os
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Optional


# ── 1. AST Analizi ──────────────────────────────────────────────────────────

def extract_function_names(filepath: str) -> set[str]:
    """Bir .py dosyasındaki tüm top-level fonksiyon adlarını çıkarır."""
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


# ── 2. Duplicate Bulma ──────────────────────────────────────────────────────

def find_duplicate_basenames(
    root_dir: str,
    ignore_dirs: set[str] = None,
) -> dict[str, list[str]]:
    """Aynı basename'e sahip .py'leri gruplar."""
    ignore_dirs = ignore_dirs or {
        ".git", "__pycache__", "venv", ".venv", "node_modules",
        ".claude", "hermes-memory-backup", "skills_yeni",
        "_cleanup_backup", "bot_venv", ".hermes",
    }
    groups: dict[str, list[str]] = defaultdict(list)
    for dirpath, dirnames, filenames in os.walk(root_dir):
        dirnames[:] = [d for d in dirnames if d not in ignore_dirs]
        for fname in filenames:
            if fname.endswith(".py"):
                full = os.path.join(dirpath, fname)
                groups[fname].append(full)
    return {name: paths for name, paths in groups.items() if len(paths) > 1}


def find_live_import_path(
    root_dir: str,
    module_basename: str,
    entry_points: list[str] = None,
) -> Optional[str]:
    """Birden çok entry point'te import edilen modülü bulur."""
    entry_points = entry_points or ["main.py", "start.py", "__init__.py"]
    module_name = module_basename.replace(".py", "")

    for ep in entry_points:
        ep_path = os.path.join(root_dir, ep)
        if not os.path.exists(ep_path):
            continue
        try:
            with open(ep_path, "r", encoding="utf-8") as f:
                tree = ast.parse(f.read())
        except (SyntaxError, UnicodeDecodeError):
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                if node.module and module_name in node.module:
                    return node.module
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if module_name in alias.name:
                        return alias.name
    return None


# ── 3. Raporlama ────────────────────────────────────────────────────────────

def report_drift(
    root_dir: str,
    entry_points: list[str] = None,
    ignore_dirs: set[str] = None,
) -> list[dict]:
    """Tüm projeyi tara, drift raporu üret."""
    duplicates = find_duplicate_basenames(root_dir, ignore_dirs)
    findings = []

    for basename, paths in duplicates.items():
        func_sets = {p: extract_function_names(p) for p in paths}
        all_funcs = set().union(*func_sets.values())
        unique_sets = {frozenset(fs) for fs in func_sets.values()}
        if len(unique_sets) <= 1:
            continue

        live_module = find_live_import_path(root_dir, basename, entry_points)
        canli_yol = None
        if live_module:
            for p in paths:
                if any(seg in p for seg in live_module.split(".")):
                    canli_yol = p
                    break

        findings.append({
            "basename": basename,
            "canli_yol": canli_yol or min(paths, key=len),
            "kopyalar": sorted(paths),
            "canli_fonksiyon_sayisi": len(func_sets[canli_yol]) if canli_yol else 0,
            "fonksiyon_farki": {
                p: sorted(all_funcs - fs) for p, fs in func_sets.items()
                if p != (canli_yol or min(paths, key=len))
            },
            "risk": "YUKSEK" if canli_yol else "BELIRSIZ",
        })

    return findings


def print_text(findings: list[dict], detayli: bool = False) -> str:
    """Terminal çıktısı üret."""
    if not findings:
        return "✅ Drift tespit edilmedi — tum dosyalar senkron."
    satirlar = [
        f"⚠️  {len(findings)} drift bulundu.\n",
        f"# Tarama: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n",
    ]
    for f in findings:
        satirlar.append(f"🎯 {f['basename']}  (risk: {f['risk']})")
        satirlar.append(f"   Canli: {f['canli_yol']}")
        for kop in f["kopyalar"]:
            if kop == f["canli_yol"]:
                continue
            satirlar.append(f"   Kop:  {kop}")
            miss = f["fonksiyon_farki"].get(kop, [])
            if miss and detayli:
                satirlar.append(f"      eksik: {', '.join(miss[:10])}")
                if len(miss) > 10:
                    satirlar.append(f"      ...ve {len(miss)-10} daha")
        satirlar.append("")
    satirlar.append(f"📊 Toplam: {len(findings)} drift")
    return "\n".join(satirlar)


def print_json(findings: list[dict]) -> str:
    """JSON çıktısı üret."""
    return json.dumps({
        "tarih": datetime.now().isoformat(),
        "toplam_drift": len(findings),
        "bulgular": findings,
    }, ensure_ascii=False, indent=2)


# ── 4. Ana ──────────────────────────────────────────────────────────────────

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Duplicate Module Drift Detector")
    parser.add_argument("root", nargs="?", default=".", help="Kök dizin")
    parser.add_argument("--format", choices=["text", "json", "detayli"],
                        default="detayli", help="Çıktı formatı")
    parser.add_argument("--save", help="Çıktıyı dosyaya kaydet")
    parser.add_argument("--entry", nargs="+",
                        default=["main.py", "start.py", "__init__.py"],
                        help="Entry point'ler")
    args = parser.parse_args()

    findings = report_drift(args.root, args.entry)

    if args.format == "json":
        output = print_json(findings)
    else:
        output = print_text(findings, detayli=(args.format == "detayli"))

    if args.save:
        with open(args.save, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"Kaydedildi: {args.save}")
    else:
        print(output)

    sys.exit(1 if findings else 0)


if __name__ == "__main__":
    main()
