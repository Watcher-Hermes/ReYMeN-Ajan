## Tool 8: Fun ASCII Utilities (via curl)

These free services return ASCII art directly — great for fun extras.

### QR Codes as ASCII Art

```bash
curl -s "qrenco.de/Hello+World"
curl -s "qrenco.de/https://example.com"
```

### Weather as ASCII Art

```bash
curl -s "wttr.in/London"          # Full weather report with ASCII graphics
curl -s "wttr.in/Moon"            # Moon phase in ASCII art
curl -s "v2.wttr.in/London"       # Detailed version
```