"""The writer: an open-weight model through a local server, with a safety net.

Primary path: any local model served by Ollama (default) or by an
OpenAI-compatible local server such as llama.cpp, LM Studio or vLLM.
Every draft goes through the rule checker. A draft that breaks the rules is
sent back with the exact violations; after two failures a template writer
(built from the same story bible) supplies a beat that is guaranteed to pass,
so the show never stalls and never ships a broken beat.
"""
import json
import os
import time
import urllib.error
import urllib.request

from . import checker, corpus
from . import content as C

LLM_URL = os.environ.get("GHOST_LLM_URL", "http://127.0.0.1:11434").rstrip("/")
LLM_API = os.environ.get("GHOST_LLM_API", "ollama")  # "ollama" or "openai"
LLM_MODEL = os.environ.get("GHOST_MODEL", "")
LLM_OFF = os.environ.get("GHOST_LLM", "").lower() in ("off", "0", "none", "template")

_status = {"t": 0.0, "ok": False, "model": None, "models": [], "error": None}
PREFERRED = ("llama3", "qwen", "gemma", "mistral", "phi", "granite", "smol")


def llm_status(force=False):
    now = time.time()
    if not force and now - _status["t"] < 20:
        return dict(_status)
    _status.update(t=now, ok=False, model=None, models=[], error=None)
    if LLM_OFF:
        _status["error"] = "disabled by GHOST_LLM"
        return dict(_status)
    try:
        path = "/api/tags" if LLM_API == "ollama" else "/v1/models"
        with urllib.request.urlopen(LLM_URL + path, timeout=1.5) as r:
            data = json.load(r)
        if LLM_API == "ollama":
            models = [m["name"] for m in data.get("models", [])]
        else:
            models = [m["id"] for m in data.get("data", [])]
        _status["models"] = models
        if LLM_MODEL:
            _status["model"] = LLM_MODEL
        elif models:
            pref = [m for m in models if any(p in m.lower() for p in PREFERRED) and "embed" not in m.lower()]
            _status["model"] = (pref or models)[0]
        _status["ok"] = bool(_status["model"])
        if not _status["ok"]:
            _status["error"] = "server is up but no model is installed"
    except Exception as e:  # noqa: BLE001 - any failure just means 'use the fallback'
        _status["error"] = f"{type(e).__name__}: {e}"
    return dict(_status)


def _chat(model, messages, temperature=0.85):
    if LLM_API == "ollama":
        body = {"model": model, "messages": messages, "stream": False,
                "options": {"temperature": temperature, "top_p": 0.92, "num_predict": 240, "repeat_penalty": 1.12}}
        url = LLM_URL + "/api/chat"
    else:
        body = {"model": model, "messages": messages, "temperature": temperature, "top_p": 0.92, "max_tokens": 240}
        url = LLM_URL + "/v1/chat/completions"
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        data = json.load(r)
    if LLM_API == "ollama":
        return data["message"]["content"]
    return data["choices"][0]["message"]["content"]


# ---------------------------------------------------------------- LLM prompts
ROLE_INSTRUCTIONS = {
    "open_mundane": "Open the story with an ordinary, relatable incident. State the time, where the narrator is, and what they do for work. Focus on everyday slice-of-life realism. Mention the planted detail in passing.",
    "mundane_second": "Another ordinary beat. The narrator confesses a quiet human flaw or observation. Mention the planted detail in passing. Focus on what they notice and hide.",
    "first_wrong": "The first subtle tension occurs. An ordinary misunderstanding, an overlooked detail, or unexpected small friction. The narrator tries to dismiss it, then mentions the planted detail casually.",
    "wrong_detail": "Another small friction or quiet complication, kept subtle and grounded. Dramatize the event if one is given. Mention the planted detail as a callback.",
    "rule_hint": "The narrator starts to notice an unspoken pattern in human behavior or their own habits. Convey the quiet pattern through what they observed.",
    "rule_confirm": "The narrator watches the pattern hold true in real time. Convey the realization through a grounded micro-action. Pay off the planted detail.",
    "escalate": "The emotional or psychological tension escalates. An unresolved conversation, message, or internal dilemma. Mention the planted detail as a callback.",
    "rattled": "The narrator's composure wavers. Self-doubt, hesitation, or second-guessing sets in. Use the doubt line. Stay restrained and realistic, never melodramatic.",
    "turn": "",
    "rule_break": "The character or someone around them breaks their usual pattern for the first time. Show it in one clear grounded image. Pay off the planted detail.",
    "aftermath": "Aftershock. A quiet pause in the room. The narrator reflects on what just shifted between people. Keep it concise.",
    "ending": "Final beat. A subtle emotional realization, an unfinished action, or an unspoken question. Pay off the planted detail and end without forced moralizing.",
}


def build_messages(session, spec, feedback=None):
    b = session.bible
    nar = b["narrator"]
    A, B, Cc = b["plants"]
    system = ("You write one beat at a time of a deeply engaging, realistic, character-driven slice-of-life story.\n\n"
              + C.STYLE_GUIDE)

    prior = [x.text for x in session.beats[-3:]]
    hint = (spec.get("event") or {}).get("line", "")
    refs = corpus.style_samples(2, hint=hint, rng=session.rng)

    lines = [
        "STORY BIBLE (hidden from the reader):",
        f"- Narrator: they {session.fmt(nar['job'])}. Flaw: {session.fmt(nar['flaw'])}.",
        f"- The thing's hidden rule (show it, never explain it): {b['rule']['secret']}",
        f"- Planted details: A) {session.fmt(A['intro'])} B) {session.fmt(B['intro'])} C) {session.fmt(Cc['intro'])}",
        f"- Current time in the story: {spec['time']}.",
        "",
        "STYLE REFERENCES (match the restraint and rhythm; never copy):",
    ]
    lines += [f"> {r}" for r in refs]
    lines += ["", "STORY SO FAR:"] + ([f"- {p}" for p in prior] or ["- (nothing yet)"]) + [""]

    role = spec["role"]
    lines.append(f"NOW WRITE BEAT {spec['n']} OF {spec['total']}. Act: {spec['act']}. Dread level: {spec['dread']}/10.")
    if role == "turn":
        t = C.TURNS[spec["turn"]]["llm"].format(
            log=spec.get("log", ""), you_line=spec.get("you_line", ""), t0=spec.get("t0", ""),
            contradiction=spec.get("contradiction", ""))
        lines.append(t)
    else:
        lines.append(ROLE_INSTRUCTIONS[role])
    if role == "rattled":
        lines.append(f"Doubt line to use: {session.fmt(nar['doubt'])}.")
    ev = spec.get("event")
    if ev:
        lines.append("Real event to dramatize as the ONE wrong detail (keep any quoted words exactly): " + ev["line"])
    plant = spec.get("plant")
    if plant and spec.get("plant_mode") != "contradiction":
        key = {"intro": "intro", "callback": "callback", "payoff": "payoff"}[spec["plant_mode"]]
        lines.append(f"Planted detail ({spec['plant_mode']}), include it using the word '{plant['kw'][0]}': "
                     + session.fmt(plant[key]))
    if role == "ending" and spec.get("loop_echo"):
        lines.append("The ending must BEGIN with this exact sentence, word for word, followed by the word 'Again.': "
                     + spec["loop_echo"])
    if feedback:
        lines.append("")
        lines.append("Your previous attempt broke these rules: " + "; ".join(feedback) + ". Rewrite it and fix every one.")
    lines.append("")
    lines.append("Output only the narration text.")
    return [{"role": "system", "content": system}, {"role": "user", "content": "\n".join(lines)}]


# ------------------------------------------------------------ template writer
def _S(text):
    t = text.strip()
    return t if t and t[-1] in ".!?'\"" else t + "."


def template_beat(session, spec):
    r = session.rng
    b = session.bible
    nar = b["narrator"]
    role = spec["role"]
    f = session.fmt
    plant, mode = spec.get("plant"), spec.get("plant_mode")
    pline = f(plant[{"intro": "intro", "callback": "callback", "payoff": "payoff",
                      "contradiction": "contradiction"}[mode]]) if plant else ""
    ev = spec.get("event")
    ctx = {"time": spec["time"]}
    parts = []

    if role == "open_mundane":
        parts = [f(r.choice(C.OPEN_FRAMES), time=spec["time"]), pline]
    elif role == "mundane_second":
        parts = [f(r.choice(C.MUNDANE_FRAMES)), pline]
    elif role == "first_wrong":
        wrong = ev["line"] if ev else f(session.pick_generic("wrong", C.GENERIC_WRONG))
        parts = [wrong, r.choice(C.DISMISSALS), pline]
    elif role == "wrong_detail":
        wrong = ev["line"] if ev else f(session.pick_generic("wrong", C.GENERIC_WRONG))
        parts = [wrong, pline]
    elif role == "rule_hint":
        parts = [f(b["rule"]["hint"])]
    elif role == "rule_confirm":
        parts = [f(b["rule"]["confirm"]), pline]
    elif role == "escalate":
        wrong = ev["line"] if ev else f(session.pick_generic("escalate", C.GENERIC_ESCALATE))
        parts = [wrong, pline]
    elif role == "rattled":
        first = not any(x.role == "rattled" for x in session.beats)
        if first:
            base = f(session.pick_generic("rattled", C.RATTLED_FRAMES))
            parts = [ev["line"], f(nar["doubt"])] if ev else [base]
        else:
            base = session.pick_generic("rattled_later", C.RATTLED_LATER)
            parts = [ev["line"], C.RATTLED_CLOSERS[0]] if ev else [base]
    elif role == "turn":
        t = spec["turn"]
        if t == "sounds_are_yours":
            parts = [
                f"I checked the log of times. {spec['log']}.",
                f"Here is what caught my attention: every time I thought of reaching out, I talked myself out of it.",
                "I kept wondering if you were on the other end, waiting for the same quiet gesture.",
            ]
        elif t == "fourth_wall":
            parts = [
                spec["you_line"],
                f"I have been sitting here since {spec['t0']}, watching the cursor blink on my screen.",
                "I am not in a rush to wrap this up. I just wonder how many times you have had this exact same silent conversation with yourself.",
            ]
        elif t == "the_loop":
            parts = [
                f"I looked at the clock and realized it was already past {spec['t0']}.",
                "I had the strange feeling that I keep having this exact same day on repeat, making the same quiet excuses and waiting for someone else to change things.",
            ]
        else:  # unreliable
            parts = [
                pline,
                f"I looked back at the note I wrote at {spec['t0']}, and my own words felt distant.",
                "I recognized my handwriting, but the certainty behind it was completely gone.",
            ]
    elif role == "rule_break":
        parts = [f(b["rule"]["break"]), pline]
    elif role == "aftermath":
        parts = [f(session.pick_generic("aftermath", C.AFTERMATH))]
        if ev:
            parts.append(ev["line"])
    elif role == "ending":
        if spec.get("loop_echo"):
            parts = [spec["loop_echo"], "Tomorrow again.", pline,
                     "I know how the routine plays out. I am just waiting to see if I choose differently next time."]
        else:
            parts = [pline, f(session.pick_generic("ending", C.ENDINGS))]
    return " ".join(_S(p) for p in parts if p)


# ------------------------------------------------------------------ main entry
def write_beat(session, spec):
    prior = [x.text for x in session.beats]
    st = llm_status()
    attempts, last_issues = 0, []
    if st["ok"]:
        feedback = None
        for _ in range(2):
            attempts += 1
            try:
                raw = _chat(st["model"], build_messages(session, spec, feedback))
            except Exception as e:  # noqa: BLE001
                last_issues = [f"model unavailable ({type(e).__name__})"]
                _status["t"] = 0  # re-probe next time
                break
            text = checker.trim_to_words(checker.clean(raw), spec["max_words"])
            issues = checker.check(text, spec, prior)
            if not issues:
                return {"text": text, "writer": "llm:" + st["model"], "attempts": attempts,
                        "issues": [], "ok": True}
            feedback, last_issues = issues, issues
    text = template_beat(session, spec)
    issues = checker.check(text, spec, prior)
    # if even the template fails, surface why (the self-test relies on this)
    return {"text": text, "writer": "template", "attempts": attempts, "issues": issues or last_issues, "ok": not issues}
