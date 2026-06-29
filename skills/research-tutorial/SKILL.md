---
name: research-tutorial
description: Build a ground-up, handbook-grade primer on a concept the reader is less familiar with — navigable (TOC), motivated, with typeset math and foldable proofs and a grounded comparison to competing methods — grounded in a /research run's gated library (or a fresh credibility-gated primer fetch), drafted, then improved through a two-lens readability review (a graduate student new to the concept, an expert in a related field) before a human-gated save. Full-depth primers also ship a companion methods-map placing the concept among its competitors. Use when a synthesis assumes familiarity with a term the reader wants explained, or the user says "/research-tutorial", "explain X", "make me a primer on X". Companion to /research; primers live under tutorials/ next to the run.
disable-model-invocation: true
argument-hint: <concept> [from-run <run-slug>] [quick|full]
---

# Research Tutorial — build a ground-up primer

Build ONE **primer**: a ground-up, handbook-grade explanation of a concept the reader is less familiar with, written FOR a specific reader and grounded in credible sources. A primer grounds *the reader* in a concept the way `/research` grounds *claims* in sources — it is the missing on-ramp when a synthesis assumes a term the reader wanted explained. A full-depth primer is modeled on the user's `GRPO_empirical` handbook: navigable (a table of contents), motivated (why the method exists), formal (typeset math, the central result derived, heavy proofs folded), and comparative (a grounded comparison to competing methods, plus a companion methods-map). Length is matched to the concept's depth; digestibility comes from navigability and folding, not from cutting depth. Textbook basics are written plainly; non-obvious or contested claims — including every comparison/when-preferred claim — cite `[S#]` from a gated library, so nothing un-vetted becomes load-bearing.

You are the **orchestrator** — a manager, not a writer-of-record. You gather grounding, draft the primer, improve it through a two-lens readability review, and save it only after the human approves. The two review lenses do the critique; you revise from their findings.

`$ARGUMENTS` carries the concept (required), an optional `from-run <run-slug>`, and an optional depth `quick|full` (default `full`). If the concept is empty, ask the human what to explain before proceeding. The skill **never spends search budget or saves anything without the human** — the fetch is human-confirmed when the run corpus could cover the basics, and the save is human-gated with a diff on re-run.

---

## Step 1 — Resolve paths, parse the request

**Resolve the canonical docs.** Same base-directory trick as `/research-profile` Step 1: the harness states `Base directory for this skill: <path>` (it ends in `…/skills/research-tutorial`). The plugin root is **two directories up** from that base. Set `RESEARCH_DOC = <plugin-root>/docs/RESEARCH_PROCESS.md` and `STYLE_DOC = <plugin-root>/docs/WRITING_STYLE.md`, verifying each with `ls`. If the consuming project has its own `docs/RESEARCH_PROCESS.md` or `docs/WRITING_STYLE.md` (relative to cwd), prefer the project copy. `{STYLE_DOC}` governs the primer's prose at the drafting step; pass `{RESEARCH_DOC}` into any scout launch. **Also resolve `WRITING_MEMORY = <cwd>/research-profiles/writing-quality--memory.md`** with the same project-local check (a sibling of `research/`, not inside it) — set it only if the file is present; it carries accrued workspace prose/depth/format lessons, threaded only into the draft step (Step 4) and the expert lens (Step 5) when present, and never threaded when absent (strictly additive).

**Parse `$ARGUMENTS`.**

- The **concept** (required) — the term to explain. If empty, ask the human in one line.
- Optional **from-run `<run-slug>`** — ground the primer in an existing `/research` run's corpus.
- Optional **depth `quick|full`** — `full` (default) is the handbook grade (TOC, Motivation, Notation when math-heavy, worked example, the required Comparison, plus the companion methods-map); `quick` is a lighter primer (no TOC, Notation, or worked example, but a short grounded Comparison).

**Canonical slug + aliases.** Derive `{concept-slug}` by the canonical rule the tutorial always applies: lowercase, hyphenated, and expand or record common acronyms (e.g. `MCMC` → `markov-chain-monte-carlo`, `CMA-ES` → `cma-es`). This slug is deterministic, so a sibling primer's `[[<concept-slug>]]` link resolves regardless of how the neighbor was named. Carry every variant into the primer frontmatter's `aliases:` (e.g. both `mcmc` and `markov-chain-monte-carlo`) so a wikilink written with either spelling lands.

**Resolve the output path(s):**

- **from-run** ⇒ primer at `research/<run-slug>/tutorials/<concept-slug>.md`; on `full` depth a companion methods-map at `research/<run-slug>/tutorials/<concept-slug>--methods-map.md`.
- **standalone** ⇒ primer at `./tutorials/<concept-slug>.md`; on `full` depth a companion methods-map at `./tutorials/<concept-slug>--methods-map.md`.

```bash
mkdir -p "$(dirname "<output-path>")"
```

---

## Step 2 — Set the two review lenses' parameters

The primer is written FOR a specific reader and reviewed by two contextual lenses, so resolve their parameters up front — before drafting, so the draft already aims at the reader.

- **Reader's background field** — the field the reader is solid in but from which this concept is foreign. **From-run:** read `research/<run-slug>/plan.md`'s **Constraints (for feasibility review)** field (the expertise it states) and derive it (e.g. a run whose plan says strong in deep-learning/LLMs with metaheuristics foreign ⇒ reader field = "ML/LLM engineering"). **Standalone:** ask the human in one line, or infer and confirm.
- **Related field(s)** — one or two fields adjacent to the concept's home domain whose expert would both catch oversimplifications and supply a bridging analogy (for simulated annealing: statistical physics for the annealing metaphor, optimization/OR for the algorithm family). Infer from the concept and confirm in one line; the human may name them. Default one related field; allow up to two ("expert(s)").
- **Optional profile attach.** If `research-profiles/` holds a dossier matching a related field (e.g. `domain-expert--optimization….md`), offer in one line to attach it to that expert lens — the same profiles hook the panel uses (read after the brief, sharpen the lens, never override it). Optional and additive; never required.

---

## Step 3 — Gather grounding (credibility-gated throughout)

Two material sources, both behind the credibility gate:

- **Run corpus (from-run, or invoked inside a run).** Read `research/<run-slug>/sources.md` and `ls research/<run-slug>/sources/`; select the entries that actually treat the concept — not the whole corpus, just the concept-relevant subset. The gate is **inherited** from the run (those sources already passed Tier A/B/Reject); no re-gating.
- **Primer fetch (as needed).** A run's corpus usually assumes familiarity (a run may even scope its primer out), so when the basics aren't covered, launch ONE `squid:literature-scout` with a tiny targeted plan inlined in the prompt to fetch one or two canonical introductory treatments (a survey, a textbook chapter, respected lecture notes) of the concept. Same launch shape as `/research-profile` Step 2, same Tier A/B/Reject gate (err toward Reject), scratch under `.build/<concept-slug>/` (**outside** `research/`). **Ask the human before spending this search budget** unless the run corpus clearly lacks the basics. **Standalone with no run:** this fetch is the only grounding.
- **Ground the compared methods too.** The required Comparison section and the full-depth methods-map make claims about the concept's competitive/related methods, so those claims need grounding as well — a when-preferred claim cites `[S#]`, and an ungrounded comparison is not allowed. Two ways to get it, in order of preference: (1) **draw from the run** — where `research/<run-slug>/synthesis.md` and `sources.md` already compare the concept to its neighbors, cite those gated `[S#]`; (2) **extend the fetch** — have the same scout-fetch step also pull credibility-gated intros to the named competitive/related methods (for simulated annealing: MCMC, Gaussian-process Bayesian optimization, evolution strategies) so the comparison rests on Tier A/B, not on the model's prior. Name the competitors in the inlined plan's Question(s) so the scout fetches them in the same pass.

```
Agent(
  subagent_type="squid:literature-scout",
  prompt="""Credibility-gated grounding for a concept primer. Read {RESEARCH_DOC} (canonical research lifecycle) and the project's AGENTS.md (or CLAUDE.md, if present) first. Follow your role definition — your headline duty is the source-credibility gate.

  This is NOT a full /research run — there is no plan.md. Treat this inlined plan as your contract:
    Mode: targeted
    Question(s): a clear, ground-up introduction to {concept} — what it is, the core intuition, how it works, and where it helps versus its alternatives — at a level a newcomer can follow; PLUS credibility-gated introductions to its named competitive/related methods {list them, e.g. for simulated annealing: MCMC, Gaussian-process Bayesian optimization, evolution strategies} so a grounded when-each-is-preferred comparison can be written.
    Source strategy: a canonical survey, a textbook chapter, or respected lecture notes; peer-reviewed venues and well-known-lab/established-author treatments. One or two strong introductory sources beat many. Include at least one source per named competitor that supports a when-preferred comparison.

  Working area: .build/{concept-slug}/  (this lives OUTSIDE the git-ignored research/ folder — write your scratch and sources.md-style output HERE, not under research/). mkdir -p it. Your local library goes in .build/{concept-slug}/sources/ (same fetch rules as a /research run).

  Run the search-as-code filtering pass, apply the Tier A/B/Reject gate (err toward Reject), fetch every accepted source into .build/{concept-slug}/sources/ (Local: field per accepted entry), and write .build/{concept-slug}/sources.md in your required shape — every Accepted source carries a Tier AND a one-line provenance line; every Reject is listed with a reason.

  Hand back: Tier-A / Tier-B counts, the local-library tally, and the path to sources.md."""
)
```

On return, **verify before drafting:** the gated set (run subset and/or `.build/{concept-slug}/sources.md`) exists and every Accepted source carries a Tier + provenance line. If credible coverage of the basics is thin, say so to the human and ask whether to proceed on a thinner base or refine the request.

---

## Step 4 — Draft the primer

Draft into the handbook-grade template below, per `{STYLE_DOC}` (tutorial register — the template-required headings and the Key-terms definitional list are exempt). A full-depth primer is length-matched to the concept and navigable: a doc-level BLUF opening, a **Table of contents** (`- [[#Section]]` Obsidian wikilinks), a **Motivation** section, a **Notation** table when math-heavy, and a required **Comparison with alternatives** section (a table plus a grounded when-each-is-preferred discussion). Write per the technical register: typeset the math (inline `$\ldots$`, display `$$\ldots$$`), derive the central result rather than narrating it, and fold the heavy derivation into a `> [!derivation]-` callout so the linear read stays light. Per the Quality rubric, **How it works** shows its load-bearing mechanism components concretely (show-don't-name — how the next state is actually produced across 2–3 representative settings, with the formal conditions), and the **worked example** is terse stepped (`Step N`) plus an inline visual (Mermaid / ASCII / values table) plus a foldable runnable snippet when the process is dynamic. Writing-quality memory: `{WRITING_MEMORY}` (if present — accrued workspace prose/depth/format lessons; read it after the style contract; it sharpens how you write, and never overrides the canonical contract or the Quality rubric). **Sourcing rule:** textbook fundamentals are written as clearly-labeled plain explanation; any non-obvious or contested claim — when the concept beats or loses to alternatives, its failure modes, performance, and every comparison/when-preferred claim — cites `[S#]` from the gated sources; nothing un-gated becomes load-bearing; the provenance note states what is explanation versus sourced.

On **full** depth, ALSO draft the companion **methods-map** (`<concept-slug>--methods-map.md`, the shape in "The companion methods-map" below): the lineage, the full comparison table, the when-to-use-which decision guide, and open problems. The primer's Comparison is the quick reference; the methods-map is the full landscape.

Run the `{STYLE_DOC}` lint on both the primer and the methods-map (tutorial exemptions apply) and record the counts in the log.

---

## Step 5 — Review and improve (the readability loop)

Before the human sees it, improve the draft through a two-lens review. Launch BOTH lenses in parallel — one message, two `Agent(subagent_type="general-purpose", …)` calls — each given the draft path, the gated `sources/` for fact-checking, and its brief. The lenses return findings; they do **not** edit the file.

- **Learner lens** — prompt: "You are a graduate student with a solid working background in {reader-field} who has NOT studied {concept}. Read `<draft path>` as your first real exposure. Find every place a reader like you stalls, in order: does the one-sentence answer land before any jargon; does the **Motivation** make you understand why the method exists before the mechanism arrives; does the intuition give a mental model you can hold; is every key term defined at or before first use; can you walk the worked example yourself with no skipped step; does each section open with its point; does the **Table of contents** and the section structure actually help you navigate, and can you follow the motivation → mechanism → comparison arc end to end; is the prose around the math followable and are heavy derivations folded into `> [!derivation]-` callouts rather than exploding the read and burying the thread. Tag a **Blocker** where a reader with your background genuinely cannot follow (an undefined load-bearing term, a skipped derivation step, an example that assumes its conclusion); tag a **Nit** for a sharpening, including a wall of unfolded math that buries the intuition or a missing/disordered TOC that makes a long primer hard to navigate. Quote the exact sentence where you stalled. You check followability, NOT correctness — that is the expert's job. Score the draft against the Quality rubric in {STYLE_DOC}; specifically, the **worked example** must be terse stepped (`Step N`) you can follow with no skipped step AND carry a **visual** (a Mermaid diagram, an ASCII sketch, or a trajectory/values table) — a prose-wall example with no stepped form or no visual is a **Blocker** (you cannot follow it), and where the process is dynamic a foldable runnable snippet should be there (a **Nit** if missing); and every link must actually jump — the TOC `[[#…]]` entries and the Go-deeper / source links are clickable markdown links (a bare, non-clickable reference is a **Nit**; the lint also catches it). Return a findings list; do not edit the file."
- **Related-field-expert lens** (launch one per related field, 1–2 total) — prompt: "You are an expert in {related-field}, adjacent to {concept}'s home domain; you know the rigorous version. Your jobs: (1) catch where simplification has crossed into wrong or misleading — a **Blocker**; (2) improve readability by bridging to ideas a reader who knows {related-field} already holds — a **Nit**, or a **Blocker** if a current analogy actively misleads; (3) check the load-bearing formalism is present and correct — the defining equation(s) given as math and the central result's derivation shown; a primer on a mathematical method that omits its key equation or central derivation, or hand-waves it in prose, is **technically incomplete — a Blocker**; (4) check the **Motivation** is real — it genuinely explains why the method exists, why the naive approach fails, and where it came from, not a throwaway line; (5) check the **Comparison with alternatives** is grounded and substantive — the comparison table is present, every when-preferred claim cites a gated `[S#]`, and — at `full` depth — the when-each-is-preferred discussion is more than a one-liner per alternative (a `quick` primer's one-line-per-alternative comparison satisfies this; scale the substance check to the declared depth, but the grounded comparison itself is required at both depths). **A primer that teaches the concept in isolation, with no grounded comparison to its competitors, is incomplete — a Blocker.** Check each stated mechanism/term/claim for correctness (consult the gated `sources/` where one is cited), whether the framing is standard or idiosyncratic, what single analogy to {related-field} would make the core idea click, and whether anything load-bearing for a correct first understanding is omitted. Quote specifics. Also score against the Quality rubric in {STYLE_DOC}; specifically **show, don't name**: a load-bearing mechanism component named but not shown concretely (how it is actually instantiated across 2–3 representative settings, with its formal conditions — e.g. a proposal/transition step explained only by name) is a **Blocker**, the same bar as omitting the central derivation. Writing-quality memory: {WRITING_MEMORY} (if present — accrued workspace prose/depth/format lessons; read it after the style contract; it sharpens what you enforce, and never overrides the canonical contract or the Quality rubric). Accuracy Blockers outrank readability Nits. Return a findings list; do not edit the file."

**Severity.** A **Blocker** = a target-background reader cannot follow a load-bearing passage, or a taught statement is incorrect or misleading. A **Nit** = a sharpening or a better bridge.

Revise the draft to resolve every Blocker (and the cheap Nits), then re-run BOTH lenses once. **Cap: 2 cycles.** Anything unresolved after cycle 2 is surfaced to the human at Step 6, flagged. Append a `[research-tutorial]` review entry to the run's `log.md` (from-run) noting the lenses, the cycle count, and the Blocker counts.

---

## Step 6 — Human review, then save

Mirror `/research-profile` Step 4/5: present the improved draft(s) plus a one-paragraph review summary (the lenses used, what changed, any unresolved flag), then **persist nothing without explicit approval.** On `full` depth, present the primer and its companion methods-map together; the single approval covers both.

- **New primer** → show the full draft (and, on full depth, the methods-map); ask `save / edit / cancel`.
- **Re-run for an existing primer** → read the current file(s), show a **diff** of each draft against it, and ask before overwriting. Never silently overwrite a primer (or methods-map) the human already reviewed.

On `save`, write to the output path(s) and set `updated:` to today — on full depth this writes both the primer and the `<concept-slug>--methods-map.md` companion. For **standalone**, optionally copy any fetched primer's local files into a persistent spot (`./tutorials/works/` — optional); for **from-run**, the run's `sources/` already holds them. Clean up the scratch:

```bash
rm -rf .build/{concept-slug}/
```

**Writing-quality memory capture (optional, human-gated).** If the human's review gave prose/depth/format feedback (edit instructions, "still too thin" / "too text-heavy"), offer to capture **1–3 writing-quality lessons** to `research-profiles/writing-quality--memory.md` — append-only, create with the `kind: writing-quality-memory` frontmatter if absent (sibling of `research/`, not inside it). Skip silently if the human declines or no `research-profiles/` dir exists; mirror the same human-gated save discipline as the primer.

When built **from a run**, drop a one-line pointer into `research/<run-slug>/synthesis.md`: a blockquote `> Primer: new to {concept}? see tutorials/<concept-slug>.md` (on full depth, add `; methods map at tutorials/<concept-slug>--methods-map.md`) inserted right after the `## The answer so far` section. Show the human exactly what was written and where.

**Cross-link into the primer web (full depth only — methods-maps maintain it).** After writing the new primer + methods-map, wire it into its siblings' methods-maps so neighbor primers form a **maintained** cross-linked web rather than hand-wired wikilinks:

1. **Scan the sibling `tutorials/` dir** — `research/<run-slug>/tutorials/` (from-run) or `./tutorials/` (standalone) — for existing primers and `*--methods-map.md` files. **Scope guard:** only this one `tutorials/` dir; never reach across into an unrelated run's tutorials.
2. **The new methods-map links its neighbors.** For every neighbor that already has a primer in this dir, write `[[<neighbor-slug>]]` in the new methods-map's comparison-table method-name cells and its `## See also` (a plain name + alias otherwise, going live when that primer is built later).
3. **Repair the back-links bidirectionally.** For each **existing** methods-map that names the new concept (in its comparison or lineage), **add or repair the `[[<new-slug>]]` link back** to the new primer — so the edge is bidirectional.
4. **Human-gated diff.** Show the human every edit to an existing file before writing it — mirror the "show the human exactly what was written" discipline above for the synthesis pointer. **Never silently rewrite a primer or methods-map the human already reviewed.**

The primer's own **Comparison with alternatives** table stays focused on teaching the one concept — **no sibling `[[ ]]` links there**; the maintained web lives on the methods-maps only.

---

## Tutorial template (the save shape)

A full-depth primer is **handbook-grade**, modeled on the user's `GRPO_empirical` guide: navigable (a table of contents), motivated (why the method exists), formal (typeset math, the central result derived, heavy proofs folded), and comparative (a table plus a grounded when-each-is-preferred discussion). Length is matched to the concept's depth — digestibility comes from the TOC and the folds, not from cutting depth. The sections, in order:

```markdown
---
title: {Concept} — a primer
aliases:
  - {concept}
  - {a common alias}
tags:
  - {topic-tag}
  - primer
concept: {the concept}
domain: {its home domain}
grounded-in: {N gated sources}{; from run <run-slug>}{; + M fetched primers}
depth: full | quick
updated: YYYY-MM-DD
---

# {Concept} — a primer

{Opening — 2-4 sentences: what this primer covers and the central takeaway (doc-level BLUF). Full depth, when built from a run: a line linking the companion [[<concept-slug>--methods-map]] and ../synthesis.md.}

## Table of contents                       <!-- full depth: list of [[#Section name]] Obsidian wikilinks; lint-exempt; quick omits -->
- [[#Motivation]]
- [[#The idea in one sentence]]
- [[#How it works]]
- [[#Comparison with alternatives]]

## Motivation
{The problem the method exists to solve; why the naive/obvious approach fails; the lineage — where it came from, what it grew out of. Well-motivated and grounded [S#]; not a throwaway line.}

## Notation                                 <!-- math-heavy concepts: define each symbol once; lint-exempt table; quick omits -->
| Symbol | Meaning |
|---|---|
| {symbol} | {meaning, used consistently throughout} |

## The idea in one sentence
{plain-language what it is, before any jargon (BLUF)}

## Intuition
{the metaphor, the problem-shaped mental model the reader can hold}

## How it works
{plain steps; the key mechanism with its defining equation(s) as display math $$\ldots$$; the central result derived — show it, don't narrate it — inline or folded in a > [!derivation]- callout when long. Per the Quality rubric's **show, don't name**: a load-bearing mechanism component (a proposal / transition / update step) is shown concretely — how the next state or value is actually produced across 2–3 representative settings, with its formal conditions — not merely named. (A proposal step shown as bit-flip / 2-opt swap / Gaussian perturbation, with the symmetry condition and the correction when it fails, and the named family it instances.)}

## A worked example
{Per the Quality rubric's **worked examples are stepped, visual, and runnable**: terse stepped — `Step 1`, `Step 2`, … — equation-forward with minimal prose, each step running the typeset formula (e.g. $\exp(-2/2)=e^{-1}\approx0.37$); an inline visual that fits the process — a Mermaid diagram, an ASCII sketch (e.g. an energy landscape), or a compact trajectory/values table; and, when the process is dynamic, a foldable runnable snippet (a > [!example]- callout wrapping a fenced code block) the reader can run to watch it. True animation isn't embeddable in static markdown — the runnable snippet is how motion is delivered.}        <!-- full depth; quick omits -->

## Comparison with alternatives
{A comparison table of the concept vs its competitive/related methods across shared dimensions, then a grounded discussion of when the concept is preferred over each. Every when-preferred claim cites [S#]; an ungrounded comparison is not allowed. Link the companion methods-map for the full landscape.}

| Method | Axis of contrast | Cost | When preferred | Source |
|---|---|---|---|---|
| {this concept} | {…} | {…} | {…} | [S#] |
| {alternative} | {…} | {…} | {…} | [S#] |

For the full landscape, see [[<concept-slug>--methods-map]].

## When to use it
{The preferred-over-alternatives summary: the specific regime where this concept wins, grounded [S#].}

## Key terms
- {term}: {one-line definition, which may include the term's formal/math form}            <!-- a real definitional list — the one place colon-form belongs -->

## Why it came up here
{one paragraph tying back to the run's question}   <!-- only when built from a run -->

## Go deeper
- {source} — Tier A|B — {Local: link if available} — {what it adds}

> Provenance: textbook basics are explained directly; comparison, performance, and fit claims cite [S#] from the gated library. Math is typeset ($\ldots$ / $$\ldots$$) and heavy derivations fold into > [!derivation]- callouts. {note any model-explanation not from a cited source.}
```

`depth: quick` produces a lighter primer: skip the **Table of contents**, the **Notation** table, and the **worked example**, but keep a short **Comparison with alternatives** (the table plus a one-line when-preferred per alternative). `depth: full` (default) is the handbook grade above, with every section, and also emits the companion methods-map (next section).

## The companion methods-map (full depth only)

On `full` depth, ALSO write a companion **methods-map** next to the primer — `research/<run-slug>/tutorials/<concept-slug>--methods-map.md` (from-run) or `./tutorials/<concept-slug>--methods-map.md` (standalone). It is modeled on `GRPO_empirical`'s `Methods map.md`: where the primer's Comparison section is the quick reference, the methods-map is the full landscape that places the concept among its family and competitors, so a choice between methods reads as a point on a known axis rather than a one-off. It is grounded the same way — the lineage and the comparison cite the gated `[S#]`, and the cross-method claims draw on the run's `synthesis.md`/`sources.md` where those already compare the methods.

Write it in this shape:

```markdown
---
title: {Concept} — methods map
tags:
  - {topic-tag}
  - moc
updated: YYYY-MM-DD
---

# {Concept} — methods map

{Opening — places {concept} among its family/competitors so a choice between them reads as a point on a known axis. Links the primer ([[<concept-slug>]]), ../synthesis.md, and ../sources.md.}

## The lineage
{The progression / family tree leading to and around the concept — what it grew out of, what sits next to it, what refined it. Grounded [S#].}

## The comparison
| Method | Mechanism | Cost | When preferred | Source |
|---|---|---|---|---|
| {this concept} | {…} | {…} | {…} | [S#] |
| [[<competitor-slug>]] | {…} | {…} | {…} | [S#] |    <!-- a sibling with a primer is a [[<neighbor-slug>]] wikilink; a neighbor with no primer yet is a plain name + alias, going live when its primer is built -->

## When to use which
{A decision guide with in-depth tradeoffs — the regime each method wins in, and the axis that decides between them. Grounded [S#].}

## Open problems / limitations
{Known weaknesses of the concept and open questions in the family — what none of these methods solves yet. Grounded where a source states it.}

## See also
- [[<concept-slug>]] — the primer (intuition, mechanism, worked example).
- [[<neighbor-slug>]] — a sibling primer in this tutorials/ dir, when one exists (maintained bidirectionally on each new build).
- ../synthesis.md — the run's synthesis this map draws on.
- ../sources.md — the gated sources.
```

For simulated annealing, the comparison and lineage cover the concept against MCMC, Gaussian-process Bayesian optimization, evolution strategies, and gradient methods — the same neighbors the primer's Comparison names, expanded to the full landscape with the when-each-is-preferred tradeoffs. Each neighbor that has its own primer in this `tutorials/` dir is a `[[<neighbor-slug>]]` wikilink in the comparison table and `## See also` (and that neighbor's methods-map links back to `[[simulated-annealing]]`); a neighbor without a primer yet stays a plain name until one is built.

---

## Notes on shape

- **Strictly additive.** A primer is opt-in. `/research` works exactly as before when one is never built; this skill only ever *creates* a primer next to a run (or standalone).
- **Handbook-grade, length-matched.** A full-depth primer is modeled on the user's `GRPO_empirical` guide: a TOC, a Motivation section, a Notation table for math-heavy concepts, typeset math with foldable proofs, a worked example (stepped `Step N` + an inline visual + a foldable runnable snippet when dynamic, per the Quality rubric), and a required Comparison-with-alternatives section. Length is matched to the concept's depth; digestibility comes from the TOC and the folds, not from cutting depth.
- **A full-depth primer ships a companion methods-map.** `<concept-slug>--methods-map.md` next to the primer places the concept among its competitors (lineage, comparison table, when-to-use-which, open problems). The primer's Comparison is the quick reference; the methods-map is the full landscape.
- **Neighbor primers form a maintained web.** Their methods-maps cross-link bidirectionally — the new methods-map links siblings that already have primers, and each existing methods-map that names the new concept is repaired to link back — and the repair runs (human-gated diff) on every new full-depth build, scoped to one `tutorials/` dir. Canonical slugs + frontmatter `aliases:` keep the `[[ ]]` links resolving. Links-only: the cross-links live on the methods-maps (the primer's own Comparison table stays focused on its one concept), and there is no separate map-of-content hub.
- **Human-gated save.** Like `/research-profile`, nothing is written without explicit approval, and a re-run shows a diff before overwriting; on full depth the one approval covers the primer and its methods-map.
- **Basics labeled, non-obvious cited — including the comparison.** Textbook fundamentals are plain explanation; any non-obvious or contested claim rests on a gated `[S#]`; every comparison/when-preferred claim is grounded (drawn from the run's synthesis/sources or a scout fetch of the competitors), and an ungrounded comparison is not allowed.
- **Reuses the scout and the credibility gate.** The primer fetch is the same `squid:literature-scout` launch and the same Tier A/B/Reject gate as the rest of the pipeline — no bespoke search. `from-run` inherits the run's gate; the fetch also grounds the named competitors when the comparison needs them.
- **The two-lens review improves readability and depth before the human sees it, scored against the Quality rubric.** A graduate student new to the concept checks followability and navigation (the TOC, the motivation → mechanism → comparison arc, heavy math folded not exploding the read) and enforces the rubric's worked example — terse stepped (`Step N`) plus a visual (Mermaid / ASCII / values table), a runnable snippet when dynamic — and that the TOC and reference links are clickable; a related-field expert checks accuracy, supplies a bridging analogy, confirms the load-bearing formalism is present and correct, enforces the rubric's **show-don't-name** (a load-bearing mechanism component named but not shown concretely is a Blocker, the same bar as omitting the central derivation), and that the Motivation and the grounded Comparison are substantive — a primer taught in isolation, with no grounded comparison to its competitors, is a Blocker. Accuracy Blockers outrank readability Nits; the loop caps at 2 cycles and the human gate is still final.
- **Depth is the user's steer.** `full` is the handbook grade (every section + the companion methods-map); `quick` is a lighter primer (no TOC, Notation, or worked example, but a short grounded Comparison).
