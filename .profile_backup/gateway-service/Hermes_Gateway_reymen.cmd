@echo off
rem Hermes Agent Gateway - Messaging Platform Integration
cd /d C:\Users\marko\AppData\Local\hermes\profiles\reymen
set "HERMES_HOME=C:\Users\marko\AppData\Local\hermes\profiles\reymen"
set "PYTHONIOENCODING=utf-8"
set "HERMES_GATEWAY_DETACHED=1"
set "TELEGRAM_BOT_TOKEN=8774151638:AAH3KTBmddzaYpFpfF4Yp_nksmPH80UUAQo"
set "VIRTUAL_ENV=C:\Users\marko\AppData\Local\hermes\hermes-agent\venv"
C:\Users\marko\AppData\Local\hermes\hermes-agent\venv\Scripts\pythonw.exe -m hermes_cli.main --profile reymen gateway run
exit /b 0