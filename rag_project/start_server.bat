@echo off
cd /d "%~dp0"
echo Starting RAG API Server...
echo This will take 30-60 seconds to load models...
echo.
python api_server.py
pause
