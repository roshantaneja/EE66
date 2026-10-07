#!/bin/bash
# macOS launcher for the EE 66 Python Bootcamp marimo notebook.
#
# Double-click this file in Finder, or run it from Terminal. If the lab environment
# is not set up yet, this script sets it up automatically (one time, ~1 minute) and
# then opens the notebook.
#
# Environment overrides, for staff/debugging:
#   EE66_PYTHON=/path/to/python   use this interpreter, skip all discovery
#   EE66_HOME=/path/to/env        put the course environment somewhere else
#   EE66_REBUILD=1                delete and rebuild the course environment

export PYTHONUTF8=1

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR" || exit 1

NOTEBOOK="ee66_python_bootcamp.py"
REQUIREMENTS="requirements.txt"
EE66_HOME="${EE66_HOME:-$HOME/.ee66}"
VENV="$EE66_HOME/venv"
VENV_PY="$VENV/bin/python"
MODULE="marimo"
# Every top-level package the notebook and autograder import. An interpreter is only
# usable if it has all of them -- a stray Anaconda with marimo but no ipywidgets would
# otherwise fail halfway through the lab.
LAB_IMPORTS="marimo, numpy, scipy, ipywidgets, IPython"

pause_and_exit() {
    echo
    read -r -p "Press Return to close this window..."
    exit "$1"
}

# Does this interpreter exist and have everything the lab needs?
has_module() {
    [ -n "$1" ] && [ -x "$1" ] && "$1" -c "import $LAB_IMPORTS" >/dev/null 2>&1
}

# Python versions this lab supports.
#   Floor   3.12 -- the notebook's own requires-python.
#   Ceiling 3.13 -- numpy 2.2.3 and scipy 1.15.1 publish wheels only up to cp313.
#                   On 3.14+ pip tries to compile them from source and fails.
# If you re-pin numpy/scipy in requirements.txt, update PY_MAX to match.
PY_MIN_MINOR=12
PY_MAX_MINOR=13

# Prints "3.13" for a working interpreter, nothing for one that will not run.
python_version() {
    [ -n "$1" ] && [ -x "$1" ] || return 1
    "$1" -c 'import sys; print("%d.%d" % sys.version_info[:2])' 2>/dev/null
}

# Is this interpreter inside the supported range?
is_supported_python() {
    [ -n "$1" ] && [ -x "$1" ] || return 1
    "$1" -c "import sys
major, minor = sys.version_info[:2]
sys.exit(0 if major == 3 and $PY_MIN_MINOR <= minor <= $PY_MAX_MINOR else 1)" >/dev/null 2>&1
}

# Look for an interpreter in the supported range, newest first. Versioned names come
# before bare "python3" on purpose: Homebrew's python3 is already 3.14, while a usable
# python3.13 often sits right beside it.
find_bootstrap_python() {
    BOOTSTRAP_PY=""
    WRONG_PY=""
    WRONG_VER=""
    ANY_PYTHON=""

    CANDIDATES="
$(command -v python3.13 2>/dev/null)
$(command -v python3.12 2>/dev/null)
/opt/homebrew/bin/python3.13
/opt/homebrew/bin/python3.12
/usr/local/bin/python3.13
/usr/local/bin/python3.12
$(command -v python3 2>/dev/null)
$(command -v python 2>/dev/null)
$HOME/miniconda3/bin/python
$HOME/anaconda3/bin/python
/opt/miniconda3/bin/python
/opt/anaconda3/bin/python
/opt/homebrew/Caskroom/miniconda/base/bin/python
/opt/homebrew/anaconda3/bin/python
/opt/homebrew/bin/python3
/usr/local/bin/python3
/usr/bin/python3
"

    OLD_IFS="$IFS"
    IFS='
'
    for CANDIDATE in $CANDIDATES; do
        [ -n "$CANDIDATE" ] || continue
        [ -x "$CANDIDATE" ] || continue
        VER="$(python_version "$CANDIDATE")"
        [ -n "$VER" ] || continue
        ANY_PYTHON="yes"
        if is_supported_python "$CANDIDATE"; then
            if [ -z "$BOOTSTRAP_PY" ]; then BOOTSTRAP_PY="$CANDIDATE"; fi
        elif [ -z "$WRONG_PY" ]; then
            WRONG_PY="$CANDIDATE"
            WRONG_VER="$VER"
        fi
    done
    IFS="$OLD_IFS"
}

# Say precisely what is wrong: no Python at all, too old, or too new.
report_no_python() {
    if [ -z "$ANY_PYTHON" ]; then
        echo "No Python installation was found."
        return
    fi

    WRONG_MINOR="${WRONG_VER#3.}"
    echo "Found Python $WRONG_VER at:"
    echo "  $WRONG_PY"
    echo
    if [ -n "$WRONG_MINOR" ] && [ "$WRONG_MINOR" -gt "$PY_MAX_MINOR" ] 2>/dev/null; then
        echo "That version is too new for this lab. NumPy and SciPy are pinned to the"
        echo "versions the course uses, and those do not publish builds for Python"
        echo "$WRONG_VER yet -- installing them would try to compile from source and fail."
        echo "The lab needs Python 3.$PY_MIN_MINOR or 3.$PY_MAX_MINOR."
    else
        echo "That version is too old for this lab, which needs Python 3.$PY_MIN_MINOR"
        echo "or 3.$PY_MAX_MINOR."
    fi
    echo
    echo "You can keep the Python you already have -- installing another version"
    echo "alongside it will not disturb it."
}

# If Homebrew is present, offer to install a supported Python. Installing software
# changes the student's machine, so this always asks first.
offer_homebrew_install() {
    command -v brew >/dev/null 2>&1 || return 0
    [ -t 0 ] || return 0

    echo
    printf "Homebrew is installed. Install Python 3.%s now with Homebrew? [y/N] " "$PY_MAX_MINOR"
    read -r REPLY
    case "$REPLY" in
        [Yy]*) ;;
        *) return 0 ;;
    esac

    echo
    echo "Running: brew install python@3.$PY_MAX_MINOR"
    if ! brew install "python@3.$PY_MAX_MINOR"; then
        echo
        echo "Homebrew could not install Python 3.$PY_MAX_MINOR."
        return 0
    fi

    echo
    find_bootstrap_python
    if [ -n "$BOOTSTRAP_PY" ]; then
        echo "Installed Python $(python_version "$BOOTSTRAP_PY")."
    else
        echo "Homebrew finished but a supported Python still is not on the PATH."
    fi
}

if [ "$EE66_REBUILD" = "1" ] && [ -d "$VENV" ]; then
    echo "Rebuilding the EE 66 environment..."
    rm -rf "$VENV"
fi

# ---------------------------------------------------------------------------
# 1. Fast path: find an interpreter that can already run the notebook.
# ---------------------------------------------------------------------------
PYTHON_EXE=""

if [ -n "$EE66_PYTHON" ]; then
    if has_module "$EE66_PYTHON"; then
        PYTHON_EXE="$EE66_PYTHON"
    else
        echo "ERROR: EE66_PYTHON is set to '$EE66_PYTHON', which is missing one of: $LAB_IMPORTS"
        pause_and_exit 1
    fi
fi

if [ -z "$PYTHON_EXE" ]; then
    for P in \
        "$VENV_PY" \
        "$DIR/../../.venv/bin/python" \
        "$HOME/miniconda3/bin/python" \
        "$HOME/anaconda3/bin/python" \
        "/opt/miniconda3/bin/python" \
        "/opt/anaconda3/bin/python" \
        "/opt/homebrew/Caskroom/miniconda/base/bin/python" \
        "/opt/homebrew/anaconda3/bin/python"
    do
        if [ -z "$PYTHON_EXE" ] && has_module "$P"; then
            PYTHON_EXE="$P"
        fi
    done
fi

if [ -z "$PYTHON_EXE" ]; then
    for CMD in python3 python; do
        if [ -z "$PYTHON_EXE" ] && command -v "$CMD" >/dev/null 2>&1; then
            RESOLVED="$(command -v "$CMD")"
            if has_module "$RESOLVED"; then
                PYTHON_EXE="$RESOLVED"
            fi
        fi
    done
fi

# ---------------------------------------------------------------------------
# 2. Nothing usable found: build the course environment automatically.
# ---------------------------------------------------------------------------
if [ -z "$PYTHON_EXE" ]; then
    find_bootstrap_python

    if [ -z "$BOOTSTRAP_PY" ]; then
        echo "The lab environment is not set up yet, and it cannot be set up"
        echo "automatically on this Mac."
        echo
        report_no_python
        offer_homebrew_install
        if [ -z "$BOOTSTRAP_PY" ]; then
            echo
            echo "Install Python 3.$PY_MAX_MINOR from:"
            echo "  https://www.python.org/downloads/macos/"
            echo "then double-click this launcher again."
            pause_and_exit 1
        fi
    fi

    echo "First-time setup for EE 66 Lab 0."
    echo "Installing the lab's Python packages. This takes about a minute and only"
    echo "happens once -- later labs will reuse this environment."
    echo
    echo "Using Python $(python_version "$BOOTSTRAP_PY") at $BOOTSTRAP_PY"
    mkdir -p "$EE66_HOME" || { echo "ERROR: Could not create $EE66_HOME."; pause_and_exit 1; }

    # A full disk otherwise shows up as a cryptic archive-extraction error.
    FREE_MB="$("$BOOTSTRAP_PY" -c "import shutil; print(shutil.disk_usage('$HOME').free // (1024*1024))" 2>/dev/null)"
    if [ -n "$FREE_MB" ] && [ "$FREE_MB" -lt 1200 ] 2>/dev/null; then
        echo "ERROR: Not enough free disk space to install the lab packages."
        echo "       Free space: ${FREE_MB} MB. The lab environment needs about 700 MB,"
        echo "       and roughly 1200 MB free to unpack safely."
        echo
        echo "Free up some space and run this launcher again. Two caches that are safe"
        echo "to delete and will rebuild themselves:"
        echo "  rm -rf ~/Library/Caches/pip"
        echo "  rm -rf ~/.cache/uv"
        echo
        echo "Then empty the Trash, and check Apple menu > System Settings > General >"
        echo "Storage for anything larger."
        pause_and_exit 1
    fi


    if [ -x "$VENV_PY" ]; then
        echo "Reusing the course environment in $VENV"
    else
        echo "Creating the course environment in $VENV"
        rm -rf "$VENV"
        if ! "$BOOTSTRAP_PY" -m venv "$VENV"; then
            echo
            echo "ERROR: Could not create the virtual environment at $VENV."
            pause_and_exit 1
        fi
    fi

    if [ ! -f "$REQUIREMENTS" ]; then
        echo "ERROR: $REQUIREMENTS is missing from $DIR."
        echo "Make sure you unzipped the entire lab folder, not just the notebook."
        pause_and_exit 1
    fi

    echo "Installing packages from $REQUIREMENTS:"
    sed -e 's/#.*//' -e '/^[[:space:]]*$/d' "$REQUIREMENTS" | sed 's/^/  - /'
    echo
    "$VENV_PY" -m pip install --quiet --upgrade pip >/dev/null 2>&1
    if ! "$VENV_PY" -m pip install -r "$REQUIREMENTS"; then
        echo
        echo "ERROR: Installing the lab packages failed."
        echo "The most common cause is no internet connection -- check your network"
        echo "and double-click this launcher again."
        echo "If it keeps failing, post on Ed with everything printed above."
        pause_and_exit 1
    fi

    if ! has_module "$VENV_PY"; then
        echo
        echo "ERROR: Setup finished but the lab packages still will not import."
        echo "Post on Ed with everything printed above and we'll help."
        pause_and_exit 1
    fi

    PYTHON_EXE="$VENV_PY"
    echo
    echo "Setup complete."
    echo
fi

# ---------------------------------------------------------------------------
# 3. Launch.
# ---------------------------------------------------------------------------
echo "Opening $NOTEBOOK ..."
echo "Leave this window open while you work. Close it (or press Control-C) when done."
echo

# --no-sandbox matters: the notebook carries a PEP 723 dependency header, and when uv
# is installed marimo offers to build a second, throwaway venv from it -- defaulting to
# yes. That ignores the environment we just built, re-downloads several hundred MB, and
# needs the network again. We have the packages already, so decline it up front.
"$PYTHON_EXE" -m marimo edit --no-sandbox "$NOTEBOOK"
STATUS=$?
if [ $STATUS -ne 0 ]; then
    echo
    echo "ERROR: marimo exited with an error (code $STATUS)."
fi
pause_and_exit $STATUS
