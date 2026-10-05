<h1 align="center">Lulu Chime</h1>

<p align="center"><b>Hear when the agent is done.</b></p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg?style=flat-square" alt="License" align="absmiddle"></a>
</p>

---

When an agent is working, the finish often happens off-screen. Checking the chat just to catch that moment is waste. Lulu Chime plays a macOS sound when the turn completes.

## Quick start

```bash
git clone https://github.com/lulufoo/lulu-chime.git ~/.agents/skills/lulu-chime
```

In a project chat:

```text
/lulu-chime init
```

`init` writes `.agents/config/lulu-chime/config.json` when it is missing (`enabled: true`) and registers this skill's stop hook. An existing config is left unchanged.

Cursor plays only when the hook payload `status` is `completed`. OpenCode uses `session.idle`, which can also fire on interrupt.

Copilot clones to `~/.copilot/skills/lulu-chime`. Claude clones to `~/.claude/skills/lulu-chime`.

## Skill

Chat entry is `lulu-chime`. The skill only runs `init`.

```text
SKILL.md
scripts/
templates/
```

## Platforms

| Platform | Hook |
|----------|------|
| Cursor | `.cursor/hooks.json` `stop` |
| Copilot | `.github/hooks/hooks.json` `Stop` |
| Claude | `.claude/settings.json` `Stop` |
| Codex | `.codex/hooks.json` `Stop` |
| OpenCode | `.opencode/plugins/lulu-chime.ts` (`session.idle`) |

Config is always `.agents/config/lulu-chime/config.json`.

`init` does not write `preToolUse`. It strips leftover `play_chime` entries from rule-guard.

## Config

`init` writes this file when it does not exist:

```json
{
  "version": 1,
  "enabled": true,
  "sound": "/System/Library/Sounds/Funk.aiff",
  "volume": 1,
  "gain": 25
}
```

| Field | Meaning |
|-------|---------|
| `enabled` | Play on stop. Missing file or `false` means silent |
| `sound` | Audio file |
| `volume` | `afplay` volume, 0–1 |
| `gain` | ffmpeg gain when ffmpeg is present |

## Develop

```bash
python3 -m pytest -q
```

## License

- Project: [MIT](./LICENSE)
