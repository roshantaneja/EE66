@echo off
REM Windows launcher for the EE 66 Python Bootcamp Jupyter notebook.
REM
REM Double-click this file. If the lab environment is not set up yet, this script
REM sets it up automatically (one time, about a minute) and then opens the notebook.
REM
REM Overrides, for staff/debugging -- set these before running:
REM   EE66_PYTHON=C:\path\to\python.exe   use this interpreter, skip all discovery
REM   EE66_HOME=C:\path\to\env            put the course environment somewhere else
REM   EE66_REBUILD=1                      delete and rebuild the course environment

setlocal enabledelayedexpansion
set "PYTHONUTF8=1"
cd /d "%~dp0"

set "NOTEBOOK=ee66_python_bootcamp.ipynb"
set "REQUIREMENTS=requirements.txt"
REM Python versions this lab supports.
REM   Floor   3.12 -- the notebook's own requires-python.
REM   Ceiling 3.13 -- numpy 2.2.3 and scipy 1.15.1 publish wheels only up to cp313.
REM                   On 3.14+ pip tries to compile them from source and fails.
REM If you re-pin numpy/scipy in requirements.txt, update PY_MAX_MINOR to match.
set "PY_MIN_MINOR=12"
set "PY_MAX_MINOR=13"
if not defined EE66_HOME set "EE66_HOME=%UserProfile%\.ee66"
set "VENV=%EE66_HOME%\venv"
set "VENV_PY=%VENV%\Scripts\python.exe"

if "%EE66_REBUILD%"=="1" if exist "%VENV%" (
    echo Rebuilding the EE 66 environment...
    rmdir /s /q "%VENV%"
)

REM ===================================================================
REM 1. Fast path: find an interpreter that can already run the notebook.
REM ===================================================================
set "PYTHON_EXE="

if defined EE66_PYTHON (
    call :check_imports "%EE66_PYTHON%"
    if errorlevel 1 (
        echo ERROR: EE66_PYTHON is set to "%EE66_PYTHON%", which is missing at least
        echo        one of the packages this lab needs.
        goto :fail
    )
    set "PYTHON_EXE=%EE66_PYTHON%"
    goto :launch
)

for %%P in (
    "%VENV_PY%"
    "%~dp0..\..\.venv\Scripts\python.exe"
    "%ProgramData%\Miniconda3\python.exe"
    "%ProgramData%\Anaconda3\python.exe"
    "%LocalAppData%\miniconda3\python.exe"
    "%UserProfile%\miniconda3\python.exe"
    "%UserProfile%\anaconda3\python.exe"
) do (
    if not defined PYTHON_EXE if exist "%%~P" (
        call :check_imports "%%~P"
        if not errorlevel 1 set "PYTHON_EXE=%%~P"
    )
)

if not defined PYTHON_EXE (
    where python >nul 2>&1
    if not errorlevel 1 (
        call :check_imports "python"
        if not errorlevel 1 set "PYTHON_EXE=python"
    )
)

if defined PYTHON_EXE goto :launch

REM ===================================================================
REM 2. Nothing usable found: build the course environment automatically.
REM ===================================================================
call :find_bootstrap_python

if not defined BOOTSTRAP_PY (
    echo The lab environment is not set up yet, and it cannot be set up
    echo automatically on this PC.
    echo.
    call :report_no_python
    call :offer_winget_install
)

if not defined BOOTSTRAP_PY (
    echo.
    echo Install Python 3.%PY_MAX_MINOR% from:
    echo   https://www.python.org/downloads/windows/
    echo Tick "Add python.exe to PATH" in the installer, then double-click
    echo this launcher again.
    goto :fail
)

echo First-time setup for EE 66 Lab 0.
echo Installing the lab's Python packages. This takes about a minute and only
echo happens once -- later labs will reuse this environment.
echo.
call :print_version "%BOOTSTRAP_PY%" %BOOTSTRAP_ARGS%
if not exist "%EE66_HOME%" mkdir "%EE66_HOME%"

REM A full disk otherwise shows up as a cryptic archive-extraction error.
call :check_free_space "%BOOTSTRAP_PY%" %BOOTSTRAP_ARGS%
if errorlevel 1 (
    echo ERROR: Not enough free disk space to install the lab packages.
    echo        Free space: %FREE_MB% MB. The lab environment needs about 700 MB,
    echo        and roughly 1200 MB free to unpack safely.
    echo.
    echo Free up some space and run this launcher again, then empty the Recycle Bin.
    echo Windows Settings ^> System ^> Storage shows what is using the most room.
    goto :fail
)


if exist "%VENV_PY%" (
    echo Reusing the course environment in %VENV%
) else (
    echo Creating the course environment in %VENV%
    if exist "%VENV%" rmdir /s /q "%VENV%"
    "%BOOTSTRAP_PY%" %BOOTSTRAP_ARGS% -m venv "%VENV%"
    if errorlevel 1 (
        echo.
        echo ERROR: Could not create the virtual environment at %VENV%.
        goto :fail
    )
)

if not exist "%VENV_PY%" (
    echo.
    echo ERROR: The environment was created but %VENV_PY% is missing.
    goto :fail
)

if not exist "%REQUIREMENTS%" (
    echo ERROR: %REQUIREMENTS% is missing from this folder.
    echo Make sure you unzipped the entire lab folder, not just the notebook.
    goto :fail
)

echo Installing packages from %REQUIREMENTS% ...
echo.
"%VENV_PY%" -m pip install --quiet --upgrade pip >nul 2>&1
"%VENV_PY%" -m pip install -r "%REQUIREMENTS%"
if errorlevel 1 (
    echo.
    echo ERROR: Installing the lab packages failed.
    echo The most common cause is no internet connection -- check your network
    echo and double-click this launcher again.
    echo If it keeps failing, post on Ed with everything printed above.
    goto :fail
)

call :check_imports "%VENV_PY%"
if errorlevel 1 (
    echo.
    echo ERROR: Setup finished but the lab packages still will not import.
    echo Post on Ed with everything printed above and we'll help.
    goto :fail
)

set "PYTHON_EXE=%VENV_PY%"
echo.
echo Setup complete.
echo.

REM ===================================================================
REM 3. Launch.
REM ===================================================================
:launch
echo Opening %NOTEBOOK% ...
echo Leave this window open while you work. Close it when you are done.
echo.
"%PYTHON_EXE%" -m jupyter notebook "%NOTEBOOK%"
if errorlevel 1 (
    echo.
    echo ERROR: Jupyter Notebook exited with an error.
)
echo.
pause
exit /b 0

:fail
echo.
pause
exit /b 1

REM ===================================================================
REM Helpers. These live outside every parenthesised block on purpose:
REM cmd.exe mis-parses the parentheses in a Python one-liner when the
REM command sits inside an if/for block.
REM ===================================================================

REM Does this interpreter have every package the lab needs? A stray Anaconda
REM with Jupyter but no ipywidgets would otherwise fail halfway through the lab.
:check_imports
"%~1" -c "import notebook, numpy, scipy, ipywidgets, IPython" >nul 2>&1
exit /b %errorlevel%

REM Is this interpreter inside the supported range?
:check_version
"%~1" -c "import sys; sys.exit(0 if sys.version_info[0] == 3 and %PY_MIN_MINOR% <= sys.version_info[1] <= %PY_MAX_MINOR% else 1)" >nul 2>&1
exit /b %errorlevel%

:check_version_py
py -3 -c "import sys; sys.exit(0 if sys.version_info[0] == 3 and %PY_MIN_MINOR% <= sys.version_info[1] <= %PY_MAX_MINOR% else 1)" >nul 2>&1
exit /b %errorlevel%

REM Record this interpreter's version in PY_VER, or clear it if it will not run.
:get_version
set "PY_VER="
for /f "tokens=1,2" %%A in ('%* -c "import sys; print(*sys.version_info[:2])" 2^>nul') do set "PY_VER=%%A.%%B"
exit /b 0

:check_free_space
set "FREE_MB="
for /f "delims=" %%F in ('%* -c "import shutil, os; print(shutil.disk_usage(os.path.expanduser(chr(126))).free // (1024*1024))" 2^>nul') do set "FREE_MB=%%F"
if not defined FREE_MB exit /b 0
if %FREE_MB% LSS 1200 exit /b 1
exit /b 0

:print_version
call :get_version %*
echo Using Python %PY_VER% at %~1
exit /b 0

REM Look for an interpreter in the supported range. Versioned launchers come first:
REM a machine's default python may already be 3.14 while a usable 3.13 sits beside it.
:find_bootstrap_python
set "BOOTSTRAP_PY="
set "BOOTSTRAP_ARGS="
set "WRONG_PY="
set "WRONG_VER="
set "ANY_PYTHON="

for %%P in (
    "%LocalAppData%\Programs\Python\Python313\python.exe"
    "%LocalAppData%\Programs\Python\Python312\python.exe"
    "%ProgramFiles%\Python313\python.exe"
    "%ProgramFiles%\Python312\python.exe"
    "%ProgramData%\Miniconda3\python.exe"
    "%ProgramData%\Anaconda3\python.exe"
    "%LocalAppData%\miniconda3\python.exe"
    "%UserProfile%\miniconda3\python.exe"
    "%UserProfile%\anaconda3\python.exe"
) do (
    if exist "%%~P" call :consider_python "%%~P"
)

where python >nul 2>&1
if not errorlevel 1 call :consider_python "python"

if not defined BOOTSTRAP_PY (
    where py >nul 2>&1
    if not errorlevel 1 call :consider_py
)
exit /b 0

REM The py.exe launcher, classified the same way as a plain interpreter.
:consider_py
call :get_version "py" -3
if not defined PY_VER exit /b 0
set "ANY_PYTHON=yes"
call :check_version_py
if not errorlevel 1 (
    set "BOOTSTRAP_PY=py"
    set "BOOTSTRAP_ARGS=-3"
    exit /b 0
)
if not defined WRONG_PY (
    set "WRONG_PY=py -3"
    set "WRONG_VER=%PY_VER%"
)
exit /b 0

REM Classify one interpreter: supported, or record it as the wrong version.
:consider_python
call :get_version "%~1"
if not defined PY_VER exit /b 0
set "ANY_PYTHON=yes"
call :check_version "%~1"
if not errorlevel 1 (
    if not defined BOOTSTRAP_PY set "BOOTSTRAP_PY=%~1"
    exit /b 0
)
if not defined WRONG_PY (
    set "WRONG_PY=%~1"
    set "WRONG_VER=%PY_VER%"
)
exit /b 0

REM Say precisely what is wrong: no Python at all, too old, or too new.
:report_no_python
if not defined ANY_PYTHON (
    echo No Python installation was found.
    exit /b 0
)
echo Found Python %WRONG_VER% at:
echo   %WRONG_PY%
echo.
for /f "tokens=2 delims=." %%M in ("%WRONG_VER%") do set "WRONG_MINOR=%%M"
set "TOO_NEW="
if defined WRONG_MINOR if %WRONG_MINOR% GTR %PY_MAX_MINOR% set "TOO_NEW=yes"
if defined TOO_NEW (
    echo That version is too new for this lab. NumPy and SciPy are pinned to the
    echo versions the course uses, and those do not publish builds for Python
    echo %WRONG_VER% yet -- installing them would try to compile from source and fail.
    echo The lab needs Python 3.%PY_MIN_MINOR% or 3.%PY_MAX_MINOR%.
) else (
    echo That version is too old for this lab, which needs Python 3.%PY_MIN_MINOR%
    echo or 3.%PY_MAX_MINOR%.
)
echo.
echo You can keep the Python you already have -- installing another version
echo alongside it will not disturb it.
exit /b 0

REM If winget is present, offer to install a supported Python. Installing software
REM changes the student's machine, so this always asks first.
:offer_winget_install
where winget >nul 2>&1
if errorlevel 1 exit /b 0
echo.
set "REPLY="
set /p "REPLY=winget is available. Install Python 3.%PY_MAX_MINOR% now with winget? [y/N] "
if /i not "%REPLY%"=="y" if /i not "%REPLY%"=="yes" exit /b 0
echo.
echo Running: winget install -e --id Python.Python.3.%PY_MAX_MINOR%
winget install -e --id Python.Python.3.%PY_MAX_MINOR% --accept-package-agreements --accept-source-agreements
if errorlevel 1 (
    echo.
    echo winget could not install Python 3.%PY_MAX_MINOR%.
    exit /b 0
)
echo.
call :find_bootstrap_python
if defined BOOTSTRAP_PY (
    call :get_version "%BOOTSTRAP_PY%"
    echo Installed Python %PY_VER%.
) else (
    echo winget finished, but a supported Python is still not visible.
    echo Close this window, open the launcher again, and it should be found.
)
exit /b 0
