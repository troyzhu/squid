---
name: plan
description: Turn a raw feature spec into an approved Tasks Plan — one markdown file per atomic task under `tasks/` — plus an optional ADR, then create the feature branch + worktree that /implement-night runs in. Grills the human to sharpen the spec, has the Product Architect groom it (reading/writing docs/adr + docs/glossary, using context7), proposes a new ADR for your approval, and writes one `tasks/<NNN>-<slug>.md` per task. Trigger when the user wants to plan a feature before building, or says "/plan".
disable-model-invocation: true
argument-hint: <feature-spec | path/to/spec.md | tracker-ref>
---

# Plan — feature spec → per-task files (+ optional ADR, + worktree)

Anchor a feature in shared understanding and prior decisions, then produce the artifact `/implement-night` consumes: an **approved Tasks Plan — one `tasks/<NNN>-<slug>.md` file per atomic task** — plus an optional ADR, with the feature branch + worktree created.

`$ARGUMENTS` is the raw feature spec — free-form text, a path to a spec file, or a tracker reference. If empty, ask the human for one.

You are the **orchestrator** — a MANAGER. You drive the grilling, launch the Product Architect (PA), run the human gates (ADR + plan approval), and set up the worktree. You do NOT groom or write code yourself.

Read `AGENTS.md` first to confirm the active **tracker mode** (`file` → `tasks/<NNN>-<slug>.md` files; `gh` → one GitHub Issue per task).

**Input:** raw feature spec.
**Output:** an approved **Tasks Plan** = one `tasks/<NNN>-<slug>.md` per atomic task (`status: pending`, `feature: <slug>`) in `tasks/` (file mode) or one issue per task (gh mode); **+ an optional new ADR** under `docs/adr/`; **+ the branch `feat/{slug}` and worktree**. This is exactly what `/implement-night` (and the granular `/implement-task`) consume.

---

## Step 0 — Resolve the feature spec

If `$ARGUMENTS` is empty, ask the human for the feature (free-form, path, or tracker ref). Otherwise resolve it: `cat` a spec file, load a tracker record, or use free-form text. Surface the resolved spec back in one paragraph.

---

## Step 1 — Grill the spec (Human ↔ /grilling)

Before grooming, sharpen the raw spec with the human. **Invoke the `grilling` skill** — interview the human relentlessly, one question at a time with a recommended answer, until scope, edge cases, non-goals, constraints, and any decisions that warrant an ADR are clear. Anything answerable by reading the codebase — explore instead of asking. The output is a **grilled spec**; carry it into Step 2.

---

## Step 2 — PA grooms → per-task files (+ proposes an ADR)

Launch ONE Product Architect:

```
Agent(
  subagent_type="squid:product-architect",
  prompt="""Feature-level grooming. Read AGENTS.md first. Follow your feature-grooming role.
  Feature (grilled): {grilled spec from Step 1}.
  1. Decompose into atomic, independently-shippable tasks. Write ONE file per task: tasks/<NNN>-<slug>.md with
     frontmatter `id`, `feature: {slug}`, `status: pending`, plus Scope, Acceptance Criteria, Out of scope, and a
     `## Log` section. Number them (NNN) in dependency order. (gh mode: one issue per task instead.)
  2. Add any new domain terms to docs/glossary.md.
  3. If the feature warrants a non-obvious architectural decision, DRAFT a proposed ADR (Nygard template) and hand it
     back as a PROPOSAL — do NOT write it to docs/adr/ yet; the human decides in the next step.
  Use the context7 plugin to look up authoritative library/API usage wherever the feature touches an external framework.
  Hand back: the list of task files created, the glossary updates, and the proposed ADR draft (if any)."""
)
```

**Verify before the gate:** the task files exist, each is atomic with acceptance criteria, and they're ordered by `NNN` in dependency order. Re-launch the PA with the gap as feedback if not.

---

## Step 3 — HUMAN GATE: ADR decision + plan approval

Surface:

```
Feature: {title}
Tasks ({N}) — tasks/<NNN>-<slug>.md (status: pending):
1. {NNN-slug} — {title}
2. ...
Glossary: {new terms, or "none"}
Proposed ADR: {ADR-NNNN "title" — 2-line summary, or "none"}

Create the proposed ADR? (y / n)    Approve the plan? (y / edit / cancel)
```

Wait for the human.

- **ADR `y`** → the PA writes the ADR to `docs/adr/NNNN-<slug>.md` (Status: Accepted). **ADR `n`** → discard the draft.
- **Plan `y`** → Step 4.
- **`edit`** → ask what to add / remove / reorder / re-split; re-launch the PA; loop back to Step 3.
- **`cancel`** → stop. Nothing has been branched yet — that's the point of creating the worktree last.

---

## Step 4 — Create the branch + worktree (final step)

Only after approval, create the feature branch in an isolated worktree:

```bash
git rev-parse --abbrev-ref HEAD          # expect main; if not, ask the human how to proceed
git pull
WORKTREE_PATH="$(git rev-parse --show-toplevel)/../$(basename $(git rev-parse --show-toplevel))-{slug}"
git worktree add -b feat/{slug} "$WORKTREE_PATH" main
```

If the worktree already exists (re-running after an abort), tell the human and ask reuse (`r`) / recreate (`d`) — default reuse.

The artifacts the PA wrote in Steps 2–3 (the `tasks/<NNN>-*.md` files, any new `docs/adr/NNNN-*.md`, and `docs/glossary.md` edits) are uncommitted in the **main** working tree. **Relocate them into the worktree** so they live on `feat/{slug}` and travel with the PR: move the new task + ADR files into `$WORKTREE_PATH` at the same relative paths, re-apply the glossary edit there, then restore the main working tree to clean (`git checkout -- docs/glossary.md`).

Hand off:

```
Plan approved. {N} tasks in tasks/ (status: pending). Branch `feat/{slug}` + worktree at {WORKTREE_PATH}.
Next: run `/implement-night` (builds every pending task in this worktree), or `/implement-task {ref}` for individual tasks.
```

`/plan` ends here.

---

## Notes

- **Grill first, groom second.** The grilling sharpens the human's intent; the PA's grooming turns it into atomic, commit-grain task files. Don't skip the grilling — a wrong-shaped plan costs the whole pipeline downstream.
- **The tasks ARE the plan.** One `tasks/<NNN>-<slug>.md` per atomic task (`status: pending`) — there is no separate plan document. See the [`tracker-workflow`](../scaffold/specs/tracker-workflow.md) spec for the file shape.
- **ADRs are human-gated.** The PA *proposes*; you decide; only approved ADRs land in `docs/adr/`. The PA also owns `docs/glossary.md`.
- **Branch/worktree is the LAST thing `/plan` does** — nothing is branched if you cancel, and the tasks + ADR fork onto the feature branch rather than landing on `main` directly.
