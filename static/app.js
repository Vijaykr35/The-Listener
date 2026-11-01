/* ==========================================================================
   THE LISTENER — Interactive Psychological Fiction App
   Branching narrative with choices, custom input, neural voice narration,
   and literary slice-of-life endings.
   ========================================================================== */
(function () {
  'use strict';

  const $ = (id) => document.getElementById(id);
  const W = 1280, H = 720;
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  const clamp = (x, a, b) => Math.max(a, Math.min(b, x));
  const wallNow = () => new Date().toTimeString().slice(0, 8);
  const safe = (fn) => { try { return fn(); } catch (e) { return null; } };

  const S = {
    status: null, sid: null, bible: null, total: 0, n: 0, running: false, abort: false,
    ctx: null, recDest: null, beat: null, dread: 1, phase: 'idle',
    // Audio hardware sync
    syncMode: 'audio', audioStartTime: 0, audioDuration: 0, activeAudioSource: null, speechProgress: 0,
    // Timer state
    timerPaused: false, timerRemaining: 10, timerInterval: null,
    // Atmospheric particles & visual state
    motes: [], raindrops: [], steams: [], lampFlare: 1.0, recorder: null, chunks: [],
    // Story history
    storyBeats: [], userChoices: [], activeChoiceResolver: null,
  };

  /* ------------------------------------------------------------- neural & human voice */
  let browserVoices = [];
  function populateVoices() {
    const sel = $('voiceSelect');
    if (!sel) return;
    const curVal = sel.value;
    sel.innerHTML = '<option value="piper" selected>🎙️ Alan (Neural Narrator - Hushed Storyteller)</option>';

    if ('speechSynthesis' in window) {
      browserVoices = window.speechSynthesis.getVoices() || [];
      const scored = browserVoices.map((v, i) => {
        let score = 0;
        const n = v.name.toLowerCase(), l = v.lang.toLowerCase();
        if (n.includes('natural') || n.includes('online')) score += 60;
        if (n.includes('neural') || n.includes('google')) score += 50;
        if (n.includes('ryan') || n.includes('jenny') || n.includes('guy') || n.includes('alan')) score += 30;
        if (l.startsWith('en')) score += 15;
        return { v, i, score };
      }).sort((a, b) => b.score - a.score);

      scored.forEach(({ v, i }) => {
        const opt = document.createElement('option');
        opt.value = 'browser_' + i;
        opt.textContent = `Browser: ${v.name} (${v.lang})`;
        sel.appendChild(opt);
      });
    }

    if (curVal && sel.querySelector(`option[value="${curVal}"]`)) {
      sel.value = curVal;
    }
  }

  if ('speechSynthesis' in window) {
    window.speechSynthesis.onvoiceschanged = populateVoices;
    populateVoices();
  }

  async function previewSelectedVoice(sampleText) {
    const sel = $('voiceSelect');
    const val = sel ? sel.value : 'piper';
    const previewBtn = $('testVoiceBtn');
    if (previewBtn) { previewBtn.disabled = true; previewBtn.textContent = 'Speaking...'; }

    try {
      if (val === 'piper') {
        const r = await fetch('/api/tts', {
          method: 'POST',
          headers: { 'content-type': 'application/json' },
          body: JSON.stringify({ text: sampleText })
        });
        if (r.ok) {
          const AC = window.AudioContext || window.webkitAudioContext;
          if (!S.ctx) S.ctx = new AC();
          if (S.ctx.state === 'suspended') await S.ctx.resume();
          const buf = await S.ctx.decodeAudioData(await r.arrayBuffer());
          const src = S.ctx.createBufferSource();
          src.buffer = buf;
          src.connect(S.ctx.destination);
          src.start();
          src.onended = () => {
            if (previewBtn) { previewBtn.disabled = false; previewBtn.innerHTML = '<span class="play-icon">▶</span> Preview Voice'; }
          };
          return;
        }
      }

      if ('speechSynthesis' in window) {
        window.speechSynthesis.cancel();
        const u = new SpeechSynthesisUtterance(sampleText);
        if (val.startsWith('browser_')) {
          const idx = parseInt(val.replace('browser_', ''), 10);
          if (browserVoices[idx]) u.voice = browserVoices[idx];
        }
        u.rate = 0.94;
        u.pitch = 1.0;
        const resetBtn = () => { if (previewBtn) { previewBtn.disabled = false; previewBtn.innerHTML = '<span class="play-icon">▶</span> Preview Voice'; } };
        u.onend = resetBtn;
        u.onerror = resetBtn;
        window.speechSynthesis.speak(u);
        return;
      }
    } catch (e) {
      console.warn('Voice preview failed:', e);
    }
    if (previewBtn) { previewBtn.disabled = false; previewBtn.innerHTML = '<span class="play-icon">▶</span> Preview Voice'; }
  }

  if ($('testVoiceBtn')) {
    $('testVoiceBtn').addEventListener('click', () => {
      previewSelectedVoice('I set my mug down and listened. An ordinary afternoon, but the quiet between our words felt heavier than before.');
    });
  }

  // Length Cards click handlers
  const lengthOptions = document.querySelectorAll('.length-option');
  lengthOptions.forEach((opt) => {
    opt.addEventListener('click', () => {
      lengthOptions.forEach((o) => o.classList.remove('active'));
      opt.classList.add('active');
      const val = opt.getAttribute('data-val');
      if ($('length')) $('length').value = val;
    });
  });

  /* ----------------------------------------------------------------- audio setup */
  async function setupAudio() {
    const AC = window.AudioContext || window.webkitAudioContext;
    S.ctx = new AC();
    S.recDest = S.ctx.createMediaStreamDestination();

    // Subtle, warm ambient acoustic drone: D minor warm hum (very low volume)
    const masterGain = S.ctx.createGain(); masterGain.gain.value = 0.025;
    const filter = S.ctx.createBiquadFilter(); filter.type = 'lowpass'; filter.frequency.value = 280;
    masterGain.connect(filter);
    filter.connect(S.ctx.destination);
    filter.connect(S.recDest);

    const freqs = [73.42, 110.0, 146.83]; // D2, A2, D3
    freqs.forEach((f) => {
      const osc = S.ctx.createOscillator();
      osc.type = 'triangle';
      osc.frequency.value = f;
      const g = S.ctx.createGain();
      g.gain.value = 0.3;
      osc.connect(g);
      g.connect(masterGain);
      osc.start();
    });

    S.drone = masterGain;
  }

  function playCeramicChime() {
    if (!S.ctx) return;
    const now = S.ctx.currentTime;
    const osc = S.ctx.createOscillator();
    const g = S.ctx.createGain();
    osc.type = 'sine';
    osc.frequency.setValueAtTime(1240, now);
    osc.frequency.exponentialRampToValueAtTime(820, now + 0.35);

    g.gain.setValueAtTime(0.12, now);
    g.gain.exponentialRampToValueAtTime(0.0001, now + 0.6);

    osc.connect(g);
    g.connect(S.ctx.destination);
    osc.start(now);
    osc.stop(now + 0.65);

    // Visual reaction: burst of steam
    burstSteam(10);
  }

  /* -------------------------------------------------------------- API helpers */
  async function api(path, opts) {
    const r = await fetch(path, opts);
    if (!r.ok) {
      const t = await r.text();
      throw new Error(`API ${r.status}: ${t}`);
    }
    return r.json();
  }

  /* ------------------------------------------------------------- main flow */
  async function begin() {
    const btn = $('begin');
    btn.disabled = true;
    btn.innerHTML = '<span class="btn-text">Initializing story...</span>';

    try {
      await setupAudio();
      if (S.ctx.state === 'suspended') await S.ctx.resume();

      const len = $('length') ? $('length').value : 'standard';
      const session = await api('/api/session', {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({ length: len })
      });

      S.sid = session.id;
      S.bible = session.bible;
      S.phase = 'running';
      S.storyBeats = [];
      S.userChoices = [];
      S.abort = false;

      $('start').hidden = true;
      $('stage').hidden = false;
      $('result').hidden = true;

      initAtmosphericScene();
      requestAnimationFrame(frame);
      startRecording();

      await runStory(session.initial_choices || []);
    } catch (e) {
      console.error('Session start error:', e);
      alert('Could not start story session: ' + e.message);
      btn.disabled = false;
      btn.innerHTML = '<span class="btn-text">Begin the Story</span><span class="btn-icon">→</span>';
    }
  }

  /* ------------------------------------------------------------- audio narration */
  async function narrate(text) {
    const words = text.split(/\s+/).length;
    const guess = window.__fastTest ? 350 : clamp(words * 320 + 800, 3000, 30000);
    
    // Wave animation active
    if ($('audioWaveWrap')) $('audioWaveWrap').classList.add('playing');
    if ($('waveStatus')) $('waveStatus').textContent = 'Narrating';

    const finishNarrationState = () => {
      if ($('audioWaveWrap')) $('audioWaveWrap').classList.remove('playing');
      if ($('waveStatus')) $('waveStatus').textContent = 'Listening';
    };

    if (!$('useVoice').checked) {
      S.syncMode = 'timer';
      S.revealStart = performance.now();
      S.revealMs = guess;
      await sleep(guess);
      finishNarrationState();
      return { ms: guess, done: Promise.resolve() };
    }

    const sel = $('voiceSelect');
    const voiceChoice = sel ? sel.value : 'piper';

    // 1. PRIMARY: In-Memory Neural Piper TTS (/api/tts)
    if (voiceChoice === 'piper' || !('speechSynthesis' in window)) {
      try {
        const r = await fetch('/api/tts', {
          method: 'POST',
          headers: { 'content-type': 'application/json' },
          body: JSON.stringify({ text })
        });
        if (r.ok) {
          const arrayBuf = await r.arrayBuffer();
          const buf = await S.ctx.decodeAudioData(arrayBuf);
          const durationMs = buf.duration * 1000;

          const src = S.ctx.createBufferSource();
          src.buffer = buf;
          const g = S.ctx.createGain();
          g.gain.value = 0.95;
          src.connect(g);
          src.connect(S.ctx.destination);
          src.connect(S.recDest);

          // EXACT AUDIO HARDWARE CLOCK SYNCHRONIZATION
          S.syncMode = 'audio';
          S.audioDuration = buf.duration;
          S.audioStartTime = S.ctx.currentTime;
          S.activeAudioSource = src;

          const done = new Promise((res) => {
            src.onended = () => {
              S.activeAudioSource = null;
              finishNarrationState();
              res();
            };
          });

          src.start();
          return { ms: durationMs, done };
        }
      } catch (e) {
        console.warn('Backend Piper TTS failed, falling back to browser speech:', e);
      }
    }

    // 2. SECONDARY: Web Speech API fallback
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      const u = new SpeechSynthesisUtterance(text);
      if (voiceChoice.startsWith('browser_')) {
        const idx = parseInt(voiceChoice.replace('browser_', ''), 10);
        if (browserVoices[idx]) u.voice = browserVoices[idx];
      }
      u.rate = 0.94;
      u.pitch = 1.0;

      S.syncMode = 'speech';
      S.speechProgress = 0.01;

      u.onboundary = (e) => {
        if (e.name === 'word') {
          const charIdx = e.charIndex + (e.charLength || 3);
          S.speechProgress = clamp(charIdx / Math.max(1, text.length), 0.05, 1);
        }
      };

      const done = new Promise((res) => {
        let finished = false;
        const finish = () => {
          if (!finished) {
            finished = true;
            S.speechProgress = 1.0;
            finishNarrationState();
            res();
          }
        };
        u.onend = finish;
        u.onerror = finish;
        setTimeout(finish, guess + 4000);
      });

      window.speechSynthesis.speak(u);
      return { ms: guess, done };
    }

    // 3. Simple Timer fallback
    S.syncMode = 'timer';
    S.revealStart = performance.now();
    S.revealMs = guess;
    await sleep(guess);
    finishNarrationState();
    return { ms: guess, done: Promise.resolve() };
  }

  /* ------------------------------------------------------------- interactive choice engine */
  function promptUserChoice(choices) {
    const box = $('choiceBox');
    const container = $('choiceCards');
    const prompt = $('choicePrompt');
    const timerSecEl = $('timerSec');
    const prog = $('choiceTimerProgress');
    const timerBadge = $('autoTimerBadge');
    if (!box || !container) return Promise.resolve(null);

    container.innerHTML = '';
    const actName = S.beat ? S.beat.act : 'The Incident';
    prompt.textContent = actName === 'The turn' ? 'The unspoken truth surfaces. What do you do?' : 'What do you do next?';

    return new Promise((resolve) => {
      let resolved = false;

      const finishChoice = (choiceObj, customInput) => {
        if (resolved) return;
        resolved = true;
        clearInterval(S.timerInterval);
        box.hidden = true;
        window.removeEventListener('keydown', handleKeyChoice);

        if (choiceObj && choiceObj.text) {
          const t = choiceObj.text.toLowerCase();
          if (t.includes('tea') || t.includes('cup') || t.includes('mug')) playCeramicChime();
          else if (t.includes('window') || t.includes('rain')) burstRain(25);
          else if (t.includes('lamp') || t.includes('light')) S.lampFlare = 2.2;
        }

        resolve({ choice: choiceObj, user_input: customInput });
      };

      S.activeChoiceResolver = finishChoice;

      // Render choice cards (Card 1 is default/basic story)
      choices.forEach((c, idx) => {
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'choice-card-btn' + (c.is_default ? ' default-choice' : '');
        btn.innerHTML = `
          <div class="choice-tag">${c.is_default ? '★ Canonical Story Path' : 'Option ' + (idx + 1)} · [Key ${idx + 1}]</div>
          <strong>${c.text}</strong>
        `;
        btn.addEventListener('click', () => finishChoice(c, null));
        container.appendChild(btn);
      });

      // Freeform action form submit
      const form = $('actionForm');
      form.onsubmit = (e) => {
        e.preventDefault();
        const inputVal = $('actionInput').value.trim();
        if (!inputVal) return;
        $('actionInput').value = '';
        finishChoice(null, inputVal);
      };

      // Keyboard shortcut navigation (1, 2, 3)
      const handleKeyChoice = (e) => {
        if (document.activeElement === $('actionInput')) return;
        if (['1', '2', '3'].includes(e.key)) {
          const idx = parseInt(e.key, 10) - 1;
          if (choices[idx]) {
            e.preventDefault();
            finishChoice(choices[idx], null);
          }
        }
      };
      window.addEventListener('keydown', handleKeyChoice);

      box.hidden = false;

      // 10-Second Auto-Advance Countdown for "generate the basic story if user does not respond"
      S.timerRemaining = 10;
      S.timerPaused = false;
      timerSecEl.textContent = S.timerRemaining;
      prog.style.width = '100%';
      timerBadge.innerHTML = 'Auto-advancing basic story in <b id="timerSec">10</b>s';

      const toggleBtn = $('toggleTimerBtn');
      toggleBtn.textContent = 'Pause';
      toggleBtn.onclick = () => {
        S.timerPaused = !S.timerPaused;
        toggleBtn.textContent = S.timerPaused ? 'Resume' : 'Pause';
        timerBadge.innerHTML = S.timerPaused ? 'Timer paused (Take your time)' : 'Auto-advancing basic story in <b id="timerSec">' + S.timerRemaining + '</b>s';
      };

      clearInterval(S.timerInterval);
      const startTime = performance.now();
      const totalDuration = 10000;

      S.timerInterval = setInterval(() => {
        if (S.timerPaused) return;
        const elapsed = performance.now() - startTime;
        const remaining = Math.max(0, totalDuration - elapsed);
        const sec = Math.ceil(remaining / 1000);
        S.timerRemaining = sec;
        const timerNum = $('timerSec');
        if (timerNum) timerNum.textContent = sec;
        prog.style.width = (remaining / totalDuration * 100) + '%';

        if (remaining <= 0) {
          clearInterval(S.timerInterval);
          const defaultChoice = choices.find((c) => c.is_default) || choices[0];
          finishChoice(defaultChoice, null);
        }
      }, 100);
    });
  }

  /* ------------------------------------------------------------- story loop */
  async function runStory(initialChoices) {
    let done = false;
    let nextChoices = initialChoices;
    let pendingChoice = null;
    let pendingInput = null;

    while (!done && !S.abort) {
      if ($('storyPhase')) $('storyPhase').textContent = `Beat ${S.n + 1} of ${S.total || 12}`;

      // Request next beat with user's chosen path
      let res;
      try {
        res = await api('/api/session/' + S.sid + '/beat', {
          method: 'POST',
          headers: { 'content-type': 'application/json' },
          body: JSON.stringify({
            choice: pendingChoice,
            user_input: pendingInput,
            wall: wallNow()
          })
        });
      } catch (e) {
        if ($('storyPhase')) $('storyPhase').textContent = 'Story interrupted';
        break;
      }

      const beat = res.beat;
      S.beat = beat;
      S.n = beat.n;
      S.total = beat.total || S.total || 12;
      S.dread = beat.dread;
      done = res.done;
      nextChoices = res.choices || [];
      S.storyBeats.push(beat);

      // Update UI Header and Meta
      if ($('storyPhase')) $('storyPhase').textContent = `Beat ${beat.n} of ${S.total}`;
      if ($('storyTime')) $('storyTime').textContent = beat.time || wallNow();
      if ($('beatBadge')) $('beatBadge').textContent = `ACT · ${beat.act.toUpperCase()}`;

      // Update DOM prose display with animated reveal
      updateDomProse(beat.text);

      // Narrate with 100% audio sync
      const nar = await narrate(beat.text);
      await nar.done;

      // Ensure full text is displayed after narration ends
      const proseEl = $('proseCurrent');
      if (proseEl) proseEl.textContent = beat.text;

      if (done) {
        S.finalEnding = res.ending;
        break;
      }

      // Present branching choices to the user
      const userResponse = await promptUserChoice(nextChoices);
      if (S.abort) break;

      pendingChoice = userResponse ? userResponse.choice : null;
      pendingInput = userResponse ? userResponse.user_input : null;
    }

    await finish();
  }

  // Update DOM prose progressively during narration
  function updateDomProse(text) {
    const proseEl = $('proseCurrent');
    if (!proseEl) return;
    proseEl.textContent = text;
  }

  async function finish() {
    clearInterval(S.timerInterval);
    if ($('storyPhase')) $('storyPhase').textContent = 'Story completed';
    if ($('choiceBox')) $('choiceBox').hidden = true;
    safe(() => document.fullscreenElement && document.exitFullscreen());
    const videoReady = stopRecording();

    let storySummary = S.finalEnding;
    if (!storySummary) {
      try { storySummary = await api('/api/session/' + S.sid + '/story'); } catch (e) { /* ignore */ }
    }

    await sleep(400);
    $('stage').hidden = true;
    if (storySummary) renderResult(storySummary);
    else $('start').hidden = false;

    const beginBtn = $('begin');
    if (beginBtn) {
      beginBtn.disabled = false;
      beginBtn.innerHTML = '<span class="btn-text">Begin the Story</span><span class="btn-icon">→</span>';
    }

    const v = await videoReady;
    if (v) showVideo(v);
  }

  /* ------------------------------------------------------------- recording */
  function startRecording() {
    S.recorder = null; S.chunks = [];
    if (!$('useRec').checked || !window.MediaRecorder) return;
    try {
      const cv = $('screen'), vs = cv.captureStream(30);
      S.recDest.stream.getAudioTracks().forEach((t) => vs.addTrack(t));
      const types = ['video/webm;codecs=vp9,opus', 'video/webm;codecs=vp8,opus', 'video/webm'];
      const mime = types.find((t) => MediaRecorder.isTypeSupported(t));
      S.recorder = new MediaRecorder(vs, mime ? { mimeType: mime, videoBitsPerSecond: 4500000 } : undefined);
      S.recorder.ondataavailable = (e) => { if (e.data && e.data.size) S.chunks.push(e.data); };
      S.recorder.start(1000);
    } catch (e) { S.recorder = null; }
  }

  function stopRecording() {
    return new Promise((res) => {
      const r = S.recorder;
      if (!r || r.state === 'inactive') return res(null);
      r.onstop = () => res(S.chunks.length ? URL.createObjectURL(new Blob(S.chunks, { type: 'video/webm' })) : null);
      setTimeout(() => safe(() => r.stop()), 1800);
    });
  }

  function showVideo(url) {
    const box = $('videoBox');
    if (!box) return;
    box.hidden = false; box.innerHTML = '';
    const v = document.createElement('video'); v.controls = true; v.src = url; box.appendChild(v);
    const a = document.createElement('a'); a.className = 'btn-download-txt'; a.href = url; a.download = 'story-recording.webm'; a.textContent = '📥 Download story video (.webm)';
    box.appendChild(a);
  }

  /* ----------------------------------------------------------- ending result page */
  function renderResult(summary) {
    if ($('endingBadge')) $('endingBadge').textContent = summary.badge || 'ENDING REACHED';
    if ($('endingTitle')) $('endingTitle').textContent = summary.title;
    if ($('endingSubtitle')) $('endingSubtitle').textContent = summary.subtitle;
    if ($('endingBlurb')) $('endingBlurb').textContent = summary.blurb;

    // Render full transcript
    const transBox = $('storyTranscript');
    if (transBox) {
      transBox.innerHTML = '';
      (summary.story_transcript || []).forEach((b) => {
        const d = document.createElement('div');
        d.className = 'transcript-beat';
        d.innerHTML = `<div class="transcript-time">${b.time} · ${b.act}</div><p class="transcript-text">${b.text}</p>`;
        transBox.appendChild(d);
      });
    }

    // Render choices timeline
    const timeList = $('choicesTimeline');
    if (timeList) {
      timeList.innerHTML = '';
      if (!summary.choices_timeline || !summary.choices_timeline.length) {
        timeList.innerHTML = '<li><span class="timeline-text">You followed the basic canonical story path.</span></li>';
      } else {
        summary.choices_timeline.forEach((c) => {
          const li = document.createElement('li');
          li.innerHTML = `<span class="timeline-time">${c.wall}</span><span class="timeline-text">${c.text}</span>`;
          timeList.appendChild(li);
        });
      }
    }

    if ($('dlStory')) $('dlStory').href = '/api/session/' + S.sid + '/story.txt';
    $('result').hidden = false;
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  /* ------------------------------------------------- atmospheric visual canvas */
  const cv = $('screen'), g = cv.getContext('2d');
  const rnd = (() => { let s = 98765; return () => ((s = (s * 16807) % 2147483647) / 2147483647); })();
  const grain = document.createElement('canvas'); grain.width = grain.height = 160;
  (function () {
    const gc = grain.getContext('2d'), id = gc.createImageData(160, 160);
    for (let i = 0; i < id.data.length; i += 4) {
      const v = rnd() * 255;
      id.data[i] = id.data[i + 1] = id.data[i + 2] = v;
      id.data[i + 3] = 255;
    }
    gc.putImageData(id, 0, 0);
  })();

  function initAtmosphericScene() {
    // Raindrops on window pane
    S.raindrops = [];
    for (let i = 0; i < 45; i++) {
      S.raindrops.push({
        x: 740 + Math.random() * 450,
        y: Math.random() * 420,
        len: 12 + Math.random() * 22,
        speed: 2.2 + Math.random() * 4.5,
        alpha: 0.2 + Math.random() * 0.45
      });
    }

    // Floating dust motes in lamp light
    S.motes = [];
    for (let i = 0; i < 35; i++) {
      S.motes.push({
        x: 340 + Math.random() * 320,
        y: 260 + Math.random() * 260,
        vx: (Math.random() - 0.5) * 0.35,
        vy: -0.2 - Math.random() * 0.4,
        size: 1.5 + Math.random() * 2.5,
        alpha: 0.15 + Math.random() * 0.4
      });
    }

    // Steam particles from mug
    S.steams = [];
    for (let i = 0; i < 18; i++) {
      S.steams.push({
        x: 535 + (Math.random() - 0.5) * 16,
        y: 470 - Math.random() * 60,
        vx: (Math.random() - 0.5) * 0.4,
        vy: -0.6 - Math.random() * 0.8,
        size: 3 + Math.random() * 7,
        alpha: 0.25 - Math.random() * 0.15
      });
    }
  }

  function burstSteam(count) {
    for (let i = 0; i < count; i++) {
      S.steams.push({
        x: 535 + (Math.random() - 0.5) * 20,
        y: 465,
        vx: (Math.random() - 0.5) * 1.5,
        vy: -1.2 - Math.random() * 1.8,
        size: 4 + Math.random() * 8,
        alpha: 0.5
      });
    }
  }

  function burstRain(count) {
    for (let i = 0; i < count; i++) {
      S.raindrops.push({
        x: 740 + Math.random() * 450,
        y: Math.random() * 120,
        len: 18 + Math.random() * 25,
        speed: 5.5 + Math.random() * 5,
        alpha: 0.7
      });
    }
  }

  function wrap(text, font, maxW) {
    g.font = font; const out = []; let line = '';
    text.split(/\s+/).forEach((w) => {
      const t = line ? line + ' ' + w : w;
      if (g.measureText(t).width > maxW && line) { out.push(line); line = w; }
      else line = t;
    });
    if (line) out.push(line); return out;
  }

  // Draw realistic contemporary interior: desk lamp, rainy window, mug
  function drawAtmosphericScene(t, dread) {
    const k = dread / 10;
    
    // Room background: quiet late afternoon / dusk gradient
    const bg = g.createLinearGradient(0, 0, 0, H);
    bg.addColorStop(0, '#0c0e15');
    bg.addColorStop(0.65, '#07080c');
    bg.addColorStop(1, '#040507');
    g.fillStyle = bg; g.fillRect(0, 0, W, H);

    // Rainy Window Frame on Right Side
    const wx = 740, wy = 40, ww = 460, wh = 420;
    
    // Outside rainy night sky gradient with distant city warmth
    const sky = g.createLinearGradient(0, wy, 0, wy + wh);
    sky.addColorStop(0, '#060810');
    sky.addColorStop(0.7, '#0b101c');
    sky.addColorStop(1, '#151320');
    g.fillStyle = sky;
    g.fillRect(wx, wy, ww, wh);

    // Distant blurred city bokeh lights through rain
    const bokehs = [
      [820, 220, 16, '#f5af4b', 0.25],
      [930, 280, 24, '#e09f3e', 0.18],
      [1040, 190, 20, '#4ea8de', 0.22],
      [1120, 260, 14, '#ffd166', 0.28],
      [870, 340, 28, '#f5af4b', 0.15],
      [990, 320, 18, '#56cfe1', 0.2],
    ];

    bokehs.forEach(([bx, by, br, color, alpha]) => {
      const pulse = 1 + Math.sin(t * 1.5 + bx) * 0.15;
      const bGrad = g.createRadialGradient(bx, by, 1, bx, by, br * pulse);
      bGrad.addColorStop(0, color);
      bGrad.addColorStop(1, 'rgba(0,0,0,0)');
      g.save();
      g.globalAlpha = alpha;
      g.fillStyle = bGrad;
      g.beginPath(); g.arc(bx, by, br * pulse, 0, Math.PI * 2); g.fill();
      g.restore();
    });

    // Animate raindrops sliding down window
    g.strokeStyle = 'rgba(180, 210, 240, 0.4)';
    g.lineWidth = 1.5;
    g.beginPath();
    for (let i = 0; i < S.raindrops.length; i++) {
      const r = S.raindrops[i];
      r.y += r.speed;
      if (r.y > wy + wh) {
        r.y = wy;
        r.x = wx + Math.random() * ww;
      }
      g.moveTo(r.x, r.y);
      g.lineTo(r.x + 1, r.y + r.len);
    }
    g.stroke();

    // Window frame border & mullions
    g.strokeStyle = '#1a1d29';
    g.lineWidth = 12;
    g.strokeRect(wx, wy, ww, wh);
    g.lineWidth = 6;
    // Crossbars
    g.beginPath();
    g.moveTo(wx + ww / 2, wy); g.lineTo(wx + ww / 2, wy + wh);
    g.moveTo(wx, wy + wh * 0.45); g.lineTo(wx + ww, wy + wh * 0.45);
    g.stroke();

    // Desk Foreground Surface (Polished warm walnut wood)
    const deskY = 470;
    const deskGrad = g.createLinearGradient(0, deskY, 0, H);
    deskGrad.addColorStop(0, '#1a1412');
    deskGrad.addColorStop(0.35, '#120d0b');
    deskGrad.addColorStop(1, '#090706');
    g.fillStyle = deskGrad;
    g.fillRect(0, deskY, W, H - deskY);

    // Desk top edge highlight line
    g.fillStyle = 'rgba(245, 175, 75, 0.18)';
    g.fillRect(0, deskY, W, 2);

    // Warm Architectural Desk Lamp (Left / Center)
    const lx = 370, ly = 240;
    if (S.lampFlare > 1.0) S.lampFlare = Math.max(1.0, S.lampFlare - 0.02);
    const flick = (0.95 + 0.05 * Math.sin(t * 4)) * S.lampFlare;

    // Gooseneck stem
    g.strokeStyle = '#2d2f3b';
    g.lineWidth = 6;
    g.beginPath();
    g.moveTo(280, deskY);
    g.quadraticCurveTo(260, 220, lx, ly);
    g.stroke();

    // Lampshade cone
    g.fillStyle = '#222530';
    g.beginPath();
    g.moveTo(lx - 25, ly - 10);
    g.lineTo(lx + 35, ly - 10);
    g.lineTo(lx + 55, ly + 35);
    g.lineTo(lx - 45, ly + 35);
    g.closePath();
    g.fill();
    g.strokeStyle = 'rgba(245, 175, 75, 0.4)';
    g.lineWidth = 2;
    g.stroke();

    // Warm bulb glow
    const bulbGlow = g.createRadialGradient(lx + 5, ly + 25, 2, lx + 5, ly + 25, 30);
    bulbGlow.addColorStop(0, '#ffffff');
    bulbGlow.addColorStop(0.4, '#ffd166');
    bulbGlow.addColorStop(1, 'rgba(245, 175, 75, 0)');
    g.fillStyle = bulbGlow;
    g.beginPath(); g.arc(lx + 5, ly + 25, 30, 0, Math.PI * 2); g.fill();

    // Broad conical light pool across desk
    const coneGrad = g.createRadialGradient(lx + 10, ly + 40, 20, 480, deskY + 100, 360);
    coneGrad.addColorStop(0, `rgba(255, 220, 140, ${0.45 * flick})`);
    coneGrad.addColorStop(0.5, `rgba(245, 175, 75, ${0.18 * flick})`);
    coneGrad.addColorStop(1, 'rgba(0, 0, 0, 0)');
    g.fillStyle = coneGrad;
    g.beginPath();
    g.moveTo(lx - 35, ly + 35);
    g.lineTo(820, deskY + 240);
    g.lineTo(160, deskY + 240);
    g.closePath();
    g.fill();

    // Ceramic Mug on Desk with Rising Steam
    const mx = 535, my = 470;
    // Mug drop shadow
    g.fillStyle = 'rgba(0, 0, 0, 0.6)';
    g.beginPath(); g.ellipse(mx, my + 38, 24, 7, 0, 0, Math.PI * 2); g.fill();

    // Mug body
    g.fillStyle = '#dfd8cc';
    g.beginPath();
    g.moveTo(mx - 18, my);
    g.lineTo(mx + 18, my);
    g.lineTo(mx + 15, my + 36);
    g.lineTo(mx - 15, my + 36);
    g.closePath();
    g.fill();
    // Mug rim
    g.fillStyle = '#f0ebe1';
    g.beginPath(); g.ellipse(mx, my, 18, 5, 0, 0, Math.PI * 2); g.fill();
    // Dark tea inside
    g.fillStyle = '#422818';
    g.beginPath(); g.ellipse(mx, my + 1, 15, 3.5, 0, 0, Math.PI * 2); g.fill();
    // Mug handle
    g.strokeStyle = '#dfd8cc';
    g.lineWidth = 4;
    g.beginPath();
    g.arc(mx + 20, my + 18, 9, -Math.PI / 2, Math.PI / 2, false);
    g.stroke();

    // Draw rising steam
    g.save();
    for (let i = 0; i < S.steams.length; i++) {
      const s = S.steams[i];
      s.y += s.vy;
      s.x += s.vx + Math.sin(t * 2 + s.y * 0.04) * 0.4;
      s.size += 0.08;
      s.alpha -= 0.003;
      if (s.y < my - 90 || s.alpha <= 0) {
        s.y = my;
        s.x = mx + (Math.random() - 0.5) * 12;
        s.size = 3 + Math.random() * 4;
        s.alpha = 0.25;
      }
      g.fillStyle = `rgba(255, 255, 255, ${s.alpha})`;
      g.beginPath(); g.arc(s.x, s.y, s.size, 0, Math.PI * 2); g.fill();
    }
    g.restore();

    // Planted Desk Items: Notebook & Envelope
    // Notebook
    g.fillStyle = '#1e2230';
    g.fillRect(350, deskY + 15, 95, 65);
    g.fillStyle = '#f4ede2';
    g.fillRect(353, deskY + 18, 42, 59);
    g.fillRect(398, deskY + 18, 43, 59);
    g.strokeStyle = '#3d445c';
    g.lineWidth = 1;
    g.strokeRect(350, deskY + 15, 95, 65);
    // Pen across spine
    g.strokeStyle = '#c49746';
    g.lineWidth = 3;
    g.beginPath(); g.moveTo(394, deskY + 10); g.lineTo(396, deskY + 75); g.stroke();

    // Envelope
    g.save();
    g.translate(620, deskY + 25);
    g.rotate(0.08);
    g.fillStyle = '#ede5d8';
    g.fillRect(0, 0, 75, 48);
    g.strokeStyle = '#c9beac';
    g.lineWidth = 1;
    g.beginPath();
    g.moveTo(0, 0); g.lineTo(37.5, 25); g.lineTo(75, 0);
    g.stroke();
    g.restore();

    // Floating Dust Motes in Lamp Beam
    g.save();
    for (let i = 0; i < S.motes.length; i++) {
      const m = S.motes[i];
      m.x += m.vx + Math.sin(t * 1.2 + m.y * 0.02) * 0.3;
      m.y += m.vy;
      if (m.y < ly) m.y = deskY + 50;
      if (m.x < 240) m.x = 600;
      if (m.x > 620) m.x = 260;

      g.fillStyle = `rgba(255, 235, 190, ${m.alpha * flick})`;
      g.beginPath(); g.arc(m.x, m.y, m.size, 0, Math.PI * 2); g.fill();
    }
    g.restore();
  }

  /* Subtitles & HUD rendered on Canvas (primarily for recorded video output) */
  function drawOverlay(now, t) {
    const b = S.beat;

    // Header bar
    g.fillStyle = 'rgba(9, 10, 15, 0.78)';
    g.fillRect(0, 0, W, 48);
    g.font = '600 13px ui-monospace, Menlo, monospace';
    g.fillStyle = '#f5af4b';
    g.fillText('THE LISTENER  ·  INTERACTIVE PSYCHOLOGICAL FICTION', 24, 30);

    g.fillStyle = '#9fa4b2';
    g.textAlign = 'right';
    g.fillText(b ? `BEAT ${b.n} OF ${S.total || 12}  ·  ${b.time}` : 'BEGINNING STORY', W - 24, 30);
    g.textAlign = 'left';

    // Cinematic subtitles box for recorded video
    if (b) {
      let p = 0;
      if (S.syncMode === 'audio' && S.audioDuration > 0 && S.ctx) {
        const elapsed = Math.max(0, S.ctx.currentTime - S.audioStartTime);
        p = clamp(elapsed / S.audioDuration, 0, 1);
      } else if (S.syncMode === 'speech') {
        p = clamp(S.speechProgress || 0, 0, 1);
      } else {
        p = clamp((now - S.revealStart) / S.revealMs, 0, 1);
      }

      const words = b.text.split(' ');
      const wordsToShow = Math.min(words.length, Math.floor(p * words.length * 1.02) + 1);
      const textShown = p >= 0.99 ? b.text : words.slice(0, wordsToShow).join(' ');

      const lines = wrap(textShown, '500 26px "Lora", Georgia, serif', W - 260), lh = 40;
      const top = H - 90 - lines.length * lh - 15;

      const grad = g.createLinearGradient(0, top - 45, 0, H);
      grad.addColorStop(0, 'rgba(0,0,0,0)');
      grad.addColorStop(0.3, 'rgba(9, 10, 15, 0.88)');
      grad.addColorStop(1, 'rgba(5, 6, 9, 0.98)');
      g.fillStyle = grad; g.fillRect(0, top - 45, W, H - top + 45);

      g.font = '500 26px "Lora", Georgia, serif';
      g.fillStyle = '#f5f3ef';
      g.shadowColor = 'rgba(0, 0, 0, 0.9)';
      g.shadowBlur = 10;
      lines.forEach((l, i) => g.fillText(l, 130, top + 30 + i * lh));
      g.shadowBlur = 0;
    }
  }

  function frame(now) {
    if (S.phase === 'done' || $('stage').hidden) return;
    const t = now / 1000, dread = S.dread || 1, k = dread / 10;
    drawAtmosphericScene(t, dread);

    if (S.drone) {
      S.drone.gain.value = 0.015 + 0.02 * k * (0.8 + 0.2 * Math.sin(t * 0.7));
    }

    // Subtle film grain
    g.globalAlpha = 0.04 + 0.03 * k;
    g.globalCompositeOperation = 'overlay';
    g.drawImage(grain, (Math.floor(now / 40) % 7) * 11, 0, 160, 160, 0, 0, W, H);
    g.globalAlpha = 1;
    g.globalCompositeOperation = 'source-over';

    drawOverlay(now, t);
    requestAnimationFrame(frame);
  }

  /* ------------------------------------------------ interactive quick buttons */
  if ($('btnChime')) $('btnChime').addEventListener('click', playCeramicChime);
  if ($('btnPetals')) $('btnPetals').addEventListener('click', () => burstRain(30));
  if ($('btnFlame')) $('btnFlame').addEventListener('click', () => { S.lampFlare = 2.4; });

  if ($('begin')) $('begin').addEventListener('click', begin);
  if ($('finish')) $('finish').addEventListener('click', () => { S.abort = true; finish(); });
  if ($('again')) $('again').addEventListener('click', () => {
    $('result').hidden = true;
    $('start').hidden = false;
    window.scrollTo({ top: 0, behavior: 'smooth' });
  });

  populateVoices();
})();
