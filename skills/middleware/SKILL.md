---
name: middleware
description: Use when writing or changing an API handler, auth gate, authorization check, audit write, or any staff-acting-on-behalf-of-a-user capability. Covers the read-vs-write authorization split, what status code to return so responses don't leak existence, step-up for privileged writes, and putting the audit row inside the transaction.
---

# API middleware and authorization

The recurring class of bug here is not a missing check. It is a check that exists on the read path
and not the write path, or a check that validates the wrong subject.

## Diagnose before you fix

**The status code tells you which layer answered.** Learn your stack's tells and read them before
touching code:

- **401** — the auth gate. The session is absent, expired or malformed.
- **403** — the application's authorization. The session was *valid*; the role was refused. So a 403
  on a write while the read of the same resource returns 200 is not a session problem, and changing
  the login flow will not fix it.
- **404** — may be a real miss, or a deliberate existence-hiding refusal (see below), or the wrong
  service answered entirely. The **message body** usually says which.

A related tell: an HTML error body from a platform (a Google/AWS error page) means the request never
reached your app — infrastructure refused it. A JSON error body in your app's own shape means your
code ran and said no. Those need completely different fixes, and confusing them wastes a session.

## Read and write are different gates

A resource surface usually has a scope resolver for reads (owner **or** staff) and a narrower check
for writes (owner only). That is often correct and deliberate. When a new capability needs staff to
write, change the gate — don't widen the resolver and hope.

```js
// On-behalf write, the shape that holds up:
const scope = resolveScope(req.user.role, req.query.targetId, req.user.id);
if (!scope.allowed) throw httpError(403, 'FORBIDDEN');
const targetId = scope.targetId;
const onBehalf = targetId !== req.user.id;

if (onBehalf && !(await stepUpPassed(req, res))) return;  // MFA for privileged writes

validateBody(req.body);              // cheap checks before any I/O
if (!isUuidShape(targetId)) throw httpError(404, 'NOT_FOUND');

const target = await pool().query('SELECT role FROM users WHERE id=$1', [targetId]);
if (!target.rowCount || !isEligible(target.rows[0].role)) {
  throw httpError(404, 'NOT_FOUND');
}
```

Four decisions in that snippet, each learned from a real hole:

1. **Validate the target on EVERY path, not just when it differs from the caller.** Guarding the
   target check behind `if (onBehalf)` lets a staff caller who simply *omits* the target id attach
   the write to their own account. The omitted-id case must be refused, never defaulted.
2. **404, not 403, for a missing or wrong-kind id.** A 403 confirms the id exists. Return the same
   404 for "no such id" and "that id is the wrong kind of account" so the response is not an
   existence oracle.
3. **Step up privileged writes.** Acting on another account's behalf is a different act from acting
   on your own. Require a fresh factor, and keep self-service un-stepped-up so normal use is not
   punished. Match whatever the sibling privileged write already does — consistency here is a
   security property.
4. **Cheap body validation before expensive I/O**, so a malformed request costs nothing.

## Consent is not delegable by default

Separate *doing work for someone* from *agreeing on their behalf*. Uploading a document for a user
can be a legitimate staff capability. Accepting a legal agreement as them is not — consent stays the
account holder's own act unless someone with authority decides otherwise in writing.

## Audit

- **Write the audit row inside the same transaction as the change.** Outside it, a rollback leaves a
  record of something that never happened, or a crash loses the record of something that did.
- Record **actor** (who did it) and **subject** (whose data), separately. They differ on exactly the
  on-behalf paths that matter most.
- Use the resource type that the audit table's index expects, or the row is written and never found.
- Decide deliberately whether self-service actions are audited. Auditing everything is defensible;
  auditing only privileged acts is defensible. Auditing inconsistently is not.
- **Widen the audit table's CHECK constraint before shipping code that emits a new event type**, or
  the events are silently rejected as 400s and you lose the trail you were building.

## Transactions and external I/O

Do not hold a row lock across a network call. If a transaction spans an object-store write, keep
existence checks *outside* it: `SELECT ... FOR UPDATE` on the target would hold a lock for the
duration of external I/O to close a narrow race. Take the race.

## Error responses

- Return a stable machine-readable code plus a human sentence. Clients branch on the code.
- Never return a raw driver error. It leaks schema and sometimes the query.
- **A failed action must not look like a successful one.** Swallowing an error in a handler — or in
  the client that calls it — is the worst bug in this whole area, because the operator believes work
  was done. Every failure path either renders an error or throws.

## Before you call it done

- [ ] The write path's gate was changed, not the read path's resolver
- [ ] The target is validated on every path, including when the caller omits it
- [ ] Existence is hidden with a consistent 404
- [ ] Privileged writes require step-up, matching the sibling privileged write
- [ ] The audit row is inside the transaction, with actor and subject distinguished
- [ ] A test exists per caller kind — owner, staff with and without step-up, wrong role, omitted id
