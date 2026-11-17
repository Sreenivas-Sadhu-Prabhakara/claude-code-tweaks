---
name: python-code
description: Use when writing or reviewing Python — scripts, tooling, hooks, status lines, data munging, small services. Covers standard-library-first choices, writing integrations that degrade instead of crashing their host, pure functions tested on fixtures, and running code that reads untrusted files safely.
---

# Python

Prefer the standard library. `json`, `pathlib`, `subprocess`, `argparse`, `dataclasses`, `re`,
`unittest`, `datetime`, `sqlite3` cover most tooling without a single install.

## Structure a script as pure functions plus a thin `main`

This is the single highest-value habit, because it makes the script testable without mocking
anything:

```python
def bar(pct, width=5):                 # pure: int -> str
    filled = max(0, min(width, round(pct / 100 * width)))
    return "▆" * filled + "▁" * (width - filled)

def render(data, now=None):            # pure: dict -> str; `now` injected
    ...

def main():                            # thin: I/O only
    try:
        sys.stdout.write(render(json.load(sys.stdin)))
    except Exception:
        sys.stdout.write("")           # see below
```

Inject `now` rather than calling `time.time()` inside logic, so countdown and window behaviour is
deterministic in tests.

## An integration must degrade, not crash its host

When your script is a hook, status line, plugin or anything another program invokes, **it must never
take the host down.** Two rules:

1. **Wrap the whole entry point** and write a sane fallback on any exception. A broken status line
   that prints nothing is a nuisance; one that raises is a broken terminal.
2. **Treat every field as absent.** Walk nested input defensively and return `None` rather than
   raising:

```python
def extract(data, *path):
    node = data
    for key in path:
        if not isinstance(node, dict):
            return None
        node = node.get(key)
    if isinstance(node, bool) or not isinstance(node, (int, float)):
        return None      # bool is a subclass of int — exclude it deliberately
    return float(node)
```

That `isinstance(node, bool)` check is not pedantry: `True` passes `isinstance(x, int)`, so without
it a boolean field silently renders as `1`.

Render a missing value as a visible placeholder. Fields legitimately go missing — an upstream value
may be absent until the first call of a session, or null right after a reset — and a dim `–` tells
the truth where a `0` lies.

## Running code that reads untrusted files

Downloaded archives, scraped data and user-supplied directories are untrusted input:

- Put the data in its own empty directory. Keep your scripts in a **different** directory.
- Pass paths as **arguments**; never run the interpreter from inside the data directory.
- Run with **`python3 -I`** (isolated mode). Python adds the script's directory to `sys.path`, so a
  planted `json.py` sitting next to the data gets imported by `import json`.
- Use `-B` when you do not want `__pycache__` written beside files you are only reading.

## Subprocess

- `subprocess.run([...], capture_output=True, text=True)` with a **list**, never a string with
  `shell=True`.
- Always check the return code, or pass `check=True` and handle the exception.
- Set a `timeout`. A hung child process in a hook hangs the host.

## Types and errors

- Type-hint public functions; explicit return types. Hints are documentation that a checker can
  verify.
- Catch the specific exception. A bare `except Exception` is acceptable at exactly one place — the
  outermost boundary of an integration, as above — and nowhere else.
- No mutable default arguments.
- Use `pathlib`, not string concatenation, for paths.
- Open text files with an explicit `encoding="utf-8"`.

## Tests

`unittest` from the standard library is enough.

```python
class RenderTests(unittest.TestCase):
    def test_absent_field_shows_placeholder(self):
        self.assertIn("wk –", plain(render({})))   # the degraded path is a test case
```

- Test the **degraded** paths explicitly — absent fields, null values, unparseable input. Those are
  what actually happen in production.
- Strip formatting (ANSI codes, whitespace) before asserting on structure, so colour and layout are
  tested separately rather than one assertion failing for two unrelated reasons.
- Fixed constants for time, so countdowns assert exactly.

## Before you call it done

- [ ] Logic is pure functions; `main` only does I/O
- [ ] Nothing writes to a path outside the directory it was given
- [ ] If it's an integration, the entry point cannot raise and missing fields show placeholders
- [ ] `subprocess` calls use a list, check the result, and set a timeout
- [ ] Degraded paths have tests, not just the happy path
- [ ] Anything reading untrusted files runs with `-I` and takes paths as arguments
