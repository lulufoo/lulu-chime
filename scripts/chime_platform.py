"""Platform detection for lulu-chime.

Precedence: call override, then LULU_PLATFORM, then runtime signals, else cursor.
"""
from __future__ import annotations

import os
from typing import Optional

SUPPORTED_PLATFORMS = ("cursor", "copilot", "claude", "codex", "opencode")

SKILL_SCRIPTS = {
    "cursor": "~/.agents/skills/lulu-chime/scripts",
    "copilot": "~/.copilot/skills/lulu-chime/scripts",
    "claude": "~/.claude/skills/lulu-chime/scripts",
    "codex": "~/.agents/skills/lulu-chime/scripts",
    "opencode": "~/.agents/skills/lulu-chime/scripts",
}


class PlatformDetectionError(Exception):
    """Raised when the platform value is unsupported."""


def _normalize_platform(value: str) -> str:
    plat = value.strip().lower()
    if plat not in SUPPORTED_PLATFORMS:
        raise PlatformDetectionError(f"unsupported platform: {value!r}")
    return plat


def _signal_platform() -> Optional[str]:
    if os.environ.get("VSCODE_TARGET_SESSION_LOG") or os.environ.get("COPILOT_AGENT") == "1":
        return "copilot"
    if os.environ.get("CURSOR_AGENT"):
        return "cursor"
    if os.environ.get("CLAUDE_CODE"):
        return "claude"
    if os.environ.get("CODEX_THREAD_ID") or os.environ.get("CODEX_SESSION_ID"):
        return "codex"
    if os.environ.get("OPENCODE_CLIENT") or os.environ.get("OPENCODE"):
        return "opencode"
    return None


def detect_platform(*, override: Optional[str] = None) -> str:
    if override:
        return _normalize_platform(override)
    lulu_platform = os.environ.get("LULU_PLATFORM")
    if lulu_platform:
        return _normalize_platform(lulu_platform)
    return _signal_platform() or "cursor"


def play_command(platform: str) -> str:
    scripts = SKILL_SCRIPTS[platform]
    return f"python3 {scripts}/play.py --platform {platform}"
