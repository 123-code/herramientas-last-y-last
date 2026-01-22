@echo off
echo ============================================================
echo    PIPELINE DE SEGURIDAD - SAST + DAST
echo ============================================================
echo.

cd /d "%~dp0"

echo [1/4] Creando directorio de reportes...
if not exist "reports" mkdir reports

echo.
echo [2/4] Ejecutando SAST con Bandit...
echo ------------------------------------------------------------
python -m bandit -r server_main.py -f html -o reports/bandit_report.html
python -m bandit -r server_main.py -f json -o reports/bandit_report.json
python -m bandit -r server_main.py -f txt
echo.

echo [3/4] Iniciando aplicacion Flask en segundo plano...
start /B python server_main.py
echo Esperando 3 segundos para que inicie...
timeout /t 3 /nobreak > nul

echo.
echo [4/4] Ejecutando DAST con OWASP ZAP (requiere Docker)...
echo ------------------------------------------------------------
docker run --rm -v "%cd%\reports:/zap/wrk:rw" --add-host=host.docker.internal:host-gateway ghcr.io/zaproxy/zaproxy:stable zap-baseline.py -t http://host.docker.internal:5000 -r zap_report.html -J zap_report.json -I

echo.
echo ============================================================
echo    PIPELINE COMPLETADO
echo ============================================================
echo.
echo Reportes generados en: %cd%\reports
echo   - bandit_report.html (SAST)
echo   - bandit_report.json (SAST)
echo   - zap_report.html (DAST)
echo   - zap_report.json (DAST)
echo.
echo Abriendo reportes...
start reports\bandit_report.html
start reports\zap_report.html
echo.
pause
