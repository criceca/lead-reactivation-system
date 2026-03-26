@echo off
setlocal enabledelayedexpansion

echo 🚀 Iniciando Sistema de Reactivación de Leads
echo ==============================================
echo.

REM 1️⃣ Activar ambiente virtual
echo 1️⃣ Activando ambiente virtual...
call venv\Scripts\activate.bat

REM 2️⃣ Verificar base de datos
if not exist lead_reactivation.db (
    echo 2️⃣ Inicializando base de datos...
    python -c "from app.database.db import init_db; init_db()"
    echo    ✅ Base de datos creada
) else (
    echo 2️⃣ Base de datos ya existe ✅
)

echo.

REM 3️⃣ Iniciar API
echo 3️⃣ Iniciando API en puerto 8000...
start "API" cmd /c python run_api.py

REM Guardar PID aproximado usando PowerShell
for /f "tokens=2" %%a in ('tasklist ^| findstr python') do set API_PID=%%a

echo    API iniciada
echo.

REM 4️⃣ Esperar a que la API esté lista
echo 4️⃣ Esperando a que la API esté lista...

set /a counter=0

:check_api
set /a counter+=1

curl -s http://localhost:8000/health >nul 2>&1
if %errorlevel%==0 (
    echo    ✅ API lista!
    goto api_ready
)

if %counter% GEQ 10 (
    echo    ❌ API no respondió a tiempo
    goto error
)

echo    Esperando... (%counter%/10)
timeout /t 2 >nul
goto check_api

:api_ready


echo.
REM 5️⃣ Iniciar Bot de Telegram
echo 5️⃣ Iniciando Bot de Telegram...
start "BOT" cmd /c python run_telegram_bot.py
echo    Bot iniciado
timeout /t 3 >nul


echo.
echo 5️⃣ Iniciando Streamlit en puerto 8501...
echo.
echo ==============================================
echo ✅ Sistema iniciado correctamente
echo.
echo URLs disponibles:
echo   - API Docs:  http://localhost:8000/docs
echo   - Streamlit: http://localhost:8501
echo.
echo Presiona Ctrl+C para detener todo
echo ==============================================
echo.

streamlit run streamlit_app.py

echo.
echo 🛑 Deteniendo API...
taskkill /IM python.exe /F >nul 2>&1

echo ✅ Sistema detenido
goto end

:error
echo.
echo ❌ Error: La API no pudo iniciarse
taskkill /IM python.exe /F >nul 2>&1
exit /b 1

:end
endlocal