# Squid Codex Adapter Rules

These rules adapt Squid's Claude Code contracts for Codex without changing the
original files.

## Source order

1. Read this adapter reference.
2. Read the canonical Squid skill or agent contract named by the adapter. In an
   installed Codex plugin, use the packaged snapshot under
   `references/canonical/`.
3. Follow the canonical contract after applying the translation rules below.

If the canonical contract is unavailable, continue only when the adapter has
enough information to do the job safely. Otherwise report the missing file as a
blocker.

## Translation rules

- `CLAUDE.md`: read `AGENTS.md` first when it exists. Read `CLAUDE.md` only as
  fallback project context or when the user explicitly asks to inspect Claude
  behavior.
- `Agent(subagent_type="squid:<role>", prompt=...)`: spawn a Codex subagent.
  Prefer the matching `.codex/agents/squid-<role>.toml` custom agent in this
  checkout. If it is unavailable, spawn a normal Codex worker and include the
  matching `agents/<role>.md` contract in the prompt.
- `Agent(subagent_type="general-purpose", prompt=...)`: spawn a normal Codex
  subagent with the prompt's full role/lens brief. Use this for workflows such
  as `research-thread` that define ad hoc review lenses rather than Squid's
  named role agents.
- `TaskCreate` or `TaskList`: maintain a visible Codex plan when a planning tool
  is available; otherwise keep a concise checklist in the response.
- `AskUserQuestion`: ask the user directly. If the canonical workflow marks the
  question as a hard gate, wait for the answer.
- Claude tool names (`Read`, `Edit`, `Write`, `Bash`, `Glob`, `Grep`,
  `WebSearch`, `WebFetch`, `Skill`) map to the closest available Codex tools and
  capabilities in the active environment.
- Slash command names such as `/plan` and `/research` map to Codex skill
  invocation (`$plan`, `$research`) or selection from `/skills`.

## Human gates

Human gates remain gates. Do not auto-approve a Tasks Plan, Research Plan, save
prompt, release action, merge, or destructive command just because the canonical
workflow is being run through Codex.

## Agent map

<!-- BEGIN GENERATED:agent-map (scripts/gen_codex.py) — do not edit by hand -->
| Claude role | Codex custom agent | Canonical contract |
|---|---|---|
| `squid:literature-scout` | `squid-literature-scout` | `agents/literature-scout.md` |
| `squid:oncall-engineer` | `squid-oncall-engineer` | `agents/oncall-engineer.md` |
| `squid:pr-reviewer` | `squid-pr-reviewer` | `agents/pr-reviewer.md` |
| `squid:product-architect` | `squid-product-architect` | `agents/product-architect.md` |
| `squid:research-lead` | `squid-research-lead` | `agents/research-lead.md` |
| `squid:research-reviewer` | `squid-research-reviewer` | `agents/research-reviewer.md` |
| `squid:software-engineer` | `squid-software-engineer` | `agents/software-engineer.md` |
| `squid:strategist` | `squid-strategist` | `agents/strategist.md` |
| `squid:synthesizer` | `squid-synthesizer` | `agents/synthesizer.md` |
| `squid:tester` | `squid-tester` | `agents/tester.md` |
<!-- END GENERATED:agent-map -->

## Claude-only persistence

Some Squid workflows were written to edit Claude setup files. In Codex:

- `self-improve`: persist Codex lessons to `AGENTS.md`, Codex memories, or
  Codex-owned files. Do not update `CLAUDE.md` unless the user explicitly asks
  to change Claude behavior too.

## Shared-file safety

For Codex-only adaptation work, do not edit `CLAUDE.md`, `.claude/`,
`.claude-plugin/`, root `agents/`, root `skills/`, or the shared lifecycle docs.
Those are the canonical Claude-facing contracts and remain the source material
for this adapter.
