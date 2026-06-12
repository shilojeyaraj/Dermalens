# Spec: Professionalize the Dermalens Repository

**Date:** 2026-06-11
**Status:** Approved
**Branch:** `chore/professional-repo-setup`

## Goal

Add the professional, production-grade repository infrastructure that recruiters look
for (CI/CD, real tests, code-quality tooling, docs, security policy) to the existing
Dermalens project, and remove accumulated cruft — so the repo reads as a well-run,
professional system.

## Context

Dermalens is an **existing, deployed** full-stack app, not greenfield:

- **Frontend:** Next.js 14 + TypeScript + React 18 + Tailwind + shadcn/ui, at repo root
  (`app/`, `components/`, `lib/`, `contexts/`). Deployed to Vercel.
- **Backend:** Python FastAPI ML service in `backend/` (Gemini-based skin analysis,
  ingredient database, product search).

### Current gaps
- No `.github/` directory — zero CI/CD.
- `tests/{unit,integration,e2e}` exist but are empty.
- No linter/formatter/test configuration files.
- No CONTRIBUTING / CHANGELOG / SECURITY / LICENSE / issue & PR templates / Makefile /
  dependabot.

### Current cruft (all tracked in git)
- `Redis-x64-3.0.504.msi` (6.7 MB binary).
- Junk files from mistyped commands: `et --hard HEAD`, `tatus`, `temp_scan_page.tsx`.
- Duplicate Dockerfiles: `Dockerfile.production`, `Dockerfile.simple`, `Dockerfile.working`.
- Abandoned monorepo `apps/` + `packages/` (90 tracked files) duplicating the root app,
  not wired into any workspace tooling.
- `backend/*.bak` files; scattered marketing/status markdown at repo root.

### Confirmed
- No `.env` files are tracked by git (only on disk + gitignored) — no committed secrets.
- `backend/ingredient_database.py` contains a real `IngredientDatabase` class with
  testable pure logic.

## Decisions (from brainstorming)

| Decision | Choice |
|---|---|
| Cleanup scope | Add infra **and** full cleanup (remove cruft + abandoned `apps/`/`packages/`) |
| License | **MIT** |
| Test depth | **Real, green tests** that pass in CI (both stacks) |
| CI security | **Include** CodeQL SAST + dependency vulnerability checks + Dependabot |

## Guiding Principle

Respect the existing idiomatic structure. **Do not** introduce a `src/` reorg — it would
break Vercel deployment and the `@/*` path imports. Frontend source stays at root
(standard Next.js); backend source stays in `backend/`.

## Tooling

| Concern | Frontend (TS/Next.js) | Backend (Python/FastAPI) |
|---|---|---|
| Test runner | Jest + `next/jest` + React Testing Library | pytest + pytest-cov |
| Coverage | Jest built-in (lcov) | pytest-cov (lcov/xml) |
| Lint | ESLint (`eslint-config-next`) | Flake8 + mypy |
| Format | Prettier | Black + isort |
| Config home | `.eslintrc.json`, `.prettierrc`, `jest.config.ts` | `pyproject.toml` + `.flake8` |

## File Manifest

### 1. Tests (real & green)
- `tests/unit/utils.test.ts` — real tests for `cn()` (Tailwind class merge/dedupe).
- `tests/integration/*.test.tsx` — React Testing Library render test of a UI component.
- `tests/e2e/*.spec.ts` — Playwright **stub** (skipped, documented).
- `backend/tests/unit/test_ingredient_database.py` — real tests against `IngredientDatabase`.
- `backend/tests/integration/test_*.py` — integration test of an ingredient lookup flow.
- `jest.config.ts`, `jest.setup.ts`, `backend/tests/conftest.py`.

### 2. Code quality
`.eslintrc.json`, `.prettierrc`, `.prettierignore`, `.editorconfig`,
`pyproject.toml` (black/isort/pytest/coverage/mypy), `.flake8`, `.pre-commit-config.yaml`.

### 3. CI/CD (`.github/workflows/`)
- `ci.yml` — two jobs: **frontend** (lint + jest + coverage) and **backend**
  (flake8 + black --check + pytest + coverage); on push/PR to `main`; upload coverage.
- `codeql.yml` — CodeQL SAST for `javascript-typescript` + `python`.
- `dependency-review.yml` — dependency vulnerability review on PRs (+ `npm audit`/`pip-audit`).
- `release.yml` — on `v*.*.*` tags: build + create a GitHub Release with notes.

### 4. GitHub meta
`.github/pull_request_template.md`,
`.github/ISSUE_TEMPLATE/{bug_report.md,feature_request.md,config.yml}`,
`CODEOWNERS`, `.github/dependabot.yml` (npm + pip + github-actions ecosystems).

### 5. Documentation
- Enhance `README.md` — add CI/coverage/license badges; ensure setup/usage/contributing/
  license sections.
- `CONTRIBUTING.md` — branching strategy, PR process, Conventional Commits.
- `CHANGELOG.md` — Keep a Changelog format.
- `docs/ARCHITECTURE.md` — high-level architecture + diagram placeholder.
- `docs/API.md` — FastAPI endpoint documentation template.
- `SECURITY.md` — responsible disclosure policy.
- `LICENSE` — MIT.

### 6. Build & env
- `Makefile` — dual-stack targets: `install`, `run`, `test`, `test-coverage`, `lint`,
  `format`, `docker-build`, `docker-run`, `clean`.
- Standardize `env.example` → `.env.example`.

### 7. Docker
- Consolidate to one root `Dockerfile` (frontend, multi-stage slim) + keep `backend/Dockerfile`.
- Review/refresh `docker-compose.yml` (app + postgres/redis stubs); keep `.dockerignore`.

## Cleanup (destructive — `git rm`)

- `Redis-x64-3.0.504.msi`
- `et --hard HEAD`, `tatus`, `temp_scan_page.tsx`
- `Dockerfile.production`, `Dockerfile.simple`, `Dockerfile.working`, `next.config.simple.js`
  (after verifying nothing references them)
- `apps/` + `packages/` (confirmed not wired into workspace tooling)
- `backend/*.bak`
- Move scattered root markdown (`HACKATHON_SUBMISSION.md`, `LINKEDIN_POST*.md`,
  `PROFILE_AND_PRODUCTS_FIXES.md`, `PRODUCT_FILTERS_VERIFICATION.md`, deployment guides)
  into `docs/`; keep only README/CONTRIBUTING/CHANGELOG/SECURITY/LICENSE at root.

### Off-limits
`app/`, `components/`, `lib/`, `contexts/`, real `backend/*.py` application logic, and
deployed config (`next.config.js`, `vercel.json`, `tsconfig.json`). Anything ambiguous is
grep-verified for references before deletion.

## Verification (definition of done)

Before claiming complete:
1. `npm install` + `npx jest` → green.
2. Backend deps install + `pytest` → green.
3. ESLint / Prettier / Black / Flake8 run clean on new files.
4. `next build` still succeeds (deployment not broken).

## Out of Scope

- Restructuring application code into `src/`.
- Rewriting existing application logic or the deployed Vercel/Cloud configs.
- Multi-agent orchestration (done manually with verification).
