# GOOD — return from hook, don't exit
[hook]
on-activate = """
  if [ ! -f config.json ]; then
    echo "Missing config — run setup first"
    return 1
  fi
"""
```

### Storing Secrets in Manifest

```toml