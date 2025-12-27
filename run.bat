@echo off
REM Simple script to run the Python console app on Windows

REM Check if virtual environment exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv

    echo Installing dependencies...
    call venv\Scripts\activate.bat
    pip install -q -r requirements.txt
) else (
    call venv\Scripts\activate.bat
)

REM Run the application
python -m src.main %*
