#!/usr/bin/env node
/**
 * 零依赖验收脚本：用 CDP 直接驱动本机 Chrome，对 public/index.html 跑结构性 + 交互断言。
 * 只需要 Node ≥ 22（内建 WebSocket / fetch）+ 本机 Chrome，不需要 npm install。
 *
 *   node dev/tools/verify.mjs                          # 默认 file:// 直开 public/index.html
 *   node dev/tools/verify.mjs --url http://localhost:8899/index.html
 *   node dev/tools/verify.mjs --chrome "/path/to/chrome"
 *
 * 设计约定：每条断言只断一件事，失败时打印实测值，便于定位是哪一层坏了。
 */
import { spawn } from 'node:child_process'
import { existsSync, mkdtempSync, readdirSync, rmSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join, resolve } from 'node:path'
import { pathToFileURL } from 'node:url'

const ROOT = resolve(import.meta.dirname, '..', '..')
const argOf = (flag, fallback) => {
  const i = process.argv.indexOf(flag)
  return i > -1 ? process.argv[i + 1] : fallback
}
const TARGET = argOf('--url', pathToFileURL(join(ROOT, 'public', 'index.html')).href)

const CHROME = argOf('--chrome', process.env.CHROME_PATH) || [
  '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge',
  '/Applications/Chromium.app/Contents/MacOS/Chromium',
  '/usr/bin/google-chrome',
  '/usr/bin/chromium',
  '/usr/bin/chromium-browser',
  'C:/Program Files/Google/Chrome/Application/chrome.exe',
].find(existsSync)
if (!CHROME) {
  console.error('找不到 Chrome：请用 --chrome <路径> 或 CHROME_PATH 指定')
  process.exit(2)
}

/* ---------- 断言收集 ---------- */
const results = []
const check = (name, ok, detail = '') => {
  results.push({ name, ok: !!ok, detail: ok ? '' : detail })
  console.log(`${ok ? '  ok  ' : ' FAIL '} ${name}${ok ? '' : '  →  ' + detail}`)
}

const sleep = ms => new Promise(r => setTimeout(r, ms))

/* ---------- CDP 极简客户端 ---------- */
async function launch() {
  const profile = mkdtempSync(join(tmpdir(), 'fw-verify-'))
  const proc = spawn(CHROME, [
    '--headless=new', '--remote-debugging-port=0', `--user-data-dir=${profile}`,
    '--no-first-run', '--no-default-browser-check', '--hide-scrollbars',
    '--disable-extensions', '--force-device-scale-factor=1', '--window-size=1440,900',
  ], { stdio: ['ignore', 'ignore', 'pipe'] })

  const wsUrl = await new Promise((res, rej) => {
    let buf = ''
    const timer = setTimeout(() => rej(new Error('等待 DevTools 端口超时')), 20000)
    proc.stderr.on('data', d => {
      buf += d
      const m = buf.match(/ws:\/\/\S+/)
      if (m) { clearTimeout(timer); res(m[0]) }
    })
    proc.on('exit', c => { clearTimeout(timer); rej(new Error(`Chrome 提前退出（code ${c}）`)) })
  })

  const port = new URL(wsUrl).port
  const target = await (await fetch(`http://127.0.0.1:${port}/json/new?about:blank`, { method: 'PUT' })).json()

  const ws = new WebSocket(target.webSocketDebuggerUrl)
  await new Promise((res, rej) => { ws.addEventListener('open', res); ws.addEventListener('error', rej) })

  let seq = 0
  const pending = new Map()
  const pageErrors = []
  const loaded = { count: 0 }

  ws.addEventListener('message', ev => {
    const msg = JSON.parse(ev.data)
    if (msg.id && pending.has(msg.id)) {
      const { res, rej } = pending.get(msg.id)
      pending.delete(msg.id)
      msg.error ? rej(new Error(msg.error.message)) : res(msg.result)
      return
    }
    if (msg.method === 'Page.loadEventFired') loaded.count++
    if (msg.method === 'Runtime.exceptionThrown') {
      pageErrors.push(msg.params.exceptionDetails.exception?.description || msg.params.exceptionDetails.text)
    } else if (msg.method === 'Runtime.consoleAPICalled' && msg.params.type === 'error') {
      pageErrors.push(msg.params.args.map(a => a.value ?? a.description ?? '').join(' '))
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

  const viewport = (width, height) =>
    send('Emulation.setDeviceMetricsOverride', { width, height, deviceScaleFactor: 1, mobile: false })

  const goto = async url => {
    const before = loaded.count
    await send('Page.navigate', { url })
    for (let i = 0; i < 100 && loaded.count === before; i++) await sleep(100)
    await sleep(300)
  }

  return { proc, profile, send, evaluate, viewport, goto, pageErrors }
}

/* ---------- 页面内的小工具（只注入一次） ---------- */
const HELPERS = `
  window.__overflow = () => document.documentElement.scrollWidth - document.documentElement.clientWidth;
  /* 竖条文本：被 flex 压成 min-content 的典型症状（一个字一行） */
  window.__stripText = () => [...document.querySelectorAll('.view.active h1, .view.active h2, .view.active p, .view.active .stat b, .view.active .sec-title')]
    .filter(el => {
      const r = el.getBoundingClientRect();
      if (r.width === 0 || r.height === 0) return false;
      const cs = getComputedStyle(el);
      const fs = parseFloat(cs.fontSize);
      const lh = parseFloat(cs.lineHeight) || fs * 1.6;
      return r.width < 3 * fs && r.height > 2 * lh;
    })
    .map(el => el.tagName + '.' + String(el.className).split(' ')[0] + ' (' + Math.round(el.getBoundingClientRect().width) + 'x' + Math.round(el.getBoundingClientRect().height) + ')');
  window.__errors = [];
  window.addEventListener('error', e => window.__errors.push(String(e.message)));
  window.__click = sel => { const el = document.querySelector(sel); if (!el) throw new Error('找不到 ' + sel); el.click(); return true; };
  window.__sleep = ms => new Promise(r => setTimeout(r, ms));
  /* 逐张探活：只靠 <img> 子资源加载判定，不走 fetch（file:// 下 fetch 会被同源策略拦） */
  window.__probeImgs = async list => {
    const bad = [];
    await Promise.all(list.map(src => new Promise(done => {
      const im = new Image();
      im.onload = done;
      im.onerror = () => { bad.push(src); done(); };
      im.src = src;
    })));
    return bad;
  };
  /* 某个容器里当前可见（未被 display:none 过滤掉）的卡片数 */
  window.__vis = sel => [...document.querySelectorAll(sel)].filter(c => c.style.display !== 'none').length;
`

const VIEWS = ['v-home', 'v-chars', 'v-lore', 'v-realms', 'v-beasts', 'v-herbs', 'v-treasures']

/* ---------- 主流程 ---------- */
const { proc, profile, send, evaluate, viewport, goto, pageErrors } = await launch()

try {
  await send('Page.enable')
  await send('Runtime.enable')

  /* ========== 1. 桌面结构 ========== */
  await viewport(1440, 900)
  await goto(TARGET)
  await evaluate(HELPERS)

  check('七个视图容器齐全',
    await evaluate(`document.querySelectorAll('.view').length`) === 7,
    `实际 ${await evaluate(`document.querySelectorAll('.view').length`)} 个`)

  const counts = await evaluate(`JSON.stringify([
    document.querySelectorAll('#characters .card').length,
    document.querySelectorAll('#beasts .card').length,
    document.querySelectorAll('#herbs .card').length,
    document.querySelectorAll('#treasureGrid .treasure-card').length])`)
  check('四库卡片数量正确（221/40/64/65）', counts === '[221,40,64,65]', `实际 ${counts}`)

  /* 图片完整性：DOM 实际引用的图必须都能在 assets 里找到、且都能解码。
     这是从页面迁出的 .asset-manifest（300 行 display:none）留下的真空 —— 那份清单既不加载
     也不校验、只能人工同步；这里改成真实断言：缺图与裂图一个都跑不掉。
     反过来「目录里有、页面没用」只做提示不判失败：那是备用的实名角色图（14 张），
     多半不在归档备份里，删掉会丢唯一副本，属于内容决策而非缺陷。 */
  const domImgs = JSON.parse(await evaluate(`JSON.stringify([...new Set([...document.querySelectorAll('img[src]')].map(i => i.getAttribute('src')))].sort())`))
  const refNames = domImgs.map(s => s.replace(/^assets\//, ''))
  const files = readdirSync(join(ROOT, 'public', 'assets')).filter(f => !f.startsWith('.'))
  const missing = refNames.filter(n => !files.includes(n))
  const spare = files.filter(f => !refNames.includes(f))
  check(`图片引用无缺图（页面引用 ${domImgs.length} 张，assets 目录 ${files.length} 张）`,
    missing.length === 0,
    `缺 ${JSON.stringify(missing.slice(0, 5))}`)
  if (spare.length) console.log(`  提示   目录里另有 ${spare.length} 张未被引用（备用素材，不计入失败）：${spare.slice(0, 6).join(' ')}${spare.length > 6 ? ' …' : ''}`)

  const broken = JSON.parse(await evaluate(`window.__probeImgs(${JSON.stringify(domImgs)}).then(a => JSON.stringify(a))`))
  check(`全部 ${domImgs.length} 张引用图都能解码加载`, broken.length === 0, `裂图 ${JSON.stringify(broken.slice(0, 5))}`)

  const refStat = await evaluate(`JSON.stringify({
    badges: document.querySelectorAll('.ref-count').length,
    inLinks: document.querySelectorAll('.ref-block').length,
    max: Math.max(...[...document.querySelectorAll('.card[data-key]')].map(c => parseInt((c.querySelector('.ref-count')||{textContent:'0'}).textContent.replace(/\\D/g,''))||0))
  })`)
  const refs = JSON.parse(refStat)
  check('互引已生成（≥ 100 张卡有被引徽记）', refs.badges >= 100, `实际 ${refs.badges} 张卡有被引徽记`)
  check('被引数最高者 > 100（韩立应是全网中心）', refs.max > 100, `最高被引 ${refs.max}`)

  const h1s = await evaluate(`JSON.stringify(${JSON.stringify(VIEWS)}.map(id => document.querySelectorAll('#' + id + ' h1').length))`)
  check('七个视图各有且仅有一个 h1', h1s === '[1,1,1,1,1,1,1]', h1s)

  /* 核心圈：默认只显示被引 ≥ 5 的条目（被引分布是长尾，208/381 条为 0） */
  const core = JSON.parse(await evaluate(`(() => {
    const visible = () => [...document.querySelectorAll('#characters .card')].filter(c => c.style.display !== 'none').length;
    const seg = n => [...document.querySelectorAll('.seg-btn')].find(b => b.dataset.core === n);
    const on = visible();
    seg('0').click();
    const all = visible();
    seg('1').click();
    return JSON.stringify({ on, all, backOn: visible(),
      labels: [...document.querySelectorAll('.seg-btn')].map(b => b.textContent.trim()) });
  })()`))
  check('核心圈默认生效（只显示被引 ≥ 5 的条目），可一键切回全部 221',
    core.on > 20 && core.on < 100 && core.all === 221 && core.backOn === core.on,
    JSON.stringify(core))

  /* ========== 2. 无横向溢出（桌面 + 移动） ========== */
  for (const [label, w, h] of [['桌面 1440×900', 1440, 900], ['移动 390×844', 390, 844]]) {
    await viewport(w, h)
    await sleep(200)
    const bad = []
    for (const v of VIEWS) {
      await evaluate(`location.hash = '#${v}'`)
      await sleep(180)
      const o = await evaluate(`window.__overflow()`)
      if (o > 0) bad.push(`${v} +${o}px`)
    }
    check(`${label} 七个视图均无横向溢出`, bad.length === 0, bad.join('，'))

    const strips = await evaluate(`JSON.stringify(window.__stripText())`)
    check(`${label} 无被压成竖条的文本`, strips === '[]', strips)
  }

  /* ========== 3. 交互 ========== */
  await viewport(1440, 900)
  await evaluate(`location.hash = '#v-chars'`)
  await sleep(250)

  const filter = JSON.parse(await evaluate(`(() => {
    /* 先退出核心圈降噪，否则数不到整篇的卡片 */
    [...document.querySelectorAll('.seg-btn')].find(b => b.dataset.core === '0').click();
    const tabs = [...document.querySelectorAll('#tabs .tab')];
    tabs.find(t => t.dataset.ch === 'huangfeng').click();
    return JSON.stringify({
      chapters: [...document.querySelectorAll('.chapter')].filter(s => getComputedStyle(s).display !== 'none').map(s => s.dataset.chapter),
      cards: [...document.querySelectorAll('#characters .card')].filter(c => c.style.display !== 'none').length });
  })()`))
  check('篇章筛选：只留该篇且卡片数一致',
    filter.chapters.length === 1 && filter.chapters[0] === 'huangfeng' && filter.cards === 29,
    `可见章节 ${JSON.stringify(filter.chapters)}，可见卡 ${filter.cards}（期望 29）`)
  await evaluate(`document.querySelector('#tabs .tab[data-ch="all"]').click()`)

  /* 灵兽 / 灵草：分类 tab 上的计数必须等于实际可见卡数（tab 文案与实际过滤任何一边错了都会被抳住） */
  const tabFilter = JSON.parse(await evaluate(`(() => {
    const out = {};
    for (const [name, tabs, cards] of [['beast', '#beastTabs .beast-tab', '#beasts .card'], ['herb', '#herbTabs .herb-tab', '#herbs .card']]) {
      const btn = [...document.querySelectorAll(tabs)];
      const rows = [];
      for (const b of btn) {
        b.click();
        rows.push([b.dataset.cat, Number((b.querySelector('.cnt') || {}).textContent), window.__vis(cards)]);
      }
      btn[0].click();
      out[name] = { rows, all: window.__vis(cards) };
    }
    return JSON.stringify(out);
  })()`))
  const tabBad = []
  for (const [name, lib] of Object.entries(tabFilter)) {
    for (const [cat, label, visible] of lib.rows) if (label !== visible) tabBad.push(`${name}/${cat} 标 ${label} 实 ${visible}`)
  }
  check('灵兽灵草分类筛选：tab 计数与实际可见卡数一致，全部时回到总数',
    tabBad.length === 0 && tabFilter.beast.all === 40 && tabFilter.herb.all === 64,
    tabBad.join('，') || JSON.stringify(tabFilter))

  /* 法宝：筛选是重渲染（不是 display 切换），所以比 展示计数 / 实际卡片 / 分类是否变窄 */
  const tresFilter = JSON.parse(await evaluate(`(() => {
    const tabs = [...document.querySelectorAll('#treasureTabs .tab')];
    const shown = () => Number(document.getElementById('treasureShown').textContent);
    const cards = () => document.querySelectorAll('#treasureGrid .treasure-card').length;
    const rows = [];
    for (const t of tabs) {
      t.click();
      rows.push([t.dataset.cat, shown(), cards()]);
    }
    tabs.find(t => t.dataset.cat === 'all').click();
    return JSON.stringify({ rows, all: [shown(), cards()] });
  })()`))
  const tresBad = tresFilter.rows.filter(([cat, shown, cards]) => shown !== cards || (cat === 'all' && shown !== 65)).map(r => r.join('/'))
  const narrowed = tresFilter.rows.some(([cat, shown]) => cat !== 'all' && shown < 65)
  check('法宝分类筛选：展示计数与卡片数一致，且分类确实收窄',
    tresBad.length === 0 && tresFilter.all[0] === 65 && tresFilter.all[1] === 65 && narrowed,
    `异常 ${tresBad.join('，')}；全部=${tresFilter.all.join('/')}；有收窄=${narrowed}`)

  /* 三库搜索：既要能按名称命中，也要能命中介于正文的字段（三库命中范围已统一），无结果时给空状态 */
  const searchProbe = JSON.parse(await evaluate(`(() => {
    const type = (id, kw) => { const el = document.getElementById(id); el.value = kw; el.dispatchEvent(new Event('input', { bubbles: true })); };
    const vis = sel => [...document.querySelectorAll(sel)].filter(c => c.style.display !== 'none');
    const shown = () => Number(document.getElementById('treasureShown').textContent);
    const out = {};
    /* 名称可能是「噬金虫（金童）」这类带形态后缀的变体，所以用包含匹配而非相等 */
    type('beastSearchInput', '噬金虫');    out.beastName = vis('#beasts .card').some(c => c.dataset.name.includes('噬金虫'));
    type('herbSearchInput', '筑基丹');     out.herbName = vis('#herbs .card').length;
    type('treasureSearchInput', '掌天瓶'); out.tresName = shown();
    /* 「韩立」只出现在 rel/camp/s 这类正文字段里，不在名称与称号上 —— 命中即证明搜索深度已统一 */
    type('beastSearchInput', '韩立');      out.beastText = vis('#beasts .card').length;
    type('herbSearchInput', '韩立');       out.herbText = vis('#herbs .card').length;
    type('treasureSearchInput', '韩立');   out.tresText = shown();
    type('beastSearchInput', '不存在的词zzz'); out.beastNone = vis('#beasts .card').length;
    out.emptyShown = getComputedStyle(document.getElementById('beastEmpty')).display !== 'none';
    ['beastSearchInput','herbSearchInput','treasureSearchInput'].forEach(id => type(id, ''));
    return JSON.stringify(out);
  })()`))
  check('三库搜索：都能按名称定位',
    searchProbe.beastName && searchProbe.herbName >= 1 && searchProbe.tresName >= 1,
    JSON.stringify(searchProbe))
  check('三库搜索：命中范围一致（正文也参与），无结果时给空状态',
    searchProbe.beastText > 0 && searchProbe.herbText > 0 && searchProbe.tresText > 0
      && searchProbe.beastNone === 0 && searchProbe.emptyShown,
    JSON.stringify(searchProbe))

  const locate = JSON.parse(await evaluate(`(async () => {
    window.dispatchEvent(new KeyboardEvent('keydown', { key: 'k', metaKey: true, bubbles: true }));
    const inp = document.getElementById('spotInput');
    inp.value = '虚天鼎';
    inp.dispatchEvent(new Event('input', { bubbles: true }));
    inp.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true }));
    await window.__sleep(1600);
    const open = document.querySelector('.view.active .card.open, .view.active .treasure-card.open');
    return JSON.stringify({
      view: document.querySelector('.view.active').id,
      key: open?.dataset.key ?? null,
      top: open ? Math.round(open.getBoundingClientRect().top) : null,
      paletteClosed: document.getElementById('spot').hidden });
  })()`))
  check('搜索定位：切到法宝库、展开目标卡并滚到顶栏之下',
    locate.key === 'tres-12' && locate.paletteClosed && locate.top !== null && locate.top > 30 && locate.top < 160,
    JSON.stringify(locate))

  const jump = JSON.parse(await evaluate(`(async () => {
    location.hash = '#v-chars';
    await window.__sleep(300);
    const card = [...document.querySelectorAll('#characters .card')].find(c => c.dataset.name === '韩立');
    card.classList.add('open');
    const chip = card.querySelector('.ref-chip');
    const target = chip.dataset.goto;
    chip.click();
    await window.__sleep(1500);
    const open = document.querySelector('.view.active .card.open, .view.active .treasure-card.open');
    return JSON.stringify({ from: card.dataset.key, target,
      view: document.querySelector('.view.active').id,
      opened: open?.dataset.key ?? null,
      /* chip 用捕获阶段拦下并阻断冒泡，否则会连带把原卡收起 */
      sourceStillOpen: document.querySelector('[data-key="' + card.dataset.key + '"]').classList.contains('open') });
  })()`))
  check('卡片互引 chip 可跳转（且不会把原卡收起）',
    jump.target === jump.opened && jump.sourceStillOpen,
    JSON.stringify(jump))

  const backTop = JSON.parse(await evaluate(`(async () => {
    location.hash = '#v-chars';
    await window.__sleep(300);
    const btn = document.getElementById('backTop');
    const bar = document.getElementById('backTopBar');
    const C = 2 * Math.PI * 21;
    const off = () => +bar.style.strokeDashoffset;
    window.scrollTo({ top: 0, behavior: 'auto' });
    await window.__sleep(300);
    const atTop = { shown: btn.classList.contains('show'), off: off() };
    window.scrollTo({ top: 3000, behavior: 'auto' });
    await window.__sleep(300);
    const mid = { shown: btn.classList.contains('show'), off: off() };
    window.scrollTo({ top: document.documentElement.scrollHeight, behavior: 'auto' });
    await window.__sleep(400);
    const bottom = { off: off() };
    btn.click();
    await window.__sleep(2000);
    return JSON.stringify({ C, atTop, mid, bottom, y: Math.round(window.scrollY) });
  })()`))
  check('返回顶部：滚动后出现、点击后归零（进度环随滚动补满、到底接近满圈）',
    backTop.atTop.shown === false && backTop.atTop.off > backTop.C - 1
      && backTop.mid.shown && backTop.mid.off < backTop.atTop.off - 1
      && backTop.bottom.off < backTop.C * 0.02 && backTop.y === 0,
    JSON.stringify(backTop))

  /* 深链：以 #v-treasures/tres-2 冷启动（先 about:blank 保证是一次完整加载） */
  await goto('about:blank')
  await goto(`${TARGET}#v-treasures/tres-2`)
  await sleep(1400)
  const deep = JSON.parse(await evaluate(`(() => {
    const open = document.querySelector('.view.active .treasure-card.open');
    return JSON.stringify({
      view: document.querySelector('.view.active').id,
      hash: location.hash,
      key: open ? open.dataset.key : null,
      top: open ? Math.round(open.getBoundingClientRect().top) : null });
  })()`))
  check('深链冷启动：#v-treasures/tres-2 直接打开对应卡片',
    deep.view === 'v-treasures' && deep.key === 'tres-2' && deep.hash === '#v-treasures/tres-2'
      && deep.top !== null && deep.top > 30 && deep.top < 160,
    JSON.stringify(deep))

  /* 点开卡片要把 URL 同步成深链，便于复制分享 */
  await evaluate(HELPERS)
  const share = JSON.parse(await evaluate(`(async () => {
    location.hash = '#v-chars';
    await window.__sleep(250);
    const card = [...document.querySelectorAll('#characters .card')].find(c => c.dataset.name === '南宫婉');
    card.click();
    const opened = location.hash;
    card.click();
    return JSON.stringify({ opened, closed: location.hash, key: card.dataset.key });
  })()`))
  check('点击卡片同步 URL（可复制分享），收起后去掉目标',
    share.opened === '#v-chars/' + share.key && share.closed === '#v-chars',
    JSON.stringify(share))

  /* 浏览器返回：popstate / hashchange 都要接住。
     不断言"退到哪一条历史"（file:// headless 下 pushState 不新增条目，条数是浏览器语义），
     改断言路由不变量：不管落到哪一条，激活视图都必须与地址栏 hash 一致 */
  await evaluate(`location.hash = '#v-treasures'`)
  await sleep(200)
  const backNav = JSON.parse(await evaluate(`(async () => {
    const act = () => document.querySelector('.view.active').id;
    const want = () => (location.hash.replace(/^#/, '').split('/')[0] || 'v-home');
    /* 挑一张指向别库的 chip，这样"确实跳走了"是可判定的 */
    const chip = [...document.querySelectorAll('.view.active [data-goto]')]
      .find(c => !c.dataset.goto.startsWith('tres-'));
    if(!chip) return JSON.stringify({ skipped: true });
    const before = act();
    chip.click();
    await window.__sleep(300);
    const jumped = act();
    history.back();
    await window.__sleep(500);
    return JSON.stringify({ before, jumped, hash: location.hash, got: act(), want: want() });
  })()`))
  check('互引 chip 跳转后按浏览器返回，激活视图仍与地址栏一致',
    !backNav.skipped && backNav.jumped !== backNav.before && backNav.got === backNav.want,
    JSON.stringify(backNav))

  /* 只看真正会发起请求的标签：canonical / alternate 这类 href 不是资源请求 */
  const thirdParty = await evaluate(`JSON.stringify(
    [...document.querySelectorAll('link[rel="stylesheet"][href], link[rel="preload"][href], link[rel="icon"][href], script[src], img[src]')]
      .map(el => el.getAttribute('href') || el.getAttribute('src'))
      .filter(u => /^https?:/i.test(u)))`)
  check('页面无第三方资源请求', thirdParty === '[]', thirdParty)

  /* ========== 4. 控制台 ========== */
  check('控制台与页面均无报错', pageErrors.length === 0, pageErrors.slice(0, 3).join(' | '))

  /* ---------- 汇总 ---------- */
  const failed = results.filter(r => !r.ok)
  console.log(`\n${results.length - failed.length}/${results.length} 通过  ·  ${TARGET}`)
  process.exitCode = failed.length ? 1 : 0
} finally {
  proc.kill('SIGKILL')
  try { rmSync(profile, { recursive: true, force: true }) } catch {}
}
