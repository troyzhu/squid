---
name: plan
description: Turn a raw feature spec into an approved Tasks Plan — one markdown file per atomic task under `tasks/` — plus an optional ADR, branch, and worktree. Grills the human to sharpen the spec, has the Product Architect groom it into draft tasks (reading docs/glossary, proposing an ADR, using context7), then runs ONE human gate with four decisions — write the tasks, create the ADR, new worktree vs current tree, and which build to run (/implement-night, an /implement-task loop, or stop). Trigger when the user wants to plan a feature before building, or says "/plan".
disable-model-invocation: true
argument-hint: <feature-spec | path/to/spec.md | tracker-ref>
---

# Plan — feature spec → per-task files (+ optional ADR, + worktree)

Anchor a feature in shared understanding and prior decisions, then produce the artifact `/implement-night` consumes: an **approved Tasks Plan — one `tasks/<NNN>-<slug>.md` file per atomic task** — plus an optional ADR, with a feature branch created and the build optionally kicked off. **Nothing touches the repo until the human gate.**

`$ARGUMENTS` is the raw feature spec — free-form text, a path to a spec file, or a tracker reference. If empty, ask the human for one.

You are the **orchestrator** — a MANAGER. You drive the grilling, launch the Product Architect (PA), run the single four-decision human gate, set up the workspace, write the approved artifacts, and kick off the chosen build. You do NOT groom, write code, or implement anything yourself — and you NEVER start building before the gate.

Read `AGENTS.md` first to confirm the active **tracker mode** (`file` → `tasks/<NNN>-<slug>.md` files; `gh` → one GitHub Issue per task).

**Input:** raw feature spec.
**Output:** decided at the human gate — by default one `tasks/<NNN>-<slug>.md` per atomic task (`status: pending`, `feature: <slug>`) + an optional new ADR under `docs/adr/` + branch `feat/{slug}` (in a new worktree or the current tree), then optionally the chosen build (`/implement-night` or an `/implement-task` loop). This is exactly what the downstream pipeline consumes.

---

## Step 0 — Resolve the feature spec

If `$ARGUMENTS` is empty, ask the human for the feature (free-form, path, or tracker ref). Otherwise resolve it: `cat` a spec file, load a tracker record, or use free-form text. Surface the resolved spec back in one paragraph.

---

## Step 1 — Grill the spec (Human ↔ /grilling)

Before grooming, sharpen the raw spec with the human. **Invoke the `grilling` skill** — interview the human relentlessly, one question at a time with a recommended answer, until scope, edge cases, non-goals, constraints, and any decisions that warrant an ADR are clear. Anything answerable by reading the codebase — explore instead of asking. The output is a **grilled spec**; carry it into Step 2.

---

## Step 2 — PA grooms → DRAFTS the plan (no writes yet)

Launch ONE Product Architect. It **drafts** everything and hands it back — it writes **nothing** to disk. The human approves at the gate; the orchestrator writes the approved artifacts into the chosen workspace in Step 4.

```
Agent(
  subagent_type="squid:product-architect",
  prompt="""Feature-level grooming. Read AGENTS.md first. Follow your feature-grooming role.
  Feature (grilled): {grilled spec from Step 1}.
  Decompose into atomic, independently-shippable tasks, numbered (NNN) in dependency order. For EACH task, draft the
  FULL tasks/<NNN>-<slug>.md content: frontmatter `id`, `feature: {slug}`, `status: pending`, then Scope, Acceptance
  Criteria, Out of scope, and an empty `## Log` section.
  Also draft: (a) any new docs/glossary.md terms, and (b) IF the feature warrants non-obvious architectural decisions, a
  SINGLE proposed ADR for the WHOLE feature (Nygard template: Status / Context / Decision / Consequences) — ONE ADR that
  captures the entire design, never one ADR per task; its Decision section records every related choice.
  DO NOT WRITE ANYTHING TO DISK — hand everything back as drafts; the human approves and the orchestrator writes them.
  Use the context7 plugin for authoritative library/API usage wherever the feature touches an external framework.
  Return: (1) the ordered task files with their full content, (2) the glossary additions (or 'none'), (3) the proposed
  ADR draft (or 'none')."""
)
```

**Verify before the gate:** the drafts are atomic, ordered by `NNN` in dependency order, and each has acceptance criteria. Re-launch the PA with the gap as feedback if not. Nothing is on disk yet — that is intentional.

---

## Step 3 — HUMAN GATE: four decisions (blocking)

This is the **only** gate, and it is **mandatory** — do not skip it, and do not start writing files, creating branches, or implementing before the human answers. Surface the plan summary, then ask all four questions in one gate (use `AskUserQuestion`) and **wait**:

```
Feature: {title}
Tasks ({N}):
  1. {NNN-slug} — {title}
  2. ...
Glossary additions: {new terms, or "none"}
Proposed ADR: {ADR-NNNN "title" — 1-line summary, or "none"}
```

1. **Write the plan?** — write these {N} tasks to `tasks/`? → **Approve** / **Edit** / **Cancel**
2. **Create the ADR?** — write the proposed ADR to `docs/adr/`? → **Create** / **Skip**  *(omit this question entirely if no ADR was proposed)*
3. **Workspace?** — where should branch `feat/{slug}` live? → **New worktree** (isolated `../{repo}-{slug}` dir) / **Current working tree** (branch in place)
4. **Build now?** — what runs after setup? → **`/implement-night`** (end-to-end to a validated PR) / **`/implement-task` loop** (build + commit the tasks only, no review/CI) / **Stop after planning**

Then act on Q1:

- **Cancel** → stop. Nothing has been written or branched — that is the whole point of drafting first. Discard Q2–Q4.
- **Edit** → ask what to add / remove / reorder / re-split; re-launch the PA (Step 2); loop back to this gate. (Q2–Q4 are re-asked too.)
- **Approve** → go to Step 4, carrying the Q2–Q4 answers.

---

## Step 4 — Execute the decisions (only after Approve)

Do these in order.

**A. Set up the workspace (Q3).**

- **New worktree:**
  ```bash
  git rev-parse --abbrev-ref HEAD          # expect main; if not, ask the human how to proceed
  git pull
  WORKTREE_PATH="$(git rev-parse --show-toplevel)/../$(basename $(git rev-parse --show-toplevel))-{slug}"
  git worktree add -b feat/{slug} "$WORKTREE_PATH" main
  ```
  If it already exists (re-running after an abort): tell the human, ask reuse (`r`) / recreate (`d`) — default reuse.
- **Current working tree:**
  ```bash
  git pull
  git switch -c feat/{slug}                # if already on a feat/* branch, reuse it instead
  ```
  `WORKTREE_PATH` = the repo root.

**B. Write the approved artifacts into the workspace.** Write to **absolute paths under `$WORKTREE_PATH`** (for a new worktree the orchestrator's cwd is still the main repo — do NOT write the tasks into `main`):

- One `$WORKTREE_PATH/tasks/<NNN>-<slug>.md` per task (`status: pending`) from the Step 2 drafts. *(gh tracker mode: create one GitHub Issue per task instead.)*
- Apply the glossary additions to `$WORKTREE_PATH/docs/glossary.md`.
- If Q2 = **Create**: write `$WORKTREE_PATH/docs/adr/NNNN-<slug>.md` (Status: Accepted) from the ADR draft. If **Skip**: discard the draft.
- **Verify:** `ls "$WORKTREE_PATH/tasks"` lists every expected file, and each has `status: pending` + acceptance criteria. If anything is missing, write it now — do not hand off an empty `tasks/`.

**C. Kick off the build (Q4).**

- **`/implement-night`** → invoke `/implement-night` with: feature `{slug}`, `Working directory: $WORKTREE_PATH`.
- **`/implement-task` loop** → invoke `/implement-task` with: the feature's pending tasks (`tasks/<NNN>-*.md`, `status: pending`), `Working directory: $WORKTREE_PATH`. (It loops SWE → Tester → commit per task; no `/review` or `/review-ci`.)
- **Stop after planning** → hand off and stop:
  ```
  Plan approved. {N} tasks in tasks/ (status: pending) on `feat/{slug}` ({worktree at $WORKTREE_PATH | current working tree}).
  Next: run `/implement-night` (builds every pending task to a validated PR), or `/implement-task` for individual tasks.
  ```

`/plan` ends here.

---

## Notes

- **Grill first, groom second, gate last.** The grilling sharpens intent; the PA's grooming turns it into atomic, commit-grain task drafts; the single gate decides everything that touches the repo. Don't skip the grilling — a wrong-shaped plan costs the whole pipeline downstream.
- **Nothing touches the repo before the gate.** The PA only drafts; the orchestrator writes task files, the ADR, the glossary edit, and creates the branch/worktree **after Approve**. Cancel leaves the repo untouched.
- **The tasks ARE the plan.** One `tasks/<NNN>-<slug>.md` per atomic task (`status: pending`) — there is no separate plan document. See the [`tracker-workflow`](../scaffold/specs/tracker-workflow.md) spec for the file shape.
- **One gate, four decisions, then act — never before.** `/plan` must not start implementing (no `/implement-night`, no `/implement-task`) until the human has answered the gate and chosen a build. The build choice is part of the gate, not an assumption.
- **One ADR per plan, not per task.** A feature gets at most ONE new ADR capturing its whole design; the tasks it decomposes into stay atomic and each links back to that single ADR. (A follow-up ADR authored mid-pipeline for an unforeseen architectural fork is the rare exception — see [`product-architect`](../../agents/product-architect.md).)
- **ADRs are human-gated.** The PA *proposes*; the human decides at Q2; only an approved ADR lands in `docs/adr/`. The PA also owns `docs/glossary.md`.
