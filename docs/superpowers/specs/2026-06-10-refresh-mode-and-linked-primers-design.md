# Refresh Mode + Linked Primers — Design Spec

> Status: design, pending review. Date: 2026-06-10. Branch: `feat/research-layer`.
> Two cohesive, additive features: upgrade a stale run **in place** (no archive), and build
> neighbor primers that form a **maintained** cross-linked web. Both honor the maintainer's
> standing preference: additive, never destructive; the run folder is a self-contained artifact.

## Context

Two requests from testing the SA workspace:

1. The existing SA run predates the depth-critic loop and local-first downloads, so its synthesis is
   shallow and its library is thin. `fresh` would archive it; the maintainer wants to **resume and
   fill the missing pieces in place**. Today's `resume` only fills *missing artifacts* — a
   complete-but-stale run looks "done" and jumps to Gate #2, so there is no upgrade path.
2. The maintainer wants neighbor topics (MCMC, CMA-ES, …) as primers **linked** to the SA work.
   `/research-tutorial` builds each today and Obsidian connects them via `[[wikilinks]]`, but the
   links are not *maintained*: building MCMC's primer doesn't link it back from SA's methods-map
   (whose comparison cites `[S#]`, not sibling primers), so the web is hand-wired.

---

## Feature 1 — Refresh mode (resume → upgrade a stale run in place)

A `refresh` path folded into the `/research` Step 1 resume protocol. When a run is **complete but
stale**, detect the gaps against the current pipeline and fill them **in place** — nothing archived.

**Staleness signals** (detected on resume of a run that has `synthesis.md` + `directions.md`):
- `sources.md` has accepted entries with `Local: none` or a missing file in `sources/` → **library stale** (predates local-first).
- `log.md` has no `depth-critic cycle` milestone → **synthesis never ran the depth loop**.
- `synthesis.md` lacks the v2 sections (`## The answer so far`, `## Analysis — beyond the sources`) or carries ~0 typeset math → **v1-shape synthesis**.

**The refresh menu** (presented instead of jumping to Gate #2; the human picks any subset):
1. **Backfill the library** — re-download only: for each accepted source with `Local: none`/missing
   file, run the open-access ladder (Step 6 logic) and update its `Local:` field. **No re-search, no
   re-gate** — the gate/tiers/provenance in `sources.md` are preserved; only `Local:` fields change.
2. **Deepen the synthesis** — regenerate `synthesis.md` against the now-local corpus (re-run Step 5)
   and run the Step 5.4 depth-critic loop. Reuses `plan.md` + `sources.md` + the library. The old
   synthesis is **backed up** (`synthesis--pre-refresh-{YYYYMMDD}.md`) and overwrite is confirmed,
   so any annotations are recoverable.
3. **Propagate downstream** — if the synthesis changed materially, optionally re-run
   directions → panel → acceptance (the existing Gate-#2 loop-back). Human-decided.

**Preserved vs rebuilt:** preserved = `plan.md`, `sources.md` (entries/tiers/provenance; only
`Local:` updated), the library files already present, `directions.md` (unless propagate is chosen).
Rebuilt = the missing library files (added), `synthesis.md` (only if deepen chosen, with a backup).

**Reusability:** works for any old run, not just SA — it is "bring this run up to the current
pipeline's standard."

### How it plugs in (reuse-first)
- `skills/research/SKILL.md` Step 1: the existing-run detection already lists which artifacts are
  present; add the staleness check and, for a complete-but-stale run, present the refresh menu. The
  top-level prompt stays `resume / fresh / abort`; `resume` routes to refresh when stale.
- **Backfill** = a focused `literature-scout` launch in a new **backfill mode**: "read the existing
  `sources.md`; for each accepted entry whose `Local:` is `none` or whose file is missing, run the
  open-access ladder and download; update only the `Local:` field; do not re-search or re-gate."
  Reuses Step 6 + the OA ladder; mirrors the local-corpus path's "copy not fetch" precedent.
- **Deepen** = the existing Step 5 (synthesizer) + Step 5.4 (depth loop) pointed at the run — so it
  inherits the rubric, the depth critic, and the writing-quality memory automatically.
- Resume re-entry note: a complete run with stale signals can refresh rather than only proceed to Gate #2.

---

## Feature 2 — Linked primers + hardened bidirectional cross-linking

Each neighbor (MCMC, CMA-ES, …) is its own `/research-tutorial "<method>" from-run <slug>` primer +
methods-map (existing flow). The new part is a **maintained** web — built, not hand-wired. (No
separate map-of-content hub — the methods-maps are the connective tissue; per the chosen option.)

**Canonical slugs.** A concept's primer/methods-map slug is deterministic (`<concept-slug>`), and the
primer frontmatter's `aliases:` carries variants (e.g. `mcmc`, `markov-chain-monte-carlo`) so
`[[mcmc]]` always resolves. A methods-map names each neighbor by its canonical `[[<neighbor-slug>]]`.

**Bidirectional linking on build** (a new step in `/research-tutorial` Step 6 — save):
- After drafting the new primer + methods-map, **scan the sibling `tutorials/` dir** (the run's, or
  `./tutorials/` standalone) for existing primers/methods-maps.
- The new methods-map links `[[<neighbor-slug>]]` for every neighbor that already has a primer.
- For each existing methods-map that names the new concept (in its comparison or lineage), **add /
  repair the `[[<new-slug>]]` link back** to the new primer — so the edge is bidirectional.
- The methods-map comparison table's method-name cells become `[[<neighbor-slug>]]` wikilinks when a
  primer for that neighbor exists (a plain name + alias otherwise, going live when it's built later).
- **Human-gated:** show a diff of every cross-link edit to existing files before writing (mirrors the
  existing "drop a `> Primer:` pointer into `synthesis.md`" step). Never silently rewrite a reviewed primer.

**Scope guard:** cross-link only within the same `tutorials/` dir; never reach across unrelated runs.

### How it plugs in (reuse-first)
- `skills/research-tutorial/SKILL.md` Step 6: add the "cross-link into the primer web" step
  (scan siblings → repair bidirectional links → human-gated diff). The methods-map template's
  comparison/see-also already use `[[ ]]`; extend them to sibling primers.
- The grounding/credibility path is unchanged — neighbors are fetched + gated as today.

---

## Reused vs new (explicit)

| Piece | Status |
|---|---|
| Staleness detection + refresh menu in resume | **New** — Step 1 extension |
| Scout **backfill mode** (download `Local:none` over existing `sources.md`) | **New mode**, reuses Step 6 + OA ladder |
| Deepen = re-run Step 5 + Step 5.4 on the run | **Reuse** — inherits rubric / depth critic / writing-memory |
| Synthesis backup before overwrite | **New** (safety) |
| Neighbor primers via `/research-tutorial` | **Reuse** — existing flow |
| Bidirectional cross-link maintenance on save | **New** step in tutorial Step 6 |
| Canonical slugs + alias-resolved `[[ ]]` | **New** convention (small) |
| Methods-MOC hub | **NOT built** — chosen option is links-only |
| Archiving a run to upgrade it | **NOT done** — refresh is in place |

## Files (anticipated; the plan finalizes)
- `skills/research/SKILL.md` — Step 1 staleness detection + refresh menu; resume re-entry note.
- `agents/literature-scout.md` — the backfill mode (download `Local:none` over existing `sources.md`).
- `skills/research-tutorial/SKILL.md` — Step 6 cross-link step; methods-map sibling `[[ ]]` links; slug/alias rule.
- `docs/RESEARCH_PROCESS.md` — document refresh mode + the maintained primer web.
- `README.md` — one line each.

## Verification
`claude plugin validate`; a trace of refresh on a complete-but-stale run (backfill updates only
`Local:`, deepen backs up + regenerates + runs the depth loop, nothing archived); a trace of building
a second primer that repairs the first's methods-map link (human-gated diff); cross-linking stays
within one `tutorials/` dir; net contract size stays lean.

## Out of scope
- A map-of-content hub note (chosen option is links-only).
- Cross-linking across unrelated runs / global primer index.
- Auto-propagating directions on every refresh (human-decided, reuses Gate-#2 loop-back).

## Resolved decisions (review, 2026-06-10)
1. **Deepen = regenerate.** Refresh re-runs the synthesizer against the backfilled corpus + the depth
   loop, after backing up the old synthesis to `synthesis--pre-refresh-{YYYYMMDD}.md` (annotations
   recoverable). Not incremental in-place editing.
2. **Refresh = pick-any-subset menu.** Present the detected stale items (backfill library / deepen
   synthesis / propagate downstream); the human runs any subset. Not a one-shot.
3. **Cross-links live on the methods-maps only.** Sibling `[[ ]]` links live in the methods-map
   (comparison table + see-also), repaired **bidirectionally** on every new primer build via a
   **human-gated diff**. The primer's own Comparison table is left focused on teaching the one
   concept (no sibling links there).
4. **Slugs:** a small documented slug rule the tutorial always applies, plus obvious `aliases:`
   (e.g. `mcmc` ↔ `markov-chain-monte-carlo`) so `[[ ]]` resolves regardless of how a neighbor is named.
