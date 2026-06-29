# Research + Generated-Codex Integration — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Re-home the fork's research layer onto upstream's v0.4.4 composable-pipeline base and replace the three hand-maintained Codex mirrors with a single generator + CI drift-check.

**Architecture:** The branch `feat/research-codex-v2` already *is* `upstream/main` (v0.4.4). We add the 5 research agents + 4 research skills + 2 research docs (fixing their soft references to deleted skills), reconcile fork identity, then make every Codex artifact a deterministic derivative of `agents/` + `skills/` + `scripts/codex/config.yaml`, produced by `scripts/gen_codex.py` and enforced by CI.

**Tech Stack:** Markdown contracts (agents/skills), JSON manifests, TOML (Codex agents), Python 3 stdlib (the generator — recommended), GitHub Actions (drift-check). No build system for the markdown contract; the generator is dev tooling, the documented analog of `scripts/release.sh`.

## Global Constraints

- **Branch:** all work on `feat/research-codex-v2`. Never modify `main`, `origin/main`, or `upstream`. (verbatim from spec §3)
- **No push** of any commit until the human explicitly approves. (spec §2)
- **Fork identity:** `owner: troyzhu`, marketplace name `troyzhu`, install `squid@troyzhu`, plugin `source: "./"`, plugin `name: "squid"`. (spec §8)
- **Version:** `0.5.0` everywhere a version appears. (spec §8)
- **`AGENTS.md` ≤ 250 lines (invariant I2):** research rules stay in their own skills/docs, cross-referenced — never inlined into `AGENTS.md`. (spec §3)
- **Generated Codex files carry a `GENERATED — do not edit; run scripts/gen_codex.py` header and are never hand-edited.** (spec §7)
- **Generator is deterministic** (no timestamps/Date.now) so the CI `git diff` check is stable. (spec §7, §11)
- **Fail-loud:** any agent/skill without a config entry (or config entry without a file) → generator exits non-zero with a named error; never silently skip. *Good:* `ERROR: skill 'research-thread' has no codex config entry`. *Bad:* skipping it. (spec §7)
- **Dropped (recoverable):** do not carry `git-guardrails` or `write-a-skill`; both remain on `feat/research-layer`. (spec §9)

---

## File Structure

**Re-homed from `origin/feat/research-layer` (Tasks 1–2):**
- `agents/{research-lead,literature-scout,synthesizer,strategist,research-reviewer}.md` — the 5 research agents.
- `skills/{research,research-profile,research-thread,research-tutorial}/SKILL.md` — the 4 research skills.
- `docs/RESEARCH_PROCESS.md`, `docs/WRITING_STYLE.md` — research lifecycle + quality rubric.
- `docs/superpowers/plans/2026-06-*.md`, `docs/superpowers/specs/2026-06-{02,10,18}-*.md` — research design history.

**Edited in place (Tasks 3–4):**
- `skills/refactor/SKILL.md`, `skills/triage-issue/SKILL.md` — fix stale `docs/PROCESS.md` + "PM agent" refs.
- `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `AGENTS.md`, `README.md`, `scripts/release.sh` — fork identity + version.

**Re-homed + edited hand-written Codex scaffolding (Task 5):**
- `plugins/squid-codex/references/codex-adapter.md` — prose kept, agent-map table replaced by a generated-region marker.
- `plugins/squid-codex/.codex-plugin/plugin.json` — static fields kept; `version` + `interface.defaultPrompt` become generated.
- `.agents/plugins/marketplace.json` — static, re-homed as-is.
- `docs/CODEX.md` — human-facing Codex guide, updated for the new skill set + generator.

**Created — generator + outputs (Task 6, Codex-owned):**
- `scripts/codex/config.yaml` — the only hand-edited Codex metadata.
- `scripts/gen_codex.py` — the generator.
- `.github/workflows/codex-sync-check.yml` — drift-check.
- Generated: `.codex/agents/squid-*.toml`, `plugins/squid-codex/skills/*/SKILL.md`, `.agents/skills/*/SKILL.md`, the agent-map block in `codex-adapter.md`, `version`+`defaultPrompt` in the codex `plugin.json`.

---

## Task 1: Re-home the research layer files

**Files:**
- Create (via checkout from `origin/feat/research-layer`): the 5 agents, 4 skills, 2 docs, and design-history docs listed in File Structure.

**Interfaces:**
- Produces: research agents/skills/docs present on the branch, byte-identical to the fork, before any edits.

- [ ] **Step 1: Bring the research files onto the branch**

```bash
cd "/Volumes/External Drive/GitHub/squid"
git checkout origin/feat/research-layer -- \
  agents/research-lead.md agents/literature-scout.md agents/synthesizer.md \
  agents/strategist.md agents/research-reviewer.md \
  skills/research skills/research-profile skills/research-thread skills/research-tutorial \
  docs/RESEARCH_PROCESS.md docs/WRITING_STYLE.md \
  docs/superpowers/plans/2026-06-02-research-layer.md \
  docs/superpowers/plans/2026-06-18-research-thread-consolidation.md \
  docs/superpowers/specs/2026-06-02-research-layer-design.md \
  docs/superpowers/specs/2026-06-10-refresh-mode-and-linked-primers-design.md \
  docs/superpowers/specs/2026-06-10-research-depth-critic-rubric-design.md \
  docs/superpowers/specs/2026-06-18-research-thread-consolidation-design.md
```

- [ ] **Step 2: Verify the files are staged and the tree is sane**

Run: `git status --porcelain && ls agents/ skills/`
Expected: the 5 research agents + 4 research skill dirs appear; `git status` shows them staged as new (`A`).

- [ ] **Step 3: Validate the plugin still loads**

Run: `claude plugin validate`
Expected: PASS (no frontmatter/schema errors). If `claude` is unavailable, skip and note it.

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "feat(research): re-home research layer onto v0.4.4 base"
```

---

## Task 2: Fix the research layer's stale references

The re-homed files reference skills/agents that the v0.4.4 base renamed or replaced. Apply the mapping, then verify zero stale tokens remain.

**Files:**
- Modify: `skills/research/SKILL.md`, `docs/RESEARCH_PROCESS.md`, `agents/research-reviewer.md` (and any other re-homed file a grep flags).

**Interfaces:**
- Consumes: the files from Task 1.
- Produces: research handoff now points at `/plan` → `/implement-night`; analogies reference `product-architect` + `AGENTS.md`.

**Mapping (old → new):**

| Old token | New token | Meaning |
|---|---|---|
| `/grill-me docs/features/<slug>.md` (+ "harden the spec") | `/plan docs/features/<slug>.md` (grills + grooms into an approved Tasks Plan) | grilling is now Step 1 of `/plan` |
| `/night docs/features/<slug>.md` | `/implement-night` | monolith → pipeline orchestrator |
| `product-manager` (as engineering analog) | `product-architect` | upstream rename |
| `docs/PROCESS.md` | the engineering pipeline (`/plan` → `/implement-night`) defined in `AGENTS.md` | PROCESS.md deleted |
| `CLAUDE.md` (where it means "the project brief") | `AGENTS.md` | brief moved; CLAUDE.md is now a symlink |

- [ ] **Step 1: Rewrite the handoff block in `skills/research/SKILL.md`**

Find the recommended-next block (near line 526):

```
  Recommended next: /grill-me docs/features/<slug>.md   (harden the spec)
  then:              /night docs/features/<slug>.md      (build it)
```

Replace with:

```
  Recommended next: /plan docs/features/<slug>.md   (grill + groom into an approved Tasks Plan)
  then:             /implement-night                (build the approved plan end-to-end)
```

Also fix the two prose mentions:
- line ~503: `handoff (promote a direction to a /night feature spec)` → `handoff (promote a direction to a feature spec for /plan)`
- line ~598: `recommending /grill-me ... then /night` → `recommending /plan ... then /implement-night`

- [ ] **Step 2: Fix `docs/RESEARCH_PROCESS.md`**

- line 5: `the research-pipeline analog of \`docs/PROCESS.md\` (the engineering pipeline)` → `the research-pipeline analog of the engineering pipeline (the \`/plan\` → \`/implement-night\` skills, described in \`AGENTS.md\`)`
- line 48: `handoff → promote a direction to a /night feature spec` → `handoff → promote a direction to a feature spec for /plan`
- line 63: `\`CLAUDE.md\` + \`skills/research/SKILL.md\` | (night/day orchestrator)` → `\`AGENTS.md\` + \`skills/research/SKILL.md\` | (implement-night orchestrator)`
- line 64: `| product-manager |` → `| product-architect |`
- line 238: heading `## \`/night\` Handoff` → `## Engineering Handoff (\`/plan\` → \`/implement-night\`)`
- line 243: `\`/grill-me docs/features/<slug>.md\` (to harden the spec), then \`/night docs/features/<slug>.md\`` → `\`/plan docs/features/<slug>.md\` (grill + groom + approve), then \`/implement-night\``
- line 245: `it does not auto-invoke \`/night\`` → `it does not auto-invoke \`/plan\``

- [ ] **Step 3: Fix `agents/research-reviewer.md`**

- line 53: `Per \`docs/RESEARCH_PROCESS.md\` (the engineering Severity Rule in \`docs/PROCESS.md\`, adapted to research):` → `Per \`docs/RESEARCH_PROCESS.md\` (the engineering Severity Rule, adapted to research):`

- [ ] **Step 4: Grep-verify zero stale tokens remain in re-homed files**

Run:
```bash
grep -rnE '/night|/grill-me|/day\b|docs/PROCESS\.md|product-manager' \
  agents/research-lead.md agents/literature-scout.md agents/synthesizer.md \
  agents/strategist.md agents/research-reviewer.md skills/research* docs/RESEARCH_PROCESS.md docs/WRITING_STYLE.md
```
Expected: **no output** (exit 1). Any hit is a missed reference — fix it, then re-run. (If a hit is a genuine, intentional mention — e.g. explaining history — leave it and note why.)

- [ ] **Step 5: Validate + commit**

Run: `claude plugin validate` → PASS.
```bash
git add -A
git commit -m "fix(research): repoint handoff + analogies to v0.4.4 pipeline"
```

---

## Task 3: Fix the two stale upstream skills

Upstream left `skills/refactor` and `skills/triage-issue` pointing at the deleted `docs/PROCESS.md` and the renamed "PM agent". Fix them so the whole tree is internally consistent.

**Files:**
- Modify: `skills/refactor/SKILL.md`, `skills/triage-issue/SKILL.md`.

- [ ] **Step 1: Find every stale reference**

Run:
```bash
grep -rnE 'docs/PROCESS\.md|PM agent|product-manager|tracker/[0-9]' skills/refactor/SKILL.md skills/triage-issue/SKILL.md
```
Expected: several hits (the lines to fix).

- [ ] **Step 2: Apply fixes in both files**

- `docs/PROCESS.md` → `AGENTS.md` (the lifecycle now lives there).
- `PM agent` / `product-manager` → `product-architect` (or `PA`).
- Old tracker paths `tracker/NNN-<slug>.groomed.md` / `.todo.md` → the canonical `tasks/<NNN>-<slug>.md` with `status:` frontmatter (see `skills/scaffold/specs/tracker-workflow.md`).

- [ ] **Step 3: Grep-verify + validate**

Run the Step-1 grep again → **no output**. Then `claude plugin validate` → PASS.

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "fix(skills): repoint refactor + triage-issue off deleted PROCESS.md / PM"
```

---

## Task 4: Reconcile fork identity + version

Switch the manifests, brief, README, and release verify-URL from upstream identity (`iusztinpaul`, 0.4.4) to the fork (`troyzhu`, 0.5.0). Keep `name: "squid"`, `source: "./"`, and the three plugin dependencies.

**Files:**
- Modify: `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `AGENTS.md`, `README.md`, `scripts/release.sh:174`.

- [ ] **Step 1: `.claude-plugin/plugin.json`**

Set `"version": "0.5.0"`; `"homepage": "https://github.com/troyzhu/squid"`; extend `description` to mention the research layer (e.g. append `Adds a research agent-team (/research) and Codex support.`). Keep `name`, `dependencies`.

- [ ] **Step 2: `.claude-plugin/marketplace.json`**

- `"name": "troyzhu"`, `owner.name: "troyzhu"`.
- `metadata.version: "0.5.0"`, `metadata.description`: append research + Codex.
- `plugins[0].version: "0.5.0"`, `plugins[0].author`: `{ "name": "troyzhu", "url": "https://github.com/troyzhu" }`, `homepage`/`repository`: `https://github.com/troyzhu/squid`.
- Keep `plugins[0].source: "./"`, `allowCrossMarketplaceDependenciesOn`. Add keywords `research`, `codex`.

- [ ] **Step 3: `AGENTS.md` + `README.md`**

- Install handle: `/plugin marketplace add troyzhu/squid && /plugin install squid@troyzhu`.
- README: reframe as the fork — add a "Research layer" section (point to `docs/RESEARCH_PROCESS.md`) and a "Codex support" section (point to `docs/CODEX.md` + the `npx skills add troyzhu/squid` path). Keep ≤ the I2 spirit for AGENTS.md (don't inline research rules; link out).

- [ ] **Step 4: `scripts/release.sh`**

- Line 174: `iusztinpaul/squid/releases` → `troyzhu/squid/releases`.
- (The `must be on main` + `origin/main` sync logic stays — for the fork, `origin` is `troyzhu/squid`, which is correct.)

- [ ] **Step 5: Verify JSON parses + validate**

Run: `python3 -c "import json; json.load(open('.claude-plugin/plugin.json')); json.load(open('.claude-plugin/marketplace.json')); print('json ok')"` → `json ok`. Then `claude plugin validate` → PASS.

- [ ] **Step 6: Commit**

```bash
git add -A
git commit -m "chore(identity): reclaim fork identity (troyzhu) + bump to 0.5.0"
```

---

## Task 5: Re-home + update the hand-written Codex scaffolding

Bring over the *non-generated* Codex parts, updated for the new skill set, and insert the generated-region marker the generator will fill in Task 6.

**Files:**
- Create (checkout + edit): `plugins/squid-codex/references/codex-adapter.md`, `plugins/squid-codex/.codex-plugin/plugin.json`, `.agents/plugins/marketplace.json`, `docs/CODEX.md`.

- [ ] **Step 1: Bring the hand-written Codex files onto the branch**

```bash
git checkout origin/feat/research-layer -- \
  plugins/squid-codex/references/codex-adapter.md \
  plugins/squid-codex/.codex-plugin/plugin.json \
  .agents/plugins/marketplace.json \
  docs/CODEX.md
```

- [ ] **Step 2: Update `codex-adapter.md` prose + insert the agent-map marker**

- Replace the slash-command examples (`/day`, `/night`) with the new pipeline (`/plan`→`$plan`, `/implement-task`→`$implement-task`, `/implement-night`→`$implement-night`, `/review`, `/review-ci`).
- In "Claude-only persistence": **remove the `git-guardrails` bullet** (skill dropped); keep the `self-improve` bullet.
- Replace the entire "## Agent map" table (the markdown table rows) with:

```
## Agent map

<!-- BEGIN GENERATED:agent-map (scripts/gen_codex.py) — do not edit by hand -->
<!-- END GENERATED:agent-map -->
```

(The generator fills between the markers in Task 6.)

- [ ] **Step 3: Update `docs/CODEX.md`**

- Replace `$day`, `$night` examples with `$plan`, `$implement-night`, `$research`.
- Add a short "How Codex artifacts are produced" section: they are generated by `scripts/gen_codex.py` from `agents/`, `skills/`, and `scripts/codex/config.yaml`; never hand-edited; CI enforces sync. Include why + a good/bad example per the repo's rule: *Good:* "edit `skills/research/SKILL.md`, run `python3 scripts/gen_codex.py`, commit." *Bad:* "hand-edit `plugins/squid-codex/skills/research/SKILL.md`" (it will be overwritten and CI will fail).

- [ ] **Step 4: Note the soon-to-be-generated fields**

Leave `plugins/squid-codex/.codex-plugin/plugin.json` `version` + `interface.defaultPrompt` as-is for now; Task 6's generator overwrites them. Add a top-of-file note is not possible in JSON — instead document in `docs/CODEX.md` that those two fields are generated.

- [ ] **Step 5: Validate + commit**

Run: `claude plugin validate` → PASS (the codex sub-plugin is not a Claude plugin, but the root must still validate). JSON parse-check `.agents/plugins/marketplace.json` + the codex `plugin.json`.
```bash
git add -A
git commit -m "feat(codex): re-home hand-written Codex scaffolding + agent-map marker"
```

---

## Task 6 — [CODEX-OWNED]: Build the Codex generator (single source of truth)

> **Hand this task to Codex.** It is the self-contained build doc the human asked for. Codex implements the generator that produces the artifacts it will itself run under. Recommended language: Python 3 stdlib (no third-party deps). Codex may choose otherwise but must keep it dependency-free and deterministic.

**Files:**
- Create: `scripts/codex/config.yaml`, `scripts/gen_codex.py`, `.github/workflows/codex-sync-check.yml`.
- Modify (generated regions only): `scripts/release.sh`.
- Generated outputs (the generator writes these): `.codex/agents/squid-*.toml`, `plugins/squid-codex/skills/*/SKILL.md`, `.agents/skills/*/SKILL.md`, the agent-map block in `codex-adapter.md`, and `version`+`interface.defaultPrompt` in the codex `plugin.json`.

**Enumeration (the generator must cover exactly these):**
- **Agents (10):** `product-architect`, `software-engineer`, `tester`, `pr-reviewer`, `oncall-engineer`, `research-lead`, `literature-scout`, `synthesizer`, `strategist`, `research-reviewer`.
- **Skills (16):** `scaffold`, `plan`, `implement-task`, `implement-night`, `review`, `review-ci`, `grilling`, `testing-python`, `self-improve`, `refactor`, `triage-issue`, `architecture-review`, `research`, `research-profile`, `research-thread`, `research-tutorial`. (A skill may set `codex: false` in config to be skipped — e.g. `testing-python` if it should not be a `$`-invocable Codex skill.)

### Step 1: Write `scripts/codex/config.{toml,json,yaml}`

**Config format is Codex's choice, but stay dependency-free** (Global Constraints): prefer `config.toml` (stdlib `tomllib`, Python 3.11+) or `config.json` (stdlib `json`, any version). YAML is allowed only if Codex accepts the one `pyyaml` dependency (then the CI step keeps `pip install pyyaml`). The schema below is shown in YAML for readability; translate field-for-field to the chosen format.

Schema (one entry per agent and per skill above):

```yaml
# scripts/codex/config.yaml
# Codex-specific metadata. The ONLY hand-edited Codex input besides agents/ and skills/.
# gen_codex.py fails if any agent in agents/ or skill in skills/ lacks an entry here,
# or if an entry names a file that doesn't exist.

agents:
  <slug>:
    title: "<Title Case role name>"     # → "You are the Squid <title> role in Codex."
    description: "<one line>"            # → TOML description; first sentence of the agent's role summary
    guardrail: "<one sentence or ''>"    # role's 'stay in your lane' rule; '' omits it
    nicknames: ["...", "...", "..."]

skills:
  <slug>:
    title: "<Title Case skill name>"
    blurb: "<short purpose phrase>"      # → stub descriptions
    codex: true                          # optional; false = skip generating Codex artifacts for this skill
    extra_steps: []                      # optional adapter steps appended after step 3 (numbered from 4)
    default_prompt: "<one line or omit>" # if present, included in plugin.json interface.defaultPrompt
```

**Verbatim worked entries (copy exactly — these match the existing artifacts):**

```yaml
agents:
  tester:
    title: "Tester"
    description: "Squid tester: verifies implementation work, acceptance criteria, and adversarial end-to-end behavior."
    guardrail: "Your core duty is evidence-backed verification, not rubber-stamping."
    nicknames: ["QA", "Verifier", "Tester"]
  research-reviewer:
    title: "Research Reviewer"
    description: "Squid research reviewer: runs one assigned review lens over synthesis or directions."
    guardrail: "Stay within the single review lens assigned in your prompt and do not revise the artifact yourself."
    nicknames: ["Reviewer", "Panelist", "Critic"]
  product-architect:
    title: "Product Architect"
    description: "Squid product architect: grooms tasks, owns ADRs + glossary, and runs user-perspective acceptance review."
    guardrail: "You author ADRs and the glossary; others read them. Decide what to build, not how to write the code."
    nicknames: ["PA", "Architect", "Acceptance"]

skills:
  research:
    title: "Research"
    blurb: "credibility-gated research planning, sourcing, synthesis, strategy, review, and handoff"
    extra_steps:
      - "Prefer the research custom agents from `.codex/agents`; otherwise spawn regular Codex workers with the matching `agents/` role contract included."
    default_prompt: "Use $research to map credible approaches."
  scaffold:
    title: "Scaffold"
    blurb: "bootstrap a new repo or component from the Squid spec library"
    extra_steps:
      - "Generate `AGENTS.md` as the canonical project brief. Generate a one-line `CLAUDE.md` pointer only because scaffolded projects are intended to work with both Claude Code and Codex."
    default_prompt: "Use $scaffold to bootstrap a new service."
  plan:
    title: "Plan"
    blurb: "turn a feature spec into an approved Tasks Plan"
    default_prompt: "Use $plan to groom a feature into an approved Tasks Plan."
```

For the remaining agents and skills, derive each field mechanically from the canonical contract: `title` = Title Case of the slug; `description` = the lead sentence of the agent's role summary (or `Codex adapter for Squid <slug>.` for skills); `guardrail` = the agent's one-line lane rule, or `''` if none; `blurb` = the skill's one-line purpose. Provide `default_prompt` for **exactly three** skills (`scaffold`, `plan`, `research`) and omit it elsewhere. `extra_steps` only where the old adapter had a step 4 (today: `research`, `scaffold`).

### Step 2: Write `scripts/gen_codex.py`

Behavior:
1. Read root version from `.claude-plugin/plugin.json` (`version`).
2. List `agents/*.md` (slug = filename without `.md`) and `skills/*/` (slug = dir name).
3. Load `scripts/codex/config.yaml`. **Fail-loud:** if any listed agent/skill lacks a config entry, or a config entry names a missing file, `print` a named error to stderr and `sys.exit(1)`.
4. For each agent, write `.codex/agents/squid-<slug>.toml` from the **TOML template** below.
5. For each skill with `codex` not `false`, write both `plugins/squid-codex/skills/<slug>/SKILL.md` (**adapter template**) and `.agents/skills/<slug>/SKILL.md` (**discovery template**).
6. Replace the agent-map block in `plugins/squid-codex/references/codex-adapter.md` between the `<!-- BEGIN GENERATED:agent-map ... -->` / `<!-- END GENERATED:agent-map -->` markers with one row per agent (**agent-map row template**).
7. In `plugins/squid-codex/.codex-plugin/plugin.json`: set `version` = root version, and `interface.defaultPrompt` = the list of `default_prompt` strings (in config order). Preserve all other keys + key order (round-trip with `json.load`/`json.dump`, `indent=2`, trailing newline — mirror `release.sh` lines 130–139).
8. Be **idempotent and deterministic**: stable ordering (sort slugs), no timestamps, trailing newline on every file.

**TOML template** (`.codex/agents/squid-<slug>.toml`) — note the literal `GENERATED` header comment:

```
# GENERATED — do not edit; run scripts/gen_codex.py
name = "squid-{slug}"
description = "{description}"
developer_instructions = """
You are the Squid {title} role in Codex.

Before acting, read `AGENTS.md` if present, then read
`plugins/squid-codex/references/codex-adapter.md` if present, then read the
canonical role contract at `agents/{slug}.md`.

Follow the canonical contract after translating Claude-specific references into
Codex equivalents. Prefer `AGENTS.md` for project guidance; read `CLAUDE.md` only
as fallback context or when the user asks about Claude behavior.{guardrail_clause} If the canonical contract
is missing, report that blocker instead of inventing the role.
"""
nickname_candidates = [{nicknames}]
```
where `{guardrail_clause}` = a leading space + `{guardrail}` when non-empty, else empty; `{nicknames}` = comma-joined quoted strings.

**Adapter template** (`plugins/squid-codex/skills/<slug>/SKILL.md`):

```
---
name: {slug}
description: Codex adapter for Squid {slug}. {blurb_capitalized}.
---

<!-- GENERATED — do not edit; run scripts/gen_codex.py -->

# {title} (Codex Adapter)

Use this adapter to run Squid's {slug} workflow in Codex.

1. Read `../../references/codex-adapter.md`.
2. Read the canonical contract at `../../../../skills/{slug}/SKILL.md`.
3. Follow the canonical workflow after applying the adapter translation rules.
{extra_steps_numbered_from_4}
```

**Discovery template** (`.agents/skills/<slug>/SKILL.md`):

```
---
name: {slug}
description: "Repo-local Codex entry point for Squid {slug}: {blurb}."
---

<!-- GENERATED — do not edit; run scripts/gen_codex.py -->

# {title}

Read and follow `../../../plugins/squid-codex/skills/{slug}/SKILL.md`.
```

**Agent-map row** (one per agent, inside the markers):

```
| `squid:{slug}` | `squid-{slug}` | `agents/{slug}.md` |
```
preceded once by the header rows:
```
| Claude role | Codex custom agent | Canonical contract |
|---|---|---|
```

### Step 3: Generate + verify idempotency

- [ ] Run `python3 scripts/gen_codex.py`.
- [ ] Run it **again**; `git diff --exit-code` must be clean (idempotent). Expected: no diff on the second run.
- [ ] Delete one generated file (e.g. `rm .codex/agents/squid-tester.toml`), re-run, confirm it is restored byte-identical (`git status` clean).
- [ ] Confirm **no** `.codex/agents/squid-product-manager.toml`, and **no** `plugins/squid-codex/skills/{day,night,grill-me,create-pr,write-a-skill}/` exist (the rename/drops took effect). Confirm `.agents/skills/research-thread/` now exists (the old drift is gone).
- [ ] TOML/JSON sanity: `python3 -c "import tomllib,glob;[tomllib.load(open(f,'rb')) for f in glob.glob('.codex/agents/*.toml')];print('toml ok')"` → `toml ok`.

### Step 4: Add CI drift-check `.github/workflows/codex-sync-check.yml`

```yaml
name: codex-sync-check
on: [push, pull_request]
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install pyyaml
      - run: python3 scripts/gen_codex.py
      - name: Fail if Codex artifacts are out of sync
        run: git diff --exit-code || (echo "::error::Codex artifacts stale — run scripts/gen_codex.py and commit." && exit 1)
```
(If the generator avoids PyYAML by parsing the small config with stdlib, drop the `pip install` line.)

### Step 5: Wire `scripts/release.sh`

Insert, **after** the `PYEOF` block that writes the new version (after line 139) and **before** `git add "$MANIFEST"` (line 143):

```bash
# regenerate Codex artifacts so their version matches the release
python3 scripts/gen_codex.py
```
And change the staging line so the regenerated artifacts are committed:
```bash
git add "$MANIFEST" .codex plugins/squid-codex .agents/skills
```

### Step 6: Commit (Codex)

```bash
git add -A
git commit -m "feat(codex): single-source-of-truth generator + CI drift-check"
```

---

## Task 7: End-to-end validation

**Files:** none (verification only).

- [ ] **Step 1: Manifest validation**

Run: `claude plugin validate`
Expected: PASS for the root `squid` plugin.

- [ ] **Step 2: Generator idempotency (clean tree)**

Run: `python3 scripts/gen_codex.py && git diff --exit-code`
Expected: clean (exit 0).

- [ ] **Step 3: No stale references anywhere**

Run:
```bash
grep -rnE '/night\b|/grill-me\b|/day\b|docs/PROCESS\.md|product-manager|squid@iusztinpaul' \
  agents skills docs README.md AGENTS.md plugins .codex .agents 2>/dev/null | grep -v 'docs/superpowers/'
```
Expected: no output (history docs under `docs/superpowers/` are exempt — they record the past intentionally).

- [ ] **Step 4: `/scaffold` dry-run**

In an empty scratch dir, run `/scaffold` and confirm it produces a sensible `AGENTS.md` + one-line `CLAUDE.md` pointer and skeleton tree, writing **no** application source. (Manual; note the result.)

- [ ] **Step 5: Research handoff resolves**

Confirm `skills/research/SKILL.md` now recommends `/plan` + `/implement-night`, and both skills exist (`ls skills/plan skills/implement-night`).

- [ ] **Step 6: Final summary to the human**

Report: branch state (`git log --oneline upstream/main..HEAD`), what changed, what stayed on `feat/research-layer`, and that **nothing was pushed**. Ask whether to (a) push the branch to `origin`, (b) open a PR on the fork, or (c) leave local.

---

## Self-Review (completed by plan author)

- **Spec coverage:** §4 strategy = the branch base (done pre-plan); §5 base fixes = Task 3; §6 research re-home = Tasks 1–2; §7 Codex generator = Task 6; §8 identity/version = Task 4; §9 dropped skills = Global Constraints + Task 6 enumeration (excludes them); §11 validation = Task 7. All covered.
- **Placeholder scan:** config values for non-worked entries use an explicit mechanical derivation rule + full enumeration (not "TODO"); all templates are literal.
- **Type/name consistency:** slugs used identically across config schema, templates, enumeration, and the agent-map row. Generated path set matches across Tasks 5–7.
- **Open dependency:** Task 6 is Codex-owned; Tasks 1–5 + 7 are Claude-owned and can land first (the CI check from Task 6 only goes green once the generator exists).
