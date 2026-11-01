# The Listener: a ghost story that listens back

**Ghost in the Machine submission.** Open-weight model + open TTS + open speech recognition, all on one laptop, no internet required.

I built a ghost story that is written live from what your room does while you sit in it. Headphones on, lights off. A local model (Llama 3.2 via Ollama) writes a creepypasta one beat at a time, as a tired narrator posting updates to a night-owl forum. Your microphone is the other author. A knock on the wall becomes "something bumped the other side of the wall, softly, like it was checking the wall was still there." A long silence becomes "the refrigerator stopped humming." Say "is anyone there" out loud, and a few beats later the hallway answers in your voice, slightly wrong. Look away from the screen, and when you look back the door is open wider. Piper narrates it, and the whole thing is rendered to a video you can download.

**The turn.** The story plants a psychological reversal at the start. My favourite: *The sounds are yours.* The narrator puts the timestamps of the night's strange noises into a column and realizes none of them happened in their apartment. Those are your real timestamps, from your real room. At the end, the app hands you the forum thread and a case file of what the microphone actually heard.

**Why open wins here.**
- *Privacy.* An always-on mic is as private as input gets. With an open stack, the audio never leaves the machine. There is no API key and no account.
- *Offline.* Unplug the network. It still works.
- *Free.* Zero cost per story.
- *Control.* A 3B model will happily wander off and explain the monster. So the model doesn't run the story: a director holds a hidden story bible, an act structure and a dread curve, and a rule checker verifies every beat in code (never name the thing, one wrong detail at a time, planted details must pay off, the rule is broken exactly once, end unresolved). Bad drafts go back to the model with the exact violations; after two misses a template writer built from the same bible steps in. I could only build that loop because I could see and swap every piece. 600 simulated stories pass every rule.

**Style, not copying.** Creepypasta craft is taught as rules and original exemplars, with public-domain horror (Poe, M. R. James, Blackwood) as an optional style library. No scraped stories.

Stack: Ollama (Llama 3.2 3B), Piper TTS, faster-whisper, FastAPI, vanilla JS + canvas + MediaRecorder.
