from __future__ import annotations

import json
from pathlib import Path

import init as init_mod
from hooks import (
    merge_claude_hooks,
    merge_codex_hooks,
    merge_copilot_hooks,
    merge_cursor_hooks,
    write_opencode_plugin,
)


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_cursor_init_writes_config_and_stop(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert init_mod.main(["--platform", "cursor"]) == 0
    cfg = tmp_path / ".agents" / "config" / "lulu-chime" / "config.json"
    assert json.loads(cfg.read_text(encoding="utf-8"))["enabled"] is True
    hooks = _load(tmp_path / ".cursor" / "hooks.json")["hooks"]
    stop = [e["command"] for e in hooks["stop"]]
    assert any("lulu-chime/scripts/play.py --platform cursor" in c for c in stop)
    assert "preToolUse" not in hooks


def test_cursor_init_preserves_pretool_and_strips_legacy(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    dest = tmp_path / ".cursor" / "hooks.json"
    dest.parent.mkdir()
    dest.write_text(
        json.dumps(
            {
                "version": 1,
                "hooks": {
                    "preToolUse": [
                        {
                            "command": "python3 ~/.agents/skills/lulu-rule-guard/scripts/entry.py --platform cursor",
                            "timeout": 5,
                            "failClosed": False,
                        }
                    ],
                    "stop": [
                        {
                            "command": "python3 ~/.agents/skills/lulu-rule-guard/scripts/play_chime.py --platform cursor",
                            "timeout": 5,
                            "failClosed": False,
                        },
                        {"command": "python3 my-stop.py", "timeout": 2},
                    ],
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )
    merge_cursor_hooks()
    merge_cursor_hooks()
    hooks = _load(dest)["hooks"]
    pre = [e["command"] for e in hooks["preToolUse"]]
    assert pre == [
        "python3 ~/.agents/skills/lulu-rule-guard/scripts/entry.py --platform cursor"
    ]
    stop = [e["command"] for e in hooks["stop"]]
    assert "python3 my-stop.py" in stop
    assert not any("play_chime" in c for c in stop)
    assert len([c for c in stop if "lulu-chime/scripts/play.py" in c]) == 1


def test_copilot_init_stop_only(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    merge_copilot_hooks()
    merge_copilot_hooks()
    hooks = _load(tmp_path / ".github" / "hooks" / "hooks.json")["hooks"]
    assert "PreToolUse" not in hooks
    stop = [e["command"] for e in hooks["Stop"]]
    assert len(stop) == 1
    assert "lulu-chime/scripts/play.py --platform copilot" in stop[0]
    assert hooks["Stop"][0]["type"] == "command"


def test_claude_and_codex_grouped_stop(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    settings = tmp_path / ".claude" / "settings.json"
    settings.parent.mkdir()
    settings.write_text(
        json.dumps(
            {
                "permissions": {"allow": ["Read"]},
                "hooks": {
                    "PreToolUse": [
                        {
                            "matcher": "Bash",
                            "hooks": [{"type": "command", "command": "echo keep"}],
                        }
                    ],
                    "Stop": [
                        {
                            "hooks": [
                                {
                                    "type": "command",
                                    "command": (
                                        "python3 ~/.claude/skills/lulu-rule-guard/"
                                        "scripts/play_chime.py --platform claude"
                                    ),
                                }
                            ]
                        }
                    ],
                },
            }
        ),
        encoding="utf-8",
    )
    merge_claude_hooks()
    merge_claude_hooks()
    data = _load(settings)
    assert data["permissions"] == {"allow": ["Read"]}
    pre = [
        hook["command"]
        for group in data["hooks"]["PreToolUse"]
        for hook in group["hooks"]
    ]
    assert pre == ["echo keep"]
    stop = [
        hook["command"] for group in data["hooks"]["Stop"] for hook in group["hooks"]
    ]
    assert len(stop) == 1
    assert stop[0].endswith("play.py --platform claude")
    assert "play_chime" not in stop[0]

    merge_codex_hooks()
    codex = _load(tmp_path / ".codex" / "hooks.json")
    assert "PreToolUse" not in codex["hooks"]
    assert "matcher" not in codex["hooks"]["Stop"][0]


def test_opencode_plugin_writes_session_idle(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    path = Path(write_opencode_plugin())
    text = path.read_text(encoding="utf-8")
    assert "session.idle" in text
    assert "lulu-chime/scripts/play.py" in text
    write_opencode_plugin()
    assert path.read_text(encoding="utf-8") == text


def test_opencode_plugin_rejects_foreign_file(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    dest = tmp_path / ".opencode" / "plugins" / "lulu-chime.ts"
    dest.parent.mkdir(parents=True)
    dest.write_text("export const Other = 1\n", encoding="utf-8")
    try:
        write_opencode_plugin()
    except OSError as exc:
        assert "not lulu-chime managed" in str(exc)
    else:
        raise AssertionError("expected OSError")
