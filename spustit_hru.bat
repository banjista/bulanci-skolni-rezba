@echo off
title Bulanci: Skolni rezba
cd /d "%~dp0"
python main.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Doslo k chybe pri spousteni. Stisknete libovolnou klavesu...
    pause
)
