@echo off

REM ---- Always move to the batch file's directory ----
cd /d %~dp0

REM ---- Check if venv exists ----
if not exist "venv\" (
    echo [INFO] venv not found. Creating virtual environment...
    python -m venv venv
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Failed to create venv. Make sure Python is installed and added to PATH.
        pause
        exit /b 1
    )
    echo [INFO] venv created successfully.

    REM Install requirements on first run only
    call venv\Scripts\activate
    echo [INFO] Installing dependencies from requirements.txt ...
    pip install -r requirements.txt

    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Failed to install requirements.
        pause
        exit /b 1
    )
    echo [INFO] Dependencies installed successfully.
) else (
    REM venv already exists, just activate
    call venv\Scripts\activate
)

REM ---- Run the Python script ----
echo [INFO] Running hires_batch_upscaler.py ...
python hires_batch_upscaler.py

REM ---- Done ----
echo [INFO] Script finished. Press any key to close this window.
pause >nul
