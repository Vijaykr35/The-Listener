# THE LISTENER

A ghost story that listens to you. Sit in the dark with headphones on. The story is written live, one beat at a time, by an **open-weight model running on your own machine**, and it is built from what your room actually does while you wait: a knock, a creak, a long silence, the words you say out loud, the moment you look away from the screen. It is narrated aloud and rendered as a video you can download. When it ends you get the whole thing as a creepypasta forum thread, plus a **case file** of what the microphone really heard.

## Run it

```bash
./run.sh            # installs deps, fetches the voice, pulls a model if Ollama is present, starts the app
# then open http://127.0.0.1:8000  (Chrome or Edge recommended)
```

Or by hand:

```bash
pip install -r requirements.txt
python scripts/get_voice.py          # Piper narrator voice (one-time download, ~60 MB)
ollama pull llama3.2:3b              # the story model (any chat model works)
pip install faster-whisper           # optional: lets it hear your actual words
python scripts/fetch_corpus.py       # optional: public-domain horror as a style library
python -m app
```

Every piece is optional except the Python server. Without Ollama it falls back to a built-in template writer that obeys the same rules, so the demo never breaks.

## Why open matters here

| Concern | What the open stack gives you |
|---|---|
| **An always-on microphone** is the most private input there is | Audio is analysed in the browser; only a short clip of speech is sent, to `127.0.0.1`, transcribed by Whisper, and deleted immediately. No cloud, no account, no key. |
| **Offline** | Model (Ollama), voice (Piper), ears (faster-whisper) all run locally. Unplug the network and it still works. |
| **Cost** | Free per story. |
| **Control** | Swap the model with `GHOST_MODEL=...`, point at llama.cpp / LM Studio / vLLM with `GHOST_LLM_API=openai`, change the narrator with `GHOST_VOICE=...`, or fine-tune a LoRA for the narrator's voice. Everything is a file you can read. |

## How it keeps a small model on the rails

The model never runs the story. A **director** (`app/director.py`) does:

1. **Story bible**, generated at the start and hidden from the viewer: the narrator's flaw, the thing's secret rule, three planted mundane details, and one psychological turn.
2. **Act structure and dread curve**: setup, wrongness, escalation, the turn, aftermath. Each beat has a role, a target dread level and a word budget.
3. **Real events** from the room (sound detector, Whisper transcript, tab-blur, anything you type) are queued and handed to the writer as "the one wrong detail" for the next beat. Your own words come back slightly distorted.
4. **Rule checker** (`app/checker.py`): every draft is verified in code: never name or explain the thing, no gore, one wrong detail, first person, no exclamation marks, planted details must pay off, the rule is broken exactly once, the turn must cite real log times or contradict a real earlier detail, the ending stays unresolved. A failing draft is sent back to the model with the exact violations. After two failures a template writer built from the same bible supplies a beat that is guaranteed to pass.

The four turns: **The sounds are yours** (the narrator's log turns out to be your room, with your real timestamps), **Fourth wall**, **The loop**, **Unreliable narrator**.

## About the style

Creepypasta craft is taught as *rules*, not copied text. Everything in `app/content.py` was written for this project. The optional style library is public-domain horror (Poe, M. R. James, Blackwood, Chambers, Henry James) from Project Gutenberg, shown to the model as tone references only.

## Tests

```bash
python scripts/selftest.py     # 600 simulated stories, 7,200 beats: every beat and every audit item must pass
node scripts/test_detect.js    # 10 unit tests for the room-sound detector
```

## Files

```
app/        content.py (story material) director.py checker.py writer.py corpus.py thread.py tts.py stt.py server.py
static/     index.html style.css app.js detect.js
scripts/    get_voice.py fetch_corpus.py selftest.py test_detect.js
```

## Honest limits

- The sound detector is loudness, spectral balance and timing, not an ML classifier. It tells a knock from speech from a rustle reasonably well; it cannot tell a door from a drawer.
- Use headphones. While the narrator speaks the mic is muted, but speakers still colour the room tone you calibrate against.
- Recording is a `.webm` captured in the browser (canvas + narration + a quiet room-tone drone). Browser-voice fallback narration is not captured in the video; Piper narration is.
- Developed in a sandbox without network access to Hugging Face or Ollama: the Piper voice download, real Ollama generation and Whisper transcription were exercised through their interfaces (mock model server, CLI flags) but not with real weights. Run `./run.sh` once on your machine and check the three status chips on the start screen.
