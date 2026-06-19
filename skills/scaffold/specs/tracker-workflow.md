---
name: tracker-workflow
description: File-based task tracker format and state machine — `tracker/NNN-slug.{todo,groomed,in-progress}.md` with a `done/` archive, acceptance criteria, `## Log` sections, and `Depends on:` links. Used by the `/plan`, `/implement-task`, and `/implement-night` pipelines. TRIGGER when creating, updating, or moving task files under `tracker/`, or when the user asks how this project tracks work. SKIP for projects using GitHub Issues as the primary tracker (`TRACKER_MODE: gh` in `AGENTS.md`).
---

# File-based tracker workflow

The default tracker is plain files under `tracker/`. The **filename encodes the task's state**, and the `## Log` section is the single source of truth for what each agent did. GitHub Issues is the opt-in alternative (`TRACKER_MODE: gh`).

## When to use

- The project chose the file-based tracker at scaffold time (`TRACKER_MODE: file`, the default — declared in `AGENTS.md`'s "Agent Team & Pipeline" section).
- You are creating, grooming, picking up, or completing a task and need to move it through its states.

## When NOT to use

- The project set `TRACKER_MODE: gh` — use `gh issue ...` for everything instead (create, label, comment, close). State lives in issue state + labels, not filenames.

## Decision tree

```
Need to track a unit of work?
├── TRACKER_MODE: gh   → gh issue create / comment / close   (labels carry state)
└── TRACKER_MODE: file → a tracker/ file whose name encodes state (below)
```

## State machine (file mode)

The filename suffix is the state; transitions are `git mv`:

```
tracker/
├── 001-add-feature.todo.md         # raw, awaiting grooming
├── 002-pagination.groomed.md       # PA-groomed, in a Tasks Plan, ready to build
├── 003-search.in-progress.md       # SWE/Tester actively working
└── done/
    └── 000-bootstrap.md            # accepted + committed
```

- New task → `NNN-slug.todo.md`
- After PA grooming → `NNN-slug.groomed.md`
- When the SWE picks it up → `NNN-slug.in-progress.md`
- After it passes and the commit lands → `git mv` to `done/NNN-slug.md`

`NNN` is a zero-padded, monotonic counter. A feature's plan lives at `tracker/feature-{slug}-plan.md` — its ordered list of groomed tasks.

## The `## Log` (single source of truth)

Every agent appends timestamped, append-only entries to the task's `## Log` section as it works. Format: `### [ROLE] YYYY-MM-DD HH:MM — Short subject`.

```markdown
## Log

### [PA] 2026-04-27 12:30 — Grooming
...

### [SWE] 2026-04-27 14:00 — Implementation
...

### [Tester] 2026-04-27 14:45 — QA
...

### [PA] 2026-04-27 15:40 — Acceptance
...

### [PR Reviewer] 2026-04-27 16:00 — Review (rollup)
...

### [On-Call] 2026-04-27 16:30 — CI
...
```

Roles: `PA` (Product Architect), `SWE`, `Tester`, `PR Reviewer`, `On-Call`. Entries are never rewritten — only appended.

## Index of supporting files

_(None — this spec is self-contained.)_

## Canonical principles

- **The filename is the state.** Don't track state inside the file when the suffix can carry it; `git mv` on every transition.
- **Append, never rewrite, the Log.** It's the audit trail across the whole pipeline.
- **One task = one file.** Rollup tasks (from a PA REJECT or PR-Reviewer Blockers) are their own files, appended to the end of the plan queue.
- **Switch trackers in one place.** `TRACKER_MODE` in `AGENTS.md` selects file vs gh; nothing else hard-codes the choice.
