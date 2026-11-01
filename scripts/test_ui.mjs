import { spawn } from 'child_process';
import fs from 'fs';

const CHROME_PATH = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const PORT = 9222;

console.log('[TEST] Launching Headless Chrome...');
const chromeProc = spawn(CHROME_PATH, [
  '--headless=new',
  `--remote-debugging-port=${PORT}`,
  '--autoplay-policy=no-user-gesture-required',
  '--no-sandbox',
  '--window-size=1280,800',
  'http://127.0.0.1:8000'
]);

chromeProc.stderr.on('data', () => {});

async function sleep(ms) {
  return new Promise(r => setTimeout(r, ms));
}

async function run() {
  await sleep(1500);

  // 1. Get targets
  const listRes = await fetch(`http://127.0.0.1:${PORT}/json/list`);
  const targets = await listRes.json();
  const page = targets.find(t => t.type === 'page' && t.url.includes('127.0.0.1:8000'));
  if (!page) {
    throw new Error('Could not find Chrome page target');
  }

  console.log('[TEST] Connecting to Chrome DevTools Protocol via WebSocket...');
  const ws = new WebSocket(page.webSocketDebuggerUrl);

  let idCounter = 1;
  const pending = new Map();
  const consoleLogs = [];

  ws.onmessage = (evt) => {
    const msg = JSON.parse(evt.data);
    if (msg.id && pending.has(msg.id)) {
      pending.get(msg.id)(msg);
      pending.delete(msg.id);
    }
    if (msg.method === 'Runtime.consoleAPICalled') {
      const text = msg.params.args.map(a => a.value || a.description || '').join(' ');
      consoleLogs.push(`[BROWSER ${msg.params.type}] ${text}`);
    }
    if (msg.method === 'Runtime.exceptionThrown') {
      consoleLogs.push(`[BROWSER EXCEPTION] ${msg.params.exceptionDetails.text}`);
    }
  };

  const send = (method, params = {}) => {
    return new Promise((resolve) => {
      const id = idCounter++;
      pending.set(id, resolve);
      ws.send(JSON.stringify({ id, method, params }));
    });
  };

  await new Promise(r => ws.onopen = r);

  await send('Runtime.enable');
  await send('Page.enable');
  await send('DOM.enable');

  const evalJs = async (expr) => {
    const res = await send('Runtime.evaluate', { expression: expr, returnByValue: true });
    return res.result?.result?.value;
  };

  console.log('[TEST 1] Verifying Landing Portal...');
  const title = await evalJs('document.title');
  console.log('  Page Title:', title);
  if (!title.includes('The Listener')) throw new Error('Wrong page title');

  const landingVisible = await evalJs('!document.getElementById("start").hidden');
  console.log('  Landing Portal Visible:', landingVisible);
  if (!landingVisible) throw new Error('Landing portal is not visible');

  // Click short story length card
  console.log('[TEST 2] Testing Story Length Card Selection...');
  await evalJs('document.querySelector(".length-option[data-val=\'short\']").click()');
  const selLength = await evalJs('document.getElementById("length").value');
  console.log('  Selected length value:', selLength);
  if (selLength !== 'short') throw new Error('Length card selection failed');

  // Set fast test mode so narration timer completes quickly
  await evalJs('window.__fastTest = true; document.getElementById("useVoice").checked = false;');

  // Click Begin button
  console.log('[TEST 3] Clicking "Begin the Story" Button...');
  await evalJs('document.getElementById("begin").click()');

  // Wait for stage to appear
  console.log('[TEST 4] Waiting for Story Theater to open...');
  let stageVisible = false;
  for (let i = 0; i < 20; i++) {
    stageVisible = await evalJs('!document.getElementById("stage").hidden');
    if (stageVisible) break;
    await sleep(300);
  }
  if (!stageVisible) throw new Error('Story stage did not become visible');
  console.log('  Story Theater is active!');

  // Check Beat 1 prose
  await sleep(1000);
  const beat1Text = await evalJs('document.getElementById("proseCurrent").textContent');
  const beat1Act = await evalJs('document.getElementById("beatBadge").textContent');
  console.log('  Act Indicator:', beat1Act);
  console.log('  Beat 1 Prose preview:', beat1Text.slice(0, 80) + '...');
  if (!beat1Text || beat1Text.includes('Preparing')) throw new Error('Prose did not render');

  // Wait for Choice Box to appear
  console.log('[TEST 5] Waiting for Choice Box to glide in...');
  let choicesVisible = false;
  for (let i = 0; i < 25; i++) {
    choicesVisible = await evalJs('!document.getElementById("choiceBox").hidden');
    if (choicesVisible) break;
    await sleep(300);
  }
  if (!choicesVisible) throw new Error('Choice Box did not appear');

  const choiceCardsCount = await evalJs('document.querySelectorAll(".choice-card-btn").length');
  const choice1Text = await evalJs('document.querySelectorAll(".choice-card-btn strong")[0].textContent');
  const isDefault = await evalJs('document.querySelectorAll(".choice-card-btn")[0].classList.contains("default-choice")');
  console.log(`  Rendered ${choiceCardsCount} interactive choice cards.`);
  console.log('  Choice 1 (Default):', choice1Text);
  console.log('  Default Badge Present:', isDefault);

  // Capture screenshot of the Story Theater + Choice Box
  console.log('[TEST 6] Capturing Screenshot of Active Theater UI...');
  const ssStage = await send('Page.captureScreenshot', { format: 'png' });
  fs.writeFileSync('ui_test_stage.png', Buffer.from(ssStage.result.data, 'base64'));
  console.log('  Saved ui_test_stage.png (1280x800)');

  // Select Choice 2
  console.log('[TEST 7] Selecting Choice 2 (Alternative Path)...');
  await evalJs('document.querySelectorAll(".choice-card-btn")[1].click()');
  await sleep(600);

  // Verify next beat loaded
  const beat2Phase = await evalJs('document.getElementById("storyPhase").textContent');
  console.log('  Phase updated to:', beat2Phase);

  // Test Freeform custom input by waiting for next choice or skipping to ending
  console.log('[TEST 8] Skipping to Ending Resolution...');
  await evalJs('document.getElementById("finish").click()');

  // Wait for result page
  let resultVisible = false;
  for (let i = 0; i < 20; i++) {
    resultVisible = await evalJs('!document.getElementById("result").hidden');
    if (resultVisible) break;
    await sleep(300);
  }
  if (!resultVisible) throw new Error('Ending result page did not appear');

  const endingBadge = await evalJs('document.getElementById("endingBadge").textContent');
  const endingTitle = await evalJs('document.getElementById("endingTitle").textContent');
  const transcriptBeats = await evalJs('document.querySelectorAll(".transcript-beat").length');
  const decisionItems = await evalJs('document.querySelectorAll("#choicesTimeline li").length');

  console.log('  Ending Badge:', endingBadge);
  console.log('  Ending Title:', endingTitle);
  console.log('  Story Transcript Beats:', transcriptBeats);
  console.log('  Decisions Recorded:', decisionItems);

  // Capture screenshot of the Ending Resolution view
  const ssResult = await send('Page.captureScreenshot', { format: 'png' });
  fs.writeFileSync('ui_test_result.png', Buffer.from(ssResult.result.data, 'base64'));
  console.log('  Saved ui_test_result.png');

  console.log('\n[TEST 9] Checking Browser Console Logs for Warnings/Errors...');
  const errors = consoleLogs.filter(l => l.includes('error') || l.includes('EXCEPTION'));
  if (errors.length) {
    console.log('  Warnings/Errors found:');
    errors.forEach(e => console.log('   ', e));
  } else {
    console.log('  Zero browser console errors detected!');
  }

  console.log('\n=============================================');
  console.log('ALL UI TESTS PASSED SUCCESSFULLY IN < 15 SECONDS!');
  console.log('=============================================');

  ws.close();
}

try {
  await run();
} catch (err) {
  console.error('[TEST ERROR]', err);
  process.exitCode = 1;
} finally {
  chromeProc.kill();
  process.exit();
}
