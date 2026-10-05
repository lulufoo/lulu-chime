from __future__ import annotations

import json

from config import default_payload, ensure_config, load_config


def test_missing_config_is_disabled(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    cfg = load_config()
    assert cfg.enabled is False


def test_ensure_writes_enabled_true(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    path = ensure_config()
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["enabled"] is True
    assert data["sound"] == default_payload()["sound"]
    assert load_config().enabled is True


def test_ensure_does_not_overwrite(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    dest = tmp_path / ".agents" / "config" / "lulu-chime" / "config.json"
    dest.parent.mkdir(parents=True)
    dest.write_text(
        json.dumps({"version": 1, "enabled": False, "sound": "/tmp/keep.aiff"}) + "\n",
        encoding="utf-8",
    )
    ensure_config()
    data = json.loads(dest.read_text(encoding="utf-8"))
    assert data["enabled"] is False
    assert data["sound"] == "/tmp/keep.aiff"
