@echo off
echo ========================================================
echo   INICIANDO SISTEMA DE INSTRUMENTACAO CAERN (OFFLINE)
echo ========================================================
echo.
echo 1. Iniciando servidor...
echo 2. Quando aparecer "Running on http://...", o sistema esta pronto.
echo.
echo Pressione CTRL+C para fechar quando terminar.
echo.

cd /d "%~dp0"
start http://localhost:5000
python app.py
pause
