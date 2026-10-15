@echo off
title Nahrani na GitHub - Bulanci
cd /d "%~dp0"
set PATH=%~dp0.portable_git\cmd;%PATH%
git config --global --add safe.directory "*"
echo ========================================================
echo   Odesilani Bulanku na GitHub repozitar:
echo   https://github.com/banjista/bulanci-skolni-rezba.git
echo ========================================================
echo.
git push -u origin main
echo.
if %ERRORLEVEL% NEQ 0 (
    echo [!] Odeslani vyzaduje prihlaseni k vasemu GitHub uctu.
    echo     GitHub vyzaduje zadat Uzivatelske jmeno (banjista) a misto hesla Personal Access Token
    echo     (vytvorite na https://github.com/settings/tokens s pravem 'repo').
) else (
    echo [V] Uspech! Projekt byl uspesne odeslan na GitHub!
)
echo.
pause
