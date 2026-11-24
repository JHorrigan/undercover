# Web standards

Every front-end app meets these, whatever it is for. An app's `SPEC.md` adds only what is specific to it. Each standard is checked automatically in CI wherever a tool can do it. Where a standard needs a paid service, the plan picks the tool and its cost is approved first.

## Mobile & speed

- Mobile first: every page works well on a phone before it is styled for larger screens.
- Lighthouse scores 90 or more for performance, accessibility, best practices and SEO on every page, checked with Lighthouse CI. A page with a 3D signature moment may score 80 or more for performance, as long as its Core Web Vitals stay in the good range.
- Core Web Vitals in Google's "good" range: LCP within 2.5 seconds, INP within 200 milliseconds, CLS under 0.1.
- Images sized for the screen and served in modern formats. Fonts loaded without shifting the page.

## Accessibility

- WCAG 2.2 level AA: usable with a keyboard and a screen reader, with enough colour contrast.
- Checked with axe in the Playwright tests.

## SEO

- Every page has its own title, description and canonical URL.
- A sitemap and a `robots.txt`.
- Structured data (schema.org JSON-LD) for the organisation, its people, articles, FAQs and breadcrumbs, as each page needs.
- Link previews for social media: Open Graph and X card tags, with an image for each page.
- Clean, readable URLs. A helpful 404 page.
- When a site replaces an old one, the old URLs redirect to their new pages so search rankings carry over.
- Images have alt text.

## AEO

So that AI answer engines, such as ChatGPT and Google's AI answers, can read the site and quote it:

- Pages are rendered on the server, so crawlers read the full content without running scripts.
- Headings ask the questions visitors ask, and the text under each answers it directly.
- FAQ sections, with matching structured data.
- An `llms.txt` that describes the site and links to its key pages.
- Clear facts about who is behind the site: the company, its founder and how to reach them.
- Every stat cites its source and the date it was last checked.
- `robots.txt` allows AI crawlers, unless the app's spec says otherwise.

## Analytics

- Nothing that tracks a visitor runs until they agree to it in a cookie consent banner. Without consent, only anonymous visits are counted.
- Every conversion, such as a form sent or a call booked, is tracked as an event.
- Campaign links use UTM tags, so each visit's source is known.
- The site is registered with Google Search Console.

## Privacy & legal

- A Privacy Notice and Terms, linked from every page.
- UK GDPR: collect only what is needed, say why, and say how to ask for it to be deleted.

## Security

- HTTPS only, with security headers: a content security policy, HSTS and the rest of the usual set. A static, cached site allows inline scripts in its policy, since a per-request nonce would make every page render on a Lambda for each visit; the policy locks everything else to the site itself. HSTS starts as `max-age` only: `includeSubDomains` and `preload` commit the whole domain, so they wait for James.
- Every stage but production sends `noindex` and a disallow-all `robots.txt`, and asks for a password before anything loads. A stage may have its own address under the production domain, such as `dev.example.com`, so it works the same as production (James, 1 November 2026).
- Forms are protected against spam and abuse.
- Emails the site sends pass SPF, DKIM and DMARC, so they are not marked as spam.
- No secrets in the front end.

## Reliability

- Uptime monitoring, which alerts when the site goes down.
- Error tracking, which records errors in the browser and the API.
