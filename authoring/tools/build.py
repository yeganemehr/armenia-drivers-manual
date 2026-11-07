#!/usr/bin/env python3
"""Render the lessons plus the question database into src/content/docs/, which Astro reads.

Practice questions always come from the database, so they can't drift from it.
"""
import csv, json, re, shutil, sqlite3, sys
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[2]
AUTHORING = ROOT / "authoring"
DATA = AUTHORING / "data"
DB = AUTHORING / "res/assets_db_questions.sqlite"
OUTLINE = AUTHORING / "outline.yaml"
CONTENT = ROOT / "src/content"
LESSONS = CONTENT / "lessons"
DOCS = CONTENT / "docs"  # generated
IMAGES = "../../../assets/questions"
UI = {
    "en": {"heading": "Practice questions", "question": "Question", "show": "Show answer", "correct": "Correct"},
    "fa": {"heading": "پرسش‌های تمرینی", "question": "پرسش", "show": "نمایش پاسخ", "correct": "پاسخ درست"},
}


TITLE = {"en": "Unofficial Armenia Driver's Manual", "fa": "راهنمای غیررسمی رانندگی ارمنستان"}


def load_terms():
    with open(DATA / "fa_terms.csv", encoding="utf8", newline="") as f:
        return [(r["find"], r["replace"], r["scope"]) for r in csv.DictReader(f)]


def built_up_only(row):
    """True if the English mentions built-up areas but not residential zones.

    Persian uses منطقه مسکونی for both, and they have different limits, so the
    term can only be corrected per question.
    """
    text = " ".join([row["question"], row["options"], row["explanation"] or ""])
    return bool(re.search(r"built[- ]up|settlement|populated", text, re.I)) and not re.search(r"residential|courtyard", text, re.I)


def fix_fa(text, terms, row):
    only = built_up_only(row)
    for find, replace, scope in terms:  # order matters: the file lists longer phrases first
        if scope == "all" or only:
            text = text.replace(find, replace)
    return text


def load_en_terms():
    with open(DATA / "en_terms.csv", encoding="utf8", newline="") as f:
        return [(re.compile(r["find"]), r["replace"]) for r in csv.DictReader(f)]


EN_TERMS = load_en_terms()


def load_explanations():
    """Explanations drafted for questions the database has none for. See REVIEW.md."""
    with open(DATA / "explanations.csv", encoding="utf8", newline="") as f:
        return {int(r["id"]): r for r in csv.DictReader(f)}


EXPLANATIONS = load_explanations()


def fix_en(text):
    for pattern, replace in EN_TERMS:
        text = pattern.sub(replace, text)
    return text


def load_assignments():
    """Return {section: [question ids]}. Rows noted 'DUP of N' count as covered but aren't printed."""
    sections = {}
    with open(DATA / "assignments.csv", encoding="utf8", newline="") as f:
        for row in csv.DictReader(f):
            if not row["note"].startswith("DUP of"):
                sections.setdefault(row["section"], []).append(int(row["question_id"]))
    return sections


def localised(row, lang, terms):
    """Return (question, options, explanation) for a language."""
    drafted = EXPLANATIONS.get(row["id"], {})
    if lang == "en":
        options = [{**o, "text": fix_en(o["text"])} for o in json.loads(row["options"])]
        return fix_en(row["question"]), options, drafted.get("en") or fix_en(row["explanation"] or "")
    fix = lambda s: fix_fa(s or "", terms, row)
    options = [{**o, "text": fix(o["text"])} for o in json.loads(row["options_fa"])]
    return fix(row["question_fa"]), options, drafted.get("fa") or fix(row["explanation_fa"])


def render_question(row, lang, terms):
    ui = UI[lang]
    question, options, explanation = localised(row, lang, terms)
    question = question.strip()
    out = [f'<a id="q{row["id"]}"></a>**{ui["question"]} {row["id"]}.** {question}', ""]
    if row["has_picture"]:
        alt = re.sub(r"[\[\]\n]", " ", question)
        out += [f'![{alt}]({IMAGES}/{Path(row["picture_location"]).name})', ""]
    out += [f'{n}. {o["text"].strip()}' for n, o in enumerate(options, 1)]
    answer = int(row["answer"])
    out += ["", '<details class="answer">', f'<summary>{ui["show"]}</summary>', ""]
    out += [f'**{ui["correct"]}: {answer}.** {options[answer - 1]["text"].strip()}', ""]
    if explanation.strip():
        out += [explanation.strip(), ""]
    out += ["</details>", ""]
    return "\n".join(out)


def render_practice(ids, rows, lang, terms):
    if not ids:
        return ""
    blocks = [f'## {UI[lang]["heading"]}', ""]
    blocks += [render_question(rows[i], lang, terms) for i in sorted(ids)]
    return "\n".join(blocks)


def main():
    outline = yaml.safe_load(open(OUTLINE, encoding="utf8"))
    assignments = load_assignments()
    terms = load_terms()
    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    rows = {r["id"]: r for r in con.execute("select * from questions")}
    shutil.rmtree(DOCS, ignore_errors=True)  # so a deleted lesson can't linger on the site
    built = 0
    for lang in UI:
        for chapter in outline["chapters"]:
            for section in chapter["sections"]:
                key = f'{chapter["id"]}/{section["id"]}'
                src = LESSONS / lang / f"{key}.md"
                if not src.exists():
                    continue
                practice = render_practice(assignments.get(key, []), rows, lang, terms)
                out = DOCS / lang / f"{key}.md"
                out.parent.mkdir(parents=True, exist_ok=True)
                out.write_text(src.read_text(encoding="utf8").replace("{{practice}}", practice), encoding="utf8")
                built += 1
    for lang in UI:
        lines = ["---", f'title: {TITLE[lang]}', "---", "", f'# {TITLE[lang]}', ""]
        for chapter in outline["chapters"]:
            written = [s for s in chapter["sections"] if (DOCS / lang / chapter["id"] / f'{s["id"]}.md').exists()]
            if written:
                lines += [f'## {chapter[lang]}', ""]
                lines += [f'- [{s[lang]}]({chapter["id"]}/{s["id"]}.md)' for s in written]
                lines.append("")
        (DOCS / lang / "index.md").write_text("\n".join(lines), encoding="utf8")
    print(f"built {built} files")


if __name__ == "__main__":
    sys.exit(main())
