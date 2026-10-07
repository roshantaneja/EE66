@echo off
setlocal EnableExtensions
set "PYTHONUTF8=1"
cd /d "%~dp0"

set "LAUNCH_MODE=marimo"
echo %~n0 | findstr /i "Notebook" >nul && set "LAUNCH_MODE=notebook"
set "LAB_FILE="
if /i "%LAUNCH_MODE%"=="marimo" (
    for /f "delims=" %%F in ('findstr /m /c:"import marimo" "*.py" 2^>nul') do if not defined LAB_FILE set "LAB_FILE=%%F"
) else (
    for %%F in (*.ipynb) do if not defined LAB_FILE set "LAB_FILE=%%F"
)
if not defined LAB_FILE goto :missing_lab
if defined EE66_TEST_ONLY (
    echo Launcher check passed: %LAUNCH_MODE% - %LAB_FILE%
    exit /b 0
)

if /i "%LAUNCH_MODE%"=="marimo" (set "LAUNCH_MODULE=marimo") else (set "LAUNCH_MODULE=notebook")
set "PYTHON_EXE="
set "PYTHON_ARGS="
for %%P in (
    "%EE66_PYTHON%"
    "%VIRTUAL_ENV%\Scripts\python.exe"
    "%CONDA_PREFIX%\python.exe"
    "%CD%\.venv\Scripts\python.exe"
    "%CD%\venv\Scripts\python.exe"
    "%CD%\..\.venv\Scripts\python.exe"
    "%CD%\..\venv\Scripts\python.exe"
    "%CD%\..\..\.venv\Scripts\python.exe"
    "%CD%\..\..\venv\Scripts\python.exe"
    "%CD%\..\..\..\.venv\Scripts\python.exe"
    "%UserProfile%\.ee66\venv\Scripts\python.exe"
    "%LocalAppData%\Programs\Python\Python313\python.exe"
    "%LocalAppData%\Programs\Python\Python312\python.exe"
    "%LocalAppData%\Programs\Python\Python311\python.exe"
    "%LocalAppData%\Programs\Python\Python310\python.exe"
    "%UserProfile%\anaconda3\python.exe"
    "%UserProfile%\miniconda3\python.exe"
    "%ProgramData%\Miniconda3\python.exe"
) do (
    if not defined PYTHON_EXE if exist "%%~P" (
        "%%~P" -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)" >nul 2>&1
        if not errorlevel 1 set "PYTHON_EXE=%%~P"
    )
)
if not defined PYTHON_EXE (
    where py >nul 2>&1
    if not errorlevel 1 (
        for %%V in (3.13 3.12 3.11 3.10) do (
            if not defined PYTHON_EXE (
                py -%%V -c "import sys" >nul 2>&1
                if not errorlevel 1 (
                    set "PYTHON_EXE=py"
                    set "PYTHON_ARGS=-%%V"
                )
            )
        )
    )
)
if not defined PYTHON_EXE (
    where python >nul 2>&1
    if not errorlevel 1 (
        python -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)" >nul 2>&1
        if not errorlevel 1 set "PYTHON_EXE=python"
    )
)
if not defined PYTHON_EXE (
    where python3 >nul 2>&1
    if not errorlevel 1 (
        python3 -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)" >nul 2>&1
        if not errorlevel 1 set "PYTHON_EXE=python3"
    )
)
if not defined PYTHON_EXE goto :missing_python

set "REQUIREMENTS=%CD%\requirements.txt"
if not exist "%REQUIREMENTS%" set "REQUIREMENTS=%CD%\..\requirements.txt"
if not exist "%REQUIREMENTS%" set "REQUIREMENTS=%CD%\..\..\requirements.txt"
if not exist "%REQUIREMENTS%" set "REQUIREMENTS=%CD%\..\..\..\requirements.txt"
if not exist "%REQUIREMENTS%" goto :missing_requirements

if defined EE66_SKIP_INSTALL goto :verify_module
"%PYTHON_EXE%" %PYTHON_ARGS% -m pip install --disable-pip-version-check --dry-run --no-index -r "%REQUIREMENTS%" >nul 2>&1
if not errorlevel 1 goto :verify_module
echo Installing missing lab packages into:
echo   %PYTHON_EXE% %PYTHON_ARGS%
"%PYTHON_EXE%" %PYTHON_ARGS% -m pip install --disable-pip-version-check -r "%REQUIREMENTS%"
if errorlevel 1 goto :install_error

:verify_module
"%PYTHON_EXE%" %PYTHON_ARGS% -c "import %LAUNCH_MODULE%" >nul 2>&1
if not errorlevel 1 goto :launch
if defined EE66_SKIP_INSTALL goto :missing_module
echo Installing the %LAUNCH_MODULE% launcher package...
"%PYTHON_EXE%" %PYTHON_ARGS% -m pip install --disable-pip-version-check "%LAUNCH_MODULE%"
if errorlevel 1 goto :install_error

:launch
if defined EE66_SKIP_LAUNCH (
    echo Launcher environment check passed: %LAUNCH_MODE% - %LAB_FILE%
    echo Python: %PYTHON_EXE% %PYTHON_ARGS%
    exit /b 0
)
echo Starting %LAB_FILE% with %PYTHON_EXE% %PYTHON_ARGS%...
if /i "%LAUNCH_MODE%"=="marimo" (
    "%PYTHON_EXE%" %PYTHON_ARGS% -m marimo edit "%LAB_FILE%"
) else (
    "%PYTHON_EXE%" %PYTHON_ARGS% -m jupyter notebook "%LAB_FILE%"
)
if errorlevel 1 goto :launch_error
exit /b 0

:missing_lab
echo ERROR: No %LAUNCH_MODE% lab file was found beside this launcher.
goto :fail
:missing_python
echo ERROR: No working Python 3.10 or newer was found.
echo Existing local virtual environments, active environments, Conda, py, and PATH were checked.
goto :fail
:missing_requirements
echo ERROR: requirements.txt was not found in the lab package.
goto :fail
:install_error
echo ERROR: Dependency verification or installation failed for the selected Python above.
goto :fail
:missing_module
echo ERROR: %LAUNCH_MODULE% is unavailable in the selected Python.
goto :fail
:launch_error
echo ERROR: The lab server exited with an error.
:fail
pause
exit /b 1
