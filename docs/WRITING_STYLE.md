# Writing Style

This is the prose contract for research **run artifacts**: the free prose of `synthesis.md`, `directions.md`, and profile dossiers. It governs how those documents read, not what structure they carry. It does not govern the plugin's own internal contract files (no existing file's voice gets rewritten to satisfy it), and it does not touch template-required structure. Required labels and headings such as `Status:`, `Derivation:`, `Confidence:`, `Tier:`, the `A1 —` ids, and the fixed section headings are exempt from every decoration limit below; write them as the templates specify. The orchestrator prefers a project-local `docs/WRITING_STYLE.md` over the plugin copy, so a project can tune taste without editing the plugin. If no copy is reachable, or no lint tooling is at hand, writers fall back to judgment under the rules stated here.

This file describes patterns by quoting them — the citation-form paragraph in "The register", the math and foldable-callout examples in "Technical content and math", the banned-phrase example in "The tutorial register", and the "Banned constructions" and "The lint" sections. Those quoted forms, the example callout and its LaTeX, and the regexes are reference material; they are exempt from matching themselves when the lint runs against this file.

## The register

Write technical exposition, closer to lecture notes than a blog post. Lead with the claim, give the evidence, then state the implication, in that order. State the formal object and move on. Cut connective narration. Prefer an equation or a definition to a paragraph when that is the precise statement, and write the equation as math (see the next section). Use plain declarative sentences with natural length variation. Prefer precise nouns over vague ones. Keep most verbs active. Give numbers their units. Treat the paragraph as the default unit of thought, and reach for a list or a table only when the content is genuinely a list or a table.

State conclusions directly. When uncertainty matters, say it once, plainly. The pipeline already carries the epistemics in its own fields: Tier A and Tier B on sources, and a Confidence on each Analysis item. Prose that hedges on top of those tags adds noise, so let the tags do that work and keep the sentence clean.

Open every section with its conclusion in one plain sentence, then give the argument that earns it. This is the bottom-line-up-front rule, applied at the section level: the reader learns the takeaway before the evidence, not after. Hold no suspense across sections either; a section is a unit of answer, not a chapter in a mystery.

Cite claims inline by source id alone: `[S11]`, or `[S11][S20]` for several. The tier lives in the sources ledger, so the inline mark stays out of the reader's way. One exception earns an inline tier: a claim that leans on a Tier-B source keeps an explicit `[S22, B]` wherever it rests on it, because that caveat is load-bearing and the reader needs it at the point of use. Analysis items cite the same way, `[A2]`.

Use American English spelling and usage throughout: optimize over optimise, behavior over behaviour, modeling over modelling, analyze over analyse, center over centre. Preserve the original spelling inside quoted material and cited source titles; do not Americanize a paper's title.

## Technical content and math

For technical material this raises the floor on substance. The top-level prose stays plain under the register above, the key equation stays visible, and the heavy derivation folds away. A wall of unbroken math is not the goal, but neither is brevity (see the Quality rubric's "length matched to depth"). This section defines the two mechanics the rubric's "derive, don't assert" leans on: writing math as math, and folding the heavy parts.

Write math as math. Inline math is `$\ldots$` (`$e^{-\Delta E/T}$`, `$T$`, `$\Delta E$`); display math is `$$\ldots$$` on its own lines with a blank line before and after, so Obsidian renders it. Do not render a formula as prose-ASCII when the formula is the precise statement: "take it with probability $e^{-\Delta E/T}$", not "take it anyway with probability exp(minus delta-E over T)".

Fold the heavy parts. Put an extended derivation, a proof, or optional deep math in an Obsidian foldable callout, collapsed by default, so the linear read stays light and the rigor is one expand away. The load-bearing equation itself stays visible inline or displayed; only the long derivation folds.

```
> [!derivation]- Why the cold limit samples the Boltzmann distribution
>
> At fixed $T$, the accept rule satisfies detailed balance with $\pi(x)\propto e^{-E(x)/T}$:
> $$ \pi(x)\,q(x\to y)\,\min\!\big(1,e^{-\Delta E/T}\big) = \pi(y)\,q(y\to x)\,\min\!\big(1,e^{+\Delta E/T}\big) $$
> so $\pi$ is stationary, and as $T\to 0$ it concentrates on $\arg\min E$.
```

The trailing `-` after `[!derivation]` collapses the block by default; `+` would open it. Each content line is `> `-prefixed. The label may be `[!derivation]`, `[!proof]`, `[!math]`, or `[!note]`. These callouts, and inline/display math, are exposition rather than prose, so the lint exempts them.

## Structure for long-form artifacts

A deep artifact stays digestible by being navigable, not by being short. Length is matched to the topic; the reader is carried through it by the doc-level scaffolding below. The model for the whole shape is the user's `GRPO_empirical` handbook: a stated job and central claim up front, a clickable table of contents, a notation table, and heavy derivations folded out of the linear read.

Open with a doc-level BLUF: one paragraph stating what the artifact covers and its central takeaway, before the first section. This is the section-level BLUF rule raised to the document — the reader learns the destination before the journey.

Then give a **Table of contents** as a list of Obsidian heading wikilinks, so a reader jumps to any section.

```
## Table of contents
- [[#Notation]]
- [[#The mechanism]]
- [[#Comparison with alternatives]]
```

Each `[[#Section name]]` links the heading of that exact name in the same file. The TOC is reference scaffolding, not prose; like a list it is lint-exempt (the `-` lines are dropped before counting).

When the artifact is math-heavy, add a **Notation** section: a `| Symbol | Meaning |` table that defines each symbol once, used consistently throughout. `GRPO_empirical`'s Notation table is the model — every symbol the derivations use is pinned there before Part I, so no later equation introduces an undefined symbol. The Notation table is reference material and, being a table, is lint-exempt.

```
## Notation
| Symbol | Meaning |
|---|---|
| $T$ | Temperature; the control parameter the schedule lowers. |
| $\Delta E$ | Change in the objective between the current and proposed state. |
```

These three (doc-level BLUF, table of contents, Notation table) are the scaffolding the rubric's "length matched to depth" relies on: they let an artifact grow to the depth a topic needs while still reading as navigable rather than as a wall. A future writer extending a deep topic adds sections and folds the heavy math.

## Quality rubric

This is the checklist the depth critic and the reviewers score a draft against. It is the one home for the depth and quality bar; the sections above and the agents reference it rather than re-state these requirements. Each item is one checkable property.

- **Show, don't name.** A load-bearing mechanism component is shown concretely — instantiated across 2–3 representative settings, with its formal conditions — not merely named. (A proposal/transition step shows how the next state is actually generated, the symmetry condition and the correction when it fails, and the named family the method instances.)
- **Derive, don't assert.** A load-bearing result a technical reader would question is derived, the steps written as display math, with heavy derivations folded into a collapsed derivation callout (see "Technical content and math").
- **Compare and place.** A concept is set against its competitive and related methods with a comparison table and a grounded, when-each-is-preferred discussion (full-depth tutorials also ship the companion methods-map).
- **Worked examples are stepped, visual, and runnable.** Terse `Step N` equation-forward steps; an inline visual (Mermaid, an ASCII sketch, or a trajectory/values table); a foldable runnable snippet when the process is dynamic.
- **Functional output.** Every reference, DOI, arXiv id, URL, and `Local:` path is a clickable markdown link (`[doi:10.1126/x](https://doi.org/10.1126/x)`, `[arXiv:2203.02201](https://arxiv.org/abs/2203.02201)`, `[S28--kirkpatrick.pdf](sources/S28--kirkpatrick.pdf)`); a long artifact carries a working `[[#anchor]]` table of contents; a math-heavy one carries a Notation table.
- **Length matched to depth.** Digestibility is navigability and folding, not brevity.
- **Inherited (defined elsewhere, not restated here):** typeset math and foldable proofs (see "Technical content and math"); slim `[S#]` citations and American English (see "The register"); the anti-tic limits (see "Hard limits on decoration"); the long-form scaffolding (see "Structure for long-form artifacts").

## The tutorial register

Primers (`/research-tutorial`) are pedagogical, so they carry two register allowances beyond the synthesis prose. A worked example may use whatever structure it needs to be walked, and the **Key terms** section is a genuine definitional list whose colon form is exempt from the colon limit. Instructional second person is also fine — "you cool the temperature each step" teaches a procedure and is not the banned rhetorical address ("you might wonder"). Everything else in the contract still applies: BLUF, slim `[S#]` citations, the dash and bold limits, the banned constructions, and the paragraph budget.

A primer on a mathematical method also meets the Quality rubric: its defining equation as math, its central result derived (folded when heavy), its worked example run through the typeset formula. A technically-thin primer that omits the key equation or the central derivation, or paraphrases the math in prose, is incomplete.

## Hard limits on decoration

Each limit has its reason in the same line.

Dashes: prefer a comma, a parenthesis, or two sentences, because a page of em-dashes reads as one breathless thought. The lint sets a budget.

Bold: use it for a term's first definition and for template-required labels, nothing else, because bold used for emphasis stops meaning anything once it is everywhere.

Italics: rare, for a foreign term or a genuine contrast, because italics for emphasis decay the same way bold does.

Colons: use them for a true list or a definition, because a colon that introduces a full sentence is usually a paragraph wearing a costume. Do not build "Label: sentence" bullet chains in place of paragraphs. Template labels are exempt.

Bullets: use them only for genuinely parallel, enumerable items. When the items carry internal logic or flow into each other, write a paragraph instead. Reserve tables for real comparisons across a shared set of dimensions.

Headings: write them as noun phrases. No question headings, no cliffhangers, because a heading is a label, not a hook.

Paragraphs: one idea each, because a paragraph that carries three ideas reads as none. The soft budget is about 120 words; above 160 the lint breaches, so split it. This is a **per-paragraph** rule, not a cap on the document: a deep topic earns many paragraphs, and length is controlled by navigability and folding (see "Structure for long-form artifacts"), never by truncating the analysis. Template blocks, tables, and the evidence ledger are exempt.

Exclamation marks: none, because technical prose earns attention with content.

## Banned constructions

These patterns read as machine-written or as filler. Avoid each one.

The "not just X, but Y" frame and its variants, including "isn't just" and "more than just".

The openers "Here's the thing", "Here's why", and "Here's how".

The invitations "Let's dive in", "dive into", and "delve".

The phrase "The real question is".

Suspense reveals such as "But here's where it gets interesting".

Filler intensifiers used to open a sentence, including "Crucially", "Importantly", "Notably", and "It's worth noting".

Direct address to the reader as a rhetorical move, such as "you might wonder" or "you may be asking".

Hype vocabulary, including "game-changing", "unlock", "harness", "navigate the landscape", and "in today's fast-paced".

Rule-of-three padding, meaning a tricolon used for rhythm rather than content.

## The lint

The writer runs this from the artifact's directory before hand-off. POSIX shell or `python3` is fine, whichever is at hand. The regexes below are normative; the implementation around them is not. Run the counts against the artifact's prose and compare to the thresholds.

```sh
# Run from the artifact's directory, e.g. against synthesis.md.
# Strip template-required labels and headings before counting where a rule says so.
F=synthesis.md

# The prose-only view P drops callout/blockquote lines (^\s*>), removes multi-line
# $$ … $$ display blocks, then strips single-line $$…$$ and inline $…$ math, so a
# \Delta, a \min\!, or a ** inside math or a callout never counts as prose. The
# decoration checks 1-3 AND the prose-content checks 4 and 6 all run on P. (Artifacts
# keep '$' balanced — escape a literal dollar as \$ — so the delimiters pair correctly.)
P=$(awk '
  /^[[:space:]]*\$\$[[:space:]]*$/ { m = !m; next }   # toggle on a lone $$ delimiter line
  m { next }                                          # inside a multi-line display block
  /^[[:space:]]*>/ { next }                           # callout / blockquote line
  { print }
' "$F" | sed -E 's/\$\$[^$]*\$\$//g; s/\$[^$]*\$//g')

# 1. em-dash density: > 1 per 1000 chars of prose => breach
chars=$(printf '%s' "$P" | wc -m)
dashes=$(printf '%s' "$P" | grep -o '—' | wc -l)

# 2. bold spans, excluding template-required labels/headings: > 6 per 1000 words => breach
words=$(printf '%s' "$P" | wc -w)
bold=$(printf '%s' "$P" | grep -oE '\*\*[^*]+\*\*' | wc -l)   # subtract known template labels

# 3. label-colon bullets outside template structures: > 2 per artifact => breach
labelcolon=$(printf '%s' "$P" | grep -cE '^\s*-\s+\*\*[^*]+:\*\*')

# 4. banned constructions (case-insensitive), on the prose-only view: any hit => breach
printf '%s\n' "$P" | grep -niE 'not just [^,]+, but|isn'\''t just|more than just|here'\''s (the thing|why|how)|let'\''s dive|dive into|delve|the real question is|here'\''s where it gets|^\s*(crucially|importantly|notably|it'\''s worth noting)|you might wonder|you may be asking|game-changing|unlock|harness|navigate the landscape|in today'\''s fast-paced'

# 5. question headings: any => breach
grep -nE '^#{1,6}\s.*\?\s*$' "$F"

# 6. exclamation marks in prose (on the prose-only view, so callout titles and \! don't count): any => breach
printf '%s\n' "$P" | grep -nE '!'

# 7. citation clusters: any sentence with 3+ [S.../[A... bracket groups => breach
# 8. paragraph length: any prose paragraph > 160 words => breach
#   both split on real boundaries; skip template blocks, tables, the ledger, callouts,
#   and display-math blocks (math and folds are exposition, not prose paragraphs).
python3 - "$F" <<'PY'
import re, sys
text = open(sys.argv[1]).read()
group = re.compile(r'\[[SA]\d')
in_math = False
for para in re.split(r'\n\s*\n', text):
    s = para.strip()
    if in_math:                        # inside a multi-paragraph display block
        if s.endswith('$$'):
            in_math = False            # its closing delimiter
        continue
    if s.startswith('$$'):             # a display-math paragraph
        if s == '$$' or not s.endswith('$$'):
            in_math = True             # opens a multi-paragraph block; skip until it closes
        continue                       # a self-contained $$ … $$ paragraph: skip, no toggle
    if not s or s.startswith(('|', '#', '```', '-', '>', '$')):
        continue                       # tables, headings, fences, lists, callouts, math
    if len(s.split()) > 160:
        print("8 paragraph >160 words:", s[:60], "…")
    for sent in re.split(r'(?<=[.!?])\s+', s):
        if len(group.findall(sent)) >= 3:
            print("7 citation cluster:", sent[:80], "…")
PY

# 9. bare reference links: a doi:/arXiv: (case-insensitive) or a bare http(s):// URL that is
#    NOT inside a markdown link [...](...) won't be clickable => breach. Runs on the file with
#    fenced ``` blocks stripped (NOT the prose-only view P — bare links can live in tables, lists,
#    and the evidence ledger). Strip code fences, drop the [text](url) link constructs so any
#    token inside a link disappears, then any doi:/arXiv:/http(s):// left in the residue is bare.
awk 'BEGIN{f=0} /^[[:space:]]*```/{f=!f; next} !f{print}' "$F" \
  | sed -E 's/\[[^]]*\]\([^)]*\)//g' \
  | grep -niE 'doi:|arxiv:|https?://'
```

Thresholds, per artifact. Checks 1-3 and the paragraph/citation checks run on prose only: inline `$…$` and display `$$…$$` math is stripped first, and callout/blockquote lines (`^\s*>`) and display-math blocks are dropped, so math and folds never count as decoration or as a paragraph.

- em-dash (`—`) density: more than 1 per 1,000 characters of prose is a breach.
- bold spans (`\*\*[^*]+\*\*`), excluding template-required labels and headings: more than 6 per 1,000 words is a breach.
- label-colon bullets (`^\s*-\s+\*\*[^*]+:\*\*`) outside template-required structures: more than 2 per artifact is a breach.
- banned-construction regex list: any hit is a breach.
- question headings (`^#{1,6}\s.*\?\s*$`): any is a breach.
- exclamation marks in prose: any is a breach.
- citation clusters: any sentence carrying 3 or more `[S…`/`[A…` bracket groups is a breach.
- paragraph length: any prose paragraph over 160 words is a breach (template blocks, tables, the ledger, callouts, and display-math blocks exempt).
- bare reference links: any reference identifier or raw web link (the forms the check 9 regex names) sitting outside a markdown link `[...](...)` is a breach, because it won't be clickable — the rubric's "functional output" rule. This one check runs on the whole file with code fences stripped, not the prose-only view, since references live in tables, lists, and the ledger.

Append a small counts table to the writer's `log.md` entry:

```markdown
| check | count | threshold | breach |
|---|---|---|---|
| em-dash / 1k chars | … | 1 | … |
| bold / 1k words | … | 6 | … |
| label-colon bullets | … | 2 | … |
| banned constructions | … | 0 | … |
| question headings | … | 0 | … |
| exclamation marks | … | 0 | … |
| citation clusters | … | 0 | … |
| paragraph > 160 words | … | 0 | … |
| bare reference links | … | 0 | … |
```

Any breach means revise before hand-off, then re-run. The lint is deterministic and auditable, the same philosophy as the credibility gate's search-as-code.

## Severity for the clarity reviewer

The clarity reviewer enforces this contract; the other four roles ignore style. A breach the writer shipped anyway is a Nit by default. It becomes a clarity Blocker when the breaches are dense enough to impede digestion, meaning more than 3 distinct breach types in one artifact, or any banned construction inside `The answer so far`.
