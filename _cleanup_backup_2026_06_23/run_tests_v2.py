#!/usr/bin/env python3
"""Run all test_*.py excluding ReYMeN_reference, batch of 10, report summary."""
import subprocess, os, glob, re, sys, json

PROJECT = r"C:\Users\marko\Desktop\Reymen Proje\hermes_projesi"
PYTHON = os.path.join(PROJECT, "venv", "Scripts", "python.exe")
os.chdir(PROJECT)

test_files = sorted(glob.glob("tests/test_*.py"))
test_files = [f for f in test_files if "ReYMeN_reference" not in f]
print(f"Found {len(test_files)} test files total.")

BATCH = 10
batches = [test_files[i:i+BATCH] for i in range(0, len(test_files), BATCH)]
print(f"Split into {len(batches)} batches of up to {BATCH}.\n")

aggregate = {"passed": 0, "failed": 0, "errors": 0, "skipped": 0}
failed_files = set()

for idx, batch in enumerate(batches):
    names = [os.path.basename(f) for f in batch]
    print(f"[Batch {idx+1}/{len(batches)}] {' '.join(names)}", flush=True)
    try:
        r = subprocess.run(
            [PYTHON, "-m", "pytest", "--tb=line", "--no-header", "-q"] + batch,
            capture_output=True, text=True, timeout=300, cwd=PROJECT
        )
    except subprocess.TimeoutExpired:
        print(f"  TIMEOUT - marking all as unknown")
        for bf in batch:
            failed_files.add(bf)
        continue

    out = r.stdout + r.stderr
    # Parse summary line
    for line in reversed(out.splitlines()):
        line = line.strip()
        m = re.search(r'(\d+)\s+passed', line)
        n = re.search(r'(\d+)\s+failed', line)
        e = re.search(r'(\d+)\s+error', line)
        s = re.search(r'(\d+)\s+skipped', line)
        if m or n or e:
            p = int(m.group(1)) if m else 0
            f = int(n.group(1)) if n else 0
            er = int(e.group(1)) if e else 0
            sk = int(s.group(1)) if s else 0
            aggregate["passed"] += p
            aggregate["failed"] += f
            aggregate["errors"] += er
            aggregate["skipped"] += sk
            print(f"  -> {p}p {f}f {er}e {sk}s")
            if f > 0 or er > 0:
                for bf in batch:
                    failed_files.add(bf)
            break
    
    # Find FAILED/ERROR lines for individual test identification
    for line in out.splitlines():
        if line.startswith("FAILED "):
            parts = line.split()
            for p in parts:
                if p.startswith("tests/"):
                    failed_files.add(p)
                    break

# Deduplicate 
unique_failed = sorted(set(failed_files))

print(f"\n{'='*60}")
print(f"FINAL RESULTS")
print(f"{'='*60}")
total = sum(aggregate.values())
print(f"Total tests collected: {total}")
print(f"Passed:  {aggregate['passed']}")
print(f"Failed:  {aggregate['failed']}")
print(f"Errors:  {aggregate['errors']}")
print(f"Skipped: {aggregate['skipped']}")
if unique_failed:
    print(f"\nFailing files ({len(unique_failed)}):")
    for f in unique_failed:
        print(f"  - {f}")
else:
    print(f"\nNo failures detected.")

# Save
with open("test_results_v2.json", "w") as f:
    json.dump({"aggregate": aggregate, "failed_files": unique_failed}, f, indent=2)
print(f"\nResults saved to test_results_v2.json")
