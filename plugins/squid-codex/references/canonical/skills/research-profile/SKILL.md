<!-- GENERATED — do not edit; run scripts/gen_codex.py -->

---
name: research-profile
description: Build or update a reviewer/lead profile dossier — a role × domain × school-of-thought lens (stance, signature questions, failure modes it hunts, key writings) that /research can layer onto a reviewer or the research-lead at launch time. Drives the literature-scout to pull the dossier's grounding material through the same credibility gate, drafts the dossier, and saves it (human-reviewed) under research-profiles/. Trigger when the user says "/research-profile", "build a reviewer profile", "make a {role} dossier for {domain}", or wants a reusable lens for the research panel. NO real-researcher personas — profiles encode schools of thought, never named living people.
disable-model-invocation: true
argument-hint: <free-form: role, domain, school-of-thought/lens>
---

# Research Profile — build a reviewer/lead lens dossier

Build (or update) ONE **profile dossier**: a `role × domain × school-of-thought lens` that `/research` can layer onto a reviewer or the research-lead at launch. A profile sharpens *what a lens looks for* — its stance, signature questions, failure modes, and the writings that ground it — built from material pulled through the literature-scout's credibility gate. It **never** overrides a reviewer's contract; it focuses it.

You are the **orchestrator** — a manager, not a researcher. You launch ONE scout to ground the dossier, draft it, and save it only after the human approves. You do not search yourself.

`$ARGUMENTS` takes three forms:

- **Explicit triple** — a comma-separated 2–3-token form (the role, the domain, and an optional school-of-thought lens, e.g. `methodologist, statistics, bayesian` — fluent in the rival camp, reviewing from Bayesian commitments). This is the direct path; it builds exactly one dossier.
- **Problem statement** — a question or problem (reads as a sentence, contains a `?`, or clearly isn't a triple). This enters **suggest mode**: the skill proposes a slate of profile candidates for the human to review, then builds only the selected ones.
- **From-run** — `from-run <run-slug>[, role, domain, lens]`. Builds a dossier from an existing `/research` run's already-gated corpus rather than searching anew (Step 1.6). The credibility gate is inherited from the run; no search budget is spent.

If `$ARGUMENTS` is empty, ask the human which mode they want (name a triple, give a problem to get suggestions, or `from-run <slug>` to ground a dossier in an existing run). The skill **never spends search budget or saves anything without an explicit selection** — in suggest mode, no dossier is grounded or written until the human picks it.

**Hard rule: NO real-researcher personas.** A profile encodes a *school of thought*, never a named living person — a privacy line, deliberate. If the user asks to model a named living person, decline and offer the school-of-thought framing instead (e.g. not "review as Dr. X" but "review from the {lens} commitments Dr. X is associated with").

---

## Step 1 — Resolve paths and parse the request

**Resolve the canonical doc.** Same base-directory trick as `/research` Step 0: the harness states `Base directory for this skill: <path>` (it ends in `…/skills/research-profile`). The plugin root is **two directories up** from that base. Set `RESEARCH_DOC = <plugin-root>/docs/RESEARCH_PROCESS.md` and verify with `ls`. If the consuming project has its own `docs/RESEARCH_PROCESS.md` (relative to cwd), prefer the project copy. Pass `{RESEARCH_DOC}` into the scout launch. Resolve `STYLE_DOC = <plugin-root>/docs/WRITING_STYLE.md` the same way (project copy preferred) — it governs the dossier's prose at the drafting step.

**Resolve the profiles dir.** Profiles live in `./research-profiles/` at the cwd root — a sibling of `research/`, NOT inside it (so they are **not** caught by the anchored `/research/` ignore rule; they are committable in a private runs repo). Create it:

```bash
mkdir -p research-profiles
```

**Interpret `$ARGUMENTS`.** Decide the form first:

- **From-run** (starts with `from-run `) → go to **Step 1.6 (from-run mode)**.
- **Triple** (comma-separated 2–3 tokens) → parse into `role` / `domain` / optional `lens`, then go to Step 2 to build that one dossier. Valid roles: `methodologist`, `domain-expert`, `novelty-impact`, `feasibility`, `clarity`, `research-lead`. If the role is not one of these, or domain is missing, or the lens is ambiguous, ask the human a single clarifying question before proceeding. Derive a `{slug}` = `{role}--{domain}[--{lens}]` (lowercase, hyphenated).
- **Problem statement** (a sentence / contains `?` / clearly not a triple) → go to **Step 1.5 (suggest mode)**.
- **Empty** → ask the human which mode they want before proceeding.

---

## Step 1.5 — Suggest mode (problem statement → reviewed slate)

Analyze the problem and propose a slate of **2–4 profile candidates** as a small table — one row each, no searching yet:

```markdown
| # | role | domain | lens | why this lens (what it would catch on this problem) |
|---|------|--------|------|------------------------------------------------------|
| 1 | methodologist | statistics | bayesian | catches over-claimed frequentist significance in the directions |
| 2 | domain-expert | {domain} | {school of thought} | flags prior art the question reinvents |
```

Each lens is a **school of thought**, never a named living person — the no-real-personas rule applies here too. Derive role + domain + lens from the problem; favor lenses whose blind-spot coverage is complementary.

Present the slate and ask the human to **select all, some, or edit** entries (the human may rename a lens, drop a row, or add one). Nothing is grounded or saved yet — **the skill never spends search budget or saves anything without an explicit selection.**

For each **selected** candidate, derive its `{slug}` = `{role}--{domain}[--{lens}]` and build it **sequentially** through the existing flow: one Step-2 scout grounding run + one human-gated Step-4 save per dossier (the Step-4 diff-on-rerun rule still applies to any that already exist). Run them one at a time, not in parallel.

---

## Step 1.6 — From-run mode (existing run's corpus → dossier)

Build a dossier from an existing `/research` run's already-gated corpus instead of searching anew. The run folder is ephemeral; the dossier (and its works) persist — so this mode **copies**, never references the run.

1. **Resolve the run and the lens.** Parse `from-run <run-slug>[, role, domain, lens]`. Read `research/<run-slug>/sources.md` and `ls research/<run-slug>/sources/`. If the role/domain/lens were omitted, infer a candidate from the run's question and corpus and confirm it with the human in one line. Derive `{slug}` = `{role}--{domain}[--{lens}]`.
2. **Select the relevant corpus.** From the run's Accepted entries, pick the ones whose material grounds this dossier's lens — not the whole corpus, just the lens-relevant subset. The credibility gate is **inherited** from the run (those sources already passed Tier A/B/Reject); no new search, no re-gating.
3. **Copy the works.** `mkdir -p research-profiles/works/{slug}/` and copy each selected entry's local file (from `research/<run-slug>/sources/`) into it. Entries whose `Local:` is `none` stay citation-only. A run that predates the local library entirely (no `sources/` dir, no `Local:` fields) still works — every entry is citation-only and the dossier is built from `sources.md` alone; say so in the dossier draft.
4. **Draft from them** — go to Step 3 with this corpus in place of a fresh `.build/{slug}/` library; the dossier's frontmatter `grounded-in` notes `from run <run-slug>`. Then Step 4 (human review) and Step 5 (save) apply unchanged, except the works are already copied (skip the Step-5 copy).

No scout runs in this mode. Everything else — the human-gated save, the diff-on-rerun, the no-real-personas rule — is the same.

---

## Step 2 — Ground the dossier (ONE literature-scout)

Launch ONE `squid:literature-scout` with a tiny targeted plan inlined in the prompt — the scout's full credibility gate (Tier A/B/Reject, err toward Reject) applies:

```
Agent(
  subagent_type="squid:literature-scout",
  prompt="""Credibility-gated grounding for a profile dossier. Read {RESEARCH_DOC} (canonical research lifecycle) and the project's AGENTS.md (or CLAUDE.md, if present) first. Follow your role definition — your headline duty is the source-credibility gate.

  This is NOT a full /research run — there is no plan.md. Treat this inlined plan as your contract:
    Mode: targeted
    Question(s): the canonical writings, load-bearing commitments, and signature critiques of {lens} within {domain}; how this lens engages the rival camp's strongest arguments.
    Source strategy: peer-reviewed venues, well-known-lab technical reports, and named-expert blogs at respected orgs in {domain}.

  Working area: research-profiles/.build/{slug}/  (this lives OUTSIDE the git-ignored research/ folder — write your scratch and sources.md-style output HERE, not under research/). mkdir -p it. Your local library goes in research-profiles/.build/{slug}/sources/ (same fetch rules as a /research run).

  Run the search-as-code filtering pass, apply the Tier A/B/Reject gate (err toward Reject), fetch every accepted source into research-profiles/.build/{slug}/sources/ (Local: field per accepted entry), and write research-profiles/.build/{slug}/sources.md in your required shape — every Accepted source carries a Tier AND a one-line provenance line; every Reject is listed with a reason.

  Hand back: Tier-A / Tier-B counts, the local-library tally, and the path to sources.md."""
)
```

On return, **verify before drafting:** `research-profiles/.build/{slug}/sources.md` exists and matches the required shape; every Accepted source has a Tier + a provenance line. If credible coverage is thin, say so to the human and ask whether to proceed on a thinner base or refine the request.

---

## Step 3 — Draft the dossier

From the gated material, draft the dossier into the template below, writing its prose per `{STYLE_DOC}` (template-required frontmatter and headings are exempt). The **Key writings** section cites the gated sources with their tiers (load-bearing claims rest on Tier A; Tier B only with a caveat) and links each to its locally persisted copy under `research-profiles/works/{dossier-slug}/`. The dossier is a *lens*, not a literature review — keep each section tight.

**Special branch — `role: research-lead` (no lens):** write the **memory-file** shape instead (frontmatter + free sections for the user's accumulated preferences and per-run lessons). This is for when the user wants to *deliberately seed* `research-lead--memory.md`; normally that file accumulates after Gate #2 inside `/research`.

---

## Step 4 — Human reviews — persist NOTHING without approval

Mirror the self-improve discipline: present the drafted dossier, then wait. **Persist nothing without explicit approval.**

- **New dossier** → show the full draft; ask `save / edit / cancel`.
- **Re-run for an existing dossier** → read the current file, show a **diff** of the draft against it, and ask before overwriting. Never silently overwrite a dossier the user already reviewed.

---

## Step 5 — Save and clean up

On approval, write to `research-profiles/{role}--{domain}[--{lens}].md` (the memory-file shape goes to `research-profiles/research-lead--memory.md`). Set `updated:` to today. **Persist the Key-writings' local files** — copy the fetched files the dossier cites from the build library into the dossier's permanent works dir, so the dossier's `Local:` links resolve after the scratch is gone (profiles outlive runs, so the works are copied, not referenced into ephemeral storage):

```bash
# {dossier-slug} and {slug} are the same value: {role}--{domain}[--{lens}]
mkdir -p research-profiles/works/{dossier-slug}/
cp research-profiles/.build/{slug}/sources/<the Key-writings' files> research-profiles/works/{dossier-slug}/
rm -rf research-profiles/.build/{slug}/
```

Show the human exactly what was written and where (the dossier and its works dir).

---

## Dossier template (the save shape)

```markdown
---
role: methodologist | domain-expert | novelty-impact | feasibility | clarity | research-lead
domain: {e.g. statistics}
lens: {school of thought, e.g. bayesian}   # omit for the research-lead memory profile
grounded-in: {N Tier-A/B sources}{; from run <run-slug> if built via from-run mode}
updated: YYYY-MM-DD
---

# Profile — {role} · {domain} · {lens}

## Stance & commitments
{What this lens believes; its priors and load-bearing commitments — including how it engages the rival camp's strongest arguments.}

## Signature questions
- {the questions this lens always asks of a directions memo / synthesis}

## Failure modes it hunts
- {the specific defects this lens is tuned to catch}

## Key writings (credibility-gated)
- {citation} — Tier A|B — Local: works/{dossier-slug}/{file} — {one line: why it grounds this lens}

> NO real-researcher personas: this dossier encodes a school of thought, never a named living person.
```

---

## Notes on shape

- **Strictly additive.** Profiles are opt-in. `/research` works exactly as before when no dossier is attached; this skill only ever *creates* one for `/research` to layer on at launch.
- **Sharpen, never override.** A profile narrows *what a lens looks for* — it cannot change a reviewer's contract, the Severity Rule, or what counts as a Blocker.
- **Human-gated save.** Like self-improve, nothing is written without explicit approval, and a re-run shows a diff before overwriting.
- **Works are persistent.** A dossier stores its key writings locally under `research-profiles/works/{dossier-slug}/` (copied, not referenced) so the lens carries its grounding; `from-run` builds a dossier from an existing run's gated corpus with the gate inherited and the works copied out of the ephemeral run folder.
- **NO real-researcher personas.** Schools of thought only — never a named living person (privacy).
