---
name: go-code
description: Use when writing or reviewing Go — services, handlers, middleware chains, money types, tests, or vendored shared packages. Covers the seams that make a Go service testable, the vendoring trap that makes a fix appear not to land, and what belongs in the standard library instead of a dependency.
---

# Go

Go rewards the boring version. Prefer the standard library, a flat package layout, and explicit
wiring over anything clever.

## Dependencies

- `net/http`, `encoding/json`, `database/sql`, `context`, `log/slog`, `testing` cover most of a
  service. Reach past them only when the standard library genuinely cannot do the job.
- Never add a dependency for a few lines of code.
- A router is worth a dependency; an assertion library usually is not — `if got != want { t.Errorf }`
  reads fine and never surprises you.

## The three seams that make a service testable

Build these in from the start; retrofitting them is what makes Go services untestable.

```go
// 1. Middleware as a value, composed explicitly.
type Middleware func(http.Handler) http.Handler

func Chain(h http.Handler, ms ...Middleware) http.Handler {
    for i := len(ms) - 1; i >= 0; i-- {   // last listed runs innermost
        h = ms[i](h)
    }
    return h
}

// 2. Interfaces defined by the CONSUMER, not the provider.
// This package says what it needs; the caller supplies anything that satisfies it.
type ConsentClient interface {
    Check(ctx context.Context, id string) (bool, error)
}

// 3. An injected clock. Never call time.Now() inside business logic.
type Clock func() time.Time
```

The injected clock is the one people skip and always regret: without it, any test touching
expiry, windows or "today" is either flaky or has to sleep.

## Money

Define a money type and use it everywhere. Never `float64`.

```go
type Amount struct {
    Minor    int64  // cents / centavos / paise
    Currency string
}
```

Two serialisation traps on the boundary:

- **JSON `number` for money loses precision** in consumers that parse into a 32-bit float. Codegen
  from an OpenAPI spec will happily produce `float32` from `type: number`. Check what your generator
  emitted rather than trusting the spec.
- **Decimal strings are the safe wire format** — `"245000.00"`, quoted. Which means your *reader*
  must expect a string, not a number. Write the parse accordingly.

## Errors

- Wrap with context as it propagates: `fmt.Errorf("fetching user %s: %w", id, err)`.
- `errors.Is` / `errors.As` at the boundary where you decide the response.
- **Never discard an error to make a signature tidy.** `_ = doThing()` is a decision, and if it is
  the right one it needs a comment saying why.
- A handler returns *either* a rendered error *or* success. Never both, never neither.

## Vendored shared packages

If services vendor a shared package rather than consuming it by version, **fixing the shared package
does not fix the consumers**. The fix lands only when each consumer re-vendors. This presents as "I
fixed it and the bug is still there", and it can waste days.

So: after changing a vendored shared package, grep the consumers for the vendored copy and update
each one in the same change. If services disagree about the vendored version, that skew is itself a
bug — screens and endpoints die from it while every repo looks correct in isolation.

## Tests

- Table-driven by default. One `t.Run` per case, named for the behaviour.
- `t.Parallel()` where there is no shared state, and remember the loop-variable capture rule for
  your Go version.
- Fixtures must carry the **production shape**. A fixture typed more narrowly than reality cannot
  express the value that actually breaks you — if a driver sends numbers as strings, the fixture
  holds strings.
- Containerised integration tests for anything touching a real database; keep them a separate tier
  from unit tests so the fast suite stays fast.
- New non-trivial logic leaves a test. Trivial changes need none.

## Deploying to a container platform

- Read the port from the environment with a local default. Hardcoding it works locally and fails on
  deploy.
- `context` from the request, honoured all the way down, so a shutdown actually drains.
- Health checks must not depend on the database, or a brief database blip rolls your deploy back.
- Keep generated code and build inputs out of source control deliberately — but then **document what
  must be generated or copied before a build works**, because a fresh clone that cannot compile is
  indistinguishable from a broken commit.

## Before you call it done

- [ ] `go build ./...` and `go vet ./...` clean
- [ ] `gofmt` applied
- [ ] Errors wrapped with context; none silently discarded
- [ ] Money is integer minor units; the wire format's type is verified, not assumed
- [ ] Clock injected wherever time matters
- [ ] If a shared vendored package changed, every consumer re-vendored in the same change
