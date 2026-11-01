"""Narration with Piper, an open-source neural text-to-speech engine that runs
fully offline on a CPU. The neural voice file lives in ./voices.

Voice: en_GB-alan-medium (hushed, restrained British male storytelling voice)
"""
import hashlib
import io
import os
import subprocess
import sys
import tempfile
import threading
import wave
from collections import OrderedDict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VOICE_DIR = Path(os.environ.get("GHOST_VOICE_DIR", ROOT / "voices"))
VOICE = os.environ.get("GHOST_VOICE", "en_GB-alan-medium")

_cache = OrderedDict()
_lock = threading.Lock()
_piper_voice = None
_piper_voice_name = None


def model_path():
    return VOICE_DIR / f"{VOICE}.onnx"


def piper_installed():
    try:
        import importlib.util
        return importlib.util.find_spec("piper") is not None
    except Exception:  # noqa: BLE001
        return False


def status():
    mp = model_path()
    ok = piper_installed() and mp.exists()
    why = None
    if not piper_installed():
        why = "piper-tts is not installed (pip install piper-tts)"
    elif not mp.exists():
        why = f"voice file missing: run python scripts/get_voice.py ({VOICE})"
    return {"ok": ok, "voice": VOICE, "error": why}


def get_voice():
    """Load and cache the in-memory PiperVoice model for instant (<400ms) synthesis."""
    global _piper_voice, _piper_voice_name
    mp = model_path()
    if not mp.exists():
        raise RuntimeError(f"voice file missing: {mp.name}")
    if _piper_voice is not None and _piper_voice_name == VOICE:
        return _piper_voice
    with _lock:
        if _piper_voice is not None and _piper_voice_name == VOICE:
            return _piper_voice
        from piper import PiperVoice
        _piper_voice = PiperVoice.load(str(mp))
        _piper_voice_name = VOICE
        return _piper_voice


def synth(text):
    """Return WAV bytes for text. Uses in-memory neural synthesis with disk-cache fallback."""
    text = " ".join(text.split())[:1200]
    if not text:
        raise RuntimeError("empty text")
    key = hashlib.sha1((VOICE + "|" + text).encode()).hexdigest()
    if key in _cache:
        _cache.move_to_end(key)
        return _cache[key]
    st = status()
    if not st["ok"]:
        raise RuntimeError(st["error"])

    # Fast in-memory synthesis via PiperVoice (no subprocess reload overhead)
    try:
        voice = get_voice()
        buf = io.BytesIO()
        with wave.open(buf, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(voice.config.sample_rate)
            for chunk in voice.synthesize(text):
                wf.writeframes(chunk.audio_int16_bytes)
        data = buf.getvalue()
    except Exception as e:
        # Fallback to subprocess if in-memory fails
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "line.wav"
            proc = subprocess.run(
                [sys.executable, "-m", "piper", "--model", str(model_path()), "--output_file", str(out)],
                input=text.encode(), capture_output=True, timeout=120,
            )
            if proc.returncode != 0 or not out.exists():
                raise RuntimeError(f"piper failed: {e}; subprocess: {proc.stderr.decode(errors='ignore')[-300:]}")
            data = out.read_bytes()

    _cache[key] = data
    if len(_cache) > 64:
        _cache.popitem(last=False)
    return data
