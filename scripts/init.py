#!/usr/bin/env python3
"""Initialize lulu-chime hooks and config in the current project."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List, Optional

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from config import ensure_config
from hooks import MERGERS
from chime_platform import PlatformDetectionError, detect_platform


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Initialize lulu-chime in this project")
    parser.add_argument("--platform", default=None)
    args = parser.parse_args(argv)
    try:
        platform = detect_platform(override=args.platform)
    except PlatformDetectionError as exc:
        print(f"[init] {exc}", file=sys.stderr)
        return 1

    config_file = ensure_config()
    try:
        hooks_path = MERGERS[platform]()
    except (json.JSONDecodeError, OSError, KeyError) as exc:
        print(f"[init] merge hooks failed: {exc}", file=sys.stderr)
        return 1

    print(f"[init] hooks updated at {hooks_path}")
    print(f"[init] lulu-chime ({platform}) initialized")
    print(f"  config: {config_file.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
