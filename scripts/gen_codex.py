#!/usr/bin/env python3
"""Generate Codex adapters from Squid's canonical agents and skills."""

from __future__ import annotations

import json
import re
import shutil
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "scripts" / "codex" / "config.yaml"
CLAUDE_MANIFEST = ROOT / ".claude-plugin" / "plugin.json"
CODEX_MANIFEST = ROOT / "plugins" / "squid-codex" / ".codex-plugin" / "plugin.json"
CODEX_ADAPTER = ROOT / "plugins" / "squid-codex" / "references" / "codex-adapter.md"

GENERATED_COMMENT = "<!-- GENERATED — do not edit; run scripts/gen_codex.py -->"
GENERATED_TOML = "# GENERATED — do not edit; run scripts/gen_codex.py"
AGENT_MAP_START = "<!-- BEGIN GENERATED:agent-map (scripts/gen_codex.py) — do not edit by hand -->"
AGENT_MAP_END = "<!-- END GENERATED:agent-map -->"


def main() -> int:
    config = load_config()
    version = load_json(CLAUDE_MANIFEST)["version"]
    agent_slugs = sorted(path.stem for path in (ROOT / "agents").glob("*.md"))
    skill_slugs = sorted(path.parent.name for path in (ROOT / "skills").glob("*/SKILL.md"))

    validate_config(config, agent_slugs, skill_slugs)
    generate_agents(config["agents"], agent_slugs)
    generate_canonical_snapshots(agent_slugs, skill_slugs)
    generated_skills = generate_skills(config["skills"], skill_slugs)
    update_agent_map(agent_slugs)
    update_codex_manifest(version, config["skills"], generated_skills)
    return 0


def load_config() -> dict[str, Any]:
    try:
        config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except FileNotFoundError:
        error(f"missing config: {CONFIG_PATH.relative_to(ROOT)}")
    except json.JSONDecodeError as exc:
        error(
            f"{CONFIG_PATH.relative_to(ROOT)} must be JSON-shaped YAML so the "
            f"generator stays dependency-free: {exc}"
        )
    if not isinstance(config, dict):
        error("config root must be an object")
    if not isinstance(config.get("agents"), dict):
        error("config must contain an agents object")
    if not isinstance(config.get("skills"), dict):
        error("config must contain a skills object")
    return config


def validate_config(config: dict[str, Any], agent_slugs: list[str], skill_slugs: list[str]) -> None:
    config_agents = set(config["agents"])
    actual_agents = set(agent_slugs)
    config_skills = set(config["skills"])
    actual_skills = set(skill_slugs)

    for slug in sorted(actual_agents - config_agents):
        error(f"agent '{slug}' has no codex config entry")
    for slug in sorted(config_agents - actual_agents):
        error(f"codex config names missing agent '{slug}'")
    for slug in sorted(actual_skills - config_skills):
        error(f"skill '{slug}' has no codex config entry")
    for slug in sorted(config_skills - actual_skills):
        error(f"codex config names missing skill '{slug}'")

    for slug in agent_slugs:
        entry = config["agents"][slug]
        require_string(entry, "title", f"agents.{slug}")
        require_string(entry, "description", f"agents.{slug}")
        guardrail = entry.get("guardrail", "")
        if not isinstance(guardrail, str):
            error(f"agents.{slug}.guardrail must be a string")
        nicknames = entry.get("nicknames")
        if not isinstance(nicknames, list) or not all(isinstance(value, str) and value for value in nicknames):
            error(f"agents.{slug}.nicknames must be a non-empty string array")

    default_prompts = 0
    for slug in skill_slugs:
        entry = config["skills"][slug]
        require_string(entry, "title", f"skills.{slug}")
        require_string(entry, "blurb", f"skills.{slug}")
        codex = entry.get("codex", True)
        if not isinstance(codex, bool):
            error(f"skills.{slug}.codex must be a boolean")
        extra_steps = entry.get("extra_steps", [])
        if not isinstance(extra_steps, list) or not all(isinstance(value, str) and value for value in extra_steps):
            error(f"skills.{slug}.extra_steps must be a string array")
        if "default_prompt" in entry:
            require_string(entry, "default_prompt", f"skills.{slug}")
            default_prompts += 1
    if default_prompts != 3:
        error(f"expected exactly 3 skills with default_prompt, found {default_prompts}")


def generate_agents(agent_config: dict[str, Any], agent_slugs: list[str]) -> None:
    out_dir = ROOT / ".codex" / "agents"
    reset_dir(out_dir)
    for slug in agent_slugs:
        entry = agent_config[slug]
        guardrail = entry.get("guardrail", "")
        guardrail_clause = f" {guardrail}" if guardrail else ""
        developer_instructions = f"""You are the Squid {entry["title"]} role in Codex.

Before acting, read `AGENTS.md` if present, then read
`plugins/squid-codex/references/codex-adapter.md` if present, then read the
canonical role contract at `agents/{slug}.md`.

Follow the canonical contract after translating Claude-specific references into
Codex equivalents. Prefer `AGENTS.md` for project guidance; read `CLAUDE.md` only
as fallback context or when the user asks about Claude behavior.{guardrail_clause} If the canonical contract
is missing, report that blocker instead of inventing the role.
"""
        body = "\n".join(
            [
                GENERATED_TOML,
                f"name = {toml_string(f'squid-{slug}')}",
                f"description = {toml_string(entry['description'])}",
                f"developer_instructions = {toml_multiline(developer_instructions)}",
                f"nickname_candidates = {json.dumps(entry['nicknames'], ensure_ascii=False)}",
                "",
            ]
        )
        write_text(out_dir / f"squid-{slug}.toml", body)


def generate_skills(skill_config: dict[str, Any], skill_slugs: list[str]) -> list[str]:
    plugin_dir = ROOT / "plugins" / "squid-codex" / "skills"
    repo_dir = ROOT / ".agents" / "skills"
    reset_dir(plugin_dir)
    reset_dir(repo_dir)

    generated: list[str] = []
    for slug in skill_slugs:
        entry = skill_config[slug]
        if entry.get("codex", True) is False:
            continue
        generated.append(slug)
        blurb = entry["blurb"].rstrip(".")
        blurb_cap = blurb[:1].upper() + blurb[1:]
        extra_steps = numbered_extra_steps(entry.get("extra_steps", []), start=4)

        plugin_skill = f"""---
name: {slug}
description: {json.dumps(f"Codex adapter for Squid {slug}. {blurb_cap}.", ensure_ascii=False)}
---

{GENERATED_COMMENT}

# {entry["title"]} (Codex Adapter)

Use this adapter to run Squid's {slug} workflow in Codex.

1. Read `../../references/codex-adapter.md`.
2. Read the packaged canonical contract at `../../references/canonical/skills/{slug}/SKILL.md`.
3. Follow the canonical workflow after applying the adapter translation rules.
{extra_steps}"""
        write_text(plugin_dir / slug / "SKILL.md", ensure_trailing_newline(plugin_skill))

        repo_skill = f"""---
name: {slug}
description: {json.dumps(f"Repo-local Codex entry point for Squid {slug}: {blurb}.", ensure_ascii=False)}
---

{GENERATED_COMMENT}

# {entry["title"]}

Read and follow `../../../plugins/squid-codex/skills/{slug}/SKILL.md`.
"""
        write_text(repo_dir / slug / "SKILL.md", repo_skill)

    return generated


def generate_canonical_snapshots(agent_slugs: list[str], skill_slugs: list[str]) -> None:
    out_dir = ROOT / "plugins" / "squid-codex" / "references" / "canonical"
    reset_dir(out_dir)
    for slug in agent_slugs:
        source = ROOT / "agents" / f"{slug}.md"
        target = out_dir / "agents" / f"{slug}.md"
        text = source.read_text(encoding="utf-8")
        write_text(target, f"{GENERATED_COMMENT}\n\n{text}")
    for slug in skill_slugs:
        source = ROOT / "skills" / slug
        target = out_dir / "skills" / slug
        copy_generated_snapshot_tree(source, target)


def copy_generated_snapshot_tree(source_dir: Path, target_dir: Path) -> None:
    for source in sorted(source_dir.rglob("*")):
        relative = source.relative_to(source_dir)
        target = target_dir / relative
        if source.is_dir():
            target.mkdir(parents=True, exist_ok=True)
        elif source.suffix == ".md":
            text = source.read_text(encoding="utf-8")
            write_text(target, f"{GENERATED_COMMENT}\n\n{text}")
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)


def update_agent_map(agent_slugs: list[str]) -> None:
    text = CODEX_ADAPTER.read_text(encoding="utf-8")
    if AGENT_MAP_START not in text or AGENT_MAP_END not in text:
        error(f"{CODEX_ADAPTER.relative_to(ROOT)} is missing generated agent-map markers")
    rows = [
        AGENT_MAP_START,
        "| Claude role | Codex custom agent | Canonical contract |",
        "|---|---|---|",
    ]
    rows.extend(
        f"| `squid:{slug}` | `squid-{slug}` | `agents/{slug}.md` |"
        for slug in agent_slugs
    )
    rows.append(AGENT_MAP_END)
    replacement = "\n".join(rows)
    pattern = re.compile(
        re.escape(AGENT_MAP_START) + r".*?" + re.escape(AGENT_MAP_END),
        flags=re.DOTALL,
    )
    write_text(CODEX_ADAPTER, pattern.sub(replacement, text))


def update_codex_manifest(version: str, skill_config: dict[str, Any], generated_skills: list[str]) -> None:
    manifest = load_json(CODEX_MANIFEST)
    manifest["version"] = version
    prompts: list[str] = []
    for slug, entry in skill_config.items():
        if slug in generated_skills and "default_prompt" in entry:
            prompts.append(entry["default_prompt"])
    manifest.setdefault("interface", {})["defaultPrompt"] = prompts
    write_text(CODEX_MANIFEST, json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")


def reset_dir(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        error(f"missing JSON file: {path.relative_to(ROOT)}")
    except json.JSONDecodeError as exc:
        error(f"invalid JSON in {path.relative_to(ROOT)}: {exc}")
    if not isinstance(payload, dict):
        error(f"{path.relative_to(ROOT)} must contain a JSON object")
    return payload


def require_string(entry: dict[str, Any], key: str, prefix: str) -> None:
    if not isinstance(entry, dict):
        error(f"{prefix} must be an object")
    value = entry.get(key)
    if not isinstance(value, str) or not value.strip():
        error(f"{prefix}.{key} must be a non-empty string")


def numbered_extra_steps(steps: list[str], *, start: int) -> str:
    if not steps:
        return ""
    return "".join(f"{idx}. {step}\n" for idx, step in enumerate(steps, start=start))


def toml_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def toml_multiline(value: str) -> str:
    if '"""' in value:
        error("developer instructions cannot contain triple quotes")
    return f'"""\n{value}"""'


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(ensure_trailing_newline(text), encoding="utf-8")


def ensure_trailing_newline(text: str) -> str:
    return text if text.endswith("\n") else text + "\n"


def error(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


if __name__ == "__main__":
    raise SystemExit(main())
