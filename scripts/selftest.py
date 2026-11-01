"""Property test for the story engine (no model, no browser needed).

Runs hundreds of simulated sessions across every length and every turn, with
random microphone events, and asserts that every beat passes the rule checker
and every whole-story audit item holds.

    python scripts/selftest.py
"""
import os
import random
import sys
from pathlib import Path

os.environ["GHOST_LLM"] = "off"
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import checker, content as C, director  # noqa: E402


def fake_events(rng, t):
    out = []
    for _ in range(rng.randint(0, 3)):
        typ = rng.choice(list(C.EVENT_PHRASES))
        e = {"type": typ, "t": t + rng.random() * 10,
             "wall": f"00:{rng.randint(10, 50):02d}:{rng.randint(0, 59):02d}", "dur": rng.randint(5, 20)}
        if typ == "said":
            e["text"] = rng.choice(["is anyone there", "hello", "I am not afraid of you", "leave me alone please", "what do you want from me"])
        out.append(e)
    return out


def run(seed, length, turn, with_events):
    rng = random.Random(seed)
    s = director.Session(seed=seed, length=length, turn=turn)
    clock = 12 * 3600
    while not s.done:
        clock += rng.randint(25, 45)
        wall = f"{clock // 3600 % 24:02d}:{clock // 60 % 60:02d}:{clock % 60:02d}"
        evs = fake_events(rng, clock) if with_events else []
        s.next_beat(evs, wall)
    return s


def main():
    fails, total, beats = 0, 0, 0
    for length in director.PLANS:
        for turn in C.TURNS:
            for with_events in (False, True):
                for seed in range(25):
                    total += 1
                    s = run(seed, length, turn, with_events)
                    beats += len(s.beats)
                    bad = [(b.n, b.role, b.issues, b.text) for b in s.beats if not b.ok]
                    audit = [a for a in checker.audit(s) if not a["ok"]]
                    # the audit item about events only applies when events exist
                    if bad or audit:
                        fails += 1
                        if fails <= 5:
                            print(f"FAIL length={length} turn={turn} seed={seed} events={with_events}")
                            for x in bad[:3]:
                                print("  beat", x)
                            for a in audit:
                                print("  audit", a)
    print(f"{total} sessions, {beats} beats, {fails} failures")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
