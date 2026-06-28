# Research-Thread Consolidation Writer — Design Spec

> Status: design, approved (pending spec review). Date: 2026-06-18. Branch: `feat/research-layer`.
> A new `/research-thread` skill that consolidates a finished `/research` run into ONE wiki-ready
> "research thread" note — a high-quality, self-contained file matching the maintainer's personal
> wiki genre and house style, ready to drop into `wiki/research-threads/` by hand.

## Context

The maintainer runs `/research` in standalone workspaces (e.g. `simulated_annealing`, `LLM_conflict`,
`text-diffusion-models`) and wants each to emit **one consolidated, high-quality writing note** that
integrates into their personal research wiki (`Dropbox/Papers/wiki/research-threads/`) as a *research
thread*. The maintainer's wiki is the gold standard for this genre (as `GRPO_empirical` was for
tutorials).

**The gap is genre, not depth.** A `/research` run already produces ~85% of the raw material —
`synthesis.md` (deep, math-typeset, foldable derivations), `directions.md`, `sources.md` (a 100%-local
gated library), and primers/methods-maps under `tutorials/`. The `simulated_annealing` run is the
richest (525-line synthesis, 88 typeset equations, 7 `> [!derivation]-` callouts, a 24-row notation
table, 34/34 local PDFs, a full primer + methods-map) and is the **test target**. What's missing is a
note in the wiki's *thread genre*: a specific section template + an annotated Tier-A/B/C bibliography +
the wiki's citation/linking conventions.

**The register is deliberately different from squid's synthesis.** Wiki threads use purposeful **bold**
keywords, em-dashes for asides, and first-person synthesis voice — exactly what squid's *synthesis* lint
suppresses as AI-tics. That is the maintainer's deliberate house voice for this genre, not slop. The
thread-writer targets the **wiki house style**, and the thread is **exempt** from squid's synthesis lint.

**Standalone constraint.** The plugin ships the thread *conventions* (template + style), never the wiki
content. A workspace's `thread.md` is self-contained; the wiki is read only optionally, read-only, to
resolve links.

## Resolved decisions

1. **Scope = full wiki-thread** — the complete genre (opener, scope, quality filter, executive summary,
   established findings, flagged synthesis, annotated Tier-A/B/C bibliography, research gap, open
   questions, minimal citation set, derivations, log).
2. **Linking = convention-matching + optional wiki resolution** — default emits convention-matching
   `[[slugs]]` + a wire-up sidecar (standalone-safe); given a wiki path, resolves links against the wiki
   read-only.
3. **Writing only** — toy/experiment references are left as a placeholder checklist; code-generation is a
   separate future ambition.
4. **One thread per run**, saved to `research/<slug>/thread.md`, complementing (not replacing) the
   existing artifacts.
5. **Thread register = wiki house style**, exempt from squid's synthesis lint.

## Design

### 1. The skill + flow

`skills/research-thread/SKILL.md` — `/research-thread <run-slug> [wiki <path>] [quick|full]`,
`disable-model-invocation: true`. Mirrors `/research-tutorial`'s proven shape:

- **Step 0 — resolve paths.** Plugin root (two dirs up from the skill base) → `RESEARCH_DOC`,
  `STYLE_DOC`. Resolve `WRITING_MEMORY` if present (reuse). Resolve the run folder
  `research/<run-slug>/`; if absent, error with the available slugs. Resolve the optional `wiki <path>`
  (and a project-local default if configured).
- **Step 1 — read the run.** Read `plan.md`, `synthesis.md`, `directions.md`, `sources.md`, the
  `tutorials/*` (primer + methods-map), and the tail of `log.md`. These are the only inputs — the thread
  re-projects existing, already-gated material; it introduces no new claims and runs no search.
- **Step 2 — draft the thread** into the canonical template (§2) per the thread register (§5), applying
  the transform (§3) and citation translation (§4). The orchestrator drafts (like the tutorial); no new
  agent.
- **Step 3 — review loop** (§6): two parallel lenses → revise → cap 2 cycles.
- **Step 4 — human-gated save** (§7): present the draft + a review summary; `save / edit / cancel`; diff
  on re-run. Save `thread.md` + the wire-up sidecar. Never write to the wiki.

`quick` vs `full`: `full` (default) is the complete genre; `quick` omits the annotated bibliography's
per-paper depth (a compact source table instead) and the Derivations section — for a lighter thread.

### 2. Canonical thread template (the save shape)

Frontmatter (the wiki's thread fields):
```yaml
---
title: "{question as a title}"
status: active | concluded            # squid runs that reached Gate #2 → concluded; else active
question: "{the run's central question, full interrogative}"
date_started: {run start, from log}
last_updated: {today}
related_topics: ["[[...]]"]            # broad topic pages (best-guess or wiki-resolved)
related_concepts: ["[[...]]"]          # concepts the thread touches (+ methods-map neighbors)
related_threads: ["[[...]]"]
tags: [{topic tags}, research-thread]
raw_folder: "research/{slug}/ (squid run; gated PDFs in sources/)"
related: ["[[...]]"]                   # catch-all
---
```

Body sections, in order (a `full` thread):
1. `> **What this note is.**` — genre = an original analysis grounded in a credibility-gated literature
   sweep; **established results are cited, my synthesis is flagged**; intended reader; honest status
   (which claims are Tier-A vs Tier-B-caveated, what's the author's analysis vs the literature's).
2. **Scope** — in / out / adjacent (from `plan.md`).
3. **Quality filter** — the Tier-A/B/C venue policy (from the credibility gate).
4. **Executive summary** — 3–7 bullet claims (from synthesis "answer so far" + top themes).
5. **Findings** — the established results argued at depth (synthesis themes; math, comparison tables,
   foldable derivations preserved), with the flagged **my-synthesis** items (the synthesis "Analysis —
   beyond the sources" A-items, confidence-tagged) clearly marked as the author's, not the literature's.
6. **Annotated bibliography — Tier A / B / C.** Per paper: **Authors** · **Venue** · `[(PDF)]` ·
   arXiv · **Paradigm** (one line) · **Why it matters** (to this thread) · **Caution** · **Use in your
   work**. Built from `sources.md` (tier, provenance, key-claims, Local) + which themes cite it.
7. **Research gap** — what the literature lacks (from synthesis "Gaps", tensions).
8. **Open questions to investigate** — actionable questions + the run's proposals (from `directions.md`).
9. **Minimal citation set** — the 4–6 load-bearing Tier-A sources.
10. **Suggested reading order** — concepts → Tier-A papers → derivations.
11. **Derivations** (D1, D2, …) — foldable, from the synthesis `> [!derivation]-` callouts + tutorial
    folded math.
12. **Log** — one dated "thread consolidated from run `<slug>`" entry summarizing the run's provenance.

### 3. The transform (artifact → section)

| Thread section | Sourced from |
|---|---|
| Frontmatter | `plan.md` (question/scope), methods-map neighbors → `related_concepts`, `log.md` dates, plan topic → tags |
| `> What this note is.` | synthesis "answer so far" + genre declaration |
| Scope / Quality filter | `plan.md` scope + `sources.md` credibility gate |
| Executive summary | synthesis "answer so far" + top themes, as claims |
| Findings (+ flagged synthesis) | synthesis themes + "Analysis — beyond the sources" (A-items) |
| Annotated bibliography | `sources.md` entries re-rendered per-paper; "why-it-matters"/"use" synthesized from relevance + which themes cite |
| Research gap / Open questions | synthesis "Gaps & follow-up queries" + `directions.md` |
| Minimal citation set | load-bearing Tier-A sources |
| Derivations | synthesis `> [!derivation]-` + tutorial folded math |
| Log | run milestones |

### 4. Citation translation

`[S#]` (squid, resolving to `sources.md`) → the wiki form: an inline `[[author-year-slug]]` source-page
wikilink **and** a `[(PDF)](<sources/S#--slug.pdf>)` link to the run's local copy. The slug is derived
canonically (first-author surname + year + short title), matching the wiki's source-page naming. Tier-B
sources keep an explicit caveat at the point of use (preserving squid's gate). Tier map: squid A → wiki
A, squid B → wiki B, context-only accepted → wiki C.

### 5. Wiki-awareness (optional, read-only)

- **Default (no wiki path):** emit convention-matching `[[slugs]]` + a **wire-up sidecar**
  `research/<slug>/thread--wireup.md` — the integration checklist: proposed `related_concepts/topics/
  threads`, the source pages to create in `wiki/sources/`, and how to drop the note into
  `wiki/research-threads/`. The thread itself stays clean and wiki-ready.
- **Given `wiki <path>`:** additionally read `<wiki>/concepts/`, `<wiki>/sources/`, `<wiki>/maps/`
  read-only to (a) resolve `related_concepts`/`maps` links to real existing slugs, (b) reuse existing
  source-page slugs for citations, (c) list in the sidecar which referenced sources still need new pages.
  **Never writes to the wiki.**

### 6. The thread register (style contract)

Captured from the wiki house style, distilled into the skill (ships the convention, not the wiki):
purposeful **bold** keywords for scanability; em-dashes for appositive asides; first-person synthesis
voice ("my analysis shows…") alongside third-person for established facts; **every term defined on first
use**; honest, explicit caveats (Tier-B, toy-scale, single-dataset); tables for comparisons; LaTeX math
(`$…$` / `$$…$$`); foldable derivations; `[[wikilinks]]` + `[(PDF)](<…>)` citations. **Exempt from
squid's synthesis lint** (the anti-bold / anti-em-dash density checks do not apply to the thread genre).
The depth requirements still hold (show-don't-name, derive-don't-assert, grounded claims).

### 7. Review loop

Two parallel lenses (mirrors `/research-tutorial`), revise to resolve Blockers, **cap 2 cycles**,
human-gated save:
- **Wiki-editor lens** — genre + house-style fidelity: all template sections present and ordered; the
  `> **What this note is.**` opener declares genre/reader/status; the annotated bibliography is complete
  per-paper; frontmatter carries the required fields; citations use `[[ ]]` + `[(PDF)]`; the register is
  the wiki voice; length in the wiki norm (~3k–15k words). Blocks on a missing genre element.
- **Source-fidelity lens** — no drift: every claim traces to the run's `synthesis.md`/`sources.md`; no
  new un-grounded claim is introduced; tiers preserved; each `[S#]→[[slug]]` points to the right source;
  the flagged "my synthesis" items are exactly the synthesis Analysis A-items (nothing smuggled). Blocks
  on drift — this is the analog of the synthesizer's grounding guard.

Thread feedback compounds into the existing `writing-quality--memory.md`.

## Reused vs new

| Piece | Status |
|---|---|
| `/research-thread` skill + thread template + transform | **New** |
| Thread register (style contract) | **New** (captured wiki convention, in the skill) |
| Two-lens review loop | **Reuse** the `/research-tutorial` pattern (new lens briefs) |
| Reading the run artifacts; `[S#]`/Tier/Local conventions | **Reuse** |
| Writing-quality memory compounding | **Reuse** |
| A dedicated thread-writer agent | **NOT built** — the skill orchestrates the draft (like the tutorial) |
| Writing to the wiki; code/toy generation; multi-run merge | **NOT built** (out of scope) |

## Files (anticipated; the plan finalizes)

- New: `skills/research-thread/SKILL.md`.
- Modify: `docs/RESEARCH_PROCESS.md` (a `## Research threads` section — the genre, the transform, the
  standalone/optional-wiki note), `README.md` (one row), `CLAUDE.md` (skills tree entry + one editing-
  conventions line).

## Verification

`claude plugin validate`; a dry run of `/research-thread simulated-annealing-ml` in the
`simulated_annealing` workspace producing `research/simulated-annealing-ml/thread.md` + the wire-up
sidecar; manual read-through against the wiki thread checklist (genre sections present, annotated
bibliography complete, citations translated, register matches, no drift from the synthesis); confirm
nothing is written to the wiki and the run's other artifacts are untouched.

## Out of scope

- Writing to / modifying the wiki (the maintainer integrates by hand; the sidecar guides it).
- Generating runnable toy/experiment code (the standalone-repo "implementation code" ambition is a
  separate, larger feature — likely the engineering layer).
- Merging multiple runs into one thread (one thread per run for v1).

## Resolved (review, 2026-06-18)

1. **Thread filename:** `research/<slug>/thread.md` (the wire-up sidecar `thread--wireup.md` names the
   eventual wiki slug).
2. **`status`:** auto-map — a run that reached Gate #2 "accept" → `concluded`, otherwise `active`; the
   maintainer overwrites if needed.
