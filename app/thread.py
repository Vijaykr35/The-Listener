"""After the story: the forum thread, and the case file of what really happened.

The thread is assembled from the story bible and the real event log, so the
replies can point at timestamps that actually occurred in the viewer's room.
"""
import random

from . import checker
from . import content as C
from .director import pretty_time

USERS = ["pale_ink", "marrow_88", "greywren", "lowtide", "ashgrove", "dusty_modem", "nightowl_77", "tin_lantern"]
TITLES = [
    "[NOCHE DE MUERTOS] Keeping vigil at the family {room} alone. Something answered the marigolds",
    "[LIVE] The candles in my {room} keep leaning toward the courtyard. I don't think I'm alone",
    "Sitting vigil on November 1st. Something is moving through the cempasúchil petals (live updates)",
]


def build_thread(s):
    rng = random.Random(s.seed + 1)
    users = USERS[:]
    rng.shuffle(users)
    u = iter(users)
    beats = s.beats
    A, B, Cc = s.bible["plants"]

    posts = []
    for i, b in enumerate(beats):
        posts.append({"author": "OP", "label": "Original post" if i == 0 else f"UPDATE {i}",
                      "time": b.time, "text": b.text, "role": b.role})

    replies = []  # (after_beat_index, author, text)

    def add(after, text):
        replies.append((min(after, len(beats) - 1), next(u), text))

    roles = [b.role for b in beats]
    idx = lambda role: roles.index(role) if role in roles else len(beats) - 1  # noqa: E731

    add(idx("first_wrong"), "Nobody writes 'nothing is wrong' as their first line unless something is wrong.")
    if "rule_confirm" in roles:
        add(idx("rule_confirm"), f"OP, go and look at the {A['kw'][0]} right now. I'm serious. Look at it.")
    used = [e for e in s.events if e.get("used")]
    if used:
        e = used[0]
        add(idx("first_wrong"), f"OP what happened at {e['wall']}? Your update jumps right over it.")
    t = s.turn
    turn_i = idx("turn")
    first_wall = beats[0].wall if beats else ""
    if t == "sounds_are_yours":
        log = s.evidence_log()
        stamp = log[0][0] if log else first_wall
        add(turn_i, f"OP, the timestamps in your log. {stamp}. I wrote that one down too. Why do I have the same ones?")
    elif t == "fourth_wall":
        add(turn_i, "OP who are you talking to? You keep saying 'you'. The rest of us are right here.")
    elif t == "the_loop":
        add(turn_i, "This is the third time this exact post has been made. Same timestamps. Same first line. Check the post history.")
    else:
        add(turn_i, f"OP, in update 2 you said: \"{s.fmt(A['intro'])}\" Now you say the opposite. Which is it?")
    add(idx("aftermath"), "OP are you still there?")
    add(len(beats) - 1, "OP?")

    replies.sort(key=lambda r: r[0])
    # interleave: each reply appears after the post it follows
    stream = []
    for i, p in enumerate(posts):
        stream.append({**p, "kind": "post"})
        for after, author, text in replies:
            if after == i:
                stream.append({"kind": "reply", "author": author, "text": text, "time": p["time"]})

    final = {
        "sounds_are_yours": "I can hear your hallway from here.",
        "fourth_wall": "Thanks for staying.",
        "the_loop": checker.sentences(beats[0].text)[0] + " Again." if beats else "Again.",
        "unreliable": "There is no OP. There never was an OP.",
    }[t]
    stream.append({"kind": "reply", "author": "[deleted]", "text": final, "time": pretty_time(beats[-1].wall) if beats else ""})
    stream.append({"kind": "mod", "text": "This thread has been locked by a moderator. Reason: account created 0 minutes ago."})

    case, others = [], 0
    ranked = sorted(s.events, key=lambda e: (not e.get("used"), -C.SALIENCE.get(e["type"], 0.3), e["t"]))
    keep = [e for e in ranked if e.get("used")] + [e for e in ranked if not e.get("used")][:6]
    others = len(s.events) - len(keep)
    for e in sorted(keep, key=lambda e: e["t"]):
        case.append({"time": e["wall"], "type": e["type"], "label": C.EVENT_LABELS[e["type"]],
                     "used": bool(e.get("used")), "text": e.get("text", ""), "dur": e.get("dur", 0)})
    return {
        "title": rng.choice(TITLES).format(room=C.ROOM),
        "board": "night-owls",
        "views": 1,
        "turn": C.TURNS[t]["label"],
        "stream": stream,
        "case_file": case,
        "case_more": max(others, 0),
    }


def thread_markdown(th):
    out = [f"# {th['title']}", f"*board: {th['board']} · views: {th['views']}*", ""]
    for item in th["stream"]:
        if item["kind"] == "post":
            out += [f"**{item['author']}** · {item['label']} · {item['time']}", "", item["text"], ""]
        elif item["kind"] == "reply":
            out += [f"> **{item['author']}**: {item['text']}", ""]
        else:
            out += [f"*{item['text']}*", ""]
    out += ["---", "", "## Case file: what the microphone actually heard", ""]
    if th["case_file"]:
        for c in th["case_file"]:
            extra = f" (\"{c['text']}\")" if c["text"] else ""
            out.append(f"- {c['time']} · {c['label']}{extra}")
    else:
        out.append("- Nothing. The room stayed quiet. (That's what makes it worse.)")
    if th.get("case_more"):
        out.append(f"- ...and {th['case_more']} smaller sounds the story never used.")
    out.append("")
    return "\n".join(out)
