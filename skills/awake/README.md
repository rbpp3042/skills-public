# awake

Keeps a Mac from sleeping **with the lid closed**, for exactly as long as an agent is working — and lets it sleep again the moment the agent stops.

Built for the case where you hand a long task to Claude Code, close the laptop, and put it in a bag. Without this, closing the lid ends the run.

## Why not `caffeinate`

`caffeinate` is the obvious first answer and it does not solve this problem.

It sets power assertions — idle sleep, display sleep, disk sleep, system sleep. Lid-close sleep ("clamshell sleep") is handled separately and is not covered by any of them: a Mac on battery with no external display goes to sleep when you close it, whatever you are holding open in the terminal.

The built-in alternative that does work is:

```bash
sudo pmset -b disablesleep 1
```

That is a global flag. It needs sudo, it has no expiry, and if you forget to set it back to `0` the machine stays awake in your bag until the battery is gone.

So this wraps [Amphetamine](https://apps.apple.com/app/amphetamine/id937984704) instead — a free Mac app with closed-display mode and a full AppleScript API. No sudo, and every session expires on its own.

## What it does

```bash
awake on [hours]   # on, default 3h — the lid can be closed
awake off          # off
awake status       # state, time remaining, who is holding it
awake -- <cmd>     # hold while <cmd> runs, release when it exits
```

`awake -- <cmd>` is the standalone form: `awake -- claude` keeps the Mac up for that session and releases on exit, including on Ctrl-C.

### Reference counting

Every holder is a file under `$XDG_STATE_HOME/awake/holders` (default `~/.local/state/awake/holders`). `acquire <id>` adds one, `release <id>` removes one, and the Amphetamine session ends only when the last holder is gone. Two parallel Claude Code sessions therefore do not switch each other off.

**Dead holders are garbage-collected.** Each holder file records the pid of the process that took it — for the Claude Code hook that is the `claude` process itself (`$PPID`). On every `acquire`, holders whose owner process is gone are removed. So a session that dies without releasing — a crash, a `kill -9`, a hook that never fired — does not hold the Mac awake.

Two further safety nets: the Amphetamine session is started with a 12-hour duration and expires by itself, and holder files older than 12 hours are pruned regardless of pid. The age rule is what covers holders with no recorded owner, such as the `manual` one.

A manual `awake on` registers its own `manual` holder, which only `awake off` clears — so hooks cannot switch off something you turned on by hand.

## Install

```bash
git clone https://github.com/rbpp3042/skills-public.git
ln -s "$PWD/skills-public/skills/awake" ~/.claude/skills/awake
```

Symlinking means `git pull` updates it in place. Claude Code follows symlinked skill directories.

For terminal use, put the script on your `PATH`:

```bash
ln -s ~/.claude/skills/awake/awake ~/bin/awake
```

## Hooks: tie it to the agent

The point of the skill. Add to `~/.claude/settings.json`, replacing `<skill-dir>` with the absolute path (hooks do not expand `~`):

```json
{
  "hooks": {
    "UserPromptSubmit": [
      { "hooks": [{ "type": "command", "command": "<skill-dir>/awake-hook.sh acquire", "timeout": 10 }] }
    ],
    "Stop": [
      { "hooks": [{ "type": "command", "command": "<skill-dir>/awake-hook.sh release", "timeout": 10 }] }
    ],
    "SessionEnd": [
      { "hooks": [{ "type": "command", "command": "<skill-dir>/awake-hook.sh release", "timeout": 10 }] }
    ]
  }
}
```

| Hook | Fires | Effect |
| --- | --- | --- |
| `UserPromptSubmit` | you send a prompt | `acquire` — Amphetamine on |
| `Stop` | the agent finishes its answer | `release` — off if no one else holds it |
| `SessionEnd` | you quit Claude Code | `release` |

The hook reads `session_id` from the JSON on stdin and uses it as the holder id. It always exits `0` and prints nothing, so it cannot block a turn or inject text into the context.

Restart Claude Code after editing `settings.json`.

**Side effect worth knowing:** the Mac now also stays awake during ordinary short exchanges — for the seconds until the answer lands. If that bothers you, move `acquire` from `UserPromptSubmit` to `PreToolUse`, so it only kicks in once the agent actually starts using tools.

## Requirements

- macOS
- [Amphetamine](https://apps.apple.com/app/amphetamine/id937984704) (free, App Store)
- Automation permission for the calling terminal to control Amphetamine — macOS prompts on first run

Closed-display mode also needs to be allowed once in Amphetamine → Preferences → Sessions. The script enables it per session, but the first time macOS shows Amphetamine's own warning prompt.

## Verifying

```bash
awake status                 # awake: off
awake acquire a && awake acquire b
awake release a && awake status   # still on, held by b
awake release b && awake status   # awake: off
```
