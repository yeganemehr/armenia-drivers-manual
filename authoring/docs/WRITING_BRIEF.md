# Writing Brief

For anyone writing a section of this book. Paths are relative to `authoring/`, except those starting with
`src/`, which are relative to the project root. Read `docs/STYLE.md` and the finished example
`src/content/lessons/en/03-rules-of-driving/03-speed.md` with `src/content/lessons/fa/03-rules-of-driving/03-speed.md`. Match that voice,
structure and depth.

## What to do for each section
1. List your questions: rows in `data/assignments.csv` for the section. Skip rows noted `DUP of`.
2. Read every assigned question in full from `res/assets_db_questions.sqlite`: question, options, answer,
   explanation. Look at images with the Read tool when the text depends on them.
3. Write `src/content/lessons/en/<chapter>/<section>.md`, then `src/content/lessons/fa/<chapter>/<section>.md`. Filenames come from `outline.json`.
4. Teach everything the questions test, so a reader who studies the lesson can answer them. Group by idea.
   Don't retell questions one by one.
5. Finish with `{{practice}}` on its own line. Never type practice questions.

## Length
Scale to the question count: about 350 words for up to 12 questions, 600 to 900 for 13 to 30, 900 to 1,400
for more. Tables and short lists beat long paragraphs.

## Accuracy rules
- Main text may only state what the questions and explanations support. List those IDs in `sources`.
- Anything else goes in an extra popup. Popups hold general safety or first-aid guidance only. Make no claim
  about Armenian law, fines or exam rules in a popup.
- Never use rules, figures, text or pictures from another country's manual.
- `REVIEW.md` lists questions that look wrong or disagree. Don't teach a disputed point as settled: teach
  what the majority of questions and the cited point support, and leave out the disputed detail if needed.
- Write new problems you find to `data/review_notes/<chapter>.md`, one per line, with question IDs. Don't
  fix the data.

## Images
- Show a picture wherever one helps. Use question images (`../../../assets/questions/Question.<id>.pic.png`)
  in lessons and in Try it yourself. Describe only what the picture really shows, so look at it first.
- Signs are in `src/content/assets/signs/`; find the filename in `data/signs.csv`. Sign lessons show every sign they
  discuss. Link as `../../../assets/signs/3.24.png`, using the exact extension listed.
- Draw simple SVG diagrams where a concept has no picture. Aim for one or two in sections with no good
  image, none where images already cover it. Save as `src/content/assets/diagrams/<section-id>-<n>.svg`. Use a clean flat
  style like `src/content/assets/diagrams/car-speed-ladder.svg`, with `role="img"` and an `aria-label`. No words inside
  the drawing: only numbers, explained in the caption. Check it renders with
  `timeout 10 rsvg-convert <file> -o <scratch>/x.png`, then look at the result.

## Persian
- Translate naturally from your English. Don't translate word for word, and keep the same friendly voice.
- Follow `data/glossary.csv` strictly. Built-up area is `محدوده شهری` and residential zone is `منطقه مسکونی`.
  They are different places with different limits.
- Keep the same headings, images, callouts and popups in the same order, so the two files match exactly.
- Keep Latin digits, as the practice questions do. Sign names should match the Persian practice text.
