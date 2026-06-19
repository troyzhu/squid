---
name: plan
description: Turn a raw feature spec into an approved, ordered Tasks Plan (+ an optional ADR), then create the feature branch + worktree that /implement-night runs in. Grills the human to sharpen the spec, has the Product Architect groom it (reading/writing docs/adr + docs/glossary, using context7), surfaces the plan for approval, and on approval sets up the worktree. Trigger when the user wants to plan a feature before building, or says "/plan".
disable-model-invocation: true
argument-hint: <feature-spec | path/to/spec.md | tracker-ref>
---

# Plan — feature spec → approved Tasks Plan (+ worktree)

Anchor a feature in shared understanding and prior decisions, then produce the artifact `/implement-night` consumes: an **approved Tasks Plan** (plus an optional ADR), with the feature branch + worktree created.

`$ARGUMENTS` is the raw feature spec — free-form text, a path to a spec file, or a tracker reference. If empty, ask the human for one.

You are the **orchestrator** — a MANAGER. You drive the grilling, launch the Product Architect (PA), enforce the human gate, and set up the worktree. You do NOT groom or write code yourself — the PA does the grooming.

Read `AGENTS.md` first to confirm the active **tracker mode** (`file` or `gh`).

**Input:** raw feature spec.
**Output:** an approved **Tasks Plan** at `tracker/feature-{slug}-plan.md` (file mode) or a pinned `feature-plan` issue (gh mode) — ordered groomed tasks, "Out of scope", documentation updates (ADRs/glossary), open questions — PLUS a created branch `feat/{slug}` and worktree at `../{repo}-{slug}`. This is the same artifact `/implement-night` (and the granular `/implement-task`) consume.

---

## Step 0 — Resolve the feature spec

If `$ARGUMENTS` is empty, ask the human for the feature (free-form, path, or tracker ref). Otherwise resolve it: `cat` a spec file, load a tracker record, or use free-form text as-is. Surface the resolved spec back in one paragraph.

---

## Step 1 — Grill the spec (Human ↔ /grilling)

Before grooming, sharpen the raw spec with the human. **Invoke the `grilling` skill** — interview the human relentlessly, one question at a time with a recommended answer, until the feature is well understood: scope, edge cases, non-goals, constraints, and any decisions that warrant an ADR. Anything answerable by reading the codebase — explore instead of asking.

The output of this step is a **grilled spec** (the raw spec plus the resolved answers). Carry it into Step 2.

---

## Step 2 — PA grooms → Tasks Plan

Launch ONE Product Architect in feature-level grooming mode:

```
Agent(
  subagent_type="squid:product-architect",
  prompt="""Feature-level grooming. Read AGENTS.md first. Follow your feature-grooming role.
  Feature (grilled): {grilled spec from Step 1}.
  Decompose into 3–8 ordered, independently-shippable tasks, each with a full groomed spec (Scope, Acceptance Criteria, User Stories, Dependencies).
  Maintain the docs: add any new domain terms to docs/glossary.md, and author an ADR under docs/adr/NNNN-*.md (Nygard template) for any non-obvious architectural decision. Use the context7 plugin to look up authoritative library/API usage wherever the feature touches an external framework.
  Produce the Tasks Plan at tracker/feature-{slug}-plan.md (file mode) or a pinned `feature-plan` issue (gh mode).
  Hand back: the plan path, a one-paragraph summary, and the list of any ADR/glossary files written."""
)
```

**Verify before surfacing to the human:** the plan file/issue exists, every task has a groomed file/issue, and tasks are ordered (no later task is a prerequisite of an earlier one). Re-launch the PA with the gap as concrete feedback if verification fails.

---

## Step 3 — HUMAN GATE: approve the Tasks Plan

Surface the plan:

```
Feature: {title}
Plan: {path or issue URL}
Tasks ({N}):
1. {ref} — {title}
2. ...
Docs: {new ADRs / glossary terms, or "none"}
Open questions (if any): ...

Approve to set up the branch + worktree? (y / edit / cancel)
```

Wait for the response.

- `y` → Step 4.
- `edit` → ask what to add/remove/reorder; re-launch the PA; loop back to Step 3.
- `cancel` → stop. Nothing has been branched yet — that's the point of creating the worktree last.

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

The planning artifacts the PA wrote in Step 2 (the Tasks Plan + groomed task files under `tracker/`, any new `docs/adr/NNNN-*.md`, and `docs/glossary.md` edits) are currently uncommitted in the **main** working tree. **Relocate them into the worktree** so they live on `feat/{slug}` and travel with the PR: move the new files into `$WORKTREE_PATH` at the same relative paths, re-apply the glossary edit there, then restore the main working tree to clean (`git checkout -- docs/glossary.md`). After this, everything the pipeline needs is on the feature branch.

Hand off:

```
Plan approved. Branch `feat/{slug}` + worktree at {WORKTREE_PATH}.
Next: run `/implement-night` to build the whole plan end-to-end (it runs in this worktree),
or `/implement-task {ref}` to build individual tasks.
```

`/plan` ends here.

---

## Notes

- **Grilling first, grooming second.** The grilling sharpens the human's intent; the PA's grooming turns the sharpened spec into commit-grain tasks. Don't skip the grilling — a wrong-shaped plan costs the whole pipeline downstream.
- **Branch/worktree is the LAST thing `/plan` does** — so nothing is branched if the human cancels, and the plan + any ADR/glossary fork onto the feature branch rather than landing on `main` directly.
- **The PA owns `docs/adr/` and `docs/glossary.md`.** New domain concepts and architectural decisions are captured here, at planning time — not retrofitted during implementation.
