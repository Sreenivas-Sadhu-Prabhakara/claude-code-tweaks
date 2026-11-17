"""Tests for the Claude Code usage status line.

Pure-function tests: feed fixture JSON dicts, assert the rendered text.
ANSI color codes are stripped before structural assertions so that color
(the TODO(human) piece) is tested separately from layout.
"""

import re
import unittest

import statusline as sl

ANSI = re.compile(r"\x1b\[[0-9;]*m")


def plain(s):
    """Strip ANSI escape codes so we assert on visible text."""
    return ANSI.sub("", s)


class BarTests(unittest.TestCase):
    def test_bar_fills_proportionally_to_percent(self):
        # Derived from the approved previews.
        self.assertEqual(sl.bar(42), "▆▆▁▁▁")
        self.assertEqual(sl.bar(71), "▆▆▆▆▁")
        self.assertEqual(sl.bar(18), "▆▁▁▁▁")

    def test_bar_empty_and_full_bounds(self):
        self.assertEqual(sl.bar(0), "▁▁▁▁▁")
        self.assertEqual(sl.bar(100), "▆▆▆▆▆")


class CwdTests(unittest.TestCase):
    def test_short_cwd_replaces_home_with_tilde(self):
        got = sl.short_cwd("/Users/you/Code/my-project", home="/Users/you")
        self.assertEqual(got, "~/Code/my-project")

    def test_short_cwd_leaves_non_home_paths(self):
        got = sl.short_cwd("/tmp/work", home="/Users/you")
        self.assertEqual(got, "/tmp/work")


class MeterTests(unittest.TestCase):
    def test_meter_shows_label_bar_and_percent(self):
        self.assertEqual(plain(sl.fmt_meter("5h", 42)), "5h ▆▆▁▁▁ 42%")

    def test_meter_rounds_fractional_percent(self):
        self.assertEqual(plain(sl.fmt_meter("wk", 41.2)), "wk ▆▆▁▁▁ 41%")

    def test_meter_absent_value_shows_placeholder(self):
        self.assertEqual(plain(sl.fmt_meter("wk", None)), "wk –")


class ExtractTests(unittest.TestCase):
    def test_extract_pct_reads_nested_path(self):
        data = {"rate_limits": {"seven_day": {"used_percentage": 18.0}}}
        self.assertEqual(sl.extract_pct(data, "rate_limits", "seven_day", "used_percentage"), 18.0)

    def test_extract_pct_missing_path_returns_none(self):
        self.assertIsNone(sl.extract_pct({}, "rate_limits", "five_hour", "used_percentage"))

    def test_extract_pct_null_value_returns_none(self):
        data = {"context_window": {"used_percentage": None}}
        self.assertIsNone(sl.extract_pct(data, "context_window", "used_percentage"))


NOW = 1_000_000_000  # fixed epoch so reset countdowns are deterministic


class TokenFmtTests(unittest.TestCase):
    def test_round_thousands_drop_decimal(self):
        self.assertEqual(sl.fmt_tokens(188000), "188k")
        self.assertEqual(sl.fmt_tokens(15000), "15k")

    def test_keeps_one_decimal_when_meaningful(self):
        self.assertEqual(sl.fmt_tokens(11300), "11.3k")

    def test_under_thousand_is_raw(self):
        self.assertEqual(sl.fmt_tokens(512), "512")

    def test_millions(self):
        self.assertEqual(sl.fmt_tokens(2100000), "2.1M")


class ResetFmtTests(unittest.TestCase):
    def test_days_and_hours(self):
        self.assertEqual(sl.fmt_reset(NOW + 6 * 86400 + 4 * 3600, NOW), "6d 4h")

    def test_hours_and_minutes(self):
        self.assertEqual(sl.fmt_reset(NOW + 3 * 3600 + 12 * 60, NOW), "3h 12m")

    def test_minutes_only(self):
        self.assertEqual(sl.fmt_reset(NOW + 45 * 60, NOW), "45m")

    def test_absent_returns_none(self):
        self.assertIsNone(sl.fmt_reset(None, NOW))


class RenderTests(unittest.TestCase):
    def full_fixture(self):
        return {
            "workspace": {"current_dir": "/Users/you/Code/my-project"},
            "model": {"display_name": "Opus 4.8"},
            "context_window": {
                "used_percentage": 71.0,
                "total_input_tokens": 188000,
                "total_output_tokens": 15000,
            },
            "rate_limits": {
                "five_hour": {"used_percentage": 42.0},
                "seven_day": {
                    "used_percentage": 18.0,
                    "resets_at": NOW + 6 * 86400 + 4 * 3600,
                },
            },
        }

    def test_render_line1_is_the_meters(self):
        lines = plain(sl.render(self.full_fixture(), home="/Users/you", now=NOW)).split("\n")
        self.assertEqual(
            lines[0],
            "~/Code/my-project  │  5h ▆▆▁▁▁ 42%   wk ▆▁▁▁▁ 18%   ctx ▆▆▆▆▁ 71%  │  Opus 4.8",
        )

    def test_render_line2_has_reset_and_tokens(self):
        lines = plain(sl.render(self.full_fixture(), home="/Users/you", now=NOW)).split("\n")
        self.assertEqual(lines[1], "wk resets in 6d 4h  ·  ↑ 188k in  ·  ↓ 15k out")

    def test_render_without_rate_limits_shows_placeholders(self):
        # Non-subscriber, or before the first API response.
        data = self.full_fixture()
        del data["rate_limits"]
        got = plain(sl.render(data, home="/Users/you", now=NOW))
        self.assertIn("5h –", got)
        self.assertIn("wk –", got)
        self.assertIn("ctx ▆▆▆▆▁ 71%", got)
        self.assertIn("wk resets in —", got)

    def test_render_null_context_after_compact(self):
        data = self.full_fixture()
        data["context_window"]["used_percentage"] = None
        got = plain(sl.render(data, home="/Users/you", now=NOW))
        self.assertIn("ctx –", got)


class ColorTests(unittest.TestCase):
    """The TODO(human) contract: thresholds green < 70, yellow 70-90, red > 90."""

    def test_color_for_low_is_green(self):
        self.assertEqual(sl.color_for(50), sl.GREEN)

    def test_color_for_mid_is_yellow(self):
        self.assertEqual(sl.color_for(80), sl.YELLOW)

    def test_color_for_high_is_red(self):
        self.assertEqual(sl.color_for(95), sl.RED)


if __name__ == "__main__":
    unittest.main()
