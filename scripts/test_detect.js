// Unit test for the room-sound detector.  node scripts/test_detect.js
const assert = require('assert');
const { Detector } = require('../static/detect.js');

const FPS = 25, DT = 1 / FPS;
function run(det, segments, startT = 0) {
  const events = []; let t = startT;
  for (const [sec, fr] of segments) {
    for (let i = 0; i < sec * FPS; i++) {
      for (const e of det.process(fr, t)) events.push({ ...e, at: +t.toFixed(2) });
      t += DT;
    }
  }
  return { events, t };
}
function calibrated(floor = 0.01) {
  const d = new Detector();
  for (let i = 0; i < 75; i++) d.calibrate(floor);
  d.finishCalibration();
  return d;
}
const QUIET = { rms: 0.01, low: 0.34, mid: 0.33, high: 0.33 };
const KNOCK = { rms: 0.30, low: 0.80, mid: 0.15, high: 0.05 };
const SQUEAK = { rms: 0.22, low: 0.05, mid: 0.20, high: 0.75 };
const SPEECH = { rms: 0.08, low: 0.15, mid: 0.75, high: 0.10 };
const HISS = { rms: 0.03, low: 0.05, mid: 0.25, high: 0.70 };

// 1. calibration sets the floor from the room
{ const d = calibrated(0.02); assert.ok(Math.abs(d.floor - 0.02) < 1e-9); }

// 2. a knock is a thud, once, even if it lasts several frames
{ const { events } = run(calibrated(), [[2, QUIET], [0.12, KNOCK], [2, QUIET]]);
  const t = events.filter(e => e.type === 'thud');
  assert.strictEqual(t.length, 1, JSON.stringify(events)); }

// 3. a high-band spike is a creak
{ const { events } = run(calibrated(), [[2, QUIET], [0.1, SQUEAK], [2, QUIET]]);
  assert.ok(events.some(e => e.type === 'creak'), JSON.stringify(events)); }

// 4. speech: no spike event, one voice event when it ends, with a duration
{ const { events } = run(calibrated(), [[2, QUIET], [2.0, SPEECH], [2, QUIET]]);
  assert.ok(!events.some(e => e.type === 'thud' || e.type === 'creak'), JSON.stringify(events));
  const v = events.filter(e => e.type === 'voice');
  assert.strictEqual(v.length, 1, JSON.stringify(events));
  assert.ok(v[0].dur > 1.5 && v[0].dur < 2.2); }

// 5. a short blip of speech-like sound is ignored
{ const { events } = run(calibrated(), [[2, QUIET], [0.4, SPEECH], [2, QUIET]]);
  assert.ok(!events.some(e => e.type === 'voice'), JSON.stringify(events)); }

// 6. a rustle is a sustained high-band sound
{ const { events } = run(calibrated(), [[2, QUIET], [1.5, HISS], [2, QUIET]]);
  assert.ok(events.some(e => e.type === 'rustle'), JSON.stringify(events)); }

// 7. silence is reported when it ends, with its length
{ const { events } = run(calibrated(), [[10, QUIET], [0.1, KNOCK], [1, QUIET]]);
  const s = events.find(e => e.type === 'silence');
  assert.ok(s && s.dur >= 9.5 && s.dur <= 10.2, JSON.stringify(events)); }

// 8. flush reports an ongoing silence once, then re-arms
{ const d = calibrated(); const { t } = run(d, [[9, QUIET]]);
  const a = d.flush(t); assert.strictEqual(a.length, 1); assert.ok(a[0].dur >= 8);
  assert.strictEqual(d.flush(t + 0.1).length, 0); }

// 9. paused/muted frames (while the narrator speaks) produce nothing
{ const d = calibrated(); d.pause(); d.resume(0, 5);
  const { events } = run(d, [[4, KNOCK]]);
  assert.strictEqual(events.length, 0, JSON.stringify(events)); }

// 10. a noisy room (high floor) does not fire on its own tone
{ const noisy = { rms: 0.05, low: 0.3, mid: 0.4, high: 0.3 };
  const { events } = run(calibrated(0.05), [[10, noisy]]);
  assert.strictEqual(events.length, 0, JSON.stringify(events)); }

console.log('detector: 10 tests passed');
