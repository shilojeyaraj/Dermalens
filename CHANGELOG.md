# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Professional repository infrastructure:
  - GitHub Actions CI (frontend lint + Jest; backend Black/isort/Flake8 + pytest, with coverage)
  - CodeQL SAST scanning, Dependency Review, and Dependabot
  - Release workflow that publishes a GitHub Release on `v*.*.*` tags
  - Jest + React Testing Library harness and a pytest suite (unit + integration)
  - ESLint, Prettier, Black, isort, Flake8, EditorConfig, and pre-commit hooks
  - `Makefile`, `Dockerfile`, and refreshed `docker-compose.yml`
  - `CONTRIBUTING.md`, `SECURITY.md`, `docs/ARCHITECTURE.md`, `docs/API.md`, issue/PR templates, `CODEOWNERS`, MIT `LICENSE`

### Fixed

- `react-hooks/rules-of-hooks` violation in the settings page (a `useEffect`
  ran after a conditional early return).
- Backend `logger` used before definition in import-time `except` blocks
  (`apps/api/main.py`, `enhanced_comprehensive_analysis_service.py`).
- Routine validation dropped accumulated warnings because sub-validator results
  were combined with `dict.update()` instead of being merged.

### Changed

- Archived the non-deployed legacy backend (`backend/`) to `docs/archive/`.
- Formatted the `apps/api` backend with Black + isort.

### Removed

- Dead duplicate directories (`apps/web`, `packages/`), a committed Redis `.msi`
  binary, duplicate Dockerfiles, and other tracked build/junk artifacts.

## [0.1.1] - 2025-12-13

### Added

- Initial Dermalens platform: AI-powered skin analysis (Google Gemini / Vertex AI),
  Elasticsearch product search, Supabase auth, and a Next.js frontend.

[Unreleased]: https://github.com/shilojeyaraj/Dermalens/compare/v0.1.1...HEAD
[0.1.1]: https://github.com/shilojeyaraj/Dermalens/releases/tag/v0.1.1
