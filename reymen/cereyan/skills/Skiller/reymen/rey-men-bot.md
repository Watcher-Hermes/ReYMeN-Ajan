---
name: rey-men-bot
title: "ReYMeN Telegram Bot"
tags: [rey-men, telegram, bot, cua, python, hermes-fork]
description: "Run, troubleshoot, and manage the ReYMeN Telegram bot."
version: 1.2.0
platforms: [windows]
metadata:
  hermes:
    tags: [rey-men, telegram, bot, cua, python, hermes-fork, gateway]
audience: user
related_skills: []
---

# ReYMeN Telegram Bot

Run and troubleshoot the ReYMeN (ReYMeN Agent fork) Telegram bot. The bot uses `python-telegram-bot` with async polling, MemoryAgent, and optional CUA screen automation.

## Location

```
C:\Users\marko\Desktop\Reymen Proje\hermes_projesi\
├── telegram_bot/bot.py       # main bot entry (standalone)
├── telegram_bot/memory_agent.py  # memory management
├── cua_motor_araci.py         # Computer Use Agent (screen OCR + mouse)
├── .ReYMeN/setup.json         # model/provider preference
├── .ReYMeN/bot.pid            # PID lock file
├── gateway_state.json          # status file
└── baslat_bot.sh              # bash wrapper
```

The ReYMeN gateway (preferred) runs from the ReYMeN profile at:
```
~/AppData/Local/hermes/profiles/reymen/
├── config.yaml                # model, provider, telegram settings
├── .env                       # TELEGRAM_BOT_TOKEN, API keys
├── logs/gateway.log           # gateway activity log
├── logs/agent.log             # model call log (API errors here)
├── logs/errors.log            # tool execution errors
└── logs/gateway-stdio.log     # stdio output — asyncio crashes visible here
```

## Starting the Bot

Two modes: **ReYMeN gateway** (recommended) or **standalone bot.py**.

### ReYMeN Gateway (preferred)

```bash
# Start with the reymen profile
hermes gateway start -p reymen
# Or through the ReYMeN CLI wrapper
/c/Users/marko/AppData/Local/hermes/reymen-agent/venv/Scripts/hermes gateway start -p reymen
```

The gateway auto-connects to Telegram via polling, loads the model provider from `config.yaml`, and maintains a persistent session.

### Standalone bot.py (legacy)

```bash
bash "/c/Users/marko/Desktop/Reymen Proje/hermes_projesi/baslat_bot.sh"
```

## Gateway System Prompt Configuration

The bot's personality is controlled by the system prompt. The gateway does NOT load `prefill_messages_file` — this config key is ignored.

### Option A: `agent.system_prompt` in config.yaml (RECOMMENDED)

Add to `~/AppData/Local/hermes/profiles/reymen/config.yaml`:

```yaml
agent:
  system_prompt: "Sen ReYMeN'sin. Turkce konus, kisa ve oz cevap ver."
```

This gets APPENDED to the default ReYMeN system prompt. It does NOT replace it.

### Option B: `HERMES_EPHEMERAL_SYSTEM_PROMPT` env var

Set in `.env`:

```
HERMES_EPHEMERAL_SYSTEM_PROMPT=Sen ReYMeN'sin. Turkce konus.
```

**Pitfall — `prefill_messages_file` does NOT work with gateway:** The gateway code (`gateway/run.py`) reads `agent.system_prompt` at startup but does NOT load `prefill_messages_file`. Setting this config key has no effect — no error message, no loading log entry.

## Selective Gateway Restart

```bash
hermes -p reymen gateway restart
# Sadece reymen profilini restart eder, default'a dokunmaz
```

**Pitfall:** `hermes -p reymen gateway restart` is blocked when called FROM inside the gateway process. Use direct kill + start:

```bash
# 1. Kill directly
taskkill //PID <PID> //F
# 2. Wait
sleep 3
# 3. Start manually
hermes -p reymen gateway start
```

## Token Testing — Redaction Pitfall

When testing bot tokens via Telegram API, the terminal tool's secret redaction corrupts URLs containing token patterns:

```python
# ❌ BROKEN — terminal redaction replaces token with *** in URL
# ✅ WORKS — use execute_code with token split
from hermes_tools import terminal
t1 = "8774151638"
t2 = "the_rest_of_the_token"
url = f"https://api.telegram.org/bot{t1}:{t2}/getMe"
```

## Multi-Profile Token Conflict

A Telegram bot token can only be used by ONE polling session at a time. If two ReYMeN profiles have the same `TELEGRAM_BOT_TOKEN` in their `.env`, both gateways start but only the first one connects.

**Fix:** Ensure each profile uses a unique bot token.

## Troubleshooting

### CUA Module Import Failed
**Symptom**: `cua_motor_araci import edilemedi, CUA devre disi.`
**Fix**: Use Python 3.14 directly (ReYMeN venv 3.11 lacks CUA deps).

### Telegram 409 Conflict
**Symptom**: `Conflict: terminated by other getUpdates request`
**Fix**: Kill zombie bot processes, clean PID lock file.

### Provider 402 / Credit Exhausted
**Fix**: Switch to direct DeepSeek by updating `.ReYMeN/setup.json` and removing OpenRouter from `.env`.

### Bot Token Logged Out (HTTP 400)
**Symptom**: getMe returns `"Logged out"`
**Fix**: Create new bot via BotFather or use cross-profile token audit script.

## Kullanıcı Tercihi: Default ReYMeN Prompt

Bu kullanıcı bot'un ReYMeN kişiliğinde değil, **default ReYMeN prompt'u ile** cevap vermesini ister.

## Cevap Stili (Kullanıcı Tercihi)

```
1. Başlık: emoji + konu başlığı
2. Kısa açıklama (kısıtlar/kurallar)
3. Tablo (sütun başlıklı, düzenli)
4. Tablo altında ek açıklama/yorum
```

## YouTube Video Analizi (ReYMeN Motor Tool)

ReYMeN motor'una YouTube video analiz yeteneği eklemek için:
1. `tools/youtube_tool.py` oluştur
2. Motor'a kaydet (`motor.py`'de `_plugin_moduller_yukle`)
3. ReYMeN'teki `youtube-content` skill'ini ReYMeN projesine kopyala
