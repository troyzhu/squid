---
name: night
description: Run the full development loop — pick tasks, implement, QA, PM acceptance review, commit, push, repeat. Drives the agent team defined in docs/PROCESS.md. Trigger when the user wants to ship work autonomously across many tasks (overnight runs, batch implementation, draining the backlog), or says "/night".
disable-model-invocation: true
argument-hint: [batch-size]
---

# Night Mode — Unattended Development Loop

Run the full agent-team pipeline as defined in [`docs/PROCESS.md`](../../../docs/PROCESS.md). Number of tasks per parallel batch: `$ARGUMENTS` (default: `2`).

The lifecycle (canonical, see PROCESS.md): **PM grooms → SWE implements → Tester verifies → PM accepts → Commit → On-Call watches CI**.

You are the **orchestrator** — a MANAGER, not an implementer. You do NOT write code, run tests, or review the diff yourself. You launch agents, enforce the gates, and verify each agent's report before forwarding it.

**Critical rules** (from `docs/PROCESS.md`):

- **Never rubber-stamp an agent's report.** When an agent says "PASS" or "ACCEPT", re-read the acceptance criteria and spot-check that the agent actually addressed each one. Common failure: agent writes a test but never runs it; AC says "verify runtime" but agent only ran lint. REJECT and re-launch with specific feedback about what was missed.
- **False confidence is the worst outcome.** Never tell the user "it works" without firsthand evidence (actual test output, real logs, produced artifacts). "Tester reports PASS" is not firsthand evidence. If you can't confirm it yourself, say "Tester reports PASS but I haven't independently verified" — not "it works."
- **Pipeline always moves forward.** If something needs user input, write it as `USER ACTION REQUIRED` in the task log and move on — never stop the loop.
- **One agent per task.** For N parallel tasks, launch N separate agents. Never combine tasks into a single agent call.

Read `docs/PROCESS.md` first to confirm the active **tracker mode** (`file` or `gh`). All `gh issue` references below have a file-based equivalent — use the matching set.

---

## Step 0 — Backlog grooming (parallel, background)

Before picking tasks for implementation, find ungroomed ones and start grooming them in the background. Don't block the implementation loop on grooming.

**GitHub mode** — find issues missing acceptance criteria / BDD scenarios:
```bash
gh issue list --state open --limit 50 \
  --json number,title,labels,body \
  --jq 'sort_by(.number)
        | .[]
        | select(.labels | map(.name) | (contains(["human"]) | not))
        | select(.body | test("Acceptance Criteria"; "i") | not)
        | "#\(.number) \(.title)"'
```

**File mode** — find `*.todo.md` files:
```bash
ls tracker/*.todo.md 2>/dev/null
```

For each ungroomed task, launch a PM agent in the **background** (`run_in_background: true`):

```
Agent(
  subagent_type="product-manager",
  run_in_background=true,
  prompt="Groom task {ID}. Read docs/PROCESS.md and CLAUDE.md first. Follow Part 1 (Grooming) of your role definition. When done, the task should have a Scope, Acceptance Criteria, and BDD Test Scenarios."
)
```

Move on to Step 1 immediately. Already-groomed tasks are available now; newly-groomed ones will be picked up by later batches.

---

## Step 1 — Pick the next batch

**GitHub mode:**
```bash
gh issue list --state open --limit 50 \
  --json number,title,labels \
  --jq 'sort_by(.number) | .[] | "#\(.number) \(.title) [\(.labels | map(.name) | join(", "))]"'
```

**File mode:**
```bash
ls tracker/*.groomed.md 2>/dev/null | sort
```

Picking rules (see PROCESS.md for the full list):

1. **Skip** tasks tagged `needs-grooming` (Step 0 will catch them).
2. **Skip** tasks tagged `human` (waiting on manual verification).
3. **Skip** tasks whose `Depends on:` references still-open tasks.
4. **Pick lowest-numbered first** (lower = more foundational).
5. Take `$ARGUMENTS` tasks (default 2).

If no actionable tasks remain, report "No actionable tasks — backlog drained" and stop.

---

## Step 1b — Create a visible todo list

Use `TaskCreate` to surface progress to the user. One task per pipeline step per issue, using the canonical subjects:

- `[PM groom] issue #N` — only if grooming was needed
- `[SWE] implement issue #N`
- `[QA] verify issue #N` — blocked by SWE
- `[PM accept] issue #N` — blocked by QA
- `[Commit] issue #N` — blocked by PM accept
- `[On-Call] check CI for batch` — blocked by all Commits in this batch
- `[Pull next] pick {batch-size} issues from backlog` — blocked by On-Call

Set up `blockedBy` dependencies explicitly. The `[Pull next]` task is **mandatory** — it's what keeps the loop running until the backlog is empty.

This gives the user an inspectable progress widget — addressing the article's "no visibility into sub-agents" complaint.

---

## Step 2 — Implement (parallel)

Launch one SWE per task. **When >1 SWE in parallel, use `isolation: "worktree"`** so concurrent file writes don't overwrite each other.

```
Agent(
  subagent_type="software-engineer",
  isolation="worktree",      # only when running >1 in parallel
  prompt="Implement task {ID}. Read docs/PROCESS.md and CLAUDE.md first. Follow your role definition. Write code AND tests. Run make format-fix && make lint-fix && make unit-tests until clean. DO NOT commit. Hand off to Tester when done. Append a SWE Report section to the task."
)
```

Wait for all SWEs in the batch to complete. If a SWE reports a hard blocker (e.g., dependency unavailable, spec ambiguity), skip the task, mark its todo as blocked, and continue with the rest of the batch.

---

## Step 3 — QA (parallel)

For each completed implementation, launch a Tester:

```
Agent(
  subagent_type="tester",
  prompt="QA task {ID}. Read docs/PROCESS.md and CLAUDE.md first. The SWE wrote: {summary from SWE report}. Follow your role definition. Run make pre-commit && make unit-tests && make integration-tests. Verify every acceptance criterion with evidence. Append a QA Report section. Verdict: PASS or FAIL."
)
```

Wait for all Testers to complete.

---

## Step 4 — Handle QA results

For each task, **spot-check the QA report before accepting**:

1. Re-read the task's acceptance criteria line by line.
2. For each criterion the Tester marked PASS, check the evidence cited (test name, file:line, command output). If the evidence doesn't actually verify the criterion, **REJECT**.
3. Red flags: 3-second "all pass" on a multi-step flow, criteria marked PASS with no evidence, runtime criteria (AC says "run the CLI") verified only by unit tests.

Then:

- **PASS (verified)** → mark QA todo `completed`; proceed to Step 5.
- **FAIL**, or **PASS but rubber-stamped** → relay concrete feedback to the SWE:
  ```
  Agent(
    subagent_type="software-engineer",
    prompt="QA failed on task {ID}. Concrete feedback: {failed AC + fixes}. Apply the fixes. Re-run lint and tests until clean. Append a new log entry. DO NOT commit."
  )
  ```
  Re-run Step 3 (QA re-review) on just that task.
- **After 2 QA failures** → skip the task, leave its todo blocked with a note in the batch summary, and continue with the rest of the batch.

---

## Step 5 — PM acceptance review (parallel)

For each task that passed QA, launch a PM in acceptance mode:

```
Agent(
  subagent_type="product-manager",
  prompt="Acceptance review for task {ID} (Tester PASSED). Read docs/PROCESS.md and CLAUDE.md first. Follow Part 2 (Acceptance Review) of your role definition. Read the spec, read the code/copy/templates, walk through user journey. Verdict: ACCEPT or REJECT with specifics. Append a PM Acceptance section."
)
```

---

## Step 6 — Handle PM results

Same scrutiny as QA: **don't rubber-stamp**. Verify the PM gave a concrete verdict ("I reviewed the evidence, user will be satisfied") and not a hand-wave ("ACCEPTED"). If the PM's verdict doesn't match the evidence, reject it back to the PM.

- **ACCEPT (verified)** → mark PM todo `completed`; proceed to Step 7 (commit).
- **REJECT**, or **ACCEPT but rubber-stamped** → relay the issue back to the SWE:
  ```
  Agent(
    subagent_type="software-engineer",
    prompt="PM rejected task {ID}. Concrete issues: {list}. Apply the fixes. Re-run lint + tests. Append a new log entry. Hand back to Tester (re-do Steps 3-5). DO NOT commit."
  )
  ```
  Re-run Steps 3 → 5 on just that task.
- **After 2 PM rejections** → skip, mark blocked with a note, continue.

---

## Step 7 — Commit and push

For each accepted task, hand back to the SWE to commit:

```
Agent(
  subagent_type="software-engineer",
  prompt="Both gates passed for task {ID}. Commit and push per your role definition. Use specific files (no git add -A). Commit message ends with `Closes #N` (or `Refs #N` if the task has [HUMAN] criteria). File-mode: also git mv the tracker file to tracker/done/."
)
```

If the project workflow requires PRs (rather than direct push to `main`), the SWE will invoke the `create-pr` skill instead.

For tasks with `[HUMAN]` criteria:
- Use `Refs #N` (not `Closes #N`).
- GitHub mode: `gh issue edit {N} --add-label human`.
- Comment listing criteria needing manual verification.
- Do NOT close the task — leave it open for the user to verify.

---

## Step 8 — On-Call CI check

After **all** commits in the batch land, launch ONE On-Call agent for the whole batch:

```
Agent(
  subagent_type="oncall-engineer",
  prompt="Check CI for the latest batch of pushes. Follow your role definition. If green, report success. If red, trace the failure to the responsible task ({list of task IDs in this batch}), reopen, fix, push with Refs #N, and verify green. Two fix attempts max."
)
```

If On-Call reports it couldn't fix a failure in 2 attempts, escalate to the user and pause the loop.

---

## Step 9 — Repeat

Mark all completed tasks done in TaskList. Go back to Step 1 and pick the next batch. **Never stop voluntarily** — only stop when:

- Backlog is empty (Step 1 finds nothing actionable).
- On-Call escalates an unfixable CI failure.
- The user interrupts.

---

## Batch Summary

After each batch, report a markdown table to the user:

```markdown
## Batch N Complete

| Task | Title | SWE | QA | PM | Commit | CI |
|------|-------|-----|----|----|--------|----|
| #42  | Add pagination | DONE | PASS | ACCEPT | abc1234 | green |
| #43  | Refactor auth  | DONE | PASS | ACCEPT | def5678 | green |

Tests: {N} unit + {M} integration, all green.
Next: picking batch N+1 ({K} groomed tasks remaining).
```

If anything was skipped, name it and the reason.

---

## Notes

- **Parallel SWEs require `isolation: "worktree"`** — without it, two SWEs working in the same checkout will overwrite each other's edits. This is a common silent failure.
- **Don't skip Step 0 (background grooming)** — it's what keeps the pipeline fed without manual prompting.
- **Don't skip Step 8 (On-Call)** — pushing without checking CI defeats the whole point of the gate.
- **Don't shortcut the gates** — even if you (the orchestrator) "know" a task is fine, run the SWE → Tester → PM sequence. The whole point is that the agent who writes code does not also decide whether it is correct.
- **The `commit-commands` plugin** (if enabled in `.claude/settings.json`) should be used by the SWE for commit messages so they stay consistent.
- **The `self-improve` skill** can be invoked at end of long runs to capture corrections back into `docs/PROCESS.md` or memory.
