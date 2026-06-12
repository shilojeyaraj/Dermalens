# 🍒 The Cherry on Top — Professional Repo Setup Prompt

Paste this prompt into Claude (terminal or chat) at the start of any new project to scaffold all the professional-grade infrastructure that FAANG recruiters look for.

---

## 📋 The Prompt

> Copy everything inside the code block below and paste it into Claude.

```
You are a senior software engineer helping me set up a professional, production-grade GitHub repository. 

Here is context about my project:
- Language/Stack: [e.g. Python, Node.js/TypeScript, Java, Go, etc.]
- Project type: [e.g. REST API, CLI tool, web app, data pipeline, ML model, etc.]
- Short description: [one sentence about what this project does]
- Testing framework preference (if any): [e.g. pytest, Jest, JUnit — or just say "your choice"]

Please scaffold the following professional infrastructure for this repo. Generate the actual file contents for each:

---

### 1. 📁 Project Structure
Create a clean, idiomatic folder structure for the stack. Include:
- `src/` or equivalent source directory
- `tests/` with at minimum one example unit test and one integration test stub
- `docs/` folder with placeholder files

---

### 2. 🧪 Testing Infrastructure
- Unit test file(s) with 2–3 real example tests relevant to the project
- Integration test stub
- Test configuration file (e.g. `pytest.ini`, `jest.config.ts`, etc.)
- Code coverage config (e.g. `.coveragerc`, `nyc` config)

---

### 3. ⚙️ CI/CD — GitHub Actions Workflows
Create `.github/workflows/` with the following:

**ci.yml** — runs on every push and pull request to `main`:
- Install dependencies
- Run linter
- Run tests with coverage
- Upload coverage report (Codecov or summary)

**release.yml** — runs on version tags (`v*.*.*`):
- Build the project
- Create a GitHub Release with changelog notes

---

### 4. 🧹 Code Quality Infrastructure
Generate config files for:
- Linter (ESLint / flake8 / golangci-lint / checkstyle — match the stack)
- Formatter (Prettier / Black / gofmt — match the stack)
- `.editorconfig` for cross-editor consistency
- `pre-commit` hooks config (`.pre-commit-config.yaml`) that runs lint + format on commit

---

### 5. 📦 Dependency & Environment Files
- Proper dependency file (`package.json`, `requirements.txt`, `go.mod`, `pom.xml`, etc.)
- `.env.example` with placeholder keys (never real values)
- `.gitignore` tailored to the stack (comprehensive, not minimal)

---

### 6. 🐳 Docker Setup
- `Dockerfile` using a slim/alpine base image, multi-stage if applicable
- `docker-compose.yml` with the app service and any common dependencies (e.g. postgres, redis) as stubs
- `.dockerignore`

---

### 7. 📝 Documentation Files
Generate content for:
- `README.md` — includes: project title, badges (CI status, coverage, license), description, features, tech stack, setup instructions, usage, contributing, license
- `CONTRIBUTING.md` — branching strategy, PR process, commit message format (Conventional Commits)
- `CHANGELOG.md` — starter template following Keep a Changelog format
- `docs/ARCHITECTURE.md` — high-level architecture overview with placeholder diagram section
- `docs/API.md` (if applicable) — endpoint documentation template

---

### 8. 🔧 GitHub-Specific Files
- `.github/pull_request_template.md` — PR checklist (tests written, docs updated, lint passing, etc.)
- `.github/ISSUE_TEMPLATE/bug_report.md`
- `.github/ISSUE_TEMPLATE/feature_request.md`
- `CODEOWNERS` file (placeholder)

---

### 9. 🏷️ Makefile
Create a `Makefile` with the following targets:
- `make install` — install dependencies
- `make run` — run the project locally
- `make test` — run all tests
- `make test-coverage` — run tests with coverage report
- `make lint` — run linter
- `make format` — run formatter
- `make docker-build` — build docker image
- `make docker-run` — run via docker-compose
- `make clean` — remove build artifacts

---

### 10. 🔐 Security & Misc
- `SECURITY.md` — responsible disclosure policy template
- `.github/dependabot.yml` — automated dependency update config
- `LICENSE` — MIT license (or ask me which license to use)

---

After generating all files, give me:
1. A summary tree of every file created
2. The 3 most important things I should customize before pushing
3. The exact git commands to initialize, commit, and push this as a new repo

Use best practices for the specific stack I've described. Prefer industry-standard tools that FAANG engineers would recognize. Add inline comments in config files to explain non-obvious settings.
```

---

## 🔁 Follow-Up Prompts

After the initial scaffold, use these to go deeper:

### Add proper logging
```
Add structured logging to this project using the idiomatic logging library for [stack]. 
Include log levels, request/trace IDs, and a config that outputs JSON in production 
and pretty-prints in development.
```

### Add database layer
```
Add a database integration layer using [Postgres/MySQL/MongoDB]. Include:
- Connection pooling setup
- Migration files/folder structure  
- A repository pattern or DAO layer
- Integration test stubs that use a test database or mock
```

### Harden CI pipeline
```
Improve the GitHub Actions CI pipeline to also include:
- SAST security scanning (e.g. CodeQL or Snyk)
- Dependency vulnerability check
- Docker image build and push to GHCR on merge to main
- Branch protection rule suggestions in comments
```

### Add API documentation
```
Generate OpenAPI 3.0 spec (openapi.yaml) for this project's endpoints, 
and add a docs:serve Makefile target that runs a local Swagger UI.
```

---

## 💡 Tips

- **Fill in the project context fields** at the top of the prompt — the more specific, the better the output.
- Run this **once per new repo**, ideally before writing any feature code.
- Commit the scaffold as an initial `chore: initial project scaffold` commit using Conventional Commits format.
- Pin the repos that use this setup on your GitHub profile — recruiters will see the CI badges immediately.

---

*Generated for use with Claude — paste into claude.ai chat or Claude Code terminal.*
