#!/usr/bin/env python3
"""Signs with no source image: hand-drawn reconstructions, plus the two end-of-town signs
built from our own town plates. All are listed for checking in REVIEW.md."""
from pathlib import Path
from PIL import Image, ImageDraw

OUT = Path(__file__).resolve().parents[2] / "src/content/assets/signs"
BLUE, RED, BLACK = "#1259a8", "#d3202a", "#111"
ARROW = "M0,-34 L16,-10 L5,-10 L5,34 L-5,34 L-5,-10 L-16,-10 Z"
CHAIR = ('<circle cx="-4" cy="-17" r="4.5"/><path d="M-7,-11 h7 v10 h12 l7,15 -5,2 -6,-11 h-15 z"/>'
         '<path d="M-10,-4 a13,13 0 1 0 19,14" fill="none" stroke="#111" stroke-width="3.5"/>')


def plate(body, width=120, height=70):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}">'
            f'<rect x="3" y="3" width="{width - 6}" height="{height - 6}" rx="8" fill="#fff" stroke="{BLACK}" stroke-width="4"/>'
            f'{body}</svg>')


SIGNS = {
    "5.18": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 90 130"><rect x="3" y="3" width="84" height="124" rx="7" '
            f'fill="{BLUE}" stroke="#fff" stroke-width="3"/><rect x="13" y="30" width="64" height="62" rx="6" fill="#fff"/>'
            f'<g fill="{BLACK}"><path d="M24,70 l6,-15 h30 l6,15 v12 h-42 z"/><rect x="36" y="46" width="18" height="8"/>'
            '<circle cx="31" cy="83" r="5"/><circle cx="59" cy="83" r="5"/></g></svg>',
    "5.28": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 110 140"><rect x="3" y="3" width="104" height="134" rx="7" '
            f'fill="#fff" stroke="{BLACK}" stroke-width="3"/><circle cx="55" cy="70" r="34" fill="#9aa3ad" stroke="#666" stroke-width="7"/>'
            '<path d="M31,46 L79,94" stroke="#666" stroke-width="7"/>'
            f'<g stroke="{BLACK}" stroke-width="3"><path d="M14,128 L96,12"/><path d="M22,132 L104,16"/><path d="M6,122 L88,6"/></g></svg>',
    "6.9": f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 130 110"><rect x="3" y="3" width="124" height="104" rx="7" fill="{BLUE}" '
           f'stroke="#fff" stroke-width="3"/><g fill="#fff"><path transform="translate(65,62)" d="{ARROW}"/>'
           '<path transform="translate(65,60) rotate(-90) translate(0,-26) scale(.7)" d="M0,-34 L16,-10 L5,-10 L5,34 L-5,34 L-5,-10 L-16,-10 Z"/>'
           '<path transform="translate(65,60) rotate(90) translate(0,-26) scale(.7)" d="M0,-34 L16,-10 L5,-10 L5,34 L-5,34 L-5,-10 L-16,-10 Z"/></g></svg>',
    "8.2.4": plate(f'<g fill="{BLACK}"><path transform="translate(35,45) scale(.95)" d="M0,-34 L14,-14 L5,-14 L5,14 L14,14 L0,34 L-14,14 L-5,14 L-5,-14 L-14,-14 Z"/></g>', 70, 90),
    "8.18": plate(f'<g transform="translate(60,36) scale(1.05)" fill="{BLACK}">{CHAIR}</g><path d="M34,60 L86,10" stroke="{RED}" stroke-width="5"/>'),
    "8.22": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 140 50"><defs><pattern id="s" width="30" height="30" patternUnits="userSpaceOnUse" '
            f'patternTransform="rotate(45)"><rect width="15" height="30" fill="{RED}"/><rect x="15" width="15" height="30" fill="#fff"/></pattern></defs>'
            f'<rect x="2" y="2" width="136" height="46" fill="url(#s)" stroke="#999" stroke-width="2"/></svg>',
}


def struck(source, name):
    image = Image.open(OUT / source).convert("RGB")
    width, height = image.size
    ImageDraw.Draw(image).line((width * .06, height * .9, width * .94, height * .1), fill=RED, width=max(5, height // 12))
    image.save(OUT / name)


def main():
    for number, svg in SIGNS.items():
        (OUT / f"{number}.svg").write_text(svg, encoding="utf8")
    struck("5.23.1.png", "5.24.1.png")
    struck("5.25.png", "5.26.png")


if __name__ == "__main__":
    main()
