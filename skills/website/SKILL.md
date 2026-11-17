---
name: website
description: Use when building, changing or deploying a marketing or small-business website — static sites, landing pages, SEO, contact forms, domains, or a deploy to Netlify, Cloudflare Pages, GitHub Pages or FTP hosting. Covers the deploy trap where a git push publishes nothing, and the content rules that keep a client site honest.
---

# Websites

Static first. A small-business site is HTML, CSS and a form endpoint. Reach for a framework when
there is real content to template, and a static site generator before anything with a server.

## The deploy trap: find out what actually publishes

**A git push does not necessarily deploy the site.** Before changing anything, establish how the
live site is published, because the four common answers behave completely differently:

| How it's hosted | How it deploys | The trap |
|---|---|---|
| Host connected to the git repo | push to the default branch | none — the normal case |
| Host **not** connected to the repo | the host's **CLI**, by hand | **a push deploys nothing.** The repo goes stale-looking while the live site is fine, or you "deploy" for an hour and nothing changes |
| Pages-style direct upload | an upload command with a project name and a token | the token lives in a git-ignored file; without it you cannot deploy at all |
| Classic shared hosting (cPanel) | **FTP** | no git anywhere in the path; the repo is only your copy |

Write the answer into the repo's README the first time you learn it. This single fact is the most
common half-hour wasted on a small site, and it is invisible from the code.

Related: if a site is served from a branch or a `/docs` directory, a build that writes elsewhere
publishes nothing. Check the configured source, not the build output.

## Domains

- Check expiry and registrar lock state **before** promising a launch date. A domain on registrar
  hold serves nothing no matter how good the deploy is.
- Apex vs `www` is a real decision; pick one as canonical and redirect the other.
- A stale apex record pointing at an old host is a common cause of "my changes aren't showing" when
  the deploy genuinely succeeded. Verify what the live hostname resolves to.

## Content rules for client sites

These are honesty constraints, not style preferences:

- **Never state a price, a rate, or a numeric claim that the client has not given you.** No
  "starting from", no illustrative figures, no placeholder that reads as real. If a number is
  needed and absent, leave the space and ask.
- **Never invent credentials** — no awards, certifications, years-in-business or client counts
  without a source. "Est. 1990" needs the client to have said 1990.
- Use the contact details that exist. If the business only has a landline, the site has a landline;
  do not invent a mobile or an email to fill a form.
- Photography-led beats CSS-illustration-led for trades, food, fitness and construction. A page of
  gradients where photographs belong reads as a placeholder, however neat the code.

## SEO, in order of effect

1. One `<h1>` per page, and a `<title>` that names the service **and** the place — local intent is
   most of the traffic for these sites.
2. A meta description per page, written for a human.
3. `LocalBusiness` structured data with address, hours and phone, and Google Business Profile
   details matching the site **exactly**.
4. Real content. A page per service beats one page listing services.
5. Images: descriptive filenames, real `alt` text, correctly sized, lazy-loaded below the fold.
6. Speed. Static, few requests, no framework you are not using, system fonts or one subset web font.

## Forms

- Confirm the form endpoint actually delivers, to the address the client reads, with a live test
  before calling it done.
- Spam protection from the start — honeypot at minimum.
- A visible success state and a visible failure state. A form that silently fails loses the lead and
  nobody finds out for a month.

## Analytics and tracking pixels

Add them only when asked, and say in the repo which are present. A tracking pixel is a privacy
decision made on the client's behalf and on their visitors' behalf.

## Before you call it done

- [ ] You know how this site deploys, and it is written in the README
- [ ] Deployed and the change verified on the live URL, not just locally
- [ ] No price, credential or contact detail that the client did not supply
- [ ] `<title>`, one `<h1>`, meta description, structured data
- [ ] The contact form was submitted end to end and the message arrived
- [ ] Checked at phone width
