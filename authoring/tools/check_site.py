#!/usr/bin/env python3
"""Validate dist/ after `astro build`: every internal link, anchor and image must resolve.

Also requires one H1 per page and the right direction, because Starlight adds the
H1 itself and the Markdown one is stripped in astro.config.mjs.
"""
import re, sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urldefrag, urljoin

DIST = Path(__file__).resolve().parents[2] / "dist"


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids, self.links, self.h1, self.dir = set(), [], 0, None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            self.ids.add(attrs["id"])
        if tag == "html":
            self.dir = attrs.get("dir")
        if tag == "h1":
            self.h1 += 1
        for name in ("href", "src"):
            if tag in ("a", "img") and attrs.get(name):
                self.links.append(attrs[name])


def target(url):
    path = DIST / unquote(url).lstrip("/")
    return path / "index.html" if path.is_dir() else path


def main():
    pages = {}
    for path in DIST.rglob("*.html"):
        page = Page()
        page.feed(path.read_text(encoding="utf8"))
        pages["/" + str(path.relative_to(DIST))] = page

    errors, checked = [], 0
    for name, page in pages.items():
        if not re.match(r"/(en|fa)/", name) or name.endswith("404.html"):
            continue
        if page.h1 != 1:
            errors.append(f"{name}: {page.h1} h1 elements")
        expected = "rtl" if name.startswith("/fa/") else "ltr"
        if page.dir != expected:
            errors.append(f"{name}: dir={page.dir}")
        here = name.removesuffix("index.html")
        for link in page.links:
            if re.match(r"[a-z]+:|//", link):
                continue
            url, fragment = urldefrag(urljoin(here, link))
            checked += 1
            file = target(url)
            if not file.is_file():
                errors.append(f"{name}: broken link {link}")
            elif fragment and fragment != "_top":
                other = pages.get("/" + str(file.relative_to(DIST)))
                if other and unquote(fragment) not in other.ids:
                    errors.append(f"{name}: missing anchor {link}")

    for message in errors[:40]:
        print("FAIL", message)
    print(f"{len(errors)} problems; {checked} links checked across {len(pages)} pages")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
