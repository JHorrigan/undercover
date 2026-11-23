# Design process

Every front-end app is designed this way before its pages are built. The aim is a site people remember: one strong idea, motion that means something, and nothing that looks like the average of every other site. Run it with the `design-direction` skill.

Each app keeps its design work in its own `docs/design/`, such as `site/docs/design/`.

## 1. References

Gather 15 to 20 sites from Awwwards, Godly, Land-book, SiteInspire, Motion Sites and the Codrops demos. Look at each with Playwright at phone and desktop sizes. In `docs/design/REFERENCES.md`, list each one's link and what is worth taking from it: a scroll effect, a type treatment, a transition, a layout. Screenshots stay out of git; the links and notes are the record. James picks the ones that land.

## 2. One big idea

One concept the whole site moves around, drawn from the business itself, not from a trend. Every section, animation and video serves it. Offer two or three, and James chooses.

## 3. Direction

`docs/design/DIRECTION.md`, a page or two, approved by James before anything is built:

- the big idea, and how a visitor experiences it as they scroll
- motion principles: what moves, what never moves, timing and easing, and how the site behaves with reduced motion
- type, layout and how `docs/BRAND.md` is applied
- where video is used and what it shows
- the signature moments: the two or three things a visitor will remember

## 4. Prototype the signature moments

Build each signature moment rough and on its own, in two or three versions, before any page exists. Record them with Playwright at phone and desktop sizes. James chooses. Claude can't watch motion, only frames, so James judges how it feels.

## 5. Assets

- The brand mark animated in Rive, so it can react to scroll and input.
- Images and video generated in ChatGPT, each from a written brief based on `docs/BRAND.md`, and each approved by James. Anything that looks like stock AI art is rejected.
- Real screen recordings of real work wherever they exist. Real beats generated.

## 6. Build & check

Build pages from the approved direction and prototypes. After each one: Playwright screenshots at phone and desktop sizes, a performance trace with Chrome DevTools MCP, and James's approval. The site still meets `docs/WEB_STANDARDS.md` and `docs/AI_SMELL.md`.

## Tools

- GSAP with ScrollTrigger and SplitText for scroll-driven sequences, pinned sections and text animation.
- Lenis for smooth scrolling.
- Motion for page transitions and small interactions in React.
- React Three Fiber and shaders for WebGL, used for one or two signature moments, not everywhere.
- Rive for interactive vector animation.
- Video as short, silent loops with a poster frame, loaded only when on screen.
- Playwright MCP and Chrome DevTools MCP to look, record and measure.
- Context7 for the current docs of every library above, and the `frontend-design` skill for each piece of UI.

## Rules

- Spectacular never means slow: heavy effects load after the page is usable, and never block the first view.
- Every animation respects reduced motion.
- A tool or asset that costs money is approved first.
