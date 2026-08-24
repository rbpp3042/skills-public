---
name: awake
description: Keep the Mac awake with the lid closed while an agent is working — a scriptable wrapper around Amphetamine. Use when the user asks to stop the machine sleeping, wants to close the laptop while a task runs, or invokes /awake.
---

# awake

Keeps a Mac from sleeping — **including with the lid closed** — for as long as an agent is actually working.

## When to use

- The user asks whether the Mac is being kept awake, or invokes `/awake`
- The user says the lock is stuck and wants it cleared
- A long-running shell command needs to survive a closed lid (`awake -- <cmd>`)

## Why not `caffeinate`

`caffeinate` sets power assertions (idle, display, disk, system). Lid-close sleep is handled separately and is **not** covered by those assertions — a Mac on battery with no external display sleeps anyway. The only built-in alternative is `sudo pmset -b disablesleep 1`, which is a global flag requiring sudo with no automatic expiry.

This skill drives [Amphetamine](https://apps.apple.com/app/amphetamine/id937984704) through its AppleScript API instead — closed-display mode, no sudo, and sessions that expire on their own.

## Commands

Run the script next to this file:

```bash
<skill-dir>/awake status       # state, time remaining, who is holding it
<skill-dir>/awake off          # emergency reset: drop every holder, switch off
<skill-dir>/awake -- <cmd>     # hold for the duration of <cmd>, release on exit
```

There is no manual on/off toggle: the lock is taken and released by the hooks (see the README), so the only thing to report on demand is `status`. Reach for `off` only when the user says it is stuck.

Report a single line of the script's output to the user. Do not add explanation or next steps.

## Requirements

macOS with Amphetamine installed. First run needs Automation permission for the calling terminal to control Amphetamine.
