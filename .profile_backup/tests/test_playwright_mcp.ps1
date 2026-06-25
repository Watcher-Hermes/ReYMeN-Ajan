# Playwright MCP Entegrasyon Testi — ReYMeN Ajan
# Baska bilgisayarda calistirmak icin: Node.js 18+ gerekli
# Kullanim: powershell -ExecutionPolicy Bypass -File test_playwright_mcp.ps1

param([int]$StartupWait = 8, [int]$NavWait = 12)

$INIT_MSG = '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"reymen-test","version":"1.0"}}}'
$INIT_NOTIFY = '{"jsonrpc":"2.0","method":"notifications/initialized","params":{}}'

function Find-Node {
    $candidates = @(
        "C:\Program Files\nodejs\node.exe",
        "C:\Program Files (x86)\nodejs\node.exe"
    )
    foreach ($c in $candidates) { if (Test-Path $c) { return $c } }
    $found = Get-Command node -ErrorAction SilentlyContinue
    if ($found) { return $found.Source }
    return $null
}

function Find-PlaywrightCli {
    # npx cache'de @playwright/mcp ara
    $cache = (npm config get cache 2>$null) + "\_npx"
    if (Test-Path $cache) {
        $hit = Get-ChildItem $cache |
            Where-Object {
                $pkg = "$($_.FullName)\package.json"
                if (Test-Path $pkg) {
                    $j = Get-Content $pkg -Raw | ConvertFrom-Json
                    $j.dependencies.PSObject.Properties.Name -contains "@playwright/mcp"
                }
            } |
            Select-Object -First 1

        if ($hit) {
            $cli = "$($hit.FullName)\node_modules\@playwright\mcp\cli.js"
            if (Test-Path $cli) { return $cli }
        }
    }
    return $null
}

function Test-PlaywrightUrl {
    param([string]$Name, [string]$Url)

    Write-Host ""
    Write-Host "[TEST] $Name"
    Write-Host "  URL : $Url"

    $NAV_MSG = "{`"jsonrpc`":`"2.0`",`"id`":2,`"method`":`"tools/call`",`"params`":{`"name`":`"browser_navigate`",`"arguments`":{`"url`":`"$Url`"}}}"

    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName  = $NODE
    $psi.Arguments = "`"$CLI`" --headless --isolated"
    $psi.UseShellExecute        = $false
    $psi.RedirectStandardInput  = $true
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError  = $true
    $psi.CreateNoWindow         = $true

    $proc = [System.Diagnostics.Process]::Start($psi)
    Start-Sleep $StartupWait

    $proc.StandardInput.WriteLine($INIT_MSG);    $proc.StandardInput.Flush()
    Start-Sleep 2
    $proc.StandardInput.WriteLine($INIT_NOTIFY); $proc.StandardInput.Flush()
    Start-Sleep 1
    $proc.StandardInput.WriteLine($NAV_MSG);     $proc.StandardInput.Flush()
    Start-Sleep $NavWait

    $proc.Kill()
    $out = $proc.StandardOutput.ReadToEnd()
    $proc.WaitForExit(3000) | Out-Null

    foreach ($line in ($out -split "`n")) {
        $line = $line.Trim()
        if (-not $line) { continue }
        try {
            $data = $line | ConvertFrom-Json
            $text = $data.result.content[0].text
            if ($text -match "Page URL:|Page Title:") {
                $preview = ($text -replace "`n", " ").Substring(0, [Math]::Min($text.Length, 120))
                Write-Host "  OK   -- $preview"
                return $true
            }
        } catch {}
    }

    Write-Host "  FAIL -- yanit alinamadi"
    if ($out) { Write-Host "  Ham: $($out.Substring(0,[Math]::Min($out.Length,150)))" }
    return $false
}

# ── Ana akis ─────────────────────────────────────────────────────────────────
Write-Host "=" * 60
Write-Host "ReYMeN Ajan -- Playwright MCP Entegrasyon Testi"
Write-Host "=" * 60

$NODE = Find-Node
if (-not $NODE) {
    Write-Host "HATA: node.exe bulunamadi. https://nodejs.org kur."
    exit 1
}

$CLI = Find-PlaywrightCli
if (-not $CLI) {
    Write-Host "Playwright MCP cache'de yok, indiriliyor..."
    # Ilk kez indirmek icin kisa calistir
    Start-Process -FilePath "C:\Program Files\nodejs\npx.cmd" `
        -ArgumentList "-y","@playwright/mcp@latest","--version" `
        -Wait -NoNewWindow 2>$null
    $CLI = Find-PlaywrightCli
    if (-not $CLI) {
        Write-Host "HATA: Playwright MCP indirilemedi. 'npx -y @playwright/mcp@latest' manuel dene."
        exit 1
    }
}

Write-Host "node : $NODE"
Write-Host "cli  : $CLI"

$tests = @(
    @{Name="Temel gezinme"; Url="https://example.com"},
    @{Name="HTTPS endpoint"; Url="https://httpbin.org/get"},
    @{Name="GitHub";         Url="https://github.com"}
)

$passed = 0
foreach ($t in $tests) {
    if (Test-PlaywrightUrl -Name $t.Name -Url $t.Url) { $passed++ }
}

Write-Host ""
Write-Host "=" * 60
Write-Host "SONUC: $passed/$($tests.Count) test gecti"
Write-Host "=" * 60

if ($passed -eq $tests.Count) {
    Write-Host ""
    Write-Host "PLAYWRIGHT MCP CALISIYOR -- ReYMeN ajana hazir!"
    Write-Host "Baska bilgisayarda da calisir (Node.js 18+ gerekli)."
    exit 0
} elseif ($passed -gt 0) {
    Write-Host "Kismi basari."
    exit 0
} else {
    Write-Host "Basarisiz -- sorun giderme: skills/playwright-mcp/references/troubleshooting.md"
    exit 1
}
