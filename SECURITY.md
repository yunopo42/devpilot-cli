# Security Policy

## Supported versions

Security fixes currently target the latest `0.x` release of DevPilot CLI.

## Reporting a vulnerability

Please use the repository's
[private GitHub security advisory form](https://github.com/yunopo42/devpilot-cli/security/advisories/new).
Do not open a public issue for an unpatched vulnerability.

Include:

- A clear description and affected command
- Reproduction steps using non-sensitive test data
- Expected and observed behavior
- Platform and Python version
- Potential impact and suggested mitigation, if known

Do not include real credentials, session cookies, tokens, or personal data.

## Security boundaries

DevPilot is a local developer utility, not a security scanner or isolation
sandbox. Web safeguards reduce accidental access to unsafe targets but do not
replace organizational network policy. Only run commands against files and web
resources you are authorized to access.
