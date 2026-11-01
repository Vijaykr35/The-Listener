"""The director: a small state machine that owns the story's structure.

The language model never runs the story. It only writes one beat at a time,
against a spec this module builds from the story bible, the act structure, the
dread curve, which planted details are still unspent, and the real events the
microphone and the viewer's own actions have produced.
"""
import random
import re
import time
import uuid
from dataclasses import dataclass, field

from . import checker
from . import content as C
from . import writer

PLANS = {
    "short": ["open_mundane", "mundane_second", "first_wrong", "rule_hint", "rule_confirm",
              "turn", "rule_break", "aftermath", "ending"],
    "standard": ["open_mundane", "mundane_second", "first_wrong", "wrong_detail", "rule_hint",
                 "rule_confirm", "escalate", "rattled", "turn", "rule_break", "aftermath", "ending"],
    "long": ["open_mundane", "mundane_second", "first_wrong", "wrong_detail", "rule_hint",
             "wrong_detail", "rule_confirm", "escalate", "rattled", "escalate", "rattled",
             "turn", "rule_break", "aftermath", "ending"],
}

ROLE_META = {
    "open_mundane":   dict(act="Setup",        dread=1,  takes_event=False, min_words=22, max_words=100),
    "mundane_second": dict(act="Setup",        dread=1,  takes_event=False, min_words=22, max_words=100),
    "first_wrong":    dict(act="Wrongness",    dread=3,  takes_event=True,  min_words=22, max_words=100),
    "wrong_detail":   dict(act="Wrongness",    dread=4,  takes_event=True,  min_words=25, max_words=100),
    "rule_hint":      dict(act="Wrongness",    dread=5,  takes_event=False, min_words=25, max_words=100),
    "rule_confirm":   dict(act="Escalation",   dread=6,  takes_event=False, min_words=30, max_words=105),
    "escalate":       dict(act="Escalation",   dread=7,  takes_event=True,  min_words=25, max_words=100),
    "rattled":        dict(act="Escalation",   dread=7,  takes_event=True,  min_words=25, max_words=100),
    "turn":           dict(act="The turn",     dread=9,  takes_event=False, min_words=35, max_words=115),
    "rule_break":     dict(act="The turn",     dread=10, takes_event=False, min_words=30, max_words=105),
    "aftermath":      dict(act="Aftermath",    dread=6,  takes_event=True,  min_words=10, max_words=75),
    "ending":         dict(act="Aftermath",    dread=5,  takes_event=False, min_words=30, max_words=115),
}

INTRO_ROLES = {"open_mundane": 0, "mundane_second": 1, "first_wrong": 2}
PAYOFF_ROLES = {"rule_confirm": 0, "rule_break": 1, "ending": 2}


def pretty_time(wall):
    m = re.match(r"\s*(\d{1,2}):(\d{2})", wall or "")
    if m:
        h, mi = int(m.group(1)) % 24, int(m.group(2))
    else:
        now = time.localtime()
        h, mi = now.tm_hour, now.tm_min
    return f"{h % 12 or 12}:{mi:02d} {'AM' if h < 12 else 'PM'}"


def full_time(wall):
    m = re.match(r"\s*(\d{1,2}):(\d{2})(?::(\d{2}))?", wall or "")
    if m:
        return f"{int(m.group(1)) % 24:02d}:{m.group(2)}:{m.group(3) or '00'}"
    return time.strftime("%H:%M:%S")


def distort(text, rng):
    """Return the viewer's words, slightly wrong. The echo should feel almost right."""
    words = re.findall(r"[\w']+", text)[:8]
    if not words:
        return "..."
    if len(words) == 1:
        return f"{words[0]}... {words[0]}"
    mode = rng.choice(["swap", "repeat", "drop", "tail"])
    w = list(words)
    if mode == "swap":
        w[-1], w[-2] = w[-2], w[-1]
    elif mode == "repeat":
        w.append(w[-1])
    elif mode == "drop" and len(w) > 2:
        del w[len(w) // 2]
    else:
        w = w[:-1] + [w[-1] + "... still"]
    out = " ".join(w)
    return out if out.lower() != " ".join(words).lower() else out + " again"


@dataclass
class Beat:
    n: int
    role: str
    act: str
    dread: int
    text: str = ""
    time: str = ""
    wall: str = ""
    plant: dict = None
    plant_mode: str = None
    event: dict = None
    writer: str = "template"
    attempts: int = 0
    ok: bool = True
    issues: list = field(default_factory=list)

    def public(self, total, choices=None):
        return {
            "n": self.n, "total": total, "role": self.role, "act": self.act, "dread": self.dread,
            "text": self.text, "time": self.time, "wall": self.wall,
            "plant": self.plant["id"] if self.plant else None, "plant_mode": self.plant_mode,
            "event": ({"type": self.event["type"], "wall": self.event["wall"]} if self.event else None),
            "writer": self.writer, "attempts": self.attempts, "ok": self.ok, "issues": self.issues,
            "choices": choices or [],
        }


class Session:
    def __init__(self, seed=None, length="standard", turn=None):
        self.id = uuid.uuid4().hex[:10]
        self.seed = seed if seed is not None else random.randrange(1 << 30)
        self.rng = random.Random(self.seed)
        self.length = length if length in PLANS else "standard"
        self.plan = list(PLANS[self.length])
        r = self.rng
        self.turn = turn if turn in C.TURNS else r.choice(list(C.TURNS))
        self.bible = {
            "narrator": r.choice(C.NARRATORS),
            "rule": r.choice(C.RULES),
            "plants": r.sample(C.PLANTS, 3),
        }
        self.beats = []
        self.events = []
        self._generic = {"wrong": set(), "escalate": set(), "aftermath": set(), "ending": set(),
                         "rattled": set(), "rattled_later": set()}
        self._used_phrases = set()
        self.created = time.time()
        self.user_choices = []
        self.choice_scores = {"reverence": 0, "curiosity": 0, "defiance": 0, "loop": 0}

    # ------------------------------------------------------------ utilities
    def fmt(self, s, **extra):
        ctx = {"hall": C.HALL, "room": C.ROOM, "time": self.beats[0].time if self.beats else pretty_time("")}
        ctx.update(self.bible["narrator"] and {"job": self.bible["narrator"]["job"],
                                                "flaw": self.bible["narrator"]["flaw"],
                                                "doubt": self.bible["narrator"]["doubt"]})
        ctx.update(extra)
        return s.format(**ctx)

    def pick_generic(self, key, pool):
        free = [i for i in range(len(pool)) if i not in self._generic[key]]
        if not free:
            self._generic[key].clear()
            free = list(range(len(pool)))
        i = self.rng.choice(free)
        self._generic[key].add(i)
        return pool[i]

    @property
    def total(self):
        return len(self.plan)

    @property
    def done(self):
        return len(self.beats) >= self.total

    # --------------------------------------------------------------- events
    def ingest(self, raw_events):
        n = len(self.beats)
        for e in raw_events or []:
            typ = str(e.get("type", ""))
            if typ not in C.EVENT_PHRASES:
                continue
            text = re.sub(r"[\x00-\x1f]", " ", str(e.get("text", "")))[:80].strip()
            ev = {
                "type": typ,
                "t": float(e.get("t", 0) or 0),
                "wall": full_time(e.get("wall")),
                "dur": int(round(float(e.get("dur", 0) or 0))),
                "text": text,
                "echo": distort(text, self.rng) if typ == "said" and text else "",
                "added": n,
                "used": False,
            }
            if typ == "said" and not text:
                ev["type"] = "voice"
            self.events.append(ev)
        # keep memory bounded
        if len(self.events) > 120:
            self.events = self.events[-120:]

    def pick_event(self, n):
        free = [e for e in self.events if not e["used"]]
        if not free:
            return None
        ev = max(free, key=lambda e: (C.SALIENCE.get(e["type"], 0.3), e["t"]))
        ev["used"] = True
        ev["used_in"] = n
        return ev

    def event_line(self, ev, n):
        r = self.rng
        label = C.EVENT_LABELS[ev["type"]]
        t = pretty_time(ev["wall"])
        fresh = [p for p in C.EVENT_PHRASES[ev["type"]] if p not in self._used_phrases]
        old_event = (n - ev["added"]) >= 2 and ev["type"] != "said" and not ev["type"].startswith("ritual_")
        if old_event or not fresh:
            variants = [
                f"Earlier tonight, at {t}, I wrote off {label} as nothing. I'm not writing it off anymore.",
                f"I keep coming back to {t}: {label}. I told myself it was nothing.",
                f"{t} in my notes: {label}. I wrote it down and moved on, and I shouldn't have moved on.",
            ]
            if ev["type"] == "said":
                variants = [
                    f"At {t} I said '{ev['text']}' to the empty room, and the {C.HALL} said back '{ev['echo']}'. I wrote it off as nothing.",
                    f"I keep coming back to {t}: I said '{ev['text']}' and it answered '{ev['echo']}'. I told myself it was nothing.",
                ]
            elif ev["type"].startswith("ritual_"):
                variants = [
                    f"At {t}, I watched you: {label}. The air in the {C.ROOM} seemed to hold its breath.",
                    f"I keep coming back to {t}: {label}. The quiet that followed was completely different.",
                    f"{t} at the altar: {label}. I watched the shadows change in that exact moment.",
                ]
            unused = [v for v in variants if v not in self._used_phrases] or variants
            line = r.choice(unused)
            self._used_phrases.add(line)
            return line
        phrase = r.choice(fresh)
        self._used_phrases.add(phrase)
        return self.fmt(phrase, text=ev["text"], echo=ev["echo"], dur=max(ev["dur"], 8))

    def evidence_log(self, limit=3):
        heard = [e for e in self.events]
        by_type = {}
        for e in sorted(heard, key=lambda e: -C.SALIENCE.get(e["type"], 0.3)):
            by_type.setdefault(e["type"], e)
        chosen = sorted(by_type.values(), key=lambda e: e["t"])[:limit]
        entries = [(e["wall"], C.EVENT_LABELS[e["type"]]) for e in chosen]
        seen = {t for t, _ in entries}
        pads = ["something I wrote down", "a second thing I wrote down", "a third thing I wrote down"]
        for b in self.beats[1:]:
            if len(entries) >= 2:
                break
            if b.wall and full_time(b.wall) not in seen:
                entries.append((full_time(b.wall), pads[len(entries) % 3]))
                seen.add(full_time(b.wall))
        return sorted(entries)

    def you_line(self):
        evs = self.events
        blur = [e for e in evs if e["type"] == "blur"]
        if blur:
            e = blur[0]
            return (f"You looked away at {e['wall']} for {max(e['dur'], 5)} seconds, "
                    f"and it moved when you did.")
        sil = [e for e in evs if e["type"] == "silence"]
        if sil:
            e = max(sil, key=lambda x: x["dur"])
            return (f"At {e['wall']} you went completely quiet for {max(e['dur'], 8)} seconds. "
                    f"That's when it got closer.")
        if evs:
            e = max(evs, key=lambda x: C.SALIENCE.get(x["type"], 0.3))
            return f"At {e['wall']} I heard you, {C.EVENT_LABELS[e['type']]}, and I wrote it down."
        return "You've been quiet this whole time. I know, because I've been listening too."

    # ---------------------------------------------------------------- plants
    def plant_for(self, role):
        A, B, Cc = self.bible["plants"]
        if role in INTRO_ROLES:
            return self.bible["plants"][INTRO_ROLES[role]], "intro"
        if role in PAYOFF_ROLES:
            return self.bible["plants"][PAYOFF_ROLES[role]], "payoff"
        prior = [b.role for b in self.beats]
        if role == "wrong_detail":
            return (A if prior.count("wrong_detail") == 0 else B), "callback"
        if role == "escalate":
            return (Cc if prior.count("escalate") == 0 else A), "callback"
        if role == "turn" and self.turn == "unreliable":
            return A, "contradiction"
        return None, None

    def get_choices_for_next(self):
        n = len(self.beats)
        if n >= len(self.plan):
            return []
        next_role = self.plan[n]
        return C.BEAT_CHOICES.get(next_role, C.BEAT_CHOICES.get("open_mundane", []))

    # ------------------------------------------------------------- the beat
    def next_beat(self, raw_events=None, wall=None, choice=None, user_input=None):
        if self.done:
            raise ValueError("story is finished")

        n = len(self.beats)
        events_list = list(raw_events or [])

        # Process user choice
        if choice and isinstance(choice, dict):
            c_text = str(choice.get("text", "")).strip()
            c_type = str(choice.get("type", "reverence"))
            self.choice_scores[c_type] = self.choice_scores.get(c_type, 0) + 1
            self.user_choices.append({
                "beat": n + 1, "text": c_text, "type": c_type, "wall": pretty_time(wall)
            })
            typ = "ritual_whisper" if any(w in c_text.lower() for w in ["whisper", "speak", "call", "demand"]) else (
                "ritual_candle" if any(w in c_text.lower() for w in ["candle", "flame", "light", "blow"]) else (
                    "ritual_petals" if any(w in c_text.lower() for w in ["petal", "marigold", "cempasúchil"]) else (
                        "ritual_bell" if "bell" in c_text.lower() else (
                            "ritual_drink" if any(w in c_text.lower() for w in ["water", "cup", "drink"]) else "thud"
                        )
                    )
                )
            )
            events_list.append({"type": typ, "text": c_text, "wall": wall})

        # Process freeform user input
        if user_input:
            u_text = str(user_input).strip()[:80]
            if u_text:
                self.choice_scores["curiosity"] = self.choice_scores.get("curiosity", 0) + 1
                self.user_choices.append({
                    "beat": n + 1, "text": f"You whispered: \"{u_text}\"", "type": "custom", "wall": pretty_time(wall)
                })
                events_list.append({"type": "ritual_whisper", "text": u_text, "wall": wall})

        # Influence the turning point based on the player's choices
        if n >= 5 and not any(b.role == "turn" for b in self.beats):
            dominant = max(self.choice_scores, key=lambda k: self.choice_scores[k])
            mapped_turn = C.ENDINGS_LORE.get(dominant, {}).get("turn")
            if mapped_turn and mapped_turn in C.TURNS:
                self.turn = mapped_turn

        self.ingest(events_list)
        role = self.plan[n]
        meta = ROLE_META[role]
        plant, mode = self.plant_for(role)
        ev = self.pick_event(n) if meta["takes_event"] else None

        spec = {
            "n": n + 1, "total": self.total, "role": role, "act": meta["act"], "dread": meta["dread"],
            "time": pretty_time(wall), "wall": full_time(wall),
            "plant": plant, "plant_mode": mode,
            "min_words": meta["min_words"], "max_words": meta["max_words"],
            "event": None, "turn": self.turn if role == "turn" else None,
        }
        if ev:
            spec["event"] = dict(ev, line=self.event_line(ev, n))
        if role == "turn":
            log = self.evidence_log()
            spec["log"] = "; ".join(f"{t}, {label}" for t, label in log)
            spec["log_times"] = [t for t, _ in log]
            spec["you_line"] = self.you_line()
            spec["t0"] = self.beats[0].time
            if mode == "contradiction":
                spec["contradiction"] = self.fmt(plant["contradiction"])
                spec["contradiction_kw"] = plant["kw"]
        if role == "ending" and self.turn == "the_loop":
            spec["loop_echo"] = checker.sentences(self.beats[0].text)[0]

        res = writer.write_beat(self, spec)
        next_choices = self.get_choices_for_next() if (n + 1) < self.total else []
        beat = Beat(
            n=n + 1, role=role, act=meta["act"], dread=meta["dread"], text=res["text"],
            time=spec["time"], wall=spec["wall"], plant=plant, plant_mode=mode, event=ev,
            writer=res["writer"], attempts=res["attempts"], ok=res["ok"], issues=res["issues"],
        )
        self.beats.append(beat)
        return beat

    def ending_summary(self):
        dominant = max(self.choice_scores, key=lambda k: self.choice_scores[k])
        lore = C.ENDINGS_LORE.get(dominant, C.ENDINGS_LORE["reverence"])
        return {
            "id": lore["id"],
            "title": lore["title"],
            "subtitle": lore["subtitle"],
            "blurb": lore["blurb"],
            "badge": lore["badge"],
            "turn": self.turn,
            "choices_timeline": self.user_choices,
            "story_transcript": [
                {"n": b.n, "time": b.time, "act": b.act, "text": b.text} for b in self.beats
            ],
            "full_text": "\n\n".join(b.text for b in self.beats),
        }

    # ------------------------------------------------------------ for the UI
    def public_bible(self):
        paid = {b.plant["id"] for b in self.beats if b.plant_mode == "payoff" and b.plant}
        b = self.bible
        return {
            "narrator": b["narrator"]["id"],
            "flaw": self.fmt(b["narrator"]["flaw"]) + ".",
            "rule": b["rule"]["secret"],
            "turn": C.TURNS[self.turn]["label"],
            "turn_id": self.turn,
            "plants": [{"id": p["id"], "detail": self.fmt(p["intro"]), "paid": p["id"] in paid} for p in b["plants"]],
            "length": self.length,
            "total": self.total,
        }
