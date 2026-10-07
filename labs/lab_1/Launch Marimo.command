#!/bin/bash
set -u
SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
cd "$SCRIPT_DIR" || exit 1
export PYTHONUTF8=1
case "$(basename "$0")" in *Notebook*) MODE=notebook;; *) MODE=marimo;; esac

LAB_FILE=""
if [ "$MODE" = marimo ]; then
  for f in ./*.py; do [ -f "$f" ] && grep -q "import marimo" "$f" && LAB_FILE="${f#./}" && break; done
  MODULE=marimo
else
  for f in ./*.ipynb; do [ -f "$f" ] && LAB_FILE="${f#./}" && break; done
  MODULE=notebook
fi
[ -n "$LAB_FILE" ] || { echo "ERROR: No $MODE lab file was found beside this launcher."; read -r -p "Press Return to close..." _; exit 1; }
[ "${EE66_TEST_ONLY:-}" = 1 ] && { echo "Launcher check passed: $MODE - $LAB_FILE"; exit 0; }

PYTHON=""
python_ok() { "$1" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3,10) else 1)' >/dev/null 2>&1; }
for candidate in "${EE66_PYTHON:-}" "${VIRTUAL_ENV:-}/bin/python" "${CONDA_PREFIX:-}/bin/python" "$SCRIPT_DIR/.venv/bin/python" "$SCRIPT_DIR/venv/bin/python" "$SCRIPT_DIR/../.venv/bin/python" "$SCRIPT_DIR/../../.venv/bin/python" "$SCRIPT_DIR/../../../.venv/bin/python" "$HOME/.ee66/venv/bin/python" python3.13 python3.12 python3.11 python3.10 /opt/homebrew/bin/python3 /usr/local/bin/python3 python3 python; do
  [ -n "$candidate" ] || continue
  resolved="$(command -v "$candidate" 2>/dev/null || true)"
  [ -n "$resolved" ] && python_ok "$resolved" && PYTHON="$resolved" && break
done
[ -n "$PYTHON" ] || { echo "ERROR: No working Python 3.10 or newer was found."; read -r -p "Press Return to close..." _; exit 1; }

REQ="$SCRIPT_DIR/requirements.txt"
[ -f "$REQ" ] || REQ="$SCRIPT_DIR/../requirements.txt"
[ -f "$REQ" ] || REQ="$SCRIPT_DIR/../../requirements.txt"
[ -f "$REQ" ] || REQ="$SCRIPT_DIR/../../../requirements.txt"
[ -f "$REQ" ] || { echo "ERROR: requirements.txt was not found."; exit 1; }

if [ "${EE66_SKIP_INSTALL:-}" != 1 ]; then
  if ! "$PYTHON" -m pip install --disable-pip-version-check --dry-run --no-index -r "$REQ" >/dev/null 2>&1; then
    echo "Installing missing lab packages into $PYTHON..."
    "$PYTHON" -m pip install --disable-pip-version-check -r "$REQ" || exit 1
  fi
  "$PYTHON" -c "import $MODULE" >/dev/null 2>&1 || "$PYTHON" -m pip install --disable-pip-version-check "$MODULE" || exit 1
fi
"$PYTHON" -c "import $MODULE" >/dev/null 2>&1 || { echo "ERROR: $MODULE is unavailable in $PYTHON"; exit 1; }
[ "${EE66_SKIP_LAUNCH:-}" = 1 ] && { echo "Launcher environment check passed: $MODE - $LAB_FILE"; echo "Python: $PYTHON"; exit 0; }
echo "Starting $LAB_FILE with $PYTHON..."
if [ "$MODE" = marimo ]; then "$PYTHON" -m marimo edit "$LAB_FILE"; else "$PYTHON" -m jupyter notebook "$LAB_FILE"; fi
