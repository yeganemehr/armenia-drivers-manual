#!/usr/bin/env python3
"""Validate the generated pages in src/content/docs/. Exits non-zero on any failure.

Default mode checks what exists, so it works mid-way. --final also requires every
section, every question and every image to be used.
"""
import csv, json, re, sqlite3, sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build import CONTENT, DATA, DB, DOCS, OUTLINE, built_up_only, fix_fa, load_terms

FINAL = "--final" in sys.argv
LABELS = {"en": ("Remember:", "Common trap:", "Did you know?"), "fa": ("به یاد داشته باشید:", "دام رایج:", "آیا می‌دانستید؟")}
DRAWN = {"5.18", "5.28", "6.9", "8.2.4", "8.18", "8.22"}
errors = []


def fail(message):
    errors.append(message)


def parts(path):
    text = path.read_text(encoding="utf8")
    body = re.sub(r"\A---\n.*?\n---\n", "", text, flags=re.S)
    return text, body


def shape(body, lang):
    return {
        "headings": len(re.findall(r"^#{1,6} ", body, flags=re.M)),
        "images": re.findall(r"!\[[^\]]*\]\(([^)]+)\)", body),
        "popups": body.count('<details class="extra">'),
        "callouts": sum(body.count(f"> **{label}") for label in LABELS[lang]),
    }


def main():
    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    answers = dict(con.execute("select id, cast(answer as int) from questions"))
    outline = json.load(open(OUTLINE, encoding="utf8"))
    valid = [f'{c["id"]}/{s["id"]}' for c in outline["chapters"] for s in c["sections"]]

    rows = list(csv.DictReader(open(DATA / "assignments.csv", encoding="utf8", newline="")))
    counts = Counter(int(r["question_id"]) for r in rows)
    for qid, n in counts.items():
        if n > 1:
            fail(f"question {qid} assigned {n} times")
        if qid not in answers:
            fail(f"question {qid} is not in the database")
    for qid in set(answers) - set(counts):
        fail(f"question {qid} has no assignment")
    for r in rows:
        if r["section"] not in valid:
            fail(f'question {r["question_id"]}: unknown section {r["section"]}')
    expected = {r["section"]: set() for r in rows}
    for r in rows:
        if not r["note"].startswith("DUP of"):
            expected[r["section"]].add(int(r["question_id"]))

    # Built-up area (60 km/h) and residential zone (20 km/h) must never share a Persian term.
    con.row_factory = sqlite3.Row
    terms = load_terms()
    for row in con.execute("select * from questions"):
        fa = fix_fa(" ".join([row["question_fa"], row["options_fa"], row["explanation_fa"] or ""]), terms, row)
        english = " ".join([row["question"], row["options"], row["explanation"] or ""])
        if built_up_only(row) and "مسکونی" in fa:
            fail(f'question {row["id"]}: built-up area still reads as residential zone')
        if not re.search(r"built[- ]up|settlement|populated", english, re.I) and "محدوده شهری" in fa:
            fail(f'question {row["id"]}: residential zone reads as built-up area')

    credits = (CONTENT / "assets/CREDITS.md").read_text(encoding="utf8")
    used_images, seen = set(), Counter()
    for lang in ("en", "fa"):
        tree = DOCS / lang
        for path in sorted(tree.rglob("*.md")):
            rel = path.relative_to(tree)
            key = str(rel.with_suffix(""))
            text, body = parts(path)
            if "{{practice}}" in text:
                fail(f"{lang}/{rel}: practice marker left in")
            if text.count("<details") != text.count("</details>"):
                fail(f"{lang}/{rel}: unbalanced <details>")
            match = re.search(r"^sources: \[(.*)\]$", text, flags=re.M)
            for qid in (match.group(1).split(",") if match and match.group(1).strip() else []):
                if int(qid) not in answers:
                    fail(f"{lang}/{rel}: unknown source {qid}")
            for link in shape(body, lang)["images"]:
                target = (path.parent / link).resolve()
                if not target.exists():
                    fail(f"{lang}/{rel}: broken image {link}")
                used_images.add(target.name)
                if "assets/signs" in link and target.suffix == ".svg" and target.name not in credits and target.stem not in DRAWN:
                    fail(f"{lang}/{rel}: {target.name} has no entry in assets/CREDITS.md")
            ids = {int(q) for q in re.findall(r'<a id="q(\d+)"></a>', text)}
            if ids != expected.get(key, set()):
                fail(f"{lang}/{rel}: questions differ from assignments.csv")
            seen.update({lang: 1})
            for qid, shown in re.findall(r'<a id="q(\d+)"></a>.*?\*\*(?:Correct|پاسخ درست): (\d+)\.\*\*', text, flags=re.S):
                if answers[int(qid)] != int(shown):
                    fail(f"{lang}/{rel}: question {qid} shows answer {shown}, database says {answers[int(qid)]}")
            if lang == "en":
                for word in set(re.findall(r"\b[Ii]tems? \d+|§ ?\d+|\b[Hh]ighways?\b", body)):
                    fail(f"en/{rel}: use the standard term instead of: {word}")
            if lang == "fa":
                clean = re.sub(r"<[^>]+>|!\[[^\]]*\]\([^)]*\)|\]\([^)]*\)", "", body)
                for word in set(re.findall(r"[A-Za-z]{4,}", clean)):
                    if "03-glossary" not in key and word != "STOP":  # glossary pairs both languages; STOP is sign wording
                        fail(f"fa/{rel}: English left in text: {word}")
                if not re.search(r"[؀-ۿ]", clean):
                    fail(f"fa/{rel}: no Persian text")

    en = {p.relative_to(DOCS / "en") for p in (DOCS / "en").rglob("*.md")}
    fa = {p.relative_to(DOCS / "fa") for p in (DOCS / "fa").rglob("*.md")}
    for rel in en ^ fa:
        fail(f"{rel}: exists in only one language")
    for rel in sorted(en & fa):
        a = shape(parts(DOCS / "en" / rel)[1], "en")
        b = shape(parts(DOCS / "fa" / rel)[1], "fa")
        for field in a:
            if a[field] != b[field]:
                fail(f"{rel}: {field} differ between en and fa")

    if FINAL:
        for key in valid:
            if not (DOCS / "en" / f"{key}.md").exists():
                fail(f"{key}: section not written")
        for name in {p.name for p in (CONTENT / "assets/questions").iterdir()} - used_images:
            fail(f"image never used: {name}")

    for message in errors:
        print("FAIL", message)
    print(f"{len(errors)} problems; {seen['en']} en, {seen['fa']} fa files; {len(used_images)} images used")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
