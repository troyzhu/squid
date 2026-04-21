# Engineering Agent Team

A [Claude Code](https://claude.com/claude-code) plugin that installs an opinionated **agent team** plus a `/scaffold` bootstrap flow into any repo — so Claude builds software the way *this* team builds it.

No file templates. No rendering step. The plugin is markdown specs and agent contracts; every file in your project gets written by an agent that reads those specs and follows them.

## What you get

After `/plugin install`, in any repo:

| Surface | What it does |
|---|---|
| `/scaffold` | Interactive bootstrap. Asks what you're building (backend / frontend / TUI / mix), reads the relevant specs, writes a tailored `CLAUDE.md`, and lays down an empty folder skeleton. Run `/day` next to have the agents fill it in. |
| `/day <task>` | Single-task supervised pipeline. `SWE implements → Tester verifies → you review + commit`. Use during active work. |
| `/night [batch-size]` | Unattended batched pipeline. `PM grooms → SWE → Tester → PM accepts → Commit → On-Call watches CI`. Use for overnight backlog runs. |
| `product-manager`, `software-engineer`, `tester`, `oncall-engineer` | Sub-agents invoked by the pipelines. Also available for direct use via the `Agent` tool. |
| `testing-python`, `create-pr`, `self-improve` | Support skills referenced by the pipelines and agents. |

The `/scaffold` spec library (under `.claude/skills/scaffold/specs/`) covers:

- **Python:** backend layout, uv, pyproject, ruff, FastAPI, FastMCP, CLI tools
- **TypeScript frontend:** package/tsconfig/vite conventions, React, Vue, Svelte, vanilla
- **Go TUI:** layout + Bubbletea / tview patterns
- **Infra:** Docker, docker-compose, GitHub Actions monorepo CI, OpenAPI contracts
- **Process:** monorepo layout, Makefile delegator, tracker workflow

Several specs are still stubs — first-pass content is in place for the foundations (`python-backend`, `typescript-frontend`, `go-tui`, `uv-python`, `pyproject`, `makefile-delegator`, `monorepo-layout`); others will be fleshed out as they're used.

## Install

**From GitHub:**

```
/plugin install iusztinpaul/engineering-agent-team
```

**From a local clone (for plugin development):**

```
/plugin install /path/to/engineering-agent-team
```

After install, the agents and skills appear in `/agents` and `/help` in any Claude Code session.

## Quick start

In an empty directory:

```
/scaffold
```

The skill asks what you want to build (components, frameworks, infra, license) and writes:

- `CLAUDE.md` — project brief distilled from the relevant specs
- Skeleton `packages/<component>/` directories with placeholder Makefiles and component-level `CLAUDE.md`s
- Root `Makefile`, `.env.example`, `.gitignore`
- Optional: `docker-compose.yml`, `.github/workflows/`, `docs/PROCESS.md` + `tracker/`

It does **not** write application source. That's the next step:

```
/day "Bootstrap packages/backend with a FastAPI /health endpoint and one unit test."
```

The SWE agent reads `CLAUDE.md`, picks up the specs it references, writes real code + tests, hands off to the Tester, and returns an uncommitted diff for you to review and commit.

## Philosophy

- **Specs over templates.** Opinions live as markdown the agent reads; no Jinja, no render step, no drift between a template and what the agent produces.
- **Progressive disclosure.** A session loads only the skills whose descriptions match the task. The spec library under `scaffold/specs/` is gated behind `/scaffold` — it doesn't pollute every session's index.
- **One skill per concern.** Six skills, twenty specs. Adding a new stack is one markdown file, not a new scaffolding engine.
- **The CLAUDE.md is the brief.** After `/scaffold`, the generated `CLAUDE.md` is the single source of truth for how that project builds. Specs are referenced, not transcluded.
- **Agents are gates.** PM catches scope drift. Tester catches false-confidence "tests pass" claims. On-Call catches CI breakage. No agent writes code and also decides whether the code is correct.

## Repo layout (plugin internals)

```
.
├── .claude-plugin/plugin.json      # manifest
├── .claude/
│   ├── agents/                     # 4 sub-agents
│   └── skills/                     # 6 skills
│       └── scaffold/specs/         # 19 reference specs
├── docs/PROCESS.md                 # canonical agent-team lifecycle
├── CLAUDE.md                       # plugin-dev brief
├── README.md                       # this file
└── LICENSE
```

For plugin development details, see [`CLAUDE.md`](CLAUDE.md).

## License

See [`LICENSE`](LICENSE).
