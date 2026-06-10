# AGENTS.md template

`/scaffold` distils this into the project's root `AGENTS.md` — the agent-agnostic memory file every coding agent reads. Scaffold also writes a one-line `CLAUDE.md` (containing only `@AGENTS.md`) so Claude Code auto-loads the same content.

Follow the canonical three-section shape — `The Why` / `The What` / `The How`. Every generated `AGENTS.md` uses this structure; only the *content* inside each section changes based on the user's choices. Sections gated on absent components (e.g. "Key TypeScript Design Choices" when frontend-web isn't selected) are omitted entirely, not left empty.

## Composing from this template

**Size target: ≤ 350 lines** (was 300; the extra 50 accommodate the External services block when several stacks are chosen). If AGENTS.md balloons past that, you're copy-pasting specs verbatim instead of distilling. Cut and link out.

**Distil, don't copy.** For each `Key {Lang} Design Choices` section, extract 3–5 headline rules from the relevant spec's "Canonical principles". The *rationale* and canonical examples stay in the spec files; AGENTS.md states the rule and points to the spec for depth.

**Gate sections on component presence.** If `backend` isn't chosen, drop "Key Python Design Choices", "Writing Scripts", "Writing Tests" (unless another language's tests apply), and every Python bullet under the tables. Same for TypeScript and Go. Drop "Shared contracts" bullets when `include_shared_contracts` is false. Drop the whole "Agent Team & Pipeline" section if the user opted out of the agent team. Drop the whole "Documentation Conventions" section if neither `adr` nor `ubiquitous-language` was chosen; otherwise emit only the bullets matching the chosen options. Do not leave empty sections.

**Fill placeholders inline.** The `{...}` braces in the template are *instructions to you* — replace with concrete content from the user's answers and the specs. The `AGENT: fill in` markers inside the rendered AGENTS.md are for the SWE agent to address on the first `/day` run (datastore CLI specifics, orchestrator CLI specifics, etc.) — leave those literal in the output.

## Template

````markdown
# The Why

{One paragraph, first-person-plural if team-built. What this project does, what it produces, who it's for. Pulled straight from the user's project description during the /scaffold interview.}

## Key Principles You Will Respect All Over Your Work

- Always prioritize removing instructions over adding more.

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

*Only emit if `backend` ∈ components. Distil 5 headline rules from [`python-backend.md`](skills/scaffold/specs/python-backend.md) — do NOT copy-paste the spec.*

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
- See the [`testing-python`](skills/testing-python/SKILL.md) skill for depth.

## Key TypeScript Design Choices

*Only emit if `frontend-web` ∈ components. Distil from [`typescript-frontend.md`](skills/scaffold/specs/typescript-frontend.md) + the chosen framework spec (`react-app.md` / `vue-app.md` / `svelte-app.md` / `vanilla-ts-app.md`).*

- Node 20+, `npm` (lockfile `package-lock.json`), Vite bundler, Vitest + jsdom for tests.
- `tsconfig`: `strict: true`, `noUnusedLocals`, `noUnusedParameters`, `noFallthroughCasesInSwitch`, `isolatedModules`, `moduleResolution: "bundler"`.
- One exported component per `.tsx` / `.vue` / `.svelte` file. Tests mirror `src/` 1:1.
- Only `VITE_*` env vars reach the browser bundle — **never** put secrets in them. Component-level `.env.example` lists the public surface.
- Generated OpenAPI client (if applicable) lands at `src/api/` — never hand-edit.

## Key Go Design Choices

*Only emit if `frontend-tui` ∈ components. Distil from [`go-tui.md`](skills/scaffold/specs/go-tui.md).*

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
- **MongoDB** — async ODM (Beanie / PyMongo); `mongosh "$MONGODB_URL"` for local queries. Spec: [`datastore-mongodb`](skills/scaffold/specs/datastore-mongodb.md).
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

## Required MCP Servers, Skills & Plugins

What this project expects connected/enabled in the Claude Code session before `/day` or `/night`. Derive the gated bullets from the step-1 answers; leave the project-specific MCP line as an `AGENT: fill in` placeholder.

{- **`squid` plugin** — supplies the agent team and the `/day` / `/night` / `/scaffold` pipelines, and bundles the `self-improve` skill used below. Install: `/plugin marketplace add iusztinpaul/squid && /plugin install squid@iusztinpaul`. *Only if agent team chosen.*}
{- **`context7` MCP server** — authoritative library/API docs for the tech stack (see [Access Documentation](#access-documentation)). Doc lookups fall back to web search when it isn't connected. *Only if any framework or external service is in the stack.*}
- **Project MCP servers** — *AGENT: fill in any MCP server this project's code talks to (datastore, browser, internal tooling) and the config each needs on first use.*

## Agent Team & Pipeline

*Only emit if agent team + tracker chosen.*

This project ships with an opinionated **agent team workflow** in two modes. The canonical lifecycle and rules live in [`docs/PROCESS.md`](docs/PROCESS.md); read it before invoking either pipeline.

| Role | File | Responsibility |
|---|---|---|
| Product Manager | [`agents/product-manager.md`](agents/product-manager.md) | Grooms tasks; final user-POV acceptance (night mode). |
| Software Engineer | [`agents/software-engineer.md`](agents/software-engineer.md) | Implements code + tests; no commit until Tester PASS. |
| Tester | [`agents/tester.md`](agents/tester.md) | Runs full suite; verifies every AC with evidence. |
| On-Call Engineer | [`agents/oncall-engineer.md`](agents/oncall-engineer.md) | Watches CI after push (night mode). |

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

**Engineering discipline lives in the agent contracts — not here.** TDD-first ordering, branching off the current active branch, running the feature end-to-end before hand-off, regression-test-first for bugs, the PR / review-response loop, and the format/lint/unit-tests/integration-tests cadence are all defined in [`agents/software-engineer.md`](agents/software-engineer.md) and [`agents/tester.md`](agents/tester.md). Read those for the general rules; `/day` and `/night` enforce them automatically.

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
- **ADRs.** Architecture Decision Records live at [`docs/adr/`](docs/adr/) as `NNNN-kebab-title.md`. Every non-obvious architectural choice (datastore, async/sync default, auth boundary, dependency lock-in) ships with one. Use the four-section Nygard template — Status / Context / Decision / Consequences. ADR-0001 ([`docs/adr/0001-record-architecture-decisions.md`](docs/adr/0001-record-architecture-decisions.md)) is already in the repo and explains the convention. Spec depth: [`adr.md`](skills/scaffold/specs/adr.md).

{If `ubiquitous-language` chosen, emit:}
- **Glossary.** The canonical domain vocabulary lives at [`docs/glossary.md`](docs/glossary.md). One canonical name per concept; code identifiers, OpenAPI schemas, database columns, and customer-facing UI all use the term as it appears there. Update the glossary in the same PR that introduces or renames a domain concept — never after. PM grooming and [`/grill-me`](skills/grill-me/SKILL.md) read it as the tie-breaker when specs and code disagree. Spec depth: [`ubiquitous-language.md`](skills/scaffold/specs/ubiquitous-language.md).

## Self Improve

If a `self-improve` skill is available in your Claude Code session, run it at the end of a session to analyse corrections and persist lessons learned into `AGENTS.md` or the memory system.
````
