#!/usr/bin/env python3
"""Stop hook — play the completion chime (macOS)."""
from __future__ import annotations

import json
import select
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Optional

from chime_platform import PlatformDetectionError, detect_platform
from config import ChimeConfig, load_config

CHIME_FFMPEG = Path("/opt/homebrew/bin/ffmpeg")


def _find_ffmpeg() -> Optional[str]:
    if CHIME_FFMPEG.is_file():
        return str(CHIME_FFMPEG)
    for candidate in ("ffmpeg", "/opt/homebrew/bin/ffmpeg", "/usr/local/bin/ffmpeg"):
        found = shutil.which(candidate)
        if found:
            return found
        if Path(candidate).is_file():
            return candidate
    return None


def _afplay_volume_arg(volume: Any) -> str:
    try:
        v = float(volume)
    except (TypeError, ValueError):
        v = 1.0
    return str(max(0.0, min(v, 1.0)))


def _ffmpeg_gain(gain: Any) -> int:
    try:
        g = int(gain)
    except (TypeError, ValueError):
        g = 25
    return max(0, g)


def _audio_filter(gain: int) -> str:
    return (
        f"volume={gain},alimiter=limit=0.99:attack=1:release=50,"
        "loudnorm=I=-12:TP=-0.5:LRA=5"
    )


def should_play(platform: str, payload: dict, cfg: ChimeConfig) -> bool:
    if not cfg.enabled:
        return False
    if platform == "cursor" and payload.get("status") != "completed":
        return False
    return True


def play_sound(cfg: ChimeConfig, *, runner=subprocess.run) -> None:
    sound = Path(cfg.sound).expanduser()
    if not sound.is_file():
        return
    volume = _afplay_volume_arg(cfg.volume)
    gain = _ffmpeg_gain(cfg.gain)
    ffmpeg_bin = _find_ffmpeg()
    if ffmpeg_bin:
        tmp = tempfile.mkstemp(prefix="lulu-chime.", suffix="")[1]
        wav_path = f"{tmp}.wav"
        runner(
            [
                ffmpeg_bin,
                "-loglevel",
                "quiet",
                "-y",
                "-i",
                str(sound),
                "-filter:a",
                _audio_filter(gain),
                wav_path,
            ],
            check=False,
            capture_output=True,
        )
        runner(["afplay", "-v", volume, wav_path], check=False)
        Path(wav_path).unlink(missing_ok=True)
        return
    runner(["afplay", "-v", volume, str(sound)], check=False)


def read_payload() -> dict:
    if sys.stdin.isatty():
        return {}
    try:
        ready, _, _ = select.select([sys.stdin], [], [], 1.0)
        if not ready:
            return {}
        raw = sys.stdin.buffer.read1(65536).decode("utf-8", errors="replace")
        return json.loads(raw) if raw.strip() else {}
    except (json.JSONDecodeError, OSError, ValueError):
        return {}


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--platform", default=None)
    args, _ = parser.parse_known_args()
    try:
        platform = detect_platform(override=args.platform)
    except PlatformDetectionError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    cfg = load_config()
    payload = read_payload()
    if should_play(platform, payload, cfg):
        play_sound(cfg)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
