@echo off
echo ============================================================
echo    SOLO DAST - Analisis Dinamico con OWASP ZAP
echo ============================================================
echo.

cd /d "%~dp0"

if not exist "reports" mkdir reports

echo [1/3] Verificando Docker...
docker ps > nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker no esta corriendo!
    echo Por favor inicia Docker Desktop y vuelve a intentar.
    pause
    exit /b 1
)
echo Docker OK!
echo.

echo [2/3] Iniciando aplicacion Flask...
start /B python app.py
echo Esperando 3 segundos...
timeout /t 3 /nobreak > nul
echo.

echo [3/3] Ejecutando OWASP ZAP...
echo Esto puede tomar unos minutos...
echo.
docker run --rm -v "%cd%\reports:/zap/wrk:rw" --add-host=host.docker.internal:host-gateway ghcr.io/zaproxy/zaproxy:stable zap-baseline.py -t http://host.docker.internal:5000 -r zap_report.html -J zap_report.json -I

echo.
echo ============================================================
echo    DAST COMPLETADO
echo ============================================================
echo Reporte: %cd%\reports\zap_report.html
echo.
start reports\zap_report.html
pause
