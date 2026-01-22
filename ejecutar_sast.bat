@echo off
echo ============================================================
echo    SOLO SAST - Analisis Estatico con Bandit
echo ============================================================
echo.

cd /d "%~dp0"

if not exist "reports" mkdir reports

echo Ejecutando Bandit...
echo.
python -m bandit -r app.py -f txt
echo.

python -m bandit -r app.py -f html -o reports/bandit_report.html
python -m bandit -r app.py -f json -o reports/bandit_report.json

echo.
echo ============================================================
echo    SAST COMPLETADO
echo ============================================================
echo Reporte: %cd%\reports\bandit_report.html
echo.
start reports\bandit_report.html
pause
