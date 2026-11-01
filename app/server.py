"""THE LISTENER: local server. Binds to 127.0.0.1 only; nothing leaves the machine."""
from pathlib import Path
import threading

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import FileResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from . import checker, corpus, stt, thread, tts, writer
from . import content as C
from .director import PLANS, Session

STATIC = Path(__file__).resolve().parent.parent / "static"
app = FastAPI(title="The Listener", docs_url=None, redoc_url=None)
SESSIONS = {}


@app.on_event("startup")
def prewarm_tts():
    """Pre-load neural voice model in memory so the first beat synthesizes instantly."""
    def _warm():
        try:
            if tts.status()["ok"]:
                tts.get_voice()
        except Exception:
            pass
    threading.Thread(target=_warm, daemon=True).start()


class NewSession(BaseModel):
    length: str = "standard"
    turn: str = "random"
    seed: int | None = None


class BeatRequest(BaseModel):
    events: list[dict] = Field(default_factory=list)
    wall: str | None = None
    choice: dict | None = None
    user_input: str | None = None


def get_session(sid):
    s = SESSIONS.get(sid)
    if not s:
        raise HTTPException(404, "unknown session")
    return s


@app.get("/api/status")
def status():
    llm = writer.llm_status(force=True)
    return {
        "llm": {"ok": llm["ok"], "model": llm["model"], "models": llm["models"], "error": llm["error"],
                "api": writer.LLM_API},
        "tts": tts.status(),
        "stt": stt.status(),
        "corpus": corpus.corpus_size(),
        "lengths": {k: len(v) for k, v in PLANS.items()},
        "turns": {k: {"label": v["label"], "blurb": v["blurb"]} for k, v in C.TURNS.items()},
        "endings": C.ENDINGS_LORE,
    }


@app.post("/api/session")
def new_session(req: NewSession):
    if len(SESSIONS) > 50:  # keep memory bounded on a long-running demo
        for k in list(SESSIONS)[:25]:
            SESSIONS.pop(k, None)
    s = Session(seed=req.seed, length=req.length, turn=None if req.turn == "random" else req.turn)
    SESSIONS[s.id] = s
    return {"id": s.id, "bible": s.public_bible(), "initial_choices": s.get_choices_for_next()}


@app.post("/api/session/{sid}/beat")
def next_beat(sid: str, req: BeatRequest):
    s = get_session(sid)
    if s.done:
        raise HTTPException(409, "story is finished")
    beat = s.next_beat(req.events, req.wall, choice=req.choice, user_input=req.user_input)
    next_choices = s.get_choices_for_next() if not s.done else []
    return {
        "beat": beat.public(s.total, choices=next_choices),
        "done": s.done,
        "bible": s.public_bible(),
        "choices": next_choices,
        "ending": s.ending_summary() if s.done else None,
        "audit": checker.audit(s) if s.done else None,
    }


@app.get("/api/session/{sid}/story")
def get_story(sid: str):
    s = get_session(sid)
    return s.ending_summary()


@app.get("/api/session/{sid}/story.txt")
def get_story_txt(sid: str):
    s = get_session(sid)
    summary = s.ending_summary()
    txt = f"THE LISTENER: OFRENDA\n{summary['title'].upper()}\n{summary['subtitle']}\n\n"
    txt += f"Resolution:\n{summary['blurb']}\n\n"
    txt += "=" * 50 + "\n\n"
    for b in summary['story_transcript']:
        txt += f"[{b['time']}] {b['text']}\n\n"
    txt += "=" * 50 + "\n"
    txt += "YOUR CHOICES PATH:\n"
    for c in summary['choices_timeline']:
        txt += f"- [{c['wall']}] {c['text']}\n"
    return PlainTextResponse(txt, headers={"Content-Disposition": f'attachment; filename="ofrenda-story-{sid}.txt"'})
    if s.done:
        raise HTTPException(409, "story is finished")
    beat = s.next_beat(req.events, req.wall)
    return {
        "beat": beat.public(s.total),
        "done": s.done,
        "bible": s.public_bible(),
        "audit": checker.audit(s) if s.done else None,
    }


@app.get("/api/session/{sid}/thread")
def get_thread(sid: str):
    s = get_session(sid)
    return {"thread": thread.build_thread(s), "audit": checker.audit(s), "bible": s.public_bible()}


@app.get("/api/session/{sid}/thread.md")
def get_thread_md(sid: str):
    s = get_session(sid)
    md = thread.thread_markdown(thread.build_thread(s))
    return PlainTextResponse(md, headers={"Content-Disposition": f'attachment; filename="the-listener-{sid}.md"'})


@app.post("/api/tts")
async def speak(request: Request):
    body = await request.json()
    text = str(body.get("text", ""))
    try:
        wav = tts.synth(text)
    except RuntimeError as e:
        raise HTTPException(503, str(e))
    return Response(wav, media_type="audio/wav")


@app.post("/api/transcribe")
async def transcribe(request: Request):
    wav = await request.body()
    if not wav or len(wav) > 4_000_000:
        raise HTTPException(400, "bad audio")
    try:
        text = stt.transcribe(wav)
    except RuntimeError as e:
        raise HTTPException(501, str(e))
    except Exception as e:  # noqa: BLE001
        raise HTTPException(500, f"transcription failed: {type(e).__name__}")
    return {"text": text}


@app.get("/")
def index():
    return FileResponse(STATIC / "index.html")


app.mount("/", StaticFiles(directory=STATIC), name="static")
