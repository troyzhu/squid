---
name: day
description: Run a single task through the inner SWE↔Tester loop with the human supervising in real time. SWE implements, Tester verifies (including the e2e adversarial pass), you review the diff and commit. No PM grooming, no PM acceptance, no PR Reviewer, no On-Call. Trigger when the user wants to ship one task under active supervision, or says "/day".
disable-model-invocation: true
argument-hint: [task-ref-or-description]
---

# Day Mode — Supervised Single-Task Inner Loop

A lean counterpart to [`/night`](../night/SKILL.md). `/day` is the **same inner SWE↔Tester loop** that `/night` runs internally per task — but standalone, with the human in the human's seat for everything around it (no PM grooming, no PM acceptance, no PR Reviewer, no On-Call).

**Scope:** `$ARGUMENTS` is either a tracker reference (`NNN-slug` or `#N`) or a free-form task description. If empty, ask the human for one before proceeding.

**Pipeline:** `SWE implements → Tester verifies (suite + e2e adversarial pass) → report to human → human reviews & commits`. The human plays the PM, PR Reviewer, and On-Call roles in real time by reading the diff and watching CI themselves.

You are the **orchestrator** — a MANAGER, not an implementer. You do NOT write code, run tests, or review the diff yourself. You launch agents, enforce the Tester gate, and hand the result back to the human.

**Critical rules** (inherit from [`docs/PROCESS.md`](../../../docs/PROCESS.md)):

- **Never rubber-stamp the Tester's report.** Spot-check that each acceptance criterion the Tester marked PASS has real evidence (test name, file:line, command output). REJECT and re-launch if not.
- **Never commit on the human's behalf.** Day mode stops before commit. The human reviews the diff and runs their own commit flow.
- **One task per invocation.** No batching. If the human wants multiple tasks, they invoke `/day` again or switch to `/night`.
- **No worktree isolation.** The human is already in their working tree — SWE works directly there so the human can watch the diff evolve.

Read [`docs/PROCESS.md`](../../../docs/PROCESS.md) to confirm the active **tracker mode** (`file` or `gh`).

---

## Step 1 — Resolve the task

Identify what to work on from `$ARGUMENTS`:

1. **Matches `NNN-slug` or `NNN`** (file mode) → locate `tracker/NNN-*.{todo,groomed,in-progress}.md`. Day mode accepts `.todo.md` directly — no PM grooming required. If the file is `.todo.md` or `.groomed.md`, `git mv` it to `.in-progress.md`.
2. **Matches `#N`** (gh mode) → `gh issue view N --json number,title,body,labels`. No grooming step.
3. **Free-form description** → treat the argument as the task spec. Do NOT create a tracker file unless the human explicitly asks. Keep the task ephemeral.
4. **Empty** → ask the human: "What should I work on? (tracker id, #issue, or a free-form description.)"

Surface the resolved task back to the human in one paragraph before launching the SWE, so they can course-correct the framing up front.

---

## Step 2 — Create a visible todo list

Use `TaskCreate` to show progress:

- `[SWE] implement {task}`
- `[QA] verify {task}` — blocked by SWE
- `[Report] hand off to human` — blocked by QA

Only three steps, no parallel branches. Keep it inspectable.

---

## Step 3 — SWE implements

Launch ONE SWE on the human's working tree (no worktree isolation):

```
Agent(
  subagent_type="software-engineer",
  prompt="Implement task {ID or description}. Read docs/PROCESS.md and CLAUDE.md first. Follow your role definition. Write code AND tests. Run make format-fix && make lint-fix && make unit-tests until clean. DO NOT commit. Append a SWE Report section (or, for ephemeral tasks, include the report in your final message). Hand off to Tester when done."
)
```

If the SWE reports a hard blocker (ambiguous spec, missing dependency), surface it to the human and pause — do not skip past like `/night` would.

---

## Step 4 — Tester verifies

```
Agent(
  subagent_type="tester",
  prompt="QA task {ID or description}. Read docs/PROCESS.md and CLAUDE.md first. The SWE wrote: {summary from SWE report}. Follow your role definition — your headline duty is the e2e adversarial pass. Run make pre-commit && make unit-tests && make integration-tests, then run the e2e adversarial pass (happy path + 2–3 realistic break paths). Verify every acceptance criterion with evidence. Append a QA Report section. Verdict: PASS or FAIL."
)
```

---

## Step 5 — Handle QA results

**Spot-check the Tester's report before accepting** — same scrutiny rules as `/night`:

- Re-read the acceptance criteria. For each PASS, check the evidence is real (test name, command output, file:line).
- Red flags: 3-second "all pass" on a multi-step flow, criteria marked PASS with no evidence, runtime criteria verified only by unit tests.

Then:

- **PASS (verified)** → proceed to Step 6.
- **FAIL**, or **PASS but rubber-stamped** → one feedback loop back to the SWE with concrete fixes:
  ```
  Agent(
    subagent_type="software-engineer",
    prompt="QA failed on {task}. Concrete feedback: {failed AC + fixes}. Apply the fixes. Re-run lint + tests. Append a new log entry. DO NOT commit."
  )
  ```
  Re-run Step 4 on the same task.
- **After 2 QA failures** → stop and hand to the human with the diagnostic. Do not silently skip.

---

## Step 6 — Report and hand back to the human

Produce a single markdown block summarising the task:

```markdown
## Day run complete — {task}

**Files changed** ({N}): `path/to/a.py`, `path/to/b.py`, ...
**Tests run:** {N} unit ({all green / details}); {M} integration ({all green / details}).
**Acceptance criteria:**
- [x] AC1 — evidence: `tests/unit/test_x.py::test_y` (passing).
- [x] AC2 — evidence: ...

Working tree has an uncommitted diff ready for your review.
Next steps: review the diff, then commit (use /commit or your preferred flow).
```

**Do NOT run `git commit`.** Day mode stops here. The human:

1. Reads the diff.
2. Decides what to stage (often a subset of what the SWE touched).
3. Commits using their preferred flow (e.g., `/commit`, the `commit-commands` plugin, or direct `git`).
4. If the task came from the tracker, `git mv`s the `.in-progress.md` file to `tracker/done/` as part of that commit, same as `/night`.
5. Watches CI themselves. If CI goes red, fixes live — no On-Call agent is invoked.

Mark all `TaskList` items completed once the report is delivered. Do **not** pick a next task — `/day` is always single-shot.

---

## Notes

- **Day mode is not a subset of `/night`.** Both modes use the same SWE and Tester agents and the same inner loop, but `/night` chains it inside a longer pipeline (PM groom + acceptance + PR Reviewer + On-Call + squash). `/day` skips all of that on purpose — the human supervises and plays those roles in real time. The Tester gate stays automated because it's the one check that's genuinely hard for a human to replicate (full suite + every AC + e2e adversarial pass).
- **No retry caps applied here.** `/day` retries until the human says stop. `/night`'s Tester FAIL Max 5 cap doesn't apply because the human is in the loop and can intervene any time.
- **If the task turns out to need design input** (ambiguous scope, multiple plausible approaches), stop and ask the human rather than letting the SWE guess. In `/night`, PM grooming absorbs that ambiguity; in `/day`, the human does.
- **The `commit-commands` plugin** (if enabled) is the recommended tool for the human's commit step — same as in `/night`.
- **Don't auto-create tracker files** for free-form tasks. If the human wants a log entry, they'll create one. Keeping day mode ephemeral by default is the point.
