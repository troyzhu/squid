---
name: night
description: Run the full agent-team pipeline end-to-end for a single feature — branch + worktree, PM grooms a Tasks Plan, human approves the plan, inner SWE/Tester loop per task, PM acceptance, push, parallel On-Call (CI) + PR Reviewer (diff), squash, optional Self-Improve, hand the squashed PR to the human to merge. Trigger when the user wants to ship one whole feature unattended between two human gates, or says "/night".
disable-model-invocation: true
argument-hint: <feature-spec | path/to/spec.md | tracker-ref>
---

# Night Mode — End-to-End Single-Feature Pipeline

Run the full agent-team pipeline as defined in [`docs/PROCESS.md`](../../../docs/PROCESS.md) for **one feature**, end-to-end.

`$ARGUMENTS` is the feature spec — a free-form description, a path to a spec file (`docs/features/{slug}.md`), or a tracker reference. If empty, ask the human for one before proceeding.

You are the **orchestrator** — a MANAGER, not an implementer. You do NOT write code, run tests, or review the diff yourself. You launch agents, enforce the gates, and verify each agent's report before forwarding it.

The pipeline blocks on the human exactly **twice**, by design:

1. **After PM produces the Tasks Plan** — human approves the plan before the inner loop runs.
2. **At the very end** — human merges the squashed Feature PR.

There is also one optional human prompt: "Run self-improve to capture corrections into CLAUDE.md? (y/N)". This runs only on yes.

Everything else is automated. Failures route back into the inner loop as new rollup tasks rather than stopping the pipeline.

**Critical rules** (from `docs/PROCESS.md`):

- **Never rubber-stamp an agent's report.** When an agent says "PASS" or "ACCEPT" or "NO BLOCKERS", re-read the spec and spot-check that the agent actually addressed each criterion. REJECT and re-launch with specific feedback if not.
- **False confidence is the worst outcome.** Never tell the user "it works" without firsthand evidence. "Tester reports PASS" is not firsthand evidence.
- **Pipeline always moves forward** between the two human gates. If something needs the user, write `USER ACTION REQUIRED` in the task log and continue. The cap-hit case is the one exception — when a retry cap is reached, surface and stop.
- **One agent per task.** Never bundle multiple tasks into one agent call.
- **The orchestrator never writes code, never merges, never touches the diff** beyond inspection (`git diff`, `git log`).

Read `docs/PROCESS.md` first to confirm the active **tracker mode** (`file` or `gh`).

---

## Step 0 — Resolve the feature spec

If `$ARGUMENTS` is empty: ask the human "What feature should I deliver tonight? (free-form description, path to a spec file, or tracker reference)" and wait for the response.

Otherwise, identify the spec form:

- **Path to a markdown file** (`docs/features/foo.md`, `tracker/NNN-foo.todo.md`) → `cat` it.
- **Tracker reference** (`#42` in gh mode, `NNN-slug` in file mode) → load the existing record.
- **Free-form text** → use as-is.

Surface the resolved spec back to the human in one paragraph as confirmation, but do NOT block here — proceed.

---

## Step 1 — Create the feature branch + worktree

The feature branch name is derived from the spec title — slugified, prefixed with `feat/`. Example: `feat/add-user-pagination`.

```bash
# Confirm we're on main
git rev-parse --abbrev-ref HEAD
git pull

# Create the feature branch in a worktree at ../{repo-name}-{slug}
WORKTREE_PATH="$(git rev-parse --show-toplevel)/../$(basename $(git rev-parse --show-toplevel))-{slug}"
git worktree add -b feat/{slug} "$WORKTREE_PATH" main
cd "$WORKTREE_PATH"
```

For the rest of the run, all agent commands operate in this worktree path. Spell that out in every agent prompt: include `Working directory: {WORKTREE_PATH}` so launched agents don't get confused.

If the worktree already exists (re-running `/night` after an aborted run), prompt the human: "Worktree exists at {path}. Reuse it (`r`) or recreate (`d`)?" — default to reuse.

---

## Step 2 — PM grooms the feature → Tasks Plan

Launch ONE PM agent in **feature-level grooming** mode:

```
Agent(
  subagent_type="squid:product-manager",
  prompt="""Feature-level grooming. Read docs/PROCESS.md and CLAUDE.md first. Follow Part 1A of your role definition.

  Working directory: {WORKTREE_PATH}
  Feature spec: {resolved spec from Step 0}

  Decompose the feature into 3–8 ordered, independently-shippable tasks. Each task gets a full groomed spec (Scope, Acceptance Criteria, User Stories, Dependencies). Produce the Tasks Plan summary at tracker/feature-{slug}-plan.md (file mode) or as a pinned `feature-plan` issue (gh mode).

  Hand back: the path to the Tasks Plan and a one-paragraph summary."""
)
```

Wait for completion. **Verify before forwarding to the human:**

- The plan file/issue actually exists.
- Each task in the plan has a groomed file/issue (don't take the PM's word for it — `ls tracker/*.groomed.md` or `gh issue list --label rollup-or-equivalent`).
- Tasks are ordered (no later task is a prerequisite of an earlier one).

If verification fails, re-launch the PM with the gap as concrete feedback.

---

## Step 3 — HUMAN GATE #1: Approve the Tasks Plan

Surface the Tasks Plan to the human:

```
Feature: {title}
Branch: feat/{slug} (worktree: {path})
Plan: {path or PR URL}

Tasks ({N}):
1. {NNN-slug or #N} — {title}
2. ...

Open questions (if any): ...

Approve to start the inner loop? (y / edit / cancel)
```

**Wait for the human's response.** This is the only mid-pipeline blocking gate.

- `y` → proceed to Step 4.
- `edit` → ask which tasks to add/remove/reorder; re-launch the PM with the human's feedback; loop back to Step 3 with the revised plan.
- `cancel` → tear down the worktree (`git worktree remove`), report cancelled, stop.

If the human is unreachable (truly unattended run), this is the natural place to stop and wait — `/night` is **not** fully autonomous, by design. Surface the plan in the final message and end the session; the human resumes by re-invoking `/night` with the same spec (Step 1 will detect the existing worktree and reuse).

---

## Step 4 — Inner implementation loop

For each task in the Tasks Plan, **in order**, run:

### 4a. SWE implements

```
Agent(
  subagent_type="squid:software-engineer",
  prompt="""Implement task {ID}. Read docs/PROCESS.md and CLAUDE.md first. Follow your role definition.

  Working directory: {WORKTREE_PATH}
  (Skip Step 3 of your role — branch already exists; you're in the worktree.)

  Write code AND tests. Run make format-fix && make lint-fix && make pre-commit && make unit-tests until clean. DO NOT commit yet — Tester goes first. Append a SWE log entry."""
)
```

### 4b. Tester verifies

```
Agent(
  subagent_type="squid:tester",
  prompt="""QA task {ID}. Read docs/PROCESS.md and CLAUDE.md first. Follow your role definition — your headline duty is the e2e adversarial pass.

  Working directory: {WORKTREE_PATH}
  SWE summary: {SWE's hand-off message}

  Run make pre-commit && make unit-tests && make integration-tests. Then run the e2e adversarial pass — happy path first, then 2–3 realistic break paths. Verify every AC with evidence. Append a Tester log entry. Verdict: PASS or FAIL."""
)
```

### 4c. Handle Tester verdict

**Spot-check the report before accepting** — re-read the AC line by line, confirm evidence is real (test name, file:line, command output), confirm the e2e adversarial section actually attempted break paths.

- **PASS (verified)** → move to the next task in the plan. When all tasks done, go to Step 5.
- **FAIL** or **PASS-but-rubber-stamped** → relay concrete feedback to the SWE:
  ```
  Agent(
    subagent_type="squid:software-engineer",
    prompt="QA failed on task {ID}. Working directory: {WORKTREE_PATH}. Concrete feedback: {failed AC + break-path failures + fixes}. Apply the fixes, re-run the local QA loop. Append a new log entry. DO NOT commit."
  )
  ```
  Then re-run Step 4b on the same task.

### 4d. Retry cap: Tester FAIL Max 5 per task

Track the FAIL count for the current task. If you hit **5 FAILs on the same task without a PASS**, stop the pipeline:

- Mark the task blocked in the tracker.
- Surface `USER ACTION REQUIRED` with the failing AC and the last Tester report.
- End the session. Do not continue with later tasks — the foundation is broken.

The counter resets when the task being implemented changes (next task in plan, or a new rollup task from Step 6 / Step 9).

### 4e. Per-task commit (after task PASS only)

Once the Tester PASSES a task, the SWE commits **just that task**:

```
Agent(
  subagent_type="squid:software-engineer",
  prompt="""Tester PASSED task {ID}. Working directory: {WORKTREE_PATH}. Commit per your role definition — `commit-commands` plugin required, specific files only, message ends with `Closes #N` (or `Refs #N` if [HUMAN] criteria, or `Closes-tracker: NNN-slug` in file mode). DO NOT push yet — push happens once for the whole feature after PM ACCEPT."""
)
```

Note the commit lands on the feature branch in the worktree. No push yet.

Continue with the next task. When all tasks in the current plan are done (and committed locally), proceed to Step 5.

---

## Step 5 — PM acceptance review (whole feature)

After every task in the plan has been committed locally, launch ONE PM in acceptance mode:

```
Agent(
  subagent_type="squid:product-manager",
  prompt="""Acceptance review for feature {title}. Read docs/PROCESS.md and CLAUDE.md first. Follow Part 2 of your role definition.

  Working directory: {WORKTREE_PATH}
  Plan: {path}
  All tasks completed locally — see git log on feat/{slug} for the commits.

  Walk the feature from the user's perspective. Verdict: ACCEPT or REJECT. On REJECT, write ONE rollup task per Part 2's rules — never one ticket per issue."""
)
```

**Spot-check** the PM's verdict:

- ACCEPT must include concrete evidence references, not just "ACCEPTED".
- Evidence must match the AC; if the PM ACCEPTs criteria the Tester didn't actually verify, treat as rubber-stamp and re-launch.

---

## Step 6 — Handle PM verdict

- **ACCEPT (verified)** → proceed to Step 7 (push).
- **REJECT** → the PM has filed a rollup task. **Append the rollup task to the end of the plan queue** and loop back to Step 4 with the rollup as the next task to implement. The Tester FAIL counter resets (rollup is a new task).
- **Cap: PM REJECT Max 3 per feature.** If a 4th REJECT would be needed, stop the pipeline, surface `USER ACTION REQUIRED` with the latest rollup task content and the original feature spec, end the session.

---

## Step 7 — Push to git (open or update Feature PR)

Hand to SWE to push and open/update the Feature PR via the `create-pr` skill:

```
Agent(
  subagent_type="squid:software-engineer",
  prompt="""Feature {title} accepted. Working directory: {WORKTREE_PATH}. Push the feature branch (`git push -u origin feat/{slug}` if first push, else `git push`). Then invoke the `create-pr` skill to open or update the Feature PR. The PR description must summarize the feature and list each task by ID. Hand back the PR number."""
)
```

Capture the PR number — you'll need it for Step 8.

---

## Step 8 — Parallel: On-Call (CI) + PR Reviewer (diff)

Launch BOTH agents in **parallel** (one message, two `Agent` calls). They are independent — On-Call reads CI/CD only, PR Reviewer reads the diff only.

```
Agent(
  subagent_type="squid:oncall-engineer",
  prompt="""Watch CI for the latest push on feat/{slug} (PR #{N}). Working directory: {WORKTREE_PATH}. Follow your role definition. CI/CD only — do not read the diff for review. If green, report success. If red, trace, fix, push with `Refs #N`, re-verify. Five fix attempts max."""
)

Agent(
  subagent_type="squid:pr-reviewer",
  prompt="""Review PR #{N} (branch: feat/{slug}). Working directory: {WORKTREE_PATH}. Read docs/PROCESS.md and CLAUDE.md first. Follow your role definition.

  Read the entire diff (`git diff $(git merge-base HEAD origin/main)...HEAD`). Walk the four review dimensions. Tag every finding Blocker or Nit. Produce ONE rollup task if there are Blockers, or report `NO BLOCKERS` and append Nits to the PR description.

  Do NOT read CI status. Do NOT comment on the PR. Do NOT merge."""
)
```

Wait for both to complete.

---

## Step 9 — Handle Step 8 verdicts

Two independent verdicts. Both must clear before Squash.

### On-Call verdict

- **Green** → On-Call's gate clears.
- **Red, fixed by On-Call (push + green)** → On-Call's gate clears (the SWE fix landed; CI is green now).
- **Red, On-Call hit Max 5** → stop the pipeline, surface `USER ACTION REQUIRED` with the last failure log.

### PR Reviewer verdict

- **NO BLOCKERS** → PR Reviewer's gate clears. Nits already appended to PR description.
- **Blockers** (rollup task filed) → append the rollup to the plan queue, loop back to Step 4 with the rollup as the next task. After it lands and is committed, the SWE pushes again (Step 7), and Step 8 re-runs (re-launching both On-Call and PR Reviewer fresh on the new push).
  - **Cap: PR Reviewer Max 3 per feature.** On the 4th would-be Blockers verdict, stop the pipeline.

When both gates have cleared, proceed to Step 10.

---

## Step 10 — Squash commits

You squash the per-task commits into one squashed commit on the feature branch, preserving the PR description.

```bash
# In the worktree:
BASE=$(git merge-base HEAD origin/main)
git reset --soft $BASE
git commit -m "$(cat <<'EOF'
{Feature title}

{1-paragraph summary, derived from the PR description}

Tasks:
- #{N1} {title}
- #{N2} {title}
...
EOF
)"
git push --force-with-lease origin feat/{slug}
```

`--force-with-lease` (not `--force`) so we abort if the remote moved unexpectedly.

Re-invoke `create-pr` to refresh the PR description against the squashed commit:

```
Agent(
  subagent_type="squid:software-engineer",
  prompt="Squash done. Working directory: {WORKTREE_PATH}. Re-invoke the `create-pr` skill to update PR #{N}'s description against the squashed commit (preserve the task list and any Nits already appended)."
)
```

---

## Step 11 — Ask the human about Self-Improve

Prompt the human:

```
Feature {title} is squashed and ready to merge: {PR URL}

Optional: Run self-improve to capture corrections from this run into CLAUDE.md? (y/N)
```

- **N (default)** → skip to Step 12.
- **y** → invoke the `self-improve` skill on this run; it produces a proposed CLAUDE.md update which the human reviews and accepts/rejects via the skill's normal flow. When the skill returns, proceed to Step 12.

Do NOT run self-improve preemptively. Only on `y`.

---

## Step 12 — Final summary; hand to human

Report a single markdown block to the human:

```markdown
## /night complete — {Feature title}

**PR:** {URL} (squashed, ready to merge)
**Branch:** feat/{slug}
**Worktree:** {path}

**Tasks delivered ({N}):**
| # | Title | Tester | PM | PR Reviewer | CI |
|---|-------|--------|----|-------------|----|
| #{N1} | ... | PASS | ACCEPT | NO BLOCKERS | green |
| ...   | ... | ...  | ...    | ...         | ... |

**Rollup tasks ({M}):** {list, or "none"}
**Nits in PR description:** {count, or "none"}
**Self-Improve:** {ran / skipped}

Next: review the PR and merge when satisfied. Worktree stays in place; remove with `git worktree remove {path}` after merge.
```

The human merges the PR. `/night` ends here.

---

## Notes on shape

- **No batching, no parallelism within a feature.** The diagram is sequential: one task at a time. Parallelism (if any) lives at the feature level — invoke `/night` twice in two terminals if you want two features in flight.
- **The two human gates are by design.** Plan approval prevents the agent team from spending hours on a wrong-shaped feature; merge approval keeps the human in control of `main`.
- **Rollups go to the END of the queue, not interleaved.** A PM rollup or PR Reviewer rollup is implemented after all original-plan tasks are done — it's a "fix everything we missed" coordinated pass, not a per-issue patch.
- **The `commit-commands` plugin and `create-pr` skill are required, not optional.** SWE invokes them. The orchestrator does not hand-craft commit messages or `gh pr` invocations.
- **Caps stop the pipeline.** Tester FAIL Max 5 (per task), PM REJECT Max 3, PR Reviewer Max 3, On-Call Max 5. When a cap fires, surface `USER ACTION REQUIRED` and stop. Don't loop forever.
- **Self-Improve is human-gated, end-of-run only.** Don't propose updates mid-run; don't run the skill before asking.
