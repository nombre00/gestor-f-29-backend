@echo off
:: ==============================================================================
:: GESTOR F29 - Backup de base de datos
:: ==============================================================================
:: Genera un archivo de respaldo completo de la base de datos MySQL.
:: El archivo se guarda en la carpeta "backups\" con fecha y hora en el nombre.
:: Se recomienda ejecutar este backup al menos una vez por semana.
:: ==============================================================================

echo.
echo ============================================================
echo   GESTOR F29 - Generando backup...
echo ============================================================
echo.

docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker no esta corriendo.
    echo Por favor inicia el sistema con iniciar.bat primero.
    echo.
    pause
    exit /b 1
)

:: Crea la carpeta "backups" si no existe.
if not exist "backups\" mkdir backups

:: Genera un nombre de archivo con fecha y hora actual.
:: Formato: backup_YYYYMMDD_HHMMSS.sql
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
set FECHA=%datetime:~0,8%
set HORA=%datetime:~8,6%
set NOMBRE_ARCHIVO=backups\backup_%FECHA%_%HORA%.sql

echo Generando archivo: %NOMBRE_ARCHIVO%
echo.

:: Lee MYSQL_ROOT_PASSWORD directamente desde el archivo .env.
set DB_PASSWORD=
for /f "usebackq tokens=1,* delims==" %%A in (".env") do (
    if "%%A"=="MYSQL_ROOT_PASSWORD" set DB_PASSWORD=%%B
)

if "%DB_PASSWORD%"=="" (
    echo [ERROR] No se encontro MYSQL_ROOT_PASSWORD en el archivo .env
    echo Verifica que el archivo .env existe y tiene esa variable definida.
    echo.
    pause
    exit /b 1
)

:: Ejecuta mysqldump dentro del contenedor db.
::   --single-transaction : hace el backup sin bloquear las tablas.
::   --routines           : incluye procedimientos almacenados si los hubiera.
docker compose exec -T db mysqldump ^
    --user=root ^
    --password=%DB_PASSWORD% ^
    --single-transaction ^
    --routines ^
    gestorf29 > %NOMBRE_ARCHIVO%

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] El backup fallo. Verifica que el sistema este corriendo.
    echo.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo   Backup completado exitosamente.
echo   Archivo guardado en: %NOMBRE_ARCHIVO%
echo.
echo   RECOMENDACION: Copia este archivo a un disco externo
echo   o a una ubicacion fuera de este PC.
echo ============================================================
echo.
pause
