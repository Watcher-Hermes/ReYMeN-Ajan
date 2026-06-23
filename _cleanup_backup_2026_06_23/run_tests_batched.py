#!/usr/bin/env python3
"""Run pytest on test_*.py files in batches of 5, excluding ReYMeN_reference."""
import subprocess
import sys
import os
import glob
import re

PROJECT = r"C:\Users\marko\Desktop\Reymen Proje\hermes_projesi"
PYTHON = os.path.join(PROJECT, "venv", "Scripts", "python.exe")

os.chdir(PROJECT)

# Get all test_*.py files (excluding anything under ReYMeN_reference)
test_files = sorted(glob.glob("tests/test_*.py"))
test_files = [f for f in test_files if "ReYMeN_reference" not in f]

print(f"Found {len(test_files)} test files to run.")

BATCH_SIZE = 5
batches = [test_files[i:i+BATCH_SIZE] for i in range(0, len(test_files), BATCH_SIZE)]

total_passed = 0
total_failed = 0
total_errors = 0
total_skipped = 0
total_tests = 0
failed_files = set()

for i, batch in enumerate(batches):
    print(f"\n{'='*70}")
    print(f"BATCH {i+1}/{len(batches)}: {', '.join(batch)}")
    print(f"{'='*70}")
    
    cmd = [
        PYTHON, "-m", "pytest",
        "-v",
        "--no-header",
        "-p", "no:warnings",
    ] + batch
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,
            cwd=PROJECT
        )
    except subprocess.TimeoutExpired:
        print(f"  ** BATCH {i+1} TIMED OUT after 300s **")
        for bf in batch:
            failed_files.add(bf)
        continue
    
    stdout = result.stdout
    stderr = result.stderr
    if stdout:
        print(stdout)
    if stderr:
        # Only show meaningful stderr
        for line in stderr.splitlines():
            if "warning" not in line.lower() and "deprecation" not in line.lower():
                print(f"STDERR: {line}")
    
    # Parse summary from last few lines
    lines = stdout.splitlines()
    for line in reversed(lines):
        line = line.strip()
        if "passed" in line or "failed" in line or "error" in line:
            passed = 0; failed = 0; errors = 0; skipped = 0
            m_passed = re.search(r'(\d+)\s+passed', line)
            m_failed = re.search(r'(\d+)\s+failed', line)
            m_errors = re.search(r'(\d+)\s+error', line)
            m_skipped = re.search(r'(\d+)\s+skipped', line)
            if m_passed: passed = int(m_passed.group(1))
            if m_failed: failed = int(m_failed.group(1))
            if m_errors: errors = int(m_errors.group(1))
            if m_skipped: skipped = int(m_skipped.group(1))
            if failed > 0 or errors > 0:
                for bf in batch:
                    failed_files.add(bf)
            total_passed += passed
            total_failed += failed
            total_errors += errors
            total_skipped += skipped
            total_tests += (passed + failed + errors + skipped)
            print(f"  --> Batch result: {passed} passed, {failed} failed, {errors} errors, {skipped} skipped")
            break
    
    # Also check exit code
    if result.returncode != 0 and result.returncode is not None:
        print(f"  --> Batch exited with code {result.returncode}")

print(f"\n{'='*70}")
print(f"FINAL SUMMARY")
print(f"{'='*70}")
print(f"Total tests collected: {total_tests}")
print(f"Total passed:          {total_passed}")
print(f"Total failed:          {total_failed}")
print(f"Total errors:          {total_errors}")
print(f"Total skipped:         {total_skipped}")

unique_failed = sorted(failed_files)
if unique_failed:
    print(f"\nFailing test files ({len(unique_failed)}):")
    for f in unique_failed:
        print(f"  - {f}")
else:
    print("\nNo failing test files detected.")

# Save results
with open("test_results_summary.txt", "w", encoding="utf-8") as f:
    f.write(f"Total tests collected: {total_tests}\n")
    f.write(f"Total passed: {total_passed}\n")
    f.write(f"Total failed: {total_failed}\n")
    f.write(f"Total errors: {total_errors}\n")
    f.write(f"Total skipped: {total_skipped}\n")
    f.write(f"\nFailing test files:\n")
    for ff in unique_failed:
        f.write(f"{ff}\n")

print(f"\nResults saved to test_results_summary.txt")
