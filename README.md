# lulu-chime

Play a macOS sound when the agent stops.

## Install

```bash
git clone https://github.com/lulufoo/lulu-chime.git ~/.agents/skills/lulu-chime
```

Then in a project:

```text
/lulu-chime init
```

## After `init`

`init` writes the stop hook for the current platform and creates the config if it is missing.

| Platform | Hook | Config |
|----------|------|--------|
| Cursor | `.cursor/hooks.json` `stop` | `.agents/config/lulu-chime/config.json` |
| Copilot | `.github/hooks/hooks.json` `Stop` | same |
| Claude | `.claude/settings.json` `Stop` | same |
| Codex | `.codex/hooks.json` `Stop` | same |
| OpenCode | `.opencode/plugins/lulu-chime.ts` (`session.idle`) | same |

Install paths:

- Cursor / Codex / OpenCode: `~/.agents/skills/lulu-chime`
- Copilot: `~/.copilot/skills/lulu-chime`
- Claude: `~/.claude/skills/lulu-chime`

`init` owns only the completion-sound hook. It strips leftover `play_chime` entries from rule-guard. It does not write `preToolUse`.

Cursor plays only when the hook payload `status` is `completed`. OpenCode uses `session.idle`, which can also fire on interrupt.

## Config

`init` writes this file when it does not exist. An existing file is left unchanged.

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

Missing config: the player exits 0 and stays silent.

## License

- Project: [MIT](./LICENSE)
