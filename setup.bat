@echo off
REM One-time setup on Windows: creates a virtual environment and installs packages
python -m venv venv
call venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
echo.
echo Setup complete. Now open the .env file, paste your MongoDB link, then double-click run.bat
pause
