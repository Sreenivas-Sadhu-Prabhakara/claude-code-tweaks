#!/usr/bin/env python3
"""Claude Code usage status line.

Reads the statusLine JSON on stdin and prints one formatted line:

    ~/Code/my-project  │  5h ▆▆▁▁▁ 42%   wk ▆▁▁▁▁ 18%   ctx ▆▆▆▆▁ 71%  │  Opus 4.8

Meters (bar + percent), all native fields from Claude Code:
  5h  -> rate_limits.five_hour.used_percentage   (subscribers, after 1st API call)
  wk  -> rate_limits.seven_day.used_percentage   (subscribers, after 1st API call)
  ctx -> context_window.used_percentage          (null right after /compact)

Missing/null fields degrade to a dim "label –" placeholder; the script never
crashes the status line.
"""

import json
import os
import sys
import time

# ANSI codes.
GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"
DIM = "\033[2m"
RESET = "\033[0m"

BAR_WIDTH = 5
FILLED = "▆"
EMPTY = "▁"


def bar(pct, width=BAR_WIDTH):
    """Render a `width`-segment bar for a 0-100 percentage."""
    filled = round(pct / 100 * width)
    filled = max(0, min(width, filled))
    return FILLED * filled + EMPTY * (width - filled)


def color_for(pct):
    """Return the ANSI color code for a usage percentage.

    Contract (see ColorTests): green below 70, yellow from 70 to 90
    inclusive, red above 90. Return one of GREEN / YELLOW / RED.
    """
    if pct > 90:
        return RED
    if pct >= 70:
        return YELLOW
    return GREEN


def fmt_meter(label, pct):
    """Format one meter as `label bar pct%`, colored by threshold.

    A None value (field absent or null) renders a dim placeholder so the
    line stays intact for non-subscribers or right after /compact.
    """
    if pct is None:
        return f"{DIM}{label} –{RESET}"
    color = color_for(pct)
    reset = RESET if color else ""
    return f"{color}{label} {bar(pct)} {round(pct)}%{reset}"


def short_cwd(path, home=None):
    """Replace a leading home directory with `~`."""
    if not path:
        return "?"
    home = home if home is not None else os.path.expanduser("~")
    if path == home:
        return "~"
    if home and path.startswith(home + "/"):
        return "~" + path[len(home):]
    return path


def extract_pct(data, *path):
    """Walk a nested dict; return a float, or None if missing/null/non-numeric."""
    node = data
    for key in path:
        if not isinstance(node, dict):
            return None
        node = node.get(key)
    if isinstance(node, bool) or not isinstance(node, (int, float)):
        return None
    return float(node)


def extract_str(data, *path, default="?"):
    """Walk a nested dict; return a string value or `default`."""
    node = data
    for key in path:
        if not isinstance(node, dict):
            return default
        node = node.get(key)
    return node if isinstance(node, str) and node else default


def fmt_tokens(n):
    """Human-readable token count: 512, 15k, 11.3k, 2.1M."""
    n = int(n or 0)
    if n < 1000:
        return str(n)
    unit, div = ("M", 1_000_000) if n >= 1_000_000 else ("k", 1000)
    s = f"{n / div:.1f}".rstrip("0").rstrip(".")
    return s + unit


def fmt_reset(resets_at, now):
    """Countdown to a Unix-epoch reset time: '6d 4h', '3h 12m', '45m'.

    None (field absent) -> None so the caller can show a placeholder.
    """
    if resets_at is None:
        return None
    delta = int(resets_at - now)
    if delta <= 0:
        return "now"
    d, rem = divmod(delta, 86400)
    h, rem = divmod(rem, 3600)
    m = rem // 60
    if d > 0:
        return f"{d}d {h}h"
    if h > 0:
        return f"{h}h {m}m"
    return f"{m}m"


def render(data, home=None, now=None):
    """Build the two-line status line from the statusLine JSON dict."""
    if now is None:
        now = time.time()
    cwd = short_cwd(extract_str(data, "workspace", "current_dir", default=data.get("cwd", "")), home)
    model = extract_str(data, "model", "display_name")
    five_h = fmt_meter("5h", extract_pct(data, "rate_limits", "five_hour", "used_percentage"))
    week = fmt_meter("wk", extract_pct(data, "rate_limits", "seven_day", "used_percentage"))
    ctx = fmt_meter("ctx", extract_pct(data, "context_window", "used_percentage"))
    line1 = f"{cwd}  │  {five_h}   {week}   {ctx}  │  {model}"

    reset = fmt_reset(extract_pct(data, "rate_limits", "seven_day", "resets_at"), now)
    reset_txt = reset if reset is not None else "—"
    inp = fmt_tokens(extract_pct(data, "context_window", "total_input_tokens") or 0)
    out = fmt_tokens(extract_pct(data, "context_window", "total_output_tokens") or 0)
    line2 = f"{DIM}wk resets in {reset_txt}  ·  ↑ {inp} in  ·  ↓ {out} out{RESET}"

    return f"{line1}\n{line2}"


def main():
    try:
        data = json.load(sys.stdin)
        home = os.environ.get("HOME") or os.path.expanduser("~")
        sys.stdout.write(render(data, home))
    except Exception:
        # Never break the status line on bad/empty input.
        sys.stdout.write("")


if __name__ == "__main__":
    main()
