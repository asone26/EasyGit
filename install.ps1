# EasyGit PowerShell One-Click Installer
$targetDir = $PSScriptRoot

# 1. 전역 등록 실행
if (Test-Path "$targetDir\easygit.exe") {
    & "$targetDir\easygit.exe" --install
} else {
    python "$targetDir\easygit.py" --install
}

# 2. 현재 열려 있는 세션에 즉시 반영
if (Test-Path $PROFILE) {
    . $PROFILE
}
$env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")

Write-Host "------------------------------------------------------------" -ForegroundColor Green
Write-Host "[완료] 현재 PowerShell 창에 즉시 반영되었습니다!" -ForegroundColor Green
Write-Host "이제 창을 닫지 않고도 바로 'easygit' 또는 '.\easygit'을 실행하실 수 있습니다." -ForegroundColor Cyan
Write-Host "------------------------------------------------------------" -ForegroundColor Green

