#!/usr/bin/env python3
"""Cut individual signs out of the question images, as listed in data/sign_crops.csv.

Answer labels printed under a sign are trimmed by keeping the largest run of
non-white rows and columns.
"""
import csv
from pathlib import Path
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "src/content/assets"
PAD = 3


def largest_run(flags):
    best, start = (0, 0), None
    for i, on in enumerate(list(flags) + [False]):
        if on and start is None:
            start = i
        elif not on and start is not None:
            if i - start > best[1] - best[0]:
                best = (start, i)
            start = None
    return best


def trim(image):
    pixels = np.asarray(image).astype(int)
    ink = pixels.min(axis=2) < 235
    top, bottom = largest_run(ink.any(axis=1))
    left, right = largest_run(ink[top:bottom].any(axis=0))
    width, height = image.size
    # Clamp to the image: crop() fills anything past the edge with black.
    return image.crop((max(left - PAD, 0), max(top - PAD, 0), min(right + PAD, width), min(bottom + PAD, height)))


def main():
    out = ASSETS / "signs"
    out.mkdir(parents=True, exist_ok=True)
    with open(ROOT / "authoring/data/sign_crops.csv", encoding="utf8", newline="") as f:
        for row in csv.DictReader(f):
            box = tuple(int(v) for v in row["box"].split())
            image = Image.open(ASSETS / "questions" / f'Question.{row["question"]}.pic.png').convert("RGB").crop(box)
            trim(image).save(out / f'{row["sign"]}.png')


if __name__ == "__main__":
    # Self-check: a label below a gap is dropped, the sign stays.
    sample = Image.new("RGB", (60, 60), "white")
    sample.paste((200, 0, 0), (10, 5, 50, 40))
    sample.paste((0, 0, 0), (28, 48, 32, 56))
    assert trim(sample).size == (46, 41), trim(sample).size
    # A sign touching the edge must not gain a black border.
    edge = Image.new("RGB", (40, 40), "white")
    edge.paste((200, 0, 0), (10, 10, 40, 40))
    assert trim(edge).getpixel((trim(edge).width - 1, trim(edge).height - 1)) == (200, 0, 0)
    main()
