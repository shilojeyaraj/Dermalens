# Contributing to Dermalens

Thanks for your interest in contributing! This guide covers the workflow,
conventions, and tooling used in this repository.

## Project layout

```
.
├── app/, components/, lib/, contexts/   # Next.js 14 frontend (deployed to Vercel)
├── apps/api/                            # FastAPI backend (deployed to Cloud Run)
├── tests/                               # Frontend Jest tests (unit/integration/e2e)
├── apps/api/tests/                      # Backend pytest tests (unit/integration)
└── docs/                                # Documentation (architecture, API, archive)
```

## Getting started

### Frontend

```bash
npm install
npm run dev          # http://localhost:3000
```

### Backend

```bash
pip install -r apps/api/requirements.txt -r requirements-dev.txt
cd apps/api && uvicorn main:app --reload   # http://localhost:8000  (docs at /docs)
```

Copy `.env.example` to `.env` and fill in your own values. **Never commit `.env`.**

## Branching strategy

- `main` is always deployable.
- Create a topic branch off `main` using a Conventional-Commit-style prefix:
  - `feat/<short-description>` — new functionality
  - `fix/<short-description>` — bug fixes
  - `chore/<short-description>` — tooling, config, maintenance
  - `docs/<short-description>` — documentation only

## Commit messages — Conventional Commits

Format: `<type>(optional scope): <description>`

| Type       | Use for                                            |
| ---------- | -------------------------------------------------- |
| `feat`     | A new feature                                      |
| `fix`      | A bug fix                                           |
| `docs`     | Documentation only                                 |
| `style`    | Formatting (no code-behavior change)               |
| `refactor` | Code change that neither fixes a bug nor adds feat |
| `test`     | Adding or fixing tests                             |
| `chore`    | Build process, tooling, dependencies               |
| `ci`       | CI/CD configuration                                |

Example: `feat(scan): add retake button to the capture screen`

## Pull request process

1. Branch off `main` and make your change.
2. Add or update tests and make sure everything passes (see below).
3. Run the linters/formatters.
4. Open a PR against `main`. Fill in the PR template checklist.
5. CI (lint, tests, CodeQL, dependency review) must be green before merge.
6. Squash-merge with a Conventional Commit title.

## Running checks locally

```bash
# Frontend
npm run lint
npm test
npm run format        # auto-format with Prettier

# Backend
black apps/api && isort apps/api      # auto-format
flake8 apps/api                       # lint
pytest apps/api/tests                 # tests

# Everything (requires GNU Make; use WSL/Git Bash on Windows)
make lint
make test
make format
```

### Pre-commit hooks (optional but recommended)

```bash
pip install pre-commit
pre-commit install
```

This runs formatters and basic checks automatically on every commit.

## Code style

- **Frontend:** Prettier + ESLint (`next/core-web-vitals`). 2-space indent, no semicolons.
- **Backend:** Black + isort (profile=black) + Flake8. 4-space indent, 100-char lines.
- `.editorconfig` enforces the basics across editors.

## Reporting issues

Use the issue templates (bug report / feature request). For security issues, see
[SECURITY.md](SECURITY.md) — do **not** open a public issue.
