"""Rule checker: every beat is verified in code before it reaches the viewer.

The language model writes; this module decides whether the writing obeyed the
genre rules. A failing beat is rewritten (with the failures fed back to the
model), and after two failed attempts the guaranteed-valid template writer
takes over for that beat.
"""
import re

from . import content as C

WORD = re.compile(r"[A-Za-z0-9]+(?:'[A-Za-z]+)*")


def words(text):
    return WORD.findall(text.lower())


def norm(text):
    return " ".join(words(text))


def sentences(text):
    return [s for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s]


def jaccard(a, b):
    sa = {w for w in words(a) if len(w) > 3}
    sb = {w for w in words(b) if len(w) > 3}
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)


def clean(text):
    """Strip the things small models like to add around a narration."""
    t = text.strip()
    t = re.sub(r"^\s*(beat\s*\d+\s*[:\-]\s*)", "", t, flags=re.I)
    t = re.sub(r"^\s*(here('s| is)[^\n:]*:\s*)", "", t, flags=re.I)
    t = t.replace("**", "").replace("*", "").replace("#", "")
    t = re.sub(r"\s*\n+\s*", " ", t)
    t = re.sub(r"\s{2,}", " ", t)
    if len(t) > 2 and t[0] in "\"“" and t[-1] in "\"”":
        t = t[1:-1].strip()
    t = t.replace("!", ".")
    return t.strip()


def trim_to_words(text, limit):
    """Cut at a sentence boundary so an over-long beat can still pass."""
    if len(words(text)) <= limit:
        return text
    out = []
    for s in sentences(text):
        if len(words(" ".join(out + [s]))) > limit:
            break
        out.append(s)
    return " ".join(out) if out else text


def check(text, spec, prior_texts):
    """Return a list of human-readable rule violations (empty list = pass)."""
    issues = []
    low = text.lower()
    n = len(words(text))
    lo, hi = spec.get("min_words", 22), spec.get("max_words", 100)
    if n < lo:
        issues.append(f"too short ({n} words; write at least {lo})")
    if n > hi:
        issues.append(f"too long ({n} words; keep it under {hi})")
    if not re.search(r"\b(i|i'm|i've|i'd|i'll|my|me)\b", low):
        issues.append("must be in the first person")
    for b in C.BANNED_ENTITY:
        if re.search(r"\b" + b, low):
            issues.append(f"never name or explain the thing (found '{b}')")
            break
    for b in C.BANNED_GORE:
        if b in low:
            issues.append(f"no gore (found '{b}')")
            break
    if low.lstrip().startswith(C.META_STARTS) or any(m in low for m in C.META_PHRASES):
        issues.append("output only the narration, with no meta text or brackets")
    if "!" in text:
        issues.append("no exclamation marks")
    cap = 9 if spec.get("role") in ("rule_confirm", "rule_break", "turn", "ending") else 7
    if len(sentences(text)) > cap:
        issues.append("too many sentences; one wrong detail per beat")

    plant = spec.get("plant")
    if plant and not any(k in low for k in plant["kw"]):
        issues.append(f"must mention the planted detail ({plant['kw'][0]})")

    ev = spec.get("event")
    if ev and ev.get("type") == "said" and ev.get("echo"):
        want = [w for w in words(ev["echo"]) if len(w) > 2][:6]
        have = set(words(text))
        if want and sum(1 for w in want if w in have) < max(1, len(want) // 2):
            issues.append("must quote the echoed words the narrator heard")

    turn = spec.get("turn")
    role = spec.get("role")
    if role == "turn" and turn == "sounds_are_yours":
        times = [t for t in spec.get("log_times", []) if t in text]
        if len(set(times)) < min(2, len(spec.get("log_times", []))):
            issues.append("must cite at least two of the exact log times")
        if not re.search(r"\byou(r|rs)?\b", low):
            issues.append("must speak to 'you'")
    if role == "turn" and turn == "fourth_wall":
        if len(re.findall(r"\byou(r|rs)?\b", low)) < 2:
            issues.append("must speak directly to 'you'")
    if role == "turn" and turn == "unreliable":
        if not re.search(r"\b(no|never|only ever|isn't|is not|are no|there is one)\b", low):
            issues.append("must flatly contradict the earlier detail")
        if spec.get("plant") is None and spec.get("contradiction_kw"):
            if not any(k in low for k in spec["contradiction_kw"]):
                issues.append("must contradict the earlier planted detail")
    if role == "ending":
        for r in C.RESOLUTIONS:
            if r in low:
                issues.append("the ending must stay unresolved")
                break
        echo = spec.get("loop_echo")
        if echo and norm(echo) not in norm(text):
            issues.append("the ending must repeat the story's first sentence word for word")

    for p in prior_texts[-3:]:
        if jaccard(text, p) > 0.5:
            issues.append("too similar to an earlier beat; say something new")
            break
    return issues


def audit(session):
    """Whole-story checklist shown in the director's view."""
    beats = session.beats
    out = []
    text_all = " ".join(b.text.lower() for b in beats)
    named = [b for b in C.BANNED_ENTITY if re.search(r"\b" + b, text_all)]
    out.append(("The thing is never named or explained", not named))

    paid = []
    for p in session.bible["plants"]:
        pb = [b for b in beats if b.plant and b.plant["id"] == p["id"] and b.plant_mode == "payoff"]
        paid.append(bool(pb) and any(k in pb[0].text.lower() for k in p["kw"]))
    out.append(("Every planted detail pays off", bool(paid) and all(paid)))

    breaks = [b for b in beats if b.role == "rule_break"]
    out.append(("The rule is broken exactly once", len(breaks) == 1))

    turn_beats = [b for b in beats if b.role == "turn"]
    out.append(("A psychological turn lands: " + C.TURNS[session.turn]["label"], len(turn_beats) == 1 and turn_beats[0].ok))

    end = [b for b in beats if b.role == "ending"]
    unresolved = bool(end) and not any(r in end[-1].text.lower() for r in C.RESOLUTIONS)
    out.append(("The ending stays unresolved", unresolved))

    heard = len(session.events)
    used = len([e for e in session.events if e.get("used")])
    out.append((f"Real events woven in ({used} of {heard} heard)", heard == 0 or used > 0))
    out.append(("Every beat passed the rule checker", all(b.ok for b in beats) and bool(beats)))
    return [{"rule": r, "ok": bool(ok)} for r, ok in out]
