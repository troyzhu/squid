#!/usr/bin/env node
// Installs the engineering-agent-team into a target project's .claude/ directory.
// Zero runtime dependencies — uses only built-in Node modules (Node 18+).

import { cp, readFile, writeFile, mkdir, access } from 'node:fs/promises';
import { join, dirname, resolve, relative } from 'node:path';
import { fileURLToPath } from 'node:url';
import { argv, cwd, exit } from 'node:process';

const PACKAGE_ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');

const args = argv.slice(2);
const flags = new Set(args.filter((a) => a.startsWith('--') || a.startsWith('-')));
const positional = args.filter((a) => !a.startsWith('-'));

if (flags.has('--help') || flags.has('-h')) {
  printHelp();
  exit(0);
}

const target = resolve(positional[0] || cwd());
const force = flags.has('--force');
const skipProcess = flags.has('--no-process');
const dryRun = flags.has('--dry-run');

function printHelp() {
  console.log(`engineering-agent-team — install the agent team into a Claude Code project

Usage:
  npx engineering-agent-team [target-dir] [options]

If target-dir is omitted, installs into the current working directory.

Options:
  --force         Overwrite docs/PROCESS.md if it already exists.
  --no-process    Skip docs/PROCESS.md entirely.
  --dry-run       Print what would be written, but make no changes.
  --help, -h      Show this help.

What gets installed:
  .claude/agents/            (overwritten — these are the agent contracts)
  .claude/skills/            (overwritten — skills referenced by the pipelines)
  .claude/settings.json      (smart-merged with any existing file)
  docs/PROCESS.md            (copied; skipped if present unless --force)

Existing customisations preserved:
  - permissions.allow / ask / deny entries union'd and deduped.
  - enabledPlugins shallow-merged (incoming keys win on conflict).
  - All other top-level keys in settings.json are preserved unchanged.
`);
}

async function exists(p) {
  try {
    await access(p);
    return true;
  } catch {
    return false;
  }
}

async function ensureDir(p) {
  if (dryRun) return;
  await mkdir(p, { recursive: true });
}

async function copyTree(src, dst) {
  if (dryRun) return;
  await cp(src, dst, { recursive: true, force: true });
}

async function copyFileForce(src, dst) {
  if (dryRun) return;
  await ensureDir(dirname(dst));
  await cp(src, dst, { force: true });
}

function dedupeUnion(a = [], b = []) {
  const seen = new Set();
  const out = [];
  for (const x of [...a, ...b]) {
    const key = typeof x === 'string' ? x : JSON.stringify(x);
    if (seen.has(key)) continue;
    seen.add(key);
    out.push(x);
  }
  return out;
}

async function readJSON(p) {
  return JSON.parse(await readFile(p, 'utf8'));
}

async function mergeSettings(srcPath, dstPath) {
  const src = await readJSON(srcPath);
  let dst = {};
  let dstExists = await exists(dstPath);
  if (dstExists) {
    try {
      dst = await readJSON(dstPath);
    } catch (e) {
      console.error(
        `! Existing ${relative(target, dstPath)} is not valid JSON: ${e.message}`,
      );
      console.error(
        `  Refusing to overwrite. Fix or delete the file and re-run.`,
      );
      exit(2);
    }
  }

  const merged = { ...dst };

  // Smart-merge permissions
  if (src.permissions) {
    merged.permissions = merged.permissions || {};
    for (const key of ['allow', 'ask', 'deny']) {
      if (src.permissions[key]) {
        merged.permissions[key] = dedupeUnion(
          merged.permissions[key],
          src.permissions[key],
        );
      }
    }
  }

  // Shallow-merge enabledPlugins (incoming wins on conflict)
  if (src.enabledPlugins) {
    merged.enabledPlugins = {
      ...(merged.enabledPlugins || {}),
      ...src.enabledPlugins,
    };
  }

  // Any other top-level keys in src that aren't in dst, copy them.
  for (const key of Object.keys(src)) {
    if (key === 'permissions' || key === 'enabledPlugins') continue;
    if (!(key in merged)) {
      merged[key] = src[key];
    }
  }

  if (dryRun) return { dstExists, merged };

  await ensureDir(dirname(dstPath));
  await writeFile(dstPath, JSON.stringify(merged, null, 2) + '\n');
  return { dstExists, merged };
}

async function main() {
  const banner = dryRun ? '(dry-run) ' : '';
  console.log(
    `${banner}Installing engineering-agent-team into ${target}\n`,
  );

  // 1. Copy .claude/agents/
  const agentsSrc = join(PACKAGE_ROOT, '.claude/agents');
  const agentsDst = join(target, '.claude/agents');
  await copyTree(agentsSrc, agentsDst);
  console.log(`  + .claude/agents/`);

  // 2. Copy .claude/skills/
  const skillsSrc = join(PACKAGE_ROOT, '.claude/skills');
  const skillsDst = join(target, '.claude/skills');
  await copyTree(skillsSrc, skillsDst);
  console.log(`  + .claude/skills/`);

  // 3. Smart-merge .claude/settings.json
  const settingsSrc = join(PACKAGE_ROOT, '.claude/settings.json');
  const settingsDst = join(target, '.claude/settings.json');
  const mergeResult = await mergeSettings(settingsSrc, settingsDst);
  console.log(
    `  + .claude/settings.json ${
      mergeResult.dstExists ? '(merged with existing)' : '(new)'
    }`,
  );

  // 4. docs/PROCESS.md (conditional)
  if (skipProcess) {
    console.log(`  - docs/PROCESS.md (skipped via --no-process)`);
  } else {
    const processSrc = join(PACKAGE_ROOT, 'docs/PROCESS.md');
    const processDst = join(target, 'docs/PROCESS.md');
    if ((await exists(processDst)) && !force) {
      console.log(
        `  - docs/PROCESS.md exists; skipped (re-run with --force to overwrite)`,
      );
    } else {
      await copyFileForce(processSrc, processDst);
      console.log(`  + docs/PROCESS.md`);
    }
  }

  console.log(`\nDone.`);
  if (!dryRun) {
    console.log(`\nNext steps:`);
    console.log(`  1. Open ${target} in Claude Code.`);
    console.log(`  2. The agents and skills are auto-discovered from .claude/.`);
    console.log(`  3. Read docs/PROCESS.md for the canonical lifecycle.`);
    console.log(`  4. Try /day for a single supervised task or /night <feature> for the full pipeline.`);
  }
}

main().catch((err) => {
  console.error(`\nInstall failed: ${err.message}`);
  if (err.stack) console.error(err.stack);
  exit(1);
});
