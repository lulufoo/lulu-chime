---
name: lulu-chime
description: >-
  Register a completion chime hook for the current project.
  Triggers: lulu-chime, init chime, completion chime, 完成提示音, 初始化提示音.
disable-model-invocation: true
argument-hint: "[init]"
---

# lulu-chime

Register the agent completion chime. Done when `$INIT` exits 0 and prints the hook path and config path.

## Script Macros

| Macro | CLI |
|-------|-----|
| `$INIT` | `python3 $SKILL_ROOT/scripts/init.py` |

`$SKILL_ROOT` is this skill's install directory.

## Commands

### `init`

Run `$INIT`. Non-zero: stop and report stderr.

`$INIT` writes `.agents/config/lulu-chime/config.json` when it is missing (`enabled: true`) and merges this skill's stop hook for the current platform. It does not overwrite an existing config. It does not edit `preToolUse` or rule-guard entries.
