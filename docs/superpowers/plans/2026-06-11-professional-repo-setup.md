# Professional Repo Setup Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add professional, production-grade repo infrastructure (CI/CD, real green tests, code-quality tooling, docs, security) to the existing Dermalens app and remove accumulated cruft.

**Architecture:** Two stacks in one repo — Next.js 14 frontend at root (`app/`, `components/`, `lib/`, `contexts/`) and a Python FastAPI backend in `backend/`. No `src/` reorg (would break Vercel + `@/*` imports). Frontend tooling: Jest/RTL, ESLint, Prettier. Backend tooling: pytest, Flake8, Black, isort, mypy. CI runs both stacks separately.

**Tech Stack:** Next.js 14, TypeScript, React 18, Tailwind; Python 3.11, FastAPI, pytest; GitHub Actions, CodeQL, Dependabot, Docker.

---

## ⚠️ Plan Correction (2026-06-11, after repo investigation)

The original assumption ("`apps/` is fully abandoned, `backend/` is canonical") was **wrong for the backend**. Verified facts:
- **`apps/api` is the LIVE deployed backend** (`cloudbuild.yaml` builds `./apps/api` → Cloud Run `dermalens-backend`; `vercel.json` rewrites `/api/*` to it). Deps: `apps/api/requirements.txt` (20 pkgs, no torch).
- **`backend/`** is an older non-deployed duplicate. The torch-heavy **root `requirements.txt`** belongs to it.
- **`apps/web`** and **`packages/`** are confirmed dead (imported/referenced by nothing).

**User decision:** Keep `apps/api`; **archive** `backend/` (+ root `requirements.txt`) into `docs/archive/legacy-backend/`; delete `apps/web` + `packages/`. Backend tests/CI/docs target **`apps/api`**; dev tooling goes in a new root **`requirements-dev.txt`**.

Tasks below are updated to reflect this. Where a task still says `backend/`, read `apps/api`.

---

## Phase A — Cleanup

### Task 1: Remove cruft, archive legacy backend, declutter root

**Files:**
- Delete (git rm): `Redis-x64-3.0.504.msi`, `et --hard HEAD`, `tatus`, `temp_scan_page.tsx`, `apps/web/` (recursive), `packages/` (recursive), `Dockerfile.production`, `Dockerfile.simple`, `Dockerfile.working`, `next.config.simple.js`, stray junk (`variables.txt`, `simple_app.py`, `camera-test.html`) after ref-check
- Archive (git mv): `backend/` → `docs/archive/legacy-backend/backend/`, root `requirements.txt` → `docs/archive/legacy-backend/requirements.txt`
- Move (git mv) scattered root markdown → `docs/archive/`
- **Keep untouched:** `apps/api/` (live backend), root frontend, `cloudbuild.yaml`, `vercel.json`

- [ ] **Step 1: (done during planning)** Verified: no live config/script references the dup Dockerfiles, `next.config.simple.js`, `apps/web`, or `packages/`; `apps/api` is referenced by `cloudbuild.yaml`.

- [ ] **Step 2: git rm junk + dead duplicates + dup Dockerfiles** (note: `apps/api` is preserved)

```bash
git rm -r --quiet "Redis-x64-3.0.504.msi" "et --hard HEAD" "tatus" "temp_scan_page.tsx" \
  apps/web packages Dockerfile.production Dockerfile.simple Dockerfile.working next.config.simple.js
```

- [ ] **Step 3: Archive legacy backend + its requirements** (preserve, don't delete)

```bash
mkdir -p docs/archive/legacy-backend
git mv backend docs/archive/legacy-backend/backend
git mv requirements.txt docs/archive/legacy-backend/requirements.txt
```

- [ ] **Step 4: Ref-check then remove stray non-md junk**

For each of `variables.txt`, `simple_app.py`, `camera-test.html`: confirm no live reference (`grep -rn name`), then `git rm`. If referenced, leave it.

- [ ] **Step 5: Move scattered root markdown into docs/archive/**

`git mv` into `docs/archive/`: `HACKATHON_SUBMISSION.md`, `LINKEDIN_POST.md`, `LINKEDIN_POST_HACKATHON.md`, `PROFILE_AND_PRODUCTS_FIXES.md`, `PRODUCT_FILTERS_VERIFICATION.md`, `PRODUCTION_READINESS_CHECKLIST.md`, `DEPLOYMENT_CHECKLIST.md`, `GOOGLE_CLOUD_DEPLOYMENT.md`, `PRODUCTION_DEPLOYMENT_GUIDE.md`, `VERCEL_DEPLOYMENT.md`, `SUPABASE_KEEPALIVE_SETUP.md`, `INSTRUCTIONS.md`, `deploy-vercel.md`, `PORTFOLIO_PROJECT_DESCRIPTION.md`, `repo_professionalism_prompt.md`.
Keep at root: `README.md`.

- [ ] **Step 6: Commit**

```bash
git add -A && git commit -m "chore: remove cruft, archive legacy backend, declutter root"
```

---

## Phase B — Code Quality Configuration

### Task 2: Frontend lint/format configs

**Files:**
- Create: `.eslintrc.json`, `.prettierrc`, `.prettierignore`, `.editorconfig`

- [ ] **Step 1: Create `.eslintrc.json`** — extends `next/core-web-vitals` + `prettier`; relax rules that would flood an existing codebase (`react/no-unescaped-entities: off`, `@next/next/no-img-element: warn`).
- [ ] **Step 2: Create `.prettierrc`** — `semi: false`, `singleQuote: false`, `printWidth: 100`, `trailingComma: "es5"` (match existing style in `lib/utils.ts`).
- [ ] **Step 3: Create `.prettierignore`** — ignore `.next/`, `node_modules/`, `backend/`, `venv/`, coverage, lockfiles, `*.png/jpg/jpeg/msi`.
- [ ] **Step 4: Create `.editorconfig`** — UTF-8, LF, 2 spaces for web, 4 spaces for `*.py`, trim trailing whitespace.
- [ ] **Step 5: Add devDeps** — `eslint`, `eslint-config-prettier`, `prettier`, plus `prettier`/eslint scripts in package.json (`"lint:fix"`, `"format"`, `"format:check"`). Run `npm install`.
- [ ] **Step 6: Verify** — `npx prettier --check "lib/**/*.ts"` runs without crashing; `npx next lint` runs.
- [ ] **Step 7: Commit** — `chore: add eslint + prettier + editorconfig`

### Task 3: Backend lint/format/test config

**Files:**
- Create: `pyproject.toml`, `.flake8`

- [ ] **Step 1: Create `pyproject.toml`** with `[tool.black]` (line-length 100, target py311), `[tool.isort]` (profile "black"), `[tool.pytest.ini_options]` (`testpaths = ["backend/tests"]`, `pythonpath = ["backend"]`), `[tool.coverage.run]` (`source = ["backend"]`, omit tests), `[tool.mypy]` (ignore_missing_imports).
- [ ] **Step 2: Create `.flake8`** — `max-line-length = 100`, `extend-ignore = E203,W503`, exclude `venv,__pycache__,backend/models,data`.
- [ ] **Step 3: Verify** — `python -m black --check backend/ingredient_database.py` runs (may report reformat needed — fine).
- [ ] **Step 4: Commit** — `chore: add black/isort/flake8/pytest/mypy config`

---

## Phase C — Tests (real & green)

### Task 4: Frontend Jest harness + real unit test

**Files:**
- Create: `jest.config.ts`, `jest.setup.ts`, `tests/unit/utils.test.ts`

- [ ] **Step 1: Add dev deps** — `jest`, `jest-environment-jsdom`, `@testing-library/react`, `@testing-library/jest-dom`, `@testing-library/user-event`, `@types/jest`, `ts-node`. Add scripts: `"test": "jest"`, `"test:watch": "jest --watch"`, `"test:coverage": "jest --coverage"`. Run `npm install`.
- [ ] **Step 2: Create `jest.config.ts`** using `next/jest` `createJestConfig`, `testEnvironment: "jest-environment-jsdom"`, `setupFilesAfterEnv: ["<rootDir>/jest.setup.ts"]`, `testMatch` for `tests/**/*.test.{ts,tsx}`, `collectCoverageFrom: ["lib/**/*.{ts,tsx}", "components/**/*.{ts,tsx}"]`, moduleNameMapper `^@/(.*)$ -> <rootDir>/$1`.
- [ ] **Step 3: Create `jest.setup.ts`** — `import "@testing-library/jest-dom"`.
- [ ] **Step 4: Write the failing test** `tests/unit/utils.test.ts`:

```ts
import { cn } from "@/lib/utils"

describe("cn", () => {
  it("merges class names", () => {
    expect(cn("a", "b")).toBe("a b")
  })
  it("dedupes conflicting tailwind classes (last wins)", () => {
    expect(cn("px-2", "px-4")).toBe("px-4")
  })
  it("handles conditional and falsy values", () => {
    expect(cn("base", false, null, undefined, "active")).toBe("base active")
  })
})
```

- [ ] **Step 5: Run** — `npx jest tests/unit/utils.test.ts` → Expected: 3 passing.
- [ ] **Step 6: Commit** — `test: add frontend jest harness and cn() unit tests`

### Task 5: Frontend integration test + e2e stub

**Files:**
- Create: `tests/integration/card.test.tsx`, `tests/e2e/scan-flow.spec.ts`

- [ ] **Step 1: Write integration test** rendering a real shadcn component (`components/ui/card.tsx`):

```tsx
import { render, screen } from "@testing-library/react"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"

describe("Card", () => {
  it("renders composed card content", () => {
    render(
      <Card>
        <CardHeader>
          <CardTitle>Skin Analysis</CardTitle>
        </CardHeader>
        <CardContent>Results</CardContent>
      </Card>
    )
    expect(screen.getByText("Skin Analysis")).toBeInTheDocument()
    expect(screen.getByText("Results")).toBeInTheDocument()
  })
})
```

- [ ] **Step 2: Run** — `npx jest tests/integration/card.test.tsx` → Expected: pass. (If card.tsx exports differ, adjust imports to match actual exports.)
- [ ] **Step 3: Create e2e stub** `tests/e2e/scan-flow.spec.ts` — a Playwright test wrapped in `test.skip(...)` with a TODO comment explaining it needs a running server; documented as a stub so it never fails CI.
- [ ] **Step 4: Commit** — `test: add card integration test and e2e stub`

### Task 6: Backend pytest tests (real & green)

**Files:**
- Create: `backend/tests/__init__.py`, `backend/tests/conftest.py`, `backend/tests/unit/test_ingredient_database.py`, `backend/tests/integration/test_ingredient_lookup.py`

- [ ] **Step 1: Inspect** `backend/ingredient_database.py` for the exact public method names (e.g. `get_ingredients_for_condition`, `get_ingredient`, interactions). Write tests against the **real** API.
- [ ] **Step 2: Create `conftest.py`** with a fixture constructing `IngredientDatabase()`.
- [ ] **Step 3: Write unit test** asserting: known ingredient (`salicylic_acid`) exists with expected `category` "BHA"; lookups return dicts; unknown ingredient returns empty/None per actual behavior.
- [ ] **Step 4: Write integration test** exercising a condition→ingredients→interactions flow end-to-end against the default in-memory data.
- [ ] **Step 5: Run** — `python -m pytest backend/tests -v` → Expected: all pass. Adjust assertions to the real return types discovered in Step 1.
- [ ] **Step 6: Commit** — `test: add backend pytest suite for ingredient database`

---

## Phase D — Pre-commit

### Task 7: pre-commit hooks

**Files:** Create `.pre-commit-config.yaml`

- [ ] **Step 1: Create `.pre-commit-config.yaml`** with: `pre-commit-hooks` (trailing-whitespace, end-of-file-fixer, check-yaml, check-added-large-files `--maxkb=1000`, detect-private-key), `black`, `isort`, `flake8` for Python; a local `prettier` and `eslint` hook (or `mirrors-prettier`) scoped to `\.(ts|tsx|js|jsx|json|css|md)$` excluding `backend/`.
- [ ] **Step 2: Verify config parses** — `python -m yaml` load or `pre-commit validate-config` if available (skip if pre-commit not installed; CI will validate).
- [ ] **Step 3: Commit** — `chore: add pre-commit hooks`

---

## Phase E — CI/CD

### Task 8: ci.yml

**Files:** Create `.github/workflows/ci.yml`

- [ ] **Step 1: Create `ci.yml`** — `on: push (main), pull_request (main)`. Two jobs:
  - `frontend`: `actions/checkout`, `actions/setup-node@v4` (node 20, cache npm), `npm ci`, `npm run lint`, `npm run test:coverage`, upload coverage to Codecov (`codecov/codecov-action@v4`, `flags: frontend`, `fail_ci_if_error: false`).
  - `backend`: `actions/setup-python@v5` (3.11, cache pip), `pip install -r requirements.txt`, `flake8 backend`, `black --check backend`, `pytest backend/tests --cov=backend --cov-report=xml`, upload coverage (`flags: backend`).
  Add inline comments explaining non-obvious settings (e.g. `--legacy-peer-deps` if needed, `fail_ci_if_error: false`).
- [ ] **Step 2: Lint the YAML** — `python -c "import yaml,sys; yaml.safe_load(open('.github/workflows/ci.yml'))"` → no error.
- [ ] **Step 3: Commit** — `ci: add lint + test + coverage workflow`

### Task 9: CodeQL + dependency review

**Files:** Create `.github/workflows/codeql.yml`, `.github/workflows/dependency-review.yml`

- [ ] **Step 1: Create `codeql.yml`** — matrix `language: [javascript-typescript, python]`; `github/codeql-action/init@v3`, `autobuild`, `analyze`; on push/PR to main + weekly schedule.
- [ ] **Step 2: Create `dependency-review.yml`** — `on: pull_request`, `actions/dependency-review-action@v4` with `fail-on-severity: high`.
- [ ] **Step 3: Lint both YAMLs** (yaml.safe_load).
- [ ] **Step 4: Commit** — `ci: add CodeQL SAST and dependency review`

### Task 10: release.yml

**Files:** Create `.github/workflows/release.yml`

- [ ] **Step 1: Create `release.yml`** — `on: push: tags: ['v*.*.*']`; build frontend (`npm ci && npm run build`); create release via `softprops/action-gh-release@v2` with `generate_release_notes: true`; `permissions: contents: write`.
- [ ] **Step 2: Lint YAML.**
- [ ] **Step 3: Commit** — `ci: add release workflow on version tags`

---

## Phase F — GitHub Meta

### Task 11: Templates, CODEOWNERS, Dependabot

**Files:**
- Create: `.github/pull_request_template.md`, `.github/ISSUE_TEMPLATE/bug_report.md`, `.github/ISSUE_TEMPLATE/feature_request.md`, `.github/ISSUE_TEMPLATE/config.yml`, `.github/CODEOWNERS`, `.github/dependabot.yml`

- [ ] **Step 1: PR template** — checklist: tests written/passing, docs updated, lint passing, Conventional Commit title, linked issue.
- [ ] **Step 2: bug_report.md / feature_request.md** — front-matter (name, about, labels) + structured sections.
- [ ] **Step 3: config.yml** — `blank_issues_enabled: false`.
- [ ] **Step 4: CODEOWNERS** — `* @shilojeyaraj` (placeholder owner).
- [ ] **Step 5: dependabot.yml** — three ecosystems: `npm` (root), `pip` (root requirements), `github-actions`; weekly; grouped minor/patch.
- [ ] **Step 6: Commit** — `chore: add issue/PR templates, CODEOWNERS, dependabot`

---

## Phase G — Documentation

### Task 12: LICENSE, SECURITY, CONTRIBUTING, CHANGELOG

**Files:** Create `LICENSE`, `SECURITY.md`, `CONTRIBUTING.md`, `CHANGELOG.md`

- [ ] **Step 1: LICENSE** — MIT, copyright `2026 Shilo Jeyaraj`.
- [ ] **Step 2: SECURITY.md** — supported versions, private disclosure via `shilo@coincidencelabs.com`, response SLA.
- [ ] **Step 3: CONTRIBUTING.md** — branching (`main` + `feat/*`, `fix/*`, `chore/*`), PR process, Conventional Commits table, local setup, how to run tests/lint/format.
- [ ] **Step 4: CHANGELOG.md** — Keep a Changelog format; `## [Unreleased]` + `## [0.1.1]` initial entry.
- [ ] **Step 5: Commit** — `docs: add license, security policy, contributing, changelog`

### Task 13: ARCHITECTURE + API docs

**Files:** Create `docs/ARCHITECTURE.md`, `docs/API.md`

- [ ] **Step 1: ARCHITECTURE.md** — system overview, component diagram (ASCII/mermaid placeholder), frontend/backend/data-flow sections, tech decisions.
- [ ] **Step 2: API.md** — endpoint documentation template; populate from `backend/main.py` routes (inspect for actual `@app.get/@app.post` paths) with request/response examples; note Swagger UI at `/docs`.
- [ ] **Step 3: Commit** — `docs: add architecture and API documentation`

### Task 14: README badges + sections + .env.example

**Files:** Modify `README.md`; create `.env.example`

- [ ] **Step 1: Add badges** to README top — CI status, CodeQL, Codecov coverage, License MIT, plus the existing tech badges. Use repo slug `shilojeyaraj/Dermalens` (verify actual slug via `git remote -v`).
- [ ] **Step 2: Ensure README sections** — Features, Tech Stack, Quick Start (frontend + backend), Testing, Project Structure, Contributing (link), License (link). Keep existing good content; add what's missing.
- [ ] **Step 3: Create `.env.example`** — copy `env.example`, scrub any real values to placeholders; keep keys only.
- [ ] **Step 4: Commit** — `docs: add README badges, sections, and .env.example`

---

## Phase H — Build & Docker

### Task 15: Makefile

**Files:** Create `Makefile`

- [ ] **Step 1: Create `Makefile`** with `.PHONY` targets: `install` (npm install + pip install -r requirements.txt), `run` (note: starts frontend; backend separate target `run-backend`), `test` (jest + pytest), `test-coverage`, `lint` (next lint + flake8 + black --check), `format` (prettier --write + black + isort), `docker-build`, `docker-run` (docker-compose up), `clean` (rm .next, coverage, __pycache__, .pytest_cache). Include `help` as default target. Add comment that Make requires WSL/Git-Bash on Windows.
- [ ] **Step 2: Verify** — `make help` prints targets (skip on native Windows; rely on CI).
- [ ] **Step 3: Commit** — `chore: add Makefile with dev/test/docker/clean targets`

### Task 16: Docker consolidation

**Files:** Review/modify `Dockerfile`, `docker-compose.yml`, `.dockerignore`

- [ ] **Step 1: Inspect** existing root `Dockerfile` and `docker-compose.yml`. Determine which service the root Dockerfile builds.
- [ ] **Step 2: Ensure root `Dockerfile`** is a multi-stage slim Next.js build (`node:20-alpine` deps → build → runner using `next start` or standalone output). Add inline comments. (Dup Dockerfiles already removed in Task 1.)
- [ ] **Step 3: Ensure `docker-compose.yml`** references the app + postgres/redis stubs with comments; uses `.env`/build args, no hardcoded secrets.
- [ ] **Step 4: Verify** — `docker compose config` parses (skip if docker absent; CI/manual).
- [ ] **Step 5: Commit** — `build: consolidate Dockerfile and refresh docker-compose`

---

## Phase I — Final Verification

### Task 17: Full green verification

- [ ] **Step 1:** `npm install` → succeeds.
- [ ] **Step 2:** `npx jest --coverage` → all green.
- [ ] **Step 3:** Backend: `pip install -r requirements.txt` (or verify already installed) → `python -m pytest backend/tests -v` → all green.
- [ ] **Step 4:** `npx next lint` → no errors (warnings ok); `npx prettier --check` on new files clean; `python -m flake8 backend` clean on touched files; `python -m black --check` on new test files clean.
- [ ] **Step 5:** `npx next build` → succeeds (deployment not broken).
- [ ] **Step 6:** Final commit if any fixups — `chore: final verification fixups`.

---

## Self-Review

- **Spec coverage:** Every spec section maps to a task — Tests (Tasks 4–6), Code quality (2,3,7), CI/CD (8–10), GitHub meta (11), Docs (12–14), Makefile (15), Docker (16), Security/misc (SECURITY in 12, dependabot in 11, LICENSE in 12, CodeQL in 9), Cleanup (1). ✅
- **Placeholder scan:** Test code is concrete; doc/config tasks specify exact required elements. Boilerplate doc bodies are specified by required sections (acceptable — standard content). ✅
- **Type consistency:** Test imports (`cn`, `Card` exports, `IngredientDatabase`) are verified against real source in their tasks before asserting. ✅
- **Risk note:** Backend test assertions and API.md/Dockerfile content depend on inspecting real source first (called out explicitly in Tasks 6, 13, 16).
