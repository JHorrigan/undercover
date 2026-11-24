---
name: website-spec
description: Write the spec for a public website by interviewing James one topic at a time. Use when asked to spec, scope or plan the content of a website, landing page or other public pages. Not for agent, workflow or internal app builds.
---

# Website spec

Goal: a short `SPEC.md` for the app, in its `docs/` folder, that says what the site must do and why, never how. The spec is in James's words, and every gap is marked `<TBD: ...>`.

## How to run the interview

- One topic at a time, in the order below. Ask, listen, then write the section into `SPEC.md` straight away and show James what you wrote.
- Use James's words. Never invent facts, results, quotes, stats or customers. Write `<TBD: ...>` and move on.
- If James has an existing site, read it and use what works. Pages may be drawn by JavaScript, so ask for screenshots when a fetch shows nothing.
- An idea for later goes in the app's `IDEAS.md`, not the spec. An idea for another app goes in that app's `IDEAS.md`.
- A standard that applies to every front-end app belongs in `docs/WEB_STANDARDS.md`, not the spec. The spec adds only what is specific to this site.
- Anything that may cost money is marked for the plan, where its cost is approved first.
- When every section is done, James reads the whole spec and approves it before it is committed.

## The sections and what to ask

1. **Who it's for:** who visits, what stage they are at, and what each is looking for. How the business presents itself, and what it does not advertise.
2. **What it must achieve:** the one goal that matters most, such as booking a call, and what the visitor must believe to do it.
3. **How we'll know it works:** today's baseline, the first target, and what to track.
4. **Pages:** each page and its job. Reuse what works from any existing site. Ask about privacy and terms pages, a blog, and pages for each kind of visitor.
5. **What visitors can do:** every action, such as booking, a contact form or a checklist, and what happens next.
6. **Content:** who writes the copy, what is reused, and what evidence exists. No evidence means none is invented. The copy follows `docs/AI_SMELL.md`.
7. **What it collects:** each form's fields, where each submission goes, analytics and consent, and the privacy notice.
8. **Quality bar:** "Meets `docs/WEB_STANDARDS.md`", plus anything specific to this site.
9. **Look:** "Set by `docs/BRAND.md`". If the brand doc is empty, fill it from James's brand files first.
10. **Rules:** what the site does alone, what needs James's approval first, and what it must never do.
11. **Not for now:** everything deliberately left out of this version.
