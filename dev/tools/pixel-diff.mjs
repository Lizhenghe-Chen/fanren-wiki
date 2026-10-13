#!/usr/bin/env node
/**
 * 零依赖像素比对：把两份页面在固定相机下渲染，逐像素算差异并做聚类，用来证明「重构没改观感」。
 *
 *   node dev/tools/pixel-diff.mjs index.html _ref_head.html [--out /tmp/dir] [--cams "900,2200,.42;800,3000,.85"]
 *
 * 页面参数按 public/ 的相对路径解析，图片/脚本能直接取到；要跟历史版本比，先把它落到 public 下：
 *   git show HEAD:public/index.html > public/_ref_head.html   （比完记得删）
 *
 * ⚠️ 必须走 http：`file://` 下 canvas 被判定跨域污染，`getImageData`/`toDataURL` 会抛 SecurityError。
 * ⚠️ 确定性靠「页面脚本执行前注入固定 rAF 时间戳 + 固定 Math.random」；否则粒子与壁障虚线相位每次
 *    都不同，任何两次截图都会有差异（实测同代码两次运行：0 像素差异）。
 *
 * 判据看**聚类形状**，不看总数：散点 / 规则格点上的小方块 / 均匀低幅度铺满 ⇒ 重采样与抗锯齿相位（无害）；
 * 连成一条边、整块平移、少一条带 ⇒ 结构性错位（必须查）。
 * 输出目录保留两侧 PNG 与 diff.html（`?a=&b=` 可换图复核），默认 /tmp/fw-pixel-diff。
 */
import { spawn } from 'node:child_process'
import { createServer } from 'node:http'
import { existsSync, mkdtempSync, mkdirSync, readFileSync, rmSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { extname, join, normalize, resolve, sep } from 'node:path'

const ROOT = resolve(import.meta.dirname, '..', '..')
const PUBLIC = join(ROOT, 'public')
const OUT_PREFIX = '/__out/'

const argv = process.argv.slice(2)
const flag = (name, fallback) => {
  const i = argv.indexOf(name)
  return i > -1 ? argv[i + 1] : fallback
}
const positional = argv.filter((a, i) => !a.startsWith('--') && !(i > 0 && argv[i - 1].startsWith('--')))
const [PAGE_A, PAGE_B] = positional
const CAMS = flag('--cams', '900,2200,.42;800,3000,.85;1500,2000,.2').split(';').map(s => s.split(',').map(Number))
const OUT = resolve(flag('--out', join(tmpdir(), 'fw-pixel-diff')))
const VIEW = [1440, 900]

if (!PAGE_A || !PAGE_B) {
  console.error('用法：node dev/tools/pixel-diff.mjs <A.html> <B.html> [--out 目录] [--cams "x,y,z;x,y,z"]')
  process.exit(2)
}
const CHROME = flag('--chrome', process.env.CHROME_PATH) || [
  '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge',
  '/Applications/Chromium.app/Contents/MacOS/Chromium',
  '/usr/bin/google-chrome',
  '/usr/bin/chromium',
].find(existsSync)
if (!CHROME) { console.error('找不到 Chrome：用 --chrome <路径> 或 CHROME_PATH 指定'); process.exit(2) }

const MIME = { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css', '.json': 'application/json', '.webp': 'image/webp', '.jpg': 'image/jpeg', '.png': 'image/png', '.svg': 'image/svg+xml', '.ico': 'image/x-icon', '.xml': 'application/xml', '.txt': 'text/plain' }
const sleep = ms => new Promise(r => setTimeout(r, ms))

/* ---------- 静态服务：`/` → public/，`/__out/` → 输出目录（同源，像素才读得到） ---------- */
function serve() {
  const server = createServer((req, res) => {
    const pathname = decodeURIComponent(new URL(req.url, 'http://x').pathname)
    const [root, rest] = pathname.startsWith(OUT_PREFIX)
      ? [OUT, pathname.slice(OUT_PREFIX.length)]
      : [PUBLIC, pathname.replace(/^\//, '')]
    const path = normalize(join(root, rest))
    if (!(path === root || path.startsWith(root + sep)) || !existsSync(path)) { res.writeHead(404).end('404'); return }
    res.writeHead(200, { 'content-type': MIME[extname(path)] || 'application/octet-stream' })
    res.end(readFileSync(path))
  })
  return new Promise(res => server.listen(0, '127.0.0.1', () => res(server)))
}

/* ---------- CDP 极简客户端 ---------- */
async function launch() {
  const profile = mkdtempSync(join(tmpdir(), 'fw-diff-'))
  const proc = spawn(CHROME, ['--headless=new', '--remote-debugging-port=0', `--user-data-dir=${profile}`,
    '--no-first-run', '--no-default-browser-check', '--hide-scrollbars', '--disable-extensions',
    '--force-device-scale-factor=1', `--window-size=${VIEW[0]},${VIEW[1]}`], { stdio: ['ignore', 'ignore', 'pipe'] })
  const wsUrl = await new Promise((res, rej) => {
    let buf = ''
    const timer = setTimeout(() => rej(new Error('等待 DevTools 端口超时')), 20000)
    proc.stderr.on('data', d => { buf += d; const m = buf.match(/ws:\/\/\S+/); if (m) { clearTimeout(timer); res(m[0]) } })
    proc.on('exit', c => { clearTimeout(timer); rej(new Error(`Chrome 提前退出（code ${c}）`)) })
  })
  const target = await (await fetch(`http://127.0.0.1:${new URL(wsUrl).port}/json/new?about:blank`, { method: 'PUT' })).json()
  const ws = new WebSocket(target.webSocketDebuggerUrl)
  await new Promise((res, rej) => { ws.addEventListener('open', res); ws.addEventListener('error', rej) })
  let seq = 0
  const pending = new Map()
  ws.addEventListener('message', ev => {
    const msg = JSON.parse(ev.data)
    if (msg.id && pending.has(msg.id)) {
      const { res, rej } = pending.get(msg.id)
      pending.delete(msg.id)
      msg.error ? rej(new Error(msg.error.message)) : res(msg.result)
    }
  })
  const send = (method, params = {}) => new Promise((res, rej) => {
    const id = ++seq
    pending.set(id, { res, rej })
    ws.send(JSON.stringify({ id, method, params }))
  })
  const evaluate = async expression => {
    const r = await send('Runtime.evaluate', { expression, returnByValue: true, awaitPromise: true })
    if (r.exceptionDetails) throw new Error(r.exceptionDetails.exception?.description || '页面内求值失败')
    return r.result.value
  }
  return { send, evaluate, close: () => { try { ws.close() } catch {} ; proc.kill('SIGKILL'); try { rmSync(profile, { recursive: true, force: true }) } catch {} } }
}

/* 固定时钟 + 固定随机数：同代码两次运行 → 完全相同的像素。
   顺带把 rAF 节流到 ~5fps：固定时间戳意味着 dt=0，若仍按浏览器最快节奏空转，一个 headless 实例能烧满一核。 */
const FREEZE = `
  Math.random = (function(){ let s = 123456789; return function(){ s = (s * 1103515245 + 12345) % 2147483648; return s / 2147483648; }; })();
  (function(){ const raf = window.requestAnimationFrame.bind(window);
    window.requestAnimationFrame = cb => raf(() => setTimeout(() => cb(10000), 200)); })();
`

const DIFF_PAGE = `<!doctype html><meta charset="utf-8"><body><script>
const q = new URLSearchParams(location.search);
const load = src => new Promise((res, rej) => { const i = new Image(); i.onload = () => res(i); i.onerror = rej; i.src = src; });
(async () => {
  try {
    const [A, B] = await Promise.all([load(q.get('a')), load(q.get('b'))]);
    const W = A.naturalWidth, H = A.naturalHeight;
    const ca = document.createElement('canvas'), cb = document.createElement('canvas');
    ca.width = cb.width = W; ca.height = cb.height = H;
    const xa = ca.getContext('2d'), xb = cb.getContext('2d', { willReadFrequently: true });
    xa.drawImage(A, 0, 0); xb.drawImage(B, 0, 0);
    const da = xa.getImageData(0, 0, W, H).data, db = xb.getImageData(0, 0, W, H).data;
    const diff = new Uint8Array(W * H);
    let n = 0, sum = 0;
    for (let i = 0, p = 0; i < da.length; i += 4, p++) {
      const d = Math.max(Math.abs(da[i]-db[i]), Math.abs(da[i+1]-db[i+1]), Math.abs(da[i+2]-db[i+2]));
      diff[p] = d; sum += d;
      if (d > 2) n++;
    }
    const seen = new Uint8Array(W * H), clusters = [];
    for (let p = 0; p < W * H; p++) {
      if (diff[p] <= 2 || seen[p]) continue;
      const stack = [p]; seen[p] = 1;
      let size = 0, max = 0, x0 = W, y0 = H, x1 = -1, y1 = -1;
      while (stack.length) {
        const cur = stack.pop(), qx = cur % W, qy = (cur / W) | 0;
        size++; if (diff[cur] > max) max = diff[cur];
        if (qx < x0) x0 = qx; if (qx > x1) x1 = qx; if (qy < y0) y0 = qy; if (qy > y1) y1 = qy;
        for (let dy = -1; dy <= 1; dy++) for (let dx = -1; dx <= 1; dx++) {
          const nx = qx + dx, ny = qy + dy;
          if (nx < 0 || ny < 0 || nx >= W || ny >= H) continue;
          const r = ny * W + nx;
          if (!seen[r] && diff[r] > 2) { seen[r] = 1; stack.push(r); }
        }
      }
      clusters.push({ n: size, max, box: x0 + ',' + y0 + '-' + x1 + ',' + y1 });
    }
    clusters.sort((p, q) => q.n - p.n);
    document.title = JSON.stringify({ size: W + 'x' + H, diffPixels: n, ratio: +(n / (W * H) * 100).toFixed(3), meanDelta: +(sum / (W * H)).toFixed(4), clusterCount: clusters.length, clusters: clusters.slice(0, 12) });
  } catch (e) { document.title = 'ERR ' + e.message; }
})();
</` + `script></body>`

const server = await serve()
const base = `http://127.0.0.1:${server.address().port}/`
const page = await launch()
await page.send('Page.enable')
await page.send('Runtime.enable')
await page.send('Page.addScriptToEvaluateOnNewDocument', { source: FREEZE })
await page.send('Emulation.setDeviceMetricsOverride', { width: VIEW[0], height: VIEW[1], deviceScaleFactor: 1, mobile: false })
mkdirSync(OUT, { recursive: true })
writeFileSync(join(OUT, 'diff.html'), DIFF_PAGE)

/* 拍照：进舆图视图 → 强制 boot → 固定相机 → 取画布像素（PNG 落盘便于人工复核） */
async function shots(tag, pagePath) {
  const files = []
  for (let i = 0; i < CAMS.length; i++) {
    const [x, y, z] = CAMS[i]
    await page.send('Page.navigate', { url: base + pagePath })
    await sleep(1800)
    await page.evaluate(`location.hash = '#v-map'`)
    await sleep(1500)
    await page.evaluate(`window.__fanrenMap && window.__fanrenMap.boot()`)
    await sleep(600)
    await page.evaluate(`window.__fanrenMap && window.__fanrenMap.snapView(${x},${y},${z})`)
    await sleep(300)
    await page.evaluate(`window.__fanrenMap && window.__fanrenMap.snapView(${x},${y},${z})`)
    await sleep(300)
    const dataUrl = await page.evaluate(`document.getElementById('cv').toDataURL('image/png')`)
    const name = `${tag}-${i}.png`
    writeFileSync(join(OUT, name), Buffer.from(dataUrl.split(',')[1], 'base64'))
    console.log(`  ${tag}[${i}] 相机 (${x},${y},${z}) → ${(dataUrl.length / 1024) | 0}KB`)
    files.push(name)
  }
  return files
}

console.log(`A = ${PAGE_A}\nB = ${PAGE_B}\n输出目录 = ${OUT}\n`)
const a = await shots('a', PAGE_A)
const b = await shots('b', PAGE_B)

console.log('\n=== 像素差异（至少一个通道差 > 2 记为不同像素） ===')
let worst = 0
for (let i = 0; i < CAMS.length; i++) {
  const url = `${base}${OUT_PREFIX.slice(1)}diff.html?a=${a[i]}&b=${b[i]}`
  await page.send('Page.navigate', { url })
  await sleep(900)
  const title = await page.evaluate(`document.title`)
  let shown = title
  try {
    const r = JSON.parse(title)
    worst = Math.max(worst, r.ratio)
    shown = JSON.stringify({ size: r.size, diffPixels: r.diffPixels, ratio: r.ratio + '%', meanDelta: r.meanDelta, clusterCount: r.clusterCount })
    if (r.clusters.length) shown += '\n      ' + r.clusters.slice(0, 6).map(c => `${c.n}px@${c.box}(最大${c.max})`).join('  ')
  } catch {}
  console.log(`  相机 ${i} (${CAMS[i].join(', ')}) → ${shown}`)
}
console.log(`\n最大差异占比 ${worst.toFixed(3)}%。形状是散点 / 规则小方块 ⇒ 重采样相位；连成边、整块平移、少一条带 ⇒ 结构错位。`)

page.close()
server.close()
