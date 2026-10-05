// lulu-chime bridge for OpenCode.
// Managed by `lulu-chime init --platform opencode`.
// session.idle also fires on interrupt; v1 does not distinguish completion.
const PLAY = "~/.agents/skills/lulu-chime/scripts/play.py"

export const ChimePlugin = async (ctx: any) => {
  const play = PLAY.replace(/^~/, process.env.HOME ?? "")
  const cwd: string = ctx?.directory ?? ctx?.project?.directory ?? process.cwd()

  const run = () => {
    const bun = (globalThis as any).Bun
    if (typeof bun !== "undefined") {
      bun.spawn(["python3", play, "--platform", "opencode"], {
        stdin: "ignore",
        stdout: "ignore",
        stderr: "ignore",
        cwd,
      })
      return
    }
    import("node:child_process").then((cp: any) => {
      cp.spawn("python3", [play, "--platform", "opencode"], {
        cwd,
        stdio: "ignore",
        detached: true,
      }).unref()
    })
  }

  return {
    event: async ({ event }: any) => {
      if (event?.type === "session.idle") run()
    },
  }
}
