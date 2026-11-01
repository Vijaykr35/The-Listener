/* Room-sound detector. Pure logic (no browser APIs) so it can be unit tested in Node.
 *
 * Input: one frame at a time {rms, low, mid, high} from the microphone analyser.
 * Output: events like thud, creak, voice, rustle, silence, learned against a
 * noise floor calibrated from the first seconds in YOUR room. No ML model, no upload:
 * it is loudness, spectral balance and timing.
 */
(function (root) {
  'use strict';
  const clamp = (x, a, b) => Math.max(a, Math.min(b, x));

  function rmsOf(buf) { // Uint8Array from getByteTimeDomainData
    let s = 0;
    for (let i = 0; i < buf.length; i++) { const v = (buf[i] - 128) / 128; s += v * v; }
    return Math.sqrt(s / buf.length);
  }

  function bandsOf(freq, sampleRate) { // Uint8Array from getByteFrequencyData
    const n = freq.length, hz = (sampleRate / 2) / n;
    let lo = 0, mid = 0, hi = 0;
    for (let i = 1; i < n; i++) {
      const f = i * hz, e = Math.pow(freq[i] / 255, 2);
      if (f < 250) lo += e; else if (f < 3000) mid += e; else if (f < 12000) hi += e;
    }
    const tot = lo + mid + hi || 1e-9;
    return { low: lo / tot, mid: mid / tot, high: hi / tot };
  }

  class Detector {
    constructor(opts) {
      this.o = Object.assign({ silenceSec: 8, cooldown: 1.5, voiceMin: 0.9, voiceEnd: 0.7 }, opts || {});
      this.reset();
    }
    reset() {
      this.floor = 0.01; this.calib = []; this.calibrated = false;
      this.prevAvg = 0; this.last = {}; this.sus = null;
      this.quietSince = null; this.silentActive = false; this.mutedUntil = 0;
    }
    calibrate(rms) { this.calib.push(rms); }
    finishCalibration() {
      const n = this.calib.length || 1;
      const mean = this.calib.reduce((a, b) => a + b, 0) / n;
      this.floor = clamp(mean, 0.004, 0.08);
      this.calibrated = true; this.calib = [];
    }
    pause() { this.sus = null; this.quietSince = null; this.silentActive = false; }
    resume(now, graceSec) { this.mutedUntil = now + (graceSec == null ? 0.6 : graceSec); this.quietSince = null; }
    _ready(type, now) {
      if (this.last[type] !== undefined && now - this.last[type] < this.o.cooldown) return false;
      this.last[type] = now; return true;
    }
    thresholds() {
      const f = this.floor;
      return { spike: Math.max(f * 3.2, f + 0.035), sound: Math.max(f * 1.8, f + 0.012), quiet: Math.max(f * 1.35, f + 0.004) };
    }
    /* Report a silence that is still going on (called when the story asks for events). */
    flush(now) {
      if (this.silentActive && this.quietSince !== null) {
        const dur = now - this.quietSince;
        this.silentActive = false; this.quietSince = now;
        return [{ type: 'silence', dur }];
      }
      return [];
    }
    process(fr, now) {
      const out = [];
      const rms = fr.rms;
      if (now < this.mutedUntil) { this.prevAvg = rms; return out; }
      const th = this.thresholds();

      // 1) sudden impulse: knock, bump, creak
      if (rms > th.spike && rms > this.prevAvg * 2.2 && fr.mid < 0.6 && this._ready('spike', now)) {
        out.push({ type: fr.high > 0.45 ? 'creak' : 'thud', level: rms });
      }
      this.prevAvg = this.prevAvg * 0.9 + rms * 0.1;

      // 2) sustained sound: a voice (mid-band) or a rustle (high band)
      if (rms > th.sound) {
        if (!this.sus) this.sus = { start: now, last: now, n: 0, mid: 0, high: 0, peak: 0 };
        const s = this.sus;
        s.last = now; s.n++; s.mid += fr.mid; s.high += fr.high; s.peak = Math.max(s.peak, rms);
      } else if (this.sus && now - this.sus.last > this.o.voiceEnd) {
        const s = this.sus, d = s.last - s.start;
        if (d >= this.o.voiceMin) {
          const m = s.mid / s.n, h = s.high / s.n;
          if (m > 0.45) out.push({ type: 'voice', dur: d, level: s.peak });
          else if (h > 0.4 && s.peak < th.spike) out.push({ type: 'rustle', dur: d, level: s.peak });
        }
        this.sus = null;
      }

      // 3) silence: reported when it ends (or when flushed)
      if (rms < th.quiet) {
        if (this.quietSince === null) this.quietSince = now;
        if (!this.silentActive && now - this.quietSince >= this.o.silenceSec) this.silentActive = true;
      } else {
        if (this.silentActive && this.quietSince !== null) out.push({ type: 'silence', dur: now - this.quietSince });
        this.quietSince = null; this.silentActive = false;
      }

      // slowly follow the room's tone
      if (rms < th.sound) this.floor = Math.max(0.004, this.floor + (rms - this.floor) * 0.002);
      return out;
    }
  }

  const api = { Detector, rmsOf, bandsOf };
  if (typeof module !== 'undefined' && module.exports) module.exports = api; else root.GhostDetect = api;
})(typeof self !== 'undefined' ? self : this);
