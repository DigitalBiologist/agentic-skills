// 用真实 headless Chrome（CDP，非 virtual-time）验证渲染：等 canvas 真正画出来再截图。
// 为什么不用 chrome --headless --screenshot --virtual-time-budget：virtual-time 驱动不了
// Web Worker 线程，PDF.js 用 worker 渲染，会一直停在 loading，截图骗人（见 SKILL.md 踩坑③）。
// 用法: node verify_render.js <输出目录>
const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');
const os = require('os');
const { pathToFileURL } = require('url');

const OUT = process.argv[2];
if (!OUT) { console.error('用法: node verify_render.js <输出目录>'); process.exit(1); }

// 跨平台探测 Chrome：CHROME_PATH 环境变量优先，再扫各平台常见安装位置。
function findChrome() {
  if (process.env.CHROME_PATH && fs.existsSync(process.env.CHROME_PATH)) return process.env.CHROME_PATH;
  const candidates = process.platform === 'win32' ? [
    'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
    'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe',
    (process.env.LOCALAPPDATA || '') + '\\Google\\Chrome\\Application\\chrome.exe',
  ] : process.platform === 'darwin' ? [
    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  ] : [
    '/usr/bin/google-chrome',
    '/usr/bin/google-chrome-stable',
    '/usr/bin/chromium',
    '/usr/bin/chromium-browser',
  ];
  for (const p of candidates) if (fs.existsSync(p)) return p;
  throw new Error('找不到 Chrome。请装 Chrome，或用 CHROME_PATH 环境变量指向你的 Chrome 可执行文件。');
}
const CHROME = findChrome();
// pathToFileURL 自动处理 Windows 反斜杠和盘符（生成 file:///D:/... 而非 file://D:%5C...）
const URL = pathToFileURL(path.resolve(OUT, 'index.html')).href;
const PORT = 9333 + Math.floor(Math.random() * 300);
// 跨平台临时目录（Windows: %TEMP%，Unix: /tmp）
const PROFILE = path.join(os.tmpdir(), 'cdpprof_paperskill_' + process.pid);
const sleep = ms => new Promise(r => setTimeout(r, ms));

const cp = spawn(CHROME, ['--headless=new','--disable-gpu','--no-sandbox',
  '--allow-file-access-from-files','--window-size=1400,950',
  '--remote-debugging-port=' + PORT, '--user-data-dir=' + PROFILE, URL]);

(async () => {
  let ws;
  for (let i = 0; i < 40 && !ws; i++) {
    try { const j = await (await fetch('http://localhost:' + PORT + '/json')).json();
      const pg = j.find(t => t.type === 'page'); if (pg) ws = pg.webSocketDebuggerUrl;
    } catch (e) {}
    if (!ws) await sleep(250);
  }
  if (!ws) { console.log('NO_WS'); cp.kill(); process.exit(2); }

  const sock = new WebSocket(ws);
  await new Promise(r => sock.onopen = r);
  let id = 0; const pend = {};
  sock.onmessage = e => { const d = JSON.parse(e.data); if (d.id && pend[d.id]) { pend[d.id](d.result); delete pend[d.id]; } };
  const cmd = (m, p) => new Promise(res => { const i = ++id; pend[i] = res; sock.send(JSON.stringify({ id: i, method: m, params: p || {} })); });

  await cmd('Runtime.enable');
  let ok = false, last;
  for (let i = 0; i < 60; i++) {
    const r = await cmd('Runtime.evaluate', { returnByValue: true, expression:
      "({load:!!document.getElementById('load'), canvases:document.querySelectorAll('#pdf-pane canvas').length, cards:document.querySelectorAll('#guide-body .card').length, ind:(document.getElementById('pageind')||{}).textContent, err:!!(document.getElementById('load')&&/失败/.test(document.getElementById('load').textContent))})" });
    last = r.result.value;
    if (last.err) { console.log('RENDER_ERROR:', JSON.stringify(last)); break; }
    if (last.canvases > 0 && !last.load) { ok = true; break; }
    await sleep(400);
  }
  console.log('FINAL:', JSON.stringify(last));
  const shot = await cmd('Page.captureScreenshot', { format: 'png' });
  const outpng = path.resolve(OUT, '_render_check.png');
  fs.writeFileSync(outpng, Buffer.from(shot.data, 'base64'));
  console.log(ok ? 'RENDER_OK' : 'RENDER_FAIL', '→ 截图:', outpng);
  cp.kill(); try { fs.rmSync(PROFILE, { recursive: true, force: true }); } catch (e) {}
  process.exit(ok ? 0 : 3);
})().catch(e => { console.error('ERR', e); cp.kill(); process.exit(1); });
