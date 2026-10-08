@echo off
REM Inicia la pagina del modulo IMAGEN
cd /d "%~dp0"
".venv\Scripts\python.exe" -m streamlit run app_imagen.py
