@echo off
REM Start the app on Windows
call venv\Scripts\activate
python -m streamlit run app.py
pause
