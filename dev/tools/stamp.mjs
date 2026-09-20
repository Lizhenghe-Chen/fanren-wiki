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
 * ⚠️ 改文本一律用 indexOf + slice 拼接，**不要用 `String.replace(re, fn)`**：
 * 2026-09-20 实测（本机 Node v24.18.0，replace 是原生实现、NODE_OPTIONS 为空），
 * `'AA首次发布：2026-09-14 · 最后更新：2026-09-19BB'.replace(re, x => x[1] + '…')`
 * 会得到 `AA次2026-09-20BB` —— 回调里的捕获组被截成 1 个字符，足以把整页写坏（v38 首次上线就这么坏的）。
 * 换成切片后同一段文本本地与 CI 结果一致。
 *
 * 每条锚点在目标文件里必须命中「恰好 1 次」，否则整体报错退出、不写任何文件 ——
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
const DATE_RE = /^\d{4}-\d{2}-\d{2}/

const die = msg => {
  console.error(`stamp: ${msg}`)
  process.exit(1)
}
const git = format =>
  execFileSync('git', ['-c', 'safe.directory=*', 'log', '-1', `--format=${format}`], {
    cwd: ROOT,
    encoding: 'utf8',
  }).trim()

const date = git('%cs')
if (!DATE_RE.test(date)) die(`git 给出的提交日期不是 YYYY-MM-DD：${JSON.stringify(date)}`)
const sha = git('%h')

/* 提交说明是任意文本：先压平折行、再转义 HTML，最后截断（截断放最后，免得多算了实体字符） */
const note = (() => {
  const flat = git('%s').replace(/\s+/g, ' ').trim()
  if (!flat) die('git 给出的提交说明为空')
  const esc = flat.split('&').join('&amp;').split('<').join('&lt;').split('>').join('&gt;')
  const chars = [...esc]
  return chars.length > NOTE_MAX ? chars.slice(0, NOTE_MAX).join('') + '…' : esc
})()

/* 每条规则：anchor（锚点，须全库唯一）+ value（写在其后的值）；
   不写 until 的，锚点后面紧跟的就是 YYYY-MM-DD；写了 until 的，替换到 until 之前。 */
const RULES = [
  { what: '首页 · 头注释 最后更新', anchor: '· 最后更新：', value: date },
  { what: '首页 · JSON-LD dateModified', anchor: '"dateModified": "', value: date },
  { what: '首页 · 导航栏 更新', anchor: '</span>更新 ', value: date },
  { what: '首页 · 页脚 最后更新', anchor: '">最后更新：', value: date },
  { what: '首页 · 页脚 提交说明', anchor: '<span class="stamp-note">', until: '</span>', value: note },
  { what: '站点地图 · lastmod', anchor: '<lastmod>', until: '</lastmod>', value: date },
]

/* 锚点定位 + 切片拼接。返回 null 表示锚点缺失或后面不是预期内容。 */
const applyRule = (text, { anchor, until, value }) => {
  const at = text.indexOf(anchor)
  if (at < 0) return null
  const from = at + anchor.length
  if (until) {
    const to = text.indexOf(until, from)
    return to < 0 ? null : text.slice(0, from) + value + text.slice(to)
  }
  const m = DATE_RE.exec(text.slice(from))
  return m ? text.slice(0, from) + value + text.slice(from + m[0].length) : null
}

const before = new Map(FILES.map(f => [f, readFileSync(join(ROOT, f), 'utf8')]))
const after = new Map(before)
const broken = []

for (const rule of RULES) {
  const where = FILES.filter(f => (after.get(f).split(rule.anchor).length - 1) === 1)
  console.log(`  ${where.length === 1 ? 'ok  ' : 'FAIL'} ${rule.what}　命中 ${where.length} 次`)
  if (where.length !== 1) {
    broken.push(`${rule.what} 命中 ${where.length} 次（应为 1）`)
    continue
  }
  const file = where[0]
  const out = applyRule(after.get(file), rule)
  if (out === null) broken.push(`${rule.what}：锚点后不是预期的日期/结尾`)
  else after.set(file, out)
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
