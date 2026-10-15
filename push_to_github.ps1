<#
.SYNOPSIS
    Skript pro snadné nahrání hry Bulánci na GitHub.
.DESCRIPTION
    Inicializuje git repozitář, vytvoří commit a nahraje kód do vašeho vzdáleného repozitáře na GitHubu.
#>

[CmdletBinding()]
param (
    [string]$RepoUrl
)

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "   Bulánci 2026 - Nahrání na GitHub     " -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

# 1. Kontrola dostupnosti programu Git
$possiblePaths = @(
    "$PSScriptRoot\portable_git\cmd\git.exe",
    "U:\Python\Bulanci2026\portable_git\cmd\git.exe",
    "C:\Program Files\Git\cmd\git.exe",
    "$env:LOCALAPPDATA\Programs\Git\cmd\git.exe",
    "C:\Program Files (x86)\Git\cmd\git.exe"
)
foreach ($p in $possiblePaths) {
    if (Test-Path $p) {
        $env:Path = "$(Split-Path $p);$env:Path"
        break
    }
}
$gitCmd = Get-Command git -ErrorAction SilentlyContinue

if (-not $gitCmd) {
    Write-Host ""
    Write-Host "[!] Git nebyl nalezen v systému." -ForegroundColor Yellow
    Write-Host "    Možnosti nahrání:" -ForegroundColor White
    Write-Host "    1. Nainstalujte Git z https://git-scm.com/download/win a spusťte tento skript znovu." -ForegroundColor White
    Write-Host "    2. Nebo nahrajte soubory přímo přes webový prohlížeč na GitHub.com:" -ForegroundColor White
    Write-Host "       - Vytvořte nový repozitář na https://github.com/new" -ForegroundColor Gray
    Write-Host "       - Klikněte na 'uploading an existing file' a přetáhněte sem celou složku Bulanci2026." -ForegroundColor Gray
    Write-Host ""
    return
}

# 2. Zadání URL repozitáře
if (-not $RepoUrl) {
    Write-Host ""
    $RepoUrl = Read-Host "Zadejte URL vašeho GitHub repozitáře (např. https://github.com/vase-jmeno/bulanci-skolni-rezba.git)"
}

if (-not $RepoUrl) {
    Write-Host "[-] URL repozitáře nebyla zadána. Nahrávání přerušeno." -ForegroundColor Red
    return
}

# 3. Git inicializace a push
Write-Host "[*] Inicializuji Git repozitář..." -ForegroundColor Green
git init

Write-Host "[*] Přidávám soubory..." -ForegroundColor Green
git add .

Write-Host "[*] Vytvářím commit..." -ForegroundColor Green
git commit -m "Bulanci: Skolni rezba - seminarni projekt z informatiky"

Write-Host "[*] Nastavuji hlavní větev (main)..." -ForegroundColor Green
git branch -M main

Write-Host "[*] Propojuji se vzdáleným repozitářem $RepoUrl..." -ForegroundColor Green
git remote remove origin 2>$null
git remote add origin $RepoUrl

Write-Host "[*] Odesílám kód na GitHub..." -ForegroundColor Green
git push -u origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "[✓] Hra byla úspěšně nahrána na váš GitHub!" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "[!] Odeslání selhalo. Zkontrolujte prosím přístupová práva nebo zda repozitář existuje." -ForegroundColor Yellow
}
