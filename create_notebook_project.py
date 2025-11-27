import argparse
import json
import logging
import shutil
import subprocess
import sys
import re
from pathlib import Path
from typing import Dict, Union

from cookiecutter.main import cookiecutter

# Configure logging
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")

# Template Directory Structure for a basic Jupyter project
TEMPLATE_STRUCTURE: Dict[str, Union[str, dict]] = {
    "cookiecutter.json": json.dumps(
        {
            "project_name": "default_project_name",
            "author_name": "Your Name",
            "description": "A Jupyter notebook-based project.",
        },
        indent=4,
    ),
    "{{cookiecutter.project_name}}": {
        "data": {},  # Data directory
        "src": {},  # Source code directory
        "notebook_01.ipynb": json.dumps(
            {"cells": [], "metadata": {}, "nbformat": 4, "nbformat_minor": 5}, indent=4
        ),  # Blank Jupyter notebook file
        "README.md": (
            "# {{cookiecutter.project_name}}\n\n"
            "{{cookiecutter.description}}\n\n"
            "## Author\n"
            "{{cookiecutter.author_name}}"
        ),
    },
}


def create_template_structure(
    base_path: Path, structure: Dict[str, Union[str, dict]]
) -> None:
    """
    Recursively creates the project structure based on the template dictionary.
    """
    for name, content in structure.items():
        current_path = base_path / name
        if isinstance(content, dict):
            current_path.mkdir(parents=True, exist_ok=True)
            create_template_structure(current_path, content)
        else:
            current_path.parent.mkdir(parents=True, exist_ok=True)
            current_path.write_text(content, encoding="utf-8")


def run_command(command: list, cwd: Path = None) -> None:
    """
    Runs shell commands using subprocess, with error handling.
    """
    logging.info(f"Running command: {' '.join(command)}")
    try:
        subprocess.run(
            command, check=True, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
    except subprocess.CalledProcessError as e:
        logging.error(
            f"Error running command {' '.join(command)}: {e.stderr.decode().strip()}"
        )
        sys.exit(1)


def initialize_project_environment(project_path: Path) -> None:
    """
    Initializes a Python project environment using `uv` and installs `ipykernel`.
    """
    if not shutil.which("uv"):
        logging.error("'uv' is not installed or not in the system PATH.")
        sys.exit(1)

    run_command(["uv", "init"], cwd=project_path)
    run_command(["uv", "add", "ipykernel"], cwd=project_path)


def update_pyproject(project_dir: Path, name: str, description: str, author: str) -> None:
    """
    Update [project] section in pyproject.toml with name, description, and authors.
    Uses simple line-level edits to avoid extra dependencies.
    """
    pyproject = project_dir / "pyproject.toml"
    if not pyproject.exists():
        logging.warning("pyproject.toml not found; skipping metadata update.")
        return

    text = pyproject.read_text(encoding="utf-8")
    lines = text.splitlines()

    # Locate [project] section boundaries
    proj_start = None
    proj_end = len(lines)
    for i, line in enumerate(lines):
        if line.strip() == "[project]":
            proj_start = i
            break
    if proj_start is None:
        logging.warning("[project] section not found in pyproject.toml; skipping metadata update.")
        return

    for j in range(proj_start + 1, len(lines)):
        if lines[j].strip().startswith("[") and lines[j].strip().endswith("]"):
            proj_end = j
            break

    def set_or_replace(key: str, value: str):
        nonlocal lines, proj_start, proj_end
        pattern = re.compile(rf"^\s*{re.escape(key)}\s*=\s*.*$")
        for k in range(proj_start + 1, proj_end):
            if pattern.match(lines[k]):
                lines[k] = f'{key} = "{value}"'
                return True
        # If not found, insert just after [project]
        lines.insert(proj_start + 1, f'{key} = "{value}"')
        proj_end += 1
        return False

    # Update name and description
    set_or_replace("name", name)
    set_or_replace("description", description)

    # Authors: set to array of tables with name only
    authors_pattern = re.compile(r"^\s*authors\s*=\s*\[")
    authors_set = False
    for k in range(proj_start + 1, proj_end):
        if authors_pattern.match(lines[k]):
            lines[k] = f"authors = [{{ name = \"{author}\" }}]"
            authors_set = True
            break
    if not authors_set:
        lines.insert(proj_start + 1, f"authors = [{{ name = \"{author}\" }}]")
        proj_end += 1

    pyproject.write_text("\n".join(lines) + "\n", encoding="utf-8")
    logging.info("Updated pyproject.toml with project metadata.")

def parse_arguments() -> argparse.Namespace:
    """
    Parses command-line arguments.
    """
    parser = argparse.ArgumentParser(
        description="Create a Jupyter project using Cookiecutter."
    )
    parser.add_argument(
        "-t",
        "--template-folder",
        default="jupyter-basic",
        help="Template folder name to use (default: 'jupyter-basic').",
    )
    parser.add_argument("-n", "--name", help="Name of the new project.")
    parser.add_argument(
        "-a",
        "--author",
        default="Giovanni",
        help="Author name (default: 'Giovanni\'Sc').",
    )
    parser.add_argument(
        "-d",
        "--description",
        default="A Jupyter notebook-based project.",
        help="Project description.",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        type=Path,
        help="Directory where the new project should be created.",
    )

    args = parser.parse_args()

    # Prompt for project name if not provided
    if not args.name:
        args.name = input("Enter the project name: ").strip()
        if not args.name:
            parser.error("the following arguments are required: -n/--name")

    return args


def find_dev_root(start: Path) -> Path:
    """
    Search upwards from 'start' for a folder named 'dev'. If not found,
    use %USERPROFILE%/dev if it exists; otherwise, return start.parent.
    """
    for ancestor in [start] + list(start.parents):
        if ancestor.name.lower() == "dev":
            return ancestor
    home_dev = Path.home() / "dev"
    if home_dev.exists():
        return home_dev
    return start.parent


def prepare_template_directory(templates_base_dir: Path, template_folder: str) -> Path:
    """
    Ensures the template directory exists and is populated.
    """
    template_path = templates_base_dir / template_folder

    if not template_path.exists():
        logging.info(f"Creating new template at: {template_path}")
        create_template_structure(template_path, TEMPLATE_STRUCTURE)
    else:
        logging.info(f"Using existing template from: {template_path}")

    return template_path


def main():
    """
    Main function to handle the creation of the project template and initialize the project.
    """
    args = parse_arguments()

    # Anchor paths to the script location (robust regardless of CWD)
    script_dir = Path(__file__).resolve().parent

    # Resolve output directory (default to nearest 'dev')
    default_output_dir = find_dev_root(script_dir)
    output_dir: Path = args.output_dir or default_output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    logging.info(f"Using output directory: {output_dir}")

    # Define the base path where all templates are stored (inside repo)
    templates_base_dir = script_dir / "cookiecutter-project-templates"
    templates_base_dir.mkdir(parents=True, exist_ok=True)

    # Prepare the template directory
    template_path = prepare_template_directory(templates_base_dir, args.template_folder)

    # Use Cookiecutter to create a new project with the provided context
    try:
        project_dir = Path(
            cookiecutter(
                str(template_path),
                no_input=True,
                extra_context={
                    "project_name": args.name,
                    "author_name": args.author,
                    "description": args.description,
                },
                output_dir=str(output_dir),
            )
        )
        logging.info(f"Project created at: {project_dir}")

        # Initialize the project environment
        initialize_project_environment(project_dir)

        # Ensure pyproject.toml reflects chosen metadata
        update_pyproject(project_dir, args.name, args.description, args.author)
        logging.info("Project environment initialized successfully.")

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
