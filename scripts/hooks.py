"""Merge lulu-chime stop hooks. Do not touch preToolUse / file-guard entries."""
from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

from chime_platform import play_command

HOOK_NEEDLES = ("lulu-chime/scripts/play", "play_chime", "play-chime")
CURSOR_HOOKS = Path(".cursor/hooks.json")
COPILOT_HOOKS = Path(".github/hooks/hooks.json")
CLAUDE_HOOKS = Path(".claude/settings.json")
CODEX_HOOKS = Path(".codex/hooks.json")
OPENCODE_PLUGIN = Path(".opencode/plugins/lulu-chime.ts")
TEMPLATE = Path(__file__).resolve().parent.parent / "templates" / "opencode-plugin.ts"


def _is_chime_command(cmd: str) -> bool:
    low = cmd.lower()
    return any(needle in low for needle in HOOK_NEEDLES)


def _strip_flat(entries: list) -> list:
    return [e for e in entries if not _is_chime_command(str(e.get("command", "")))]


def _strip_grouped(groups: list) -> list:
    kept: list = []
    for group in groups:
        if not isinstance(group, dict):
            kept.append(group)
            continue
        hooks = group.get("hooks")
        if not isinstance(hooks, list):
            kept.append(group)
            continue
        remaining = [
            hook
            for hook in hooks
            if not (
                isinstance(hook, dict)
                and _is_chime_command(str(hook.get("command", "")))
            )
        ]
        if not remaining:
            continue
        if len(remaining) == len(hooks):
            kept.append(group)
            continue
        updated = dict(group)
        updated["hooks"] = remaining
        kept.append(updated)
    return kept


def _read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def _write_json(path: Path, data: dict) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return str(path)


def _cursor_stop_entry() -> dict:
    return {
        "command": play_command("cursor"),
        "timeout": 5,
        "failClosed": False,
    }


def _copilot_stop_entry() -> dict:
    return {
        "type": "command",
        "command": play_command("copilot"),
        "timeout": 5,
    }


def _grouped_stop(platform: str) -> dict:
    return {
        "hooks": [
            {"type": "command", "command": play_command(platform), "timeout": 5}
        ]
    }


def _drop_empty_events(hooks: dict) -> None:
    for event in list(hooks.keys()):
        entries = hooks.get(event)
        if isinstance(entries, list) and len(entries) == 0:
            del hooks[event]


def merge_cursor_hooks() -> str:
    data = _read_json(CURSOR_HOOKS)
    data["version"] = 1
    hooks = data.get("hooks")
    if not isinstance(hooks, dict):
        hooks = {}
    data["hooks"] = hooks
    for event, entries in list(hooks.items()):
        if isinstance(entries, list):
            hooks[event] = _strip_flat(entries)
    stop = hooks.get("stop")
    hooks["stop"] = _strip_flat(stop if isinstance(stop, list) else [])
    hooks["stop"].append(deepcopy(_cursor_stop_entry()))
    _drop_empty_events(hooks)
    return _write_json(CURSOR_HOOKS, data)


def merge_copilot_hooks() -> str:
    data = _read_json(COPILOT_HOOKS)
    data["version"] = 1
    hooks = data.get("hooks")
    if not isinstance(hooks, dict):
        hooks = {}
    data["hooks"] = hooks
    stop = hooks.get("Stop")
    hooks["Stop"] = _strip_flat(stop if isinstance(stop, list) else [])
    hooks["Stop"].append(deepcopy(_copilot_stop_entry()))
    _drop_empty_events(hooks)
    return _write_json(COPILOT_HOOKS, data)


def _merge_grouped(path: Path, platform: str) -> str:
    data = _read_json(path)
    hooks = data.get("hooks")
    if not isinstance(hooks, dict):
        hooks = {}
    data["hooks"] = hooks
    stop = hooks.get("Stop")
    hooks["Stop"] = _strip_grouped(stop if isinstance(stop, list) else [])
    hooks["Stop"].append(_grouped_stop(platform))
    return _write_json(path, data)


def merge_claude_hooks() -> str:
    return _merge_grouped(CLAUDE_HOOKS, "claude")


def merge_codex_hooks() -> str:
    return _merge_grouped(CODEX_HOOKS, "codex")


def write_opencode_plugin() -> str:
    if OPENCODE_PLUGIN.exists():
        existing = OPENCODE_PLUGIN.read_text(encoding="utf-8")
        if "lulu-chime" not in existing:
            raise OSError(
                f"{OPENCODE_PLUGIN.as_posix()} exists and is not lulu-chime managed"
            )
    OPENCODE_PLUGIN.parent.mkdir(parents=True, exist_ok=True)
    OPENCODE_PLUGIN.write_text(TEMPLATE.read_text(encoding="utf-8"), encoding="utf-8")
    return str(OPENCODE_PLUGIN)


MERGERS = {
    "cursor": merge_cursor_hooks,
    "copilot": merge_copilot_hooks,
    "claude": merge_claude_hooks,
    "codex": merge_codex_hooks,
    "opencode": write_opencode_plugin,
}
