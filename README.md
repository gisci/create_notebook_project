# Minimal Viable Notebook Project 

This project is discussed in more detail in the Flocode Newsletter - [#081 | Reducing Friction: The Minimal Notebook Project Tool](https://flocode.substack.com/p/081-reducing-friction-the-minimal)

A small, clonable utility for creating engineering notebook projects quickly. It:
- scaffolds a simple Jupyter-friendly project using Cookiecutter (data/, src/, README, blank notebook)
- initializes a local Python environment with uv and installs ipykernel
- updates pyproject.toml with the chosen project name, description, and author (default: "James O'Reilly")

Everything is self-contained in this repo, including Cookiecutter templates.

## Dev Folder Structure
This tool creates and organizes your development projects in a structured way:
- **Personal projects**: Created in `%USERPROFILE%\dev` (e.g., `C:\Users\YourName\dev`)
- **Work projects**: Created in `%USERPROFILE%\dev\work-dev` (e.g., `C:\Users\YourName\dev\work-dev`)

These folders are automatically created if they don't exist when you run the tool. This keeps your personal and work projects organized in separate directories under your user profile.

## Clonable design
- Templates live inside this repo at `cookiecutter-project-templates` and are created automatically on first use.
- The Windows launcher `new_notebook_project.bat` sits next to the Python script and finds it via a relative path, so you can clone this repo anywhere.
- By default, new projects are created under:
  - Personal: `%USERPROFILE%\dev`
  - Work: `%USERPROFILE%\dev\work-dev`
  The launcher creates these folders if they don't exist.

## Prerequisites (Windows)
- Python 3.10+ with the `py` launcher (recommended from python.org)
- uv (Python environment and package manager)
- cookiecutter (Python package)

Install suggestions:
- cookiecutter (user install):
  ```powershell
  py -3 -m pip install --user cookiecutter
  ```
- uv (choose one):
  - Official installer:
    ```powershell
    iwr https://astral.sh/uv/install.ps1 -UseBasicParsing | iex
    ```
  - Or via pip (works, but installer is preferred):
    ```powershell
    py -3 -m pip install --user uv
    ```

## How to use
You can use either the batch launcher or the Python CLI.

### Option A: Windows launcher (recommended)
- Run (double-click or from a terminal):
  `new_notebook_project.bat`
- Choose:
  - 1) Personal Project  -> `%USERPROFILE%\dev`
  - 2) Work Project      -> `%USERPROFILE%\dev\work-dev`
- Enter Project Name and Description when prompted.

The tool will:
1) Scaffold the project under the chosen output folder
2) Run `uv init` in that project and install `ipykernel`
3) Update `pyproject.toml` with name, description, and authors = [{ name = "James O'Reilly" }]

### Option B: Python CLI (if you prefer the terminal)
From this repo directory:
```powershell
py -3 .\create_notebook_project.py -n "MyProject" -d "Short description" -o "$env:USERPROFILE\dev"
```
Flags:
- `-n/--name` Project name (required if not prompted)
- `-d/--description` Project description
- `-a/--author` Author (default: James O'Reilly)
- `-o/--output-dir` Where to create the new project. If omitted, defaults to the nearest `dev` folder (or `%USERPROFILE%\dev`).

## Where the environment lives
- `uv init` runs inside the project directory, so the virtual environment is created in the project (commonly `.venv`).
- `ipykernel` is installed into that environment so your notebooks can use the project interpreter.

Tip: In VS Code, use "Python: Select Interpreter" and choose the interpreter from your project's `.venv`.

## Cookiecutter templates location
- Templates are stored under: `<repo>\cookiecutter-project-templates`.
- The folder is created and maintained by the script; you do not need a separate templates directory in `dev`.

## Troubleshooting
- "Access is denied" when selecting menu options in the batch file: ensure you are using the provided launcher (it escapes `>` correctly). Running it from any directory is fine.
- `py` not found: ensure Python from python.org is installed, or replace `py -3` with `python` in commands.
- `uv` not found: install uv using one of the methods above.
- `cookiecutter` not found: install it with `py -3 -m pip install --user cookiecutter`.

## Publishing to GitHub and sensitive info
- This repo does not contain secrets by default.
- Generated projects and their virtual environments are separate from this repo.
- `.gitignore` includes common environment folders (`.venv`, etc.). We've also added ignores for uv artifacts.
- Before pushing, quickly review your changes and avoid committing any generated project folders into this repo.

If you later publish generated projects, review those repos independently for secrets.

---
For more Python for Engineering content, see: https://flocode.substack.com/
