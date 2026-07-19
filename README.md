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

Use everyday developer utilities:

```powershell
devpilot dev json format data.json
Get-Content data.json | devpilot dev json validate
devpilot dev json format data.json --write
devpilot dev base64 encode "hello"
devpilot dev base64 decode "aGVsbG8="
devpilot dev uuid --count 5
devpilot dev password --length 24
```

JSON files are never modified unless `--write` is provided explicitly. A write
uses a complete temporary file followed by an atomic replacement. Passwords are
generated with Python's cryptographically secure `secrets` module.

Configure motion and visual themes:

```powershell
devpilot config show
devpilot config set animations false
devpilot config set reduced-motion true
devpilot config reset
devpilot theme list
devpilot theme set hacker
devpilot hacker banner
```

Settings are validated and stored in the operating system's standard user config
directory. Hacker Mode changes presentation only; it does not enable security or
network-access features.

Run optional, bounded visual effects:

```powershell
devpilot hacker boot
devpilot hacker matrix --duration 5
devpilot --no-animation hacker boot
```

Animations automatically fall back to static output when reduced motion is
enabled, animations are disabled in config, output is piped, or a CI environment
is detected. Matrix duration is restricted to 1–15 seconds.

Inspect public web pages within strict request limits:

```powershell
devpilot web robots https://example.com
devpilot web title https://example.com
devpilot web links https://example.com --limit 20
devpilot web fetch https://example.com
```

Web commands respect robots.txt, validate every redirect, reject local/private
network targets, use a 15-second timeout, and limit response bodies to 2 MiB.
They do not use cookies, credentials, environment proxies, or browser sessions.

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
