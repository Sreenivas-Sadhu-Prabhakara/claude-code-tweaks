---
name: microservices
description: Use when designing or changing a service boundary, a contract between services, a shared library, or deciding whether to build or buy a component. Covers contract-first work, the shared-code distribution trap, build-vs-buy split at the right seam, and what a service owes its operators.
---

# Microservices

Most pain in a service estate is not inside a service. It is at the seams: contracts, shared code,
and version skew between repos that each look correct on their own.

## Contract first

- The contract (OpenAPI, protobuf, schema) is the source of truth. Generate clients and models from
  it; never hand-roll a request shape a contract already defines.
- A contract change is an API change — version it, and support both shapes until every consumer has
  moved.
- **Verify what the generator emitted**, not what the spec says. Generators silently pick a type that
  loses data, especially for money and large integers. Read the generated model.
- A drift check that diffs generated output against committed output proves nothing when the
  generator is deterministic and the spec is unchanged. The check with teeth is a test asserting the
  **serialised shape** on the wire.

## Shared code: pick a distribution model and know its failure

- **Versioned dependency** — consumers upgrade deliberately. Slower, visible, safe.
- **Vendored copy** — consumers hold their own copy. Fast to change, and the trap below.

**If shared code is vendored, fixing it does not fix the consumers.** The fix lands only when each
consumer re-vendors. This presents as "I fixed the bug and it's still happening", and it is
especially vicious because every repo looks right in isolation.

So:

- After changing vendored shared code, grep every consumer and update each in the same change.
- Treat version skew between consumers as a bug in its own right, not a tolerable state. Services
  disagreeing on a shared type is how a screen dies for days while all the code reads correctly.
- Record which model you are using where a newcomer will see it.

## Define interfaces at the consumer

The service that *needs* a capability declares the interface it needs; the caller supplies something
satisfying it. This keeps a provider's changes from rippling and gives you the natural test seam.
Provider-declared interfaces drag their whole dependency graph into every consumer.

## Build vs buy: split at the seam, not by language

When evaluating whether to build a component, find where the **conformance burden** actually sits
before choosing. A worked example: for a regulated API profile, roughly 90% of the conformance
requirement lived in the authorization server and 10% in the resource servers. That makes the
decision "build the resource servers, buy the authorization server" — a build-vs-buy split — rather
than a language or framework debate, which is what the discussion will default to if nobody measures
first.

Two rules that follow:

- **Do not hand-roll security infrastructure without a credible library.** Check maintainership
  seriously: a pre-1.0 single-maintainer library, or one missing a mandatory part of the spec, is a
  disqualification, not a gap to fill later.
- **"Enforces the profile" is not "certified for the profile."** Verify a certification claim against
  the certifying body's own register before any document repeats it.

## Observability a service owes its operators

- **Structured logs** with a correlation id propagated across every hop. Without it, a multi-service
  failure is unreadable.
- **Health checks that do not depend on the database.** Otherwise a brief database blip rolls back a
  good deploy.
- **An audit trail for state changes**, written in the same transaction as the change.
- Honour the request context all the way down so shutdown drains instead of dropping work.

## Deployment reality

- Know what each pipeline actually deploys. "Merging to main deploys the service" and "merging to
  main deploys the front end" are frequently different answers, and assuming the generous one ships
  a half-release.
- Know whether migrations run from CI or at service boot. If at boot, a deploy that later fails
  health checks has already migrated.
- Preserve environment variables and secrets when deploying a new revision by hand. Deploying a new
  image without them is the classic way to take an environment down with a correct build.
- Keep a written rollback: the previous image tag or revision id, recorded before you deploy.

## Before you call it done

- [ ] Contract updated and clients regenerated; generated types inspected
- [ ] A test asserts the serialised wire shape, not just the spec
- [ ] If shared code changed, every consumer updated in the same change
- [ ] Correlation id propagated; health check independent of the database
- [ ] You know what the pipeline deploys, and what it does not
- [ ] Rollback target written down before deploying
