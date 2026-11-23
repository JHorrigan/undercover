# AI smell

Nothing we make should read or look as if AI made it. This covers copy, design, code and docs. The cure is almost always the same: be specific, and write it the way a person would say it.

## Words

Don't use these, or anything that does the same job:

delve, leverage, unlock, seamless, elevate, empower, harness, game-changer, cutting-edge, revolutionise, transformative, landscape, realm, tapestry, journey (for anything but travel), navigate (for anything but a site), streamline, supercharge, effortless, robust (say what makes it hold up instead), holistic, synergy, "in today's fast-paced world", "let's dive in", "look no further", "take it to the next level".

## Patterns

- Lists of three by habit, such as "fast, simple and secure". Use the number of items there really are.
- "It's not just X, it's Y."
- "Whether you're X or Y..."
- Opening with a rhetorical question.
- Every heading in the "Title: subtitle" shape.
- Every bullet starting with a bold label.
- Sentences all the same length. Vary them.
- A closing line that repeats what was just said.
- Claims with nothing behind them, such as "we deliver results". Name the process, the number and its source, or the person.
- Em dashes, emoji and exclamation marks.

Instead: name real things ("the same numbers typed into three systems"), use plain verbs, and read each line aloud. If a person wouldn't say it, rewrite it.

## Design

Avoid:

- purple and blue gradient blobs, glassmorphism and gradient text
- a centred hero with two buttons, followed by three feature cards with icons
- sparkles, robots, glowing brains, and stock images of people touching holograms
- the same rounded card with a soft shadow repeated everywhere
- one default font, such as Inter, on everything

Instead: follow `docs/BRAND.md`, use real screenshots and real examples, and give each page a layout that suits its content.

## Code & docs

- No comments that restate the code, and no "This function..." docstrings. A docstring says what the function does in one line.
- No banner comments, and no emoji in code, logs or messages.
- No defensive code for cases that can't happen.
- Commit messages and docs are short and plain.

## Checks

`scripts/smell.sh`, run by the check command and the pre-commit hook:

- Em dashes and emoji fail everywhere.
- The words and phrases above fail in website copy (any `web/` app), and only warn in docs and code, where some have plain technical meanings.

It can't catch the patterns, so James's approval of copy is the final check.
