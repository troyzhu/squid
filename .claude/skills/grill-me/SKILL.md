---
name: grill-me
description: Adversarially interview a feature spec before plan approval — surface every unresolved decision (auth model, error semantics, persistence, idempotency, observability, rollout, scope edges), draft codebase-grounded answers where possible, and ask the human only the questions that genuinely need their input. Output is a decision-resolved spec ready for PM grooming. Trigger when the user says "/grill-me", asks "is this spec ready", "poke holes in this", "interview me on this plan", or before invoking `/night` on a vague feature description.
disable-model-invocation: false
argument-hint: <feature-spec | path/to/spec.md | tracker-ref>
---

# Grill — adversarial Q&A on a spec, before the PM grooms it

`/night`'s plan-approval gate stops bad plans from running, but a vague spec produces a vague plan that *looks fine at the gate* and only explodes inside the inner loop on the third task. The cure is to harden the spec **before** PM grooming.

This skill takes a spec and an adversarial-but-fair posture: it surfaces every meaningful decision the spec leaves implicit, drafts a candidate answer when the codebase makes one obvious, and only asks the human the questions where their input is genuinely required. The output is a decision-resolved spec that goes to PM grooming with confidence.

You are the **interviewer** — you may delegate exploration to sub-agents, but the questions and the synthesis are yours. You do NOT change the spec's *intent*; you make its decisions explicit.

`$ARGUMENTS` is one of:

- A free-form feature description.
- A path to a markdown spec.
- A tracker reference.

If empty, ask the user for one.

## When to use

- Right before invoking `/night` on a non-trivial feature.
- When a spec has been bouncing around without consensus and the team can't tell what's blocking.
- After [`/refactor`](../refactor/SKILL.md) plan generation if the structural goal still feels under-specified.

## When NOT to use

- For a bug fix — use [`/triage-issue`](../triage-issue/SKILL.md), which has a tighter Q&A flow built in.
- For trivial features (≤ 1 task, ≤ 1 day of work). Grilling overhead exceeds the value.
- For exploratory / spike work where the *point* is to leave decisions open. Grilling kills exploration.
- After PM grooming. By then the decisions are baked into tasks; grilling now causes plan churn. Re-grill the spec, then re-groom from scratch if needed.

## Step 1 — Resolve the spec and read it carefully

Resolve `$ARGUMENTS` (same rules as `/triage-issue` and `/refactor`).

`Read` the spec end-to-end yourself — this is one of the rare skills where a sub-agent summary loses too much. Mark internally:

- Sentences that contain **modal verbs without specifics** ("should handle", "must support", "may need to").
- Nouns that hide a decision ("the user", "the database", "the API" — which one? when there are several?).
- Any list ending in "etc.".
- Any "for now" / "we'll figure out later" markers.

These are your raw question candidates. Don't surface them yet — go to Step 2 first.

## Step 2 — Reconnoitre the codebase

Spawn 1–2 Explore agents in parallel:

```
Agent(
  subagent_type="Explore",
  prompt="""Feature spec under review: {one-paragraph summary}.

  Find existing patterns I should reuse or be consistent with:
  (1) similar existing endpoints / commands / flows — file:line + 1-line shape;
  (2) the project's auth model (how is `current_user` propagated; where is it enforced);
  (3) the project's error-handling convention (exception types, HTTP error mapping, log shape);
  (4) the project's persistence layer (which datastore; where transactions are scoped; soft-delete or hard-delete);
  (5) the project's observability convention (logging style, metric/trace naming);
  (6) the project's feature-flag mechanism, if any.

  Report as six sections. Be concrete with file:line. If a category isn't present in the codebase, say so explicitly."""
)
```

The point is to **draft answers** before bothering the user. If the project clearly already has one auth model, "how is auth handled?" isn't a question for the user — it's a fact.

## Step 3 — Build the question matrix

Walk these dimensions for every spec. For each one, decide: (a) the spec already answers it; (b) the codebase implies the answer (you'll draft it); (c) the user must answer.

| Dimension | What to look for |
|---|---|
| **Scope edges** | What's explicitly OUT of scope? What's the smallest version that ships value? Is anything "phase 2" hiding inside phase 1? |
| **Inputs / outputs** | Exact shape of every API surface (HTTP, CLI, function signature). Validation rules. Error shape. |
| **Auth & authorisation** | Who can do this? How is identity established? What's the failure mode for unauthorised? |
| **Persistence & state** | What data is read / written / created / deleted? Transactional boundaries? Soft vs hard delete? Migrations needed? |
| **Idempotency & retries** | Is this safe to retry? Does it use idempotency keys? What happens on partial failure? |
| **Concurrency** | Two simultaneous calls — is that allowed? Does ordering matter? Locking strategy? |
| **Error semantics** | Recoverable vs not? User-visible message vs internal log? Should errors fail-open or fail-closed? |
| **Observability** | What's logged at success / failure? What metrics / traces / events fire? Is this on the existing dashboard? |
| **Performance / SLA** | Expected latency / throughput / load profile? Any back-pressure? Timeouts? |
| **Rollout** | Feature flag? Gradual rollout? Migration path for existing users / data? Rollback story? |
| **Backwards compatibility** | Existing callers / clients — do they break? Versioning required? |
| **Testing strategy** | Unit / integration / e2e split? Any external service that needs a fake / fixture? |
| **Documentation** | What docs / changelog / runbook entries does shipping this require? |
| **Security & privacy** | New attack surface? PII handling? Audit-log entries? Rate limiting? |

Not every dimension applies to every spec — discard the irrelevant ones explicitly with a one-line reason ("no persistence: this is a stateless transformation"). Don't pad the matrix.

## Step 4 — Draft and ask

For each dimension where the codebase implies an answer, **draft it**. Phrase as a statement followed by `(from: file:line)`:

> **Auth:** request requires an authenticated user; identity comes from `request.state.user` populated by the existing `AuthMiddleware` (`src/api/middleware/auth.py:34`). Unauthenticated requests get `401`. **Confirm or correct.**

For each dimension where the codebase doesn't decide and the spec doesn't either, **ask**. Use `AskUserQuestion`. Cap at 3–5 questions per round. If you have more, group / prioritise — the most blocking decisions go first. Re-run if needed; one grill round of 4 questions is much more productive than 12 questions in one wall.

Question shape:

```
header: "Auth model" (≤ 12 chars)
question: "Should this endpoint accept service-to-service tokens in addition to user sessions?"
options:
  - "User-only" — desc: "Reject anything that isn't a user session. Simpler; matches existing /api/* endpoints."
  - "Both, user preferred" — desc: "Accept both, but service tokens get a narrower scope. Matches /admin/* pattern."
  - "Service-only" — desc: "This is an internal endpoint; no human caller expected."
```

Show the codebase precedent inline so the user can choose by analogy, not by re-deriving.

## Step 5 — Synthesise the resolved spec

Update the spec (or write a sibling `*-grilled.md`) with every decision now explicit. Use this shape:

```markdown
# {Original feature title} — grilled

> Source: {original spec path or tracker ref}.
> Grilled on: {date}. Decisions below are explicit; PM grooming starts from this version.

## Goal (unchanged from source)

{copy from source}

## Scope

**In:** {explicit list}
**Out:** {explicit list}

## Decisions

### Auth & authorisation
{drafted statement, confirmed or corrected by user}

### Inputs / outputs
{...}

### Persistence
{...}

(... one section per dimension that applied ...)

## Open questions deferred to PM grooming

- {anything the user explicitly chose to defer — e.g., "exact rate-limit numbers: PM to propose during task decomposition"}

## Open questions NOT decided here

- {anything the user genuinely couldn't answer — surface so the PM grooming can flag and the human can revisit before plan approval. Empty list is fine.}
```

The "open questions deferred / NOT decided" sections are the receipts. They prevent PM grooming from inheriting silent ambiguity.

## Step 6 — Hand off

Single markdown block:

```markdown
## Grill complete — {feature title}

**Source spec:** {path or ref}
**Resolved spec:** {path or ref}

**Decisions made:** {N}
**Decisions deferred to PM:** {N}
**Decisions still open:** {N}  ← if > 0, list them inline.

### Recommended next step

{If "still open" is 0:}
`/night {resolved-spec-ref}` — the resolved spec is ready for PM grooming.

{If "still open" > 0:}
Resolve the remaining {N} open questions before invoking `/night`. Re-run `/grill-me` after, or update the resolved spec by hand.
```

## Notes on shape

- **Adversarial, not destructive.** The point is to harden the spec, not to argue it shouldn't ship. If you find the feature itself doesn't make sense, surface that as a single observation at the end — don't bury it in dimension-by-dimension nitpicks.
- **Drafted answers > questions.** Every decision the codebase already implies is a question you don't need to ask. Drafting first respects the user's time and produces consistency with the rest of the codebase as a side effect.
- **Cap question rounds.** 3–5 questions per `AskUserQuestion` round. One short round is more productive than one giant one. If the user is engaged, go a second round; don't try to hit it all in one wall of options.
- **One grill per spec.** Re-grilling drives consistency drift. If a spec needs grilling twice, it likely needed a different shape of grilling — try `/refactor` if it's actually a refactor in disguise, or escalate to a design conversation.
- **The codebase is the tie-breaker.** When the user is ambivalent ("either is fine"), pick whichever option matches existing patterns and note it ("chose `Both, user preferred` to match `/admin/*`"). Spec consistency compounds; spec inconsistency compounds harder.
- **No code, no plan.** Grill stops at the resolved spec. PM grooming (inside `/night`) decomposes into tasks. Don't pre-empt that step.
