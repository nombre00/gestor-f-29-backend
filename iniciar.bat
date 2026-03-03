@echo off
:: ==============================================================================
:: GESTOR F29 - Iniciar sistema
:: ==============================================================================
:: Levanta los contenedores de la base de datos y el backend.
:: Si es la primera vez, construye la imagen del backend automáticamente.
:: Ejecutar con doble clic o desde la terminal en esta misma carpeta.
:: ==============================================================================

echo.
echo ============================================================
echo   GESTOR F29 - Iniciando sistema...
echo ============================================================
echo.

:: Verifica que Docker esté corriendo antes de intentar levantar los contenedores.
:: Si Docker Desktop no está abierto, docker compose up falla con un error confuso.
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker no está corriendo.
    echo Por favor abre Docker Desktop y espera a que termine de cargar.
    echo Luego vuelve a ejecutar este archivo.
    echo.
    pause
    exit /b 1
)

:: Levanta todos los servicios definidos en docker-compose.yml.
::   -d        : modo "detached", corre en segundo plano (no bloquea la terminal).
::   --build   : reconstruye la imagen del backend si hubo cambios en el código.
::               En instalaciones normales no reconstruye si no hay cambios,
::               así que no agrega tiempo innecesario.
echo Levantando contenedores...
docker compose up -d --build

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Hubo un problema al levantar el sistema.
    echo Revisa los logs con: docker compose logs
    echo.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo   Sistema iniciado correctamente.
echo   Accede desde el navegador en: http://localhost:8000
echo ============================================================
echo.
pause
