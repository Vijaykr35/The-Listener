"""Optional local speech-to-text with faster-whisper (open-weight Whisper models).

When the microphone hears you speak, the browser sends that one short clip to
THIS machine only. It is transcribed, the temp file is deleted immediately, and
the audio is never stored. If faster-whisper is not installed the story still
works; the narrator just hears 'a voice' instead of your words.

Install:   pip install faster-whisper
"""
import os
import tempfile
import threading
from pathlib import Path

MODEL = os.environ.get("GHOST_WHISPER", "tiny.en")
_lock = threading.Lock()
_model = None
_error = None


def installed():
    try:
        import importlib.util
        return importlib.util.find_spec("faster_whisper") is not None
    except Exception:  # noqa: BLE001
        return False


def status():
    return {"ok": installed() and _error is None, "model": MODEL,
            "error": None if installed() else "faster-whisper is not installed (pip install faster-whisper)"}


def _load():
    global _model, _error
    if _model is None:
        from faster_whisper import WhisperModel
        try:
            _model = WhisperModel(MODEL, device="cpu", compute_type="int8")
        except Exception as e:  # noqa: BLE001
            _error = str(e)
            raise
    return _model


def transcribe(wav_bytes):
    """Transcribe a short WAV clip. Returns '' when nothing intelligible was said."""
    if not installed():
        raise RuntimeError("faster-whisper is not installed")
    with _lock:
        model = _load()
        fd, path = tempfile.mkstemp(suffix=".wav")
        try:
            with os.fdopen(fd, "wb") as f:
                f.write(wav_bytes)
            segments, _ = model.transcribe(path, language="en", vad_filter=True, beam_size=1)
            parts = [s.text.strip() for s in segments if getattr(s, "no_speech_prob", 0) < 0.6]
        finally:
            Path(path).unlink(missing_ok=True)
    text = " ".join(parts).strip()
    # Whisper tends to hallucinate filler on near-silence
    if text.lower().strip(" .!") in {"you", "thank you", "thanks for watching", "bye", ""}:
        return ""
    return text[:160]
