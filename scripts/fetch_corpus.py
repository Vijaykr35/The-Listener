"""Fetch a few public-domain horror books from Project Gutenberg into ./corpus.

These are used ONLY as style references shown to the local model (restraint,
rhythm, atmosphere). The app works without them.

    python scripts/fetch_corpus.py
"""
import re
import urllib.request
from pathlib import Path

BOOKS = {
    # id: (filename, title)   -- Project Gutenberg ebook numbers
    932: ("poe_usher.txt", "The Fall of the House of Usher (Poe)"),
    8486: ("mrjames_antiquary.txt", "Ghost Stories of an Antiquary (M. R. James)"),
    11438: ("blackwood_willows.txt", "The Willows (Blackwood)"),
    209: ("james_turn_of_the_screw.txt", "The Turn of the Screw (Henry James)"),
    8492: ("chambers_king_in_yellow.txt", "The King in Yellow (Chambers)"),
}


def strip_boilerplate(raw):
    m = re.search(r"\*\*\* ?START OF (THE|THIS) PROJECT GUTENBERG.*?\*\*\*", raw, re.S)
    e = re.search(r"\*\*\* ?END OF (THE|THIS) PROJECT GUTENBERG", raw)
    return raw[m.end(): e.start() if e else None] if m else raw


def main():
    out = Path(__file__).resolve().parent.parent / "corpus"
    out.mkdir(exist_ok=True)
    for num, (fname, title) in BOOKS.items():
        dest = out / fname
        if dest.exists():
            print("have", fname)
            continue
        url = f"https://www.gutenberg.org/cache/epub/{num}/pg{num}.txt"
        try:
            with urllib.request.urlopen(url, timeout=30) as r:
                raw = r.read().decode("utf-8", errors="ignore")
            dest.write_text(strip_boilerplate(raw), encoding="utf-8")
            first = raw[:400].replace("\n", " ")
            print(f"ok   {fname:32s} {len(raw) / 1e3:.0f} KB   [{first[:70].strip()}]")
        except Exception as e:  # noqa: BLE001
            print(f"FAIL {fname}: {type(e).__name__}: {e}")
    print("\nDone. Check each first line above matches the title you expect.")


if __name__ == "__main__":
    main()
