#!/usr/bin/env python3
"""Generate the sign gallery, glossary and question index into the lessons' 07-appendices/."""
import csv, re, sqlite3
from collections import Counter, defaultdict
from pathlib import Path
import yaml
from build import DATA, DB, LESSONS, OUTLINE, fix_fa, load_terms

CHAPTER = LESSONS / "{lang}/07-appendices"
FAMILIES = {
    "1": ("Warning signs", "تابلوهای هشداردهنده"), "2": ("Priority signs", "تابلوهای حق تقدم"),
    "3": ("Prohibitory signs", "تابلوهای ممنوعیت"), "4": ("Mandatory signs", "تابلوهای دستوری"),
    "5": ("Special regulation signs", "تابلوهای مقررات ویژه"), "6": ("Information signs", "تابلوهای اطلاعاتی"),
    "7": ("Service signs", "تابلوهای خدماتی"), "8": ("Additional plates", "تابلوهای تکمیلی"),
}
TEXT = {
    "en": {"gallery": "Sign Gallery", "intro": "Every sign that the exam questions refer to, by family and number.",
           "sign": "Sign", "number": "Number", "name": "Name", "glossary": "Glossary", "english": "English", "persian": "Persian",
           "gloss_intro": "The terms this book uses, in both languages.", "index": "Question Index",
           "index_intro": "Find any question by its number. Each number links to the question."},
    "fa": {"gallery": "گالری تابلوها", "intro": "همه تابلوهایی که پرسش‌های آزمون به آن‌ها اشاره می‌کنند، به تفکیک گروه و شماره.",
           "sign": "تابلو", "number": "شماره", "name": "نام", "glossary": "واژه‌نامه", "english": "انگلیسی", "persian": "فارسی",
           "gloss_intro": "اصطلاحات این کتاب به هر دو زبان.", "index": "فهرست پرسش‌ها",
           "index_intro": "هر پرسش را با شماره‌اش پیدا کنید. هر شماره به پرسش پیوند دارد."},
}
GENERIC = {"1.11", "1.12", "1.20", "6.15"}  # the book shows their numbered variants instead
SIGN = r"([1-8]\.\d{1,2}(?:\.\d{1,2})?)"


def persian_names(con, terms):
    names = defaultdict(Counter)
    for (text,) in con.execute("select explanation_fa from questions"):
        for number, name in re.findall(SIGN + r"\s*«([^»]{3,48})»", text or ""):
            names[number][name.strip()] += 1
    result = {}
    for number, counts in names.items():
        built_up = number.startswith(("5.23", "5.24", "5.25", "5.26"))
        row = {"question": "built-up" if built_up else "residential", "options": "", "explanation": ""}
        result[number] = fix_fa(counts.most_common(1)[0][0], terms, row)
    return result


def write(lang, name, title, lines):
    path = Path(str(CHAPTER).format(lang=lang)) / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"---\ntitle: {title}\nsources: []\n---\n\n# {title}\n\n" + "\n".join(lines) + "\n", encoding="utf8")


def gallery(rows, fa_names):
    fixes = {r["sign"]: r for r in csv.DictReader(open(DATA / "sign_names.csv", encoding="utf8", newline=""))}
    rows = [r for r in rows if r["sign"] not in GENERIC]
    for row in rows:
        fix = fixes.get(row["sign"], {})
        row["name"] = fix.get("en") or row["name"]
        fa_names[row["sign"]] = fix.get("fa") or fa_names.get(row["sign"], "")
    for lang, text in TEXT.items():
        lines = [text["intro"], ""]
        for family, titles in FAMILIES.items():
            lines += [f'## {titles[0 if lang == "en" else 1]}', "", f'| {text["sign"]} | {text["number"]} | {text["name"]} |', "|---|---|---|"]
            for row in rows:
                if row["sign"].split(".")[0] == family and row["file"]:
                    name = row["name"] if lang == "en" else fa_names.get(row["sign"], "")
                    lines.append(f'| ![{row["sign"]}](../../../assets/signs/{row["file"]}) | {row["sign"]} | {name} |')
            lines.append("")
        write(lang, "01-sign-gallery.md", text["gallery"], lines)


def glossary():
    terms = list(csv.DictReader(open(DATA / "glossary.csv", encoding="utf8", newline="")))
    for lang, text in TEXT.items():
        key = "en" if lang == "en" else "fa"
        lines = [text["gloss_intro"], "", f'| {text["english"]} | {text["persian"]} |', "|---|---|"]
        lines += [f'| {t["en"]} | {t["fa"]} |' for t in sorted(terms, key=lambda t: t[key].lower())]
        write(lang, "03-glossary.md", text["glossary"], lines)


def index():
    outline = yaml.safe_load(open(OUTLINE, encoding="utf8"))
    assigned = defaultdict(list)
    for row in csv.DictReader(open(DATA / "assignments.csv", encoding="utf8", newline="")):
        if not row["note"].startswith("DUP of"):
            assigned[row["section"]].append(int(row["question_id"]))
    for lang, text in TEXT.items():
        lines = [text["index_intro"], ""]
        for chapter in outline["chapters"]:
            for section in chapter["sections"]:
                key = f'{chapter["id"]}/{section["id"]}'
                if key in assigned:
                    links = ", ".join(f"[{q}](../{key}.md#q{q})" for q in sorted(assigned[key]))
                    lines += [f"## {section[lang]}", "", links, ""]
        write(lang, "04-question-index.md", text["index"], lines)


def main():
    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    rows = list(csv.DictReader(open(DATA / "signs.csv", encoding="utf8", newline="")))
    gallery(rows, persian_names(con, load_terms()))
    glossary()
    index()


if __name__ == "__main__":
    main()
