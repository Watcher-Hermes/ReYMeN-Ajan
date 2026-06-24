# Playwright MCP — Sorun Giderme

## "Browser not found" / Tarayıcı bulunamadı

```powershell
npx playwright install chromium
# Tümünü kurmak için:
npx playwright install
```

## MCP sunucusu başlamıyor

```powershell
# Manuel test:
npx -y @playwright/mcp@latest --headless
# → "Listening on stdio" mesajı görünmeli
```

config.yaml'da `command: npx` ve `args` doğru mu kontrol et.

## "Navigation timeout"

`--timeout-navigation 120000` ekle (ms cinsinden).

## Headless modda site çalışmıyor

Bazı siteler headless tespiti yapar. `--headless` argümanını kaldır:

```yaml
mcp_servers:
  playwright:
    command: npx
    args:
    - -y
    - "@playwright/mcp@latest"
    # --headless yok = görünür pencere
```

## Görüntü/Screenshot çalışmıyor

`--caps vision` ekle:

```yaml
    args:
    - -y
    - "@playwright/mcp@latest"
    - --caps
    - vision
```

## MCP log dosyası

```
C:\Users\marko\AppData\Local\hermes\profiles\reymen\mcp-stderr.log
```
