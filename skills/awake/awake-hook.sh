#!/bin/sh
# Claude Code hook: acquire a wake-lock when a prompt is submitted, release it
# when the agent stops. Claude Code passes a JSON payload on stdin; we use
# session_id as the holder id so parallel sessions refcount correctly.
#
# Usage in settings.json: "<skill-dir>/awake-hook.sh acquire" | "... release"
DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
id=$(/usr/bin/python3 -c 'import sys,json;print(json.load(sys.stdin).get("session_id","unknown"))' 2>/dev/null)
[ -z "$id" ] && id=unknown
"$DIR/awake" "$1" "claude-$id" >/dev/null 2>&1
exit 0
