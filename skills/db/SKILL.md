---
name: db
description: Use before writing or changing any SQL, schema, migration, or code that reads a database row — queries, migrations, CHECK constraints, money columns, multi-tenant filters, aggregate reads. Covers the serialisation traps that crash a UI from a correct query, migration ordering, and the tenancy and money rules that are not negotiable.
---

# Working with a database

Priority is **accuracy over everything**. A wrong number that renders is worse than an error that
doesn't — a crash gets fixed, a silently wrong balance gets trusted.

## Non-negotiable

- **Parameterized queries only.** Never build SQL by string interpolation, not even for an integer,
  not even in a migration, not even in a one-off script.
- **Every query in a multi-tenant system filters on `tenant_id`.** Not "most". A read that omits it
  is a data-leak bug even when it currently returns the right rows, because the next tenant makes it
  wrong. Put it in the `WHERE`, not in application code after the fetch.
- **Money is an integer in minor units** (cents, centavos, paise) — or whole units as `int64` where
  the domain has no subunit in practice. Never a float. Decide once per project and write it down;
  the bug is always a mix of the two conventions in one codebase.
- **Validate at the trust boundary**, before the value reaches SQL.

## The serialisation trap that crashes UIs

**A driver may send you a number as a string.** node-postgres serialises `numeric` and `count(*)`
as STRINGS to avoid precision loss. So a peso column arrives as `"245000.00"`, and
`COALESCE(sum(...),0)` arrives as `"0"`, and `count(*)` arrives as `"1"`.

In a strongly-typed consumer this is a crash, not a wrong value:

```dart
// WRONG — throws on a String. In Dart, `"1" as num?` does NOT return null.
(row['property_count'] as num?)?.toInt() ?? int.tryParse('${row['property_count']}') ?? 0
```

That line looks defended — the author clearly knew a string was possible, which is what
`int.tryParse` is for. But the cast throws **before** the `??` can run, so the fallback is dead
code. Thrown inside a render method, it takes the whole screen down to a blank slab rather than
degrading one cell.

**Write one coercion helper per project and route every numeric read through it:**

```dart
num? pgNumber(Object? v) {
  if (v is num) return v;
  if (v is String) return num.tryParse(v.trim());
  return null;   // absent or unparseable costs a dash, never the page
}
```

The general rule: **`as` asserts and throws; `is` narrows.** On a nullable cast only `null` is
exempt — every other wrong type is an exception. Prefer a type test over a cast on anything that
crossed a wire.

**Grep for the pattern when you inherit a codebase:** `as num`, `as int`, `as double` on anything
read from a row or a JSON payload. Better, add a lint that bans the cast outside the one helper, so
the next one cannot be written.

## Migrations

- **A CHECK constraint must widen before the application sends the new value.** Deploy the
  migration, confirm it, then ship the code. Reversed, the app's writes fail with a generic 400 and
  the cause is invisible — enum-ish CHECKs on audit or status columns are where this bites.
- **Read-modify-write anything that replaces a list.** A PATCH that takes an array usually replaces
  it wholesale rather than appending.
- Know whether migrations run from CI or from the service at boot. If at boot, a deploy that fails
  health checks may have already migrated.

## Reading a connection string

A managed-Postgres `DATABASE_URL` from a secret store is often the **unix-socket** form:

```
postgres://user:pass@/dbname?host=/cloudsql/project:region:instance
```

Parsed as an ordinary URL that yields **no host**. Take only user, password and database name from
it and override host/port to your local proxy.

## Extensions have their own casts

Vector columns need an explicit cast on the parameter — `$1::vector`, not `$1`. The same is true of
several extension types; a plain placeholder gives an unhelpful type error.

## Before you call it done

- [ ] Parameterized, with no interpolation anywhere in the statement
- [ ] `tenant_id` in every query touching tenant data
- [ ] Money in integer minor units, one convention project-wide
- [ ] Every numeric read from a row goes through the coercion helper
- [ ] A test feeds the **production shape** — if the driver sends strings, the fixture holds strings
- [ ] Migration deployed and confirmed before the code that depends on it
