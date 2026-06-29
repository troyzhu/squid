# Using Squid with Codex

Codex support in this repo is additive. The original Squid contracts stay in
the root `agents/` and `skills/` directories for Claude Code. Codex uses a thin
adapter layer that reads those canonical contracts and translates Claude-only
tool syntax into Codex workflows.

## What was added

- `.agents/skills/`: repo-local Codex skill entry points. Launch Codex from the
  repo root and use `$scaffold`, `$plan`, `$implement-night`, `$research`, and
  the other Squid skills from `/skills`.
- `.codex/agents/`: project-scoped Codex custom agents matching the Squid
  roles, such as `squid-software-engineer`, `squid-tester`, and
  `squid-research-lead`.
- `plugins/squid-codex/`: a local Codex plugin package for exposing the adapter
  skills through a Codex marketplace.
- `.agents/plugins/marketplace.json`: repo-local marketplace metadata for the
  `squid-codex` plugin.

## How the Codex layer is generated

The Codex artifacts are **generated**, not hand-maintained. `agents/*.md` and
`skills/*/SKILL.md` are the single source of truth; `scripts/gen_codex.py` reads
them plus `scripts/codex/config.yaml` and regenerates the `.codex/agents/*.toml`,
the `plugins/squid-codex/skills/*/SKILL.md` adapters, the `.agents/skills/*`
discovery stubs, and the agent-map table in `codex-adapter.md`. CI
(`.github/workflows/codex-sync-check.yml`) fails if they drift.

- **Good:** edit `skills/research/SKILL.md`, run `python3 scripts/gen_codex.py`,
  commit the regenerated files.
- **Bad:** hand-edit `plugins/squid-codex/skills/research/SKILL.md` — it is
  overwritten on the next regen and CI will fail.

Every generated file carries a `GENERATED — do not edit` header. Hand-written
Codex files are only: this guide, `codex-adapter.md` prose, and
`.agents/plugins/marketplace.json`.

## Local use

Start Codex at the repository root. Codex will load this `AGENTS.md`, discover
the `.agents/skills` adapters, and see the `.codex/agents` custom agents.

The adapters deliberately keep the original Squid files read-only for Codex-only
work. If a workflow says to read `CLAUDE.md`, Codex reads `AGENTS.md` first and
uses `CLAUDE.md` only as fallback project context.

## Plugin use

The local plugin package is `plugins/squid-codex`. Its manifest is
`plugins/squid-codex/.codex-plugin/plugin.json`, and its adapter skills live in
`plugins/squid-codex/skills/`.

The repo marketplace entry points at `./plugins/squid-codex`. In Codex, open
the plugin browser after restarting in this repo, install `squid-codex`, then
start a new thread before trying the newly installed skills.

## Known boundary

Codex plugins currently package skills, apps, and MCP config. Squid's specialized
roles are exposed for this repo through `.codex/agents/*.toml`; when the adapter
is used outside this checkout, it falls back to spawning regular Codex workers
and includes the matching role contract in the prompt when the contract file is
available.

## Research-thread gap (current)

Squid's Codex layer is a **workflow/skill adapter** over the canonical contracts,
not a Codex-native agent runtime. In particular there is no Codex-native
research-thread runtime yet: the adapter can guide Codex through the existing
Squid research workflow in a normal Codex thread, but a durable research-thread
layer — portable run-state, resume, and thread-aware orchestration outside the
Claude plugin environment — still needs design and implementation. Do not
describe Codex `$research` as having tested persistent research-thread semantics
across arbitrary directories; treat that as future work.
