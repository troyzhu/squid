# Research Layer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a research layer to the Squid plugin — five research agents and a `/research` orchestrator that turn a research question into a credibility-grounded, reviewer-critiqued "directions" memo, with an optional handoff into the existing `/night` engineering pipeline.

**Architecture:** Pure markdown contracts, mirroring Squid's engineering team. A canonical `docs/RESEARCH_PROCESS.md` is the single source of truth; five agents (`research-lead`, `literature-scout`, `synthesizer`, `strategist`, parameterized `research-reviewer`) are launched by a `/research` orchestrator skill through a two-gate pipeline (approve plan → autonomous run → review directions). Source data lives in git-ignored `research/<slug>/` folders.

**Tech Stack:** Markdown only. No build, no runtime, no test suite (per `CLAUDE.md`). Verification = `claude plugin validate` + content/cross-reference checks + manual `--plugin-dir` smoke test.

**Source spec:** `docs/superpowers/specs/2026-06-02-research-layer-design.md` (approved). Section refs below (e.g. "spec §8") point there.

---

## Testing approach for this repo (read first)

This plugin ships markdown, not code. There is no pytest/jest and no `make test`. Each task's "verify" steps therefore use:

1. **`claude plugin validate`** (run from repo root) — validates `plugin.json`, and every agent/skill/command frontmatter block. This is the closest thing to a compiler; run it after any frontmatter change. Expected output on success: a report with no errors (e.g. `✔` lines / "valid").
2. **Content/cross-reference greps** — confirm required sections and cross-references exist (exact `grep` commands given per task).
3. **Manual smoke test** (final task only) — load the working tree with `claude --plugin-dir .` and confirm the agents/skill appear and the first gate works.

Commits are per-file (specific paths, never `git add -A`), Conventional Commits subject, ending with the `Co-Authored-By` trailer. Work happens on the existing `feat/research-layer` branch.

---

## Scope check

This spec is **one cohesive subsystem** (a research layer), not several independent ones — the agents only function together via the orchestrator. It stays a single plan. Tasks are dependency-ordered: the canonical doc first (everything references it), then agents (the orchestrator references them), then the orchestrator, then wiring, then validation.

---

## File structure

**Create:**

| File | Responsibility |
|---|---|
| `docs/RESEARCH_PROCESS.md` | Canonical research lifecycle: loop, two gates, credibility tiers, panel + severity, caps, artifact layout, handoff. Every research agent reads it first. |
| `agents/research-lead.md` | Grooms question → `plan.md`; user-POV acceptance of the directions memo. |
| `agents/literature-scout.md` | Credibility-gated multi-source search → `sources.md`. Headline duty: the credibility gate. |
| `agents/synthesizer.md` | `sources.md` → `synthesis.md` (themes, findings, contradictions, gaps & follow-up queries). |
| `agents/strategist.md` | `synthesis.md` → `directions.md`; revises after panel review. |
| `agents/research-reviewer.md` | Parameterized panel reviewer; one role per invocation; tags Blocker/Nit. |
| `skills/research/SKILL.md` | The two-gate `/research` orchestrator. |

**Modify:**

| File | Change |
|---|---|
| `.gitignore` | Add `research/` (run output is user data, not plugin content). |
| `README.md` | Add the research layer to "What you get" + a short how-it-works note. |
| `CLAUDE.md` | Add research agents/skills to the repo map; note the second canonical lifecycle doc. |
| `docs/PROCESS.md` | One-line cross-reference to `docs/RESEARCH_PROCESS.md`. |

**Deferred to ship time (not a task here):** `.claude-plugin/plugin.json` version bump, done via `scripts/release.sh` per `CLAUDE.md`.

---

## Task 1: Canonical lifecycle doc

**Files:**
- Create: `docs/RESEARCH_PROCESS.md`

Model the structure on `docs/PROCESS.md` (read it first for tone, table style, and the "Issue Log" / "Responsibility Model" / "False Confidence" patterns to mirror).

- [ ] **Step 1: Write `docs/RESEARCH_PROCESS.md`**

It MUST contain these sections (in order):

1. **Intro** — "single source of truth for the research pipeline; every research agent reads this first," analogous to `docs/PROCESS.md`'s opening.
2. **Lifecycle diagram** — reproduce the pipeline diagram from spec §4 verbatim (the ASCII flow from "raw research question" through both gates).
3. **Agents table** — the 5 agents + orchestrator, with one-line roles (from spec §5).
4. **The two human gates** — Gate #1 (approve plan), Gate #2 (review directions: accept / loop-back / handoff).
5. **Source-Credibility Gate** — reproduce spec §8 in full: Tier A / Tier B / Reject definitions; the rules (provenance justification on every source; load-bearing claims need Tier A; insufficient credible sources → surface; **err toward Reject when provenance is unclear**; rejected sources listed with reasons).
6. **Reviewer Panel** — the 5 roles table (spec §9) + the adapted Severity Rule (Blocker vs Nit definitions from spec §9) + revision cap (Max 2 cycles).
7. **Iteration caps** — table: revision Max 2 (counter resets per directions draft); scout insufficient-sources → surface & stop; loop-back human-decided (no auto-cap).
8. **Artifacts & layout** — the `research/<slug>/` table (spec §7) + the Version-control note (spec §7: git-ignored on public branch, `git add -f` on a private branch for personal use).
9. **Issue Log** — append-only role-tagged entries `### [ROLE] YYYY-MM-DD HH:MM — subject` in `log.md` (mirror `docs/PROCESS.md`'s Issue Log section).
10. **Loop-back mechanics** — seeded by the synthesis "gaps & follow-up queries"; human-decided at Gate #2 (spec §10).
11. **`/night` handoff** — chosen direction → `docs/features/<slug>.md` → recommend `/grill-me` then `/night` (spec §11). Stops at writing the feature spec; never auto-invokes `/night`.
12. **Responsibility Model** — who owns what (lead owns "does this answer the question"; scout owns credibility; synthesizer owns faithful synthesis; strategist owns directions; reviewers own their dimension; orchestrator verifies every report). Mirror `docs/PROCESS.md`'s Responsibility Model.
13. **No False Confidence (research variant)** — "the literature says X" is not evidence; a Tier-A citation is. The orchestrator spot-checks that load-bearing claims carry credible citations before forwarding.

- [ ] **Step 2: Verify required sections present**

Run:
```bash
grep -nE '^## |^### ' docs/RESEARCH_PROCESS.md
```
Expected: headings for all 13 sections above, including "Source-Credibility Gate", "Reviewer Panel", "Iteration caps", "Artifacts", "Issue Log", "/night handoff".

- [ ] **Step 3: Verify tier rule is concrete (no vagueness)**

Run:
```bash
grep -nE 'Tier A|Tier B|Reject|err toward Reject|Tier-A' docs/RESEARCH_PROCESS.md
```
Expected: matches for all three tiers and the err-toward-Reject rule.

- [ ] **Step 4: Commit**

```bash
git add docs/RESEARCH_PROCESS.md
git commit -m "$(cat <<'EOF'
docs(research): add RESEARCH_PROCESS canonical lifecycle

Single source of truth for the research pipeline: two-gate lifecycle,
source-credibility tier gate, 5-role reviewer panel + severity, caps,
artifact layout, loop-back, and the /night handoff.

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 2: `research-lead` agent

**Files:**
- Create: `agents/research-lead.md`

Mirror the section scaffolding of `agents/product-manager.md` (frontmatter, "Always read first", Trigger, Input, numbered Parts, Definition of Done, Rules). Only the research-specific content below is novel; everything else follows that file's pattern.

- [ ] **Step 1: Write `agents/research-lead.md`**

Frontmatter (exact):
```yaml
---
name: research-lead
description: Grooms a raw research question into a Research Plan (key questions, targeted-vs-exploratory mode, scope, source strategy, success criteria, constraints) before the run, and performs user-POV acceptance of the directions memo at the end. Use as the first and last step of the /research pipeline. Does NOT search, synthesize, or draft directions itself.
tools: Read, Bash, Glob, Grep, Edit, Write
model: opus
---
```

Body sections:
- **Role** — owns "does this actually answer the question." Grooms up front; accepts at the end. Never searches/synthesizes/drafts.
- **Always read first** — `docs/RESEARCH_PROCESS.md`, `CLAUDE.md`.
- **Trigger / Input** — launched by `/research`; input is the raw question (Part 1) or the revised `directions.md` + `plan.md` (Part 2).
- **Part 1 — Grooming.** Produce `research/<slug>/plan.md` with EXACTLY these fields:
  ```markdown
  # Research Plan — {question title}

  **Question(s):** {the key research question(s), as a short list}
  **Mode:** targeted | exploratory
  **Scope — in:** {what's covered}
  **Scope — out:** {explicitly excluded}
  **Source strategy:** {academic / web / local; named venues or authors if known}
  **Success criteria:** {what makes the directions memo good enough — e.g. ">=3 credible directions, each grounded in >=2 Tier-A sources, each with a feasibility verdict"}
  **Constraints (for feasibility review):** {compute / data / time / expertise available}
  ```
  Choosing `mode`: targeted = a narrow, well-formed question (depth over breadth); exploratory = a landscape/"what's out there" question (breadth first). State the reason for the chosen mode in one line.
- **Part 2 — Acceptance.** Walk the directions memo from the user's POV against `plan.md`'s success criteria. Verdict ACCEPT or REJECT-with-reasons. On concerns, list them concretely (which direction, what's missing) — do not rewrite the memo (that's the strategist's job); hand concerns back so the orchestrator can route a revision. Confirm any "Unresolved blockers" are surfaced, not buried.
- **Definition of Done** — plan has all fields; mode justified; success criteria are checkable; (Part 2) acceptance cites the success criteria.
- **Rules** — never search/synthesize/draft; never silently descope a question (file it explicitly); append a `[Research Lead]` log entry.

- [ ] **Step 2: Validate frontmatter**

Run: `claude plugin validate`
Expected: no errors; `research-lead` recognized as an agent.

- [ ] **Step 3: Verify plan template fields present**

Run:
```bash
grep -nE 'Mode:|Source strategy:|Success criteria:|Constraints' agents/research-lead.md
```
Expected: all four field labels present.

- [ ] **Step 4: Commit**

```bash
git add agents/research-lead.md
git commit -m "$(cat <<'EOF'
feat(research): add research-lead agent

Grooms a question into a Research Plan and does user-POV acceptance of
the directions memo. Two-part role mirroring product-manager.

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 3: `literature-scout` agent

**Files:**
- Create: `agents/literature-scout.md`
- Modify: `docs/RESEARCH_PROCESS.md` (add a "search-as-code" note to the Source-Credibility Gate section — spec §8)

Mirror the section scaffolding of `agents/tester.md` (its "headline duty" framing maps directly onto the credibility gate). Note this agent needs web tools. **The search step reuses the existing `deep-research` skill (+ `huggingface-papers` for academic sources, `WebSearch`/`WebFetch` fallback) as the engine — no new search skill is built; the scout adds the credibility-tier gate + a reproducible "search-as-code" filtering pass. See spec §3/§5/§8/§14/§15.**

- [ ] **Step 1: Write `agents/literature-scout.md`**

Frontmatter (exact):
```yaml
---
name: literature-scout
description: Runs credibility-gated multi-source literature search for an approved Research Plan, driving deep-research / huggingface-papers / web tools as the engine, and produces a provenance-tagged sources.md. Headline duty is the source-credibility gate (Tier A/B/Reject) applied as reproducible search-as-code — only verifiable, respected-source material passes. Use as step (a) of the /research pipeline, after the plan is approved.
tools: Read, Bash, Glob, Grep, Edit, Write, WebSearch, WebFetch
model: opus
---
```

Body sections:
- **Role** — find credible sources for `plan.md`'s questions; the credibility gate is the headline duty (the way the Tester's is the e2e adversarial pass).
- **Always read first** — `docs/RESEARCH_PROCESS.md`, `CLAUDE.md`.
- **Trigger / Input** — launched by `/research` after Gate #1; input is the approved `plan.md`.
- **Workflow:**
  1. Read `plan.md`; note `mode`. Targeted → narrow, deep query set on the named topic/authors/venues. Exploratory → broad landscape sweep, then deepen on the strongest clusters.
  2. **Drive the search engine.** Prefer the `deep-research` skill for fan-out + fetch + adversarial verification; use `huggingface-papers` for arXiv/HF academic sources; fall back to `WebSearch`/`WebFetch`. For a local corpus, read the paths named in `plan.md`'s source strategy. (If you cannot invoke `deep-research` as a subagent, the orchestrator supplies its results — work from those.)
  3. **Search-as-code filtering pass** (after research.perplexity.ai's "search as code"). Collect candidate hits into a scratch file, then write + run a small script (Bash, or Python via `uv run python`) in the run folder that: dedupes (by DOI / arXiv-id / normalized title); rejects known aggregator / SEO / content-farm domains; flags respected-venue and lab domains as Tier-A candidates; and computes **per-question coverage** (Tier-A count supporting each plan question). Keep the script + its output as the auditable trail. For a small result set, reasoning-based filtering is acceptable instead — the script is the method when volume makes it worthwhile.
  4. Apply the **Credibility Gate** to the survivors — judge the gray zone the script can't (final Tier A vs B, the provenance justification). Reproduce the tier rubric from `docs/RESEARCH_PROCESS.md` here so the agent is self-contained:
     - **Tier A (load-bearing OK):** peer-reviewed at a recognized venue; or a report/preprint from a well-known lab or established researcher.
     - **Tier B (supporting, cite with caveat):** arXiv preprint (not yet peer-reviewed) from attributable, credible authors; named-expert blog at a respected org.
     - **Reject:** anonymous, SEO/content-farm, marketing, predatory venue, unverifiable provenance.
     - **When provenance is unclear, err toward Reject.**
  5. **Adaptive refinement.** Where coverage is sparse for a plan question, generate refined follow-up queries and repeat from step 2 (bounded — a couple of rounds; this is the scout's internal loop, distinct from the human-gated loop-back at Gate #2).
  6. Extract key claim(s) from each accepted source.
- **Output — `research/<slug>/sources.md`** in EXACTLY this shape:
  ```markdown
  # Sources — {topic}

  ## Accepted

  ### S1 — {citation: authors, title, venue/year, link}
  - **Tier:** A | B
  - **Provenance:** {one line — why this source is credible}
  - **Relevance:** {how it bears on the plan's questions}
  - **Key claim(s):** {extracted; note page/section where useful}

  ### S2 — ...

  ## Rejected
  - {citation} — **Reason:** {anonymous / SEO / marketing / unverifiable / predatory venue}
  ```
- **Insufficient-sources rule** — if you cannot find enough credible (Tier A/B) sources to support the plan's questions, say so explicitly in `sources.md` and in your hand-off, rather than padding with weak sources. The orchestrator surfaces this.
- **Rules** — CLI/tools only, never fabricate a citation, every accepted source gets a tier + provenance line, append a `[Scout]` log entry.

- [ ] **Step 2: Validate frontmatter**

Run: `claude plugin validate`
Expected: no errors; `literature-scout` recognized; `WebSearch, WebFetch` accepted in `tools`.

- [ ] **Step 3: Verify credibility gate, search-as-code, and sources format present**

Run:
```bash
grep -nE 'Tier A|Tier B|Reject|Provenance:|err toward Reject|Insufficient|deep-research|search.as.code|coverage' agents/literature-scout.md
grep -niE 'search.as.code|coverage|deep-research' docs/RESEARCH_PROCESS.md
```
Expected: scout has all tiers, the provenance field, err-toward-Reject, the insufficient-sources rule, the `deep-research` engine reuse, and the search-as-code/coverage pass; `RESEARCH_PROCESS.md` now carries the search-as-code note.

- [ ] **Step 4: Commit**

```bash
git add agents/literature-scout.md docs/RESEARCH_PROCESS.md
git commit -m "$(cat <<'EOF'
feat(research): add literature-scout agent

Credibility-gated multi-source search producing a provenance-tagged
sources.md. Reuses deep-research / huggingface-papers as the engine and
applies the Tier A/B/Reject gate as reproducible search-as-code (dedupe
+ domain filter + per-question coverage). Errs toward Reject on unclear
provenance. Adds a search-as-code note to RESEARCH_PROCESS.md.

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 4: `synthesizer` agent

**Files:**
- Create: `agents/synthesizer.md`

Mirror the section scaffolding of `agents/software-engineer.md`.

- [ ] **Step 1: Write `agents/synthesizer.md`**

Frontmatter (exact):
```yaml
---
name: synthesizer
description: Reviews a credibility-tagged sources.md and produces synthesis.md — themes, findings (each cited and tier-tagged), contradictions/debates, an evidence-quality assessment, and an explicit gaps & follow-up queries section that seeds loop-back. Use as step (b) of the /research pipeline, after the scout. Does NOT draft directions.
tools: Read, Bash, Glob, Grep, Edit, Write, WebFetch
model: opus
---
```

Body sections:
- **Role** — turn sources into a faithful synthesis; do NOT propose solutions (that's the strategist). `WebFetch` only to re-check a source, never to add un-vetted ones.
- **Always read first** — `docs/RESEARCH_PROCESS.md`, `CLAUDE.md`.
- **Trigger / Input** — launched after the scout; input is `sources.md` + `plan.md`.
- **Workflow** — cluster into themes; extract findings, each tagged with its source IDs and tiers; record contradictions/debates between sources; assess overall evidence quality; list gaps and turn each into a concrete follow-up query.
- **Output — `research/<slug>/synthesis.md`** in EXACTLY this shape:
  ```markdown
  # Synthesis — {topic}

  ## Themes
  - {theme} — supported by S1, S3 (Tier A)

  ## Key findings
  - {finding} — cites S1 (Tier A){; caveat if only Tier B}

  ## Contradictions / debates
  - {X claims A (S2); Y claims not-A (S5)} — {state of the debate}

  ## Evidence-quality assessment
  - {overall strength; where the evidence is thin or single-sourced}

  ## Gaps & follow-up queries
  - {gap} → follow-up query: "{a concrete search query}"
  ```
- **Load-bearing rule** — every finding cites at least one source ID; a finding the directions will lean on MUST cite Tier A (or be explicitly flagged "Tier B — caveat"). Never state a finding without a citation.
- **Rules** — no new sources, no solutioning, append a `[Synthesizer]` log entry.

- [ ] **Step 2: Validate frontmatter**

Run: `claude plugin validate`
Expected: no errors; `synthesizer` recognized.

- [ ] **Step 3: Verify mandatory sections present**

Run:
```bash
grep -nE 'Key findings|Contradictions|Evidence-quality|Gaps & follow-up queries' agents/synthesizer.md
```
Expected: all four present (the gaps/follow-up section is what seeds loop-back).

- [ ] **Step 4: Commit**

```bash
git add agents/synthesizer.md
git commit -m "$(cat <<'EOF'
feat(research): add synthesizer agent

Turns sources.md into synthesis.md: themes, cited+tier-tagged findings,
contradictions, evidence-quality, and gaps & follow-up queries that seed
loop-back. No solutioning.

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 5: `strategist` agent

**Files:**
- Create: `agents/strategist.md`

Mirror `agents/software-engineer.md`. Two-part role: draft, then revise after the panel.

- [ ] **Step 1: Write `agents/strategist.md`**

Frontmatter (exact):
```yaml
---
name: strategist
description: Drafts directions.md from synthesis.md (candidate directions, each grounded with citations, with novelty/feasibility/risks and a ranking) and revises it after the reviewer panel — addressing every Blocker and emitting a changelog. Use as step (c) of the /research pipeline. Does NOT search or judge its own directions.
tools: Read, Bash, Glob, Grep, Edit, Write
model: opus
---
```

Body sections:
- **Role** — convert synthesis into actionable directions; after review, revise. Does not search or self-review.
- **Always read first** — `docs/RESEARCH_PROCESS.md`, `CLAUDE.md`.
- **Trigger / Input** — Part 1: `synthesis.md` + `plan.md`. Part 2 (revision): also `reviews.md`.
- **Part 1 — Draft `research/<slug>/directions.md`** in EXACTLY this shape:
  ```markdown
  # Directions — {topic}

  ## D1 — {direction statement}
  - **Rationale:** {grounded in synthesis}, cites S1, S4 (Tier A)
  - **Novelty delta:** {what's new vs existing work}
  - **Feasibility:** {given plan.md constraints}
  - **Risks:** {key risks / unknowns}

  ## D2 — ...

  ## Recommendation / ranking
  {directions ranked, with one-line reasoning each}
  ```
- **Part 2 — Revise.** Read `reviews.md`; address EVERY Blocker. Append to `directions.md`:
  ```markdown
  ## Revisions made (cycle {n})
  - Addressed {Blocker id} ({role}): {what changed}

  ## Unresolved blockers
  - {none | Blocker id + why it can't be resolved this cycle}
  ```
  Never silently drop a Blocker — if it can't be resolved, it goes under "Unresolved blockers" with a reason.
- **Rules** — every direction's rationale cites synthesis findings; load-bearing rationale traces to Tier A; append a `[Strategist]` log entry.

- [ ] **Step 2: Validate frontmatter**

Run: `claude plugin validate`
Expected: no errors; `strategist` recognized.

- [ ] **Step 3: Verify draft + revision structure present**

Run:
```bash
grep -nE 'Novelty delta|Feasibility:|Recommendation / ranking|Revisions made|Unresolved blockers' agents/strategist.md
```
Expected: all five present.

- [ ] **Step 4: Commit**

```bash
git add agents/strategist.md
git commit -m "$(cat <<'EOF'
feat(research): add strategist agent

Drafts directions.md from the synthesis (grounded, ranked) and revises
it after the panel, addressing every Blocker with a changelog and an
explicit unresolved-blockers section.

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 6: `research-reviewer` agent (parameterized panel)

**Files:**
- Create: `agents/research-reviewer.md`

Mirror `agents/pr-reviewer.md` (the Blocker/Nit + rollup pattern). The novelty here: ONE agent, parameterized by a `ROLE` passed in the launch prompt.

- [ ] **Step 1: Write `agents/research-reviewer.md`**

Frontmatter (exact):
```yaml
---
name: research-reviewer
description: One member of the research reviewer panel, parameterized by a ROLE the orchestrator passes in the prompt (methodologist, domain-expert, novelty-impact, feasibility, or clarity). Reviews directions.md through that single lens, tags findings Blocker or Nit, and writes its section of reviews.md. Launched once per role, in parallel, by /research. Does NOT revise the directions itself.
tools: Read, Bash, Glob, Grep, Edit, Write, WebSearch, WebFetch
model: opus
---
```

Body sections:
- **Role** — you are ONE reviewer; the orchestrator tells you which `ROLE` you are. Review `directions.md` (with `synthesis.md` as context) through that lens only. Stay in your lane.
- **Always read first** — `docs/RESEARCH_PROCESS.md`, `CLAUDE.md`.
- **Trigger / Input** — launched (in parallel with the other roles) after the strategist drafts; input is `directions.md`, `synthesis.md`, and your assigned `ROLE`.
- **Role briefs** (include all five verbatim; you act as exactly one per invocation):
  - **methodologist** — Rigor: validity, statistics, reproducibility, confounds, overclaiming, evidence quality. **Block** when a direction rests on a misread of evidence or an unsupported leap from the synthesis. Verify load-bearing claims trace to Tier-A sources.
  - **domain-expert** — Prior art & correctness. Does the synthesis read the literature right? Is a "novel" direction already published? Is seminal work missing? **Block** on factual misreadings or missing key work. You may `WebSearch` to check prior art.
  - **novelty-impact** — Is the direction genuinely new and worth pursuing? Assess the delta over existing work and who benefits if it succeeds. **Block** when a direction is a known result repackaged, or impact is negligible.
  - **feasibility** — Can this be executed with the data/compute/time/expertise in `plan.md`'s constraints? **Block** when an infeasible direction is presented as feasible; suggest the smallest viable version.
  - **clarity** (junior-staff lens) — Could a grad student or new hire follow *what was done and why*? Check that jargon is explained, assumptions stated, and the evidence→direction chain is legible. **Block ONLY on incomprehensibility, never on correctness** — that is other reviewers' job.
- **Severity Rule** (adapted from `docs/PROCESS.md`): **Blocker** = a defect that makes the memo misleading, wrong, or unusable (unsupported load-bearing claim, misread source, already-published "novel" direction, infeasible-presented-as-feasible, or a section a junior literally cannot follow). **Nit** = non-blocking improvement (phrasing, an extra citation worth adding, a minor caveat). On judgment calls, default to Nit.
- **Output — append YOUR section to `research/<slug>/reviews.md`:**
  ```markdown
  ## [{ROLE}]
  **Blockers**
  - {ROLE-prefix}{n} — {location: which direction / section} — {what's wrong} — why a Blocker — suggested fix
  **Nits**
  - {suggestion}
  ```
  Use a short id prefix per role so the strategist can reference findings: methodologist→`M`, domain-expert→`DE`, novelty-impact→`NI`, feasibility→`F`, clarity→`C` (e.g. `M1`, `F2`).
- **Rules** — review only through your assigned role; never edit `directions.md`; tag every finding; default to Nit when unsure; append a `[Reviewer:{ROLE}]` log entry.

- [ ] **Step 2: Validate frontmatter**

Run: `claude plugin validate`
Expected: no errors; `research-reviewer` recognized.

- [ ] **Step 3: Verify all five role briefs present**

Run:
```bash
grep -nE 'methodologist|domain-expert|novelty-impact|feasibility|clarity' agents/research-reviewer.md
```
Expected: all five role keys present, plus a Blocker/Nit Severity section.

- [ ] **Step 4: Commit**

```bash
git add agents/research-reviewer.md
git commit -m "$(cat <<'EOF'
feat(research): add parameterized research-reviewer panel agent

One agent, one ROLE per invocation (methodologist, domain-expert,
novelty-impact, feasibility, clarity). Tags Blocker/Nit and writes its
section of reviews.md. Launched once per role in parallel.

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 7: `/research` orchestrator skill

**Files:**
- Create: `skills/research/SKILL.md`

Mirror `skills/night/SKILL.md` closely — same orchestrator framing ("you are a MANAGER, not an implementer"), same gate/verify/cap discipline, same `Agent(...)` launch-block style. Agent `subagent_type` values use the `squid:` prefix (e.g. `squid:research-lead`), exactly as `/night` uses `squid:product-manager`.

- [ ] **Step 1: Write `skills/research/SKILL.md`**

Frontmatter (exact):
```yaml
---
name: research
description: Run the research pipeline end-to-end for one research question — research-lead grooms a plan, human approves it, then literature-scout searches (credibility-gated), synthesizer synthesizes, strategist drafts directions, a 5-role reviewer panel critiques in parallel, strategist revises, research-lead accepts, and the human reviews the directions memo to accept / loop-back / hand off to /night. Trigger when the user wants a credibility-grounded, reviewer-critiqued set of research directions, or says "/research".
disable-model-invocation: true
argument-hint: <research-question | path/to/question.md | topic-slug>
---
```

Body — orchestrator steps (mirror `/night`'s numbered structure, including the "verify before forwarding / never rubber-stamp / no false confidence" preamble adapted to citations):

- **Preamble** — you are the orchestrator/manager; you never search, synthesize, or draft. You launch agents, enforce the two gates, and **spot-check that load-bearing claims carry credible (Tier-A) citations** before forwarding any report. Read `docs/RESEARCH_PROCESS.md` first.
- **Step 0 — Resolve the question.** If `$ARGUMENTS` empty, ask. Restate in one paragraph.
- **Step 1 — Create run folder.** `slug` from the question. `mkdir -p research/<slug>`. (No worktree.) Create an empty `research/<slug>/log.md`. Note: `research/` is git-ignored; that's intended.
- **Step 2 — research-lead grooms.** Launch:
  ```
  Agent(
    subagent_type="squid:research-lead",
    prompt="""Groom this research question into a Research Plan. Read docs/RESEARCH_PROCESS.md and CLAUDE.md first. Follow Part 1 of your role.
    Run folder: research/<slug>/
    Question: {resolved question}
    Write research/<slug>/plan.md with all required fields (questions, mode, scope, source strategy, success criteria, constraints). Hand back a one-paragraph summary."""
  )
  ```
  Verify `plan.md` exists and has all fields before the gate.
- **Step 3 — HUMAN GATE #1.** Present plan summary; ask `y / edit / cancel`. On `edit`, re-launch lead with feedback; on `cancel`, stop (optionally `rm -rf research/<slug>` if nothing worth keeping). Use this exact prompt shape:
  ```
  Research question: {title}
  Plan: research/<slug>/plan.md
  Mode: {targeted|exploratory}   Key questions: {...}
  Sources: {...}   Success criteria: {...}

  Approve the plan to start the autonomous run? (y / edit / cancel)
  ```
- **Step 4 — literature-scout searches.** Launch `squid:literature-scout` with the run folder + plan path. On return, verify every accepted source in `sources.md` has a Tier + provenance line. **If the scout reports insufficient credible sources, STOP** and surface `USER ACTION REQUIRED` (don't synthesize on weak ground).
- **Step 5 — synthesizer.** Launch `squid:synthesizer`. Spot-check that findings cite tier-tagged sources and that a "Gaps & follow-up queries" section exists.
- **Step 6 — strategist drafts.** Launch `squid:strategist` (Part 1) → `directions.md`.
- **Step 7 — reviewer panel (PARALLEL).** In ONE message, launch FIVE `squid:research-reviewer` agents, one per ROLE:
  ```
  Agent(subagent_type="squid:research-reviewer", prompt="ROLE: methodologist. Review research/<slug>/directions.md (context: synthesis.md). Read docs/RESEARCH_PROCESS.md first. Tag Blocker/Nit; append your section to research/<slug>/reviews.md.")
  Agent(subagent_type="squid:research-reviewer", prompt="ROLE: domain-expert. ...")
  Agent(subagent_type="squid:research-reviewer", prompt="ROLE: novelty-impact. ...")
  Agent(subagent_type="squid:research-reviewer", prompt="ROLE: feasibility. ...")
  Agent(subagent_type="squid:research-reviewer", prompt="ROLE: clarity. ...")
  ```
  Wait for all five.
- **Step 8 — strategist revises (cap: Max 2 cycles).** If any Blockers were filed, launch `squid:strategist` (Part 2) with `reviews.md`; then re-run Step 7 ONCE. Track the cycle count. After 2 cycles, carry any "Unresolved blockers" forward (flagged) rather than looping again.
- **Step 9 — research-lead acceptance.** Launch `squid:research-lead` (Part 2). Spot-check the verdict against `plan.md`'s success criteria.
- **Step 10 — HUMAN GATE #2.** Present the memo + panel summary + unresolved Blockers + the synthesizer's follow-up queries:
  ```
  Directions ready: research/<slug>/directions.md
  Directions ({N}): {one-line each, with the lead's recommendation}
  Panel: {Blockers resolved: X; Unresolved: Y (listed)}
  Follow-up queries surfaced: {...}

  Choose: accept (done) / loop-back (re-search with refined queries) / handoff (promote a direction to a /night feature spec)
  ```
  - **accept** → final summary, stop.
  - **loop-back** → ask which follow-up queries / scope refinements; update a scratch note; re-enter at Step 4 (scout) with the refined queries. (Human-decided; no auto-cap.)
  - **handoff** → ask which direction; write `docs/features/<slug>.md` from it (problem, goal, scope, acceptance-shaped notes, link back to `research/<slug>/`); recommend `/grill-me docs/features/<slug>.md` then `/night docs/features/<slug>.md`. Do NOT auto-invoke `/night`.
- **Caps & final summary** — like `/night`: caps surface `USER ACTION REQUIRED` and stop; end with a single markdown summary block (run folder, directions count, panel tallies, chosen next action).

- [ ] **Step 2: Validate frontmatter**

Run: `claude plugin validate`
Expected: no errors; `/research` skill recognized; `disable-model-invocation: true` accepted.

- [ ] **Step 3: Verify gates, parallel panel, and handoff present**

Run:
```bash
grep -nE 'HUMAN GATE #1|HUMAN GATE #2|squid:research-reviewer|squid:literature-scout|loop-back|handoff|docs/features/' skills/research/SKILL.md
```
Expected: both gates, all referenced `squid:` agents, and the loop-back/handoff branches present.

- [ ] **Step 4: Verify all five panel ROLE launches are present**

Run:
```bash
grep -cE 'ROLE: (methodologist|domain-expert|novelty-impact|feasibility|clarity)' skills/research/SKILL.md
```
Expected: `5`.

- [ ] **Step 5: Commit**

```bash
git add skills/research/SKILL.md
git commit -m "$(cat <<'EOF'
feat(research): add /research two-gate orchestrator skill

Drives research-lead -> [gate] -> scout -> synthesizer -> strategist ->
5-role panel (parallel) -> revise (max 2) -> accept -> [gate] with
accept / loop-back / /night-handoff branches. Manager-only, spot-checks
citations, mirrors /night.

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 8: Wire into repo (gitignore, README, CLAUDE.md, PROCESS cross-ref)

**Files:**
- Modify: `.gitignore`, `README.md`, `CLAUDE.md`, `docs/PROCESS.md`

- [ ] **Step 1: Add `research/` to `.gitignore`**

Append to `.gitignore` (read it first to match its comment style):
```
# Research-layer run output — user data, not plugin content.
# Keep personally with `git add -f research/<slug>/` on a private branch.
research/
```

- [ ] **Step 2: Add the research layer to `README.md`**

In the "What you get" table, add a `/research` row mirroring the existing `/night` row's phrasing. Then add a short subsection after the `/night` description, e.g.:
```markdown
For research instead of building, `/research <question>` drives a literature → synthesis → reviewed-directions pipeline with two human gates (approve the plan, review the directions), built on a source-credibility gate. A chosen direction can be handed off to `/night` as a feature spec. See [`docs/RESEARCH_PROCESS.md`](docs/RESEARCH_PROCESS.md).
```
Also add the five research agents to the agents row, and `RESEARCH_PROCESS.md` to the repo-layout block.

- [ ] **Step 3: Update `CLAUDE.md`**

In the "What's in the repo" tree, add the five research agents under `agents/`, `skills/research/` under `skills/`, and `docs/RESEARCH_PROCESS.md`. Add a one-line note under editing conventions: "Editing the research lifecycle — `docs/RESEARCH_PROCESS.md` is the canonical research-pipeline doc (parallel to `docs/PROCESS.md`); the `/research` skill and the five research agents read it first." Keep edits terse (the repo's "remove before you add" principle).

- [ ] **Step 4: Cross-reference from `docs/PROCESS.md`**

Add one line near the top of `docs/PROCESS.md` (after the intro paragraph):
```markdown
> For the **research** pipeline (literature → synthesis → reviewed directions), see [`RESEARCH_PROCESS.md`](RESEARCH_PROCESS.md). This file covers the engineering pipeline.
```

- [ ] **Step 5: Validate + verify cross-references**

Run: `claude plugin validate`
Expected: no errors.
Run:
```bash
grep -n 'research/' .gitignore
grep -n 'RESEARCH_PROCESS' README.md CLAUDE.md docs/PROCESS.md
```
Expected: `research/` ignored; `RESEARCH_PROCESS` referenced from all three docs.

- [ ] **Step 6: Commit**

```bash
git add .gitignore README.md CLAUDE.md docs/PROCESS.md
git commit -m "$(cat <<'EOF'
docs(research): wire research layer into repo docs and gitignore

Add /research + agents to README and CLAUDE.md, cross-reference
RESEARCH_PROCESS.md from PROCESS.md, and gitignore research/ run output.

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 9: Validate the whole plugin + manual smoke test

**Files:** none (verification only)

- [ ] **Step 1: Full plugin validation**

Run: `claude plugin validate`
Expected: no errors across `plugin.json`, all agents (including the 5 new ones), and all skills (including `/research`).

- [ ] **Step 2: Confirm the new surfaces load**

Run:
```bash
claude --plugin-dir . -p "List the agents and skills you can see whose names start with 'research' or are '/research'." 2>&1 | tail -30
```
Expected: the five research agents and the `/research` skill are listed. (If `-p` headless mode isn't available, instead launch `claude --plugin-dir .` interactively and run `/agents` and `/help`; confirm the same.)

- [ ] **Step 3: Smoke-test Gate #1 (dry run)**

In a `claude --plugin-dir .` session, run:
```
/research "What are credible recent approaches to <small, well-bounded topic you can sanity-check>?"
```
Expected: `research-lead` produces `research/<slug>/plan.md` with all fields and the run stops at HUMAN GATE #1 asking for plan approval. Confirm `plan.md` exists and `research/` is git-ignored (`git status` should NOT show it). You can `cancel` at the gate — a full end-to-end run (real searches, panel) is a longer manual validation to do when you actually use the layer.

- [ ] **Step 4: Record smoke-test result**

No commit needed (verification only). If anything failed, fix the relevant file and re-run its task's verify steps before proceeding.

---

## Self-review (run against the spec)

**1. Spec coverage** — every spec section maps to a task:
- §4 lifecycle → Task 1 (diagram) + Task 7 (orchestrator steps).
- §5 agents → Tasks 2–6.
- §6 orchestrator → Task 7.
- §7 artifacts + version control → Task 1 (layout) + Task 8 (gitignore); each agent task defines its artifact's format.
- §8 credibility gate → Task 1 + Task 3.
- §9 panel → Task 1 + Task 6.
- §10 loop-back → Task 1 + Task 7 (Step 10).
- §11 /night handoff → Task 1 + Task 7 (Step 10).
- §12 canonical doc → Task 1.
- §13 files → Tasks 2–8.
- §14 defaults → encoded across Tasks 1, 3, 7, 8. No gaps.

**2. Placeholder scan** — file contents are specified by exact frontmatter + enumerated sections + the load-bearing templates/rubrics/role-briefs reproduced inline. "Mirror `agents/X.md`" points at a real committed file (a pattern to follow), not an unwritten task — allowed in an existing codebase. No "TBD/handle edge cases/write tests for the above".

**3. Type/name consistency** — agent names (`research-lead`, `literature-scout`, `synthesizer`, `strategist`, `research-reviewer`), `subagent_type` values (`squid:<name>`), artifact filenames (`plan.md`, `sources.md`, `synthesis.md`, `directions.md`, `reviews.md`, `log.md`), tier names (Tier A/B/Reject), role keys (methodologist/domain-expert/novelty-impact/feasibility/clarity), and finding-id prefixes (M/DE/NI/F/C) are used consistently across Tasks 1, 6, and 7. Gate names ("HUMAN GATE #1/#2") match between Task 7 and its grep check.

No issues found requiring a new task.
