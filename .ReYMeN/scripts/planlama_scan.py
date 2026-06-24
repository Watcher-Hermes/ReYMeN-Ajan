#!/usr/bin/env python3
"""Planlama (Alan 2) scan: compile + import validation for tests/"""
import py_compile, os, sys, importlib

proj = r"C:\Users\marko\Desktop\Reymen Proje\hermes_projesi"
test_dir = os.path.join(proj, "tests")

# Step A1: Compile all .py files
print("=== A1: Syntax compile check ===")
compile_ok = 0
compile_err = []
for root, dirs, files in os.walk(test_dir):
    dirs[:] = [d for d in dirs if d != "__pycache__"]
    for f in files:
        if not f.endswith(".py"):
            continue
        fp = os.path.join(root, f)
        try:
            py_compile.compile(fp, doraise=True)
            compile_ok += 1
        except py_compile.PyCompileError as e:
            compile_err.append(fp)

print(f"OK: {compile_ok}  ERR: {len(compile_err)}")
for e in compile_err[:10]:
    print(f"  FAIL: {e}")

# Step A2: Top-level import test for test modules
print("\n=== A2: Top-level import test ===")
test_modules = ["tests.conftest", "tests.gen_all", "tests.reymen_coverage_runner"]
ok = 0
fail = 0
for mod_name in test_modules:
    try:
        importlib.import_module(mod_name)
        ok += 1
        print(f"  ✅ {mod_name}")
    except ImportError as e:
        fail += 1
        print(f"  ❌ {mod_name}: {e}")

print(f"\nImport: {ok}/{len(test_modules)} OK")

# Step A3: Check for stale .pyc or other maintenance items
print("\n=== A3: Maintenance scan ===")
# Check for BOM
import codecs
bom_count = 0
for root, dirs, files in os.walk(test_dir):
    dirs[:] = [d for d in dirs if d != "__pycache__"]
    for f in files:
        if f.endswith(".py"):
            fp = os.path.join(root, f)
            try:
                with open(fp, "rb") as fh:
                    raw = fh.read(3)
                    if raw.startswith(codecs.BOM_UTF8) or raw.startswith(codecs.BOM_UTF16_LE) or raw.startswith(codecs.BOM_UTF16_BE):
                        bom_count += 1
                        print(f"  BOM: {fp}")
            except Exception:
                pass
print(f"BOM files: {bom_count}")

# FIXME/HACK/TODO count in tests/
todo_count = 0
for root, dirs, files in os.walk(test_dir):
    dirs[:] = [d for d in dirs if d != "__pycache__"]
    for f in files:
        if f.endswith(".py"):
            fp = os.path.join(root, f)
            try:
                with open(fp, "r", encoding="utf-8", errors="replace") as fh:
                    for line in fh:
                        if "FIXME" in line or "HACK" in line:
                            todo_count += 1
            except Exception:
                pass
print(f"FIXME/HACK markers: {todo_count}")

print("\n=== Scan complete ===")
