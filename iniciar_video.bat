@echo off
REM Inicia el sistema del grupo VIDEO (camara, deteccion y alarma).
REM Las capturas de la alarma se guardan en alertas\ y la pagina de IMAGEN las procesa.
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    echo Primero ejecuta iniciar_app.bat para preparar el entorno.
    pause
    exit /b 1
)
".venv\Scripts\python.exe" principal.py
