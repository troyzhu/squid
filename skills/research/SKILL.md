---
name: research
description: Run the research pipeline end-to-end for one research question — research-lead grooms a plan, human approves it, then literature-scout searches (credibility-gated), synthesizer synthesizes, strategist drafts directions, a 5-role reviewer panel critiques in parallel, strategist revises, research-lead accepts, and the human reviews the directions memo to accept / loop-back / hand off to /plan. Trigger when the user wants a credibility-grounded, reviewer-critiqued set of research directions, or says "/research".
disable-model-invocation: true
argument-hint: <research-question | path/to/question.md | topic-slug>
---

# Research Mode — End-to-End Single-Question Pipeline

Run the full research-team pipeline as defined in [`docs/RESEARCH_PROCESS.md`](../../docs/RESEARCH_PROCESS.md) for **one research question**, end-to-end. This is the research analog of `/implement-night`.

`$ARGUMENTS` is the research question — a free-form question, a path to a question file, or a topic slug. If empty, ask the human for one before proceeding.

You are the **orchestrator** — a MANAGER, not a researcher. You do NOT search, synthesize, or draft directions yourself. You launch agents, enforce the two gates, and verify each agent's report before forwarding it. In particular, **spot-check that load-bearing claims carry credible (Tier-A) citations** before forwarding any report — this is the research analog of `/implement-night`'s "never rubber-stamp."

The pipeline blocks on the human exactly **twice**, by design:

1. **After research-lead produces the Research Plan** — human approves the plan (questions, scope, mode, sources) before any search runs.
2. **At the very end** — human reviews the critiqued directions memo and chooses accept / loop-back / handoff.

Everything else is automated. Between the two gates the pipeline moves forward on its own — it does not silently skip steps and it does not wait for extra input. Caps stop it and surface `USER ACTION REQUIRED`. The opt-in synthesis checkpoint (Step 5.5) is human-controlled and default-off — it does not change the two-mandatory-gate contract; when off, behavior is identical to today.

**Critical rules** (from `docs/RESEARCH_PROCESS.md`):

- **Never rubber-stamp an agent's report.** When an agent says "ACCEPT", "NO BLOCKERS", or "sufficient sources", re-read the plan and spot-check that the agent actually addressed each criterion. REJECT and re-launch with specific feedback if not.
- **No false confidence.** "The literature says X" is not evidence — a Tier-A citation is. Before forwarding `synthesis.md` or `directions.md`, re-read the load-bearing claims and confirm each carries an `[S#]` citation that resolves to a tier in `sources.md` / the evidence ledger. Citations are slim inline (`[S#]`); the tier lives in the ledger, except a Tier-B-leaning claim keeps the explicit `[S#, B]` mark plus a caveat at the point of use. A load-bearing claim resting on no credible source — or on a Tier-B source without that explicit caveat — is a Blocker, not a footnote: REJECT and re-launch. (Load-bearing still requires Tier A.)
- **If the scout can't find enough credible sources, that is the finding.** Surfacing "insufficient credible evidence" beats synthesizing on weak ground. Stop; don't push forward.
- **One agent per step.** Never bundle steps into one agent call. (The reviewer panel is five agents — one per role — launched together in Step 7.)
- **The orchestrator never searches, synthesizes, or drafts** beyond reading the artifacts to verify them.

Read `{RESEARCH_DOC}` (resolved in Step 0) first — the lifecycle, the two gates, the source-credibility tiers, the reviewer panel, the Max-2 cap, and the artifact layout.

---

## Step 0 — Resolve the canonical doc, then the question

**Resolve the canonical doc.** When this skill launches, the harness states `Base directory for this skill: <path>` (it ends in `…/skills/research`). The plugin root is **two directories up** from that base. Set `RESEARCH_DOC = <plugin-root>/docs/RESEARCH_PROCESS.md` and verify it exists with `ls`. **If the *consuming project* has its own `docs/RESEARCH_PROCESS.md`** (relative to the cwd), prefer the project copy — it may carry project-specific overrides. Use `{RESEARCH_DOC}` (the resolved absolute path) everywhere below, and pass it into every agent launch. The canonical doc does **not** exist in consuming projects, so launching agents with a bare `docs/RESEARCH_PROCESS.md` would have them read nothing.

**Resolve the style contract.** Set `STYLE_DOC = <plugin-root>/docs/WRITING_STYLE.md` the same way, and prefer a project-local `docs/WRITING_STYLE.md` (relative to the cwd) over the plugin's — a project copy lets the user tune prose taste per workspace. `{STYLE_DOC}` governs the free prose of the run artifacts; thread it only into the launches noted below.

**Resolve the profiles directory.** Check `./research-profiles/` at the cwd root (a sibling of `research/`, not inside it). If present, `ls` it — these dossiers (role × domain × school-of-thought lenses, built by `/research-profile`) can layer onto reviewers and the lead; pass matching **absolute** paths into the launches in Steps 2, 7, and 9. **Exclude `research-lead--memory.md`** from the reviewer-dossier list — it is the lead's memory profile, read separately by the lead (Steps 2 and 9), not a reviewer lens. **Also exclude `writing-quality--memory.md`** from the reviewer-dossier list — it is NOT the lead memory either; it is a third, distinct file (accrued workspace prose/depth/format lessons) read by the prose writers (the synthesizer, Step 5) and the depth critic (Step 5.4), not a reviewer lens and not the lead's. Set `WRITING_MEMORY = <cwd>/research-profiles/writing-quality--memory.md` if it is present (absolute path); thread it only into the launches noted in Steps 5 and 5.4, and only when present. If the directory is absent: profiles are simply unused — this layer is **strictly additive**, and with no `research-profiles/` dir (or no `writing-quality--memory.md`) everything **degrades to today's behavior** (no `Profile:` threading, plan says `Profiles: none`, no memory read, no `WRITING_MEMORY` threading).

**Resolve the question.**

If `$ARGUMENTS` is empty: ask the human "What research question should I work tonight? (free-form question, path to a question file, or topic slug)" and wait for the response.

Otherwise, identify the form:

- **Path to a markdown file** (`docs/questions/foo.md`) → `cat` it.
- **Topic slug** → treat as the question stem.
- **Free-form text** → use as-is.

Restate the resolved question back to the human in one paragraph as confirmation, but do NOT block here — proceed.

---

## Step 1 — Create or resume the run folder

Derive `<slug>` from the question — slugified (lowercase, hyphenated, short). There is **no git worktree** — these are documents, not code. (`/research <slug>` — the existing argument form — is the natural way to resume an interrupted run, since the slug derives back to the same folder.)

**Existing-run detection.** If `research/<slug>/` already exists and is non-empty, do NOT touch anything yet — `ls` it to see which artifacts are present and read the tail of `log.md`, then prompt the human:

```
Run folder research/<slug>/ already exists ({list which artifacts are present: plan/sources/synthesis/directions/reviews, and the last log entry}).

resume (default) — continue this run from where it stopped
fresh — archive the old folder to research/<slug>--archived-{YYYYMMDD-HHMM}/ and start over
abort — stop; touch nothing
```

**Staleness signals (compute only when the run is COMPLETE).** A run is complete when it has BOTH `synthesis.md` AND `directions.md`. For a complete run, compute these signals (they decide whether `resume` offers the refresh menu below; an incomplete run skips this — it resumes by filling missing artifacts as usual):

- **Library stale** — count accepted entries in `sources.md` whose `Local:` is `none`, or whose named file is missing from `sources/`. Any such entry predates local-first downloads.
- **Synthesis never ran the depth loop** — `log.md` has no `depth-critic cycle` milestone.
- **v1-shape synthesis** — `synthesis.md` lacks the v2 sections (`## The answer so far`, `## Analysis — beyond the sources`) or carries ~0 typeset `$…$` math.

A complete run with **none** of these signals is current — `resume` goes straight to Gate #2 as today (no menu).

- **resume** (default) → follow the **Resume protocol** below.
- **fresh** → archive the old folder with a plain `mv` (the folder is git-ignored user data — never `rm` it), then fall through to the create block:

  ```bash
  mv "research/$SLUG" "research/$SLUG--archived-$(date +%Y%m%d-%H%M)"
  ```

- **abort** → stop; touch nothing.

If `research/<slug>/` does not exist (or is empty), proceed straight to the create block.

```bash
SLUG="{slug}"
mkdir -p "research/$SLUG"
# The log is append-only and must survive re-runs — create only if missing, never truncate.
touch "research/$SLUG/log.md"
```

**Ensure the target repo ignores `research/`.** The privacy claim below is only true if the repo this runs in actually ignores the run folder — and a freshly scaffolded (or unrelated) project may not. If in a git repo, check it:

```bash
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  ROOT="$(git rev-parse --show-toplevel)"
  if ! git check-ignore -q "$ROOT/research/"; then
    printf '\n# /research run folders — local working artifacts, never shipped\n/research/\n' >> "$ROOT/.gitignore"
    echo "Added '/research/' to .gitignore (the run folder was not ignored)."
  fi
fi
```

The appended rule is **anchored** (`/research/`, leading slash) on purpose: an unanchored `research/` would also ignore any nested `research/` directory elsewhere in the user's project (e.g. `src/research/`) — never silently swallow their files.

If it is **not** a git repo, skip this — there is nothing to leak onto a branch.

`research/` is git-ignored — Step 1 *ensures* this in the target repo. The run output is the human's working artifact, not plugin content that ships. Never `git add -A`; a stray add cannot leak the run onto a public branch because the ignore rule is uniform across branches.

**Resume protocol** (on `resume`). Read `log.md` end-to-end plus the artifact presence, then **report the detected state and the proposed re-entry point to the human and confirm before continuing** — never silently jump back in. A complete run with stale signals (see below) may **refresh** (backfill / deepen / propagate) **in place** rather than only proceeding to Gate #2 — nothing is archived; the synthesis is backed up before a deepen regenerate. The agents already log their own steps; the `[orchestrator]` entries (see below) carry the gate decisions. Use the artifacts and the log together to pick the re-entry step (guidance, not an exhaustive table):

- `plan.md` but no logged Gate-#1 approval → re-present Gate #1 (Step 3).
- Gate #1 logged approved but no `sources.md` → Step 4.
- `sources.md` but no `synthesis.md` → Step 5.
- `synthesis.md` but no logged `depth-critic cycle` milestone → Step 5.4 (the depth-critic pass hasn't run).
- `synthesis.md` with a logged depth-critic milestone but no `directions.md` → Step 5.5 if the plan opted in and no checkpoint decision is logged, else Step 6.
- `directions.md` but no `reviews.md` → Step 7.
- `reviews.md` but no logged completed cycle's revision → Step 8.
- revision logged (changelog in `directions.md`) but no acceptance entry → Step 9.
- acceptance logged → Gate #2 (Step 10).

**Passed gates are never re-asked when the log shows them.** When the log is ambiguous — e.g. a pre-resume run that has artifacts but no `[orchestrator]` entries — **ask the human** which step to re-enter rather than guess.

**Refresh a complete-but-stale run (on `resume`).** When the run is complete (has `synthesis.md` AND `directions.md`) AND carries one or more staleness signals (computed above), it predates current pipeline upgrades — so `resume` does NOT jump to Gate #2 as "done." Instead present a **pick-any-subset refresh menu** that upgrades the run **in place — nothing is archived**:

```
This run is complete but predates current pipeline upgrades:
  {stale signals, e.g. "12 of 18 accepted sources are Local: none", "synthesis never ran the depth-critic loop", "synthesis is v1-shape"}
Refresh in place — nothing is archived. Choose any (e.g. "1,2"):
  [1] backfill library  — download the {N} Local:none sources via the open-access ladder
  [2] deepen synthesis  — regenerate against the now-local corpus + the depth-critic loop (backs up the current synthesis first)
  [3] propagate         — after a deepened synthesis, re-run directions → panel → acceptance
  proceed               — skip refresh; go to Gate #2 as-is
```

Run the chosen actions in order (`1` before `2` before `3` if multiple are picked — backfill feeds deepen, deepen feeds propagate):

- **[1] backfill library.** Launch the scout in **backfill mode** (see `agents/literature-scout.md`) on the existing `sources.md` — it downloads the `Local: none` / missing-file accepted sources via the open-access ladder and updates **only** their `Local:` fields, never re-searching or re-gating. On return, re-run the **Step-4 library verification** (`ls research/<slug>/sources/`, confirm accepted entries resolve to real files). Log `[orchestrator] refresh: backfill — {N} downloaded, {M} still none`.
- **[2] deepen synthesis.** If the library is still stale, **recommend running backfill ([1]) first** — deepening reads the local full texts. Back up the current synthesis, then re-run **Step 5** (synthesizer regenerates `synthesis.md` against the now-local corpus) and **Step 5.4** (the depth-critic loop, its Max-2 cap intact). Confirm the overwrite with the human (the backup makes it safe). Log `[orchestrator] refresh: deepen — synthesis regenerated + depth loop`.

  ```bash
  cp "research/$SLUG/synthesis.md" "research/$SLUG/synthesis--pre-refresh-$(date +%Y%m%d-%H%M).md"
  ```

- **[3] propagate.** After a deepened synthesis, re-enter the pipeline at **Step 6** (strategist) and run directions → panel → revise → acceptance → Gate #2 — the existing flow, unchanged. Log `[orchestrator] refresh: propagate — directions → panel → acceptance re-run`.

Refresh actions are **human-chosen** — there is no new auto-loop; the depth loop inside deepen keeps its Max-2 cap, and propagate's panel keeps its Max-2 cap. `proceed` skips refresh and goes to Gate #2 exactly as a current run would.

**Orchestrator milestone logging.** The agents log their steps, but the orchestrator's own gate decisions would otherwise be invisible to a cold resume. So at the moments listed below, append an entry to `log.md` in the standard Issue-Log format `### [orchestrator] YYYY-MM-DD HH:MM — {milestone}` (append-only, never rewrite):

- **Gate #1** decision — approved / edit round / cancelled.
- **Refresh actions** (on a resume that refreshes a complete-but-stale run) — `refresh: backfill — {N} downloaded, {M} still none` / `refresh: deepen — synthesis regenerated + depth loop` / `refresh: propagate — directions → panel → acceptance re-run`.
- **Each depth-critic cycle** — `depth-critic cycle {n} — {X} Blockers` (Step 5.4).
- **Synthesis checkpoint** decision — only when the plan opted in (continue / feedback / loop-back / cancel).
- **Each panel cycle completion** — `panel cycle {n} complete — {X} Blockers`.
- **Gate #2** decision — accept / loop-back round {n} (with the refined queries) / handoff target.
- **Memory-capture** outcome.

The step sections below each carry a one-line reminder at the matching moment.

For the rest of the run, every agent prompt names the run folder so launched agents operate on the right files: include `Run folder: research/<slug>/` in each launch prompt.

---

## Step 2 — research-lead grooms the question → Research Plan

Launch ONE research-lead agent in **Part 1 (grooming)** mode:

```
Agent(
  subagent_type="squid:research-lead",
  prompt="""Grooming (Part 1 of your role). Read {RESEARCH_DOC} (canonical research lifecycle) and the project's AGENTS.md (or CLAUDE.md, if present) first. Follow Part 1 of your role definition.

  Run folder: research/<slug>/
  Research question: {resolved question from Step 0}

  {If research-profiles/research-lead--memory.md exists, add: Lead memory profile (read this FIRST — accumulated user preferences + per-run lessons; informs grooming, never overrides the plan's success criteria): {absolute path}.}
  {If the orchestrator found reviewer dossiers in Step 0, add: Available reviewer dossiers (propose per-role attachments in the plan's Profiles field): {list each as `{role}--{domain}[--{lens}].md (updated: YYYY-MM-DD)`}.}

  Choose the mode (targeted | exploratory) and write the Research Plan at research/<slug>/plan.md with every field in the template — Question(s), Mode, Scope — in, Scope — out, Source strategy, Success criteria, Constraints, Synthesis checkpoint, Profiles. Success criteria must be checkable (counts/tiers, not adjectives). For Profiles, propose `{role → dossier filename}` for any dossier whose lens sharpens that role for this question, or `none`. You may ALSO list profiles worth BUILDING that the dossier list doesn't cover — mark each `suggested (not yet built)` with a one-line reason, derived from the question and domain. Append a [research-lead] grooming entry to research/<slug>/log.md.

  Hand back: the path to plan.md and a one-paragraph summary."""
)
```

Wait for completion. **Verify before forwarding to the human:**

- `research/<slug>/plan.md` actually exists.
- It has **every** field in the template — Question(s), Mode, Scope (in/out), Source strategy, Success criteria, Constraints, Synthesis checkpoint, Profiles — none left as a placeholder (`Profiles: none` is a valid filled value).
- Success criteria are checkable (counts/tiers), not vague adjectives. Constraints are concrete enough for a feasibility verdict.

If verification fails, re-launch the research-lead with the gap as concrete feedback.

---

## Step 3 — HUMAN GATE #1: Approve the plan

Surface the Research Plan to the human:

```
Question: {title}
Plan: research/<slug>/plan.md
Mode: {targeted | exploratory}

Key questions:
- {q1}
- {q2}

Source strategy: {academic / web / local corpus at <path> (local-first | local-only); named venues or authors}
Success criteria: {the checkable bar}
Synthesis checkpoint: {yes (opt-in mid-run pause) | no}
Profiles: {role → dossier (updated: YYYY-MM-DD), or none}{; any `suggested (not yet built)` rows the lead proposed, each with its one-line reason}

Open questions (if any): ...

{If suggested-not-built profiles exist: Suggested profiles (not yet built): {list}. Build them first? (~one scout run each)}

Approve the plan to start the search? (y / b (build suggested profiles, then re-present) / edit / cancel)
```

The `Profiles:` line keeps the surfaced plan summary; the `Suggested profiles …` prompt line appears **only when** the lead proposed `suggested (not yet built)` rows (or the human asked for a lens no dossier covers). When there are no suggestions, omit that line and the `b` choice reads as a no-op.

**Wait for the human's response.** This is the first of the two blocking gates. When the Source strategy names a local corpus, the human confirms the corpus path and the supplement behavior (`local-first` vs `local-only`) here, alongside approving the questions and scope. The human may adjust the profile attachments here (add / drop / swap a dossier per role). If the lead surfaced `suggested (not yet built)` rows — or the human wants a lens no dossier covers — the human may pause to build them first. Recommend `/research-profile "{role}, {domain}, {lens}"` in one sentence; if the human says "build them" at the gate, you MAY invoke `/research-profile` with the suggested entries (explicit human direction at the gate is not auto-invocation). Do **NOT** invoke it unprompted. Otherwise the run proceeds without them.

**After building at the gate, attach before re-presenting.** A `suggested (not yet built)` row is not an attachment, and Step 7 threads only real `{role → dossier}` attachments — so a built-but-unattached dossier would never be used this run. Once the builds finish: re-`ls` `research-profiles/` to refresh the dossier list and absolute paths (the Step-0 discovery predates these files; still exclude the `*--memory.md` files — `research-lead--memory.md` and `writing-quality--memory.md` are not reviewer dossiers), then convert the now-built rows in `plan.md`'s `Profiles:` field into real attachments — either re-launch the research-lead (Part 1, profiles field only) or, with the human's confirmation, edit the field in place — and loop back to Step 3 to re-present the gate with the attachments live.

- `y` → proceed to Step 4.
- `b` (only meaningful when suggestions exist) → build the `suggested (not yet built)` profiles now: invoke `/research-profile` once per suggested entry (explicit human direction at the gate, not auto-invocation), then run the **"After building at the gate, attach before re-presenting"** block above (re-`ls` the profiles dir → convert the now-built plan rows into real attachments → loop back to Step 3) so the gate re-presents with the dossiers live before any search.
- `edit` → ask what to change (questions, scope, mode, sources, criteria, profile attachments); re-launch the research-lead (Part 1) with the human's feedback; loop back to Step 3 with the revised plan.
- `cancel` → report cancelled and stop. Offer to remove the run folder if nothing in it is worth keeping (`rm -rf research/<slug>/`) — default to leaving it.

Append the `[orchestrator]` milestone entry for the Gate-#1 decision (approved / edit round / cancelled).

If the human is unreachable (truly unattended run), this is the natural place to stop and wait — `/research` is **not** fully autonomous, by design. Surface the plan in the final message and end; the human resumes by re-invoking `/research` with the same question (the run folder will already exist).

---

## Step 4 — literature-scout searches (credibility-gated)

Launch ONE literature-scout agent:

```
Agent(
  subagent_type="squid:literature-scout",
  prompt="""Credibility-gated literature search. Read {RESEARCH_DOC} (canonical research lifecycle) and the project's AGENTS.md (or CLAUDE.md, if present) first. Follow your role definition — your headline duty is the source-credibility gate.

  Run folder: research/<slug>/
  Approved plan: research/<slug>/plan.md

  Drive deep-research / huggingface-papers / WebSearch / WebFetch as the search engine (branch on the plan's mode). If the plan's Source strategy names a local corpus, instead ingest it — read each file, extract its bibliographic identity, gate-tier it (hand-gathered PDFs are NOT auto-Tier-A; the user's own notes are context, not citable sources), dedupe, and build the library from the files — and honor the supplement mode (local-first: web-supplement ONLY under-covered questions; local-only: don't). Run the search-as-code filtering pass (dedupe + domain filter + per-question coverage), apply the Tier A/B/Reject gate, and write research/<slug>/sources.md in the required shape — every Accepted source carries a Tier AND a one-line provenance line; every Reject is listed with a reason. Download every accepted source's full text into the local library research/<slug>/sources/ — a local copy is the default outcome (the run folder must read offline): arXiv/OA PDFs via curl, pages as dated .md snapshots; when the canonical link is paywalled, seek the open-access copy (arXiv/PMC/author/publisher-open) before settling for `none`. Give each accepted entry a Local: field; `none` is the audited last resort and records the reason + routes tried. If credible coverage is thin for any plan question, SAY SO explicitly rather than padding. Append a [literature-scout] entry to research/<slug>/log.md.

  Hand back: Tier-A / Tier-B counts, per-question coverage, the local-library tally (fetched / snapshot / none), anything under-covered, and the path to sources.md."""
)
```

The scout invokes the engine skills itself (it has the `Skill` tool). `deep-research` and `huggingface-papers` are **separate plugins** that may not be installed in the consuming project — if the scout reports a degraded engine (native WebSearch/WebFetch fan-out because the companion plugins are absent), carry that fact into the Gate #2 summary so the human knows the search ran on a thinner engine.

On return, **verify before forwarding:**

- `research/<slug>/sources.md` exists and matches the required shape.
- **Every Accepted source has a Tier (A/B) AND a one-line provenance line.** Spot-check a couple — no bare links in Accepted.
- **Every Accepted source has a Local: field, and the library is actually populated.** `ls research/<slug>/sources/` and confirm accepted sources resolve to real files — a downloaded full text is the expected default, not best-effort. If a notable share of accepted sources are `Local: none`, that is a flag: the run won't read offline and the synthesis leans on extracted claims. Surface the `none` count and reasons to the human (and have the scout retry the open-access ladder on re-run) rather than silently proceeding. In local-corpus mode, the library should hold the ingested files and the Engine line should read local ingestion (with `+ web supplement` if it filled gaps).
- The Rejected list carries reasons (the filter is auditable).

**If the scout reports insufficient credible sources** (the insufficient-sources rule tripped), **STOP.** Surface `USER ACTION REQUIRED` with which questions are under-covered and the per-question coverage counts — do NOT synthesize on weak ground. Offer the human: refine/relax the source strategy and re-run Step 4, or cancel.

---

## Step 5 — synthesizer synthesizes

Launch ONE synthesizer agent:

```
Agent(
  subagent_type="squid:synthesizer",
  prompt="""Synthesis. Read {RESEARCH_DOC} (canonical research lifecycle) and the project's AGENTS.md (or CLAUDE.md, if present) first. Follow your role definition. Do NOT draft directions — that's the strategist, downstream.

  Run folder: research/<slug>/
  Sources: research/<slug>/sources.md
  Plan: research/<slug>/plan.md
  Style contract: {STYLE_DOC}
  Writing-quality memory: {WRITING_MEMORY} (if present — accrued workspace prose/depth/format lessons; read it after the style contract; it sharpens how you write / what you enforce, and never overrides the canonical contract or the Quality rubric).

  Synthesize load-bearing findings from the local full texts in research/<slug>/sources/ (the Read tool reads PDFs directly), not just the scout's extracted claims — when an entry's Local: is none, work from the claims and say so in the evidence-quality assessment. Write research/<slug>/synthesis.md in the required shape — these sections, in order: The answer so far (reader-facing prose), the argued themes (depth matched to the material — theory gets its derivations; each claim citing a slim [S#] that resolves to a tier in the ledger, Tier-B-leaning claims keeping their [S#, B] mark), Tensions & debates, Analysis — beyond the sources, Implications for your questions, Where I need your judgment, Gaps & follow-up queries (each gap a concrete, re-runnable search string), and an Appendix — evidence ledger. Analysis items are OURS-derived (Status: OURS + Confidence-tagged), grounded only in cited S#/A# already in scope — no new sources, no directions. Write the memo's prose per {STYLE_DOC}; run its lint on synthesis.md before hand-off and record the counts in your log entry. Append a [synthesizer] entry to research/<slug>/log.md.

  Hand back: theme count, finding count (Tier-A vs Tier-B), A-item count and confidence distribution (high/medium/speculative), sharpest tensions, the evidence-quality verdict, the open gaps with their follow-up queries, primer candidates (foundational concepts a newcomer would want grounding on, with a one-line why), or none, and the path to synthesis.md."""
)
```

On return, **spot-check before forwarding:**

- Every finding cites a source ID (`[S#]`) that resolves to a tier in `sources.md` / the ledger; load-bearing findings rest on Tier A, and a Tier-B-leaning claim carries the explicit `[S#, B]` mark plus a caveat.
- Every A-item in `## Analysis — beyond the sources` carries **Status: OURS** + a **Confidence** + a **derivation** whose steps cite in-scope `S#`/`A#`. **An A-item whose grounding doesn't hold is a Blocker: REJECT and re-launch** with the specific item called out.
- `## The answer so far` exists and is reader-facing prose for the human — not an index or a bullet dump.
- A `## Gaps & follow-up queries` section exists, and each gap is a concrete query (not "needs more research").

If a load-bearing finding has no credible citation, REJECT and re-launch with the specific finding called out.

The orchestrator may re-run the `{STYLE_DOC}` lint on `synthesis.md`; a breach the writer did not record in its log entry is treated like any unverified claim — send it back.

---

## Step 5.4 — Depth-critic pass (capped, runs every run)

The synthesis is the artifact that has historically fallen shortest of the handbook-grade bar, and it never had a revise loop. This step adds one: a depth critic scores it against the Quality rubric and the synthesizer deepens it. It runs on **every** run (not opt-in) but is strictly bounded — **Max 2 cycles** — and the human gate (the checkpoint / Gate #2) remains the final control.

**Launch ONE `squid:research-reviewer` with `ROLE: depth`** on the synthesis:

```
Agent(
  subagent_type="squid:research-reviewer",
  prompt="""ROLE: depth. Run folder: research/<slug>/. Read {RESEARCH_DOC} (canonical research lifecycle) and the project's AGENTS.md (or CLAUDE.md, if present) first. You are the rubric scorer, NOT a content lens — score research/<slug>/synthesis.md against the Quality rubric in {STYLE_DOC} (structure, depth, usability — not correctness). Style contract (the rubric): {STYLE_DOC}. Writing-quality memory: {WRITING_MEMORY} (if present — accrued workspace prose/depth/format lessons; read it after the style contract; it sharpens how you write / what you enforce, and never overrides the canonical contract or the Quality rubric). For each rubric property, emit a specific, located finding where the draft falls short (named-not-shown, asserted-not-derived, comparison with no when-preferred/no table, prose worked example with no visual/no stepped form, bare non-clickable reference link, math-heavy+long but no Notation/no TOC). Tag each Blocker/Nit (prefix DPT). Write your findings to research/<slug>/synthesis-depth-review.md and append a [research-reviewer:depth] entry to log.md. Do NOT edit synthesis.md.

  Hand back: your Blocker count and Nit count, and the path to synthesis-depth-review.md."""
)
```

**Then loop, capped at 2 cycles:**

1. If the depth critic returns **zero** Blockers → done; fall through to Step 5.5.
2. If it returns Blockers → re-launch ONE `squid:synthesizer` in **revise mode** (Part 2), passing `research/<slug>/synthesis-depth-review.md`, `research/<slug>/synthesis.md`, `{STYLE_DOC}`, and `{WRITING_MEMORY}` (if present, so the deepening pass applies the same accrued lessons as the initial draft); tell it this is depth cycle `{n}`. It deepens `synthesis.md` (adds the missing derivation/table/visual/Notation/clickable links), appends a `## Depth revisions (cycle {n})` changelog and a `## Unresolved depth findings` section, and never silently drops a finding.
3. **Re-run the Step-5 grounding spot-check on the deepened synthesis** — a revision can introduce a new un-grounded A-item; if one doesn't hold, REJECT and re-launch the revise. Then **re-launch the depth critic** on the revised synthesis (it overwrites `synthesis-depth-review.md` and confirms its prior `DPT#` Blockers are resolved before tagging new ones), and read its fresh Blocker count.

**Cap: Max 2 cycles.** Track the cycle count. If Blockers remain after cycle 2, **do NOT loop again** — carry the synthesizer's `## Unresolved depth findings` forward (flagged) into the checkpoint (Step 5.5) and Gate #2, never silently dropped. Then the existing Step-5 spot-check and Step 5.5 checkpoint proceed as before.

Append the `[orchestrator]` milestone entry per cycle: `depth-critic cycle {n} — {X} Blockers`.

---

## Step 5.5 — OPTIONAL: synthesis checkpoint (only if plan.md says yes)

Read plan.md's **Synthesis checkpoint:** field. `no` (default) ⇒ skip to Step 6. `yes` ⇒ present and BLOCK:

```
Synthesis checkpoint (you opted in at Gate #1).

The answer so far — research/<slug>/synthesis.md
{paste the "## The answer so far" section verbatim}

Where I need your judgment:
{paste the "## Where I need your judgment" prompts}

Primer candidates (concepts a newcomer would want grounding on first):
{the synthesizer's primer candidates with their one-line why, or "none"}

Choose: continue (draft directions) / primer (build a ground-up tutorial on a concept) / feedback (revise the synthesis) / loop-back (re-search) / cancel
```

**Wait for the human.** This is an opt-in checkpoint, **NOT** a third mandatory gate — it fires only because the human asked for it at Gate #1.

- **continue** → proceed to Step 6.
- **primer** → ask which concept (offer the primer candidates; the human may name any other). Invoke `/research-tutorial <concept> from-run <slug>` (it grounds in this run, runs the readability review, and on save drops a pointer into `synthesis.md`). Then re-present this checkpoint — the human may build several primers before continuing. Building is human-directed here, not auto.
- **feedback** → relaunch ONE synthesizer with the human's notes; it revises `synthesis.md` in place; **re-run the Step-5 spot-check on the revision** (a revision can introduce a new un-grounded A-item), then re-present this checkpoint. Human-decided, no auto-cap (the checkpoint is the control — same discipline as the Gate-#2 loop-back).
- **loop-back** → re-enter **Step 4** with refined queries (same as the Gate-#2 loop-back).
- **cancel** → report and stop; offer to keep the run folder.

Append the `[orchestrator]` milestone entry for the synthesis-checkpoint decision.

---

## Step 6 — strategist drafts directions

Launch ONE strategist agent in **Part 1 (draft)** mode:

```
Agent(
  subagent_type="squid:strategist",
  prompt="""Directions draft (Part 1 of your role). Read {RESEARCH_DOC} (canonical research lifecycle) and the project's AGENTS.md (or CLAUDE.md, if present) first. Follow Part 1 of your role definition. Do NOT search and do NOT judge your own directions — the panel reviews, the research-lead accepts.

  Run folder: research/<slug>/
  Synthesis: research/<slug>/synthesis.md
  Plan: research/<slug>/plan.md
  Style contract: {STYLE_DOC}

  Form N candidate directions and write research/<slug>/directions.md in the required shape — each direction with Rationale (citing synthesis findings by source ID + tier; load-bearing rationale on Tier A), Novelty delta, Feasibility (against plan.md constraints), and Risks — plus a ## Recommendation / ranking section. Write the memo's prose per {STYLE_DOC}; run its lint on directions.md before hand-off and record the counts in your log entry. Append a [strategist] entry to research/<slug>/log.md.

  Hand back: direction count, how many rest on Tier-A rationale, the recommended ranking, and the path to directions.md."""
)
```

On return, spot-check that every direction's rationale cites a synthesis finding (Tier A where load-bearing) and that a ranking exists. Also confirm the direction count meets any count bar in `plan.md`'s success criteria — catching a count miss here avoids burning a revision cycle on it later.

---

## Step 7 — Reviewer panel (PARALLEL — five roles)

In ONE message, launch FIVE `squid:research-reviewer` agents — one per ROLE. They are independent; each stays in its lane and appends its own `## [{ROLE}]` section to `reviews.md`.

For any role the plan's **Profiles** field attached a dossier, append `Profile: {absolute path}` to that role's launch (the orchestrator resolved these absolute paths in Step 0), plus the one-line instruction: **"If a Profile: path is given, read it after the canonical doc — it sharpens your lens, never overrides your contract."** Roles with no attachment launch exactly as before (no `Profile:` line).

```
Agent(subagent_type="squid:research-reviewer", prompt="ROLE: methodologist. Run folder: research/<slug>/. Review research/<slug>/directions.md (context: research/<slug>/synthesis.md, research/<slug>/plan.md). Read {RESEARCH_DOC} (canonical research lifecycle) and the project's AGENTS.md (or CLAUDE.md, if present) first. {Profile: {abs path} — read it after the canonical doc; it sharpens your lens, never overrides your contract.} Tag findings Blocker/Nit (prefix M); append your ## [methodologist] section to research/<slug>/reviews.md and a [research-reviewer:methodologist] entry to log.md. Do NOT edit directions.md.")
Agent(subagent_type="squid:research-reviewer", prompt="ROLE: domain-expert. Run folder: research/<slug>/. Review research/<slug>/directions.md (context: research/<slug>/synthesis.md, research/<slug>/plan.md). Read {RESEARCH_DOC} (canonical research lifecycle) and the project's AGENTS.md (or CLAUDE.md, if present) first. {Profile: {abs path} — read it after the canonical doc; it sharpens your lens, never overrides your contract.} Check prior art (you may WebSearch). Tag findings Blocker/Nit (prefix DE); append your ## [domain-expert] section to research/<slug>/reviews.md and a [research-reviewer:domain-expert] entry to log.md. Do NOT edit directions.md.")
Agent(subagent_type="squid:research-reviewer", prompt="ROLE: novelty-impact. Run folder: research/<slug>/. Review research/<slug>/directions.md (context: research/<slug>/synthesis.md, research/<slug>/plan.md). Read {RESEARCH_DOC} (canonical research lifecycle) and the project's AGENTS.md (or CLAUDE.md, if present) first. {Profile: {abs path} — read it after the canonical doc; it sharpens your lens, never overrides your contract.} Tag findings Blocker/Nit (prefix NI); append your ## [novelty-impact] section to research/<slug>/reviews.md and a [research-reviewer:novelty-impact] entry to log.md. Do NOT edit directions.md.")
Agent(subagent_type="squid:research-reviewer", prompt="ROLE: feasibility. Run folder: research/<slug>/. Review research/<slug>/directions.md (context: research/<slug>/synthesis.md, research/<slug>/plan.md). Read {RESEARCH_DOC} (canonical research lifecycle) and the project's AGENTS.md (or CLAUDE.md, if present) first. {Profile: {abs path} — read it after the canonical doc; it sharpens your lens, never overrides your contract.} Judge against plan.md constraints (data/compute/time/expertise). Tag findings Blocker/Nit (prefix F); append your ## [feasibility] section to research/<slug>/reviews.md and a [research-reviewer:feasibility] entry to log.md. Do NOT edit directions.md.")
Agent(subagent_type="squid:research-reviewer", prompt="ROLE: clarity. Run folder: research/<slug>/. Review research/<slug>/directions.md (context: research/<slug>/synthesis.md, research/<slug>/plan.md). Read {RESEARCH_DOC} (canonical research lifecycle) and the project's AGENTS.md (or CLAUDE.md, if present) first. {Profile: {abs path} — read it after the canonical doc; it sharpens your lens, never overrides your contract.} Junior-staff lens — block ONLY on incomprehensibility, never on correctness. Also enforce {STYLE_DOC} per its severity note (breaches are Nits; dense breaches are clarity Blockers). Tag findings Blocker/Nit (prefix C); append your ## [clarity] section to research/<slug>/reviews.md and a [research-reviewer:clarity] entry to log.md. Do NOT edit directions.md.")
```

**Wait for all five to complete.** Verify each appended its `## [{ROLE}]` section and left `directions.md` untouched.

---

## Step 7.5 — Collate the consolidated Blockers list

The parallel reviewers each wrote their own section but cannot author a shared list. **You (the orchestrator)** now append a single `## Blockers to resolve` section to `reviews.md` that collects every Blocker from all five role sections, by their `{ROLE-prefix}{n}` ids (e.g. `M1`, `DE2`, `F1`). This is the one list the strategist works from in Step 8.

```markdown
## Blockers to resolve
- M1 — {one-line restatement of the methodologist Blocker}
- DE2 — {...}
- F1 — {...}
```

If there are **zero** Blockers across all five roles, write `- none (panel is clear)` under the heading and skip directly to Step 9 (no revision needed).

Append the `[orchestrator]` milestone entry once this cycle's panel is collated: `panel cycle {n} complete — {X} Blockers` (this fires on each collation, including the cycle-2 re-review in Step 8).

---

## Step 8 — strategist revises (cap: Max 2 cycles)

If Step 7.5 found one or more Blockers, launch ONE strategist agent in **Part 2 (revision)** mode:

```
Agent(
  subagent_type="squid:strategist",
  prompt="""Revision (Part 2 of your role). Read {RESEARCH_DOC} (canonical research lifecycle) and the project's AGENTS.md (or CLAUDE.md, if present) first. Follow Part 2 of your role definition.

  Run folder: research/<slug>/
  Reviews (with the consolidated ## Blockers to resolve list): research/<slug>/reviews.md
  Directions to revise: research/<slug>/directions.md
  Synthesis (your evidence base): research/<slug>/synthesis.md
  Style contract: {STYLE_DOC}

  This is revision cycle {n}. Address EVERY Blocker in the ## Blockers to resolve list — re-derive each fix from synthesis.md, never search to patch a gap. Append a ## Revisions made (cycle {n}) changelog and an ## Unresolved blockers section to directions.md. Never silently drop a Blocker — anything unresolvable goes under Unresolved blockers with a reason. Write any revised prose per {STYLE_DOC}; re-run its lint on directions.md before hand-off and record the counts in your log entry. Append a [strategist] entry to log.md.

  Hand back: how many Blockers addressed (one line each), any Unresolved blockers with reasons, the cycle number, and the path to the revised directions.md."""
)
```

Then **re-run Step 7 (+ Step 7.5) ONCE** — re-launch the five-role panel against the revised `directions.md`; each role confirms its prior Blockers are resolved before tagging anything new, and you re-collate the `## Blockers to resolve` list. **Cycle-2 re-reviews reuse the SAME profile attachments as cycle 1** — a reviewer must not change lens mid-revision.

**Cap: Max 2 cycles per directions draft.** Track the cycle count. The counter RESETS on a Gate-#2 loop-back: a loop-back re-enters at Step 4 with fresh search → fresh synthesis → fresh draft, so it earns a fresh Max-2 counter.

- If the second panel comes back clean → proceed to Step 9.
- If Blockers remain after cycle 2, **do NOT loop again.** Carry any `## Unresolved blockers` forward (flagged) into Gate #2 — they ship surfaced to the human, never silently dropped.

---

## Step 9 — research-lead acceptance

Launch ONE research-lead agent in **Part 2 (acceptance)** mode:

```
Agent(
  subagent_type="squid:research-lead",
  prompt="""Acceptance (Part 2 of your role). Read {RESEARCH_DOC} (canonical research lifecycle) and the project's AGENTS.md (or CLAUDE.md, if present) first. Follow Part 2 of your role definition. You verify the memo is RIGHT (answers the question against plan.md's bar) — not the evidence chain (the scout and panel did that).

  Run folder: research/<slug>/
  Revised directions: research/<slug>/directions.md
  Plan: research/<slug>/plan.md

  {If research-profiles/research-lead--memory.md exists, add: Lead memory profile (READ-ONLY — accumulated user preferences + per-run lessons; informs acceptance, never overrides plan.md's success criteria): {absolute path}.}

  Walk directions.md from the user's POV. Check each Success criterion in plan.md off or note the gap; confirm every plan question is addressed or its absence accounted for; confirm any Unresolved blockers are surfaced (not buried). Verdict: ACCEPT or REJECT-with-reasons (name the direction + success criterion). Do NOT rewrite the memo. Append a [research-lead] acceptance entry to log.md.

  Hand back: the verdict, the success-criteria checklist, and any concerns."""
)
```

When multiple cycles ran, the strategist appended a changelog and an `## Unresolved blockers` section each cycle — the **LATEST** `## Unresolved blockers` section is authoritative; ignore the superseded earlier ones when reading what still stands.

**Spot-check the verdict against `plan.md`'s success criteria — don't rubber-stamp.** ACCEPT must cite the criteria, not just say "ACCEPTED"; if the lead accepts criteria the directions don't actually meet, treat as rubber-stamp and re-launch.

- **ACCEPT (verified)** → proceed to Step 10.
- **REJECT (verified)** → route the lead's concerns back to the strategist (Step 8, Part 2) as a revision — **within the same Max-2-cycle cap**. If the cap is already spent, carry the lead's concerns into Gate #2 flagged, rather than looping again.

---

## Step 10 — HUMAN GATE #2: Review the directions memo

Surface the critiqued directions memo to the human with the panel summary and the synthesizer's follow-up queries:

```
Directions ready: research/<slug>/directions.md

Directions ({N}):
1. D1 — {one-line statement} {(lead's recommended pick, if so)}
2. D2 — {one-line statement}
...

Panel: Blockers resolved: {X}; Unresolved: {Y} (listed: {ids + one-liners}, or "none")
Analysis items: {N} ({high}/{medium}/{speculative}){; note any direction leaning load-bearing on a speculative A-item}
Follow-up queries surfaced: {the synthesizer's gaps-as-queries}

New to a concept in here? `/research-tutorial <concept> from-run <slug>` builds a grounded primer.

Choose: accept (done) / loop-back (re-search with refined queries) / handoff (promote a direction to a feature spec for /plan)
```

**Wait for the human's response.** This is the second and final blocking gate.

- **accept** → proceed to **Step 11** (lead-memory capture), then emit the final summary (below) and stop.
- **loop-back** → ask which follow-up queries to run and any scope refinements (the human may edit). Re-enter the pipeline at **Step 4** (scout) seeded by those refined queries — synthesis, directions, panel, acceptance all re-run on the fresh evidence. Loop-back is **human-decided; there is no auto-cap** — the gate is the control.
- **handoff** → ask which direction to promote. Ensure the target dir exists (`mkdir -p docs/features`), then write `docs/features/<slug>.md` from that direction:

  ```markdown
  # {Direction title}

  **Problem:** {what gap / question this addresses}
  **Goal:** {the outcome the build should produce}
  **Scope:** {in / out, drawn from the direction's statement and feasibility notes}
  **Acceptance-shaped notes:** {checkable signals of done, from the direction's rationale + feasibility}
  **Research backing:** see research/<slug>/ — directions.md (D{n}), synthesis.md, sources.md.
  ```

  Then recommend the next commands — **do NOT auto-invoke either:**

  ```
  Feature spec written: docs/features/<slug>.md
  Recommended next: /plan docs/features/<slug>.md   (grill + groom into an approved Tasks Plan)
  then:             /implement-night                (build the approved plan end-to-end)
  ```

  Research → build stays a human decision. Then proceed to **Step 11** (lead-memory capture) before the final summary.

Append the `[orchestrator]` milestone entry for the Gate-#2 decision (accept / loop-back round {n} with the refined queries / handoff target).

---

## Step 11 — Lead-memory capture (after Gate #2 resolves)

Once Gate #2 resolves on a **run-ending** choice (accept / handoff — **not** loop-back, which re-enters Step 4 and reaches this step only when its final Gate #2 pass ends the run), distill **1–3 lesson lines** from the run for the lead's memory profile: scoping habits that worked, what the human accepted or rejected and **why**, success-criteria patterns worth reusing. Present them to the human and **persist nothing without explicit approval** (the self-improve discipline — present → approve → persist, never silently).

- On approval, **append-only** to `research-profiles/research-lead--memory.md` (create it with frontmatter `role: research-lead` and `updated:` if absent — sibling of `research/`, not inside it). Show the human exactly what was written.
- If no `research-profiles/` dir exists and the human declines creating one, **skip silently** — no dir, no capture, no change.

**Writing-quality memory capture (a SECOND, distinct distillation).** When this run's human feedback touched **prose/depth/format** — a checkpoint steer about depth, a clarity Blocker the human echoed, a Gate-#2 prose comment — distill **1–3 writing-quality lesson lines** (concrete and durable, e.g. "show a proposal step with bit-flip / 2-opt / Gaussian-perturbation instantiations, never just by name"), present them, and on approval **append-only** to `research-profiles/writing-quality--memory.md` (create it with the `kind: writing-quality-memory` frontmatter below if absent — sibling of `research/`, not inside it). Keep these **DISTINCT** from the lead/scoping lessons — those still go to `research-lead--memory.md`; the writing-quality lessons are read by the prose writers (the synthesizer, Step 5) and the depth critic (Step 5.4), never override the canonical contract or the Quality rubric, and are append-only. The frontmatter to create it with:

  ```markdown
  ---
  kind: writing-quality-memory
  updated: YYYY-MM-DD
  ---
  # Writing-quality memory

  Accrued, workspace-specific prose/depth/format lessons from human feedback across runs.
  Read by the prose writers (synthesizer, tutorial) and the depth critic — it sharpens how
  they write and what the critic enforces. It never overrides the canonical WRITING_STYLE
  contract or its Quality rubric; it adds workspace taste on top.

  ## Lessons
  - {YYYY-MM-DD} {one concrete durable lesson}
  ```

  If no `research-profiles/` dir exists and the human declines creating one, **skip silently** — same discipline as the lead memory. The run's human feedback not touching prose/depth/format ⇒ no writing-quality capture; nothing changes.

**Seed-a-dossier offer (optional).** If this run's gated corpus would obviously seed a dossier — a `suggested (not yet built)` lens from the plan, or a domain the corpus covers densely — offer ONE line: `This run's gated corpus could seed {dossier}; build it now via /research-profile from-run <slug>? (y/N)`. Human-gated; on decline, skip silently (no offer if the corpus seeds nothing obvious).

Append the `[orchestrator]` milestone entry for the memory-capture outcome — both distillations (lead-memory captured / skipped; writing-quality captured / skipped).

**v1 non-goal:** no per-dossier run-notes — only the single lead memory file accumulates. (On a `loop-back`, capture runs after the human's *final* Gate #2 choice ends the run, not on each intermediate loop.)

---

## Caps & final summary

Caps surface `USER ACTION REQUIRED` and stop the pipeline — they do not loop forever:

- **Depth critic → synthesizer deepen: Max 2 cycles** (Step 5.4). Unresolved depth findings after cycle 2 are carried into the checkpoint / Gate #2, flagged. Bounded and human-gated; the synthesis is the artifact this targets.
- **Strategist revise → panel re-review: Max 2 cycles** per directions draft. Unresolved Blockers after cycle 2 are carried into Gate #2, flagged.
- **Scout finds too few credible sources: surface & stop** (Step 4). No synthesizing on weak ground.
- **Loop-back at Gate #2: human-decided, no auto-cap.** The human gate is the control.
- **Refresh of a stale run: human-chosen, no new auto-loop** (Step 1). The human picks the actions; deepen reuses the depth loop's Max-2 cap and propagate reuses the panel's Max-2 cap — refresh adds no cap of its own.

End every run with a single markdown summary block to the human:

```markdown
## /research complete — {Question title}

**Run folder:** research/<slug>/
**Plan:** research/<slug>/plan.md ({targeted | exploratory})
**Directions:** research/<slug>/directions.md ({N} directions)

**Panel:** Blockers resolved: {X}; Unresolved (surfaced): {Y} (listed)
**Sources:** {Tier-A count} Tier-A, {Tier-B count} Tier-B accepted
**Analysis items:** {N} ({high}/{medium}/{speculative}){; note if any direction leans on a speculative A-item}
**Follow-up queries surfaced:** {count, or "none"}

**Next action chosen:** {accept (done) | loop-back (re-searching {queries}) | handoff → docs/features/<slug>.md}
```

`/research` ends at the human's Gate #2 choice. On `handoff`, it stops at writing the feature spec and recommending `/plan` then `/implement-night` — it never auto-invokes `/plan`.

---

## Notes on shape

- **Two human gates by design.** Plan approval prevents the team from searching the wrong question for hours; the directions review keeps the human in control of what (if anything) becomes a build.
- **The pipeline moves forward between the gates.** It never silently skips a step and never waits for extra input — except when a cap fires or the scout can't proceed, where it surfaces `USER ACTION REQUIRED` and stops.
- **One agent per step; the panel is the one parallel fan-out** (five roles in one message). The orchestrator collates their Blockers in Step 7.5 — the reviewers can't author a shared list.
- **No git worktree.** Research artifacts are documents in a git-ignored `research/<slug>/` — not code on a branch. Never `git add -A`.
- **The orchestrator never researches.** It launches agents, enforces the gates, and spot-checks that load-bearing claims carry credible citations before forwarding. "The agents agree" is never sufficient if the evidence chain doesn't hold.
