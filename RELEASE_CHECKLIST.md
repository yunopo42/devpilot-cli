# v0.1.0 Release Checklist

## Code and tests

- [x] Working tree is clean.
- [x] Full pytest suite passes.
- [x] Coverage meets the configured threshold.
- [x] Ruff lint and format checks pass.
- [x] Windows, Ubuntu, and macOS CI jobs pass on Python 3.11-3.13.

## Package

- [x] `python -m build` creates one wheel and one source distribution.
- [x] `python -m twine check dist/*` passes.
- [x] Wheel installs in a clean virtual environment.
- [x] `devpilot version` reports `0.1.0`.
- [x] `devpilot doctor` passes in the clean environment.
- [x] Wheel metadata and included files are inspected.

## Documentation and security

- [x] README installation and examples are current.
- [x] CHANGELOG contains the release date and features.
- [x] SECURITY and CONTRIBUTING policies are present.
- [x] Web safety limits and Hacker Mode boundaries are documented.

## Publication

- [x] GitHub Actions is green on `main`.
- [x] TestPyPI Trusted Publishing is configured for `test-publish.yml`.
- [x] TestPyPI upload and clean installation succeed.
- [ ] PyPI Trusted Publishing is configured for `release.yml`.
- [ ] The `pypi` GitHub environment requires maintainer approval.
- [ ] Signed or annotated `v0.1.0` tag is created.
- [ ] GitHub Release is published from the tag.
- [ ] PyPI upload is confirmed explicitly by the maintainer.
