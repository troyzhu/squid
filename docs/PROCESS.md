# Development Process

This document defines the agent-team workflow for this project. It is the **single source of truth** for the pipeline. Every agent (PM, SWE, Tester, On-Call) reads this file before acting, and the `/night` and `/day` skills drive the loops described here.

## Modes

The agent team ships with two entry points:

| Mode | Entry | Gates active | Commits? | When to use |
|---|---|---|---|---|
| Night | `/night [batch-size]` | PM-groom, Tester, PM-accept, On-Call CI | Yes — agent commits | Unattended batch runs, draining the backlog, overnight work |
| Day | `/day [task]` | Tester only | No — human commits | Supervised single-task work, fast iteration, human in the loop |

**Night mode** runs the full pipeline described below. It's engineered for unattended runs: the PM absorbs spec ambiguity up front (grooming) and catches user-experience regressions at the end (acceptance); On-Call absorbs CI regressions after push. Parallel batches, worktree isolation, and rubber-stamp spot-checks keep the loop honest with no human present.

**Day mode** is the lean counterpart. The human is supervising in real time and plays the PM and On-Call roles themselves — so those stages are skipped. Only the Tester gate remains automated (it's the one check that's genuinely hard for a human to replicate, since it runs the whole suite and cross-references every AC). Day mode handles one task per invocation, does not commit, and hands the uncommitted diff back to the human for review. Everything else — agent role definitions, tracker format, Definition of Done, and the false-confidence rules — is shared between the two modes.

## Lifecycle (night mode)

Every night-mode task moves through this sequence:

```
PM grooms  →  SWE implements  →  Tester verifies  →  PM accepts  →  Commit & push  →  On-Call watches CI
(raw spec)    (code + tests,     (runs all tests,    (user POV     (only after PM    (fixes failures,
              uncommitted)        evidence-based)     review)        accepts)          re-runs CI)
```

Day mode collapses the sequence to `SWE implements → Tester verifies → human reviews and commits`.

## Agents

Four sub-agents plus the orchestrator (the top-level Claude Code session).

| Agent | File | Role |
|---|---|---|
| Orchestrator | `CLAUDE.md` + `.claude/skills/night/SKILL.md` / `.claude/skills/day/SKILL.md` | Picks tasks, launches agents, enforces the pipeline. Never writes code itself. |
| Product Manager | `.claude/agents/product-manager.md` | Grooms raw tasks into specs (start) + user-perspective acceptance review (end) |
| Software Engineer | `.claude/agents/software-engineer.md` | Implements code + tests; does NOT commit until Tester PASS |
| Tester | `.claude/agents/tester.md` | Runs the full suite; verifies every acceptance criterion with evidence; reports PASS/FAIL |
| On-Call Engineer | `.claude/agents/oncall-engineer.md` | Monitors CI/CD after push; reopens, fixes, and closes failures |

## Responsibility Model

Every role owns their deliverable. Quality is not centralized — it is distributed across the team.

| Role | Owns | Accountable For |
|---|---|---|
| PM | The whole feature — UX, functionality, quality | Ensuring the feature actually works as the user expects. If PM says "accepted" and the user finds it broken, that's a PM failure. The PM is the user's last line of defense. |
| SWE | Code correctness, tests | Writing code that works and tests that prove it. If the Tester finds bugs, that's an SWE failure. |
| Tester | Verification, evidence | Providing proof that things work — not claims. If the Tester says "PASS" without running the test, that's a Tester failure. |
| Orchestrator | The team | Managing the pipeline and verifying each agent did their job. If an agent cuts corners and the orchestrator accepts it, that's an orchestrator failure. |
| On-Call | Pipeline health after push | Catching and fixing CI breakages. If a red pipeline sits red and unattended, that's an On-Call failure. |

**The PM owns the user experience.** The PM is the user's advocate. When accepting a deliverable, the PM must verify the feature works from the user's perspective — not just that code was written and tests pass. The PM should:

- Verify actual output / UI matches what the user asked for.
- Check test output, logs, and any generated artifacts — not just agent claims.
- Reject if the deliverable doesn't meet user expectations.
- Think "if the user checks this right now, will they be satisfied?"

**The orchestrator is a MANAGER, not an implementer.** The orchestrator NEVER writes or modifies code. It only touches tracker files, task panel items, and git commits (after PM accepts). Writing code, running tests, reviewing the diff — all of that belongs to the sub-agents.

## False Confidence Is the Worst Outcome

The single worst thing the orchestrator can do is tell the user "it works" when it doesn't. This destroys trust. Four rules to prevent it:

1. **Never say "it works" unless you have firsthand evidence.** An agent saying "PASS" is not firsthand evidence. Actual test output showing real data, logs showing real requests, artifacts produced by the code — that is evidence.
2. **If you're not sure, say you're not sure.** "The Tester reports PASS but I haven't independently verified" is always better than "it works." Honesty about uncertainty is valued. False certainty is not.
3. **If something contradicts user experience, the user is right.** The user is testing the real app. If they say it's broken, it's broken — regardless of what any test or agent claims. Investigate why the test passed when the feature is broken.
4. **Treat every "it works" claim as a promise.** Before making it, ask yourself: "If the user checks right now, will it actually work?" If you can't answer yes with evidence, don't make the claim.

The orchestrator must verify each agent's results before forwarding them. When the Tester or PM reports back:

1. Re-read the task's acceptance criteria line by line.
2. Check each criterion against the agent's report — did the agent actually address it, or just say "tests pass"?
3. **Reject and re-launch if any criterion was skipped** — with specific instructions about what was missed.

Common failures to watch for:

- AC says "run e2e test" → agent wrote the test file but never ran it. **REJECT.**
- AC says "verify CLI output" → agent only ran unit tests. **REJECT.**
- AC says "no regressions in module X" → agent only ran new tests. **REJECT.**
- AC says "logs show correct values" → agent checked that the log call compiles. **REJECT.**

"Tests pass" is NEVER sufficient if the AC requires runtime or visual verification.

## Pipeline Always Moves Forward

- **NEVER wait for user input.** The pipeline runs autonomously. If something needs the user (configuring a secret, testing on their machine, confirming a deployment), write it as a `USER ACTION REQUIRED` entry in the task file and move on to the next task. Do not stop the pipeline.
- **NEVER block on dependencies within a batch.** If task A is groomed but task B is still grooming, launch the SWE for A immediately. Each task's pipeline is independent — launch agents as soon as their predecessor step completes, regardless of other tasks in the batch.
- **Always queue a "pick next" task.** When starting a batch, immediately create a `[Pull next]` task panel item blocked on the current batch's commit. The loop stops only when the backlog is empty, not after one batch.
- **One agent per task.** When working on N tasks in parallel, launch N separate agents — never combine multiple tasks into a single agent call.

## Orchestrator Commit Rules

- Commit code ONLY after the PM accepts.
- The orchestrator does not `git add` arbitrary file trees — the SWE stages specific files, then the orchestrator commits.
- The commit message ends with `Closes #N` (issue) or moves the tracker file to `done/` in the same commit.
- If the SWE's work includes `[HUMAN]` acceptance criteria: use `Refs #N`, add the `human` label / note, do NOT close the task.

## Definition of Done

"Done" has a specific meaning at each stage. Each role has concrete checkboxes.

### SWE Done

- [ ] Code follows existing patterns (see `CLAUDE.md`).
- [ ] Unit tests written and passing — **actual test output appended to the task log**.
- [ ] Format + lint clean (`make format-check && make lint-check`) — output appended to log.
- [ ] For any runtime behavior: the code was actually exercised (CLI invoked, service started, endpoint called) — output appended to log.
- [ ] For bug fixes: TDD — a failing regression test was added FIRST, confirmed to fail, then the fix, then confirmed to pass. Both outputs appended to log.
- [ ] If a verification step couldn't be completed, explicitly say `NOT RUN — reason` (never silently skip).

"It compiles" is NOT done. "I ran it, here's the output" IS done.

### Tester Done

- [ ] Every acceptance criterion walked through and marked PASS / FAIL with evidence (command output, file:line, artifact path).
- [ ] Full suite run (`make unit-tests`, integration if relevant) — output appended to log.
- [ ] Any SWE `NOT RUN` items: either run them now or explain why they can't run.
- [ ] Any suspicious results investigated (a 3-second pass on a multi-step flow is a red flag — check what was actually executed).
- [ ] Verdict: PASS or FAIL, with reasons.

"I read the diff and it looks right" is NOT done. "I ran every test, walked every AC, here's the evidence" IS done.

### PM Done

- [ ] Reviewed the Tester's evidence — read every log entry, check artifact paths.
- [ ] Verified each user story has a corresponding test that passed.
- [ ] Walked through the feature from the user's perspective.
- [ ] Any silently-dropped scope: filed as a new task and linked.
- [ ] Verdict: "If the user checks this right now, they will be satisfied" — yes or no?

"QA said PASS" is NOT done. "I reviewed the evidence, I guarantee user satisfaction" IS done.

### Orchestrator Done

- [ ] PM gave a concrete verdict with evidence references (not just "ACCEPTED").
- [ ] PM's evidence matches the acceptance criteria (orchestrator spot-checks).
- [ ] No contradictions with user feedback.
- [ ] Commit only after all the above.

## No Silent Descoping

The PM must NEVER silently drop acceptance criteria. If something is too large or out of scope:

1. Call out what is being descoped and why.
2. File a new `tracker/NNN-{slug}.todo.md` (or GitHub issue) for each descoped item.
3. The descoped items must reference the original task so the trail is preserved.

## Issue Log (single source of truth)

Every agent MUST append log entries to the task file as they work. The task file is the single source of truth for what happened.

Each agent appends to a `## Log` section with timestamped entries:

```markdown
## Log

### [PM] 2026-04-20 12:30 — Grooming
- Researched related code: {file paths}
- Identified dependencies: #N1, #N2
- Wrote 6 acceptance criteria, 4 user stories

### [SWE] 2026-04-20 14:00 — Implementation
- Created `src/{{pkg}}/...`
- Added 8 unit tests; `make unit-tests` → 12 pass, 0 fail
- Files modified: ...

### [Tester] 2026-04-20 14:45 — QA
- AC 1-5: PASS (evidence inline)
- AC 6: FAIL — {expected vs actual}
- VERDICT: FAIL

### [SWE] 2026-04-20 15:10 — Fix
- Fixed AC 6; tests 13 pass, 0 fail

### [Tester] 2026-04-20 15:25 — QA re-review
- All AC PASS
- VERDICT: PASS

### [PM] 2026-04-20 15:40 — Acceptance
- Reviewed evidence; user satisfaction verified
- VERDICT: ACCEPT
```

Format: `### [ROLE] YYYY-MM-DD HH:MM — Short subject`. Entries are append-only; do not rewrite history.

## Orchestrator Workflow

```
Raw task
    │
    ▼
Product Manager ─────► grooms into agent-ready spec (AC + BDD scenarios)
    │
    ▼
Orchestrator picks groomed task
    │
    ├─► Software Engineer ──► writes code + tests (uncommitted)
    │           │
    │           ▼
    │     Tester ──► runs tests, verifies AC, reports PASS/FAIL
    │           │
    │     ┌─────┴─────┐
    │     │           │
    │   FAIL        PASS
    │     │           │
    │     ▼           ▼
    │   SWE fixes   Product Manager ──► acceptance review (user POV)
    │   (loop)            │
    │               ┌─────┴──────┐
    │             REJECT       ACCEPT
    │               │            │
    │               ▼            ▼
    │            SWE fixes    SWE commits + pushes (Closes #N)
    │            (loop)            │
    │                              ▼
    │                       On-Call ──► watches CI, fixes any failure
    │
    └─► Pick next batch
```

## Mandatory Steps (never skip)

- Every task goes through **all** stages: PM groom → SWE implement → Tester verify → PM accept → commit → On-Call CI check.
- **Tester must actually run the full suite**, not just review code. The QA report must include test counts by type (unit, integration, e2e if applicable).
- **Tester must update acceptance criteria checkboxes** in the task body (`- [ ]` → `- [x]`) for every criterion they verified.
- **Never commit without Tester PASS**, even for "trivial" changes. The whole point of the pipeline is that the agent who writes code does not also decide whether it is correct.
- **Never use `git add -A` / `git add .`**. Always commit specific files, with a commit message that ends in `Closes #N` (issue) or appropriate tracker reference.
- **After push, always run On-Call Engineer** to check CI. Don't just "look manually."

## How to Pick Tasks

1. List open tasks in the active tracker (see "Tracker Modes" below).
2. Skip tasks tagged `needs-grooming` (groom them first via PM agent — typically in parallel/background, see Continuous Pipeline).
3. Skip tasks tagged `human` (waiting on manual verification).
4. Skip tasks whose `Depends on:` field references still-open tasks.
5. Pick the **lowest-numbered** open groomed tasks first (lower number = more foundational).
6. Default batch size: **2 tasks in parallel**. Configurable via `/night [batch-size]`. (`/day` is single-task, always — no batching.)
7. When running >1 SWE agent in parallel on different tasks, launch each with `isolation: "worktree"` so concurrent file writes don't overwrite each other.

## Continuous Pipeline

The pipeline must keep itself fed. When the orchestrator starts a batch, it immediately queues a "pick next batch" task that depends on the current batch's commit step. This makes the loop continuous: as soon as Batch N commits, Batch N+1 starts. Stop only when the backlog is empty.

```
Batch N: groom → implement → verify → accept → commit
                                                    │
                                                    ▼
                                              Pick Batch N+1 → ...
```

## Human Verification Escape Hatch

Some acceptance criteria can't be verified by an agent: OAuth flows, third-party redirects, visual judgment, real payment captures. The PM marks these `[HUMAN]` during grooming.

When a task passes all agent reviews **but has `[HUMAN]` criteria**:

1. Commit and push the code (use `Refs #N`, not `Closes #N` — don't auto-close).
2. Add the `human` label to the issue/task.
3. Comment listing the criteria that need manual verification.
4. **Do NOT close the task** — leave it open for the human to verify and close.
5. Continue to the next task; don't block on the human.

## Tracker Modes

This template supports two trackers. Pick one per project; document the choice at the top of this file.

### Default: file-based tracker (`tracker/`)

Filename encodes the state:

```
tracker/
├── 001-add-feature.todo.md         # raw, awaiting grooming
├── 002-pagination.groomed.md       # PM-groomed, ready for SWE
├── 003-search.in-progress.md       # SWE/Tester actively working
└── done/
    └── 000-bootstrap.md            # accepted, committed
```

State transitions are file renames:
- New task → write `NNN-slug.todo.md`
- After PM grooming → rename to `NNN-slug.groomed.md`
- When SWE picks up → rename to `NNN-slug.in-progress.md`
- After PM accepts and commit lands → `git mv` to `done/NNN-slug.md`

Agents append their reports as sections within the file (`## SWE Report`, `## QA Report`, `## PM Acceptance`) instead of separate comments. See `tracker/README.md` for the full format.

### Opt-in: GitHub Issues

Use `gh issue ...` for everything: PM edits the issue body during grooming, SWE/Tester comment on the issue with reports, commit messages use `Closes #N`. Best when the project has visible coordination needs (multiple humans, public repo).

To switch a project from file-based to GitHub Issues mode:

1. Set `TRACKER_MODE: gh` at the top of this file (replace the default).
2. Migrate any open `tracker/*.md` files into GitHub Issues (or leave them; agents will treat the file-based ones as legacy).
3. Agents check the `TRACKER_MODE` line before acting.

**Active tracker for this project:** `TRACKER_MODE: file` *(change to `gh` to switch)*

## Tech Stack Hooks

Agents reference these stack-agnostic conventions instead of hardcoded tools. Each project's `CLAUDE.md` fills in the specifics.

- **Format / lint**: `make format-fix && make lint-fix && make format-check && make lint-check`
- **Pre-commit**: `make pre-commit`
- **Unit tests**: `make unit-tests`
- **Integration tests**: `make integration-tests`
- **All tests**: `make tests`
- **Build**: `make build`
- **Run any project-level Python**: `uv run python ...`

## Reuse Existing Skills

Agents do not duplicate logic that lives in the project's skill catalog:

- **Test writing conventions** — defer to `.claude/skills/testing-python/SKILL.md`.
- **PR creation** — defer to `.claude/skills/create-pr/SKILL.md` (when the project pushes via PR rather than directly to `main`).
- **Commit messages** — defer to the `commit-commands` plugin.
- **Code review** — Tester may invoke the `code-review` plugin as an extra signal.
- **Self-improvement** — orchestrator runs `.claude/skills/self-improve/SKILL.md` at end of long sessions to capture corrections back into this file or memory.

## When to Use Which Workflow

- **Direct chat / single-session**: trivial edits, one-shot questions, typo fixes.
- **`/day`**: a single feature, bug fix, or refactor you want to ship under active supervision with a Tester gate but without PM ceremony. You stay in the loop and commit yourself.
- **`/night`**: multi-task projects, overnight runs, parallel work across independent tasks, anything where you want both PM gates plus On-Call enforced.
