# Research Layer: Depth-Critic + Quality Rubric — Design Spec

> Status: design, pending review. Date: 2026-06-10. Branch: `feat/research-layer`.
> This spec is the input to an implementation plan. It is the response to a maintainer instruction:
> stop patching the contract reactively to each test example; design the *systemic* improvement.

## Context

The research layer keeps producing artifacts that fall short of the maintainer's bar (high-level
synthesis, thin tutorials), and each test round has been answered by bolting another requirement
onto the contract (`WRITING_STYLE.md`, `synthesizer.md`, `research-tutorial`). That is a treadmill:
the contract bloats (so agents skim it and each new rule earns less), and the maintainer's standard
is re-taught every round instead of captured once — the exact repetitive effort this repo exists to
remove.

**Diagnosis.** The gap is not a missing instruction. It is two structural facts:

1. **No mechanism drives depth.** One synthesizer/tutorial pass plus review loops that check
   *compliance* (tics, grounding, structure) cannot match a document refined over many human
   iterations. The reviews audit; they do not elaborate. The synthesis has no revise loop at all
   (only an orchestrator spot-check and an optional human checkpoint).
2. **The standard is described, not captured.** Quality requirements are scattered as prose across
   five files and re-stated each round. There is no single, checkable home for "what good looks like."

**Constraint (from the maintainer).** The plugin stays **standalone** — it ships conventions, not
artifacts. No bundled example repo. A gold-standard exemplar, if ever used, lives in the *consuming
project* and is strictly opt-in; the plugin ships none and depends on none.

**Recurring symptoms are categories, not one-offs.** The three latest items —
(a) a mechanism *named but not shown* (the proposal stage), (b) a worked example that is prose with
*no visual*, (c) *dead* (non-clickable) reference links — are instances of three rubric categories:
show-don't-name depth, use-the-medium, and functional output. They belong in the rubric, not as
bespoke patches.

## The design (three parts, lean, reusing what exists)

### Part 1 — A distilled quality rubric (the captured standard)

A single concise, checkable list of the handbook-grade properties an artifact must have. It is
*conventions*, the same kind of thing `WRITING_STYLE.md` already is — a few dozen lines, standalone,
no example artifact. It becomes the **one home** for depth/quality requirements; the agents, skills,
and reviewers **reference it** instead of each restating their own depth prose (a net de-duplication —
this is where the treadmill's bloat gets paid back).

Rubric contents (each a checkable property):

- **Show, don't name.** A load-bearing mechanism component is shown concretely — instantiated across
  2–3 representative settings, with its formal conditions — not just named. *(e.g. SA's proposal step:
  bit flip / 2-opt swap / Gaussian perturbation; the symmetry condition $q_{ij}=q_{ji}$ and the
  Metropolis–Hastings correction when it fails; SA is MH-MCMC with a cooling schedule.)*
- **Derive, don't assert.** A load-bearing result a technical reader would question is derived
  (steps as display math), heavy derivations folded into `> [!derivation]-` callouts.
- **Compare and place.** A concept is set against its competitive/related methods with a table and a
  grounded, when-each-is-preferred discussion (full-depth tutorials also ship the companion methods-map).
- **Worked examples are stepped + visual.** Terse `Step N` equation-forward steps; an inline visual
  (Mermaid / ASCII sketch / trajectory table); a foldable runnable snippet when the process is dynamic.
- **Functional output.** Every reference, DOI, arXiv id, URL, and `Local:` path is a clickable
  markdown link; long artifacts carry a working `[[#anchor]]` table of contents; math-heavy ones
  carry a Notation table.
- **Length matched to depth.** Digestibility is navigability + folding, not brevity.
- (Inherited, unchanged) typeset math, slim `[S#]` citations, American English, the anti-tic limits.

Location (resolved): a concise `## Quality rubric` section in `WRITING_STYLE.md`.

### Part 2 — A depth/quality critic + elaboration loop (the missing mechanism)

A review pass whose job is *depth*, not compliance: it scores a draft against the rubric and emits
**specific, located** findings — "Section X names {mechanism} but never shows it → deepen", "the
worked example is prose with no visual → restructure to stepped + add a diagram/table/runnable
snippet", "reference Y is a bare DOI, not a link", "this comparison has no when-preferred discussion
or grounding", "math-heavy and long but no Notation/TOC". Findings are tagged Blocker (a rubric
requirement unmet) / Nit (polish). The critic does **not** rewrite; the writer elaborates.

Where it plugs in (reuse-first):

- **Synthesis (NEW loop).** Today the synthesis has no revise loop. Add one: after the synthesizer
  produces `synthesis.md`, run the depth critic against the rubric; the synthesizer revises to
  resolve Blockers; re-run; **cap 2 cycles**; then the existing orchestrator spot-check + optional
  human checkpoint. This is the main new mechanism and targets the artifact that fell shortest.
- **Tutorial (EXTEND existing).** The two-lens review loop (`/research-tutorial` Step 5) already
  exists; make it rubric-driven — the expert lens scores against the rubric explicitly, the learner
  lens checks navigability/visual. No new loop, just the rubric as its checklist.
- **Directions (EXTEND existing).** The 5-role panel stays 5 roles; the methodologist/clarity lenses
  reference the rubric. No new role on the directions panel.

Implementation of the critic (resolved): a **`ROLE: depth` on the existing parameterized
`research-reviewer` agent**, launched as the synthesis depth pass and reused conceptually by the
tutorial lenses — not a new agent.

**Deterministic where possible.** Some rubric items are lintable, so push them into the
`WRITING_STYLE` lint rather than model judgment: a **bare-reference-link check** (a `doi:`/`arXiv:`/
bare `http(s)://` not inside `[...](...)`, outside code fences) catches dead links cheaply and
exactly. The critic handles the judgment items (show-don't-name, comparison substance, visual fit).

### Part 3 — Compounding (so feedback is captured, not repeated)

Extend the existing end-of-run **lead-memory** capture (`research-profiles/research-lead--memory.md`,
human-gated, append-only) to also accrue **writing-quality lessons** — when the maintainer corrects
the same kind of shortfall twice, it becomes a durable note the writers read, or a proposed rubric
delta. This is what turns "the maintainer re-explains each run" into "the standard sharpens itself."
The memory lives in the consuming workspace (standalone-friendly); the rubric lives in the plugin.

## Reused vs new (explicit)

| Piece | Status |
|---|---|
| Quality rubric (Part 1) | **New** — concise, standalone, consolidates scattered depth prose |
| Synthesis depth-critic + elaborate loop | **New** — the synthesis had no revise loop |
| `ROLE: depth` on `research-reviewer` | **New role**, reuses the existing parameterized-reviewer + launch machinery |
| Tutorial two-lens loop made rubric-driven | **Extend** existing Step-5 loop |
| Directions panel referencing the rubric | **Extend** existing 5-role panel (still 5 roles) |
| Bare-reference-link lint check | **New** deterministic check in the existing lint |
| Lead-memory accruing writing lessons | **Extend** existing human-gated capture |
| Bundled exemplar | **Explicitly NOT built** — standalone constraint |

## Cost, risk, and the bloat payback

- The synthesis loop adds 1–2 reviewer launches + synthesizer revise passes per run; capped at 2
  cycles; the human gate stays the final control. Proportionate to the quality goal.
- Net contract size should **not** grow and may shrink: the rubric is the single home for depth
  requirements, and the agents/skills reference it instead of each restating their own depth prose.
  The implementation plan should de-duplicate as it goes (remove-before-adding).
- Risk: the critic becomes "more rules" rather than a generative loop. Mitigation: the critic's
  output must be *specific located deepen-findings that trigger expansion*, not a pass/fail score —
  it imitates the maintainer's manual iteration.

## Files (anticipated; the plan finalizes)

- New: the rubric (a `WRITING_STYLE.md` section or `docs/QUALITY_RUBRIC.md`).
- Modify: `agents/research-reviewer.md` (the `depth` role), `skills/research/SKILL.md` (synthesis
  depth loop), `skills/research-tutorial/SKILL.md` (rubric-driven lenses; the 3 items as rubric refs),
  `agents/synthesizer.md` (reference the rubric; revise-against-critic), `docs/WRITING_STYLE.md`
  (the bare-link lint check; reference the rubric), `docs/RESEARCH_PROCESS.md` (document the loop),
  `README.md` (one line). Lead-memory capture wording in `skills/research/SKILL.md`.

## Verification

`claude plugin validate`; the lint self-passes (incl. the new bare-link check, with the doc's own
example forms self-exempt); a trace showing the synthesis depth loop is capped and human-gated; the
3 items are present as rubric entries and the critic/lenses reference them; net contract line-count
does not balloon (ideally drops via consolidation).

## Out of scope

- A bundled exemplar repo (standalone constraint). An optional project-local exemplar pointer is a
  possible future opt-in, not this spec.
- Generating image/GIF assets into run folders (reproducibility/credibility; the runnable snippet is
  the reproducible "animation").
- Re-running any existing workspace artifact — that is the maintainer's action once the plugin ships.

## Resolved decisions (review, 2026-06-10)

1. **Rubric location:** a concise `## Quality rubric` section in `WRITING_STYLE.md` (it is the
   prose-quality contract already; one source of truth).
2. **Critic surface:** a `ROLE: depth` on the existing parameterized `research-reviewer` agent
   (reuses the panel/launch machinery).
3. **First build = core, then follow.** Core (build now): the rubric + the synthesis
   depth-critic/elaborate loop + the bare-reference-link lint check. Fast follow (after the core is
   validated): make the tutorial two-lens loop rubric-driven, and extend lead-memory to compound
   writing-quality lessons. The shared rubric + lint already benefit the tutorial in the core (its
   writer reads `WRITING_STYLE.md` and runs the lint); the follow adds dedicated lens enforcement.
