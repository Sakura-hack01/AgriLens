@echo off
echo ==============================================
echo      Agro-Sentinel Data Scraper (v2.0)
echo ==============================================
echo.
echo Checking for Python Environment...

:: Activate your virtual environment
call "C:\Users\Saket Dixit\tf-env\Scripts\activate.bat"

if %errorlevel% neq 0 (
    echo [ERROR] Could not activate 'tf-env'.
    echo Please ensure the folder 'tf-env' exists.
    pause
    exit
)

echo Environment Activated.
echo Starting Scraper...
echo.

:: --- THE FIX IS BELOW ---
:: Point to the file inside the src\data folder
python "C:\Users\Saket Dixit\Downloads\Agro Sentinel\src\data\scraper.py"

echo.
echo ==============================================
echo Scraping Finished.
pause