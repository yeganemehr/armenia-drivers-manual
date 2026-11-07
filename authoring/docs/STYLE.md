# Style Guide

Every section of the book follows this guide. The goal is a patient instructor talking to a learner, not
a statute and not a list of questions.

## Voice
- Speak to the reader as "you". Use short commands: "Slow down before the bend."
- Give the reason for every rule. A rule with a reason is remembered; a bare rule is not.
- Use plain words. Prefer "must not" to "is prohibited from". Explain a legal term the first time.
- Ask the question a learner would ask, and use it as a heading where it fits: "Who goes first?"
- Put the reader in the scene: "You are the blue car."
- Turn rules into something usable: a memory hook, a check, a before-and-after.
- State numbers exactly as the source gives them.
- No filler ("it is important to note"), no scare tactics, no moralising.

## Section template
Every lesson uses these parts in this order. Skip part 3 or 5 only if there is nothing worth saying.

1. `# Title`, then **Why this matters**: two sentences, no heading.
2. **The rules**: `##` subheadings, each with a short explanation and a picture where one helps.
3. `## Try it yourself`: one to three scenarios using question images. State the answer and the reason.
4. **Callouts**, placed beside the rule they support.
5. **Extra popups**, placed beside the rule they relate to.
6. `## Key points`: three to seven bullets.
7. `{{practice}}` on its own line. The build replaces it. Never type a practice question by hand.

## Frontmatter
```yaml
---
title: Speed
sources: [437, 607, 609]
---
```
`sources` lists the question IDs behind the main text, so each claim can be traced.

## Callouts
Only these three, each a blockquote starting with its label. In Persian use the label on the right.

| Label | Persian | Use for |
|---|---|---|
| `> **Remember:**` | `> **به یاد داشته باشید:**` | The one fact to keep from this part |
| `> **Common trap:**` | `> **دام رایج:**` | A mistake the exam catches, from the wrong answers in the explanations |
| `> **Did you know?**` | `> **آیا می‌دانستید؟**` | A reason or consequence that makes the rule stick |

## Extra popups
Anything not supported by the questions goes here and nowhere else.

```html
<details class="extra">
<summary>Extra: Why stopping distance grows so fast</summary>

*Not from the question bank.*

Text goes here. Keep the blank lines so markdown works inside.

</details>
```
Persian: `<summary>مطلب تکمیلی: ...</summary>` and `*این مطلب از بانک سؤالات نیامده است.*`

- Claims about Armenian law or the exam must be checked against an official source and cite it.
- General safety and first aid must be widely accepted guidance.
- If it can't be verified, leave it out.
- Never use rules, figures, text or pictures from other countries' manuals.

## Terms and citations
- Follow `data/glossary.csv` in both languages.
- Say "the Traffic Rules", and cite "point 36". Never "item" or "§".
- Say "the RA law" for the law "On ensuring road traffic safety", cited by article.
- Refer to signs and markings by number and name: sign 3.26 "Audible signal prohibited".

## Images
- Reference images relative to the section file: `![description](../../../assets/questions/Question.7.pic.png)`.
- Alt text describes what the picture shows.
- Prefer existing question images, then licensed web images, then drawn SVGs.
- Drawn SVGs contain no words. Use numbers and explain them in the caption.
- Every non-database image needs an entry in `src/content/assets/CREDITS.md`.

## Files
- Write in `src/content/lessons/en/<chapter>/<section>.md` and `src/content/lessons/fa/<chapter>/<section>.md`.
  Never edit `src/content/docs/`: it is generated.
- Persian mirrors English exactly: same headings, images, callouts and popups, in the same order.
