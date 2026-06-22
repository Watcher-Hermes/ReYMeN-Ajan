#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UI/UX Pro Max - ReYMeN Agent wrapper
Provides design intelligence search + design system generation.

Usage:
    python3 ~/.hermes/scripts/ui-ux-pro-max/uipro.py search "beauty spa" --domain product
    python3 ~/.hermes/scripts/ui-ux-pro-max/uipro.py search "SaaS dashboard" --design-system -p "MyApp"
    python3 ~/.hermes/scripts/ui-ux-pro-max/uipro.py search "form validation" --stack react
    python3 ~/.hermes/scripts/ui-ux-pro-max/uipro.py search "typography" --domain typography
"""
import subprocess, sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
result = subprocess.run(
    [sys.executable, str(SCRIPT_DIR / "search.py")] + sys.argv[1:],
    cwd=str(SCRIPT_DIR),
)
sys.exit(result.returncode)
