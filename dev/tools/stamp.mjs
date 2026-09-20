#!/usr/bin/env node
/**
 * 把「最后更新」写进 public/index.html 与 public/sitemap.xml —— 部署时自动刷新，日期不再手写。
 *
 *   node dev/tools/stamp.mjs           # 体检：打印取值与每条锚点的命中数，不改文件
 *   node dev/tools/stamp.mjs --write   # 写入（GitHub Actions 在打包产物前跑这一条）
 *
 * 取值来源：本仓库 git HEAD —— `%cs`（提交日期）+ `%s`（提交说明首行）。
 *
 * 为什么在部署时注入、而不是页面运行时拉 GitHub API：
 * ① `api.github.com` 在国内经常超时，本站读者大多在国内；
 * ② 未认证接口 60 次/小时/IP，扛不住每次访问；
 * ③ 注入的是静态文本 ⇒ 关掉 JS、爬虫抓页面、另存到本地，日期与 JSON-LD / 站点地图都是对的。
 *
 * ⚠️ `--write` 只在 CI 跑，**不要在本地对工作区跑**（2026-09-20 实测）：
 * VS Code 编辑器缓冲区会把它自己那份内容回写，把脚本写入的结果覆盖成"吞字"的坏文本
 * （`<span …>` 变成 `s`、`最后更新：` 整段消失），只能 `git checkout` 恢复。
 * 部署在 runner 上跑没有编辑器，安全；本地要改日期就用编辑工具手改这几处（保持同值）。
 *
 * 每条锚点在目标文件集合里必须命中「恰好 1 次」，否则整体报错退出、不写任何文件 ——
 * 页面改版把锚点改没了，就同步改下面的 RULES，让部署失败（可见），
 * 而不是静默失效、日期又退回手写并互相漂移（v38 之前手写就漂移过：导航 09-17 / 页脚 09-19）。
 */
import { execFileSync } from 'node:child_process'
import { readFileSync, writeFileSync } from 'node:fs'
import { join, resolve } from 'node:path'

const ROOT = resolve(import.meta.dirname, '..', '..')
const FILES = ['public/index.html', 'public/sitemap.xml']
const WRITE = process.argv.includes('--write')
const NOTE_MAX = 56 // 提交说明首行超过这么多字符就截断（按码点，中文一个字算一个）

const die = msg => {
  console.error(`stamp: ${msg}`)
  process.exit(1)
}
const git = format =>
  execFileSync('git', ['-c', 'safe.directory=*', 'log', '-1', `--format=${format}`], {
    cwd: ROOT,
    encoding: 'utf8',
  }).trim()
const hitsOf = (text, re) => (text.match(new RegExp(re.source, 'g')) || []).length

const date = git('%cs')
const sha = git('%h')
if (!/^\d{4}-\d{2}-\d{2}$/.test(date)) die(`git 给出的提交日期不是 YYYY-MM-DD：${JSON.stringify(date)}`)

/* 提交说明是任意文本：先压平折行、再转义 HTML，最后截断（截断放最后，免得多算了实体字符） */
const note = (() => {
  const flat = git('%s').replace(/\s+/g, ' ').trim()
  if (!flat) die('git 给出的提交说明为空')
  const esc = flat.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
  const chars = [...esc]
  return chars.length > NOTE_MAX ? chars.slice(0, NOTE_MAX).join('') + '…' : esc
})()

/* 首页 4 处日期 + 页脚提交说明 + 站点地图 lastmod，全部同源。正则只捕获锚点，替换时拼上新值。 */
const RULES = [
  {
    what: '首页 · 头注释 最后更新',
    re: /(首次发布：\d{4}-\d{2}-\d{2} · 最后更新：)\d{4}-\d{2}-\d{2}/,
    to: m => m[1] + date,
  },
  { what: '首页 · JSON-LD dateModified', re: /("dateModified": ")\d{4}-\d{2}-\d{2}/, to: m => m[1] + date },
  { what: '首页 · 导航栏 更新', re: /(· 更新 )\d{4}-\d{2}-\d{2}/, to: m => m[1] + date },
  {
    what: '首页 · 页脚 最后更新',
    re: /(<span style="color:var\(--gold\)">最后更新：)\d{4}-\d{2}-\d{2}/,
    to: m => m[1] + date,
  },
  { what: '首页 · 页脚 提交说明', re: /(<span class="stamp-note">)[^<]*(<\/span>)/, to: m => m[1] + note + m[2] },
  { what: '站点地图 · lastmod', re: /(<lastmod>)\d{4}-\d{2}-\d{2}(<\/lastmod>)/, to: m => m[1] + date + m[2] },
]

const before = new Map(FILES.map(f => [f, readFileSync(join(ROOT, f), 'utf8')]))
const after = new Map(before)
const broken = []

for (const { what, re, to } of RULES) {
  const hits = FILES.reduce((n, f) => n + hitsOf(after.get(f), re), 0)
  console.log(`  ${hits === 1 ? 'ok  ' : 'FAIL'} ${what}　命中 ${hits} 次`)
  if (hits !== 1) {
    broken.push(`${what} 命中 ${hits} 次（应为 1）`)
    continue
  }
  const file = FILES.find(f => hitsOf(after.get(f), re) === 1)
  after.set(file, after.get(file).replace(re, to))
}
if (broken.length) die(`锚点对不上，未写入任何内容：\n  - ${broken.join('\n  - ')}`)

console.log(`\n取值：${date} · ${note}\n      （HEAD ${sha}）`)
for (const f of FILES) {
  if (after.get(f) === before.get(f)) console.log(`${f}：已是该值，无需写入。`)
  else if (!WRITE) console.log(`${f}：体检模式，未写入（加 --write 生效）。`)
  else {
    writeFileSync(join(ROOT, f), after.get(f))
    console.log(`${f}：已刷新。`)
  }
}
