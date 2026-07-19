# DevPilot CLI

[![Tests](https://github.com/yunopo42/devpilot-cli/actions/workflows/tests.yml/badge.svg)](https://github.com/yunopo42/devpilot-cli/actions/workflows/tests.yml)

One terminal. Many developer tools.

DevPilot CLI is a modular Python command-line toolkit for system inspection,
safe file analysis, JSON and encoding utilities, accessible terminal themes,
and robots-aware public web inspection.

> Status: `v0.1.0` alpha release. The command API may change before 1.0.

## Highlights

- Cross-platform system information with table and JSON output
- Streaming SHA-256, SHA-512, and BLAKE2b file hashing
- Bounded directory trees and largest-file discovery
- JSON validation, formatting, and atomic `--write`
- Unicode Base64 helpers, UUID4 generation, and secure passwords
- Persistent validated configuration and accessible Hacker Mode visuals
- Public-web URL, redirect, peer-IP, robots.txt, timeout, and size safeguards
- Tested on Python 3.11, 3.12, and 3.13

## Requirements

- Python 3.11 or newer
- Windows, Linux, or macOS

## Installation

For an isolated command-line installation, use
[pipx](https://packaging.python.org/en/latest/guides/installing-stand-alone-command-line-tools/):

```powershell
pipx install devpilot-cli
```

Alternatively, install DevPilot in an active virtual environment with
`python -m pip install devpilot-cli`.

Verify the installation:

```powershell
devpilot version
devpilot doctor
devpilot --help
```

## Command overview

### Core

```powershell
devpilot version
devpilot about
devpilot doctor
devpilot --debug doctor
```

### System information

```powershell
devpilot system info
devpilot system info --output json
devpilot system cpu
devpilot system memory
devpilot system disk
```

### Read-only file tools

```powershell
devpilot file info README.md
devpilot file hash README.md
devpilot file hash README.md --algorithm sha512
devpilot file tree . --depth 3
devpilot file largest . --limit 10
```

Hashing is streamed in chunks. Recursive commands do not follow symbolic links.
File commands in `v0.1.0` do not delete, move, or rename data.

### Developer utilities

```powershell
devpilot dev json format data.json
Get-Content data.json | devpilot dev json validate
devpilot dev json format data.json --write
devpilot dev base64 encode "hello"
devpilot dev base64 decode "aGVsbG8="
devpilot dev uuid --count 5
devpilot dev password --length 24
```

JSON is only modified when `--write` is explicit, using an atomic replacement.
Passwords use Python's cryptographically secure `secrets` module.

### Configuration and themes

```powershell
devpilot config show
devpilot config set animations false
devpilot config set reduced-motion true
devpilot config reset
devpilot theme list
devpilot theme set hacker
devpilot hacker banner
devpilot hacker boot
devpilot hacker matrix --duration 5
devpilot --no-animation hacker boot
```

Animations automatically become static for reduced motion, disabled config,
piped output, or CI. Matrix duration is restricted to 1-15 seconds. Hacker Mode
changes presentation only and does not enable security or network-access powers.

### Safe public-web inspection

```powershell
devpilot web robots https://example.com
devpilot web title https://example.com
devpilot web links https://example.com --limit 20
devpilot web fetch https://example.com
```

Web commands respect robots.txt and enforce public-network URL checks, redirect
and peer-IP validation, a 15-second timeout, and a 2 MiB body limit. They do not
use cookies, credentials, environment proxies, or browser sessions.

## Development

Clone the repository and install it with development tools:

```powershell
git clone https://github.com/yunopo42/devpilot-cli.git
cd devpilot-cli
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

Run the quality checks:

```powershell
pytest
pytest --cov=devpilot --cov-report=term-missing
ruff check .
ruff format --check .
python -m build
python -m twine check dist/*
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for the contribution workflow and
[SECURITY.md](SECURITY.md) for vulnerability reporting.

## Roadmap after v0.1.0

- Reusable scraping recipes with rate limiting and cache
- Project generators
- Textual full-screen interface
- Stable plugin API

## License

DevPilot CLI is available under the [MIT License](LICENSE).
