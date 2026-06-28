# Research Layer for Squid — Design Spec

> Status: approved shape, pending spec review.
> Date: 2026-06-02.
> Source: brainstorming session. This spec is the input to the implementation plan.

## 1. Context & goal

Squid is a Claude Code plugin that drives an **engineering** agent team (PM → SWE →
Tester → PR Reviewer → On-Call) through gated loops to turn a feature spec into a
reviewed PR. The contract layer is markdown only — agents, skills, `docs/PROCESS.md`.

This spec adds a **research layer** alongside the engineering team: an agent-driven
pipeline that takes a research question and produces a **reviewer-critiqued "directions"
memo** grounded in credible literature. The two layers chain optionally: a chosen
direction can be promoted into a `/night` feature spec (research decides *what* to build;
the engineering team builds it).

The research layer encodes a specific human workflow:

- **(a) Literature search** — targeted *or* broadly exploratory.
- **(b) Literature synthesis** — review the literature, then synthesize findings/analysis.
- **(c) Analysis → directions** — draft potential solutions/directions from the synthesis;
  a panel of role-based reviewers critiques the draft; the human reviews the revision.
- The loop **(c) → back to (a)/(b)** repeats based on what (c) reveals (human-decided).

## 2. Design principles (inherited from Squid)

- **Markdown contracts only.** No build step, no runtime tooling. New agents are `.md`
  files under `agents/`; the orchestrator is a `SKILL.md`; the lifecycle lives in a
  canonical process doc.
- **Agents are gates; the orchestrator is a manager.** The orchestrator launches agents,
  enforces gates, and verifies each report. It never does the research work itself.
- **Evidence over claims / no false confidence.** A claim is only as good as its cited,
  credibility-tagged source. "The literature says X" is not evidence; a Tier-A citation is.
- **Humans at the edges.** Two gates by design: approve the plan, review the directions.
- **Remove before you add.** Reuse existing skills (`deep-research`, `grill-me`) rather
  than rebuild; new machinery only where Squid genuinely lacks it.

## 3. Approach

**Chosen: B — lean reuse.** Add a small set of named research agents (mirroring Squid's
five), one `/research` orchestrator skill, and a canonical `docs/RESEARCH_PROCESS.md`.
For the search step, **reuse the existing `deep-research` skill** (fan-out → fetch →
adversarially-verify → cited synthesis) as the engine, plus `huggingface-papers` for the
academic/arXiv channel and `WebSearch`/`WebFetch` as fallback primitives — **do not build a
new search skill**, since `deep-research` already covers that capability. The `literature-scout`
adds only the layer those tools lack: the credibility-tier gate (§8) and a **search-as-code**
filtering pass (deterministic, reproducible dedupe + provenance filtering + coverage stats,
after research.perplexity.ai's "search as code"). Borrow `grill-me`'s "adversarial critique
with drafted answers" pattern for the reviewer step.

Rejected alternatives:

- **A — full mirror:** a complete parallel team plus standalone phase commands. Rejected
  as over-built; it duplicates search machinery `deep-research` already provides.
- **C — skills-only:** no named agents. Rejected because it loses the "agents-as-named-gates"
  ergonomics (`/agents`, `Agent(subagent_type=…)`) that make Squid coherent, and the
  reviewer roles become anonymous and un-reusable.

## 4. Architecture overview

```
raw research question
        │
        ▼
research-lead grooms → Research Plan (plan.md)
        │
        ▼
HUMAN GATE #1 — approve the plan (questions, scope, mode, sources)   ← gate 1/2
        │
        ▼
literature-scout searches (credibility-gated)  → sources.md
        │
        ▼
synthesizer  → synthesis.md  (incl. gaps & follow-up queries)
        │
        ▼
strategist drafts  → directions.md
        │
        ▼
research-reviewer ×5 IN PARALLEL  → reviews.md (per-role Blocker/Nit rollup)
        │
        ▼
strategist revises (Max 2 cycles)  → directions.md (revised)
        │
        ▼
research-lead acceptance (does this answer the question, from the user's POV?)
        │
        ▼
HUMAN GATE #2 — review the critiqued directions memo                 ← gate 2/2
        │
        ├── accept / done
        ├── loop back → refine queries, re-run from search   (human-decided)
        └── handoff → promote a direction to a /night feature spec
```

## 5. Agents (5 new files under `agents/`)

Each agent follows Squid's existing agent conventions: YAML frontmatter
(`name`, `description`, `tools`, `model`), an "Always read first" pointer to
`docs/RESEARCH_PROCESS.md` + `CLAUDE.md`, a Trigger, an Input, a numbered Workflow,
a rubric, and a Rules section. Each appends a role-tagged entry to the run's `log.md`.

| Agent | Engineering analog | Responsibility |
|---|---|---|
| `research-lead` | product-manager | Grooms the raw question into a **Research Plan**. Sets `mode` (targeted/exploratory), scope, source strategy, and success criteria. At the end, performs **user-POV acceptance** of the directions memo before hand-off. Owns "does this actually answer the question." |
| `literature-scout` | tester | Step **(a)**. Drives the search using `deep-research` (+ `huggingface-papers` for academic sources, `WebSearch`/`WebFetch` as fallback) as the engine, then applies a **search-as-code** filtering pass — deterministic, reproducible dedupe + domain-based credibility pre-filter + per-question coverage stats — and the **credibility gate** (§8), its headline duty (as the Tester's is the e2e pass). Produces a provenance-tagged `sources.md`. |
| `synthesizer` | software-engineer | Step **(b)**. Reviews `sources.md` → `synthesis.md`: themes, findings (each cited + tier-tagged), contradictions/debates, an evidence-quality assessment, and an explicit **gaps & follow-up queries** section that seeds any loop-back. |
| `strategist` | software-engineer | Step **(c) draft + revision**. Turns the synthesis into `directions.md` (candidate directions, each grounded in the synthesis with citations). After the panel runs, addresses every Blocker and re-emits the revised `directions.md` with a "Revisions made" changelog. |
| `research-reviewer` | pr-reviewer | The **panel**, as a single **parameterized** agent. The orchestrator launches it once per role (in parallel), passing the role in the prompt. Each invocation tags findings **Blocker/Nit** and writes its section of `reviews.md`. Adding/removing a role is a prompt change, not a new file. |

**Decision — `synthesizer` and `strategist` stay separate** (not merged into one "analyst").
Rationale: synthesis ("what does the literature say") and strategy ("what should we do about
it") are distinct cognitive tasks producing distinct artifacts (`synthesis.md` vs
`directions.md`); the panel reviews the directions while the synthesis is a stable input;
and five agents mirror Squid's five.

## 6. The `/research` orchestrator (`skills/research/SKILL.md`)

A `disable-model-invocation: true` skill (explicit `/research` invocation only), mirroring
`/night`'s structure. `$ARGUMENTS` is the research question (free-form text, a path to a
question file, or a topic slug). The orchestrator is a **manager** — it launches agents,
enforces the two gates, verifies each report (spot-checking that claims carry credible
citations), and never writes synthesis/directions itself.

Steps:

0. **Resolve the question.** If empty, ask the human. Surface a one-paragraph restatement.
1. **Create the run folder** `research/<topic-slug>/` (and optional `research/<slug>` branch).
   No git worktree — these are documents.
2. **research-lead grooms** → `plan.md`. Verify the plan has questions, a mode, a source
   strategy, and success criteria before forwarding.
3. **HUMAN GATE #1 — approve the plan.** `y` / `edit` / `cancel`. On `edit`, re-groom.
4. **literature-scout searches** → `sources.md`. Verify every load-bearing source is
   tier-tagged with a provenance justification; if too few credible sources, surface and stop.
5. **synthesizer** → `synthesis.md`. Spot-check that findings cite tier-tagged sources.
6. **strategist drafts** → `directions.md`.
7. **Reviewer panel (parallel).** Launch `research-reviewer` once per role (one message,
   N `Agent` calls). Collect into `reviews.md`.
8. **strategist revises** → re-emit `directions.md` (addressing all Blockers). Re-run the
   panel once if Blockers were filed. **Cap: Max 2 revision cycles.** If Blockers remain
   after cycle 2, carry them into the hand-off, flagged.
9. **research-lead acceptance** — user-POV check that the directions answer the question.
10. **HUMAN GATE #2 — review the directions memo.** Present the memo + a summary of panel
    findings + any unresolved Blockers + the synthesizer's follow-up queries. The human
    chooses: **accept** / **loop back** (re-run from step 4 with refined queries) /
    **handoff** (§11).

Caps stop the pipeline and surface `USER ACTION REQUIRED`, as in `/night`. Between the two
gates the pipeline moves forward on its own; it does not silently skip.

## 7. Artifacts & layout

A run owns `research/<topic-slug>/`:

| File | Written by | Contents |
|---|---|---|
| `plan.md` | research-lead | Research question(s); `mode: targeted\|exploratory`; in/out scope; source strategy (which of academic/web/local; named venues/authors if known); success criteria; known constraints (compute/data/time) for the feasibility reviewer. |
| `sources.md` | literature-scout | One entry per accepted source: citation, **tier (A/B)**, one-line provenance justification, relevance note, extracted key claim(s). A separate **Rejected** list with reasons (the filter leaves a trail). |
| `synthesis.md` | synthesizer | Themes/clusters; key findings (each cited + tier-tagged); contradictions/debates; evidence-quality assessment; **gaps & follow-up queries**. |
| `directions.md` | strategist | N candidate directions. Each: statement; rationale grounded in the synthesis (citations); novelty delta; feasibility assessment; risks. A recommendation/ranking. After review: a "Revisions made" changelog and an "Unresolved blockers" section (if any). |
| `reviews.md` | research-reviewer ×5 | One section per role, each with Blockers + Nits (location ref, what's wrong, why, suggested fix), then a consolidated "Blockers to resolve" list the strategist works from. |
| `log.md` | all | Append-only, role-tagged entries: `### [ROLE] YYYY-MM-DD HH:MM — subject`. Same Issue-Log discipline as Squid's tracker. |

**Version control.** Run folders are *not plugin content*. The plugin repo (and scaffolded
projects) `.gitignore` `research/` so research output never ships on a public branch. To
keep a personal research knowledge base in git, `git add -f research/<slug>/` on a private
branch or private remote that is never pushed publicly. Because the ignore rule is uniform
across branches, a stray `git add -A` cannot leak research into the public branch.

## 8. Source-credibility gate (the user's principle, encoded)

The scout tags every source:

- **Tier A — load-bearing OK:** peer-reviewed at a recognized venue; or a technical
  report/preprint from a well-known lab or an established researcher.
- **Tier B — supporting, cite with caveat:** arXiv preprint (not yet peer-reviewed) from
  attributable, credible authors; a named-expert engineering blog at a respected org.
- **Reject:** anonymous, SEO/content-farm, marketing, predatory venue, or unverifiable
  provenance.

Rules:

- Every accepted source carries a one-line provenance justification.
- **Load-bearing synthesis claims must rest on Tier A** (Tier B only with an explicit caveat).
- If the scout cannot find enough credible sources to support the plan's questions, it
  **surfaces that** rather than synthesizing on weak ground (the "no false confidence" rule).
- **When provenance is unclear, err toward Reject** — a missing source is safer than an
  uncredible one silently treated as load-bearing.
- Rejected sources are listed with reasons — the credibility filter is auditable.

**Search-as-code (how the gate is applied).** After research.perplexity.ai's "search as code",
the scout applies the gate as *reproducible code*, not ad-hoc judgement: it collects candidate
hits (via `deep-research` / `huggingface-papers` / web tools), then runs a small script
(Bash/Python) to dedupe (by DOI / arXiv-id / normalized title), reject known aggregator /
SEO / content-farm domains, flag respected-venue and lab domains as Tier-A candidates, and
compute per-question **coverage** (how many Tier-A sources support each plan question — this
drives the insufficient-sources check and the gaps list). The model judges only the gray zone
(final Tier A vs B, the provenance justification). The script and its output are the auditable
trail (kept in the git-ignored run folder). Deterministic compute also keeps token use down on
large result sets. For small result sets, reasoning-based filtering is acceptable — the script
is the method when volume makes it worthwhile, not a hard requirement.

## 9. Reviewer panel

Five roles, run in parallel. Each tags findings **Blocker / Nit** (reusing Squid's Severity
Rule, adapted to research).

| Role | Reviews for |
|---|---|
| **Methodologist / skeptic** | Rigor: validity, statistics, reproducibility, confounds, overclaiming, evidence quality. Blocks when a direction rests on a misread of evidence or an unsupported leap. |
| **Domain expert** | Prior art & correctness: does the synthesis read the literature right? Is a "novel" direction already published? Is seminal work missing? Blocks on factual misreadings or missing key work. |
| **Novelty & impact** | Is the direction genuinely new and worth pursuing? Delta over existing work; who benefits. Blocks when a direction is a known result repackaged, or impact is negligible. |
| **Feasibility / practitioner** | Executable with realistic data/compute/time (per `plan.md` constraints)? Blocks when an infeasible direction is presented as feasible. |
| **Clarity reviewer** (junior-staff lens) | Can a grad student / new hire follow *what was done and why*? Reviews accessibility of method notes and documentation: jargon explained, assumptions stated, evidence→direction chain legible. **Blocks on incomprehensibility, not on correctness** — purely a communication-quality gate. |

Severity, adapted:

- **Blocker** = a defect that makes the memo misleading, wrong, or unusable: an unsupported
  load-bearing claim, a misread cited source, a "novel" direction that is already published,
  an infeasible direction presented as feasible, or (clarity) a section a junior literally
  cannot follow.
- **Nit** = non-blocking improvement: phrasing, an extra citation worth adding, a minor caveat.

The strategist must resolve every Blocker; the panel re-reviews once (**Max 2 cycles**).
Unresolved Blockers after cycle 2 are surfaced to the human at gate #2, flagged — never
silently dropped.

## 10. Loop-back mechanics

`synthesis.md` and `directions.md` each end with an explicit **gaps & follow-up queries**
section. At gate #2, "loop back" re-enters the pipeline at the search step (step 4) seeded
by those queries, with a refined scope the human can edit. Loop-back is **always
human-decided** — there is no automatic loop-back and no auto-cap on rounds (the human gate
is the control).

## 11. Optional `/night` handoff

At gate #2, "handoff" promotes a chosen direction into an engineering feature spec:

1. The orchestrator writes `docs/features/<slug>.md` from the chosen direction (problem,
   goal, scope, acceptance-shaped notes, links back to `research/<topic-slug>/`).
2. It suggests the next command: `/grill-me docs/features/<slug>.md` (to harden the spec),
   then `/night docs/features/<slug>.md`.

The handoff stops at writing the feature spec and recommending the command — it does not
auto-invoke `/night`. Research → build stays a human decision.

## 12. Canonical doc — `docs/RESEARCH_PROCESS.md`

The single source of truth for the research lifecycle, analogous to `docs/PROCESS.md`:
the a→b→c loop, the two gates, the credibility tiers, the reviewer panel + severity, the
revision cap, the artifact layout, and the `/night` handoff. Every research agent reads it
first. `docs/PROCESS.md` gets a one-line cross-reference pointing to it.

## 13. Files to create / modify

**Create:**

- `docs/RESEARCH_PROCESS.md` — canonical research lifecycle.
- `agents/research-lead.md`
- `agents/literature-scout.md`
- `agents/synthesizer.md`
- `agents/strategist.md`
- `agents/research-reviewer.md` (parameterized by role)
- `skills/research/SKILL.md` — the orchestrator.

**Modify:**

- `README.md` — add the research layer to "What you get" and a short "how it works" note.
- `CLAUDE.md` — add the research agents/skills to the repo map and editing conventions;
  note `docs/RESEARCH_PROCESS.md` as a second canonical lifecycle doc.
- `docs/PROCESS.md` — one-line cross-reference to `docs/RESEARCH_PROCESS.md`.
- `.gitignore` — add `research/` (run output is user data, not plugin content; §7).
- `.claude-plugin/plugin.json` — version bump at ship time (per release process).

## 14. Defaults & decisions

- **Targeted vs. exploratory** is a `mode` field on `plan.md`, set by research-lead, approved
  at gate #1. Targeted = narrow query set, depth over breadth; exploratory = broad landscape
  sweep, breadth first.
- **Reviewer panel = one parameterized agent**, launched once per role, in parallel.
- **Caps:** revision Max 2 cycles; search loop-back human-decided (no auto-cap).
- **No git worktree** — documents, not code. Optional *private* `research/<slug>` branch for self-review.
- **`research/` is git-ignored** on the public branch (run output is user data). Personal
  knowledge-base use is opt-in via `git add -f research/<slug>/` on a private branch/remote
  that is never pushed publicly — see §7.
- **Per-invocation, not a backlog.** Like `/night`, `/research` takes one question per run.
- **The search step reuses `deep-research`** as the engine (+ `huggingface-papers` for academic
  sources, `WebSearch`/`WebFetch` as fallback); the scout always owns the credibility-tier gate
  and the search-as-code filtering pass. Prefer invoking `deep-research` at whichever level the
  harness allows — orchestrator-level is guaranteed; scout-level if subagent skill-invocation is
  supported, else the orchestrator runs `deep-research` first and passes results to the scout.
  **No new search skill is built** — `deep-research` already covers the general capability (§15).

## 15. Out of scope (v1)

- Standalone phase commands (`/lit-search`, `/synthesize`, `/critique`). Loop-back is handled
  inside `/research`; split phases out later only if real usage demands it.
- A new literature-search skill. `deep-research` (already available) + `huggingface-papers`
  cover the general search / verify / synthesis capability; the scout reuses them and adds only
  the credibility-tier + search-as-code layer. (Extractable into a thin reusable skill later if
  standalone credibility-gated search is wanted, outside `/research`.)
- Automatic loop-back or auto-promotion to `/night`.
- A research-specific `self-improve` pass (revisit after the layer sees use).
- Citation-manager / reference-format export (BibTeX, etc.).

## 16. Open questions

Resolved during spec review (2026-06-02):

1. **Spec doc home** — confirmed: `docs/superpowers/specs/`.
2. **`research/` version control** — confirmed: git-ignored on the public branch; committed
   for personal use via `git add -f` on a private branch/remote (see §7 and §14).

None remaining.
