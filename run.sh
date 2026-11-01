#!/usr/bin/env bash
# One-command launcher. Everything stays on 127.0.0.1.
set -e
cd "$(dirname "$0")"
pip install -q -r requirements.txt
[ -f voices/en_GB-alan-medium.onnx ] || python scripts/get_voice.py
if command -v ollama >/dev/null 2>&1; then
  ollama list 2>/dev/null | grep -q llama3.2 || ollama pull llama3.2:3b
else
  echo "Ollama not found: the app will use its built-in offline writer. Install from https://ollama.com for the full effect."
fi
python -m app
