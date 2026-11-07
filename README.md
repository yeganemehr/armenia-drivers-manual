# Unofficial Armenia Driver's Manual

A bilingual (Persian and English) study guide, built with [Starlight](https://starlight.astro.build) and
hosted on Cloudflare Workers.

## Layout
- `src/content/lessons/`: the lessons. Edit these.
- `src/content/assets/`: signs, question images and diagrams. Image credits are in `CREDITS.md` there.
- `src/content/docs/`: generated. Lessons plus practice questions from the database. Never edit it.
- `authoring/`: what produces the book: the question database (`res/`), term lists and question assignments
  (`data/`), scripts (`tools/`), writing rules (`docs/`), chapter order (`outline.yaml`) and open
  items (`REVIEW.md`).

## Commands
```sh
npm run dev      # generate the pages and start a local server
npm run build    # generate the pages and build dist/
npm run check    # validate the generated pages and dist/; run after build
npm run preview  # serve dist/ locally
npm run deploy   # build, check and publish to Cloudflare
```
Generating the pages needs Python 3 with PyYAML. `authoring/tools/build_appendices.py` regenerates the
gallery, glossary and question index in `src/content/lessons/`. `crop_signs.py` and `draw_signs.py` in the
same folder regenerate signs, and need Pillow and numpy.

## Markup the site relies on
- Lessons use raw `<details class="extra">` (popups) and `<details class="answer">` (hidden answers), with
  blank lines inside so the Markdown in them still renders.
- `<a id="q123">` anchors each question for the question index.
- Blockquotes starting with a bold label are the Remember, Common trap and Did you know? callouts.
