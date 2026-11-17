---
name: frontend-ui
description: Use before any change to a user interface — a screen, component, layout, theme, typography or spacing change, in any framework. Covers the type and shape ramp that keeps an app looking like one product, mobile-first verification, why UI guards miss shared components, and the states every screen owes its user.
---

# Front-end UI

A clean app is one with **few** decisions repeated consistently, not many decisions each locally
reasonable. Before changing a screen, find the ramp the app already uses and use it.

## Read the standard before the code

If the project has a written UI standard, read it first, and treat a rule's **status** as part of
the rule:

- **guarded** — a named test enforces it. Breaking it fails CI.
- **guarded in part** — the test pins a subset. The rest is on you.
- **live** — true on the reference screens, enforced by nothing.
- **target** — a ticket says it; the build does not do it yet.

**Never silently adopt a built value over a specified one.** If the code says 13px and the ticket
says 14px, the ticket wins and the difference belongs in a debt register, not in a quiet decision to
match the neighbours.

## The ramp

Five text styles are enough for an application. A representative set:

| Style | Size / line-height | Weight | Used for |
|---|---|---|---|
| Title | 24 / 30 | 500 | page titles |
| Heading | 16 / 22 | 600 | section and card headings |
| Body | 14 / 20 | 400 | ordinary text |
| Label | 14 / 20 | 600 | field labels, buttons, table headers |
| Small | 12 / 16 | 400 | captions, helper text |

With it: **nothing above 24px, no weight above 600, sentence case everywhere**, and five text
colours at most. Shape ramp: radii from a set of four (e.g. 4 / 8 / 12 / 0), **one** shadow used
only on floating layers, **no pills, no decorative circles**.

The point is not these exact numbers. It is that there is one list, it lives in one file, and
screens read from it rather than declaring their own sizes.

## Tokens are copied, not chosen

Colour, font and radius tokens live in exactly one place. Change them there and copy outward. Never
re-pick a value per screen, and never let a second source of truth appear — if two packages define
the palette, say explicitly which one the app reads and make the other's irrelevance obvious in a
comment, because the next person will read the wrong one.

## Mobile-first, and verify it

Design and **check** every screen at phone width (≤400px) *first*, then scale up. This applies to
web apps, not just native.

- Prefer compact controls — radio buttons, segmented toggles, choice chips — over stacked
  full-width cards.
- Let content wrap or scroll rather than overflow. No fixed pixel widths that break narrow layouts.
- Tap targets ≥ 48dp.
- Below the phone breakpoint, secondary app-bar actions go into a "More" menu.
- A UI change is **not done** until it is usable on a phone. Checking only the wide breakpoint is
  the most common way a "finished" change ships broken.

## Why your guards miss things

**Lint and theme guards usually scan only the application directory.** A shared widget imported from
a sibling package reaches the screen completely unchecked. That is how a decorative circle, or an
off-palette grey, lands in an app whose guards are green.

So: when a visual rule is violated and the guard passed, look in the shared packages first. And
when adding a guard, decide deliberately whether it should follow imports.

Also: an exemption marker on a *constant* exempts every use of that constant, not just the one you
meant. Prefer exempting at the use site.

## Every screen owes four states

Loading, empty, error, offline. Each is explicit, each is designed, and the error state offers a
retry when retrying could help. Specifically:

- An empty state must distinguish **"nothing matched your filter"** from **"there is nothing here"**.
  Blaming the wrong one sends the user hunting for a problem that isn't there.
- An error that tells the reader to retry must actually give them a retry control.
- A failed read that renders as empty is the worst case: it reads as a verified all-clear that was
  never checked. Render a failed probe as visibly as a missing one.

## Hierarchy

**One filled primary button per viewport.** Two or three means the eye lands on the wrong one and
the screen has no answer to "what am I meant to do here". Secondary actions get a quieter style; a
row of records gets one action style, not four.

And a control's label must match where it leads. A button that says "View project" and opens a
payment form is a bug, not a wording nit.

## Accessibility is not optional

- Contrast: 4.5:1 for body text, 3:1 for large text and meaningful non-text.
- **Never signal state with colour alone.** A selected segment at 1.45:1 against its neighbours is
  invisible; add a second cue — weight, an underline, a check.
- Keyboard focus must be visible *and* keep its label readable. A solid fill behind unchanged text
  can drop the label to near-zero contrast, which is worse than no focus style.
- Platform-specific: some canvas-based web renderers make text unselectable by default. Wrap content
  in the platform's selection affordance and use plain text widgets where selection matters.

## Judge letterforms on the real thing

Screenshot and fixture harnesses commonly substitute the font. Layout and spacing are testable
there; **typography is not**. Judge type on a real deployment.

## Before you call it done

- [ ] Read the project's standard, and respected rule status
- [ ] Every size, weight, colour and radius comes from the shared ramp
- [ ] Verified at ≤400px, not only wide
- [ ] One filled primary action in view
- [ ] Loading, empty, error and offline all designed; empty distinguishes filter from no-data
- [ ] Contrast checked, state never colour-only, focus visible with a readable label
- [ ] If a guard passed but something looks wrong, checked the shared packages
