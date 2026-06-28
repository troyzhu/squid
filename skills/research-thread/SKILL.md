---
name: research-thread
description: Consolidate a finished /research run into ONE wiki-ready research-thread note: a self-contained, readable writing artifact in a personal research wiki's "thread" genre. Re-projects the run's already-gated material (synthesis, directions, sources, primers) into a reader-facing note with a What-this-note-is opener, scope, summary, findings/guide body, compact source map, known gaps, and suggested reading order. Translates [S#] citations to wiki [[source-slug]] links plus local [(PDF)]/snapshot links. Introduces no new claims and runs no search. Drafted, improved through a two-lens review (wiki-editor + source-fidelity), then saved (human-gated) to research/<slug>/thread.md plus a wire-up sidecar; never writes to the wiki. Process details belong in log.md, sources.md, reviews.md, or thread--wireup.md, not in the thread body. Use when a finished /research run should become a publishable thread note, or the user says "/research-thread", "consolidate <run> into a thread", "make a wiki thread from <run>". Companion to /research; threads live next to the run.
disable-model-invocation: true
argument-hint: <run-slug> [wiki <path>] [quick|full]
---

# Research Thread — consolidate a run into a wiki-ready note

Consolidate ONE finished `/research` run into a single **research thread**: a self-contained, high-quality writing note in the maintainer's personal-wiki *thread genre*, ready to drop into `wiki/research-threads/` by hand. A `/research` run already produces most of the raw material: `synthesis.md`, `directions.md`, `sources.md` (a credibility-gated, mostly-local library), and primers under `tutorials/`. The gap is genre: the thread re-projects that material into a readable note with wiki citations and a compact source map. The thread **introduces no new claims and runs no search**; it re-renders already-gated material in a new shape.

You are the **orchestrator** — a manager who also drafts, exactly like `/research-tutorial`. You read the run, draft the note into the thread template applying a defined transform and citation translation, improve it through a two-lens review, and save it only after the human approves. The two review lenses do the critique; you revise from their findings. The skill **never writes to the wiki** (reading a given wiki path is read-only and optional) and **never saves without the human** (the save is human-gated, with a diff on re-run).

`$ARGUMENTS` carries the **run-slug** (required), an optional `wiki <path>` (read-only resolution of links against an existing wiki), and an optional depth `quick|full` (default `full`). If the run-slug is empty or names no run folder, list the available run slugs and stop.

---

## Step 0 — Resolve paths, parse the request

**Resolve the canonical docs.** Same base-directory trick as `/research-tutorial` Step 1: the harness states `Base directory for this skill: <path>` (it ends in `…/skills/research-thread`). The plugin root is **two directories up** from that base. Set `RESEARCH_DOC = <plugin-root>/docs/RESEARCH_PROCESS.md` and `STYLE_DOC = <plugin-root>/docs/WRITING_STYLE.md`, verifying each with `ls`. If the consuming project has its own `docs/RESEARCH_PROCESS.md` or `docs/WRITING_STYLE.md` (relative to cwd), prefer the project copy. `{STYLE_DOC}` is referenced for the depth rules its `## Quality rubric` carries, but its synthesis-prose lint does **not** govern the thread (the thread register, below, is the wiki house style and is **exempt** from that lint). **Also resolve `WRITING_MEMORY = <cwd>/research-profiles/writing-quality--memory.md`** with the same project-local check (a sibling of `research/`, not inside it) — set it only if the file is present; it carries accrued workspace prose/depth/format lessons, threaded only into the draft step (Step 2) when present, and never threaded when absent (strictly additive). This is the same resolution `/research-tutorial` does; do not re-derive it.

**Parse `$ARGUMENTS`.**

- The **run-slug** (required) — names a run folder `research/<run-slug>/`. Resolve it relative to cwd. **If absent**, `ls research/` and list the available slugs for the human, then stop — never invent a run.
- Optional **`wiki <path>`** — a personal-wiki root. If given, it is read **read-only** in Step 1/wiki-awareness to resolve links and reuse source slugs; the skill never writes there. If a project-local default wiki path is configured (a `wiki:` line in a project settings file), use it; otherwise default to no wiki (the standalone path).
- Optional **depth `quick|full`** — `full` (default) is the complete reader-facing genre (contents, scope, summary, findings/guide body, compact source map, known gaps, suggested reading order, and useful reasoning checks); `quick` may omit contents and reasoning checks for a lighter thread. Neither depth includes process telemetry in `thread.md`.

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

**Reader-facing rule.** `thread.md` is for the finished note, not for process telemetry. Keep it readable and useful to a wiki reader. Do not put review-cycle details, gate summaries, blocker counts, source-rejection process, A-code labels, or "thread consolidated from..." log entries in the note body. Put those details in `research/<run-slug>/log.md`, `sources.md`, `reviews.md`, and `thread--wireup.md`. The thread may include a compact source map and caveats needed to understand the claims, but it should not read like an audit report.

**The transform (artifact → section).** Each thread section is re-projected from the run, not re-researched:

| Thread section | Sourced from |
|---|---|
| Frontmatter | `plan.md` (question/scope) → `title`/`question`; methods-map neighbors → `related_concepts`; `log.md` dates → `date_started`; plan topic → `tags` |
| `> **What this note is.**` | synthesis "answer so far" + the genre declaration (cited established results vs the author's flagged synthesis; intended reader; honest Tier-A/Tier-B status) |
| Scope | `plan.md` in / out / adjacent |
| Source note / source map | `sources.md` credibility gate, local-copy status, and the compact map from claims to load-bearing sources; full provenance and rejected-source details stay in `sources.md` |
| Executive summary | synthesis "answer so far" + top themes, rewritten as 3–7 claims |
| Findings / guide body | synthesis themes, tables, and practical implications; integrate the **Analysis — beyond the sources** A-items as clearly marked synthesis or "main synthesis" prose, but do not expose internal A-code labels unless they are genuinely useful to the reader |
| Known gaps | synthesis "Gaps & follow-up queries" + tensions, rewritten as reader-facing limits |
| Follow-up questions | actionable questions from `directions.md`, rewritten without D1/D2/D3/D4 or reviewer-process labels |
| Suggested reading order | the 4–8 most useful load-bearing sources in reading order |
| Reasoning checks | only include foldable derivations or procedural inference chains when they make the note clearer; omit empty "no derivations" boilerplate |

**Citation translation.** `[S#]` (squid, resolving to `sources.md`) becomes the wiki form at every point of use: an inline `[[source-slug]]` source-page wikilink **and** a `[(PDF)](<sources/S#--slug.pdf>)` link to the run's local copy. Derive the slug to match the wiki's source-page convention — **title-first, kebab-cased short title, optionally suffixed `-<first-author-surname>-<year>` for disambiguation** (e.g. `S1` → `[[neural-simulated-annealing-correia-2023]]`; a distinctive title may stand alone). **If a source's first author, year, or title is missing from `sources.md`, read its local PDF (the `Local:` path) to recover the real provenance before emitting the slug** — emit a clearly-flagged placeholder only when the PDF is also unavailable, and flag it in the entry's **Caution** and the sidecar. Never invent an author. **Tier-B sources keep an explicit caveat at the point of use** (preserving squid's gate; the synthesis's `[S#, B]` mark carries over as a caveat clause). **Tier map:** squid Tier A → wiki Tier A; squid Tier B → wiki Tier B; a context-only accepted source → wiki Tier C.

**`status` auto-map.** A run that reached **Gate #2 "accept"** (the `log.md` shows an accept/handoff — handoff follows an accept) → `status: concluded`; otherwise → `status: active`. The human overrides at the gate.

Then thread the depth rules: the `{STYLE_DOC}` **Quality rubric** still binds (show-don't-name, derive-don't-assert, grounded claims, functional clickable output) even though the synthesis lint does not. Writing-quality memory: `{WRITING_MEMORY}` (if present — accrued workspace prose/depth/format lessons; read it after the register; it sharpens how you write and never overrides the Quality rubric).

---

## Step 3 — Review and improve (the two-lens loop)

Before the human sees it, improve the draft through a two-lens review. Launch BOTH lenses in parallel — one message, two `Agent(subagent_type="general-purpose", …)` calls — each given the draft path, the run's `sources/` and `synthesis.md` for fact-checking, and its brief. The lenses **return findings; they do not edit the file**. This mirrors `/research-tutorial` Step 5.

- **Wiki-editor lens** — prompt: "You are the editor of a personal research wiki. Read `<draft path>` as a thread about to be filed. Check that the note is reader-facing: frontmatter is present; the `> **What this note is.**` opener declares the reader and practical scope; the body is organized for reading rather than for audit; claims are cited with `[[source-slug]]` wikilinks plus local `[(PDF)]`/snapshot links; caveats are visible at the point of use; tables and foldable reasoning checks are included only where they improve readability; and the note contains a compact source map, known gaps, and suggested reading order. Treat process chatter as a problem: review-cycle details, gate summaries, blocker counts, source-rejection process, A-code labels, and in-thread `## Log` sections belong in `log.md`, `sources.md`, `reviews.md`, or `thread--wireup.md`, not in `thread.md`. Tag a **Blocker** on missing frontmatter, a missing What-this-note-is declaration, a bare `[S#]` citation, absent local source links, or process sections that make the note read like an audit report. Tag a **Nit** for sharpening. Do not flag length by itself; flag only sections that are too thin, repetitive, or chatty. Return a findings list; do not edit the file."
- **Source-fidelity lens** — prompt: "You are a fact-checker guarding against drift. Read `<draft path>` against the run's `synthesis.md` and `sources.md` (and `sources/` for the full texts). The thread must re-project the run with **no drift**: every claim traces to `synthesis.md` or `sources.md`; **no new un-grounded claim** is introduced (the thread runs no search and adds no literature); the tiers are preserved (a Tier-B source still carries its caveat); each `[S#] → [[source-slug]]` translation resolves to the **right** source; the `[(PDF)]` or snapshot path matches the run's local file; and any constructed reasoning check traces to the synthesis's claims without introducing a new result. The author's synthesis may be integrated into readable prose instead of exposed as internal A-code labels, but it must remain distinguishable from what the sources directly state. Tag a **Blocker** on any drift: an un-grounded claim, a mis-resolved citation, a dropped Tier-B caveat, or a synthesis claim presented as if it were directly stated by the literature. Quote the exact location and the source it should trace to. Return a findings list; do not edit the file."

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

A `full` thread is complete but reader-facing. The frontmatter carries the wiki's thread fields; the body should read like a useful note, not an audit trail. `depth: quick` may omit the table of contents and foldable reasoning checks, but both `quick` and `full` keep process details out of `thread.md`.

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

> **What this note is.** A practical note for {the intended reader, from plan.md Constraints}. It turns the run's local, gated sources into a readable synthesis. Established guidance is cited; synthesis beyond the sources is signposted in ordinary prose. Professional advice topics are routed to local verification rather than answered universally.

## Contents                        <!-- full depth: Obsidian [[#Heading]] links for navigation; quick may omit -->
{Link the major `##` sections and useful `###` sub-sections. Each anchor's text must match its heading exactly.}

## Scope
{in / out / adjacent, from plan.md.}

## Summary
{3–7 bullet claims, from the synthesis "answer so far" + top themes.}

## Core model / Findings
{The established results argued at depth, rewritten as a readable guide or note. Preserve useful tables and foldable reasoning checks. Translate citations to [[source-slug]] plus local [(PDF)]/snapshot links at each point of use; keep Tier-B caveats at the point of use.}

### Synthesis beyond the sources
{Include only when useful. Integrate the synthesizer's Analysis items as readable "main synthesis" or "interpretation" prose. Do not expose internal A-code labels, status scaffolding, or derivation bookkeeping unless the reader benefits from it.}

## Source map
{A compact table mapping claim areas to load-bearing sources and local copies. Full provenance, source rejection details, and review-cycle details stay in `sources.md`, `reviews.md`, and `log.md`.}

| Use | Sources |
|---|---|
| {claim area} | [[source-slug]] [(PDF)](<sources/S#--slug.pdf>) |

## Known gaps
{What the accepted sources do not yet support. Phrase as practical limits, not as process commentary.}

## Suggested reading order
{The most useful path through the local sources.}

## Reasoning checks                         <!-- full depth only, and only when useful -->
{Folded derivations or procedural inference chains when they materially improve the note. Omit this section if there is no useful reasoning check; do not write "No derivations appear".}

> [!derivation]- D1 — {title}
>
> {the derivation, math as math, each content line `> `-prefixed.}
```

---

## Thread register (the style contract)

The thread is written in the **wiki house style**, captured here as a convention the plugin ships (it ships the *register*, never the wiki content). This register is **deliberately different from squid's synthesis prose** and is **explicitly exempt from `{STYLE_DOC}`'s synthesis lint** — its anti-bold and anti-em-dash density checks, and its first-person ban, do **not** apply to the thread genre. The depth rules in `{STYLE_DOC}`'s `## Quality rubric` still bind.

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
- **The two-lens review improves the note before the human sees it.** A wiki-editor lens checks reader-facing genre fidelity, citation readability, compact source mapping, and absence of process chatter; a source-fidelity lens checks no drift (every claim traces to the run, tiers preserved, citations resolve, and synthesis is distinguishable from direct source claims). Genre Blockers and drift Blockers are equal; the loop caps at 2 cycles; the human gate is final.
- **Human-gated save.** Like `/research-tutorial`, nothing is written without explicit approval, and a re-run shows a diff before overwriting.
- **Depth is the user's steer.** `full` is the complete reader-facing genre; `quick` is a lighter thread. Both use a compact source map and keep run/process details in the log and sidecar.
