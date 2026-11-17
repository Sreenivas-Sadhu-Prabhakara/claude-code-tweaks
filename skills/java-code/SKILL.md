---
name: java-code
description: Use when writing or reviewing Java / Spring Boot services — controllers, money types, OpenAPI codegen, validation, tests. Also use before estimating work on an inherited Java estate, where generated scaffolds routinely outnumber real services and make a codebase look far more complete than it is.
---

# Java / Spring Boot

## First, find out what is actually there

An inherited Java estate is usually part real and part generated scaffold, and the repo count tells
you nothing. In one audited estate, **7 of 162 services were real**; the other 155 were
byte-identical generated stubs. A second estate was **48 of 48 scaffolds** — an entire domain that
appeared to exist and did not.

Tells of a scaffold:

- `additionalProperties: true` left in the schema — nobody modelled the payload.
- A `ConcurrentHashMap` standing in for persistence.
- A comment to the effect of "Phase 2 replaces this".
- Byte-identical files across services once names are normalised.
- No tests, or tests that assert the stub's own placeholder.

**Check which services are actually deployed and serving traffic** before believing a count, and say
plainly in any estimate how many are real. This is the difference between a week and a quarter.

## Money

`BigDecimal` with an explicit scale and `RoundingMode`, or an integer minor-unit type. **Never
`double` or `float`.** Never rely on a default rounding mode — state it at every operation that can
produce a fraction.

On the wire, serialise money as a **quoted decimal string**, not a JSON number. A number is parsed
by some consumers into a 32-bit float and loses precision silently.

## OpenAPI codegen traps

Codegen is worth using and worth checking. Two failures that pass review if you only read the spec:

- **`type: number` becomes a 32-bit float** in several generators. For money, that is data loss.
  Specify `type: string` with a decimal `format`/`pattern` for monetary fields.
- **`format: decimal` may emit a quoted string** where your reader expects a number, or the reverse.

So after generating: **read the generated model**, not the spec, and confirm the types of every
monetary and identifier field. And note that a `git diff` check on generated output is vacuous if the
generator is deterministic and the spec did not change — it will pass while proving nothing. The
check that means something is a test asserting the serialised shape.

## Controllers and validation

- Validate at the boundary with `@Valid` plus explicit constraint annotations. Do not validate in
  the service layer and hope the controller is never called another way.
- One `@ControllerAdvice` for error mapping, returning a stable machine-readable code plus a human
  sentence.
- Never return an entity directly. Map to a response type, so a schema change is a deliberate API
  change.
- Constructor injection, `final` fields. No field injection.

## Transactions

- `@Transactional` on the service method that owns the unit of work, not sprinkled on repositories.
- Know your propagation and isolation; do not accept the default by accident on anything financial.
- Do not call an external service inside a transaction that holds locks.
- An audit write belongs in the same transaction as the change it records.

## Tests

- JUnit 5. `@SpringBootTest` sparingly — it is slow; prefer plain unit tests with a mocked
  collaborator.
- Containerised integration tests for repository and migration behaviour.
- Assert on the **serialised JSON** for anything with a money or date field. That is the only test
  that catches a serialisation regression, and serialisation is where this stack's real bugs live.

## Steal the good parts

An over-generated estate often still has genuinely good Helm charts, CI pipelines and contract-test
templates. Those are worth lifting even when the services themselves are not worth keeping.

## Before you call it done

- [ ] Compiles; static analysis clean
- [ ] No `double`/`float` anywhere near money; rounding mode explicit
- [ ] Generated models inspected for actual field types, not assumed from the spec
- [ ] A test asserts the serialised JSON shape for money and dates
- [ ] Validation at the boundary, errors mapped in one place
- [ ] If you reported scope on an inherited estate, you said how many services are real
