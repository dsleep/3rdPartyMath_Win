@ECHO OFF

echo Updating Git
git submodule update --recursive --remote --merge

PowerShell.exe -NoProfile -ExecutionPolicy Bypass -Command "& '%~dpn0.ps1'"

PAUSE