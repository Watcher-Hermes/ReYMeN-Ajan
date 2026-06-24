# Check for common issues
git diff | grep -i "todo\|fixme\|hack\|xxx"
git diff | grep "print("  # Debug statements
git diff | grep "DEBUG = True"  # Debug mode
git diff | grep "import pdb"  # Debugger
```

Checklist:
- No debugging statements (print, pdb, breakpoint())
- No TODO/FIXME comments in critical code
- No hardcoded secrets or credentials
- Database migrations included for model changes
- Configuration changes documented
- Error handling present for external calls
- Transaction management where needed