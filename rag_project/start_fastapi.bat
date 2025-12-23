@echo off
echo ========================================
echo Starting FastAPI RAG Server
echo ========================================
echo.

REM Activate virtual environment if exists
if exist venv\Scripts\activate.bat (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
)

echo Installing/Updating dependencies...
pip install -r requirements_api.txt
echo.

echo Starting FastAPI server...
echo Server will be available at: http://localhost:5000
echo API Documentation (Swagger): http://localhost:5000/docs
echo.

python api_server_fastapi.py

pause
