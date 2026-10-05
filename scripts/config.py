"""Load and create .agents/config/lulu-chime/config.json."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

CONFIG_REL = Path(".agents/config/lulu-chime/config.json")
DEFAULT_SOUND = "/System/Library/Sounds/Funk.aiff"
DEFAULT_VOLUME = 1.0
DEFAULT_GAIN = 25


@dataclass
class ChimeConfig:
    enabled: bool = False
    sound: str = DEFAULT_SOUND
    volume: float = DEFAULT_VOLUME
    gain: int = DEFAULT_GAIN
    path: str = CONFIG_REL.as_posix()


def default_payload() -> dict:
    return {
        "version": 1,
        "enabled": True,
        "sound": DEFAULT_SOUND,
        "volume": DEFAULT_VOLUME,
        "gain": DEFAULT_GAIN,
    }


def config_path() -> Path:
    return CONFIG_REL


def _parse_bool(raw: object, default: bool = False) -> bool:
    if raw is None:
        return default
    if isinstance(raw, str):
        return raw.strip().lower() == "true"
    return bool(raw)


def load_config() -> ChimeConfig:
    path = config_path()
    if not path.exists():
        return ChimeConfig(path=path.as_posix())
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError, ValueError):
        return ChimeConfig(path=path.as_posix())
    if not isinstance(data, dict):
        return ChimeConfig(path=path.as_posix())
    try:
        volume = float(data.get("volume", DEFAULT_VOLUME))
    except (TypeError, ValueError):
        volume = DEFAULT_VOLUME
    try:
        gain = int(data.get("gain", DEFAULT_GAIN))
    except (TypeError, ValueError):
        gain = DEFAULT_GAIN
    return ChimeConfig(
        enabled=_parse_bool(data.get("enabled"), False),
        sound=str(data.get("sound") or DEFAULT_SOUND),
        volume=volume,
        gain=gain,
        path=path.as_posix(),
    )


def ensure_config() -> Path:
    dest = config_path()
    dest.parent.mkdir(parents=True, exist_ok=True)
    if not dest.exists():
        dest.write_text(
            json.dumps(default_payload(), indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    return dest
