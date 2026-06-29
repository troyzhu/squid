# Research Process

This document defines the agent-team workflow for the **research pipeline**. It is the **single source of truth** for that pipeline. Every research agent (research-lead, literature-scout, synthesizer, strategist, research-reviewer) reads this file before acting, and the `/research` skill drives the loop described here.

It is the research-pipeline analog of the engineering pipeline (the `/plan` → `/implement-night` skills, described in `AGENTS.md`). Research decides *what* to build; the engineering team builds it. The two layers chain optionally at Gate #2 via the `/plan` handoff.

## Lifecycle

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
synthesizer  → synthesis.md  (reader-facing answer + Analysis (OURS A#) + gaps & follow-up queries)
        │
        ▼
depth critic (research-reviewer ROLE: depth) scores synthesis vs the Quality rubric
   → synthesizer deepens  (Max 2 cycles, capped, human-gated downstream)
        │
        ▼
[ synthesis checkpoint — present answer-so-far, BLOCK for human steer ]  (opt-in; plan.md gated, default off)
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
        └── handoff → promote a direction to a feature spec for /plan
```

The pipeline blocks on the human exactly twice by design: once after the research-lead produces the Research Plan (approve the plan), and once at the end (review the directions memo). Between the two gates the pipeline moves forward on its own — it does not silently skip, and it does not wait for additional input. The optional synthesis checkpoint (above) is default-off and fires only when the human opted in at Gate #1; it is human-controlled and is **not** a third mandatory gate — with it off, behavior is identical to a two-gate run.

**Interrupted runs resume from the run folder.** All run state lives in `research/<slug>/`: the artifacts mark which steps completed, and `log.md` carries the gate decisions (the orchestrator's `[orchestrator]` entries). Re-invoking `/research <slug>` re-enters the run rather than restarting it — the orchestrator reads the log and artifacts, reports the detected state and the proposed re-entry step, and confirms with the human before continuing. Passed gates are never re-asked when the log shows them.

**Refreshing a stale run.** A run that is *complete* but predates current pipeline upgrades (its library has `Local: none` sources, its synthesis never ran the depth-critic loop, or it is v1-shape) can be upgraded by `resume` **in place — nothing is archived**. The orchestrator detects the stale signals and offers a pick-any-subset menu: **backfill the library** (the scout downloads the `Local: none` sources via the open-access ladder, in backfill mode — no re-search, no re-gate), **deepen the synthesis** (regenerate against the now-local corpus and re-run the depth loop, after backing up the old synthesis to `synthesis--pre-refresh-{YYYYMMDD-HHMM}.md`), and optionally **propagate** (re-run directions → panel → acceptance). It reuses Step 5/5.4 and the scout's download ladder, is human-chosen (no new auto-loop), and works for any old run — it is "bring this run up to the current pipeline's standard." A complete run with no stale signals resumes to Gate #2 unchanged.

## Agents

Five sub-agents plus the orchestrator (the top-level Claude Code session).

| Agent | File | Engineering analog | Role |
|---|---|---|---|
| Orchestrator | `AGENTS.md` + `skills/research/SKILL.md` | (implement-night orchestrator) | Drives the pipeline, enforces the two gates, verifies each report; never does the research itself. |
| research-lead | `agents/research-lead.md` | product-architect | Grooms the raw question into a Research Plan (questions, mode, scope, source strategy, success criteria); performs user-POV acceptance of the directions memo. Owns "does this answer the question." |
| literature-scout | `agents/literature-scout.md` | tester | Runs credibility-gated multi-source search (web + academic), fan-out → fetch → verify. **Headline duty: the source-credibility gate.** Produces `sources.md`. |
| synthesizer | `agents/synthesizer.md` | software-engineer | Reviews `sources.md` → `synthesis.md`, a reader-facing memo: a one-screen answer; themes argued at the material's depth; tensions; an **Analysis — beyond the sources** section (OURS, confidence-tagged A# items derived past the literature); implications; where-I-need-judgment; gaps & follow-up queries; an evidence-ledger appendix. Derives knowledge, not directions. After the draft, **revises against the depth critic** — deepening the synthesis to resolve every rubric Blocker (the synthesis depth loop). Also flags primer candidates in its hand-off (foundational concepts a newcomer would want grounding on), seeding the optional `/research-tutorial` offer at the checkpoint. |
| strategist | `agents/strategist.md` | software-engineer | Turns the synthesis into candidate directions (`directions.md`, each cited); after the panel, resolves every Blocker and re-emits the revised memo. |
| research-reviewer | `agents/research-reviewer.md` | pr-reviewer | The panel, as one **parameterized** agent. The five content roles launch in parallel on `directions.md` and write their sections of `reviews.md`. A sixth role, **`depth`**, scores an artifact against the Quality rubric (structure/depth/usability, not correctness) and returns located findings; it runs alone on the synthesis (the depth-critic step) and is not part of the five-role panel. Tags findings Blocker/Nit. |

## The Two Human Gates

| Gate | When | Human choice |
|---|---|---|
| **Gate #1 — approve the plan** | After research-lead grooms `plan.md` | `y` (approve) / `edit` (re-groom) / `cancel`. Confirms questions, scope, mode, and source strategy before any search runs. Any profile attachments are surfaced (with `updated:` dates) and adjustable here. |
| **Gate #2 — review the directions** | After research-lead acceptance | **accept** (done) / **loop back** (refine queries, re-run from search — human-decided) / **handoff** (promote a direction to a feature spec for `/plan`). Presented with the memo, a panel-findings summary, any unresolved Blockers, and the synthesizer's follow-up queries. |

**Opt-in synthesis checkpoint (NOT a gate).** When `plan.md` sets `Synthesis checkpoint: yes`, the pipeline pauses after the synthesizer to present the answer-so-far and the synthesizer's "where I need your judgment" prompts, so the human's feedback can shape the directions (continue / primer / feedback-revise / loop-back / cancel). The checkpoint also surfaces the synthesizer's flagged **primer candidates** and can build a grounded primer (`/research-tutorial`) on one before continuing — human-directed, the checkpoint re-presents after each build. It is **human-controlled and default-off** — it does not count toward the two mandatory gates, and with it off the run behaves exactly as a two-gate run.

## Source-Credibility Gate

The scout tags every source. This is the scout's own contract, independent of which search mechanism runs underneath.

The scout does not build a search engine — it reuses `deep-research` (fan-out → fetch → adversarial verify) and `huggingface-papers` (arXiv/HF academic lookup) as the engine, then applies the gate as reproducible **search-as-code**: a re-runnable script that dedupes (DOI / arXiv-id / normalized title), filters known content-farm/SEO domains, and computes per-question coverage (the Tier-A count behind each plan question, which drives the insufficient-sources check). The script and its output are the auditable trail.

| Tier | Meaning | Sources |
|---|---|---|
| **Tier A — load-bearing OK** | Strong provenance; safe to rest a claim on. | Peer-reviewed at a recognized venue; or a technical report/preprint from a well-known lab or an established researcher. |
| **Tier B — supporting, cite with caveat** | Credible but not yet vetted; only with an explicit caveat. | arXiv preprint (not yet peer-reviewed) from attributable, credible authors; a named-expert engineering blog at a respected org. |
| **Reject** | Provenance fails. | Anonymous, SEO/content-farm, marketing, predatory venue, or unverifiable provenance. |

Rules:

- Every accepted source carries a **one-line provenance justification**.
- **Load-bearing synthesis claims must rest on Tier A** (Tier B only with an explicit caveat).
- If the scout cannot find enough credible sources to support the plan's questions, it **surfaces that** rather than synthesizing on weak ground (the "no false confidence" rule).
- **When provenance is unclear, err toward Reject** — a missing source is safer than an uncredible one silently treated as load-bearing.
- **Rejected sources are listed with reasons** — the credibility filter is auditable.
- **The local library is local-first and offline-readable.** The scout downloads the full text of every accepted source into the run's library (`research/<slug>/sources/`) by default — seeking the open-access copy (arXiv / PMC / author / publisher-open) when the canonical link is paywalled — so synthesis, review, and the user read full texts offline, not just extracted claims. `Local: none` is the audited exception (a hard paywall with no open version; reason + routes-tried recorded), not a routine outcome; the orchestrator surfaces a high `none` rate rather than synthesizing on claims.

**Local corpus.** When the plan's source strategy names a **local corpus** (the user's existing papers — a folder, glob, or file list), the scout ingests it through this same gate instead of web-searching past it: each file is read, its bibliographic identity extracted, tiered by provenance (a hand-gathered PDF is **not** auto-Tier-A), deduped, and copied into the run's library. The default is **local-first** — a bounded gated web supplement fills only the questions the corpus under-covers; **local-only** forbids the supplement and surfaces those gaps via the insufficient-sources rule. The user's own notes / README / scratch are context, not citable Tier-A sources. This is how `/research` is brought to bear on material you already gathered.

## Reviewer Panel

Five roles, run in parallel. Each tags findings **Blocker / Nit** (reusing the engineering team's Severity Rule, adapted to research).

| Role | Reviews for |
|---|---|
| **Methodologist / skeptic** | Rigor: validity, statistics, reproducibility, confounds, overclaiming, evidence quality. Blocks when a direction rests on a misread of evidence or an unsupported leap. Also scrutinizes the synthesis's **Analysis** section: an A-item whose derivation doesn't follow from its cited `S#`/`A#`, or that smuggles in an un-grounded claim, is a Blocker (same bar as a load-bearing finding). |
| **Domain expert** | Prior art & correctness: does the synthesis read the literature right? Is a "novel" direction already published? Is seminal work missing? Blocks on factual misreadings or missing key work. |
| **Novelty & impact** | Is the direction genuinely new and worth pursuing? Delta over existing work; who benefits. Blocks when a direction is a known result repackaged, or impact is negligible. |
| **Feasibility / practitioner** | Executable with realistic data/compute/time (per `plan.md` constraints)? Blocks when an infeasible direction is presented as feasible. |
| **Clarity reviewer** (junior-staff lens) | Can a grad student / new hire follow *what was done and why*? Jargon explained, assumptions stated, evidence→direction chain legible; the Analysis derivations must be followable by a junior — an unfollowable derivation is a clarity Blocker. **Blocks on incomprehensibility, not on correctness** — purely a communication-quality gate. |

### Severity Rule (adapted)

| Severity | Definition |
|---|---|
| **Blocker** | A defect that makes the memo misleading, wrong, or unusable: an unsupported load-bearing claim, a misread cited source, a "novel" direction that is already published, an infeasible direction presented as feasible, (clarity) a section a junior literally cannot follow, or an Analysis item whose grounding doesn't hold. |
| **Nit** | Non-blocking improvement: phrasing, an extra citation worth adding, a minor caveat. |

The strategist must resolve **every Blocker**; the panel re-reviews once (**Max 2 cycles**). Unresolved Blockers after cycle 2 are surfaced to the human at Gate #2, flagged — never silently dropped.

## Profiles

Profiles are **optional, strictly additive** dossiers that sharpen a reviewer (or the lead) at launch. Each is a `role × domain × school-of-thought lens` — e.g. `methodologist--statistics--bayesian`: fluent in the rival camp, reviewing from Bayesian commitments. A dossier carries the lens's stance, signature questions, the failure modes it hunts, and credibility-gated key writings. With no profiles attached, the pipeline behaves exactly as a no-profile run.

- **Where they live.** `./research-profiles/` at the project root — a **sibling** of `research/`, NOT inside it. The anchored `/research/` ignore rule does **not** catch this directory, so profiles are intentionally **not git-ignored**: they are committable in a private runs repo (a reusable knowledge base of lenses), unlike the per-run `research/<slug>/` artifacts.
- **How they're built.** The `/research-profile` skill drives the literature-scout to pull the dossier's grounding material through the same Tier A/B/Reject credibility gate, drafts the dossier, and saves it under `research-profiles/` only after a human review (a re-run shows a diff before overwriting). It is the same human-gated discipline as `self-improve`. A dossier stores its key writings locally under `research-profiles/works/{dossier-slug}/` (copied, not referenced — profiles outlive runs), and its Key-writings cite those local copies. `/research-profile` also accepts a problem statement instead of an explicit triple and proposes a reviewed slate of 2–4 candidates, building only the ones the human selects (nothing is searched or saved without an explicit selection). A **from-run** form (`from-run <run-slug>`) builds a dossier from an existing run's already-gated corpus instead of searching anew — the gate is inherited from the run and the relevant works are copied out of the ephemeral run folder. The lead may surface `suggested (not yet built)` entries in the plan's Profiles field at Gate #1, where building them remains the human's call.
- **How they're used.** `/research` discovers dossiers in Step 0; the research-lead proposes per-role attachments in the plan's **Profiles** field (surfaced with `updated:` dates at Gate #1, where the human may adjust them); the panel reads an attached profile **after** the canonical doc. **A profile sharpens the lens — what a reviewer looks for — but never overrides** the reviewer's contract, the Severity Rule, or what counts as a Blocker. The same attachments are reused across both review cycles (a reviewer never changes lens mid-revision). At Gate #1, building any `suggested (not yet built)` profiles is a first-class choice (`b`) — build them, attach them, then re-present the gate; and after Gate #2, the end-of-run capture offers to seed a dossier from the run's gated corpus (`from-run`). Both are human-gated.
- **Lead memory profile.** `research-lead--memory.md` is a distinct profile shape — the lead's accumulated user preferences and per-run lessons. It is read (read-only) by the lead during grooming and acceptance, and **excluded** from the reviewer-dossier discovery list. After Gate #2 resolves, the orchestrator proposes 1–3 lesson lines and, **only on explicit human approval**, **appends** them to this file (the self-improve discipline). It is append-only and human-gated.
- **Writing-quality memory.** `research-profiles/writing-quality--memory.md` is a third, distinct file — accrued workspace-specific prose/depth/format lessons from human feedback across runs. It is read by the **prose writers** (the synthesizer and the `/research-tutorial` draft + expert lens) and the **depth critic**, sharpening how they write and what the critic enforces; it never overrides the canonical `WRITING_STYLE` contract or its Quality rubric, only adds workspace taste on top. Like the lead memory it is **append-only and human-gated** — captured at `/research` Step 11 (when the run's feedback touched prose/depth/format) and at the tutorial's human-gated save, present → approve → append. It lives in the workspace (sibling of `research/`, intentionally **not git-ignored**, like the other profiles), is **excluded** from the reviewer-dossier discovery list, and is **distinct** from the lead memory and from the reviewer dossiers. **Strictly additive:** with no file, behavior is exactly today's.
- **Deliberate exclusion: NO real-researcher personas.** A profile encodes a *school of thought*, never a named living person — a privacy line, on purpose. `/research-profile` declines a request to model a named living person and offers the school-of-thought framing instead.
- **v1 non-goal:** no per-dossier run-notes — only the single lead memory file accumulates across runs.

## Primers (tutorials)

A **primer** is a ground-up, digestible explanation of a concept the reader is less familiar with. Where the pipeline grounds *claims* in sources, a primer grounds *the reader* in a concept — the on-ramp for when a synthesis assumes a term the reader wanted explained. Primers are optional and built on demand; they never change a run when none is built.

- **How they're built.** The `/research-tutorial` skill builds one primer. **From-run** mode grounds it in a finished run's already-gated corpus (the gate inherited from the run); standalone mode (or a run whose corpus skips the basics) fetches one or two canonical introductory treatments through the same `squid:literature-scout` Tier A/B/Reject gate — the human confirms that search budget. The skill also reads the plan's expertise constraint (from-run) to set who the primer is written for.
- **Handbook-grade.** A full-depth primer is modeled on the user's `GRPO_empirical` guide: a **Table of contents**, a **Motivation** section (why the method exists, the lineage), a **Notation** table when math-heavy, typeset math with foldable proofs, a worked example, and a required **Comparison with alternatives** section (a table plus a grounded when-each-is-preferred discussion). Length is matched to the concept's depth; digestibility comes from navigation and folding. `quick` depth is a lighter primer (no TOC, Notation, or worked example, but a short grounded Comparison).
- **Companion methods-map.** A full-depth primer also emits a companion `tutorials/<concept-slug>--methods-map.md`, modeled on `GRPO_empirical`'s `Methods map.md`: it places the concept among its competitors with a lineage, a comparison table, a when-to-use-which decision guide, and open problems. The primer's Comparison is the quick reference; the methods-map is the full landscape.
- **A maintained primer web.** Neighbor primers (MCMC, CMA-ES, …) build via the same `/research-tutorial` flow; their methods-maps cross-link into a **maintained** web rather than hand-wired wikilinks. On each new full-depth build the save step scans the sibling `tutorials/` dir and repairs the cross-links **bidirectionally** — the new methods-map links neighbors that already have primers, and each existing methods-map that names the new concept is repaired to link back — shown as a **human-gated diff** before writing and **scoped to one `tutorials/` dir** (never across unrelated runs). Canonical slugs + frontmatter `aliases:` keep the `[[ ]]` links resolving. The cross-links live on the **methods-maps only** (the primer's own Comparison table stays focused on its one concept); there is **no separate map-of-content hub** — the methods-maps are the connective tissue.
- **Sourcing rule.** Textbook fundamentals are written as clearly-labeled plain explanation; any non-obvious or contested claim (when the concept beats or loses to alternatives, its failure modes, performance) cites `[S#]` from the gated library; nothing un-gated becomes load-bearing, and a provenance note draws the line. The Comparison and the methods-map make claims about competitive/related methods, so those are grounded too — drawn from the run's `synthesis.md`/`sources.md` where they compare the methods, or from a scout fetch of the named competitors; an ungrounded comparison is not allowed.
- **Review-and-improve loop.** Before the human sees it, the draft is improved through a two-lens readability review launched in parallel: a graduate student solid in the reader's field but new to the concept checks followability and navigation (does the answer land before the jargon, is every term defined at first use, can the example be walked, does the TOC and the motivation → mechanism → comparison arc aid the read), and an expert in a related field checks accuracy, supplies a bridging analogy, and confirms the Motivation and the grounded Comparison are substantive — a primer taught in isolation, with no grounded comparison to its competitors, is a Blocker. Accuracy Blockers outrank readability Nits; the loop caps at **2 cycles**; the save is human-gated with a diff on re-run.
- **Where they live.** From-run: `research/<run-slug>/tutorials/<concept-slug>.md` (and, on full depth, `tutorials/<concept-slug>--methods-map.md`; a one-line pointer dropped into `synthesis.md`). Standalone: `./tutorials/<concept-slug>.md` (plus the methods-map on full depth). The synthesis checkpoint can also offer to build a primer on a flagged concept before continuing (the synthesizer flags primer candidates in its hand-off).

## Research threads

A **research thread** is a wiki-ready consolidation of a finished run: one self-contained, high-quality writing note in a personal research wiki's *thread genre*, ready to drop into `wiki/research-threads/` by hand. Where a primer grounds *the reader* in a concept, a thread re-projects a *whole run* into a publishable shape. The gap a run leaves is genre, not depth — `synthesis.md`, `directions.md`, `sources.md`, and the `tutorials/` primers already carry ~85% of the material; the thread supplies the wiki's section template (an intuition-first Prerequisites + Notation on-ramp, a motivated problem formulation, a core-N-plus-scannable References section, provenance demoted to an end method note), and the wiki's citation and linking conventions. Threads are optional and built on demand; they never change a run when none is built.

- **How they're built.** The `/research-thread <run-slug> [wiki <path>] [quick|full]` skill consolidates one run. It reads the run's artifacts — the only inputs; the thread **introduces no new claims and runs no search** — and drafts them into the canonical thread template (a `> **What this note is.**` opener with the stakes; an intuition-first Prerequisites primer + Notation table for a newcomer reader; scope; a motivation/problem-formulation beat; executive summary; established findings led intuition-first with the author's synthesis flagged; a **References** section that is a core-N-must-trust list plus one scannable tier-as-a-column table; research gap; open questions; a minimal citation set; a suggested reading order; foldable derivations; an end **Provenance (method note)**; a log). The orchestrator drafts (like `/research-tutorial`); no new agent. `full` (default) is the complete genre; `quick` omits the Prerequisites/Notation on-ramp and the Derivations section.
- **The transform + citation translation.** Each section is re-projected from the run (synthesis "answer so far" → executive summary; synthesis themes + the `Analysis — beyond the sources` A-items → findings with the author's synthesis flagged; synthesis gaps + `directions.md` → research gap and open questions; the synthesis `> [!derivation]-` callouts + tutorial folded math → Derivations; `sources.md` → the References (a core-N list + a scannable tier-as-a-column table) and the end Provenance method note). Citations are translated from squid's `[S#]` to the wiki form at every point of use: an inline `[[author-year-slug]]` source-page wikilink plus a `[(PDF)](<sources/S#--slug.pdf>)` local link. Tier-B sources keep their explicit caveat (the gate carries over); the tier map is squid A → wiki A, squid B → wiki B, context-only → wiki C. The `status` frontmatter auto-maps — a run that reached Gate #2 "accept" → `concluded`, else `active`.
- **The register.** A thread is written in the **wiki house style**, the convention the plugin ships (it ships the register, never the wiki): intuition before the formalism, self-contained sections that motivate each object before its closed form, purposeful bold, em-dashes for asides, first-person synthesis voice, define-on-first-use, lightweight "solid"/"press-grade" provenance tags (the tier apparatus demoted to the end method note), honest caveats, tables, typeset LaTeX, foldable derivations, and `[[wikilinks]]` + `[(PDF)]` citations. This genre is **exempt from `WRITING_STYLE`'s synthesis lint** (its anti-bold / anti-em-dash density checks and first-person ban do not apply); the `## Quality rubric` depth rules (show-don't-name, derive-don't-assert, grounded claims, functional output) still bind.
- **Review-and-improve loop.** Before the human sees it, the draft is improved through a two-lens review launched in parallel: a **wiki-editor** lens checks genre + house-style + digestibility (every template section present and ordered, the intuition-first on-ramp and Findings, the core-N + scannable References, provenance demoted to the end method note, citations translated, the register the wiki voice, the length in the wiki norm), and a **source-fidelity** lens checks no drift (every claim traces to `synthesis.md`/`sources.md`, no new un-grounded claim, tiers preserved, each `[S#] → [[slug]]` resolves to the right source, the flagged "my synthesis" items are exactly the synthesis `Analysis` A-items). Genre Blockers and drift Blockers are equal; the loop caps at **2 cycles**; the save is human-gated with a diff on re-run.
- **Standalone, never writes to the wiki.** A thread is self-contained and wiki-ready with no wiki present. Default emits convention-matching `[[slugs]]` plus a **wire-up sidecar** `research/<slug>/thread--wireup.md` (the integration checklist: proposed `related_concepts`/`related_topics`/`related_threads`, which referenced sources need new `wiki/sources/` pages, how to drop the note into `wiki/research-threads/`, and runnable-toy placeholders). Given a `wiki <path>`, the skill reads `concepts/`/`sources/`/`maps/` **read-only** to resolve links and reuse existing source slugs — it **never writes to the wiki**. Writing-only (toys are placeholders, not generated) and human-gated; thread feedback compounds into `research-profiles/writing-quality--memory.md`.
- **Where they live.** `research/<run-slug>/thread.md` (the consolidated thread) and `research/<run-slug>/thread--wireup.md` (the wire-up sidecar), next to the run's other artifacts. Strictly additive — one thread per run; `/research` and the other skills behave exactly as before when none is built.

## Writing Style

The free prose of the run artifacts (`synthesis.md`, `directions.md`, and profile dossiers) follows a style contract at [`docs/WRITING_STYLE.md`](WRITING_STYLE.md): a linear technical-exposition register (closer to lecture notes than a blog) with hard limits on dashes, bold, and colon scaffolding, plus a banned-construction inventory that strips recognizable AI-writing tics. Its `## Quality rubric` is the single checkable home for the handbook-grade depth bar (show-don't-name, derive-don't-assert, compare-and-place, stepped-visual-runnable worked examples, functional clickable output, length matched to depth); a depth critic scores artifacts against it (the synthesis depth loop below), and the lint now also catches bare (non-clickable) `doi:`/`arXiv:`/URL references. For technical material the contract requires real depth — math written as math (`$\ldots$` / `$$\ldots$$`), load-bearing derivations shown not narrated, and heavy derivations folded into Obsidian `> [!derivation]-` callouts so the linear read stays light — enforced by the contract, by the depth critic scoring the synthesis against the rubric, and by the expert/methodologist reviewers. Artifacts are **handbook-grade**: length is matched to the topic's depth, and digestibility comes from navigability rather than from cutting depth — a deep artifact carries a doc-level BLUF, a **Table of contents** (Obsidian `[[#anchor]]` wikilinks), a **Notation** symbol table when math-heavy, dense comparison tables where methods compete, and foldable proofs. The synthesis is the run-level methods comparison. The paragraph budget is per-paragraph, not a cap on document length. Citations are slim inline — `[S#]` (the tier resolves in the sources ledger), except a Tier-B-leaning claim keeps an explicit `[S#, B]` mark because that caveat is load-bearing; every section opens with its conclusion (BLUF), and paragraphs stay one-idea under a 160-word breach line. A project-local `docs/WRITING_STYLE.md` overrides the plugin copy, so taste is tunable per workspace. Writers (the synthesizer and the strategist, and `/research-profile` for dossiers) self-lint with the contract's deterministic checks before hand-off and log the counts. The clarity reviewer enforces it — a breach is a Nit by default, a Blocker when breaches are dense per the contract's severity note; the other four roles ignore style. Template-required labels and headings are exempt; the plugin's own internal contract files are out of scope.

## Iteration Caps

Hard caps. When a cap is hit (or the scout can't proceed), the orchestrator stops the pipeline and surfaces a `USER ACTION REQUIRED` summary.

| Loop | Cap | Counter resets / behavior |
|---|---|---|
| Depth critic scores synthesis → synthesizer deepens | **Max 2 cycles** | Runs every run on `synthesis.md`. Unresolved depth findings after cycle 2 are carried into the checkpoint / Gate #2, flagged. Bounded and human-gated. |
| Strategist revises → panel re-reviews | **Max 2 cycles** | Resets per directions draft. Unresolved Blockers after cycle 2 are carried into the hand-off, flagged. |
| Scout finds too few credible sources | **Surface & stop** | No synthesizing on weak ground — surface to the human rather than proceed. |
| Loop back → re-run from search (Gate #2) | **Human-decided, no auto-cap** | The human gate is the control; there is no automatic loop-back and no cap on rounds. |

## Artifacts & Layout

A run owns `research/<slug>/`:

| File | Written by | Contents |
|---|---|---|
| `plan.md` | research-lead | Research question(s); `mode: targeted\|exploratory`; in/out scope; source strategy (academic/web/local corpus at a path with local-first|local-only supplement mode; named venues/authors if known); success criteria; known constraints (compute/data/time) for the feasibility reviewer; `Synthesis checkpoint: yes\|no` (opt-in mid-run pause, default `no`); `Profiles` (per-role dossier attachments, or `none`). |
| `sources.md` | literature-scout | One entry per accepted source: citation, **tier (A/B)**, one-line provenance justification, a `Local:` link, relevance note, extracted key claim(s). A separate **Rejected** list with reasons (the filter leaves a trail). |
| `sources/` | literature-scout | The local library: fetched PDFs / dated markdown snapshots of accepted sources (`S{n}--{slug}.{pdf\|md}`), so synthesis and review read full texts. Paywalled/unfetchable entries are citation-only (no file). Rejected sources are never fetched. |
| `synthesis.md` | synthesizer | Reader-facing answer (the best current answer, in prose); themes argued at the material's depth (each claim citing a slim `[S#]` that resolves to a tier in the ledger; Tier-B-leaning claims keep `[S#, B]`); tensions/debates; **Analysis — beyond the sources** (OURS, confidence-tagged A# items pushing past the literature, each derivation grounded in cited `S#`/`A#`); implications for the plan questions; where-I-need-judgment; **gaps & follow-up queries**; an evidence-ledger appendix. After the depth-critic loop, a "Depth revisions" changelog and an "Unresolved depth findings" section (if any). |
| `synthesis-depth-review.md` | research-reviewer (`depth`) | The depth critic's located rubric findings on `synthesis.md` (`DPT#` Blockers + Nits), in the reviewer-section shape. The synthesizer deepens the synthesis to resolve them; capped at Max 2 cycles. |
| `directions.md` | strategist | N candidate directions. Each: statement; rationale grounded in the synthesis (citations); novelty delta; feasibility assessment; risks. A recommendation/ranking. After review: a "Revisions made" changelog and an "Unresolved blockers" section (if any). |
| `tutorials/` | `/research-tutorial` | Companion primers on concepts a reader is unfamiliar with, grounded in the run's gated library plus optional gated primer fetches (basics labeled, non-obvious claims cited `[S#]`), each improved through a two-lens readability review (a graduate student new to the concept + a related-field expert) before a human-gated save. Handbook-grade at full depth: a TOC, Motivation, Notation (math-heavy), foldable proofs, and a required Comparison section; a full-depth primer also emits a companion `<concept-slug>--methods-map.md` placing the concept among its competitors (lineage, comparison table, when-to-use-which, open problems). Built on demand, never required. |
| `reviews.md` | research-reviewer ×5 | One section per role, each with Blockers + Nits (location ref, what's wrong, why, suggested fix), then a consolidated "Blockers to resolve" list the strategist works from. |
| `log.md` | all | Append-only, role-tagged entries: `### [ROLE] YYYY-MM-DD HH:MM — subject`. Same Issue-Log discipline as the engineering tracker. |

Two profile artifacts live **outside** the per-run folder — they are persistent and shared across runs, and (unlike `research/`) **not git-ignored**:

| File | Written by | Contents |
|---|---|---|
| `research-profiles/{role}--{domain}[--{lens}].md` | `/research-profile` | A reviewer/lead lens dossier: frontmatter (`role`, `domain`, optional `lens`, `grounded-in`, `updated`); stance & commitments; signature questions; failure modes it hunts; credibility-gated key writings (cited with tiers, each linked to its local copy under `works/`). Persistent, sibling of `research/`. |
| `research-profiles/works/{dossier-slug}/` | `/research-profile` | The dossier's grounding writings, copied locally (PDFs / snapshots) so the lens carries its evidence; persists with the dossier, unlike the ephemeral per-run library. |
| `research-profiles/research-lead--memory.md` | `/research` (after Gate #2) + `/research-profile` | The lead's memory profile: accumulated user preferences and per-run lessons. Append-only, human-gated; created/extended only on explicit approval. Excluded from reviewer-dossier discovery. |
| `research-profiles/writing-quality--memory.md` | `/research` (Step 11) + `/research-tutorial` (save) | Accrued workspace prose/depth/format lessons from human feedback. Read by the prose writers (synthesizer, tutorial) and the depth critic; never overrides the `WRITING_STYLE` contract or its Quality rubric. Append-only, human-gated; created/extended only on explicit approval. Distinct from the lead memory; excluded from reviewer-dossier discovery. |

**Version control.** Run folders are *not plugin content*. The plugin repo (and scaffolded projects) `.gitignore` the top-level run folder (an anchored `/research/` rule, so nested `research/` dirs elsewhere in a project are never caught), and research output never ships on a public branch — and the `/research` orchestrator ensures the target repo ignores `research/` on its first run, so the claim holds even in a project that hadn't set it up. To keep a personal research knowledge base in git, `git add -f research/<slug>/` on a private branch or private remote that is never pushed publicly. Because the ignore rule is uniform across branches, a stray `git add -A` cannot leak research into the public branch.

## Issue Log (single source of truth)

Every agent appends timestamped, role-tagged entries to the run's `log.md` as they work.

```markdown
### [research-lead] 2026-06-02 12:30 — Grooming
...

### [literature-scout] 2026-06-02 13:10 — Search (credibility gate)
...

### [synthesizer] 2026-06-02 14:00 — Synthesis
...

### [strategist] 2026-06-02 14:45 — Directions draft
...

### [research-reviewer:methodologist] 2026-06-02 15:00 — Panel review
...

### [research-lead] 2026-06-02 15:40 — Acceptance
...
```

The orchestrator also appends its own `[orchestrator]` milestone entries at each gate decision, each panel-cycle completion, and memory capture, so a cold resume can reconstruct which steps and gates have passed. Example:

```markdown
### [orchestrator] 2026-06-02 12:35 — Gate #1 approved
```

Format: `### [ROLE] YYYY-MM-DD HH:MM — Short subject`. Append-only.

## Loop-Back Mechanics

`synthesis.md` and `directions.md` each end with an explicit **gaps & follow-up queries** section. At Gate #2, "loop back" re-enters the pipeline at the search step seeded by those queries, with a refined scope the human can edit.

Loop-back is **always human-decided** — there is no automatic loop-back and no auto-cap on rounds. The human gate is the control.

## Engineering Handoff (`/plan` → `/implement-night`)

At Gate #2, "handoff" promotes a chosen direction into an engineering feature spec:

1. The orchestrator writes `docs/features/<slug>.md` from the chosen direction (problem, goal, scope, acceptance-shaped notes, links back to `research/<slug>/`).
2. It recommends the next command: `/plan docs/features/<slug>.md` (grill + groom + approve), then `/implement-night`.

The handoff **stops at writing the feature spec and recommending the command** — it does not auto-invoke `/plan`. Research → build stays a human decision.

## Responsibility Model

Every role owns their deliverable. Quality is distributed across the team.

| Role | Owns | Accountable For |
|---|---|---|
| research-lead | The whole question — scope, mode, and user-POV acceptance | "Does this answer the question?" If research-lead accepts and the directions don't address what the user asked, that's a research-lead failure. |
| literature-scout | Source credibility | If a Reject-grade source is treated as load-bearing, or credible work is missed, that's a scout failure. |
| synthesizer | Faithful synthesis (incl. the Analysis section) | If `synthesis.md` misreads or overstates what the sources say, that's a synthesizer failure. The Analysis is the synthesizer's too: an OURS A-item whose grounding doesn't hold is a synthesizer failure (and a methodologist Blocker). |
| strategist | The directions | If a direction is unsupported, infeasible-as-presented, or a known result repackaged, that's a strategist failure. |
| research-reviewer | Their one dimension | If a Blocker-grade defect in their dimension lands and they didn't flag it, that's a reviewer failure. |
| Orchestrator | The team | Verifying each agent's report before forwarding it. If an agent cuts corners and the orchestrator accepts it, that's an orchestrator failure. |

**The orchestrator is a MANAGER, not a researcher.** It NEVER writes synthesis or directions itself. It launches agents, enforces the two gates, and verifies reports — spot-checking that load-bearing claims carry credible citations before forwarding.

## No False Confidence (research variant)

The single worst thing the orchestrator can do is forward a directions memo as "grounded" when it rests on weak or absent evidence.

1. **"The literature says X" is not evidence — a Tier-A citation is.** A claim is only as good as its cited, credibility-tagged source.
2. **A load-bearing claim without a credible citation is a Blocker, not a footnote.** Surface it; don't smooth it over.
3. **If the scout can't find enough credible sources, that is the finding.** Surfacing "insufficient credible evidence" beats synthesizing on weak ground.
4. **When provenance is unclear, err toward Reject.** A missing source is safer than an uncredible one silently treated as load-bearing.

Before forwarding a report, the orchestrator verifies:

1. Re-read the load-bearing claims in `synthesis.md` / `directions.md`.
2. Check each against `sources.md` — does it carry an `[S#]` citation that resolves to a tier in the ledger? Citations are slim inline; the tier lives in the ledger, except a Tier-B-leaning claim keeps an explicit `[S#, B]` mark plus a caveat.
3. **REJECT and re-launch if a load-bearing claim has no credible citation, or a Tier-B source is used load-bearing without that explicit `[S#, B]` mark and caveat** — with specific instructions about what was missed.

"The agents agree" is NEVER sufficient if the evidence chain doesn't hold.
