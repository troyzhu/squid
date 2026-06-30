---
name: research-thread
description: "Codex adapter for Squid research-thread. Consolidate a finished research run into a wiki-ready thread note."
---

<!-- GENERATED — do not edit; run scripts/gen_codex.py -->

# Research Thread (Codex Adapter)

Use this adapter to run Squid's research-thread workflow in Codex.

1. Read `../../references/codex-adapter.md`.
2. Read the packaged canonical contract at `../../references/canonical/skills/research-thread/SKILL.md`.
3. Follow the canonical workflow after applying the adapter translation rules.
4. Apply the Codex-only article-mode overlay before the canonical template: the default thread should read like a high-quality expanded tutorial/blog article, not an audit ledger. Add `Prerequisites — a five-minute primer`, `Notation and key concepts`, and `Problem formulation` before `Findings`; move `Quality filter`/tier methodology to an end `Provenance (method note)` section; use `References` with a core-N must-trust list plus a scannable table rather than a tier-grouped per-paper bibliography as the main reading flow.
5. `Problem formulation` is mandatory in Codex output. It must state the motivation, the core question in words, the formal setup (variables, inputs, decisions, uncertainty, objective, constraints), why the problem is hard, and how the relevant literatures map onto the setup.
6. Write article-first: lead with intuition and concrete motivation before formalism, define key concepts inline, and organize findings as a narrative through-line. Avoid glossary-like enumeration; demote Tier A/B/C details to provenance/logging while preserving caveats at the point of use.
7. Update the wiki-editor lens accordingly: it must check digestibility as an article, the on-ramp, notation/key-concepts table, mandatory problem formulation, narrative coherence, and whether provenance/tier machinery stays out of the main reading flow. The source-fidelity lens remains strict: no new claims, no new search, citations resolve, and caveats are preserved.
8. Preserve the source-fidelity rule: introduce no new claims and run no new search.
9. Keep the wiki write boundary: write only to the run folder and never directly to the target wiki.
