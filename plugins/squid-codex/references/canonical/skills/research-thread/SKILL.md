<!-- GENERATED — do not edit; run scripts/gen_codex.py -->

---
name: research-thread
description: Consolidate a finished /research run into ONE wiki-ready research-thread note — a self-contained, high-quality writing artifact in a personal research wiki's "thread" genre. Re-projects the run's already-gated material (synthesis, directions, sources, primers) into the canonical thread template — a What-this-note-is opener, an intuition-first Prerequisites primer + Notation table for newcomer readers, scope, a motivation/problem-formulation beat, executive summary, established findings (led intuition-first) with the author's synthesis flagged, a core-N-plus-scannable-table References section, research gap, open questions, foldable derivations, an end provenance method note, a log — translating [S#] citations to the wiki's [[author-year-slug]] + [(PDF)] form and writing in the wiki house register. Introduces no new claims and runs no search. Drafted, improved through a two-lens review (wiki-editor + source-fidelity), then saved (human-gated) to research/<slug>/thread.md plus a wire-up sidecar; never writes to the wiki. Use when a finished /research run should become a publishable thread note, or the user says "/research-thread", "consolidate <run> into a thread", "make a wiki thread from <run>". Companion to /research; threads live next to the run.
disable-model-invocation: true
argument-hint: <run-slug> [wiki <path>] [quick|full]
---

# Research Thread — consolidate a run into a wiki-ready note

Consolidate ONE finished `/research` run into a single **research thread**: a self-contained, high-quality writing note in the maintainer's personal-wiki *thread genre*, ready to drop into `wiki/research-threads/` by hand. A `/research` run already produces ~85% of the raw material — `synthesis.md` (deep, typeset math, foldable derivations), `directions.md`, `sources.md` (a credibility-gated, mostly-local library), and primers under `tutorials/`. The gap is **genre, not depth**: the thread re-projects that material into the wiki's specific section template (an intuition-first on-ramp, a motivated problem formulation, a core-N-plus-scannable References section, provenance demoted to an end method note), and the wiki's citation and linking conventions. The thread **introduces no new claims and runs no search** — it re-renders already-gated material in a new, more digestible shape.

You are the **orchestrator** — a manager who also drafts, exactly like `/research-tutorial`. You read the run, draft the note into the thread template applying a defined transform and citation translation, improve it through a two-lens review, and save it only after the human approves. The two review lenses do the critique; you revise from their findings. The skill **never writes to the wiki** (reading a given wiki path is read-only and optional) and **never saves without the human** (the save is human-gated, with a diff on re-run).

`$ARGUMENTS` carries the **run-slug** (required), an optional `wiki <path>` (read-only resolution of links against an existing wiki), and an optional depth `quick|full` (default `full`). If the run-slug is empty or names no run folder, list the available run slugs and stop.

---

## Step 0 — Resolve paths, parse the request

**Resolve the canonical docs.** Same base-directory trick as `/research-tutorial` Step 1: the harness states `Base directory for this skill: <path>` (it ends in `…/skills/research-thread`). The plugin root is **two directories up** from that base. Set `RESEARCH_DOC = <plugin-root>/docs/RESEARCH_PROCESS.md` and `STYLE_DOC = <plugin-root>/docs/WRITING_STYLE.md`, verifying each with `ls`. If the consuming project has its own `docs/RESEARCH_PROCESS.md` or `docs/WRITING_STYLE.md` (relative to cwd), prefer the project copy. `{STYLE_DOC}` is referenced for the depth rules its `## Quality rubric` carries, but its synthesis-prose lint does **not** govern the thread (the thread register, below, is the wiki house style and is **exempt** from that lint). **Also resolve `WRITING_MEMORY = <cwd>/research-profiles/writing-quality--memory.md`** with the same project-local check (a sibling of `research/`, not inside it) — set it only if the file is present; it carries accrued workspace prose/depth/format lessons, threaded only into the draft step (Step 2) when present, and never threaded when absent (strictly additive). This is the same resolution `/research-tutorial` does; do not re-derive it.

**Parse `$ARGUMENTS`.**

- The **run-slug** (required) — names a run folder `research/<run-slug>/`. Resolve it relative to cwd. **If absent**, `ls research/` and list the available slugs for the human, then stop — never invent a run.
- Optional **`wiki <path>`** — a personal-wiki root. If given, it is read **read-only** in Step 1/wiki-awareness to resolve links and reuse source slugs; the skill never writes there. If a project-local default wiki path is configured (a `wiki:` line in a project settings file), use it; otherwise default to no wiki (the standalone path).
- Optional **depth `quick|full`** — `full` (default) is the complete genre (every section, including the Prerequisites primer + Notation on-ramp for a newcomer reader, and the Derivations section); `quick` omits the on-ramp (Prerequisites + Notation) and the Derivations section, for a lighter thread. The References section (core-N + scannable table) stays at both depths.

**Derive the canonical thread slug.** The wiki slug is `<run-slug>` by default (it already reads as a topic slug); record it for the wire-up sidecar. The output path is fixed: `research/<run-slug>/thread.md`, with the wire-up sidecar at `research/<run-slug>/thread--wireup.md`.

---

## Step 1 — Read the run (the only inputs)

Read the run's artifacts — **these are the ONLY inputs**; the thread introduces no new claims and runs no search:

- `research/<run-slug>/plan.md` — question(s), in/out/adjacent scope, the credibility gate's source strategy, the `Constraints` (intended reader), the topic (for tags).
- `research/<run-slug>/synthesis.md` — the answer-so-far, the themes argued at depth (math, comparison tables, `> [!derivation]-` callouts), the **Analysis — beyond the sources** A-items (Status / Derivation / Confidence), the gaps & follow-up queries, the evidence ledger.
- `research/<run-slug>/directions.md` — the candidate directions (these seed the open-questions section).
- `research/<run-slug>/sources.md` — per-source Tier (A/B), one-line provenance, `Local:` path, relevance, key-claim(s), and the Rejected list. List `research/<run-slug>/sources/` to confirm the local PDFs the citations link to.
- `research/<run-slug>/tutorials/*` — the primer and methods-map if present (they feed the Derivations section's folded math and the reading order).
- the tail of `research/<run-slug>/log.md` — the run's milestones and the Gate-#2 decision (drives the `status` auto-map below).

Confirm the artifacts exist before drafting. If `synthesis.md` or `sources.md` is missing, the run is not far enough along to consolidate — say so and stop.

---

## Step 2 — Draft the thread

Draft into the canonical thread template (below) applying the transform and the citation translation, in the thread register (below). The orchestrator drafts (like the tutorial); no new agent.

**The transform (artifact → section).** Each thread section is re-projected from the run, not re-researched:

| Thread section | Sourced from |
|---|---|
| Frontmatter | `plan.md` (question/scope) → `title`/`question`; methods-map neighbors → `related_concepts`; `log.md` dates → `date_started`; plan topic → `tags` |
| `> **What this note is.**` | synthesis "answer so far" + the genre declaration (cited results vs the author's flagged synthesis; intended reader; the stakes / why-it-matters; honest solid-vs-press-grade status; a pointer to the end Provenance note) |
| Prerequisites — a primer | the foundational terms a newcomer reader needs, intuition-first (plan.md expertise constraint decides whether to include); `tutorials/` primers for the deep dives |
| Notation and key concepts | the symbols/terms the synthesis math uses → two glossed tables with a plain-language-handle column |
| Scope | `plan.md` in / out / adjacent |
| Motivation & problem formulation | the stakes for the reader + the central object/setup motivated (from synthesis "answer so far" + the first theme's formulation) |
| Executive summary | synthesis "answer so far" + top themes, rewritten as 3–7 claims |
| Findings (+ flagged synthesis) | synthesis themes (math, tables, foldable derivations preserved), led intuition-first and self-contained, + the **Analysis — beyond the sources** A-items, **clearly marked as the author's, not the literature's** |
| References | the credibility-gated library → a **core-N must-trust** list + ONE scannable table (tier as a column); NOT a per-paper, tier-grouped catalog |
| Research gap | synthesis "Gaps & follow-up queries" + tensions |
| Open questions | actionable questions + the run's proposals (from `directions.md`) |
| Minimal citation set | the 4–6 load-bearing Tier-A sources (may merge into the References core-N) |
| Derivations | the synthesis `> [!derivation]-` callouts + tutorial folded math; AND where the synthesis argues load-bearing math in prose without a callout, a derivation **constructed** from that math (grounded — every step traces to the synthesis/sources; no new result) |
| Provenance (method note) | `sources.md` credibility gate (the Tier-A/B venue policy + counts) — demoted to an end note, *skip on a reading pass* |
| Log | one dated "thread consolidated from run `<slug>`" entry summarizing the run's provenance |

**Citation translation.** `[S#]` (squid, resolving to `sources.md`) becomes the wiki form at every point of use: an inline `[[source-slug]]` source-page wikilink **and** a `[(PDF)](<sources/S#--slug.pdf>)` link to the run's local copy. Derive the slug to match the wiki's source-page convention — **title-first, kebab-cased short title, optionally suffixed `-<first-author-surname>-<year>` for disambiguation** (e.g. `S1` → `[[neural-simulated-annealing-correia-2023]]`; a distinctive title may stand alone). **If a source's first author, year, or title is missing from `sources.md`, read its local PDF (the `Local:` path) to recover the real provenance before emitting the slug** — emit a clearly-flagged placeholder only when the PDF is also unavailable, and flag it in the entry's **Caution** and the sidecar. Never invent an author. **Tier-B sources keep an explicit caveat at the point of use** (preserving squid's gate; the synthesis's `[S#, B]` mark carries over as a caveat clause). **Tier map:** squid Tier A → wiki Tier A; squid Tier B → wiki Tier B; a context-only accepted source → wiki Tier C.

**`status` auto-map.** A run that reached **Gate #2 "accept"** (the `log.md` shows an accept/handoff — handoff follows an accept) → `status: concluded`; otherwise → `status: active`. The human overrides at the gate.

Then thread the depth rules: the `{STYLE_DOC}` **Quality rubric** still binds (show-don't-name, derive-don't-assert, grounded claims, functional clickable output) even though the synthesis lint does not. Writing-quality memory: `{WRITING_MEMORY}` (if present — accrued workspace prose/depth/format lessons; read it after the register; it sharpens how you write and never overrides the Quality rubric).

---

## Step 3 — Review and improve (the two-lens loop)

Before the human sees it, improve the draft through a two-lens review. Launch BOTH lenses in parallel — one message, two `Agent(subagent_type="general-purpose", …)` calls — each given the draft path, the run's `sources/` and `synthesis.md` for fact-checking, and its brief. The lenses **return findings; they do not edit the file**. This mirrors `/research-tutorial` Step 5.

- **Wiki-editor lens** — prompt: "You are the editor of a personal research wiki; you know its *research-thread* genre and house style cold. Read `<draft path>` as a thread about to be filed. Check genre + house-style + DIGESTIBILITY: every template section is present and in order (What-this-note-is → Table of contents [full] → Prerequisites primer [include when the intended reader is a newcomer to the domain] → Notation and key concepts [include when math/symbol-heavy] → Scope → Motivation & problem formulation → Executive summary → Findings → References → Research gap → Open questions → Minimal citation set → Suggested reading order → Derivations [full only] → Provenance (method note) → Log); the `> **What this note is.**` opener declares the genre, the intended reader, the stakes (why it matters), and the honest solid-vs-press-grade status, and points provenance to the end note; the on-ramp is present for a newcomer reader (a Prerequisites primer that leads intuition-first, and a Notation table with a plain-language-handle column), each term also glossed inline; Findings **lead with intuition/analogy before the formalism** and are **self-contained** (each formal object defined inline and *motivated before its closed form*, with no required click-out to the Notation table / a fold / a source to follow the argument); **References is a core-N must-trust list + ONE scannable table with tier as a COLUMN — NOT a per-paper, tier-grouped, eight-bullet catalog**; the credibility-gate scaffolding is demoted to the end **Provenance (method note)** and the prose uses lightweight \"solid\"/\"press-grade\" tags rather than a `(Tier B)` apparatus; the frontmatter carries the required fields; citations use `[[source-slug]]` wikilinks + `[(PDF)]` local links; the register is the wiki voice (purposeful bold, em-dashes for asides, first-person synthesis, define-on-first-use, honest caveats, tables, typeset LaTeX, foldable derivations); the note has **sufficient depth** — the wiki norm runs long, and **quality and depth outrank brevity: never flag length as excess; a thread is as long as its material warrants.** Flag only a section too THIN, never the note too long. Tag a **Blocker** on a missing genre element (an absent or out-of-order template section; a Findings theme that opens with the formalism instead of the intuition, or that forces a click-out to follow; a References section reverting to the per-paper tier-grouped catalog; credibility-gate scaffolding left inline in the body; a missing What-this-note-is declaration; a citation left as a bare `[S#]`). Tag a **Nit** for a sharpening. Note: this genre is the wiki house style and is **exempt from the synthesis lint** — do NOT flag purposeful bold, em-dashes, or first-person as AI-tics; they are the register here. Quote the exact location. Return a findings list; do not edit the file."
- **Source-fidelity lens** — prompt: "You are a fact-checker guarding against drift. Read `<draft path>` against the run's `synthesis.md` and `sources.md` (and `sources/` for the full texts). The thread must re-project the run with **no drift**: every claim traces to `synthesis.md` or `sources.md`; **no new un-grounded claim** is introduced (the thread runs no search and adds no literature); the tiers are preserved (a Tier-B source still carries its caveat); each `[S#] → [[source-slug]]` translation resolves to the **right** source (the slug matches the wiki's title-first convention for the actual source in `sources.md`); the `[(PDF)]` path matches the run's local file; **any constructed derivation's every step traces to the synthesis's math/claims — it makes implicit math explicit and introduces no new result**; and the flagged **'my synthesis'** items in Findings are **exactly** the synthesis's `Analysis — beyond the sources` A-items, with nothing smuggled in as the author's that the literature actually stated, and nothing stated as the literature's that is really the author's. Tag a **Blocker** on any drift — an un-grounded claim, a mis-resolved citation, a dropped Tier-B caveat, a mis-attributed synthesis item. This is the analog of the synthesizer's grounding guard. Quote the exact location and the source it should trace to. Return a findings list; do not edit the file."

**Severity.** A **Blocker** = a missing genre element (wiki-editor) or any drift from the run (source-fidelity). A **Nit** = a sharpening. Drift Blockers and genre Blockers are equal — fix both.

Revise the draft to resolve every Blocker (and the cheap Nits), then re-run BOTH lenses once. **Cap: 2 cycles.** Anything unresolved after cycle 2 is surfaced to the human at Step 4, flagged. Append a `[research-thread]` review entry to the run's `log.md` noting the lenses, the cycle count, and the Blocker counts.

---

## Step 4 — Human review, then save + wire-up sidecar

Mirror `/research-tutorial` Step 6: present the improved draft plus a one-paragraph review summary (the lenses used, what changed, any unresolved flag), then **persist nothing without explicit approval.**

- **New thread** → show the full draft; ask `save / edit / cancel`.
- **Re-run for an existing thread** → read the current `thread.md`, show a **diff** of the draft against it, and ask before overwriting. Never silently overwrite a thread the human already reviewed.

On `save`, write **both** files and set `last_updated:` to today:

1. `research/<run-slug>/thread.md` — the consolidated thread (the template below).
2. `research/<run-slug>/thread--wireup.md` — the **wire-up sidecar**, the integration checklist that keeps `thread.md` clean and wiki-ready: the proposed `related_concepts` / `related_topics` / `related_threads` (best-guess or wiki-resolved); which referenced sources still need a new page under `wiki/sources/` (and the slug each should take); the eventual wiki slug and how to drop the note into `wiki/research-threads/`; and any runnable-toy placeholders the genre wants (the thread is **writing-only** — toy/experiment references are left as a placeholder checklist, not generated).

**NEVER write to the wiki.** The sidecar guides the maintainer's by-hand integration; the skill's only writes are `thread.md` and `thread--wireup.md` under the run folder.

**Writing-quality memory capture (optional, human-gated).** If the human's review gave prose/depth/format feedback (edit instructions, "still too thin" / "the bibliography entries are too terse"), offer to capture **1–3 writing-quality lessons** to `research-profiles/writing-quality--memory.md` — append-only, create with the `kind: writing-quality-memory` frontmatter if absent (sibling of `research/`, not inside it). Skip silently if the human declines or no `research-profiles/` dir exists; mirror the same human-gated save discipline as the thread.

---

## The canonical thread template (the save shape)

A `full` thread is the complete wiki genre. The frontmatter carries the wiki's thread fields; the body sections follow in this order. `depth: quick` omits the per-paper bibliography depth (a compact source table instead) and the **Derivations** section.

```markdown
---
title: "{the question as a title}"
status: active | concluded            # a squid run that reached Gate #2 "accept" → concluded; else active
question: "{the run's central question, full interrogative}"
date_started: {run start, from log.md}
last_updated: {today}
related_topics: ["[[...]]"]            # broad topic pages (best-guess, or wiki-resolved with a wiki path)
related_concepts: ["[[...]]"]          # concepts the thread touches (+ methods-map neighbors)
related_threads: ["[[...]]"]
tags: [{topic tags}, research-thread]
raw_folder: "research/{slug}/ (squid run; gated PDFs in sources/)"
related: ["[[...]]"]                   # catch-all
---

> **What this note is.** An original analysis grounded in a credibility-gated literature sweep: established results are cited, **my synthesis is flagged** as mine. Written for {the intended reader, from plan.md Constraints} — so {a newcomer-facing note defines every term on first use and leads with intuition before the formalism; an expert-peer note assumes fluency and moves fast}. **Why it matters:** {the stakes — what the answer changes for that reader, in their terms}. Honest status: which claims are **solid** (load-bearing, peer-reviewed or major-institution), which lean on **press-grade** sources (caveated in-text), and which are my analysis beyond the literature. How the sources were vetted is a method note at the [[#Provenance (method note)|end]], deliberately out of the reading flow.

## Table of contents                        <!-- full depth: Obsidian [[#Heading]] links for navigation; quick omits -->
{Link the major `##` sections and the **Findings** `###` sub-sections — `- [[#Heading]]`, sub-sections indented. Do NOT list the per-paper References rows. Each anchor's text must match its heading EXACTLY (watch em-dashes and parentheses, a frequent break).}

## Prerequisites — a primer            <!-- when the intended reader is a newcomer to the domain (read plan.md's expertise constraint); for an expert-peer reader, trim or omit. quick depth: omit. -->
{A short on-ramp, **intuition first, then the precise meaning**. One bullet per foundational term the rest of the note leans on, each with a concrete analogy or a mnemonic; a term that feeds a load-bearing claim links to its source. Mark the elementary definitions as standard convention (not from the gated library) and ground the load-bearing ones in a cited source. Connect to the reader's own field where the structure genuinely matches (for an ML reader: a value function as a Bellman backup, a coupled objective as a two-player game). Point to companion `tutorials/` primers for the deep dives.}

## Notation and key concepts            <!-- when the thread is symbol- or math-heavy. quick depth: omit. -->
{A `| Symbol | Meaning | Plain-language handle |` table for the symbols and a `| Term | Definition (first-use gloss) |` table for the named concepts. The "plain-language handle" column is the intuitive one-liner, not the formal definition. Each symbol and term is ALSO glossed at first use in the prose — the table lets the prose stay light, it never replaces the inline gloss.}

## Scope
{in / out / adjacent, from plan.md.}

## Motivation & problem formulation
{Two beats, kept tight. **Why it matters:** the stakes for the intended reader — what decision or understanding the answer changes, in their terms. **How the problem is framed:** the central object or setup, stated and *motivated* — what is being optimized / measured / compared, why this is the right framing, and the assumptions it rests on — before Findings dives into results. If the first Findings theme already formulates the object rigorously (motivated, not merely asserted), fold the formulation there and keep this section to the why-it-matters beat, rather than duplicating.}

## Executive summary
{3–7 claims, from the synthesis "answer so far" + top themes. Open with the framing or the verdict, then the load-bearing facts; mark confidence where it matters.}

## Findings
{The established results argued at depth — the synthesis themes, with their math (typeset $\ldots$ / $$\ldots$$), comparison tables, and foldable `> [!derivation]-` callouts preserved. Three register rules carry the digestibility. **Lead each theme with the intuition and a concrete analogy, THEN the formal statement** — never the formalism first. **Make every section self-contained:** define each formal object inline at first use, and *motivate why it is the right object before giving its closed form* (show the object is forced by a no-arbitrage / optimality / symmetry argument and why this functional form is the natural one — do not just assert the formula); the reader should never need to click to the Notation table, a derivation fold, or a source page to follow the argument. **Connect to the reader's domain** where the structure matches. Citations are translated to `[[source-slug]]` + `[(PDF)](<sources/S#--slug.pdf>)` at each point of use; a press-grade (Tier-B) claim carries a lightweight in-text caveat ("press-grade", "one small-scale study"), NOT a `(Tier B)` tag.}

### My synthesis (beyond the sources)
{The synthesizer's `Analysis — beyond the sources` A-items, confidence-tagged, clearly marked as the author's analysis — NOT the literature's. Each carries its Status / Derivation / Confidence and grounds its derivation in the cited sources.}

## References
{NOT a tier-grouped, per-paper catalog (that read as cumbersome — a glossary, not a guide). Two parts. **(1) The core N (~4–6) you must trust** — a short numbered list, one line each on what the thread's *verdict and load-bearing claims* rest on, each with a `[(PDF)]` link (and a `[[source-slug]]` wikilink). **(2) The rest of the library** — ONE scannable table, `| Source | Tier | What it establishes | PDF |`, with **tier as a column** (A = solid, B = press-grade) so a reader scans source quality at a glance. A source the thread never leans on is cited inline only, not given a row. This replaces the old per-paper, eight-bullet, Tier-A/B/C-heading format.}

**The core N.**
1. **{Authors (year), venue}** — {the one thing the thread's verdict rests on it for; why you must trust it.} [(PDF)](<sources/S#--slug.pdf>) [[source-slug]]
2. ...

**The rest of the library.**

| Source | Tier | What it establishes | PDF |
|---|---|---|---|
| {Authors (year), venue} | A | {one line} | [(PDF)](<sources/S#--slug.pdf>) |
| {Authors (year), venue} | B | {one line} *(press-grade)* | [(PDF)](<sources/S#--slug.pdf>) |

## Research gap
{what the literature lacks, from the synthesis "Gaps & follow-up queries" and tensions.}

## Open questions to investigate
{actionable questions + the run's proposals (from directions.md), each grounded.}

## Minimal citation set
{the 4–6 load-bearing Tier-A sources — the ones a reader must read to trust the thread.}

## Suggested reading order
{concepts → Tier-A papers → derivations: the path through the material.}

## Derivations                              <!-- full depth only; quick omits -->
{D1, D2, … — foldable `> [!derivation]-` callouts. Carry over the synthesis's and the tutorial's folded math; AND where the synthesis argues load-bearing math in prose without a callout, **construct** a grounded foldable derivation from it (every step traces to the synthesis/sources — no new result). The load-bearing equation stays visible; the long derivation folds.}

> [!derivation]- D1 — {title}
>
> {the derivation, math as math, each content line `> `-prefixed.}

## Provenance (method note)
{*Internal record — skip on a reading pass.* The demoted credibility-gate scaffolding, kept out of the main reading flow on purpose. The tier policy the in-text "solid" / "press-grade" tags reflect: **Tier A (solid, load-bearing)** = peer-reviewed at a recognized venue, or a report from a major institution / well-known lab; **Tier B (press-grade, caveated)** = a preprint, workshop paper, or reputable press / sell-side source, used only where no Tier-A source exists yet and always flagged in-text, never for a definition or a core result. The accepted / rejected counts (from `sources.md`), and what stays press-grade by necessity (the soft spot the verdict still rests on).}

## Log
- {today} — Thread consolidated from run `{slug}` ({the run's provenance: N gated sources, M Tier-A; synthesis depth loop; primers built; Gate-#2 outcome}).
```

---

## Thread register (the style contract)

The thread is written in the **wiki house style**, captured here as a convention the plugin ships (it ships the *register*, never the wiki content). This register is **deliberately different from squid's synthesis prose** and is **explicitly exempt from `{STYLE_DOC}`'s synthesis lint** — its anti-bold and anti-em-dash density checks, and its first-person ban, do **not** apply to the thread genre. The depth rules in `{STYLE_DOC}`'s `## Quality rubric` still bind.

- **Intuition before formalism.** Lead with a concrete analogy or a mental handle, then the precise statement — never the formula first. A correct result stated cold reads flat; give the reader something to hold first.
- **Self-contained sections.** Define each formal object inline at first use, and motivate *why it is the right object* before giving its closed form (it is forced by a no-arbitrage / optimality / symmetry argument; this functional form is the natural one). The reader should never need to click to the Notation table, a derivation fold, or a source page to follow the argument.
- **Connect to the reader's domain.** Bridge to the reader's own field where the structure genuinely matches (for an ML reader: Bellman/MDP value functions, two-player games, importance weights) — a borrowed intuition lands faster than a fresh one.
- **Provenance stays out of the reading flow.** In the prose use lightweight "solid" / "press-grade" tags only where a caveat is load-bearing; the tier methodology, counts, and venue policy live in the end **Provenance (method note)**, not inline.
- **Purposeful bold** for key terms, so a reader can scan the note. (Exempt from the bold-density check.)
- **Em-dashes** for appositive asides — used where a comma would blur the aside. (Exempt from the em-dash-density check.)
- **First-person synthesis voice** ("my analysis shows…") alongside third-person for established facts, so the author's contribution is audible and separable from the literature's. (Exempt from the first-person ban.)
- **Every term defined on first use.**
- **Honest, explicit caveats** — Tier-B, toy-scale, single-dataset — stated at the point of use.
- **Tables** for genuine comparisons across a shared set of dimensions.
- **LaTeX math** — inline `$\ldots$`, display `$$\ldots$$` — never prose-ASCII where the formula is the precise statement.
- **Foldable derivations** — the heavy derivation folds into a `> [!derivation]-` callout; the load-bearing equation stays visible.
- **`[[wikilinks]]` + `[(PDF)](<…>)` citations** — the wiki form, not squid's `[S#]`.

**The depth rules still hold** (the `## Quality rubric`): show-don't-name (a load-bearing mechanism component shown concretely, not merely named), derive-don't-assert (a result a technical reader would question is derived, the heavy steps folded), grounded claims (no claim outruns the run's gated sources), and functional output (every reference, arXiv id, and `Local:` path is a clickable link). The register is permissive on decoration and first-person; it is **not** permissive on depth or grounding. **Length follows the material — quality over brevity. A thread is as long as its depth warrants; never compress or drop substance to hit a word target.** The wiki norm runs long, and that is fine.

---

## Wiki-awareness (optional, read-only)

The thread is **standalone**: it is written to be wiki-ready without any wiki present. A given wiki path only sharpens the link resolution; it is never required and is never written to.

- **Default (no wiki path).** Emit convention-matching `[[slugs]]` — the canonical first-author-year-title source slugs and best-guess concept/topic slugs — plus the **wire-up sidecar** `research/<slug>/thread--wireup.md`. The sidecar is the integration checklist: the proposed `related_concepts` / `related_topics` / `related_threads`, the source pages to create under `wiki/sources/` (with the slug each takes), and how to drop the note into `wiki/research-threads/`. The thread itself stays clean and wiki-ready; the human integrates by hand.
- **Given `wiki <path>`.** Additionally read `<wiki>/concepts/`, `<wiki>/sources/`, and `<wiki>/maps/` **read-only** to (a) resolve `related_concepts` / `related_topics` / `maps` links to real existing slugs, (b) reuse existing source-page slugs for citations (so a `[[ ]]` lands on the page the wiki already has, rather than a fresh convention-matching guess), and (c) list in the sidecar which referenced sources still need a new page. **The skill never writes to the wiki** — reading is the only access. If a referenced concept or source has no existing page, the convention-matching slug stands and the sidecar flags it as needing a new page.

---

## Notes on shape

- **Strictly additive.** A thread is opt-in and changes nothing else. `/research` and every other skill behave exactly as before when a thread is never built; this skill only ever *creates* `thread.md` + `thread--wireup.md` next to a run.
- **One thread per run.** v1 consolidates a single run; merging multiple runs into one thread is out of scope.
- **Standalone, ships the convention not the wiki.** The plugin ships the thread template + register; it never ships the maintainer's wiki or threads (those live in the consuming project / the maintainer's wiki). The thread is self-contained, and a wiki path is read-only and optional.
- **Never writes to the wiki.** The only writes are `thread.md` and the wire-up sidecar under the run folder. The sidecar guides the by-hand integration into `wiki/research-threads/`; the maintainer files it.
- **Writing-only; toys are placeholders.** Toy/experiment references in the thread are left as a placeholder checklist in the sidecar — generating runnable code is a separate, larger ambition (the engineering layer), out of scope here.
- **Re-projects, never re-researches.** The run's already-gated material is the only input; the thread introduces no new claims and runs no search. The source-fidelity lens enforces this.
- **The two-lens review improves the note before the human sees it.** A wiki-editor lens checks genre + house-style + digestibility (every section present and ordered, the intuition-first on-ramp and Findings, the core-N + scannable References, provenance demoted to the end note, citations translated, the register the wiki voice); a source-fidelity lens checks no drift (every claim traces to the run, tiers preserved, citations resolve, the flagged synthesis is exactly the synthesis Analysis items). Genre Blockers and drift Blockers are equal; the loop caps at 2 cycles; the human gate is final.
- **Human-gated save.** Like `/research-tutorial`, nothing is written without explicit approval, and a re-run shows a diff before overwriting.
- **Depth is the user's steer.** `full` is the complete genre (a navigational Table of contents, the Prerequisites primer + Notation on-ramp when the reader is a newcomer, every section, and the Derivations section); `quick` is a lighter thread (no Table of contents, no Prerequisites/Notation on-ramp, no Derivations section). The References core-N + scannable table is compact enough to keep at either depth.
