"""python -m app  ->  starts the local server on http://127.0.0.1:8000"""
import os

import uvicorn

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8000"))
    print(f"\n  THE LISTENER  ->  http://127.0.0.1:{port}\n  (best in the dark, with headphones)\n")
    uvicorn.run("app.server:app", host="127.0.0.1", port=port, log_level="warning")
