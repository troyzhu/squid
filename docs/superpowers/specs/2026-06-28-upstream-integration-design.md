# Design: Rebuild the `troyzhu/squid` fork on upstream v0.4.4 + research layer + generated Codex support

- **Date:** 2026-06-28
- **Branch:** `feat/research-codex-v2` (created off `upstream/main` @ v0.4.4)
- **Status:** Approved (brainstorming) — pending implementation plan
- **Owner:** troyzhu

## 1. Context

The fork (`troyzhu/squid`) diverged from upstream (`iusztinpaul/squid`) at **v0.2.7** (commit `1ac149c`):

| Branch | Ahead | Behind | What it is |
|---|---|---|---|
| `main` / `origin/main` | 0 | 37 | Clean v0.2.7 ancestor — untouched |
| `origin/feat/research-layer` | 54 | 37 | The real work: research layer + a hand-built Codex port |

In those 37 commits upstream shipped a **breaking refactor** (v0.2.8 → v0.4.4): it decomposed the two monolithic skills (`/day`, `/night`) into a **composable pipeline**, deleted `docs/PROCESS.md`, renamed `product-manager` → `product-architect`, and moved the canonical brief to `AGENTS.md` (with `CLAUDE.md` reduced to a symlink). The fork's research + Codex work is built on the *old* structure those deletions removed.

### Inventory (verified)

```
Skill                         main(0.2.7)   upstream(0.4.4)        research-layer
scaffold/refactor/triage-issue/
  architecture-review/self-improve/
  testing-python                 ✓               ✓                     ✓
day                              ✓        → implement-task            ✓
night                            ✓        → implement-night           ✓
grill-me                         ✓        → grilling                  ✓
create-pr                        ✓        → folded into review        ✓
git-guardrails                   ✓          (deleted)                 ✓
write-a-skill                    ✓          (deleted)                 ✓
plan/implement-task/implement-night/
  review/review-ci/grilling      –               ✓                    –
research/research-profile/
  research-thread/research-tutorial –             –             ✓  (fork's own)

Agent: product-manager → product-architect (upstream rename).
Fork adds 5 research agents: literature-scout, research-lead, research-reviewer,
  strategist, synthesizer.
```

Working tree is clean (only `.remember/` is gitignored). Nothing was lost locally; every fork skill is committed on `feat/research-layer`.

## 2. Goals / Non-goals

**Goals**
1. Adopt upstream's v0.4.4 architecture (composable pipeline, product-architect, scaffold rules/evaluate, ADR/glossary/tracker specs, Pydantic + clean-architecture rules, `AGENTS.md`-centric memory, plugin deps).
2. Re-home the fork's **research layer** (5 agents, 4 skills, 2 docs) onto that base, with its soft couplings fixed.
3. Replace the fork's fragile **three hand-maintained Codex mirrors** with a **single source of truth + one generator + CI drift-check**, so an upstream change is one regen instead of ~24 hand-edits.
4. Preserve fork identity (`owner: troyzhu`, install `squid@troyzhu`).

**Non-goals**
- No change to `main`, `origin/main`, or anything on `upstream` (read-only).
- No push of anything without explicit human approval.
- No new build system for the *markdown contract* (the Codex generator is dev tooling, the documented analog of `scripts/release.sh` — not part of the contract).
- Not inventing new research/Codex semantics — re-home what exists, modernized.

## 3. Constraints & guardrails

- **Fork only.** All work lands on `feat/research-codex-v2`. `feat/research-layer` is kept verbatim as backup and as the source to re-home from.
- **No unsanctioned push.** Local commits only until the human approves a push.
- **`upstream` remote is read-only** (added this session for comparison/cherry-pick); removable at the end.
- **`AGENTS.md` ≤ 250 lines (invariant I2).** Research rules live in their own skills/docs, cross-referenced — never inlined into `AGENTS.md`.

## 4. Strategy decision

**Chosen: B1 — Rebuild on the upstream base.** Fresh branch off `upstream/main`; re-apply the research layer (it ports cleanly); regenerate Codex from a single source of truth.

**Why B1 over the alternatives**
- **A — `git merge upstream/main` into the fork branch:** upstream *deleted* the files the fork builds on, producing dozens of delete-vs-modify conflicts, and the Codex stubs would survive pointing at deleted targets. "Worst of both": heavy conflict resolution *and* a tangled tree that still needs the Codex cleanup. Rejected.
- **C — Surgical cherry-pick** of standalone specs onto the old base: low-risk but forgoes the composable pipeline *and* the `AGENTS.md`-centric foundation — i.e. it skips the single biggest win *and* the keystone that makes Codex clean. Rejected.
- **B1 is cheap because the research layer was designed to be strictly additive.** Its only couplings to the deleted skills are two handoff strings and a few documentation analogies — nothing in research *calls into* the engineering pipeline. Re-homing is therefore mostly mechanical.

**Keystone insight:** upstream already moved the canonical brief from `docs/PROCESS.md` (Claude-flavored) to `AGENTS.md` (tool-neutral), with `CLAUDE.md` as a one-line `@AGENTS.md` pointer. Codex reads `AGENTS.md` natively. So adopting upstream is not in tension with the Codex goal — it is the better foundation *for* it.

## 5. Base adoption (v0.4.4)

The branch starts *as* `upstream/main`, so adoption is automatic. On top of it we:
- **Fix two stale upstream bugs** the analysis caught: `skills/refactor/SKILL.md` and `skills/triage-issue/SKILL.md` still reference the deleted `docs/PROCESS.md` and the renamed "PM agent" — repoint to `AGENTS.md` and "product-architect", and align their tracker layout with the canonical `tasks/<NNN>-<slug>.md` + `tasks/done/` model.
- Keep upstream's three standalone helpers (`/refactor`, `/triage-issue`, `/architecture-review`) and the three plugin deps (`context7`, `code-review`, `commit-commands`).

## 6. Research layer re-homing

Bring over from `feat/research-layer`, unchanged except where noted:
- **Agents (5):** `research-lead`, `literature-scout`, `synthesizer`, `strategist`, `research-reviewer`.
- **Skills (4):** `research`, `research-profile`, `research-tutorial`, `research-thread`.
- **Docs (2):** `docs/RESEARCH_PROCESS.md`, `docs/WRITING_STYLE.md`.
- **Design specs/plans:** the research design history under `docs/superpowers/`.

**Required edits (all soft couplings):**
1. **Handoff strings** in `skills/research/SKILL.md` (Gate #2) and `docs/RESEARCH_PROCESS.md`: replace the `/grill-me` + `/night` recommendation with the v0.4.4 flow — write `docs/features/<slug>.md`, then recommend `/plan docs/features/<slug>.md` (which now subsumes grilling) → `/implement-night`.
2. **Doc analogies:** update the "engineering analog" table (`product-manager` → `product-architect`) and repoint the `docs/PROCESS.md` cross-reference → `AGENTS.md`.
3. **Severity Rule:** `RESEARCH_PROCESS.md` already restates it self-containedly; just drop the dead `docs/PROCESS.md` pointer.

The research run folder stays git-ignored; nothing in research is `git add -A`'d. No change to the two-human-gate research flow.

## 7. Codex generated support (design level)

Replace the triplicated, hand-maintained Codex layer with a generator. **Detailed build doc for Codex is produced in the implementation plan (writing-plans).** Design contract:

**Canonical inputs (the only hand-edited Codex inputs):**
- `agents/*.md` and `skills/*/SKILL.md` — their existence *defines* which Codex artifacts exist.
- One data file `scripts/codex/config.yaml` — per-role guardrail sentence + Codex-only metadata (nicknames, `brandColor`, the `defaultPrompt` skill list). The single place Codex-specific wording lives.

**Generated outputs** (each carries a `GENERATED — do not edit; run scripts/gen_codex` header; never hand-edited):
- `.codex/agents/squid-<role>.toml` — one per agent.
- `plugins/squid-codex/skills/<name>/SKILL.md` and `.agents/skills/<name>/SKILL.md` — pointer stubs, one per skill.
- The agent-map table + skill list inside `plugins/squid-codex/references/codex-adapter.md`, between `<!-- BEGIN GENERATED -->` / `<!-- END GENERATED -->` markers (surrounding prose stays hand-written).
- `version` + `defaultPrompt` in `plugins/squid-codex/.codex-plugin/plugin.json` and `.agents/plugins/marketplace.json`.

**Fail-loud rule (kills the drift already observed — `research-thread` was missing from `.agents/`):** if an agent/skill exists with no `config.yaml` entry, or a `config.yaml` entry names a non-existent agent/skill, the generator **exits non-zero with a named error**. *Good:* `ERROR: skill 'research-thread' has no codex config entry`. *Bad:* silently skipping it.

**CI** `.github/workflows/codex-sync-check.yml`: run the generator, then `git diff --exit-code` must be clean — same pattern as the existing `release-check.yml`.

**`scripts/release.sh`:** after the version bump, run the generator so Codex artifacts version in lockstep and land in the release commit (today they silently go stale; the sub-plugin is pinned at `0.2.7+codex.20260627005000`).

**Recommended generator language:** Python 3 stdlib (no third-party deps; clean TOML/JSON/markdown templating; macOS ships `python3`). Final call left to Codex per the division of labor.

**Validation acceptance:** generator is **idempotent** (running twice → no diff; deleting any generated file and regenerating restores it byte-identical), and the emitted `.codex/*.toml` + `.codex-plugin/plugin.json` validate against **current Codex docs** (to be confirmed via context7/web during build, since these conventions may have moved since the fork's commit).

## 8. Manifest / version / fork identity

- `plugin.json` + both marketplace files: keep `owner: troyzhu`, `source: ./`; set version **`0.5.0`** (signals "adopted 0.4.4 + research + generated Codex").
- `README.md` reframed as the fork: what it adds (research layer, generated Codex) on top of upstream, install via `troyzhu/squid`, plus the `npx skills` / Codex path.

## 9. Dropped skills (reversible)

Follow upstream and **do not carry** `git-guardrails` or `write-a-skill` onto the new branch. This is **non-destructive** — both remain on `feat/research-layer` and in history, recoverable with `git checkout origin/feat/research-layer -- skills/<name>`. Both are listed here as **"re-home on request."** (`git-guardrails` overlaps the `commit-commands` dep; `write-a-skill` overlaps the official `plugin-dev` skills — upstream's stated reasons for removal.)

## 10. Division of labor

- **Claude (high repo-context):** create branch; re-home research layer + fix handoffs; fix the two stale upstream skills; reconcile manifest/version/README; author the Codex generator **build doc** (the spec, not the code); write + commit this design doc.
- **Codex (from the build doc):** implement `gen_codex` + `config.yaml`; generate the Codex artifacts; add the CI drift-check; wire `release.sh`. It builds the tooling it will itself run.

## 11. Validation (before "done")

- `claude plugin validate` clean.
- `gen_codex` idempotent (run-twice no-diff; delete-and-restore byte-identical).
- `.codex/*.toml` + `.codex-plugin/plugin.json` schema-valid against current Codex docs.
- `/scaffold` dry-run in an empty dir → sensible `AGENTS.md` + `CLAUDE.md` symlink, no app source written.
- Research handoff strings resolve to skills that exist (`/plan`, `/implement-night`).

## 12. Sequencing (each phase = one reviewable commit)

1. Branch off `upstream/main`; commit this design doc. *(in progress)*
2. Re-home research layer (agents + skills + docs) + fix handoff strings.
3. Fix the two stale upstream skills (`refactor`, `triage-issue`).
4. Reconcile manifest / version / README (fork identity, 0.5.0).
5. Author the Codex generator build doc → hand to Codex → Codex implements generator + `config.yaml` + artifacts + CI + `release.sh`.
6. End-to-end validation.

## 13. Open items / assumptions

- Branch name `feat/research-codex-v2`, version `0.5.0`, owner `troyzhu` — assumed; easy to change.
- Codex artifact schemas assumed stable vs. the fork's hand-built shapes; to be confirmed against current Codex docs during build.
- If more-developed local versions of any dropped skill exist outside this repo, fold them in on request.
