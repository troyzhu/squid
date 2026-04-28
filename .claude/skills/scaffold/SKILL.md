---
name: scaffold
description: Bootstrap a new polyglot monorepo (or a new component in an existing one) from an opinionated spec library. Asks what to build, picks the relevant specs from specs/, writes a tailored CLAUDE.md, and lays down an empty folder skeleton. TRIGGER when the user says "/scaffold", asks to bootstrap a project, create a new codebase, start a fresh repo, or add a new component. SKIP for work inside an already-scaffolded project — pick /day or /night instead.
disable-model-invocation: false
argument-hint: [optional one-line project description]
---

# Scaffold

Interactive bootstrap for a new repo (or a new component in an existing one).

- Ask the user what they want to build.
- Read only the specs under [`specs/`](specs/) that apply.
- Write a tailored `CLAUDE.md` at the target project root that **distils** those specs (doesn't copy-paste them).
- Lay down an empty folder skeleton (no source code).
- Hand control back — the user runs `/day` next to have the SWE agent write the first code against the generated CLAUDE.md.

## When to use

- Bootstrapping a brand-new repo.
- Adding a new runtime component (backend / frontend-web / frontend-tui) to an existing scaffolded repo.
- Re-generating the root `CLAUDE.md` after a major stack change (e.g. swapping Vue for React).

## When NOT to use

- Writing application source code (that's the SWE agent's job under `/day` or `/night`).
- Filling in business logic, API handlers, components, etc.
- Adjusting opinions inside an existing project — edit the generated `CLAUDE.md` directly.
- Non-polyglot single-package projects where the full machinery is overkill. (You can still use a single spec as reference, but skip the scaffold flow.)

## Flow

### 1. Gather requirements

Use `AskUserQuestion` to collect answers. Consolidate where possible — one or two prompts, not a twelve-step interview. Minimum set:

1. **Project identity** — name, short description, license (MIT / Apache-2.0 / proprietary). Name becomes the repo / root CLAUDE.md title; slug is derived.
2. **Layout** — monorepo (`packages/<c>/` tree) or standalone single-package?
3. **Components** (multi-select; at least one required):
   - `backend` — Python service / pipeline / library
   - `frontend-web` — TypeScript browser SPA
   - `frontend-tui` — Go terminal UI
4. **Backend variant** (if backend chosen): `fastapi-service` / `fastmcp-server` / `cli-tool-python` / `library-only`.
5. **Frontend-web framework** (if frontend-web chosen): `react` / `vue` / `svelte` / `vanilla`.
6. **Frontend-tui framework** (if frontend-tui chosen): `bubbletea` (default) / `tview`.
7. **Shared OpenAPI contracts** (only if backend + ≥1 frontend): yes / no.
8. **Infra** (multi-select): `docker`, `github-actions`, `pre-commit-hooks`.
9. **Agent team + tracker?** yes (recommended) / no. Also: file-based tracker or GitHub Issues?
10. **Process & documentation** (multi-select, optional): `adr` (Architecture Decision Records under `docs/adr/`), `ubiquitous-language` (project glossary at `docs/glossary.md`). Recommend `adr` for any project expected to live > 6 months; recommend `ubiquitous-language` for backend services with named domain entities.
11. **External services** (optional, multi-select — skip any category that doesn't apply). Each selection pulls a `specs/<category>-<choice>.md` stub and emits a one-line bullet into the generated CLAUDE.md, wrapped in `<!-- stack:<slug> -->` comments so the user can find-and-delete it later:
   - **Datastore:** `mongodb` / `postgresql` / `redis` / `sqlite` / `other` / `none`
   - **Orchestrator:** `prefect` / `dagster` / `temporal` / `other` / `none`
   - **Observability & evals:** `opik` / `opentelemetry` / `sentry` / `other` / `none`
   - **LLM API:** `anthropic` / `openai` / `gemini` / `other` / `none`
   - **Embedding API:** `voyageai` / `openai` / `sentence-transformers` / `other` / `none`
   - **Model serving:** `modal` / `replicate` / `other` / `none`
   - **Web scraping:** `firecrawl` / `playwright` / `requests-bs4` / `other` / `none`

   Ask this as ONE consolidated question: "Which external services will you use? (deselect anything you don't need)." `none` skips the category entirely — no stub read, no bullet emitted. `other` keeps an `AGENT: fill in` placeholder so the SWE can document the real choice on first use.

Before proceeding to step 2, echo the picked configuration back to the user in a two-line summary and confirm.

### 2. Select specs

Always include:

- [`monorepo-layout.md`](specs/monorepo-layout.md) — unless the user chose standalone single-package.
- [`makefile-delegator.md`](specs/makefile-delegator.md) — unless standalone.

Conditionally include (from answers):

| Answer | Specs to read |
|---|---|
| `backend` (any variant) | [`python-backend.md`](specs/python-backend.md) + [`uv-python.md`](specs/uv-python.md) + [`pyproject.md`](specs/pyproject.md) + [`ruff-python.md`](specs/ruff-python.md) |
| backend = `fastapi-service` | + [`fastapi-service.md`](specs/fastapi-service.md) |
| backend = `fastmcp-server` | + [`fastmcp-server.md`](specs/fastmcp-server.md) |
| backend = `cli-tool-python` | + [`cli-tool-python.md`](specs/cli-tool-python.md) |
| `frontend-web` | [`typescript-frontend.md`](specs/typescript-frontend.md) + the chosen framework spec ([`react-app.md`](specs/react-app.md) / [`vue-app.md`](specs/vue-app.md) / [`svelte-app.md`](specs/svelte-app.md) / [`vanilla-ts-app.md`](specs/vanilla-ts-app.md)) |
| `frontend-tui` | [`go-tui.md`](specs/go-tui.md) (already covers both bubbletea and tview) |
| shared OpenAPI contracts | [`openapi-contracts.md`](specs/openapi-contracts.md) |
| docker | [`docker.md`](specs/docker.md) |
| github-actions | [`github-actions.md`](specs/github-actions.md) |
| pre-commit-hooks | [`pre-commit-hooks.md`](specs/pre-commit-hooks.md) |
| agent team + tracker | [`tracker-workflow.md`](specs/tracker-workflow.md) |
| process: `adr` | [`adr.md`](specs/adr.md) |
| process: `ubiquitous-language` | [`ubiquitous-language.md`](specs/ubiquitous-language.md) |
| datastore = `mongodb` / `postgresql` / `redis` / `sqlite` | + [`datastore-<choice>.md`](specs/) |
| orchestrator = `prefect` / `dagster` / `temporal` | + [`orchestrator-<choice>.md`](specs/) |
| observability = `opik` / `opentelemetry` / `sentry` | + [`observability-<choice>.md`](specs/) |
| llm-api = `anthropic` / `openai` / `gemini` | + [`llm-<choice>.md`](specs/) |
| embeddings = `voyageai` / `openai` / `sentence-transformers` | + [`embeddings-<choice>.md`](specs/) |
| model-serving = `modal` / `replicate` | + [`model-serving-<choice>.md`](specs/) |
| scraping = `firecrawl` / `playwright` / `requests-bs4` | + [`scraping-<choice>.md`](specs/) |

Skip any row where the user picked `none` / `other`. `other` is handled at compose time by leaving an `AGENT: fill in` placeholder in the generated CLAUDE.md.

`Read` each selected spec end-to-end. Specs are short markdown — full read is fine. Skip reading specs that don't apply; keep context lean.

### 3. Compose `CLAUDE.md`

Write a single `CLAUDE.md` at the target project root (or wherever `/scaffold` was invoked). **Follow the canonical three-section template below — `The Why` / `The What` / `The How`.** Every generated CLAUDE.md uses this structure; only the *content* inside each section changes based on the user's choices. Sections gated on absent components (e.g. "Key TypeScript Design Choices" when frontend-web isn't selected) are omitted entirely, not left empty.

```markdown
# The Why

{One paragraph, first-person-plural if team-built. What this project does, what it produces, who it's for. Pulled straight from the user's project description during the /scaffold interview.}

# The What

## Key Components

{One bullet per enabled component, linking into its package directory. 1–2 sentences per bullet stating the component's role. Example shape:}

- **Backend:** [`packages/backend/`](packages/backend/) — {chosen Python variant: FastAPI HTTP API / FastMCP MCP server / CLI tool / library-only}. {One-line purpose from user input.}
- **Web frontend:** [`packages/frontend-web/`](packages/frontend-web/) — {chosen framework} SPA. {One-line purpose.}
- **TUI frontend:** [`packages/frontend-tui/`](packages/frontend-tui/) — {chosen framework: bubbletea / tview} terminal UI.
- **Shared contracts:** [`packages/shared/`](packages/shared/) — OpenAPI 3.1 spec + per-language codegen. *Only if shared chosen.*

## Project Structure

{ASCII tree pulled from `monorepo-layout.md`, trimmed to the chosen components. Include tracker/ and docs/PROCESS.md when agent team is chosen.}

## Key Python Design Choices

*Only emit if `backend` ∈ components. Distil 5 headline rules from [`python-backend.md`](.claude/skills/scaffold/specs/python-backend.md) — do NOT copy-paste the spec.*

- Python 3.12+ minimum; async for I/O-bound work, sync for CPU.
- Loose clean architecture — `entities/` for shared ODM/Pydantic models and enums; per-module `types.py` for narrow types used only within that module or layers upward.
- Flat structure by actionable concern (`ingestion/`, `serving/`) — not dogmatic clean-arch layers.
- Infrastructure dependencies (DB, orchestrator, observability) are **imported directly, not abstracted**. No premature interfaces.
- Pipelines: idempotent, retryable, checkpointed. Datetimes: timezone-aware, UTC by default. Types: annotate everything including `-> None`.

### Writing Scripts

Every entry-point module in `scripts/` calls `init_logger()` (or the project's logging bootstrap) at module level **before any logic or project import**. Never `print()` in library code — use the project logger.

### Writing Tests

- `tests/` mirrors `src/` 1:1. Files `test_*.py`, functions `test_*`. AAA pattern.
- Shared fixtures in `conftest.py`; no manual setup/teardown.
- Mocking via `pytest-mock` (`mocker`), never hand-rolled.
- `@pytest.mark.parametrize` for table tests.
- **Zero warnings.** `filterwarnings = ["error"]` in pytest config.
- **AVOID** unit-testing infrastructure components (orchestrator adapters, model-serving runtime, observability client) — those belong in integration tests only.
- See the [`testing-python`](.claude/skills/testing-python/SKILL.md) skill for depth.

## Key TypeScript Design Choices

*Only emit if `frontend-web` ∈ components. Distil from [`typescript-frontend.md`](.claude/skills/scaffold/specs/typescript-frontend.md) + the chosen framework spec (`react-app.md` / `vue-app.md` / `svelte-app.md` / `vanilla-ts-app.md`).*

- Node 20+, `npm` (lockfile `package-lock.json`), Vite bundler, Vitest + jsdom for tests.
- `tsconfig`: `strict: true`, `noUnusedLocals`, `noUnusedParameters`, `noFallthroughCasesInSwitch`, `isolatedModules`, `moduleResolution: "bundler"`.
- One exported component per `.tsx` / `.vue` / `.svelte` file. Tests mirror `src/` 1:1.
- Only `VITE_*` env vars reach the browser bundle — **never** put secrets in them. Component-level `.env.example` lists the public surface.
- Generated OpenAPI client (if applicable) lands at `src/api/` — never hand-edit.

## Key Go Design Choices

*Only emit if `frontend-tui` ∈ components. Distil from [`go-tui.md`](.claude/skills/scaffold/specs/go-tui.md).*

- Go 1.22+, `gofmt` authoritative, `go vet ./...` for lint, stdlib `testing`.
- `cmd/<slug>/main.go` is thin — wires the framework, calls `run()`. `internal/` holds ~95% of code; `pkg/` only for externally importable API.
- Tests co-located (`foo.go` + `foo_test.go` in the same package); co-location lets tests reach unexported identifiers.
- Pin exact dependency versions in `go.mod` so `go mod tidy` is deterministic.
- TUIs are **not** containerised for dev — they need a real TTY. Use `goreleaser` or a CI build step for reproducible binaries.

## Tech Stack

Multi-language — each component brings its own toolchain:

{- **Python 3.12+** (backend) — `uv`, `ruff`, `pytest`.}
{- **Node.js 20+** (frontend-web) — `npm`, `vite`, `vitest`, `eslint` 9, `prettier` 3.}
{- **Go 1.22+** (frontend-tui) — `go mod`, `gofmt`, `go test`.}
{- **OpenAPI 3.1 + codegen** (shared) — `openapi-spec-validator`, `openapi-python-client`, `@openapitools/openapi-generator-cli`, `oapi-codegen`.}

### External services

*For each external-service slug the user selected in step 1, emit one bullet here wrapped in `<!-- stack:<slug> -->` / `<!-- /stack:<slug> -->` HTML comments. Pull the one-line summary from the spec's frontmatter `description` (distil if too long). Slug = short tool name; disambiguate where the same name appears in multiple categories (`openai-llm`, `openai-embeddings`). Emit nothing for categories the user left as `none`. Use the `other` pattern below when the user picked `other` for a category. Post-scaffold, the user can grep `<!-- stack:` to find any block and delete it.*

Example (MongoDB selected):

```
<!-- stack:mongodb -->
- **MongoDB** — async ODM (Beanie / PyMongo); `mongosh "$MONGODB_URL"` for local queries. Spec: [`datastore-mongodb`](.claude/skills/scaffold/specs/datastore-mongodb.md).
<!-- /stack:mongodb -->
```

Example (user picked `other` for datastore):

```
<!-- stack:other-datastore -->
- **{Datastore — other}** — *AGENT: fill in client CLI and connection details on first use.*
<!-- /stack:other-datastore -->
```

### Access Documentation

Use the `context7` MCP server (when available in the Claude Code session) to look up authoritative usage and best practices for any of the above tech-stack items.

# The How

All core commands live in the [`Makefile`](Makefile). Prefer `make <target>` over ad-hoc shell invocations.

Per-component dependency managers:
{- `uv` for Python (`packages/backend/`).}
{- `npm` for TypeScript (`packages/frontend-web/`).}
{- `go mod` for Go (`packages/frontend-tui/`).}

## Agent Team & Pipeline

*Only emit if agent team + tracker chosen.*

This project ships with an opinionated **agent team workflow** in two modes. The canonical lifecycle and rules live in [`docs/PROCESS.md`](docs/PROCESS.md); read it before invoking either pipeline.

| Role | File | Responsibility |
|---|---|---|
| Product Manager | [`.claude/agents/product-manager.md`](.claude/agents/product-manager.md) | Grooms tasks; final user-POV acceptance (night mode). |
| Software Engineer | [`.claude/agents/software-engineer.md`](.claude/agents/software-engineer.md) | Implements code + tests; no commit until Tester PASS. |
| Tester | [`.claude/agents/tester.md`](.claude/agents/tester.md) | Runs full suite; verifies every AC with evidence. |
| On-Call Engineer | [`.claude/agents/oncall-engineer.md`](.claude/agents/oncall-engineer.md) | Watches CI after push (night mode). |

**Entry points:**

- **`/night [batch-size]`** — unattended batch pipeline (default 2). Full PM groom → SWE → Tester → PM accept → Commit → On-Call CI.
- **`/day [task]`** — supervised single-task pipeline. SWE → Tester → you commit.

**Tracker:** file-based by default — see [`tracker/README.md`](tracker/README.md). Switch to GitHub Issues via `TRACKER_MODE` at the top of [`docs/PROCESS.md`](docs/PROCESS.md).

**When to use which workflow:**

- **Direct chat** — trivial edits, one-shot questions, typos.
- **`/day`** — a single feature, bug fix, or refactor you want to ship under active supervision with a Tester gate.
- **`/night`** — multi-task batches, unattended runs, anything where you want both PM gates plus On-Call enforced.

## Developing New Features and Bug Fixes Workflow

Direct chat is for trivial edits and one-shot questions. For anything that needs a test gate, use `/day`; for unattended batches, use `/night`.

**Engineering discipline lives in the agent contracts — not here.** TDD-first ordering, branching off the current active branch, running the feature end-to-end before hand-off, regression-test-first for bugs, the PR / review-response loop, and the format/lint/unit-tests/integration-tests cadence are all defined in [`.claude/agents/software-engineer.md`](.claude/agents/software-engineer.md) and [`.claude/agents/tester.md`](.claude/agents/tester.md). Read those for the general rules; `/day` and `/night` enforce them automatically.

Project-specific invariants the agents can't fully own:

- **Dependencies:** add to the **component-specific** manifest — {`packages/backend/pyproject.toml`}{, `packages/frontend-web/package.json`}{, `packages/frontend-tui/go.mod`}. Never mix languages' deps.
- **New env vars:** update the **component's** `.env.example` + the component's config module. Cross-cutting secrets go in the **root** `.env.example` and are documented there.
{- **New shared contracts:** edit `packages/shared/openapi/api.yaml` and run `make openapi-gen` to regenerate clients. **Never hand-edit** generated client files (`packages/frontend-web/src/api/`, `packages/frontend-tui/internal/api/client.go`, `packages/backend/src/<pkg>/generated_client/`).}

## Step-by-Step Verification Steps

Standard per-atomic-change verification (format/lint, pre-commit, unit tests, running the feature end-to-end, integration tests pre-PR) is defined in the SWE and Tester agent contracts and runs automatically under `/day` and `/night`.

Project-specific additions:

{- **Editing the OpenAPI spec:** run `make openapi-validate && make openapi-gen` and confirm the generated clients compile.}
{- **Editing the root `Makefile` or adding a component:** run `make help` to confirm the target surface is coherent and every per-component verb is wired.}
{- **Editing `docker-compose.yml`:** run `make docker-up` then `docker compose ps` — every service should be `healthy` within 30s.}
{- **Editing an orchestrator-driven pipeline:** serve the worker in the background (`make serve-workflows &`), then trigger via a wrapped `make run-<pipeline>` so logs stream to the current terminal. Re-serve after code changes — running workers don't auto-reload.}

## Build

```
make build
```

Builds every enabled component's deployable artifact. For a single component: `make build-<component>`.

## Running QA and Tests

Every verb runs at repo root. The root Makefile **delegates** to `packages/<c>/Makefile` via `$(MAKE) -C packages/<c> <verb>`; it never reimplements per-component logic. Each component owns its own toolchain (`uv` / `npm` / `go`).

### Aggregate (every enabled component)

| Target | What it does |
|---|---|
| `make install` | Install/refresh every component's deps. |
| `make test` | Run every component's test suite. |
{| `make unit-tests` | Backend unit tests only. |}
{| `make integration-tests` | Backend integration tests only. |}
| `make lint-check` / `make lint-fix` | Static checks / auto-fix. |
| `make format-check` / `make format-fix` | Formatting check / apply. |
| `make pre-commit` | `format-check + lint-check + light tests`. |
| `make build` | Build every deployable artifact. |
| `make ci` | Full pre-PR fan: `install → test → lint-check → format-check → pre-commit → build`. |
| `make help` | Curated target list with descriptions. |

> **Manual QA order:** `format-fix → lint-fix → format-check → lint-check → pre-commit → unit-tests`. Fixers before checkers so auto-fixable issues don't surface as false failures. CI runs the non-fix variants only.

### Per-component (fast inner loop)

Every aggregate verb has a `-<component>` form: `make test-backend`, `make lint-fix-frontend-web`, `make format-check-frontend-tui`, etc. Use these during active work on a single component to skip the fan-out cost.

### Component-specific

{- `make dev-frontend-web` — Vite dev server.}
{- `make run-frontend-tui` — `go run ./cmd/<slug>`.}
{- `make openapi-gen` / `make openapi-validate` — regen clients / validate spec (shared contracts).}
{- `make docker-up` / `make docker-down` — local compose stack.}

Every command uses `$(MAKE) -C` under the hood — **never literal `make`** — so `-j`, variable overrides, and recursion tracking propagate cleanly.

## Running Custom Commands for Project-Level Dependencies

For any command not wrapped by the Makefile:

{- **Python (backend):** `uv run python ...`, `uv run pytest ...`, `uv run ruff ...`, `uvx <one-shot-tool>` (e.g. `uvx openapi-spec-validator`). From the repo root without `cd`: `uv --directory packages/<c> run ...`.}
{- **TypeScript (frontend-web):** `npm run <script>`, `npx <one-shot-tool>`.}
{- **Go (frontend-tui):** `go run ./cmd/<slug>`, `go test ./...`, `go run <module>@<version>` for one-shot tools.}

## Running Custom Commands for Accessing Infrastructure and External Services

External CLIs used during development:

- **Git:** `git` for generic VCS operations.
- **GitHub:** `gh` for PRs, issues, Actions logs.
{- **Docker:** `docker compose up -d`, `docker compose down`, `docker compose logs -f <svc>`.}

External-service CLIs (datastore, orchestrator, observability, LLM, embedding, serving, scraping) are documented per-service in [**Tech Stack › External services**](#external-services) above — each `<!-- stack:<slug> -->` block there includes its invocation. Delete a block to drop the service from the project.

## Documentation Conventions

*Only emit if `adr` and/or `ubiquitous-language` were chosen in step 1.*

{If `adr` chosen, emit:}
- **ADRs.** Architecture Decision Records live at [`docs/adr/`](docs/adr/) as `NNNN-kebab-title.md`. Every non-obvious architectural choice (datastore, async/sync default, auth boundary, dependency lock-in) ships with one. Use the four-section Nygard template — Status / Context / Decision / Consequences. ADR-0001 ([`docs/adr/0001-record-architecture-decisions.md`](docs/adr/0001-record-architecture-decisions.md)) is already in the repo and explains the convention. Spec depth: [`adr.md`](.claude/skills/scaffold/specs/adr.md).

{If `ubiquitous-language` chosen, emit:}
- **Glossary.** The canonical domain vocabulary lives at [`docs/glossary.md`](docs/glossary.md). One canonical name per concept; code identifiers, OpenAPI schemas, database columns, and customer-facing UI all use the term as it appears there. Update the glossary in the same PR that introduces or renames a domain concept — never after. PM grooming and [`/grill-me`](.claude/skills/grill-me/SKILL.md) read it as the tie-breaker when specs and code disagree. Spec depth: [`ubiquitous-language.md`](.claude/skills/scaffold/specs/ubiquitous-language.md).

## Self Improve

If a `self-improve` skill is available in your Claude Code session, run it at the end of a session to analyse corrections and persist lessons learned into `CLAUDE.md` or the memory system.
```

**Size target: ≤ 350 lines** (was 300; the extra 50 accommodate the External services block when several stacks are chosen). If CLAUDE.md balloons past that, you're copy-pasting specs verbatim instead of distilling. Cut and link out.

**Distil, don't copy.** For each `Key {Lang} Design Choices` section, extract 3–5 headline rules from the relevant spec's "Canonical principles". The *rationale* and canonical examples stay in the spec files; CLAUDE.md states the rule and points to the spec for depth.

**Gate sections on component presence.** If `backend` isn't chosen, drop "Key Python Design Choices", "Writing Scripts", "Writing Tests" (unless another language's tests apply), and every Python bullet under the tables. Same for TypeScript and Go. Drop "Shared contracts" bullets when `include_shared_contracts` is false. Drop the whole "Agent Team & Pipeline" section if the user opted out of the agent team. Drop the whole "Documentation Conventions" section if neither `adr` nor `ubiquitous-language` was chosen; otherwise emit only the bullets matching the chosen options. Do not leave empty sections.

**Fill placeholders inline.** The `{...}` braces in the template are *instructions to you* — replace with concrete content from the user's answers and the specs. The `AGENT: fill in` markers inside the rendered CLAUDE.md are for the SWE agent to address on the first `/day` run (datastore CLI specifics, orchestrator CLI specifics, etc.) — leave those literal in the output.

### 4. Create the folder skeleton

Create these files / directories, **empty or with minimal placeholders**. Do NOT write application source.

Always:

- `CLAUDE.md` — from step 3.
- `README.md` — one-paragraph project-facing intro pointing at `CLAUDE.md`.
- `.gitignore` — language-appropriate (`.venv/`, `node_modules/`, `dist/`, `bin/`, `.DS_Store`, `.env`).
- `.env.example` — cross-cutting placeholder keys (one commented sample var).

If monorepo:

- **Root `Makefile`** — delegator, generated dynamically from the chosen components per [`makefile-delegator.md`](specs/makefile-delegator.md). For every enabled component, emit:
  - The standard verb set (each present as both aggregate and per-component form):
    - `install`, `test`, `lint-check`, `lint-fix`, `format-check`, `format-fix`, `pre-commit`, `build`
  - Backend-only extras (if `backend` in components): `unit-tests`, `integration-tests`.
  - Frontend-web extras (if `frontend-web` in components): `dev`.
  - Frontend-tui extras (if `frontend-tui` in components): `run`.
  - Cross-cutting verbs (if applicable): `openapi-gen`, `openapi-validate` (shared chosen), `docker-up`, `docker-down` (docker chosen), `ci` (always), `help` (always).
  - `.PHONY` list built dynamically from emitted verbs (never hardcoded).
  - `help` target that echoes the enabled-component summary + the curated target list.
  - Component-gating: use `HAS_<component> := $(shell test -d packages/<c> && echo yes)` and gate targets via `$(if $(HAS_<X>), <target>)` — so `make test` on a backend-only render doesn't try to run `test-frontend-web`.
  - Every recipe is `$(MAKE) -C packages/<c> <verb>` — **never** a literal `make` or a `cd` chain.

- **Per-component `packages/<c>/Makefile`** — implements the verb set in the chosen language's tooling. Use the canonical sketches from [`makefile-delegator.md`](specs/makefile-delegator.md):
  - **Python backend:** `uv sync`, `uv run pytest`, `uv run ruff check`, `uv run ruff format`, `uv build`.
  - **TypeScript frontend-web:** `npm ci`, `npm run test`, `npm run lint`, `npm run format`, `npm run build`.
  - **Go frontend-tui:** `go mod tidy`, `go test ./...`, `go vet ./...`, `gofmt -l/-w`, `go build`.
  - **Shared OpenAPI:** `uvx openapi-spec-validator`, `uvx openapi-python-client`, `@openapitools/openapi-generator-cli`, `oapi-codegen`.
  - Scaffold writes a **working first-pass Makefile** per component (not `AGENT: fill in` stubs) — the verbs are mechanical, the tooling is standard per language, and having `make install` work out-of-the-box on the fresh scaffold lets the user run `make install && make test` before any SWE work. Real-code placeholders still apply to `src/`, not to the Makefile.

- Each `packages/<c>/` also gets:
  - `CLAUDE.md` — one-paragraph component brief + "see root CLAUDE.md for conventions".
  - `.env.example` — component-local placeholder.
  - *No source files.* (Those are SWE agent's job on first `/day` run.)

- If shared OpenAPI chosen: `packages/shared/openapi/api.yaml` with a minimal `/health` endpoint seed.

If docker chosen:

- `docker-compose.yml` — one service block per runtime component with `AGENT: fill in` placeholders for image / ports / healthcheck.
- Component-level `Dockerfile` stub with `AGENT: fill in` multi-stage build.

If github-actions chosen:

- `.github/workflows/ci.yml` — umbrella workflow with `dorny/paths-filter` routing.
- `.github/workflows/ci-<c>.yml` — one reusable workflow stub per component.
- `.github/dependabot.yml` — one ecosystem per component.

If agent team + tracker chosen:

- `docs/PROCESS.md` — copy from the plugin (same file).
- `tracker/README.md` + `tracker/done/.gitkeep`.
- `.claude/` — only if the user isn't installing the plugin globally; otherwise skip (the plugin provides it).

If `adr` chosen (Process & documentation):

- `docs/adr/0001-record-architecture-decisions.md` — drop the canonical ADR-0001 boilerplate verbatim from [`adr.md`'s Bootstrap section](specs/adr.md), with `{YYYY-MM-DD}` replaced by today's date. This is the only ADR scaffold writes — subsequent ADRs are authored by the SWE / PR Reviewer / `/architecture-review` flow as decisions arise. Do **not** emit a `docs/adr/.gitkeep` (ADR-0001 already keeps the directory non-empty).

If `ubiquitous-language` chosen (Process & documentation):

- `docs/glossary.md` — minimal seed: a one-paragraph header declaring the discipline ("The canonical vocabulary for {project}. When code, docs, specs, or conversation use a domain concept, use the term as it appears here.") + an empty 3-column table (`| Term | Definition | Notes |`) with a single commented-out example row so the format is unambiguous. Do **not** invent domain terms — the SWE / PM agent populate it as the first feature lands. Recommended seed body:

  ```markdown
  # Glossary

  The canonical vocabulary for {project name}. When code, docs, specs, or conversation use a domain concept, use the term as it appears here. PRs that introduce or rename a domain concept update this file in the same change.

  | Term | Definition | Notes |
  |---|---|---|
  <!-- | **OrderLine** | One line item within an Order, identified by `order_line_id`. | Distinct from "Item" (the catalogue entry). | -->
  ```

### 5. Report back

Summarise for the user:

- File tree created (full list, relative paths).
- Which specs informed the CLAUDE.md (named).
- **Exact next step** — e.g. `/day "bootstrap packages/backend with a minimal FastAPI app and a /health endpoint"`. The SWE agent will read CLAUDE.md and the spec references, and write the first real code.

## Rules

- **Never write application source.** Not `main.py`, not `App.tsx`, not `cmd/<slug>/main.go`. Only structural / configuration files with AGENT-fill-in placeholders.
- **Distil, don't transclude.** CLAUDE.md cites specs; it doesn't reproduce them.
- **Stop and ask on conflicts.** If the user picks `cli-tool-python` and `fastapi-service` for the same backend, ask which one (they can always run `/scaffold` again to add the other).
- **Don't overwrite without confirmation.** If the target dir already has a `CLAUDE.md` or a `packages/<c>/` for a chosen component, ask before clobbering.
- **Don't mutate the spec library.** `specs/` is read-only at scaffold time. Edits happen on the plugin repo, not in a consumer project.
- **Stack stubs are optional and deletable.** The `datastore-*`, `orchestrator-*`, `observability-*`, `llm-*`, `embeddings-*`, `model-serving-*`, `scraping-*` files are all stubs pending real-project use. If a category turns out not to be worth maintaining, delete the stub(s) in plugin-repo edits and drop the matching row in Step 2's decision table — nothing else references them.

## Index of specs

The spec library lives at [`specs/`](specs/). Each file is a standalone reference doc describing *opinions*, not *code*. Grouped by role:

**Layout & tooling (foundational)**
- [`monorepo-layout.md`](specs/monorepo-layout.md) — polyglot monorepo tree + component boundaries.
- [`makefile-delegator.md`](specs/makefile-delegator.md) — root Makefile pattern + canonical example.

**Python**
- [`python-backend.md`](specs/python-backend.md) — layout, discipline, testing conventions.
- [`uv-python.md`](specs/uv-python.md) — uv usage (add / sync / run / build / publish).
- [`pyproject.md`](specs/pyproject.md) — `pyproject.toml` structure + canonical example.
- [`ruff-python.md`](specs/ruff-python.md) — ruff configuration opinions.

**Python project types**
- [`fastapi-service.md`](specs/fastapi-service.md) — FastAPI app factory, lifespan, endpoints.
- [`fastmcp-server.md`](specs/fastmcp-server.md) — FastMCP server shape.
- [`cli-tool-python.md`](specs/cli-tool-python.md) — typer/click CLI conventions.

**TypeScript frontend**
- [`typescript-frontend.md`](specs/typescript-frontend.md) — package layout + canonical configs.
- [`react-app.md`](specs/react-app.md) — React SPA specifics.
- [`vue-app.md`](specs/vue-app.md) — Vue SPA specifics.
- [`svelte-app.md`](specs/svelte-app.md) — Svelte SPA specifics.
- [`vanilla-ts-app.md`](specs/vanilla-ts-app.md) — no-framework TypeScript SPA.

**Go TUI**
- [`go-tui.md`](specs/go-tui.md) — layout, Bubbletea, and tview in one doc.

**Infrastructure**
- [`docker.md`](specs/docker.md) — slim Dockerfile + docker-compose opinions.
- [`github-actions.md`](specs/github-actions.md) — monorepo CI patterns.
- [`openapi-contracts.md`](specs/openapi-contracts.md) — contract-first OpenAPI 3.1 workflow.
- [`pre-commit-hooks.md`](specs/pre-commit-hooks.md) — project-side hook conventions (`pre-commit` / `lefthook` / `husky`), what runs in `pre-commit` vs `pre-push`, escape-hatch policy.

**Process & documentation**
- [`tracker-workflow.md`](specs/tracker-workflow.md) — file-based task tracker format.
- [`adr.md`](specs/adr.md) — Architecture Decision Records (`docs/adr/NNNN-title.md`), Nygard template, status lifecycle.
- [`ubiquitous-language.md`](specs/ubiquitous-language.md) — project glossary at `docs/glossary.md`; one canonical name per domain concept.

**External services** *(all stubs — flesh out as real projects reveal opinions; delete any category or file you decide isn't worth maintaining, and drop the matching row in Step 2's decision table)*
- Datastore: [`datastore-mongodb.md`](specs/datastore-mongodb.md), [`datastore-postgresql.md`](specs/datastore-postgresql.md), [`datastore-redis.md`](specs/datastore-redis.md), [`datastore-sqlite.md`](specs/datastore-sqlite.md).
- Orchestrator: [`orchestrator-prefect.md`](specs/orchestrator-prefect.md), [`orchestrator-dagster.md`](specs/orchestrator-dagster.md), [`orchestrator-temporal.md`](specs/orchestrator-temporal.md).
- Observability: [`observability-opik.md`](specs/observability-opik.md), [`observability-opentelemetry.md`](specs/observability-opentelemetry.md), [`observability-sentry.md`](specs/observability-sentry.md).
- LLM API: [`llm-anthropic.md`](specs/llm-anthropic.md), [`llm-openai.md`](specs/llm-openai.md), [`llm-gemini.md`](specs/llm-gemini.md).
- Embeddings: [`embeddings-voyageai.md`](specs/embeddings-voyageai.md), [`embeddings-openai.md`](specs/embeddings-openai.md), [`embeddings-sentence-transformers.md`](specs/embeddings-sentence-transformers.md).
- Model serving: [`model-serving-modal.md`](specs/model-serving-modal.md), [`model-serving-replicate.md`](specs/model-serving-replicate.md).
- Scraping: [`scraping-firecrawl.md`](specs/scraping-firecrawl.md), [`scraping-playwright.md`](specs/scraping-playwright.md), [`scraping-requests-bs4.md`](specs/scraping-requests-bs4.md).
