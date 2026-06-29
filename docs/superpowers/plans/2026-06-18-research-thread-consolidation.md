# Research-Thread Consolidation Writer — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a `/research-thread` skill that re-projects a finished `/research` run into ONE wiki-ready research-thread note.

**Architecture:** A new single-file skill (`skills/research-thread/SKILL.md`) mirroring `/research-tutorial`: the orchestrator reads a run's artifacts, drafts the note into the wiki thread template applying a defined transform + citation translation + the captured wiki house register, runs a two-lens review (wiki-editor + source-fidelity), and human-gates the save to `research/<slug>/thread.md` + a wire-up sidecar. No new agent. Then doc updates.

**Tech Stack:** Markdown contracts only — **no code, no tests, no TDD** (per `CLAUDE.md`). Per-task "verification" = `claude plugin validate .` passes + targeted `grep` confirms required content. Acceptance test = a manual `/research-thread` smoke run on the `simulated_annealing` workspace via `--plugin-dir`.

**Source of truth for content:** `docs/superpowers/specs/2026-06-18-research-thread-consolidation-design.md` (committed `b74bf6a`). The implementer reads it in full and renders the skill faithfully; this plan gives structure + the resolved specifics, the spec gives the detailed template/transform/register.

## Global Constraints

- **Standalone:** the plugin ships the thread *conventions* (template + register), never the wiki content. The feature must run with no wiki present.
- **Never write to the wiki.** Reading a given `wiki <path>` is read-only and optional.
- **Thread register = wiki house style**, exempt from squid's synthesis lint (purposeful bold/em-dash/first-person); depth rules (show-don't-name, derive-don't-assert, grounded) still hold.
- **Reuse, don't duplicate:** mirror `/research-tutorial`'s flow (path resolution, two-lens loop, human-gated save, writing-quality-memory threading). Reference `{STYLE_DOC}`/`{RESEARCH_DOC}` resolution the same way.
- **Strictly additive:** no change to `/research` or other skills' behavior.
- **Filename:** the note is `research/<slug>/thread.md`; the wire-up sidecar is `research/<slug>/thread--wireup.md`.
- **`status` auto-map:** Gate-#2-"accept" run → `concluded`, else `active`; the user overrides.
- **American English.** Conventional Commits, each commit trailer:
  `Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>`
- **Never `git add -A`.** `docs/superpowers/` specs are historical — read, never edit.

---

### Task 1: The `/research-thread` skill

**Files:**
- Create: `skills/research-thread/SKILL.md`
- Read (reference, do not edit): `skills/research-tutorial/SKILL.md` (the pattern to mirror), `docs/superpowers/specs/2026-06-18-research-thread-consolidation-design.md` (the design), `docs/WRITING_STYLE.md` (to state the thread's exemption), one example run for shape calibration (`/Users/haonanzhu/Documents/GitHub/simulated_annealing/research/simulated-annealing-ml/`).

**Interfaces:**
- Produces: the skill `/research-thread <run-slug> [wiki <path>] [quick|full]` (default `full`), `disable-model-invocation: true`.
- Consumes: a finished run folder `research/<run-slug>/` (plan.md, synthesis.md, directions.md, sources.md, tutorials/*, log.md).

- [ ] **Step 1: Write the frontmatter + intro.** YAML (`name: research-thread`, a trigger `description`, `disable-model-invocation: true`, `argument-hint: <run-slug> [wiki <path>] [quick|full]`). Intro: the orchestrator drafts the note (manager-but-drafts, like the tutorial); the thread re-projects already-gated run material — it introduces no new claims and runs no search; it never writes to the wiki.

- [ ] **Step 2: Step 0 — resolve paths.** Mirror `/research-tutorial` Step 1 path resolution: plugin root two dirs up → `RESEARCH_DOC`, `STYLE_DOC` (prefer project-local copies). Resolve `WRITING_MEMORY` if present (thread feedback compounds there). Resolve the run folder `research/<run-slug>/`; if absent, list available slugs under `research/` and stop. Parse optional `wiki <path>` and `quick|full`.

- [ ] **Step 3: Step 1 — read the run.** Read `plan.md`, `synthesis.md`, `directions.md`, `sources.md`, `tutorials/*` (primer + methods-map if present), and the tail of `log.md`. State these are the ONLY inputs.

- [ ] **Step 4: Step 2 — draft the thread.** Into the canonical template (Step 7 below) applying the transform (spec §3) and citation translation (spec §4: `[S#]` → `[[author-year-slug]]` + `[(PDF)](<sources/S#--slug.pdf>)`, Tier-B keeps its caveat, squid A→wiki A / B→wiki B / context→C). Per the thread register (Step 8). `status` auto-maps per the Global Constraints.

- [ ] **Step 5: Step 3 — the two-lens review loop.** Mirror `/research-tutorial` Step 5: launch BOTH lenses in parallel (general-purpose), each given the draft path + the run's `sources/` + `synthesis.md` + its brief; they return findings, do not edit. **Wiki-editor lens:** genre + house-style fidelity (all template sections present + ordered; the `> **What this note is.**` opener declares genre/reader/status; the annotated Tier-A/B/C bibliography is complete per-paper; frontmatter fields present; citations use `[[ ]]` + `[(PDF)]`; register is the wiki voice; length ~3k–15k words) → Blocker on a missing genre element. **Source-fidelity lens:** no drift (every claim traces to `synthesis.md`/`sources.md`; no new un-grounded claim; tiers preserved; each `[S#]→[[slug]]` resolves to the right source; the flagged "my synthesis" items are exactly the synthesis Analysis A-items) → Blocker on drift. Revise to resolve Blockers, re-run both, **cap 2 cycles**, surface unresolved at Step 4. Append a `[research-thread]` log entry (lenses, cycles, Blocker counts).

- [ ] **Step 6: Step 4 — human-gated save + wire-up sidecar.** Mirror `/research-tutorial` Step 6: present the draft + a one-paragraph review summary (lenses, what changed, unresolved flags); `save / edit / cancel`; on re-run, show a diff before overwriting. On `save`: write `research/<slug>/thread.md` and the wire-up sidecar `research/<slug>/thread--wireup.md` (the integration checklist: proposed `related_concepts/topics/threads`, which referenced sources need new `wiki/sources/` pages, the eventual wiki slug + how to drop it into `wiki/research-threads/`, and any runnable-toy placeholders the genre wants). Set `last_updated:` to today. NEVER write to the wiki. Offer the writing-quality-memory capture (reuse the existing human-gated pattern) for any prose/depth feedback.

- [ ] **Step 7: The canonical thread template (the save shape).** Embed the full template from spec §2: the YAML frontmatter block, then the ordered sections (1 `> **What this note is.**`, 2 Scope, 3 Quality filter, 4 Executive summary, 5 Findings + flagged my-synthesis, 6 Annotated bibliography Tier A/B/C with per-paper Authors·Venue·`[(PDF)]`·arXiv·Paradigm·Why-it-matters·Caution·Use-in-your-work, 7 Research gap, 8 Open questions, 9 Minimal citation set, 10 Suggested reading order, 11 Derivations D1/D2… foldable, 12 Log). State `quick` omits the per-paper bibliography depth (a compact source table instead) and the Derivations section.

- [ ] **Step 8: The thread register + wiki-awareness sections.** A "Thread register" section distilled from spec §6 (purposeful bold, em-dashes, first-person synthesis, define-on-first-use, honest caveats, tables, LaTeX, foldable derivations, `[[wikilinks]]`+`[(PDF)]`; **exempt from `{STYLE_DOC}`'s synthesis lint**, depth rules still hold). A "Wiki-awareness" section from spec §5 (default convention-matching slugs + the wire-up sidecar; given `wiki <path>`, read `concepts/`/`sources/`/`maps/` read-only to resolve links + reuse source slugs + list sources needing new pages; never writes). A "Notes on shape" closing (strictly additive; one thread per run; writing-only, toys are placeholders; standalone).

- [ ] **Step 9: Verify.** Run:
  - `claude plugin validate .` → passes (warnings OK).
  - `grep -n 'research-thread\|thread--wireup\|What this note is\|Annotated bibliography\|Wiki-awareness\|Thread register' skills/research-thread/SKILL.md` → all present.
  - `grep -n 'exempt' skills/research-thread/SKILL.md` → the lint-exemption is stated.
  - Confirm two review lenses (wiki-editor + source-fidelity), the 2-cycle cap, and the human-gated save are present.

- [ ] **Step 10: Commit.**
```bash
git add skills/research-thread/SKILL.md
git commit -m "$(printf 'feat(research): /research-thread — consolidate a run into a wiki-ready thread note\n\nRe-projects a finished /research run into ONE research-thread note in the\nwiki genre: the section template (opener, scope, quality filter, exec\nsummary, established findings + flagged synthesis, annotated Tier-A/B/C\nbibliography, research gap, open questions, minimal citation set, foldable\nderivations, log), the wiki house register (exempt from the synthesis\nlint), [S#] -> [[slug]]+[(PDF)] citation translation, and convention-\nmatching links with optional read-only wiki resolution. Two-lens review\n(wiki-editor + source-fidelity), human-gated save to research/<slug>/\nthread.md + a wire-up sidecar. Writing-only; standalone.\n\nCo-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>')"
```

---

### Task 2: Docs — process, README, CLAUDE.md

**Files:**
- Modify: `docs/RESEARCH_PROCESS.md` (add `## Research threads`), `README.md` (one row), `CLAUDE.md` (skills tree entry + one editing-conventions line).

**Interfaces:**
- Consumes: the skill from Task 1 (names, paths, behavior).

- [ ] **Step 1: `docs/RESEARCH_PROCESS.md` — add `## Research threads`.** After the Primers section: the genre (a wiki-ready consolidation of a finished run), the artifact (`research/<slug>/thread.md` + `thread--wireup.md`), the transform-in-brief (synthesis+directions+sources+tutorials → the wiki thread shape), the register (wiki house style, exempt from the synthesis lint), the standalone + optional-read-only-wiki note, and that it's writing-only + human-gated + strictly additive.

- [ ] **Step 2: `README.md` — one row.** In the research-layer feature list: `/research-thread` consolidates a finished run into one wiki-ready research-thread note (annotated bibliography, citation translation, wiki house voice), human-gated, never touching your wiki.

- [ ] **Step 3: `CLAUDE.md` — tree + conventions.** Add `skills/research-thread/` to the skills tree block (one line), and one editing-conventions bullet: the thread genre/template/register live in `skills/research-thread/SKILL.md` and `docs/RESEARCH_PROCESS.md` (`## Research threads`); the plugin ships the convention, never the user's wiki or threads.

- [ ] **Step 4: Verify.** `claude plugin validate .` passes; `grep -rn 'research-thread' docs/RESEARCH_PROCESS.md README.md CLAUDE.md` → all present; `grep -rn 'seven fields\|all five sections' agents skills docs --include='*.md' | grep -v superpowers` → 0.

- [ ] **Step 5: Commit.**
```bash
git add docs/RESEARCH_PROCESS.md README.md CLAUDE.md
git commit -m "$(printf 'docs(research): document /research-thread (consolidation writer)\n\nCo-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>')"
```

---

### Acceptance test (after Task 2): smoke run on simulated_annealing

Not a build task — the proof. In the `simulated_annealing` workspace, with the working-tree plugin loaded (`claude --plugin-dir /Users/haonanzhu/Documents/GitHub/squid`):

- [ ] Run `/research-thread simulated-annealing-ml full`.
- [ ] Confirm it produces `research/simulated-annealing-ml/thread.md` + `thread--wireup.md`, and writes nothing to the wiki / leaves the run's other artifacts untouched.
- [ ] Read `thread.md` against the wiki thread checklist: genre sections present + ordered; the `> **What this note is.**` opener; the annotated Tier-A/B/C bibliography complete per-paper; `[S#]` translated to `[[slug]]` + `[(PDF)]`; the register matches the wiki voice (purposeful bold/em-dash/first-person); foldable derivations carried over; no claim drifts from `synthesis.md`.
- [ ] Spot-check against a real wiki thread (e.g. `wiki/research-threads/gflownet-for-reasoning.md`) for genre fidelity — read-only.
- [ ] Report findings; iterate via the writing-quality memory / a contract fix if it falls short.

## Self-Review (against the spec)

- **Spec coverage:** §1 skill+flow → Task 1 Steps 2–6; §2 template → Step 7; §3 transform + §4 citation → Step 4 + Step 7; §5 wiki-awareness → Step 8; §6 register → Step 8; §7 review → Step 5; reused-vs-new (no new agent, reuse tutorial pattern + writing-memory) → honored; docs → Task 2; verification (validate + smoke on SA) → Step 9 + acceptance test. No spec section unmapped.
- **Placeholders:** none — each step names exact files/sections/greps; long-form content is delegated to the committed spec by explicit section reference (the repo's established plan style; the skill prose is too large to inline and already exists in the spec).
- **Consistency:** filenames (`thread.md`, `thread--wireup.md`), the two lens names, the 2-cycle cap, and the `status` auto-map are used identically across tasks and match the Global Constraints + spec.
