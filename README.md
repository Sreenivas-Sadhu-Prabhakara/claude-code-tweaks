# Claude Code tweaks

Small, self-contained customizations for [Claude Code](https://claude.com/claude-code). Each one
lives in its own folder with its own install note. No dependencies beyond Python 3 and bash.

- **[`skills/`](skills/)** — nine skills for the domains I work in: website, frontend UI,
  microservices, Java, Go, Python, databases, middleware, Apigee. Standards and gotchas written where
  Claude loads them automatically.
- **[`statusline/`](#statusline--see-your-rate-limits-without-asking)** — a status line showing your
  5-hour, weekly and context usage as meters, plus a Monday pacing hook.

## statusline — see your rate limits without asking

Claude Code exposes your usage limits to the status line as JSON. This renders them as meters, so
your remaining budget is simply always on screen:

```
~/Code/my-project  │  5h ▆▆▁▁▁ 42%   wk ▆▁▁▁▁ 18%   ctx ▆▆▆▆▁ 71%  │  Opus 5
wk resets in 6d 5h  ·  ↑ 1.2M in  ·  ↓ 15.3k out
```

| Meter | What it is | Field read |
|---|---|---|
| `5h` | the rolling **5-hour** limit | `rate_limits.five_hour.used_percentage` |
| `wk` | the **7-day (weekly)** limit | `rate_limits.seven_day.used_percentage` |
| `ctx` | this session's **context window** | `context_window.used_percentage` |

Colours: green below 70%, yellow 70–90%, red above 90%.

**There is no "daily" meter on purpose.** Claude Code only exposes `five_hour` and `seven_day`, so
a daily figure would have to be invented by summing transcripts and wouldn't correspond to anything
that actually throttles you. The meters are named after the windows that can really cut you off.

Missing or null fields degrade to a dim `label –` placeholder rather than breaking the line. That
matters in practice: the two rate-limit fields are absent until the first API call of a session, and
`ctx` is briefly null right after `/compact`.

### Install

Copy the files into `~/.claude/`:

```bash
cp statusline/statusline.py statusline/test_statusline.py ~/.claude/
cp statusline/monday-guide.sh statusline/weekly-usage-guide.md ~/.claude/
chmod +x ~/.claude/monday-guide.sh
```

Then in `~/.claude/settings.json`:

```json
{
  "statusLine": {
    "type": "command",
    "command": "python3 ~/.claude/statusline.py"
  },
  "hooks": {
    "SessionStart": [
      { "hooks": [{ "type": "command", "command": "bash ~/.claude/monday-guide.sh" }] }
    ]
  }
}
```

If you already have a `hooks.SessionStart` array, add the entry to it rather than replacing it.

### Tests

```bash
cd statusline && python3 -m unittest test_statusline   # 25 tests
```

They're pure-function tests over fixture JSON, with ANSI codes stripped before the layout
assertions, so colour thresholds are checked separately from rendering.

## monday-guide.sh + weekly-usage-guide.md — a pacing guide, on the day it helps

`monday-guide.sh` is a `SessionStart` hook. On Mondays (`date +%u` = 1) it injects
`weekly-usage-guide.md` as `additionalContext` plus a one-line banner, so the first session of a
fresh weekly budget opens with the plan. Every other day it exits silently and injects nothing.

The guide itself is a pacing method — model mix, context hygiene, a day-by-day pace table — written
to be applied to your own usage figures rather than to anyone else's.

## Licence

MIT. See [LICENSE](LICENSE).
