---
name: git-guardrails
description: Install Claude Code PreToolUse hooks that block destructive git/shell commands before they execute — force-push to protected branches, `git reset --hard` of unstaged work, `git push --no-verify`, and `rm -rf` paths that escape the worktree. Smart-merges into the project's `.claude/settings.json` and writes one guardian script. Trigger when the user says "/git-guardrails", asks to harden Claude Code against destructive git commands, or is about to run `/night` unattended for the first time.
disable-model-invocation: false
argument-hint: [optional: --protected-branches main,master,prod]
---

# Git Guardrails — block destructive git commands at the hook layer

Claude Code's `PreToolUse` hooks fire **before** a tool call executes. If the hook script exits non-zero, the call is blocked and the failure message returned to the agent. This skill writes a small guardian script and a settings entry that together catch the worst classes of accidental damage:

1. **Force-push to a protected branch** — `git push --force` / `--force-with-lease` to `main` / `master` / `prod` (configurable).
2. **`git reset --hard`** when there's unstaged or uncommitted work.
3. **`git push --no-verify`** (skipping pre-push hooks).
4. **`git commit --no-verify` / `--no-gpg-sign` / `-c commit.gpgsign=false`** (skipping pre-commit hooks or signing).
5. **`rm -rf` of paths that resolve outside the current worktree.**
6. **`git worktree remove --force`** of a worktree that has uncommitted changes.

These guardrails complement, not replace, the retry caps in [`docs/PROCESS.md`](../../../docs/PROCESS.md). Caps stop runaway loops; guardrails stop a single agent call from deleting your work.

## When to use

- First time setting up `/night` for unattended runs in a project.
- After a near-miss where an agent ran a destructive command that "almost" got through.
- When inheriting a repo that doesn't yet have these hooks configured.

## When NOT to use

- For `/day` (supervised, you watch every diff). The hooks don't hurt there, but the human is already the guardrail.
- To replace pre-commit hooks (lint, format, tests). Those are project-side hooks; this skill is about Claude Code agent-side guardrails. See [`pre-commit-hooks.md`](../scaffold/specs/pre-commit-hooks.md) for the project side.
- On a per-command basis. If you find yourself disabling a guardrail repeatedly, the right fix is to update the rule, not to bypass it.

## Step 1 — Resolve options

Parse `$ARGUMENTS` for `--protected-branches=<csv>`. Default protected list: `main,master,prod`.

If the project has a non-standard default branch (e.g. `develop`), surface that and ask the user once: "Default branch is `develop`. Add to protected list? (Y/n)".

## Step 2 — Show the proposed configuration

Before writing anything, show the user exactly what will land:

1. The path of the guardian script (`.claude/scripts/git-guardrails.sh`).
2. The settings.json hook entry that will be merged.
3. The list of rules the script enforces.

Ask explicit approval. Do NOT write on assumed approval — this skill modifies a settings file the user owns.

## Step 3 — Write the guardian script

Path: `.claude/scripts/git-guardrails.sh`. Make it idempotent — overwriting a previous version is fine.

```bash
#!/usr/bin/env bash
# git-guardrails — invoked by Claude Code PreToolUse hooks.
# Reads the proposed Bash command from $CLAUDE_TOOL_INPUT_command (set by the harness).
# Exits 0 to allow, non-zero with a stderr message to block.
set -uo pipefail

cmd="${CLAUDE_TOOL_INPUT_command:-}"
[ -z "$cmd" ] && exit 0

# Configurable: protected branch list (comma-separated, no spaces).
PROTECTED="${GIT_GUARDRAILS_PROTECTED:-main,master,prod}"

block() {
  echo "git-guardrails: blocked — $1" >&2
  echo "  command: $cmd" >&2
  echo "  override: tell the human and have them run the command themselves." >&2
  exit 2
}

# Rule 1: force-push to a protected branch.
if echo "$cmd" | grep -qE 'git[[:space:]]+push.*(--force|--force-with-lease|-f([[:space:]]|$))'; then
  for br in ${PROTECTED//,/ }; do
    if echo "$cmd" | grep -qE "(^|[[:space:]])${br}(\$|[[:space:]:])"; then
      block "force-push to protected branch '$br'"
    fi
  done
fi

# Rule 2: git reset --hard with unstaged / uncommitted work present.
if echo "$cmd" | grep -qE 'git[[:space:]]+reset[[:space:]]+(--hard|--merge[[:space:]]+--hard)'; then
  if [ -n "$(git status --porcelain 2>/dev/null)" ]; then
    block "'git reset --hard' would discard uncommitted work (run 'git stash' first if you mean it)"
  fi
fi

# Rule 3: --no-verify on push or commit (skips hooks).
if echo "$cmd" | grep -qE 'git[[:space:]]+(push|commit).*--no-verify'; then
  block "--no-verify skips hooks; fix the underlying lint/test failure instead"
fi

# Rule 4: skipping commit signing.
if echo "$cmd" | grep -qE 'git[[:space:]]+commit.*(--no-gpg-sign|-c[[:space:]]+commit\.gpgsign=false)'; then
  block "commit-signing bypass requested; do not bypass without explicit human direction"
fi

# Rule 5: rm -rf of paths escaping the current working tree.
if echo "$cmd" | grep -qE 'rm[[:space:]]+(-[a-zA-Z]*r[a-zA-Z]*f|-[a-zA-Z]*f[a-zA-Z]*r|-rf|-fr)'; then
  # Extract path arguments (very rough — sufficient for blocking obvious cases).
  paths=$(echo "$cmd" | sed -E 's/^.*rm[[:space:]]+-[a-zA-Z]*[[:space:]]+//; s/[[:space:]]*&&.*//; s/[[:space:]]*\|\|.*//; s/[[:space:]]*;.*//')
  worktree="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
  for p in $paths; do
    case "$p" in
      /*|~*|..*|"$HOME"*) block "'rm -rf' on absolute / home / parent path: $p" ;;
    esac
    abs=$(cd "$(dirname "$p")" 2>/dev/null && pwd)/$(basename "$p") || continue
    case "$abs" in
      "$worktree"*) ;;  # inside worktree — allowed
      *) block "'rm -rf' on path outside worktree ($worktree): $p" ;;
    esac
  done
fi

# Rule 6: git worktree remove --force when worktree has uncommitted changes.
if echo "$cmd" | grep -qE 'git[[:space:]]+worktree[[:space:]]+remove.*--force'; then
  block "'git worktree remove --force' can drop uncommitted work; remove without --force, or commit/stash first"
fi

exit 0
```

`chmod +x` the file after writing it.

## Step 4 — Smart-merge the hook entry into `.claude/settings.json`

Read the existing file if present (create it if missing). Merge **without disturbing anything else**:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          { "type": "command", "command": ".claude/scripts/git-guardrails.sh" }
        ]
      }
    ]
  }
}
```

If `hooks.PreToolUse` already has a `Bash` matcher, append our `command` to its `hooks` array — don't replace. Use a stable equality check on the `command` string so re-running the skill is idempotent (no duplicate entries).

## Step 5 — Smoke-test the hooks

Run two tests against a scratch worktree (do NOT run against the user's main worktree):

```bash
# 1. Should block.
CLAUDE_TOOL_INPUT_command='git push --force origin main' .claude/scripts/git-guardrails.sh; echo "exit=$?"
# Expect: exit=2 with a 'force-push to protected branch' message.

# 2. Should allow.
CLAUDE_TOOL_INPUT_command='git push origin feat/example' .claude/scripts/git-guardrails.sh; echo "exit=$?"
# Expect: exit=0.
```

Surface both results to the user as confirmation before declaring success.

## Step 6 — Report

Single markdown block:

```markdown
## git-guardrails installed

**Wrote:** `.claude/scripts/git-guardrails.sh` (executable)
**Merged into:** `.claude/settings.json` — `hooks.PreToolUse[Bash]`
**Protected branches:** main, master, prod (override with `GIT_GUARDRAILS_PROTECTED` env var)
**Smoke tests:** force-push to main → blocked; push to feature branch → allowed.

The next time an agent attempts a destructive command, the call will be blocked and the failure message returned to it.
```

## Notes on shape

- **Block, don't warn.** Hooks that print a warning but allow the command train agents to ignore them. Exit 2 with a clear message; the agent gets the message back as a tool failure and adapts.
- **Exit 2, not exit 1.** Claude Code distinguishes "hook failed, block" (exit 2) from "hook errored" (exit 1). Use 2 so the agent sees a deterministic block, not a flaky tool.
- **Don't try to be clever.** This script doesn't parse shell — it greps. Sophisticated bypasses (`eval`, base64-decoded commands) are out of scope. The threat model is *honest agent runs into a sharp edge*, not adversarial.
- **The user is the override.** Every block message tells the agent to hand back to the human. The human runs the command themselves; they're the only one with full context on whether the destructive action is intended.
- **Re-run is safe.** Step 4's idempotence rule and Step 3's overwrite-fine guarantee mean re-invoking `/git-guardrails` to refresh after a plugin update never duplicates anything.
- **Matched commands list lives in the script, not settings.json.** Easier to audit, easier to extend. Settings.json just points at the script.
