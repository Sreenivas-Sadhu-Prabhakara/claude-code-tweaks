#!/bin/bash
# SessionStart hook: on Mondays, surface the weekly usage game plan.
# Non-Monday -> exit silently (no output = nothing injected).

[ "$(date +%u)" = "1" ] || exit 0

GUIDE="$HOME/.claude/weekly-usage-guide.md"
[ -f "$GUIDE" ] || exit 0

python3 - "$GUIDE" <<'PY'
import json, sys
guide = open(sys.argv[1], encoding="utf-8").read()
ctx = (
    "It is Monday and the weekly usage window has reset. Before anything else "
    "in your first reply, present the following Weekly Usage Game Plan to the "
    "user, rendered as markdown, then continue with their request:\n\n" + guide
)
print(json.dumps({
    "hookSpecificOutput": {
        "hookEventName": "SessionStart",
        "additionalContext": ctx,
    },
    "systemMessage": "🗓️ Monday — weekly budget just reset. Loading your usage game plan.",
}))
PY
