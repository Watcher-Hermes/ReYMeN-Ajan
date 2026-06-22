# BAD — kills the shell
[hook]
on-activate = """
  if [ ! -f config.json ]; then
    echo "Missing config"
    exit 1
  fi
"""