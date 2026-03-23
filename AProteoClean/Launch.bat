@echo off
echo Lansare ProteoClean...
cd /d "%~dp0"
start "" .venv\Scripts\python.exe -m streamlit run Home.py
pause
