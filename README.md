# DevPilot CLI

A modular developer toolkit for the terminal, built with Python, Typer, and Rich.

## Development setup

Create and activate a virtual environment on Windows:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install the project with its development tools:

```powershell
python -m pip install -e ".[dev]"
```

Run the CLI:

```powershell
devpilot --help
```

Core commands:

```powershell
devpilot version
devpilot about
devpilot doctor
```

Use the global debug option before a command when detailed error diagnostics are
needed:

```powershell
devpilot --debug doctor
```

Inspect local system resources:

```powershell
devpilot system info
devpilot system cpu
devpilot system memory
devpilot system disk
devpilot system info --output json
```

Human-facing commands use Rich tables. The JSON output preserves byte counts as
numbers so it can be consumed safely by scripts and other tools.

Inspect files and directories without modifying them:

```powershell
devpilot file info README.md
devpilot file hash README.md
devpilot file hash README.md --algorithm sha512
devpilot file tree . --depth 3
devpilot file largest . --limit 10
```

File hashes are calculated incrementally, so large files are not loaded fully
into memory. Recursive commands do not follow symbolic links.

Run the quality checks:

```powershell
pytest
ruff check .
ruff format --check .
```

## Project status

DevPilot CLI is in early development. The current milestone provides the tested
project foundation; developer tools will be added incrementally.

## License

This project is licensed under the MIT License. See `LICENSE` for details.
