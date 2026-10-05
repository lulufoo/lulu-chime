from __future__ import annotations

from config import ChimeConfig
from play import play_sound, should_play


def test_should_play_requires_enabled():
    cfg = ChimeConfig(enabled=False)
    assert should_play("cursor", {"status": "completed"}, cfg) is False


def test_should_play_cursor_requires_completed():
    cfg = ChimeConfig(enabled=True)
    assert should_play("cursor", {"status": "aborted"}, cfg) is False
    assert should_play("cursor", {}, cfg) is False
    assert should_play("cursor", {"status": "completed"}, cfg) is True


def test_should_play_other_platforms_ignore_status():
    cfg = ChimeConfig(enabled=True)
    assert should_play("opencode", {}, cfg) is True
    assert should_play("claude", {"status": "aborted"}, cfg) is True


def test_play_sound_skips_missing_file(tmp_path):
    calls = []
    play_sound(
        ChimeConfig(enabled=True, sound=str(tmp_path / "missing.aiff")),
        runner=lambda *a, **k: calls.append((a, k)),
    )
    assert calls == []
