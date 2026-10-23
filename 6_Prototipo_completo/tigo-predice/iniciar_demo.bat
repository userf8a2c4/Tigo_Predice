@echo off
REM ============================================================
REM  Tigo Predice - doble clic para iniciar la demo
REM  Abre http://127.0.0.1:8000 en el navegador. Ctrl+C para cerrar.
REM ============================================================
chcp 65001 >nul
cd /d "%~dp0"
set "VENV=%USERPROFILE%\.venvs\tigo-predice"
set "PY=%VENV%\Scripts\python.exe"

echo.
echo   ===  TIGO PREDICE  ===
echo   Que el cliente se entere por nosotros, no por la falla.
echo.

if not exist "%PY%" (
    echo [1/4] Creando entorno de Python por primera vez...
    python -m venv "%VENV%" || goto :error_python
    "%PY%" -m pip install --disable-pip-version-check -q -r requirements.lock || goto :error
) else (
    echo [1/4] Entorno de Python listo.
)

if not exist "reports\metricas_hogar.json" goto :preparar
if not exist "data\tigo_predice.db" goto :preparar
echo [2/4] Datos y modelos listos.
goto :interfaz

:preparar
echo [2/4] Generando datos simulados y entrenando la IA ^(2 minutos^)...
"%PY%" -m ml.generar_datos >nul || goto :error
"%PY%" -m ml.generar_hogar >nul || goto :error
"%PY%" -m ml.entrenar || goto :error
"%PY%" -m ml.entrenar_72h || goto :error
"%PY%" -m ml.entrenar_hogar || goto :error
"%PY%" -m ml.evaluar >nul || goto :error

:interfaz

if not exist "frontend\dist\index.html" (
    echo [3/4] Compilando la interfaz...
    pushd frontend
    call npm install --no-fund --no-audit || goto :error
    call npm run build || goto :error
    popd
) else (
    echo [3/4] Interfaz lista.
)

echo [4/4] Iniciando servidor en http://127.0.0.1:8000 ...
echo.
if not defined TIGO_SIN_NAVEGADOR start "" cmd /c "timeout /t 5 >nul & start http://127.0.0.1:8000/"
"%PY%" -m uvicorn backend.app.main:app --port 8000
goto :eof

:error_python
echo.
echo  No se encontro Python. Instale Python 3.11 o superior desde python.org y vuelva a intentar.
pause
exit /b 1

:error
echo.
echo  Algo fallo. Revise el mensaje de arriba.
pause
exit /b 1
