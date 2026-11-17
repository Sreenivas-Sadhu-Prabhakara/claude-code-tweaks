# 🗓️ Weekly Usage Game Plan — Maximize Without Running Out

*The weekly cap resets ~Monday, so Monday is a fresh budget — spend it deliberately.*

## Work out your own usage signature first

The rules below are ordered by impact for a **typical heavy Claude Code user**: one who keeps a
large cached context, runs long sessions, and leaves the model on its most capable setting. Before
you follow them, check whether that is you. The four numbers worth knowing:

- **Model mix** — what share of your billed turns ran on the top-tier model vs the cheaper ones.
- **Cache-read share** — what share of your tokens are `cache_read` rather than fresh input.
  A high share means your caching is already working and is *not* a lever.
- **Peak-to-median week** — a large ratio means spiky weeks are your run-out risk, not steady ones.
- **Day-of-week shape** — which days you actually ramp, so you know when to pace.

A common signature for this kind of user: almost all turns on the top model, the large majority of
tokens being cache reads, and a peak week several times the median. If that matches you, rule 1 is
where nearly all of your savings are.

---

## The 5 Rules (in order of impact)

### 1. Default to the cheaper model. Escalate on purpose. ⟵ biggest lever
Every turn re-reads your (large) cached context. On the top-tier model that river costs several
times more per token.
- **Use the cheaper model for:** file reads, searches, straightforward edits, boilerplate, git/test
  runs, refactors with a clear spec, "make it match this pattern."
- **Keep the top model for:** architecture/design, gnarly debugging, ambiguous decisions,
  security-sensitive logic.
- Switch mid-session with `/model`. Note that `/fast` does **not** save budget.
- **Rule of thumb:** start every session on the cheaper model; upgrade the moment you hit something
  genuinely hard, then drop back.

### 2. Keep context lean — cache_read is taxed every turn.
A bloated context is a per-message tax that compounds over a long session.
- `/clear` at **task boundaries** (new, unrelated task = fresh context). This is the cheap reset.
- Do **not** `/compact` mid-task just to save tokens — it discards cache and forces expensive
  re-reads (cache_write costs far more than cache_read).
- Lean on subagents for searches and audits — they return the *conclusion*, not the file dumps,
  keeping your main context small.
- Set heavy subagents to the cheaper model so fan-out work doesn't burn your top-tier budget.

### 3. Be concise on output — it's your priciest token.
Output tokens cost far more than a cache read.
- Prefer **targeted edits** over full-file rewrites.
- Don't ask for regenerated large files when a diff will do.
- Trim verbose thinking on routine work; raise effort only for hard tasks.

### 4. Pace against the `wk` meter on your status line.
The status line in this repo shows `wk NN%`. Simple pace line — stay at or under it:

| By end of… | Weekly % should be under |
|---|---|
| Monday | ~15% |
| Wednesday | ~45% |
| Friday | ~70% |
| Sunday | 100% |

If `wk%` is **ahead** of the pace line → switch to the cheaper model and defer non-urgent heavy work.

### 5. Smooth the spikes (protects the 5-hour cap).
Marathon days can hit the **5-hour** throttle even when the weekly budget is fine.
- Break marathon sessions into chunks across the day.
- Batch the truly heavy work; don't run it back-to-back-to-back.

---

## Monday 90-second ritual
1. Fresh week → note the `wk` meter is near 0%. This is your full budget.
2. Set the session default to the cheaper model.
3. List this week's heavy/ambiguous tasks — those are your top-model reservations; everything else
   is the cheaper model.
4. Sanity-check against the pace table above each day.

**One-line version:** *Cheap model by default, top model on purpose, `/clear` between tasks, watch
`wk%` against the pace line.*
