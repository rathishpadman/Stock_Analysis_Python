@echo off
REM Equity Research Pipeline Runner
REM This batch file runs the equity analysis pipeline with a template and output file

setlocal enabledelayedexpansion

REM Get the current directory (where this batch file is located)
set SCRIPT_DIR=%~dp0

REM Set the Python executable path (virtual environment)
set PYTHON_EXE=%SCRIPT_DIR%venv\Scripts\python.exe

REM Check if virtual environment exists
if not exist "%PYTHON_EXE%" (
    echo Error: Virtual environment not found at %PYTHON_EXE%
    echo Please ensure the venv folder exists with Python installed.
    pause
    exit /b 1
)

REM Set default template and output paths
set TEMPLATE=%SCRIPT_DIR%Stocks_Analysis_Template_v3.xlsx
set OUTPUT=Stocks_Analysis_Populated.xlsx

REM Check if template file exists
if not exist "%TEMPLATE%" (
    echo Error: Template file not found at %TEMPLATE%
    echo Please ensure Stocks_Analysis_Template_v3.xlsx exists in this directory.
    pause
    exit /b 1
)

REM Change to script directory
cd /d "%SCRIPT_DIR%"

REM Run the pipeline
echo.
echo ========================================
echo  Equity Research Pipeline
echo ========================================
echo.
echo Template: %TEMPLATE%
echo Output:   %OUTPUT%
echo.
echo Starting pipeline...
echo.

"%PYTHON_EXE%" run_refresh.py --template "%TEMPLATE%"

REM Check if the command was successful
if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo  Pipeline completed successfully!
    echo ========================================
    echo.
) else (
    echo.
    echo ========================================
    echo  Pipeline failed with error code: %errorlevel%
    echo ========================================
    echo.
    pause
    exit /b %errorlevel%
)

endlocal
