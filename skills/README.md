# Skills

Claude Code skills for the domains I work in. A skill is a Markdown file that Claude loads when the
task matches its `description`, so these are my standards and hard-won gotchas written where they
get applied automatically, instead of in a wiki nobody opens.

| Skill | Use it for | The thing it exists to prevent |
|---|---|---|
| [`website`](website/SKILL.md) | static sites, SEO, domains, deploys | assuming a `git push` deploys the site when the host isn't connected to the repo |
| [`frontend-ui`](frontend-ui/SKILL.md) | any UI change, any framework | a screen that invents its own sizes, and shared components slipping past UI guards |
| [`microservices`](microservices/SKILL.md) | service boundaries, contracts, build-vs-buy | fixing vendored shared code and wondering why consumers still break |
| [`java-code`](java-code/SKILL.md) | Java / Spring Boot | estimating an inherited estate where most "services" are generated scaffolds |
| [`go-code`](go-code/SKILL.md) | Go services and middleware | untestable logic from an un-injected clock, and float money |
| [`python-code`](python-code/SKILL.md) | scripts, tooling, hooks, status lines | an integration that crashes its host instead of degrading |
| [`db`](db/SKILL.md) | SQL, schema, migrations, money columns | a driver sending a count as a string and a cast crashing the render |
| [`middleware`](middleware/SKILL.md) | handlers, auth, authorization, audit | a write path whose gate is narrower than its read path, validating the wrong subject |
| [`apigee`](apigee/SKILL.md) | Apigee X proxies and policies | policy XML that imports cleanly and fails at runtime |

They share a spine, which is worth stating once rather than nine times:

- **Accuracy > quality > speed > quantity.** A wrong number that renders beats nothing, in the worst
  possible way — an error gets fixed, a silently wrong value gets trusted.
- **Never hallucinate an import, an API or a signature.** Read the generated model, not the spec.
  Check what the tool emitted, not what it should have.
- **Diagnose before fixing.** The status code, the error body and which layer produced them usually
  name the bug.
- **Scope discipline.** Don't touch files outside the task; don't refactor unless asked.
- **Money is never a float**, and one convention per codebase.
- **Validate at trust boundaries**, and in a multi-tenant system every query filters on the tenant.
- **A fixture must carry the production shape.** A test typed more narrowly than reality cannot
  express the value that breaks you — this is how a green suite ships a crash on a screen it covers.
- **Verify before claiming done.** Run the command, read the output, then say it works.

## Install

Copy any skill folder into `~/.claude/skills/`:

```bash
cp -r skills/db ~/.claude/skills/
```

Claude Code picks it up at the next session start and loads it when a task matches its description.
For a project-specific skill, use `.claude/skills/` inside that repo instead.
