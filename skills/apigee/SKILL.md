---
name: apigee
description: Use when building, deploying or debugging an Apigee X API proxy — policy XML, routing, auth stacks (API key / OAuth2 / JWT), fault handling, TargetServers, environment groups, or southbound Private Service Connect. Covers the policy traps that each cost a debugging round and the limits of a trial organisation.
---

# Apigee X proxies

Verify policy XML against the current docs before authoring. Apigee's policy surface has many
near-identical spellings where only one works, and a wrong one usually fails at runtime, not at
import.

## Build pattern that works

1. Research and verify the policy XML syntax for every policy you intend to use.
2. Author the bundle.
3. Adversarial review of the bundle before deploying — assume each policy is wrong and check.
4. Deploy.
5. Live smoke test against the runtime host, with a numbered pass/fail count.

Steps 1 and 3 are the ones people skip, and they are the ones that save rounds.

## Policy traps, each learned the hard way

- **`<Property name="copy.pathsuffix">false</Property>` is IGNORED.** Set the runtime *variable*
  `target.copy.pathsuffix` to `false` in the target PreFlow instead. A property and a variable with
  the same name are not the same thing.
- **An `AssignMessage` in the request flow cannot set a non-200 status on a targetless route.**
  Route synthetic errors through **RaiseFault → FaultRule** instead.
- **Auth policies must exclude the token endpoint** in their step `<Condition>`. Otherwise minting a
  token requires a token and the flow deadlocks.
- **A credential-stripping policy must only strip for backend-bound requests.** Strip
  indiscriminately and you remove the Basic auth the token endpoint needs, or the bearer the JWT
  verifier needs.
- **ProxyEndpoint FaultRules evaluate bottom-to-top. TargetEndpoint FaultRules evaluate
  top-to-bottom.** Ordering a list the wrong way means the wrong rule wins.
- **VerifyJWT with no token at all throws `FailedToResolveVariable`**, surfacing as a 500, unless
  your fault rule matches that condition alongside `FailedToDecode` / `InvalidClaim`. Handle the
  missing-token case explicitly.
- **A key from the wrong product gives `oauth.v2.InvalidApiKeyForGivenResource` as a 401.** It is an
  authorization failure, so remap it to 403.
- **`action=validate` returns no revision number.** Only `action=import` does. Scripts that parse the
  revision out of a validate response get nothing.
- **An environment-group hostname PATCH replaces the whole list.** Always read-modify-write, and
  provide a teardown script — mutating a shared environment group affects every proxy in it.

## Resolve routing once

When routing on several inputs (a header, then Host, then path), resolve them into **one variable**
in a single JavaScript policy, and have both the route rules and the authorization policies read
that variable. Two independent resolutions of "which backend is this" will disagree eventually, and
when they do, authorization is applied to a different backend than the one that serves the request.

## TargetServers

- **A TargetServer is not a proxy.** Repoint a backend by updating the TargetServer; the proxy
  refers to it by name and needs no change.
- **If the backend is behind a tunnel or any TLS edge, the port is 443 with TLS enabled** — not the
  application's own port. The application port is the recurring wrong value and it fails *silently*,
  showing as an unreachable backend rather than an error.

## Host headers and southbound PSC

- **Apigee overrides the outbound Host header to the target host.** An `AssignMessage` setting Host
  does **not** survive. So any backend that is strict about Host — anything behind a CDN that
  validates it — is unreachable this way. Choose a Host-agnostic origin or terminate differently.
- **Load balancers generally cannot rewrite Host** either; custom-request-header directives reject
  it. So route an internal load balancer **by path**, set verbatim via `target.url`, rather than
  trying to fix up Host.
- A **cross-region** internal Application LB rejects internet NEG backends. Use a **regional** one.
- A proxy-only subnet needs **Cloud NAT** to reach public origins. Without it, everything times out.
- `--allow-global-access` must be set on the forwarding rule **before** creating the Apigee endpoint
  attachment. It cannot be added afterwards.
- An `import` of a URL map can silently no-op. Create a fresh map and repoint the target proxy
  rather than trusting an in-place update.

## Trial and evaluation organisations

Check the org's `expiresAt` through the management API **before** planning work on it — evaluation
orgs expire roughly 60 days after creation, taking the deployed proxies with them. Anything you
record as "live" in a trial org should carry that date beside it.

Typical trial limits that shape a design:

- JavaScript policies must finish in ~200 ms.
- JavaScript is ES5 only (Rhino) — no modern syntax, no `let`, no arrow functions.
- All outbound HTTP from a policy goes through **ServiceCallout**.
- Key-value map values cap at ~10 KB.

## Tooling

Drive the management API with a bearer token from your cloud CLI's `print-access-token`. Do not
assume a convenience CLI is installed — raw `curl` against the management API always works and is
what a script should use if the helper's presence is not guaranteed.

## Secrets

A demo HS256 secret sitting in policy XML is fine for a demo and must be labelled as such in the
repo. For anything real, move it to an encrypted key-value map. Git-ignore every environment file,
every local Postman environment, and every generated key file — and verify the ignore actually
matches before the first commit, not after.
