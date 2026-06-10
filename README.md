# Squid: An Opinionated Agentic Engineering Team for Claude Code

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-2.1%2B-blue)](https://claude.com/claude-code)
[![Plugin version](https://img.shields.io/github/v/tag/iusztinpaul/squid?label=version)](https://github.com/iusztinpaul/squid/tags)

Claude Code writes code fast. It's worse at writing the code *your team* would actually ship — the kind that follows your conventions, has tests you trust, and survives review.

**Squid is a [Claude Code](https://claude.com/claude-code) plugin that turns a feature spec into a reviewed PR using a 5-agent pipeline — PM → SWE → Tester → PR Reviewer → On-Call — with exactly two human gates: plan approval and final merge.**

No file templates. No render step. Markdown specs + agent contracts only; every file in your project gets written by an agent that reads those specs and follows them.

## How it works

Run `/night <feature-spec>` and Squid drives this pipeline end-to-end:

```
   feature spec
        │
        ▼
  ┌─────────────┐     ┌─────────────────────┐     ┌────────────────────┐
  │ PM grooms   │────▶│  HUMAN approves     │────▶│ SWE ↔ Tester loop  │
  │ Tasks Plan  │     │  Tasks Plan  (1/2)  │     │      (per task)    │
  └─────────────┘     └─────────────────────┘     └────────────────────┘
                                                            │
                                                            ▼
  ┌─────────────┐     ┌─────────────────────┐     ┌────────────────────┐
  │ HUMAN       │◀────│  PR Reviewer  ‖     │◀────│ PM accepts + push  │
  │ merges PR   │     │  On-Call (CI)       │     │                    │
  │     (2/2)   │     │  (run in parallel)  │     │                    │
  └─────────────┘     └─────────────────────┘     └────────────────────┘
```

Branch + worktree, grooming, the per-task implement/verify loop, push, parallel CI + diff review, squash — all automated. You only show up for the two gates.

For active iteration on a single task, use `/day <task>` instead — same SWE ↔ Tester loop, no PM grooming, no PR pipeline. Use `/scaffold` first if you're starting from an empty directory; it interviews you about the stack, picks the right specs, and writes a tailored `CLAUDE.md` plus a folder skeleton (no application source).

## Who this is for

- **Yes:** solo devs and small teams shipping Python backends, TypeScript frontends, or Go TUIs who want Claude Code to *consistently* hit your team's bar without re-explaining conventions every session.
- **Maybe not:** teams with an established in-house agent pipeline they don't want to displace, or stacks Squid doesn't cover yet (Rust, Java, mobile — [PRs welcome](#contributing)).


## [Learn How to Build Agentic Coding Frameworks From Scratch](https://decodingai.com)

If you want to learn how to build agentic coding frameworks such as Squid from scratch, consider joining 40k+ engineers by subscribing to [the Decoding AI Magazine](https://decodingai.com).

![Decoding AI Magazine](./assets/decodingai.jpg)

## Install

```
/plugin marketplace add iusztinpaul/squid
/plugin install squid@iusztinpaul
```

That's it. Open any repo in Claude Code; the agents and skills appear in `/agents` and `/help`. Run `/plugin marketplace update iusztinpaul` later to pull fresh changes.

<details>
<summary><b>Per-project install</b> — auto-prompt for everyone who clones a specific repo</summary>

Commit this into the target repo's `.claude/settings.json`:

```json
{
  "extraKnownMarketplaces": {
    "iusztinpaul": {
      "source": {
        "source": "github",
        "repo": "iusztinpaul/squid"
      }
    }
  },
  "enabledPlugins": {
    "squid@iusztinpaul": true
  }
}
```

When a teammate (or future-you on a fresh machine) opens that repo and trusts the folder, Claude Code prompts them to add the marketplace and install in one step. `enabledPlugins` alone isn't enough — `extraKnownMarketplaces` is what tells Claude Code where `squid@iusztinpaul` resolves to.

</details>

<details>
<summary><b>Local plugin development</b> — test uncommitted changes to Squid itself</summary>

```
claude --plugin-dir /path/to/squid
```

Launches Claude Code with the plugin loaded for the session. No marketplace, no install, no cache. Re-run after edits. This is the only path that exercises your local working tree directly on Claude Code v2.1+.

> `/plugin marketplace add /path/to/squid` reads the local `marketplace.json` but the plugin's `source` points at GitHub — so the install still fetches from `iusztinpaul/squid`, not your working tree.

</details>

## What you get

| Surface | What it does |
|---|---|
| `/scaffold` | Interactive bootstrap. Asks what you're building (backend / frontend / TUI / mix), reads the relevant specs, writes a tailored `CLAUDE.md`, and lays down an empty folder skeleton. Run `/day` next to have the agents fill it in. |
| `/day <task>` | Single-task supervised inner loop. `SWE implements → Tester verifies → you review + commit`. Use during active work. |
| `/night <feature-spec>` | End-to-end single-feature pipeline (the diagram above). |
| `product-manager`, `software-engineer`, `tester`, `pr-reviewer`, `oncall-engineer` | Sub-agents invoked by the pipelines. Also available for direct use via the `Agent` tool. |
| `testing-python`, `create-pr`, `self-improve` | Support skills referenced by the pipelines and agents. |

The `/scaffold` spec library (under `skills/scaffold/specs/`) covers:

- **Python:** backend layout, uv, pyproject, ruff, FastAPI, FastMCP, CLI tools
- **TypeScript frontend:** package/tsconfig/vite conventions, React, Vue, Svelte, vanilla
- **Go TUI:** layout + Bubbletea / tview patterns
- **Infra:** Docker, docker-compose, GitHub Actions monorepo CI, OpenAPI contracts
- **Process:** monorepo layout, Makefile delegator, tracker workflow

Several specs are still stubs — foundations are filled in (`python-backend`, `typescript-frontend`, `go-tui`, `uv-python`, `pyproject`, `makefile-delegator`, `monorepo-layout`); the rest are good first contributions.

## Contributing

Issues and PRs welcome — especially for new specs (Rust, Java, mobile, additional Python/TS frameworks) and stub fill-ins. See [`CONTRIBUTING.md`](CONTRIBUTING.md) to get started, and [`CLAUDE.md`](CLAUDE.md) for the underlying plugin-dev conventions.

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
- **Agents are gates.** PM catches scope drift (and signs off from the user's perspective). Tester catches false-confidence "tests pass" claims (and runs an e2e adversarial QA pass). PR Reviewer catches dead/duplicate/untested code and narrow performance regressions in the diff. On-Call catches CI breakage. No agent writes code and also decides whether the code is correct.

## Repo layout (plugin internals)

```
.
├── .claude-plugin/
│   ├── plugin.json                # manifest
│   └── marketplace.json           # one-plugin marketplace catalog
├── agents/                        # 5 sub-agents
├── skills/                        # 12 skills
│   └── scaffold/specs/            # 19 reference specs
├── docs/PROCESS.md                # canonical agent-team lifecycle
├── CLAUDE.md                      # plugin-dev brief
├── README.md                      # this file
└── LICENSE
```

For plugin development details, see [`CLAUDE.md`](CLAUDE.md).

## License

See [`LICENSE`](LICENSE).
