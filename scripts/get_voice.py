"""Download a Piper voice into ./voices (one-time, then fully offline).

    python scripts/get_voice.py                      # en_GB-alan-medium (hushed British male)
    python scripts/get_voice.py en_US-ryan-high      # any voice from rhasspy/piper-voices
"""
import sys
import urllib.request
from pathlib import Path

BASE = "https://huggingface.co/rhasspy/piper-voices/resolve/main"


def voice_url(name):
    # name looks like en_GB-alan-medium -> en/en_GB/alan/medium/en_GB-alan-medium
    locale, speaker, quality = name.split("-", 2)
    lang = locale.split("_")[0]
    return f"{BASE}/{lang}/{locale}/{speaker}/{quality}/{name}"


def main():
    name = sys.argv[1] if len(sys.argv) > 1 else "en_GB-alan-medium"
    out = Path(__file__).resolve().parent.parent / "voices"
    out.mkdir(exist_ok=True)
    for ext in (".onnx", ".onnx.json"):
        dest = out / (name + ext)
        if dest.exists() and dest.stat().st_size > 0:
            print("have", dest.name)
            continue
        url = voice_url(name) + ext
        print("downloading", url)
        urllib.request.urlretrieve(url, dest)
        print("  ->", dest, f"{dest.stat().st_size / 1e6:.1f} MB")
    print(f"\nDone. Run the app with:  GHOST_VOICE={name} python -m app")


if __name__ == "__main__":
    main()
