@echo off
chcp 65001 >nul 2>&1
cd /d "C:\Users\marko\Desktop\Reymen Proje\hermes_projesi"
python reymen/sistem/monitoring/config_guard.py --daemon --fix --interval 5
