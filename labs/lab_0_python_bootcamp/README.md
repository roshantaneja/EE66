# EE 66 Lab 0: Python Bootcamp

## Opening the lab

**macOS:** double-click **`Launch Marimo.command`**
**Windows:** double-click **`Launch Marimo.bat`**

That's the whole setup. The first time you run it, the launcher installs the lab's
Python packages for you — it takes about a minute and prints what it is doing. Every
launch after that opens the notebook immediately, and later EE 66 labs reuse the same
environment.

You do **not** need to install anything by hand, create a virtual environment, or
touch conda.

### First launch on macOS

Because the lab arrives as a downloaded zip, macOS may refuse to run the launcher the
first time, saying it "cannot be opened because it is from an unidentified developer."
To allow it:

* **Control-click** (or right-click) `Launch Marimo.command` → **Open** → **Open**.
* If that doesn't offer an **Open** button, go to
  **System Settings → Privacy & Security**, find the message about the blocked file,
  and click **Open Anyway**.

You only have to do this once per download.

If double-clicking opens the file in TextEdit instead of running it, the executable
bit was lost when the folder was unzipped. Fix it once in Terminal:

```bash
cd /path/to/lab_0_python_bootcamp
chmod +x "Launch Marimo.command"
```

## What the launcher does

1. Looks for a Python that can already run the lab — the shared course environment,
   a course virtual environment two directories up, a Miniconda/Anaconda install, or
   `python3` on your `PATH`. It checks for *every* package the lab needs, not just
   marimo, so a half-configured Anaconda doesn't fail you partway through the lab.
2. If it doesn't find one, it looks for a Python it can build with, reports exactly
   what it found if none works (nothing installed / too old / too new), and offers to
   install a supported version via Homebrew or winget if either is available.
3. It checks there's enough free disk space, then creates the shared course
   environment at `~/.ee66/venv`
   (`%UserProfile%\.ee66\venv` on Windows) and installs `requirements.txt` into it.
   This needs an internet connection.
4. Opens the notebook.

Because the environment lives in your home folder rather than in the lab folder, it
survives re-downloading the lab and is shared with future labs.

## Running it yourself

If you'd rather not use the launcher:

```bash
python3 -m pip install -r requirements.txt
python3 -m marimo edit ee66_python_bootcamp.py
```

## Jupyter backup

If marimo doesn't work on your machine, `jupyter-backup/` has the same lab as a
classic Jupyter notebook, with launchers that set themselves up the same way:

* macOS: `jupyter-backup/Launch Notebook.command`
* Windows: `jupyter-backup/Launch Notebook.bat`

## Troubleshooting

**"Too old" / "too new" Python.** The lab needs **Python 3.12 or 3.13**. The ceiling is
real: `numpy==2.2.3` and `scipy==1.15.1` publish wheels only up to cp313, so on Python
3.14+ pip tries to compile them from source and fails. Install 3.13 from
[python.org](https://www.python.org/downloads/) — on Windows, tick *Add python.exe to
PATH* — then run the launcher again. Installing 3.13 alongside a newer Python is fine;
the launcher prefers versioned names like `python3.13` over a bare `python3`.

If Homebrew (macOS) or winget (Windows) is installed, the launcher offers to install a
supported Python for you. It always asks first.

**"Installing the lab packages failed."** Almost always no internet connection.
Reconnect and run the launcher again; it picks up where it left off.

**"Not enough free disk space."** The environment needs about 700 MB, and the launcher
asks for 1200 MB free so unpacking doesn't fail halfway. Two caches are safe to delete
and rebuild themselves: `~/Library/Caches/pip` and `~/.cache/uv`
(`%LocalAppData%\pip\Cache` and `%LocalAppData%\uv\cache` on Windows).

**Something is wedged.** Rebuild the environment from scratch:

```bash
# macOS
EE66_REBUILD=1 "./Launch Marimo.command"

# Windows (Command Prompt, from the lab folder)
set EE66_REBUILD=1
"Launch Marimo.bat"
```

Or just delete `~/.ee66` (`%UserProfile%\.ee66`) and launch again.

### Staff overrides

| Variable | Effect |
| --- | --- |
| `EE66_PYTHON` | Use this interpreter, skip all discovery |
| `EE66_HOME` | Put the course environment somewhere other than `~/.ee66` |
| `EE66_REBUILD=1` | Delete and rebuild the course environment |

## Files

| File | Purpose |
| --- | --- |
| `ee66_python_bootcamp.py` | The lab notebook (marimo) |
| `autograder.py` | Autograder used by the notebook's `Test Q#` buttons |
| `requirements.txt` | Lab dependencies, installed by the launchers |
| — | *If you re-pin numpy/scipy there, update `PY_MAX_MINOR` in all four launchers.* |
| `Launch Marimo.command` / `.bat` | macOS / Windows launchers |
| `.marimo.toml` | Disables marimo's AI features |
| `jupyter-backup/` | Same lab as a classic Jupyter notebook |

## Why `--no-sandbox`

The marimo launchers pass `--no-sandbox`. The notebook carries a PEP 723 dependency
header, and when `uv` is installed marimo offers to build a *second*, throwaway venv
from it — with the prompt defaulting to **yes**. Accepting that ignores the environment
the launcher just built, re-downloads several hundred MB, and needs the network again.
Don't remove the flag.

## A note on AI

AI use is not permitted in EE 66 labs. `.marimo.toml` disables marimo's built-in AI
assistant and Copilot integration.
