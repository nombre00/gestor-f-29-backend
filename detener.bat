@echo off
:: ==============================================================================
:: GESTOR F29 - Detener sistema
:: ==============================================================================
:: Detiene los contenedores del sistema de forma segura.
:: Los datos de la base de datos NO se eliminan, quedan guardados en el volumen.
:: Para volver a levantar el sistema, ejecuta iniciar.bat.
:: ==============================================================================

echo.
echo ============================================================
echo   GESTOR F29 - Deteniendo sistema...
echo ============================================================
echo.

docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker no está corriendo.
    echo.
    pause
    exit /b 1
)

:: Detiene y elimina los contenedores, pero conserva los volúmenes de datos.
:: Sin la flag --volumes, los datos de MySQL están seguros.
docker compose down

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Hubo un problema al detener el sistema.
    echo.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo   Sistema detenido correctamente.
echo   Los datos están guardados y seguros.
echo   Para volver a iniciar, ejecuta iniciar.bat
echo ============================================================
echo.
pause
