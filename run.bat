@echo off
call venv\Scripts\activate

REM Start Streamlit in the background
start "" streamlit run Home.py

REM Give the server a few seconds to boot up before opening the browser
timeout /t 2 /nobreak >nul

REM Open Chrome specifically, without changing your default browser
start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" "http://localhost:8501"