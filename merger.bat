@echo off
TITLE Agro Sentinel HTML Parser
CLS

ECHO ==================================================
ECHO      Starting HTML Parsing Engine
ECHO ==================================================
ECHO.

REM --- PATH CONFIGURATION ---
SET "VENV_PYTHON=C:\Users\Saket Dixit\tf-env\Scripts\python.exe"
SET "SCRIPT_PATH=C:\Users\Saket Dixit\Downloads\Agro Sentinel\src\data\merge.py"

REM --- DEBUG: CHECK PATHS ---
IF NOT EXIST "%VENV_PYTHON%" (
    ECHO CRITICAL ERROR: Python not found at:
    ECHO "%VENV_PYTHON%"
    PAUSE
    EXIT
)

IF NOT EXIST "%SCRIPT_PATH%" (
    ECHO CRITICAL ERROR: Script not found at:
    ECHO "%SCRIPT_PATH%"
    PAUSE
    EXIT
)

REM --- INSTALL DEPENDENCIES ---
ECHO Installing lxml and beautifulsoup4...
"%VENV_PYTHON%" -m pip install pandas lxml beautifulsoup4 html5lib

ECHO.

REM --- RUN SCRIPT ---
ECHO Running Merge Script...
"%VENV_PYTHON%" "%SCRIPT_PATH%"

ECHO.
ECHO ==================================================
ECHO      Process Completed.
ECHO ==================================================
PAUSE