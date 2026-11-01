"""Optional style references from public-domain horror.

Drop plain-text books into ./corpus (scripts/fetch_corpus.py downloads a few from
Project Gutenberg). The retriever picks short atmospheric passages and shows them
to the local model as *style references only*. If the folder is empty, the
built-in original exemplars in content.py are used instead, so the app always works.
"""
import random
import re
from pathlib import Path

from . import content as C

CORPUS_DIR = Path(__file__).resolve().parent.parent / "corpus"
ATMOSPHERE = {
    "dark", "silence", "silent", "cold", "door", "whisper", "shadow", "window", "stair", "stairs",
    "night", "candle", "footsteps", "empty", "corridor", "moon", "wind", "room", "listen", "listened",
    "dread", "slowly", "alone", "curtain", "passage", "creak", "creaked",
}

_cache = None


def _load():
    global _cache
    if _cache is not None:
        return _cache
    passages = []
    if CORPUS_DIR.exists():
        for f in sorted(CORPUS_DIR.glob("*.txt")):
            try:
                raw = f.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            for para in re.split(r"\n\s*\n", raw):
                para = re.sub(r"\s+", " ", para).strip()
                n = len(para.split())
                if 28 <= n <= 70 and para.count('"') < 4 and para.count("“") < 3:
                    passages.append(para)
    _cache = passages
    return passages


def corpus_size():
    return len(_load())


def style_samples(k=2, hint="", rng=None):
    """Return k short passages to show the model as style references."""
    rng = rng or random.Random()
    passages = _load()
    if not passages:
        return rng.sample(C.EXEMPLARS, min(k, len(C.EXEMPLARS)))
    hint_words = set(re.findall(r"[a-z]+", hint.lower()))

    def score(p):
        ws = set(re.findall(r"[a-z]+", p.lower()))
        return len(ws & ATMOSPHERE) + 2 * len(ws & hint_words)

    pool = sorted(rng.sample(passages, min(400, len(passages))), key=score, reverse=True)[:12]
    return rng.sample(pool, min(k, len(pool)))
