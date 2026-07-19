# Contributing to DevPilot CLI

Thanks for helping improve DevPilot CLI.

## Development setup

1. Fork and clone the repository.
2. Create a feature branch from `main`.
3. Create a virtual environment.
4. Install the editable package with development tools.

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

## Before opening a pull request

```powershell
pytest --cov=devpilot --cov-report=term-missing
ruff check .
ruff format --check .
python -m build
python -m twine check dist/*
```

New behavior should include tests. Keep command functions focused on input and
presentation; put reusable logic in `services/` and structured results in
`models/`.

## Safety expectations

- Do not add destructive defaults.
- Do not bypass robots.txt, authentication, paywalls, or CAPTCHA.
- Do not log credentials, tokens, cookies, or personal data.
- Validate file paths, URLs, redirects, and output bounds.
- Keep Windows, Linux, and macOS compatibility in mind.

Use Conventional Commit-style messages when practical, such as `feat:`, `fix:`,
`test:`, and `docs:`.
