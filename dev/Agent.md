# 《凡人修仙传》百科 · 全篇资料图谱 — 开发文档

> 本文档供后续 LLM（或开发者）快速理解本项目并上手开发。先读本节即可动手，细节按需跳读。

## 1. 项目是什么

一个**纯静态、本地化运行**的《凡人修仙传》全篇资料可视化站点（单页应用 + 若干本地脚本，全部在仓库内），用户用于回忆剧情、检索人物、理解境界体系、查灵兽/丹药/法宝；运行时仅首页浏览统计的 JSONP 可能发出外部请求。

### 1.1 四条硬约束（红线，2026-10-13 由「自包含单页」改写）

判断一段改动能不能做，看这四条：

1. **默认零第三方请求**：不发 CDN、不发外部接口。唯一例外是运行时访客统计的 JSONP（见 §7），且必须**可失败、失败即静默**。
2. **发布物只有 `public/`**：GitHub Actions 只上传这一层，`dev/` 永不上站。
3. **`file://` 双击打开就能用**：不允许「必须起服务器」的功能（不用 ES module、不用 `fetch` 读本地文件）。
4. **无构建步骤**：改完直接能跑，不引入打包/编译/依赖安装（`echarts.min.js` 的按需打包是「改库」不是「改站」，见 §7）。

历史口径「自包含单页 / CSS JS 全内联」**已作废**：内联与拆分是**实现细节，不是目的**。拆分的收益是**按文件缓存**（回访只重新取改动的那份）、**可单独 diff/回滚**、**HTML 与脚本各自增量更新**——**不是**体积：拆完 gzip 总量与拆前基本持平（647KB+176KB，gzip 273KB vs 拆前 272KB）。只要不破坏上面四条就允许。已落地：`public/javascripts/map.js`（修仙界全图引擎，176KB，v59 从 `index.html` 拆出）。页面仍是**一个 HTML 十一个视图**的单页应用（路由用 hash，见 §3）。

- **默认首页（v-home）**：百科式介绍页——网站命名《凡人修仙传》百科，含"为什么做这个网站"（`<details class="home-why">` 折叠，摘要一句话 + "展开全文"，默认收起以缩首屏）、六大收录板块入口卡片、"问道自述"、"收录说明"、"数据来源"。用户明确要求"首页不要开门见山放人物图鉴"。（2026-09-17 已删掉"页面包含"功能清单区块——功能靠界面自身说明，不再用一段清单复述。）
- **降噪可选**：人物图谱**默认显示全部 263 条**（2026-09-22 起，见 v39；此前默认只显示被引 ≥ 5 的核心圈）；`#tabs` 内的分段选择器可一键切「核心圈 87 / 全部 263」。互引网络与定位能力见 §5。
- 收录 **6 个篇章、263 条人物记录**（跨篇章重复出现的角色按"出现即写"重复收录，如韩立 6 篇、南宫婉 4 篇）+ **灵兽灵虫 42 条** + **灵草丹药 65 条** + **法器法宝 71 条** + **功法 53 条 / 阵法 44 条 / 符箓 34 条**（共 **十一个视图**、七库合计 **572 条**；修仙界全图另含 156 处地点，与全库索引 `INDEX` 条目数一致）。
- 每人默认卡片显示：**头像图、名字、身份、本篇修为、关系/势力/种族标签**；点击展开显示**生平梗概与结局**（默认不剧透）。**修为演进 ev 字段已全量补齐（263/263）**，卡片修为行显示本篇内的境界变化（如"炼气→筑基→结丹后期"）。
- 页面支持 **人物图片**（优先动画形象，同一角色可挂多形象轮播）、**境界图表**（外部 cultivation-chart.js）、**妖兽等级制度**与**灵药年份等级**对照区块。
- **剧情速览分两栏（页内 tab）**：`境界时间线`（默认）与 `情节梳理 · 全书十一卷`（11 卷 / 55 地点篇 / 388 步，首次点开才渲染）。后者内容整理自第三方公众号文章并已署名，见 §9 与 `NOTICE`。

## 2. 目录结构

```
fanren-wiki/                # 独立仓库（2026-09-17 从主站拆出，git 历史保留）
├── public/                 # ← 唯一发布目录，GitHub Actions 只上传这里
│   ├── index.html          # 页面本体：十一视图标记 + 内联 CSS + 内联数据/主逻辑（≈646KB）
│   ├── cultivation.css     # 图表样式（境界阶梯【用户自加部分原样不改】+ 末尾追加的概览图表，见 §7）
│   ├── javascripts/
│   │   ├── map.js                 # 修仙界全图引擎（Canvas，IIFE + 懒启动，171KB；v59 从 index.html 拆出，见 §1.1）
│   │   ├── cultivation-chart.js   # 境界阶梯图（本站自持，不再依赖主站）
│   │   ├── echarts.min.js         # ECharts 5.6.0 **按需构建包**（527KB，零 CDN，可重建；页面改成「容器进视口才注入」，见 §7）
│   │   └── overview-charts.js     # 人物关系图谱（力导向）+ 篇章×势力旭日图
│   ├── assets/             # 500 张图：482 张被页面引用（.webp/.jpg 混合，逐图最优）+ 18 张备用图，见 §6
│   ├── sitemap.xml
│   └── robots.txt
└── dev/                    # 开发资料：永不上站；只跟踪文档与工具（见下方说明）
    ├── Agent.md            # 本文档
    ├── _review.md          # 数据审校笔记
    ├── tools/              # 在用的工具：image-slim.py（图片瘦身，见 §6）、verify.mjs（零依赖验收，见 §8.3）、pixel-diff.mjs（改观感类改动的像素比对，见 §8.3）、echarts-entry.js（ECharts 按需构建入口，见 §7）、readme-shots.py（README 宣传图：整页截图 → 16:10 缩略图，输出 image/README/shots/，原图被 .gitignore 忽略；⚠️ 只认「整页长图」来源，2026-10-12 起另有逐视图顶屏截图法，见 §11）、stamp.mjs（部署时把「最后更新」+ 提交说明注入 index.html、把 lastmod 注入 sitemap.xml，见 §7「元数据」）
    ├── _image-slim-report.json  # 瘦身逐图决策记录（体积/SSIM/所选质量档）
    ├── _backup/            # 历史堆积：index-vNN.html 版本次级（21 个）+ 一次性的 migrate 脚本（apply_*/add_*/fix_*/sync_*）+ meta/stories/ev/herbs_data/treasures_data 等中间数据
    └── watermark.svg       # 仅供 _backup/index-v*.html 引用的水印瓦片（当前页面已内联 base64）
```

- `_backup/` 里的脚本不参与运行、也不要“顺手执行”：它们是当时的字符串级插入脚本，路径写死在旧仓库（`Lizhenghe-Chen.github.io/...`）。要重跑得先把路径改回来。
- ⚠️ `dev/unused-assets/` **已不存在**：那批备用图已全部清理到归档目录（见 §6 原图备份）。目前未被引用的 14 张实名图留在 `public/assets/` 里，由验收脚本作为提示列出（见 §6）。

- 工作目录：`~/Documents/GitProjects/fanren-wiki/`（原地址 `Lizhenghe-Chen.github.io/docs/docs/Other/fanren-characters/` 已停用，主站只留跳转桩）；早期旧版在 `~/Doubao/chats/2026-09-14/new-chat/fanren-characters/`（仅参照）。
- 线上地址：`https://bunnychen.top/fanren-wiki/`（项目页，继承用户站自定义域名，本仓库无需 CNAME）。
- 参考资料页仍在主站：`https://bunnychen.top/docs/Other/fanren-xiuxian/`（**仅作首页介绍文案的素材来源**）。
- **反馈 / 勘误走 B 站视频评论区**（2026-10-21 起）：`https://www.bilibili.com/video/BV1Ameq6vECK/`（《我做了一本《凡人修仙传》百科全书：221 位人物全收录》）—— 读者不必注册 GitHub，留个评论就行；页面上四处入口（hero「勘误与反馈」/ 收录说明 `.home-note` / 图片准确性声明 `.img-note` / 页脚）全指这一条。**GitHub Issues 只留给源码与技术问题**（页脚并列一句），不再当作内容勘误入口。⚠️ **主站评论区仍不是入口**，不要把链接指回 `bunnychen.top/docs/.../#__comments`。
- **开发资料一律放进 `dev/`**：发布边界由目录决定（只上传 `public/`），不要把 `_backup/`、自检截图、笔记放进 `public/`。
- ⚠️ **`dev/` 的跟踪策略（2026-09-18 调整）**：**只跟踪「活文档 + 工具」**（`Agent.md`、`_review.md`、`Bili-Feedback.md`、`tools/`、`_image-slim-report.json`），`_backup/`、`demos/`、`watermark.svg` 仍在 `.gitignore` 里（仅本地保留）。理由是前者没有版本历史就只能靠本机磁盘活着、且与 `public/` 的改动一一对应；后者要么 git 历史里本来就有一份（`_backup/index-vNN.html` 就是各次提交的副本），要么是一次性产物。
  - 📄 `Bili-Feedback.md` 是**视频评论区专用手册**（抓全评论 / 核查口径 / 用 API 回帖的三个坑）。它是写给作者本人和后续 agent 的**内部操作记录，不对外引用**（README、页面、对外文案里都不要提）。
  ⚠️ **`dev/` 仍然不会上站**（CI 只传 `public/`）：公开可见 ≠ 交付物，README 里不要把 `dev/` 当交付物引用。

## 3. 页面结构：十一视图 + hash 路由

页面**不是单页长滚**，而是**页内多视图切换**（用户明确要求"分页面"，否决过"左右分栏"）：

```
<body>
  <nav class="topnav">                        # 顶部主导航（sticky top:0，48px 内容高+1px 边框=49px）：首页 | 人物图谱 | 剧情速览 | 修仙界全图 | 境界体系 | 灵兽灵虫 | 灵草丹药 | 法器法宝 | 功法 | 阵法 | 符箓（**十一入口**）+ 搜索按钮 + **GitHub 图标（≥1100px 才显示，见下）** + 持续更新·作者主页·日期
  <div class="view" id="v-home">              # 视图0 首页（默认）
    hero（标题/统计/按钮） → 为什么做这个网站（<details class="home-why">，默认收起） → **篇章×势力旭日图 #chart-sunburst**（ECharts sunburst，首页"收录内容"之前） → 收录内容 6 卡 → 问道自述（.home-quest） → 收录说明 → 数据来源（.src-list） → **开源（.repo-card）**
  </div>
  <div class="view" id="v-chars">             # 视图1 人物图谱
    .page-head（紧凑页头，含唯一的 h1 + 统计） → sticky .navbar（top:49px：.tabs 篇章 tab + .seg 核心圈切换 + 搜索框） → .img-note 图片准确性声明（<details>，默认收起） → **人物关系图谱 <details class="graph-fold">**（ECharts 力导向 #chart-graph，默认展开，可折叠） → 卡片区 <main id="characters">
  </div>
  <div class="view" id="v-lore">              # 视图2 剧情速览（页内两支，由 .lore-tabs 切换）
    .page-head（h1 + 统计 #lore-nodes） → .lore-tabs（境界时间线 / 情节梳理 · 全书十一卷）
      ├ #lorePaneTimeline（默认显示）：韩立境界演进时间轴 #timeline → 故事脉络 6 卡 → 双韩立因果闭环
      └ #lorePanePlot（hidden，首次点开才渲染）：#plotList ← renderPlot()，11 卷 → 地点篇 → 步骤
  </div>
  <div class="view" id="v-map">               # 视图3 修仙界全图：Canvas 三界舆图、地点索引与十段巡游
  </div>
  <div class="view" id="v-realms">            # 视图4 境界体系（约 1 屏）
    .page-head → 境界 rail → 3 个 data-cultivation 图表 → 各篇人数柱状 → 图例
  </div>
  <div class="view" id="v-beasts">            # 视图5 灵兽灵虫（约 3 屏）
    .page-head（含 .ph-lead 一句话引导） → 妖兽等级制度 rail #beastRail → 分类 tab #beastTabs → 共用搜索框 .lib-search（#beastSearchInput） → 卡片区 <div class="grid beast-grid" id="beasts">
  </div>
  <div class="view" id="v-herbs">             # 视图6 灵草丹药（约 2-3 屏）
    .page-head → 灵药年份等级 rail #herbRail → 分类 tab #herbTabs → 共用搜索框 .lib-search（#herbSearchInput） → 卡片区 <div class="grid herb-grid" id="herbs">
  </div>
  <div class="view" id="v-treasures">         # 视图7 法器法宝（约 2-3 屏）
    .page-head → 法宝品阶 rail #treasureRail → 分类 tab #treasureTabs → 共用搜索框 .lib-search（#treasureSearchInput） → 展示计数 #treasureShown → 卡片区 #treasureGrid
  </div>
  <div class="view" id="v-gongfa">            # 视图8 功法（结构同 v-beasts，**单分类故不渲染分类 tab**）
    .page-head（含 #gongfa-total / #gongfa-anim） → rail #gongfaRail → 搜索框 #gongfaSearchInput → 卡片区 #gongfaGrid
  </div>
  <div class="view" id="v-zhenfa">            # 视图9 阵法（同上：#zhenfaRail / #zhenfaGrid / #zhenfa-total / #zhenfa-anim）
  </div>
  <div class="view" id="v-fu">                # 视图10 符箓（同上：#fuRail / #fuGrid / #fu-total / #fu-anim）
  </div>
  <footer>…</footer>
  <button class="back-top" id="backTop">↑ + 进度环</button>   # 滚过 700px 后出现（.show）；环按滚动比例补满
  <div class="spot" id="spot" hidden>…</div>        # 全站搜索面板（见 §5）
  <script>…</script>
```

- **切换机制**：`.topnav a[data-view]` + `switchView(id)`（IIFE 内）。`.view{display:none}`，`.view.active{display:block}`。
- **hash 路由（一个真相源 = 地址栏）**：
  - `#v-chars` —— 切视图；`#v-treasures/tres-12` —— 切视图并展开那条卡（深链）。
  - `parseHash()` 把 `v-treasures/tres-12` 拆成 `{view, target}`；`setHash(view, target, replace)` 写地址（`replaceState`/`pushState`，**`file://` 下个别浏览器会抛 SecurityError，已 try/catch**）；`applyHash()` = `switchView(p.view)` + 有 target 则 `gotoEntry`。
  - **`hashchange` 与 `popstate` 都要监听**：`setHash` 走的是 History API —— `replaceState` 不触发任何事件，`pushState` 只触发 `popstate`，而手改地址栏/退后到带 hash 的历史条目触发的是 `hashchange`。少一个就会"地址变了、视图不动"（已踩过：旧实现 `openFromHash()` 只处理 target，从不切视图）。
  - **`data-key` 里不能用 `#`**：分隔符是 `-`（`qixuanmen-0` / `beast-0` / `herb-0` / `tres-12`），`#` 在 URL 里是 fragment 分隔符，根本传不过去。
- **默认视图**：无 hash 或非法时回退 **`v-home`**（不是 v-chars）。
- **新增视图**：加一个 `<div class="view" id="v-xxx">`（内部只放一个 `h1`），在 `VIEWS` 数组里登记（脚本与外链都读它），topnav 加链接即可。
- **展开态与地址栏的一致性（2026-10-05 加）**：筛选/切降噪都是**整表重排**（卡片会被卸载重建），所以 ① `openKeyFromHash()` 在挂载时按地址栏 target 还原 `.open`；② `syncTargetToResults(libId, keys)` 在重排后若 target 已不在结果集里就撤掉 target（**只撤 target，视图不动**）。两者都只处理「target 属于本库」的情况 —— 启动时各库都会先重排一次，那会儿 hash 可能指向**别的**库（深链冷启动）。
- **移动端**：`@media (max-width:640px)` 下 **topnav 换行显示**（`.topnav .wrap{height:auto;flex-wrap:wrap}` + `.tn-links{flex:1 1 0;flex-wrap:wrap}`，十一个入口分两行全部落在视口内；状态位 `.tn-update` 隐藏，日期与作者主页下沉到页脚），`.topnav a` 同时降字号内边距；`@media (max-width:400px)` 再降一档。因为顶栏变高：`.chapter` 不再 sticky、`.view{scroll-margin-top:88px}`。`.navbar{top:45px}`、`.tabs` 仍是单行横向滚动。
- **⚠ 锚点注释会撞车**：`/* ===== 韩立境界时间轴 ===== */` 在 `<style>`（`.timeline-sec` 注释）与 `<script>`（`const TL` 前）各出现一次——脚本插入若用该注释定位 JS 数据，会误命中 CSS 区导致 `BEASTS is not defined`。定位 JS 数据应匹配 `];\n\n/* ===== 韩立境界时间轴 ===== */\nconst TL = [` 整段。历史修复：`_backup/fix_beast_data_pos.py`。

## 4. 数据模型（`const DATA`）

`DATA` 是 6 键对象，键 = 篇章 id，值 = 人物数组：

| 键 | 篇章 | 条数 |
|---|---|---|
| `qixuanmen` | 七玄门 | 17 |
| `huangfeng` | 黄枫谷 | 35 |
| `luanxing` | 乱星海 | 37 |
| `dajin` | 大晋 | 74 |
| `lingjie` | 灵界 | 41 |
| `xianjie` | 仙界 | 59 |
| （合计） | 全书 | **263** |

每人字段（部分可选）：

| 字段 | 含义 | 备注 |
|---|---|---|
| `n` | 名字 | 必填 |
| `t` | 身份/称号 | 如"韩立·全书主角" |
| `r` | 本篇修为/境界过程 | 如"结丹 → 元婴"（显示在卡片上） |
| `e` | 本篇人物结局 | 展开区显示 |
| `img` | 图片文件名 | 可选，无图用姓氏首字占位 |
| `s` | 生平梗概（剧透） | 展开区显示，默认卡片不展示 |
| `rel` | 与韩立的关系 | 如"仇敌/挚友/道侣" |
| `camp` | 势力阵营 | 如"七玄门/黄枫谷" |
| `race` | 种族 | 如"人族/妖族/傀儡" |
| `ev` | 本篇修为演进 | **已全量补齐 263/263**（v16 首次补齐；v47 新增的 12 条同步补齐），如"炼气→筑基→结丹后期（天灵根）"；凡人角色写"凡人"或"凡人（无灵根）" |

**新增/修改人物**：直接在 `DATA` 对应数组追加/编辑对象即可；跨篇角色在每篇各自收录（可各自配不同图片，如韩立每篇不同形象）。
**批量补 ev 参考**：`/tmp/add_ev.py`（173 条映射表 + 字符串级精确插入逻辑，含"数花括号深度找记录闭合"的方法，可复用）。

### 条目标识（`data-key`）与七库统一

- 七库记录在渲染时都带 **`data-key`**，是深链与互引网络的主键：人物 `"<篇章id>-<序号>"`（如 `qixuanmen-0`）、灵兽 `beast-0`、灵草 `herb-0`、法宝 `tres-12`、功法 `gongfa-5`、阵法 `zhenfa-3`、符箓 `fu-7`。**分隔符是 `-`，不能用 `#`**（`#` 会把 URL 截断，深链传不到）。
- **key 必须用「原数组下标」**（`cfg.prefix + i` 里的 `i` 是全量数据下标，不是筛选后的下标）：`INDEX` / `ENTRY_BY_KEY` / `REFS` 都按这个 key 建表，筛选后若按下标重排，互引 chip 与 `gotoEntry` 会整体指错条目（2026-10-05 修过一次，见 §10 v48⑤/v49③）。
- 七库在 `LIBS` 里各占一项（`{id, name, view, color}`；各库的 `prefix`/分类/文案在 `BEAST_LIB` 等配置里），搜索面板、互引 chip、`gotoEntry` 都靠它统一分发到对应视图与渲染函数。
- 人物图谱另有 **核心圈降噪**：`CORE_MIN = 5`（被引 ≥ 5 才入圈，当前 263 条里 87 条达标）。全站七库索引现为 572 条；**默认显示全部**（2026-09-22 起），顶栏分段选择器可一键切核心圈。

### 灵兽灵虫数据（`BEASTS` / `BEAST_CATS` / `BEAST_RAIL`）

| 常量 | 含义 | 备注 |
|---|---|---|
| `BEASTS` | 42 条灵兽灵虫 | 字段同人物（`n/t/r/e/img/s/rel/camp/race/ev`），另加 `cat` 分类键 |
| `BEAST_CATS` | 5 类 + 全部 | `chong`灵虫 / `shou`灵兽 / `yao`妖兽妖修 / `zhen`真灵·神兽 / `lian`炼尸魔物 |
| `BEAST_RAIL` | 妖兽等级制度 6 格 | 原著 1-13 级 + 真灵级，对应人界修士境界（见页面说明） |

- `r` 字段在此处为**妖兽等级**（如"二级妖兽（筑基期）""十级妖修（≈元婴后期）"），部分带 `ev` 演进（如噬金虫"虫群→噬金仙→太乙→吞噬道祖"）。
- 等级制度口径：一级≈炼气 / 二~四级≈筑基 / 五~七级≈结丹（凝妖丹）/ 八~十级≈元婴（化形期）/ 化神级及以上≈化神—大乘（十级后不再用数字等级，直接以修士境界命名）。

### 灵草丹药数据（`HERBS` / `HERB_CATS` / `HERB_RAIL`）

| 常量 | 含义 | 备注 |
|---|---|---|
| `HERBS` | **65 条**灵草丹药 | 字段同灵兽（`n/t/r/e/img/s/rel/camp`），另加 `cat` 分类键，无 `race/ev` |
| `HERB_CATS` | 5 类 + 全部 | `lingcao`灵草灵药 / `tiancai`天材地宝 / `tupo`突破丹药 / `fuzhu`辅助丹药 / `danfang`丹方·主材 |
| `HERB_RAIL` | 灵药年份等级 6 格 | 普通草药≈凡人—炼气 / 百年≈炼气—筑基 / 千年≈筑基—结丹 / 万年≈结丹—元婴 / 灵界奇珍≈化神—大乘 / 仙界仙药≈真仙—道祖 |

- `r` 字段在此处为**灵药年份/品阶/对应境界用途**（如"千年灵药（≈结丹—元婴用途）""百年灵药（≈筑基用途）"）。
- 数据来源：起点《凡人必备手册》第二版（最权威）+ 原著情节 + 本地资料库交叉验证，全部标注"已查证"。
- 关键核查结论：筑基丹三大主药=玉髓芝+紫猴花+天灵果（三源一致）；"生生造化丹"官方名为造化丹（灵烛果为主材）；用户清单中"元婴丹/化神丹/大衍丹/洗髓丹/回春丹"等为原著不存在或别名，已按原著名称收录或拒绝。

### 法器法宝数据（`TREASURES` / `TREASURE_CATS` / `TREASURE_RAIL`）

| 常量 | 含义 | 备注 |
|---|---|---|
| `TREASURES` | 71 条法器法宝 | 字段同灵草（`n/t/r/e/s/rel/camp` + `cat`），记录前有分类注释 `/* ===== xxx ===== */` |
| `TREASURE_CATS` | 6 类 + 全部 | `xuanbao`玄天之宝·至宝 / `benming`本命法宝 / `tongji`神通秘术 / `gongfa`功法秘典 / `fulu`符箓·阵法 / `qita`其他法宝 |
| `TREASURE_RAIL` | 法宝品阶 5 格 | 法器→灵器→法宝→仙器→玄天之宝（近似境界对照） |

- **⚠ 配图未完成**：v-treasures 数据中原含 `img` 字段引用（如 `xuantianhulu.jpg`、`balinchi.jpg`），因用户 2026-09-16 叫停图片工作，**61 个指向不存在文件的 img 字段已被移除**（见 §10 待补清单），渲染自动回退首字占位。后续恢复图片时：下载文件到 assets/ → 数据补 `img:"文件名"` → 跑 `dev/tools/verify.mjs`（它会断言"页面引用的图都能找到且能解码"，**不再需要手工登记 manifest**，见 §6）。

## 5. 关键函数与交互

文件末尾初始化：`renderTimeline(); renderBars(); renderLegend();` → `renderCharSkeleton(); renderTabs();` → 建 `charPager` → `applyCharsFilter()` → `initCardLib(×5)` → 视图切换 IIFE（末尾 `applyHash()`）。人物卡片与各库列表都走**瀑布分批渲染**，顺序依赖见本节末尾「启动顺序」。

| 函数 | 作用 |
|---|---|
| `renderTimeline()` | 渲染韩立境界时间轴（`TL` 数据，14 节点；`#lore-nodes` 填节点数） |
| `renderTabs()` | 生成篇章 tab + 核心圈「核心圈 87 / 全部 263」分段选择器（`.seg`）。计数走 `coreCount()` **纯数据计算**，不再依赖卡片先渲染 |
| `makePager(o)` | **瀑布分批渲染引擎**：`render(items)` 重置并挂首批（`firstN=10`）、由 IntersectionObserver（`rootMargin:800px`）按 `stepN=12` 续传、加载完隐藏哨兵 `.batch-sentinel`；`ensureAll()` 立即补全；`ensureKey(key)` 补齐到某张卡（深链/互引定位用）。环境不支持 IntersectionObserver 时直接补全 |
| `renderCharSkeleton()` | 一次成型人物篇章骨架（`<section class="chapter">` + 空 `.grid`），卡片随后分批挂入 |
| `charCardHTML(x)` / `bindCharCard(el)` | 人物卡片模板 + **就地绑定**（裂图兜底、多形象轮播）。分批挂载下不能"整表渲染完再统一绑事件" |
| `mountCharCards(batch)` | 一批卡片按篇章分片插入各篇 `.grid`；地址栏 target 指向的那张带上 `.open` |
| `renderBars()` | 各篇人数柱状图 |
| `renderLegend()` | 图例 |
| `toggleCard(el)` | 点击卡片展开/收起生平（默认收起不剧透）；同时把 URL 同步成深链（可复制分享） |
| `charFiltered()` / `applyCharsFilter()` | 人物筛选**下沉到数据层**（篇章 tab + 关键词（名称/称号）+ 核心圈降噪），按结果整表重排：篇章区块按数据预判显隐 → `charPager.render(list)` → `syncTargetToResults()`。`applyFilter()` 只是兼容别名 |
| `isCore(key)` / `coreCount()` / `CORE_MIN` | 核心圈判定与计数（被引 ≥ 5） |
| `haystack(o)` | 六库（灵兽/灵草/功法/阵法/符箓 + 法宝）**统一的命中范围**：名称/称号/等级/结局/演进/生平/关系/出处/种族 —— 与全库搜索面板同一套字段。改搜索命中范围就改这一处（人物卡搜索比对 `n`/`t`，见上） |
| `initCardLib(cfg)` + `BEAST_LIB` / `HERB_LIB` / `GONGFA_LIB` / `ZHENFA_LIB` / `FU_LIB` | **五库共用的一套实现**（配置驱动：库 id、数据、分类、文案、字段差异全在配置里；`cats.length <= 1` 的单分类库不渲染分类 tab）。实例按库 id 存进 `LIB_UI`（对外只有 `reset` / `ensureKey`），`gotoEntry` 用它复位筛选。改一库行为就是改这一处 |
| `renderTreasureRail()` / `renderTreasureTabs()` / `treasureCardHTML(t,i)` / `bindTreasureCard(el)` / `treasurePager` / `applyTreasureFilter()` | 法宝视图（**不并入上面的工厂**：卡片结构与展示计数不同）。同样走 `makePager` 分批挂载 |
| `renderPlot()` / `plotStepHTML(s)` | 情节梳理渲染：`PLOT_VOLS` → 卷 → 地点篇 → 步骤，`[注记]` 高亮成金色斜体；**首次点开该 tab 才渲染** |
| `openKeyFromHash()` / `syncTargetToResults(libId, keys)` | 地址栏 target 与展开态的一致性（挂载还原 `.open` / 重排后撤掉失效 target），见 §3 |
| `switchView(id)` | 切视图（同步 topnav 高亮；非法 id 回退 v-home） |
| `parseHash()` / `setHash(view,target,replace)` | 读写地址（深链的真相源） |
| `applyHash()` | `hashchange` + `popstate` 的统一入口：切视图 + 有 target 则展开定位 |
| `gotoEntry(key, keepHash)` | 跨库定位：切库/清筛选（**并退出核心圈降噪**）/展开目标卡/滚到 sticky 顶栏之下（双 rAF 延后，等视图切换的重排完成） |
| `INDEX` / `ENTRY_BY_KEY` / `REFS` / `REF_SCORE` / `LIBS` | 跨库索引与互引网络：一次正则扫过全部文本（长名优先匹配，`baseName()` 合并同名，如韩立 6 篇合成一个被引数） |
| `refCount(key)` / `refsBlock(key)` / `refBadge(key)` | 互引展示：「相关条目」/「被引用于」 chip（各取前 8 + `+N`）与「被引 N」徽记 |
| `spotOpen/spotRender/spotMove/spotClose` | 全站搜索面板（`⌘K` / `Ctrl+K` / `/` 唤起；572 条、跨库分组、关键词高亮、方向键+Enter 定位） |
| `back-top` 逻辑 | 滚过 700px 后 `.show` → 点击回顶（尊重 `prefers-reduced-motion`）；圆环 `strokeDashoffset = C × (1 − 已滚比例)`（`C = 2πr`，r 取 `<circle>` 的 21），监听 `scroll` / `resize` + `hashchange`（切视图后文档总高会变、滚动位置不变，**不会触发 scroll**，所以必须补一次） |

搜索框匹配名称与称号（数据层比对 `c.n` / `c.t`；三库统一走 `haystack(o)`）。

**启动顺序**（文件末尾 IIFE，顺序有依赖，别乱动）：互引索引构建（`INDEX`→`ENTRY_BY_KEY`→`REFS`→`REF_SCORE`）→ 搜索面板接线 → 首页统计（读 DATA/BEASTS/HERBS/TREASURES/GONGFA/ZHENFA/FU 长度填 `#home-st-*`）→ 各视图渲染 → `renderCharSkeleton()` 建骨架 **然后** `renderTabs()`（`coreCount()` 已是纯数据计算，**不再要求卡片先渲染** —— v22 那条顺序约束已随本次重构解除）→ 建 `charPager` 并 `applyCharsFilter()` → `initCardLib(×5)` → `applyHash()`。
⚠️ 各库在建 pager 前都会先 `apply*()` 一次，此时 hash 可能指向**别的库**（深链冷启动）⇒ `syncTargetToResults` 必须按 lib 判归属，不能"target 不在我的结果集里就删"。

**修仙界全图引擎（`public/javascripts/map.js`，v59 从本文件拆出）不在上表**：它是独立 IIFE + 懒启动，关键常量与「改之前必读」集中记在 §7 的舆图条目（坐标基准=天南贴图、面积口径的两处出处、乱星海群岛六处同批改、`ARCH_SCAT_D`/`ARCH_BOX_D` 单一真源），迭代原因记 §10；引擎内部函数（`buildLand` / `archIslands` / `fitAll` / `collectStaticLabels` …）不在这里重复登记。

## 6. 图片体系（重要红线）

- **图片文件**：`public/assets/<拼音名>[_<篇章>].<ext>`，跨篇同角色可不同文件（如 `hanli_qixuanmen.webp` / `hanli_xianjie.webp`）。
  **扩展名不固定**：`.webp` 或 `.jpg` 都可能，**以文件实际存在为准，不要凭名字猜**（见下方「体积规范」）。
- **⚠️ 引用分两种，统计时必须都算**：① 页面里的字面量 `assets/xxx.ext`；② **数据里的 `img:"xxx.ext"` 字段**（渲染时才拼成路径，如丹药/灵草/法宝的 `img`）。
  只查字面量会漏掉大量图（`img` / `imgs` 字段在渲染时才拼成路径）。当前真实引用 **482** 张、目录共 500 张（另 18 张为备用图）。曾因此误删了 5 张被数据引用的丹药图（`dan_blue/gold/green/purple/red.jpg`）。
  正解：直接断言“**页面实际引用的图无缺图 + 全部能解码**”（已写进 `dev/tools/verify.mjs`，见 §8.3），不要再用拼正则统计字面量。
- **图片体积规范（2026-09-17 定）**：卡片实际只显示 180–360px，发布图统一 **长边 ≤ 800px / 渐进式 / 去元数据**（90.4MB → 20.0MB，-78%）。
  新增或替换图片时按同一标准压一遍：resize LANCZOS → 存 JPEG q76 与 WebP 各一份取小者，**仅在输出更小时才替换原文件**。
  原始高清图保留在 git 历史里，随时可取回：`git show 15cfee4:dev/unused-assets/<名>`（迁移前）或 `git show 143a8c9:public/assets/<名>`（瘦身前）。
- **格式：逐图最优，不是一刀切（2026-09-17 晚）**。WebP 并非总比 JPEG 小：本仓库的 JPEG 已是 q76 压缩产物，其中约 1/3 已接近无损，硬转 WebP 反而最大 +13.7%。
  故用 `python3 dev/tools/image-slim.py --dry-run` 逐图试 WebP q∈{60,66,72,78,84}，只取「**相对高清原图的 SSIM 不低于当前 JPEG（容差 0.002）** 且明显更小」的档位；达不到就保留 JPEG。实测 **245 张转 WebP / 129 张保留**，21.0MB → 15.8MB（-22.3%，单张中位 -32%）。
  ⇒ 新增图片无需手动跑工具，但要遵守同一逻辑：**画质不降级优先，格式之争让数据决定**。工具里的坑：编码源必须是「原图降采样」的无损图，**不能拿已压过的 JPEG 再编码**（体积与画质双输）。
- **引用方式（发布链路硬规则）**：图片路径只能出现在 **`<img src="assets/…">`** 或 **CSS `url()`** 中。JS 常量数组、`data-src` 等一律发布后裂图。
- **图片引用清单已移除**（2026-09-17）。原 `.asset-manifest` 是一个 `display:none` 的 CSS 规则，用 302 条 `url()` 做“引用登记”——它既不加载也不校验，还得人工同步，且**已经与真实引用脱节（写 302、实际 360）**，因此连元素一起删除（省 13.3KB / 4.2%）。
  改为**真实断言**（`dev/tools/verify.mjs`）：① 页面实际引用的图（DOM 里的 `img[src]`）在 assets 里必须都找得到；② 每一张都必须能解码加载。新增图片不再需要任何手工登记。
  ③ 反向的“目录里有、页面没用”只打印提示、不判失败：当前有 15 张这样的实名备用图（0 / bingfeng / dayan / dongxuaner / hanli / jintong / linghu / lingyuling / tihun / wangchan / xiangzhili / yinyue / yuanyao / yunlulaomo / ziling；原列表里的 nangongwan 已挂上卡片）。
  ⚠️ 其中多数**不在归档原图备份里**（那批是 143a8c9 时的 302 张），所以不要为了“干净”去删它们 —— 删了就丢唯一副本。
- **无图角色**：不硬凑图，卡片显示姓氏首字占位（渲染逻辑：`c.img ? '<img …>' : '<div class="ph">首字</div>'`）。
- **舆图类大图的体积（2026-10-13 优化）**：这一类图不在首屏、单张都是几百 KB 到 1.7MB，按「够用即可」重设过一轮，改图前先看这张表：
  | 用途 | 文件 | 现规格 | 说明 |
  |---|---|---|---|
  | 主图天南底图 | `assets/tiannan-map-cutout.webp` | 1800×1013 / 254KB | 显示尺寸 ≈ 891 世界单位 × zoom（zoom ≤2.8 ⇒ 最大约 2495px），1800px 在常用缩放下无损、极限缩放下略软 |
  | 舆图原图 · 天南 | `assets/tiannan-map.webp` | 2400×1350 / 436KB | 面板 fit 宽度 ≈1365px、可放大 6×，2400px 够日常放大 |
  | 舆图原图 · 大晋/乱星海/风元 | `assets/map-*.webp` | 同尺寸 / 66~133KB | 由同名 `.jpg` 转 webp q84（原图留在 git 历史） |
  ⚠️ `tianfeng.jpg`（533×800 / 155KB）**转 webp 反而更大**（167KB），按「只在更小时才替换」的规矩保持 JPEG 不动。
- **天南舆图切图（2026-10-13 清理）**：天南底图链路是 `image/tiannan-map-cutout.png`（16MB 源图，只留仓库）→ `public/assets/tiannan-map-cutout.webp`（532KB，页面唯一引用，见 §5 地图）。中间产物 `public/assets/tiannan-map-cutout.png`（11MB）**已 `git rm` 并写进 `.gitignore`**：页面从不引用它，但它会跟着 Pages 一起发布。`extract_map.py` / `make_preview.py` 仍在仓库根目录（里面是 Windows 绝对路径，重跑要先改路径）。
- **准确性声明**：页面已含多处声明（v-home 收录说明、hero 副标题、v-chars 卡片区上方橙色警示框、页脚）——图片是网络检索素材（动画截图/官方概念图/百科插画/同人立绘），受动画进度限制（播至人界篇·慕兰之战），灵界/仙界多数角色未在动画登场，**可能与官方形象存在偏差甚至错配**。此声明是用户明确要求，勿删除。
- **找图规范**：优先动画形象 → 官方概念图 → 百科插画 → 同人图；下载后必须用读图能力逐张核对角色身份、清晰度、无水印，错配宁可不用。用户提供图源优先级：百度图片 / 必应图片 / 搜狗图片 / 花瓣网 / B站专栏 / 豆瓣剧照 / 站酷 / trace.moe 识图。
- **删除图片引用的注意**：移除数据内 `img` 字段时，若字段在记录末尾会留下 `, }` 孤立逗号导致 JS SyntaxError；manifest 删除 url 会留下 `,,`。必须做全局清理：`re.sub(r',\s*}', '}')` + **循环** `re.sub(r',\s*,', ',')`（多层逗号需多次）+ `re.sub(r',\s*;', ';')`。

## 7. 样式与外部依赖

- 色板：深色底 + 金色（`--gold: #d4af6a` 系）+ oklch 派生，详见 `<style>` 顶部 CSS 变量。
- `cultivation-chart.js`（境界阶梯图的渲染逻辑）：**用户项目自带，不改**；图表用 `data-cultivation` 属性 + IntersectionObserver 延迟初始化，视图隐藏时切回会自动重播，**无需适配**。
- `cultivation.css`：**允许追加**（2026-09-18 改，原写「用户项目自带，不可修改」）。它是全站**唯一的外链样式表**、职责就是图表，把概览图表样式塞进 `index.html` 内联会把同一类东西劈成两处（图表样式一半在外链表、一半在内联），属于约束反噬；用户拍板「约束如果弄巧成拙就修改」。
  ✅ **追加规矩：只在文件末尾新增 `/* ===== 概览图表 ===== */` 段；不重排、不删改上方任何 `.cv-*` 规则**（那是用户原样的境界阶梯样式），并保持该文件的压缩单行风格。末尾现已追加三段：概览图表尺寸 → **分批渲染哨兵** `.batch-sentinel`（`grid-column:1/-1`，2px 占位）→ **剧情速览「情节梳理」样式** `.lore-tabs` / `.lore-tab` / `.plot-*`（含 ≤640px 单列降档）。
- **ECharts 现在是「进视口才注入」**（2026-10-13）：`<script src=echarts.min.js>` 已从 HTML 里摘掉，改成 `</body>` 前一段小 loader —— 用 IntersectionObserver 盯 `#chart-sunburst` / `#chart-graph`，容器真的进入视口才注入 echarts，`onload` 后再注入 `overview-charts.js`（它自身在 echarts 缺失时会直接 return，天然适配）。桌面 1440×900 上旭日图在首屏内 ⇒ 立即加载；窄屏 390×844 上旭日图在首屏外 ⇒ 不滚动就不下这 527KB。`window.__loadEcharts()` 是显式触发器，**验收脚本必须先用它**（`verify.mjs` 里已加一条「懒加载的 ECharts 已注入并完成初始化」断言）。
- **ECharts 5.6.0 按需构建包**（`javascripts/echarts.min.js`，**527KB**；官方全量包 1006KB，本站只用到 graph + sunburst 两种图，故按需打包，入口与重建命令见 `dev/tools/echarts-entry.js`，许可头写在产物开头、`NOTICE` 有「第三方组件」段 —— 换版本或加图型必须同步改这两处）：零 CDN、零第三方请求，满足"静态资源无第三方请求"硬约束。配套 `javascripts/overview-charts.js`（IIFE 包裹，约 6.6KB）画两张图：
  - **首页旭日图** `#chart-sunburst`：中心"全书人物"→ 六篇章 → 各篇前 6 大势力 + 其他。数据直接复用主页面运行时的 `CHAPTERS` / `DATA[chapId]`，按 `camp` 字段统计（INDEX 条目不含 camp，必须遍历 DATA）。
  - **人物图谱力导向图** `#chart-graph`：基础名级被引 ≥ `MIN_REF`（= 3）的核心角色（**随互引扩写增长，v49 时为 98 人**；`#graph-core-n` 显示这个数，`verify.mjs` 断言它与实际节点数一致），节点大小 = `REF_SCORE`，颜色 = 首次登场篇章，连线 = `REFS[].out` 互引。分批生长动画（按篇章每 450ms 一批 setOption merge），`roam: 'move'` 只拖拽平移（禁滚轮缩放，避免和页面滚动冲突）。节点 click 通过改 `location.hash = 'v-chars/<key>'` 跳人物卡（`gotoEntry` 在主 IIFE 内外部访问不到，走 hash 路由）。
  - **初始化时机**：脚本在 `</body>` 前，但必须等 `window load` 后再 `sync()`，否则 echarts.init 时 canvas 尺寸为 0 只画出空圆环；`setTimeout(…, 300)` 再补一次 `resize()`。
  - **折叠**：图谱区包在 `<details class="graph-fold" open>` 里，默认展开；toggle 事件里 `setTimeout(resize, 60)` 修正收起后展开的 canvas 尺寸。
  - **配色只有一个来源**：篇章名与色值都取自 `CHAPTERS`（其 `color` 形如 `var(--c1)`）→ 运行时用 `getComputedStyle` 解析成具体色值（canvas 读不了 CSS 变量）。**不要在 JS 里再手抄一份 hex**：2026-09-18 之前那份就是这么来的，与页面 `--cN` 只有 c1 对得上（c2–c6 全错）。
  - **样式归属**：`.graph-fold` 一族与 `#chart-sunburst` / `#chart-graph` 的尺寸（含 ≤760px 降档）都在 `cultivation.css` 末尾的「概览图表」段。**画布高度不要再写回内联 `style`**。
- **修仙界全图的离屏画布内存（v59）**：底图/色带都只沿 y 变化（横向完全一致）⇒ 不再烘焙世界尺度位图，改成两条 **1px 宽竖条**（`offBg` 海色渐变、`offBand` 三界色带 + 壁障渐变带，各 1×5600 ≈ 22KB），每帧按可见范围横拉；经纬网横向不均 ⇒ 每帧只画可见格点（`drawSea()` / `drawGraticule()`，压在底图之上、色带之下，与原烘焙顺序一致）。唯一保留世界尺度栅格的是大陆层 `offLand`（`WORLD + 2×PAD`，`PAD=300` ⇒ 3600×4800 ≈ 66MB），接缝临时画布按单块 bbox 分配（≈11MB）。总计 **177MB → 77MB**（实测 `__fanrenMap.canvasInfo().mb`：底图+色带 0.04MB、陆面 65.9MB、接缝临时画布 11MB；verify 有「≤ 90MB」断言）。
  · **两个外延常数别搞混**：`PAD` 只管**陆面栅格**外延（决定内存，`canvasInfo().landExtent` 必须落在 `bounds` 内）；**观感外延**（海色/经纬网/壁障虚线铺多远）由独立的 `BG_PAD=700` 决定，它不占内存、改它会改观感。
  · 拆出来的 `javascripts/map.js` 是独立 IIFE + 懒启动（首次进 `#v-map` 才 init），`window.__fanrenMap.*` 自检 API 全在它里面。
  · **天南贴图是「坐标基准」**：越国/溪国/天南一带的地点坐标是照贴图上的刻字摆的（图上字形即真值），贴图落位 = `区域中心 ± wrx*2.7`。**换图、换裁切、动这个落位系数，都要同批重标这批坐标**，并用 `__fanrenMap.locsOffLand()` 核（见 §8.3、§10 v60）。
  · **「面积比例」的口径全图只有两处出处**：页脚那条 note 与「地理考据」抽屉的「图上比例 · 压缩示意」段。**改比例必须同批改这两处**，否则网友按图问「为什么不是十倍」时两边打架（v61 加）。
  · **乱星海群岛的坐标是「一整套」**：`ARCH_SPECS`（手绘岛）+ 撒点环半径/尺寸 + 撒点裁剪范围 + 17 处点位 + `REGIONS` 的乱星海椭圆 + `OCEANS` 四条海域注记，六处必须同批改。数据坐标包围盒已提成单一真源 `ARCH_SCAT_D`（撒岛中心范围）/ `ARCH_BOX_D`（含岛体半径，供 `sameSea()` 判「同处一片海」）——**动群岛先改这两个常量**（v61 修掉了 v56 搬家时漏改、一直指着大晋位置的 `ARCH_BOX`）。另注意 `REGIONS` 的 `rx/ry` 只决定标签落点与取景框，**图面体量由 `ARCH_SPECS` 决定**：只改 rx/ry 是「假放大」。
  · **改大晋/天南一带尺寸前先读 §10 v61**：西缘受天南贴图的硬右缘（数据 x≈583）约束、南缘受 `landExtent` 栅格上界约束，两条都是「碰了就出直缝/被平切」的硬边界；`buildLand` 纵向是 `wry×1.18` 而 `landBox` 余量只有 `1.28`，ry 一大就会被切平。

- 字体：**纯系统字体栈**（`--font-serif` 优先 Songti SC / STSong，`--font-sans` 优先 PingFang SC / Microsoft YaHei，逐级回退）。2026-09-17 已移除 `miaoda.feishu.cn` 的 Noto 字体 CDN（省 11.35MB）：**静态资源 0 第三方请求**（唯一例外见下条「访问统计」），离线/`file://` 打开外观完全一致，**不要再引入外部字体**。
- **访问统计（不蒜子官方 busuanzi.ibruce.info）**：首页 hero 统计行末的「次浏览」是全页唯一的外部请求。由 `public/index.html` 里一小段内联代码在**真实域名下**才发起（`file://` 与 `localhost/127.0.0.1` **不发起** ⇒ 本地预览零外部请求、也不会把调试流量写进线上计数）；本地想看效果加 `?stats=1`。
  · **接口与取值（2026-10-09 迁回官方）**：注入 `<script src="https://busuanzi.ibruce.info/busuanzi?jsonpCallback=BusuanziCallback_<随机>">`（官方**没有 CORS 头**、只认 Referer ⇒ 只能走 JSONP 注入，`fetch` 读不到响应；`referrerPolicy='no-referrer-when-downgrade'` 必须显式写，跨域默认策略只送 origin、服务端拿不到路径），显示 **`BASE_PV + site_pv`**，其中 `BASE_PV = TARGET_PV(1888) − OFFICIAL_AT_SWITCH(1224)`（见下条「起点对齐」）。**不要换回 `page_pv`** —— 它是按「完整 URL 字符串」分桶的：尾斜杠、`?from=wechat`、深链 hash 都会各成一个独立小桶从 1 重新累计（实测同一页面 127 / 1 / 1 / 8），展示出来就是「一千四百零几」的假小数字；`site_pv` 实测按 host 分桶、跨所有 URL 变体统一累加（`http`/`https`、带不带端口、带不带尾斜杠都进同一个桶）。`verify.mjs` 有三条断言专守这些口径。
  · ⚠️ **字段名别抄错（本次踩过的坑）**：官方 JSONP 回的是**扁平**字段 `site_pv` / `page_pv` / `site_uv`（官方那支 `busuanzi.pure.mini.js` 也是这么读的）；带 `busuanzi_` 前缀那套是 `busuanzi.cc` 的。迁回时若漏改字段名，取到 `undefined` ⇒ 直接落到「— 统计暂不可用」（这次就是本地 headless Chrome 抓调用栈才定位到的）。
  · **口径**：每次载入都直接取回一次累计值并显示 —— 不写本地缓存、不做去重窗口（v28 那套「1 分钟内只计一次」已按用户要求移除，见 v33；**不要再加回来**）。
  · **失败降级**：`#stat-views` 默认 `display:none`，取到值才显示；请求失败或 6 秒无响应显示「— 统计暂不可用」。
  · **起点对齐（2026-10-09，用户指定 1888）**：显示 = `BASE_PV + site_pv`，`BASE_PV = TARGET_PV − OFFICIAL_AT_SWITCH` = 1888 − 1224 = 664。`OFFICIAL_AT_SWITCH` 是迁回瞬间官方桶的值（实测 1223 + 首次载入自身 1 = 1224），**改起点只改 `TARGET_PV`**；改 `OFFICIAL_AT_SWITCH` 会平移整个数字。`verify.mjs` 有一条断言守这个推式（`BASE_PV = TARGET_PV − OFFICIAL_AT_SWITCH` 且真的相加）。
  · **迁移史**：2026-10-03（v46）官方持续 502/超时 ⇒ 迁到 `busuanzi.cc` 的 POST JSON 接口，并用 `BASE_PV` 叠加原累计；**2026-10-09 该站（cdn 与主站）整站 502**、它在 10-03 之后新增的计数取不回来，而官方已恢复 ⇒ 迁回官方取 `site_pv`。⚠️ 官方桶**不是**原封不动：迁回时实测只有 1223，比 10-03 记录在案的 ≈1400 还低（计数不会自己变小）⇒ **它在 9 月下旬那波长时间 502 里丢/回滚过数据**；另算上换站期间丢掉的 ≈400，用户记得的 ≈1800+ 里有 ≈600 真的没了。故按用户指定把显示起点对齐到 1888（`TARGET_PV`），而不是直接显示 1223。
  · ⚠️ **`site_uv` 不可信，所以只展示 PV、不展示「访客数」**：同 IP 同 UA 连打 3 次，`site_uv` 5→6→7 逐次递增（根本没去重）。
  · ⚠️ `127.0.0.1` 是**全服共享桶**，本地预览看到的大数字与本页无关（且本地默认不发起）。
  · ⚠️ 官方接口会下发它自己的 `busuanziId` cookie（`SameSite=None; Secure`，供它做 UV 去重）；**本站代码不读写 cookie**，别把这条写成「零 cookie 请求」。
- 无任何构建工具，原生 JS，`file://` 可直接打开（图片为相对路径，**转发时需连同 assets/ 一起**）。
- 首页样式类：`.home-section` / `.home-why`（`<details>` 折叠） / `.home-cards` / `.home-card` / `.home-note` / `.home-quest`（问道自述） / `.src-list`（数据来源）（`/* ===== 首页 ===== */` 段）。
- 全局复用类：`.page-head`（紧凑页头，内含唯一的 `h1` + `.stats` + `.ph-lead` 一句话引导；≤640px 收窄内边距） / `.seg`+`.seg-btn`（分段选择器） / `.lib-search`（三库共用搜索框，胶囊，与分类 tab 同一套形态与 10/12px 外边距） / `.ref-chips`+`.ref-chip`（互引 chip） / `.spot*`（搜索面板一整套） / `.back-top` / `.img-note`（`<details>` 免责声明）。

### 出处与防盗（改动前必读）

> ⚠️ **许可现为 CC BY-NC-SA 4.0（2026-10-07 起；2026-09-17 ~ 2026-10-07 间为 Apache-2.0）**，水印的性质不变：它仍是**出处标识**，**不是「禁止去除」的许可条件** —— CC BY-NC-SA 4.0 第 2(a)(5)(C) 条同样不允许对下游附加额外限制（当年那两条“禁止商业使用”“禁止去除署名与水印”里，前者已回到许可正文，后者**不要**再写回成条款）。页脚保持“欢迎保留”。**不要再把水印写回成强制条款。**
> 但“不在卡片图上盖章”这条**依然成立** —— 理由不变（图不是你画的），且第三方图片**本来就不在 CC BY-NC-SA 4.0 范围内**。

- **全页水印**：`.watermark`（`position:fixed` 全屏平铺）的背景图**已内联为 base64 data URI**，不再引用 `watermark.svg`——`dev/watermark.svg` 仅为 `dev/_backup/index-v*.html` 保留，**勿删**（删了旧备份开出来就没水印）。改水印要改那段 base64，别改回外部文件引用。**瓦片三行 = 首页大标题的两行原文（`《凡人修仙传》` / `百科 · 全篇资料图谱`，与 `#v-home .hero-title h1` 逐字一致，别并成一行）+ 站点网址 `bunnychen.top`**；网址行是「截图转发后还能找回本站」的唯一线索，**不能删**。改名时两处同步：那段 base64 与 `dev/watermark.svg`。
- **无 `@media print` 例外**：打印/导出 PDF 也带水印（`position:fixed` 在分页媒体里逐页重复），别再加 `display:none` 把它关掉。
- **不在卡片图片上盖章**：曾经加过 `.card-top::after{content:"bunnychen.top"}` 的右下角标，**已移除且不要再加**——图片本身是网络检索的第三方素材，不是本站作品，在别人的图上盖自己的出处站不住脚（真有争议时也不占理）。图片区保持干净。
- **元数据**：`<head>` 里三件套——版权注释块（含版本/日期/仓库地址，抄整页的人会把出处一起带走）、`<link rel="canonical">`、JSON-LD（author / datePublished / dateModified / license / isBasedOn）。**改版必须同步**。许可字段当前为 `https://creativecommons.org/licenses/by-nc-sa/4.0/`。
- **「最后更新」四处 + 两处元信息：全部自动注入，不要手写**（`dev/tools/stamp.mjs`，2026-09-20 起）。四处 = 页脚「最后更新」/ 头注释 / JSON-LD `dateModified` / 导航栏「更新 YYYY-MM-DD」，另加页脚 `.stamp-note` 里的本次提交说明首行（压平 → HTML 转义 → 截断 56 码点）与 `public/sitemap.xml` 的 `<lastmod>`。取值 = `git log -1` 的 `%cs` + `%s`；GitHub Actions 在 `upload-pages-artifact` **之前**跑 `node dev/tools/stamp.mjs --write`，改的是 runner 工作区里的 `public/index.html` 与 `public/sitemap.xml`，**不进 git**。
  · **为什么不做成页面运行时拉 `api.github.com`**（2026-09-20 用户二选一后拍板 CI 注入）：国内经常超时（本站读者大多在国内）+ 未认证限流 60 次/小时/IP；静态注入零新增请求（不动「静态资源 0 第三方请求」红线），关掉 JS / 爬虫抓取 / 另存到本地日期与 JSON-LD 都是对的。
  · **锚点必须恰好命中 1 次**，否则脚本报错退出且不写文件：动这些锚点（尤其页脚 `.stamp-note` 那个 `<span>`）就要同步改 `stamp.mjs` 的 `RULES`，宁可部署失败也不要静默退回手写（v38 之前手写就漂移过：导航 09-17 / 页脚 09-19 打架）。
  · ⚠️ **改这段文本别用 `String.replace(re, fn)`**（2026-09-20 实测：本机 Node v24.18.0、`replace` 是原生实现、`NODE_OPTIONS` 为空，仍复现）：回调里的捕获组会被截成 1 个字符 —— `'AA首次发布：2026-09-14 · 最后更新：2026-09-19BB'` 经回调替换后得到 `AA次2026-09-20BB`。v38 首次上线就是这么把线上写坏的（`dateModified`、页脚 `.stamp-note`、sitemap `lastmod` 全被吞掉）。脚本已改成 `indexOf` + `slice` 拼接，本地与 CI 结果一致；**不要把 `replace` 回调写回 `stamp.mjs`**。
  · 本地可放心跑 `node dev/tools/stamp.mjs`（体检，只读，验证 6 条锚点是否还在）；`--write` 会真的改工作区文件，跑完记得连同日期一起提交，或提交前 `git checkout -- public/index.html public/sitemap.xml` 还原。
- **明确不做**：禁用右键/选择、JS 混淆、反调试——伤体验与无障碍、几秒可绕过，已否决。

## 8. 开发流程（照做）

1. **先备份**：`cp public/index.html dev/_backup/index-vX.html`（版本号递增，防改坏）。
2. 小改动直接改；大改（结构/批量数据）参照"对象级替换 + 章节标记定位"脚本模式。**改 JS 数据用字符串级精确插入**（数花括号深度找记录闭合，避免 to_json 全量重排破坏格式；`DATA.xxx` 段正则 `(DATA\.%s = \[)(.*?)(\];)`）。
3. **自检（唯一验收方式，改完必须全绿）**：
   ```bash
   node dev/tools/verify.mjs                                   # 默认验 ./public/index.html（file://）
   node dev/tools/verify.mjs --url http://localhost:8899/index.html   # 也可指定 URL
   ```
   **零依赖**：Node ≥ 22 内置 `WebSocket`/`fetch` + 本机 Chrome，自己拉起 headless Chrome 走 CDP，**不装 puppeteer/playwright**。当前 **52 条断言**：十一视图容器、**分批渲染首屏只挂首批**、七库卡片数（期望值取页面自身数组长度，不再写死）、**卡片里没有 undefined/NaN 残字**（rows 缺字段的兜底，v63 加）、他角色具名功法/阵法/灵兽/法宝防回归抽查、**图片引用无缺图 + 全部能解码**、互引网络规模、**每个视图有且仅有一个 h1**、**开源入口齐全（顶栏图标 / hero / 首页卡片 / 页脚同指一仓）**、**勘误引导到 B 站视频评论区（GitHub Issues 只留技术问题，且无主站评论区旧链接）**、**访问统计三条口径（site_pv / 官方 JSONP + 无前缀字段 / 显示起点自洽）**、默认全部且可一键切核心圈、桌面 1440×900 与移动 390×844 双视口的横向溢出与"竖条文本"、篇章筛选、**三库分类筛选（含 tab 计数一致性）与三库搜索**、搜索定位、互引 chip 跳转、返回顶部与进度环、深链冷启动、**深链落到首批之外的卡（按需补齐渲染）**、**筛选后地址栏与展开态一致**、点卡片同步 URL、浏览器返回后视图与地址一致、**静态资源无第三方请求**、**统计位默认隐藏 + 本地不发起上报 + 取到值后显示累计次数（千位分隔）+ 统计位可见时双视口无溢出 + 取值字段是 site_pv**、**两张概览图表渲染与配色来源 + 悬浮详情 + 图谱节点点击跳转 + 折叠展开后 canvas 尺寸恢复**、**舆图离屏画布内存 ≤ 90MB 且陆面栅格覆盖全部陆面内容（`__fanrenMap.canvasInfo()`，v59 加）**、**舆图地点都落在「真的画了陆地」的地方（`__fanrenMap.locsOffLand()`，v60 加；例外只有北海三岛与火云岛两处海岛）**、0 控制台报错。
  ⚠️ **用 `--url` 跑线上会真实计数**：脚本对目标地址共导航 **3 次**（首屏 + `#v-treasures/tres-2`、`#v-chars/lingjie-0` 两条深链冷启动），每次都是真实访客请求 ⇒ 每跑一轮线上验收就给线上统计 **+3**（2026-10-09 复核时把自己的数字从 1224 推到 1240）。要复核就用一次、别反复跑。
  ⚠️ **分批渲染后，"扫 DOM"型断言必须先补齐**：DOM 只是数据的子集（首屏每库 10 条）。脚本注入的 `window.__loadAll(id)` / `window.__loadAllLibs()` 负责补齐（chars / tres 走 `ensureAll()`，三库借 `LIB_UI[id].ensureKey(该库最后一个 key)`）。**忘了补齐会写成假绿** —— 图片完整性那条就从 481 张掉到 70 张覆盖（v49 修）。同理，切降噪/切分类 tab 都会重排，**每次计数前**都要补。
   - 断言失败先看输出里打印的**实际值**再动代码（有 3 条断言曾是自己写错：阈值拍脑袋、期望值写反、把 `<link rel=canonical>` 当资源请求）。
   - ⚠️ **视口用 `Emulation.setDeviceMetricsOverride` 设置**：VS Code 内置浏览器**无视** `setViewportSize()`（请求 1440 实得 729），别拿它做响应式验收，也别用 iframe 顶替（Promises 会永不 resolve）。
   - 快速 JS 语法检查：提取内联 `<script>` 块逐个 `node --check`；拆分后 `public/javascripts/*.js` 也要各自 `node --check`（地图引擎就在里面）。
   - ⚠️ **不要用 `perl -0pi` 改校验脚本**：`@` 在 perl 双引号串里会当数组插值，实测把 `history.length` 改成了 `history.length` 缺字符的语法错。要改就用编辑工具。
   - **「图上位置对不对」要用「是否画了陆地」判，不要用椭圆包含判定**（v60 教训）：`__fanrenMap.landPainted(wx,wy)` 读离屏陆面层 `offLand` 的 alpha（天南贴图、大陆、近海岛屿都画在这层，海面留空），`locsOffLand()` 返回没落在陆地上的地点名单（读不到像素时返回 `null`）。**`file://` 下读画布像素会被浏览器判为「跨域污染」而抛 SecurityError**，所以脚本给 Chrome 加了 `--allow-file-access-from-files`（仅影响验收用的无头浏览器）。
   - **「改观感类改动」的硬证据用 `pixel-diff.mjs`**（v59 新增）：`git show HEAD:public/index.html > public/_ref_head.html` 后 `node dev/tools/pixel-diff.mjs _ref_head.html index.html`（比完删掉 `_ref_head.html`）。它自己起静态服务（**必须 http**：`file://` 下 canvas 被判跨域污染，`getImageData`/`toDataURL` 会抛 SecurityError），并在页面脚本前注入固定 rAF 时间戳 + 固定 `Math.random` 保证可复现；三相机各截一帧后逐像素比对 + 8 邻域聚类，PNG 落在 `--out`（默认 `/tmp/fw-pixel-diff`）便于人工复核。
     **判据是聚类形状，不是总数**：规则格点上的小方块 / 散点（如经纬网十字、文字抗锯齿）属重采样相位，无害；连成一条边、整块平移、少一条带则是结构错位，必须查。基准参考值：v59 拆分 + 画布改造后三帧差异 **0.058% / 0.012% / 0.001%**、最大色差 10/255。
4. **交付**：发布产物是 `public/`（`index.html` 页面本体 + `javascripts/` + `assets/` 图 + `sitemap.xml`/`robots.txt`）；`index.html` 仍是单页应用，不再是「唯一文件」。
5. **发布**：`git push origin main` → GitHub Actions 先跑 `node dev/tools/stamp.mjs --write` 把「最后更新」、提交说明与 `sitemap.xml` 的 `lastmod` 刷成本次提交（见 §7），再只把 `public/` 上传为 Pages 产物（线上 `https://bunnychen.top/fanren-wiki/`）。**提交时不必再手动改这些日期。**首次需在仓库 **Settings → Pages → Source** 选 **GitHub Actions**。推完等约 30s，用 `curl -sI` 看体积/状态码再抽查关键标记（`gh` CLI 未安装，Actions API 未鉴权返回 404，一律以线上地址为准）。
6. **文档同步（交付的一部分）**：结构性改动、新增函数/常量、流程变化都要顺手更新本文档（§3 结构、§5 函数表、§10 迭代日志至少各改一处），别让它烂掉。

## 9. 数据来源与已核验事实

- 用户提供分析资料库：`~/Downloads/fanren-xiuxian-zhuan-analysis-master/`（人物谱系 73 人/故事梗概/社会结构/小说概述资料库/时间关系图/README，声称基于原著 20 卷 532,528 行逐段验证、结局带原文行号）。曾据此：新增 17 位谱系角色、丰富 17 处核心角色生平、纠错"王婵→王蝉"（全站已统一）。
- 关键剧情设定（已在页面"剧情速览"呈现）：双韩立因果闭环——A 韩立=轮回殿主（时间道祖→败古或今→散尽时间法则铸掌天瓶→穿越远古→改修轮回→创轮回殿→妻甘如霜=南宫婉前世→联手 B 击败古或今→陨落）；B 韩立=本线主角（捡瓶→大罗→放弃道祖→掌天瓶返回过去救元瑶/帮厉飞雨结仙缘/踢瓶给少年自己→因果闭环→隐居黑土仙域）；掌天瓶=唯一逆转时空之物。
- **剧情速览 · 情节梳理（全书十一卷）是第三方内容**：整理自微信公众号「书生去哪了」的原创文章《凡人修仙传》情节梳理（全）（2026-05-27 发布，https://mp.weixin.qq.com/s/jbp5FD4rk07W4aeNd9wFXQ ）。页面该栏上下各有一处署名 + 原文链接，`README` / `NOTICE` 有对应声明 —— **改这条内容前先看 NOTICE 的口径**，权利人若提出异议应改为仅保留摘要 + 跳转原文。
- 首页"为什么做这个网站"文案来源：`../fanren-xiuxian.md`（境界差距感悟 + 映照现实 + 统一资料集定位 + 页面包含 + 问道自述）——2026-09-17 已把该页文字**整体并入首页正文**，两边互为镜像，改一处要同步另一处。

## 10. 已知限制与迭代历史摘要

**限制**
- 部分冷门角色无可靠图片（页面保留首字占位），后续有官方设定图可继续补；曲魂/极阴祖师等已按用户反馈迭代修正。
- **法宝/灵草配图待补（61 个文件名）**：2026-09-16 用户叫停图片工作后，已移除 61 个指向不存在文件的 img 引用（数据文字完整）。待补清单（拼音文件名）：`balinchi biyanjiu chuwudai dayanrenxingkuilei diandaowuxingzhen dulongdan ganyingling guiluofan hanyuanren haoyuandan heifengqi hongxiandunguangzhen hualingubao huanglinjia huazhou hunyuanbo jiangyundan jinfuzimuren jingangzhao juguiikuilei langshoukuilei langshouyuruyi lingshouhuan liudaolunhuipan luohunsha lvhuangjian miechendan minghunzhu molongren mosuiduan qiankunta qianlanbingyan qingmingzhen qingxudan qiyanshan renhuyaokuilei sheweikuilei shiling taiyangjingshi tanyaofan tianluyin tianshizhu wanyaofan wuxinghuan wuyulingcha xiusuidan xuanhuangjing xuantianhulu xuantianzhanlingjian xuantiefeitiandun xuelingshui xueningsowuxingdan xueqidan xuhuangding yingyuehuan yuanmingdeng yuanyingjikuilei zhangtianyin zhenhaizhong zhuquehuan ziyinwan`（.jpg，对应 TREASURES/HERBS 中的法宝丹药）。恢复图片流程见 §4 TREASURES 小节。
- 图片可能错配（已有声明）；用户曾要求逐张核对，历史轮次修过多处错图（陈巧倩↔董萱儿、风希、尸魈、曲魂、极阴祖师等）。
- 人物卡区 263 张卡很长（**全量渲染约 2 万 px / 21,903 个 DOM 节点**）——已用**瀑布分批渲染**（首屏 10 条、滚动续传；实测首屏 DOM 降到 3,812 节点，本机加载 185ms → 91ms）+ 篇章 tab + 全站搜索缓解；默认显示全部，也可一键切「核心圈 87」。
  ⚠️ **分批渲染的代价（知情取舍，别当缺陷报）**：浏览器 Ctrl+F / 打印只覆盖**已挂载**的卡（首屏 10 条/库）。深链与互引定位靠 `ensureKey` 按需补齐，"点进去一片空白"的局面已经消除，但"Ctrl+F 找不到"是设计取舍 —— 站内搜索面板（572 条全量索引）才是检索入口。
- **情节梳理是第三方内容**：整理自微信公众号文章（见 §9），若权利人提出异议需改为摘要 + 跳转原文。
- 未做（按需）：展开卡改为侧边抽屉（现在原位摊开、把下方内容顶下去）、3–4 张带第三方水印/游戏 UI 的法宝图待换（如 `liudaolunhuipan.webp` 带 NGA 水印与「无法转赠」框）。
- ❌ **已否决：人物总览页**（把韩立 6 张卡合成一条人生线）—— 2026-09-17 做过可用原型（六段人生线 + 全书境界总演进 + 关联条目 254 条，数据取自真实记录），用户判断「没用」明确否决。**不要再提这条建议**，也不要再拿它当"未完成项"。

**历史迭代**（备份文件即版本节点）
- v1：六篇章全量人物表格 → v2：+故事脉络/双韩立因果闭环 → v3：+rel/camp/race 三标签 + 修为演进 ev → v4：+点击展开生平、默认不剧透、修为行上卡片、图片准确性声明 → v5：+分析资料库补充（17 新角色、王蝉纠错、5 张新图、.asset-manifest 登记）→ v6：三视图分页重构 → **v7：+第四视图「灵兽灵虫」**（BEASTS 40 条、妖兽等级制度 rail）→ **v8：图片修复**（余子童/曲魂/六道极圣/石坚 4 错图替换 + 23 张生物补图）→ **v9：数据合理性修正**（依据 _review.md：BEAST_RAIL"化神级及以上"、白老鬼化神后期、Hero 副标题 221、蟹道人/魔主结局、CSS 修复、v-beasts 搜索框）→ **v10：+第五视图「灵草丹药」**（HERBS 49 条→复查 64 条、灵药年份等级 rail、22 张中国风插画）→ **v11：全量图片更新**（按用户指定图源质检 218 张，assets 218→267）→ **v12：修曲魂/极阴祖师错图 + 再补 41 个无图角色**（顶部加"持续更新中 · 作者主页 · 更新 2026-09-16"）→ **v13：+第六视图「法器法宝」**（TREASURES 65 条、6 分类、品阶 rail，配图因用户叫停未完成）→ **v14：文字资料补全——ev 修为演进字段 173→0（221/221 全齐）** → **v15：首页重构《凡人修仙传》百科**（v-home 默认视图：为什么做这个网站 + 6 板块入口卡 + 收录说明；topnav 加"首页"；title/品牌/页脚统一；移动端 topnav 防溢出）→ **v16：清理 61 个缺失图片引用**（v-treasures/v-herbs 未完成配图，移除 img 字段与 manifest 登记，修复孤立逗号 JS 错误，全 7 视图自检 0 错误）→ **v17：首页新增「数据来源」板块**（.src-list 样式，注明原著/动画/起点《凡人必备手册》/分析资料库/百科社区/图片素材六大来源，位于收录说明下方）→ **v18：全量 ev 补全 + 文本打磨**（用户指令"终止所有流程、只做文本补全"后执行：BEASTS ev 补 35 条、HERBS ev 补 64 条、TREASURES ev 补 65 条——全站 390 条记录 ev 字段 100% 覆盖；扩写 15 条过短生平 s；完善 4 处结局 e（野狼帮帮主/风老怪/魏无涯/武阳）；node --check 通过；备份 _backup/index-v18.html）→ **v19：法宝 rail 瘦身 + 首页来源附链接**（①TREASURE_RAIL note 精简至灵草 rail 同风格（去长出处、保留"来源：起点手册+B站"简注）；note 单行截断 `white-space:nowrap;overflow:hidden;text-overflow:ellipsis` + `title` 属性悬浮全文——rail 卡片 177px→89px、rail 总高 103px（比灵草 rail 155px 矮 1/3），实测 playwright 计算样式验证 grid 6 列生效；②首页「数据来源」板块 6 条来源全部附可点击官方链接：起点正版 https://www.qidian.com/book/107580/、B站国创 https://www.bilibili.com/bangumi/media/md28223043、起点《凡人必备手册》https://read.qidian.com/chapter/Gyliu2kLjSQ1/ldlf0qmr1zwex0RJOkJclQ2/、本仓库资料页 ../fanren-xiuxian/、百度百科 https://baike.baidu.com/item/凡人修仙传/10375488、起点资源站境界页 https://m.qidian.com/ziyuan/fanrenxiuxianzhuan/post/jingjie、图片检索平台（百度图片/必应/花瓣）；新增 .src-list a/.src-site 样式，移动端 overflow-wrap 修复；桌面/移动自检 0 错误；备份 _backup/index-v19.html）。
- 中途否决方案：**左右分栏**（用户不喜欢，改"分页面"）；已废弃脚本 `_backup/apply_layout.py`（分栏死路，勿再引用）；**AI 生成图片**（用户明确否决"不要AI生成"）。
- **v23：返回顶部进度环**（用户看到参考项目 `talesov/fanren-kb` 的按钮后提出"进度条也可参考"）——.back-top 内嵌 SVG 双圆（`bt-track`/`bt-bar`，`viewBox 0 0 48 48`、`r=21`、`-rotate-90`），`strokeDashoffset = 2πr × (1 − 已滚比例)`，`stroke-linecap:round` + hover 金色微光；只加了三行事件（scroll/resize/hashchange），仍用 `ticking` + rAF 限频。验收断言扩为三点：顶部不显示且空圈、滚动后出现且环推进、到底近满圈、点击归零。
- **v24：代码整理（质量复审，不改变任何输出）**——
  ① **先补测试再动手**：断言 19 → **24 条**（新增：图片引用无缺图、全部能解码、三库分类筛选与 tab 计数一致性、法宝分类收窄、三库搜索可用）。新断言当场抓到两个真问题：manifest 清单与真实引用脱节、14 张未引用备用图。
  ② **修法宝库 4 处**：`renderTreasureRail` 缺容器兜底（与灵兽/灵草不一致）；`applyTreasureFilter` 直接取 `.tab.active` 会抛 TypeError（改成 `?.` 式兜底 + `|| "all"`）；`TREASURES.indexOf(t)` 求 key（O(n²) 且依赖对象唯一）改用 map 下标；**补裂图兜底**（原来只有灵兽/灵草有，法宝裂了就裂着）。
  ③ **去重**：灵兽/灵草两套逐字重复的 rail + tabs + 卡片模板 + 筛选 + 事件接线（约 220 行）→ 一套 `initCardLib(cfg)`（约 100 行）；字段差异全走配置（`chips`/`rows`/`unit`）。验证方式：重构前后取 `#beasts`/`#herbs`/`#beastRail`/`#herbRail`/`#beastTabs`/`#herbTabs` 的 innerHTML SHA-256，**6 项全部逐字节一致**。法宝库不并入（它是整表重渲染 + 不同卡片结构）。
  ④ **删死代码**：`.asset-manifest`（302 条 URL 的隐藏清单，已与真实引用脱节）+ `.home-feats` 6 条规则（首页「页面包含」早已删除）+ `.home-why .lead`。
  ⑤ 体积：`public/index.html` 315.8KB → **302.5KB**（-4.2%）、行数 2493 → 2377。
  ⑥ 顺带校正：`.gitignore` 里还写着 Doubao 时代 `shot.py` 的注释；§2 目录树还列着并不存在的 `dev/unused-assets/`。
- **v25：三库搜索框与搜索深度统一**（用户就 v24 报告的两个“不齐”点要求统一）——
  ① **样式**：灵兽（绝对定位图标+矩形框）、灵草（flex 胶囊）、法宝（CSS 内联 SVG 背景）三套 → 一个 `.lib-search`（胶囊、与分类 tab 同形态，真 DOM `<svg>` 图标；≤640px 占满宽）；三处 tab 行外边距也对齐为 `10px 0 12px`。实测三处计算样式只有**一个指纹**（340×41、图标 left 15 / 中心 y 20、输入 left 37）。
  ② **顺序**：灵兽/灵草原来是“搜索框→tab”，法宝是“tab→搜索框” → 统一为 **tab → 搜索框**（与人物图谱的“篇章 tab + 搜索”一致）。
  ③ **命中范围**：原来法宝匹配 名称+称号+来历+持有者+出处+生平，灵兽/灵草只匹配 名称+称号 → 抽出 `haystack(o)` 三库共用（9 个字段，与全库搜索面板同一套）。正文不再塞进 DOM 属性，而是在 `list()` 里存成 `Map<data-key, 命中文本>`。placeholder 同时写明搜索范围（如「搜索灵兽灵虫：名称·等级·生平·结局」）。
  ④ 验收 24 → **25 条**：搜索拆为“按名称定位”与“命中范围一致 + 无结果给空状态”两条（用「韩立」这种只出现在正文字段里的词做判据 —— 旧实现下命中数必为 0）。
- **v20：界面治理（字体/首屏/顶栏/搜索/配色）**——① 字体治理：移除 `miaoda.feishu.cn` 的 Noto CDN（-11.35MB、首屏零第三方请求），改用系统字体栈；② v-chars 首屏瘦身：hero→紧凑 `.page-head`（760→339px）、navbar 109→59px、免责声明折进 `.img-note`（112→42px）、`.tabs` 强制单行 + 右端渐隐遮罩，全页高度 65423→45167px；③ sticky 顶栏（`.topnav` top:0 / `.navbar` top:49px）+ `.back-top` 返回顶部；④ 全站搜索面板（⌘K / Ctrl+K / `/`，390 条跳库索引、分组、高亮、定位）；⑤ 颜色收敛 34→6 色相，`.img-note`/法宝视图统一到同一套 token，免责声明去重 5→2；⑥ 修 2 个既有 bug：`applyFilter()` 用全局 `.card` 导致 `closest(".chapter")` 为 null（灵兽/灵草卡在页上时篇章切换直接抛错）、篇章 tab 清 `.active` 时把法宝 tab 一起清掉（`#treasureTabs .tab.active` 为 null → TypeError）。
- **v21：互引网络**——`INDEX`/`ENTRY_BY_KEY`/`REFS`/`REF_SCORE`：一次正则扫过全部文本（长名优先，避免"韩立"截断"韩立之师"），`baseName()` 合并跳库同名实体（韩立 6 篇合成一个被引数），卡片底部渲染「相关条目」「被引用于」 chip（各前 8 + `+N`）与「被引 N」徽记。实测 390 条里 331 条有互链（85%），加载 +10~15ms；韩立被引 254、掌天瓶 19、南宫婉 17。⚠️ chip 必须用**捕获阶段**监听 + `stopPropagation`，否则会被卡片自身的展开/收起吃掉。
- **v22：降噪与定位（核心圈 + 深链 + 首页瘦身 + 统一页头 + 验收脚本）**——① 被引分布是长尾（381 条中 208 条为 0、仅 38 条 ≥ 5）⇒ `CORE_MIN = 5` + `coreOnly` 默认开，`#tabs` 内 `.seg` 分段选择器「核心圈 N / 全部 221」；`gotoEntry` 跳转时自动退出降噪（否则滚过去是一片空白）；② 条目深链：`data-key` 分隔符由 `#` 改 `-`（`#v-treasures/tres-12`），点卡即同步地址栏；路由补齐 `hashchange` + `popstate` 双监听（**旧实现 `openFromHash()` 只处理 target、从不切视图 —— 手改地址或浏览器返回时视图不动**，被新增断言抓到）；③ 首页瘦身：「为什么做这个网站」折进 `<details class="home-why">`、删「页面包含」清单、清 4 处裸 URL 的 `.src-site`；④ v-beasts/v-herbs/v-lore/v-realms 统一 `.page-head` 紧凑页头，每视图补齐唯一 `h1`；⑤ `dev/tools/verify.mjs` 新增并把断言从 14 条扩到 **19 条**（新增：每视图唯一 h1、核心圈默认与回全部、深链冷启动、URL 同步、浏览器返回后路由一致）。
- **v26：转 Apache-2.0 + 开源准备（2026-09-17）**——用户已知悉与 `zjy2931/fanren-wiki`（Next.js + Cloudflare 的动画社区共建版）撞名，判断不属于冲突（GitHub 仓库名只在账号内唯一），决定公开仓库并给出三条指令：`dev/` ignore、许可转 Apache-2.0、仓库转 public。
  ① **`dev/` 移出仓库**：`.gitignore` 加 `dev/`（原先只忽略 `dev/_shots/`、`dev/_chk_*.html`）+ `git rm -r --cached dev/`，本地文件全部保留。
  ② **LICENSE 换 Apache-2.0 逐字全文**：从 `https://www.apache.org/licenses/LICENSE-2.0.txt` 直接 curl 落盘（**202 行 / 11358 字节，sha256 `cfc7749b…`**），**不手打、不改写**（Apache 要求许可全文不得修改）。原“中文范围说明 + CC 官方 deed/legalcode”版本废置。
  ③ **新增 `NOTICE`**：Apache-2.0 §4 要求随分发保留。写明授权范围（页面代码 + 原创整理内容）、**明确排除** `public/assets/` 第三方图片与原作 IP、以及名称标识不授商标权（§6）。
  ④ **页面三处许可声明同步**（漏一处就自相矛盾）：`<head>` 版权注释块、JSON-LD `license`、页脚。页脚原链接指向 `bunnychen.top/about/LICENSE/`（那是**主站的** CC-BY-NC 页），已改为直接链 apache.org（顺带避免仓库改名后链失效）。
  ⑤ **删掉的表述**：“禁止商业使用”“禁止去除署名与页面水印后发布” —— 与 Apache-2.0 不相容（该许可禁止对下游附加额外限制）。水印保留为**出处标识**，页脚改为“欢迎保留”；`README.md` 许可段落同步。
  ⑥ 核对过 `cultivation.css` / `cultivation-chart.js` **无第三方版权头**（自持代码），故可整体纳入 Apache-2.0；将来若引入外部库，必须补进 `NOTICE` 的“第三方组件”段。
  ⑦ **全站开源入口**（用户要求"主页等内容也要体现开源，并附 GitHub 仓库链接与图标"）：四处同指一仓——顶栏图标按钮（`.tn-github`，与 `.tn-search` 同形态）、hero `.project-links` 的「GitHub 源码」按钮、首页新增「开源」板块（`.repo-card`：图标 + 仓库名 + 许可说明 + 「前往仓库」）、页脚一行链接。图标为**内联 SVG**（16×16 GitHub mark 路径，三处复用）——**不能引 CDN 或图标字体**，否则直接打破「静态资源 0 第三方请求」断言。
     ⚠️ 两个坑：① `.tn-github` 的内边距必须写成 **`.topnav a.tn-github`**，裸类名权重（0,1,0）盖不住 `.topnav a`（0,1,1）的 `padding:6px 16px`；② 顶栏图标在 **≤1100px 隐藏** —— 实测 698px 下链接区本就差 33px（法器法宝已被切一半），图标再占 40px 会把末个入口整个切掉，与该断点「优先保证 7 个视图入口完整可见」的既定意图冲突（沿用 `tn-update` 的处理）。窄屏仍有 hero / 首页卡片 / 页脚三处入口。
     改后实测：`.topnav .wrap` 高度仍 **48px**（`.navbar` 的 `top:49px` 与 `.view` 的 `scroll-margin-top:49px` 未错位）、729px 下 `scrollWidth == clientWidth`。
  ⑧ **验收 25 → 26 条**：新增「开源入口齐全（顶栏图标 / hero / 首页卡片 / 页脚同指一仓，图标真实渲染）」，覆盖链接一致性 + 图标实际渲染尺寸（防 SVG 路径写空）。顺带修正 §8.3 里早已过期的「当前 24 条」。
  **历史取舍（已决 2026-09-17）**：`dev/` 虽已 ignore，但 **`dev/Agent.md`（11 个版本）与 `dev/_backup/` 仍留在 git 历史里**（81 个 blob / 3.9 MB），转 public 后可被任意 checkout —— ignore 只防未来、不护历史。已扫描全部 `dev/` 历史文本确认**无凭据、无个人隐私**（唯一命中是 B 站 opus 链接里的长数字串），用户判断可接受，**决定不动历史**（不用 `git-filter-repo`）。若日后反悔，代价是重写全部 SHA + 摘 remote + force push，且那时仓库已 public、可能已有 fork。
  ⑨ **已转 public 并上线**：仓库转公开（`Settings → Danger Zone`，用户手动操作；`gh` CLI 未安装）→ `git push` 触发 deploy #12 → 线上已验证：`HTTP 200 / 308057 bytes`（与本地文件字节数一致）、`repo-card` 命中 4、`apache.org` 命中 2、`CC-BY-NC` 命中 0；GitHub 仓库页已显示 **Apache-2.0 license** 徽章，文件树无 `dev/`。
- **v27：页脚接入访问统计（不蒜子，2026-09-17）**——用户问「Google Analytics 能看到这个页面吗」（答案：看不到，GA 只由主站 `mkdocs.yml` 的 `extra.analytics` 在 MkDocs 构建时注入，而本页是手写单文件 HTML、独立仓库独立部署；旧路径桩页也是手写 HTML，同样没报），随后要求「能简单实现、在页面上直接看到真实查看人数就行」。
  ① **选型**：不蒜子（`busuanzi.pure.mini.js`）是唯一**零注册、无需后端、有现成页内组件**的方案。替代方案实测不可用：GoatCounter 的 CDN `gc.zgo.at` 从本机直接请求 **HTTP 000 超时**（8s），国内访客基本拿不到数据；`abacus.jasoncameron.dev` 需先 `/hit` 建键；GA4/counter.dev 只有后台看，没有页内数字。
  ② **只展示 PV 不展示 UV**（见 §7 实测：`site_uv` 同 IP 同 UA 不去重）。
  ③ **UI**：计数并入页脚「最后更新」那一行尾（` · 本文浏览 N 次`），**不新增行、不产生布局位移**；容器默认 `display:none`，脚本成功才显示 ⇒ 服务不可用时零残留。数字到手后补千位分隔。
  ④ **不污染本地**：`file://` 与 `localhost/127.0.0.1` 一律不注入 ⇒ 既保住「本地/file:// 零外部请求」，也不会把验收脚本每次跑的流量写进线上计数。
  ⑤ **验收 27 → 29 条**（v28 后为 **30 条**，见下）：新增统计相关断言；原「页面无第三方资源请求」改名为「**页面静态资源无第三方请求**」（统计请求是运行时注入，不在静态标签里）。
  ⚠️ **计数粒度（2026-09-17 实测）**：计数键 = **host + 路径**，**查询串不参与**（`?probe=9` / `?zz=abc123` / 无参数三者共用同一个计数：14→15→16）；fragment 更不会发 ⇒ hash 路由与 UTM 参数都不会分裂计数。
  ⚠️ **口径与实测行为**：这是 **PV**，**每次页面重新加载都 +1**（刷新 10→11→12）；**站内改 hash 切视图不计数**（12→12，因为没有重新加载）；跨站跳走再**返回**（`back_forward`）也 +1（实测 12→13）。反过来说：装了拦截第三方脚本插件的访客**不会被计入** ⇒ 数字永远偏低，只能当趋势看。
  ⚠️ **上线初期的数字基本是我自己的测试噪声**（探接口 + 浏览器验收 + 上面那几轮刷新，合计 ~16）：因为计数键不带参数，我原以为用 `?probe=1` 能隔离测试，**实际没有隔离**，那些探测都落进了同一个桶。真实读者数据从 2026-09-17 之后开始。
- **v28：计数去重 + 移到首页显眼处（2026-09-17）**——用户接着提两点：「能不能优美简洁地避免频繁刷新就频繁计数」「浏览次数放在显眼的地方」。
  ① **去重**：`localStorage['fw-pv-v1'] = {v,t}`，**1 分钟内只上报一次**（`TTL = 60 * 1000`）；窗口内重载**根本不发外部请求**、直接渲染缓存值 ⇒ 自己刷 20 次也只 +1。窗口长度是权衡过的：太长（如 24h）会让数字「整天不动」、看起来像坏了；太短又回到刷一次涨一格。**用户最终指定 1 分钟**（我原本取 30 分钟，已抄回）。缓存不可用（隐私模式/禁存储）时 fail-open，退回每次都上报。
     ⚠️ **本条已于 2026-09-19（v33）被用户要求整段移除**，此处仅存历史；配套的「去重窗口内重载」断言也一并换成「取到值后显示累计次数」。
     ✅ **窗口边界实测**（localhost 数 `performance` 里的 busuanzi 请求）：清缓存首载 1 请求/值 376965 → 窗口内重载 0 请求/值不变 → 再重载 0 请求 → **把缓存时间改成 61 秒前再载：1 请求、值 +1=376966**。
  ② **位置**：从页脚挪到**首页 hero 统计行末**（`#stat-views`：`<b>1,234</b><span>次浏览</span>`，复用现有 `.stat` 金色衬线大字号样式，不新增 CSS）。页脚恢复原样（只留「最后更新」），**不做两处重复展示**。默认 `display:none`，取到值才显示。
  ③ **顺手简化**：不再引不蒜子那支 1.9KB 的 `busuanzi.pure.mini.js`，**自己发 JSONP** 并显式 `referrerPolicy='no-referrer-when-downgrade'`（默认策略只发 origin → 服务端拿不到路径，计数会退化成站点级）。顺带**少一个网络请求**、也不再依赖它的 `busuanzi_value_*` DOM 约定。
  ④ **验收 29 → 30 条**：删掉两条旧断言（容器隐藏 / 本地不注入），换成更有信息量的三条 —— 「首页浏览统计默认隐藏且本地未上报」、**「去重窗口内重载：显示缓存值且不重复上报」**（写缓存→重载→断言显示 `1,234` 且 `script[src*=busuanzi]` 仍为 0，这才是「反复刷新不叠加」的真实证据）、「统计位显示后两套视口仍无横向溢出」（**布局断言必须在统计位可见的状态下补测**，否则测的是隐藏态的假绿）。30/30 通过。
      ⚠️ `file://` 下 `localStorage` 在 Chrome 里**是可用的**（实测 `setItem` 成功），所以这条缓存断言能在默认的 `file://` 验收里跑；换浏览器/加 `--incognito` 之类要重测。
  ⑤ **本地实测**（localhost + `?stats=1`，用 `performance.getEntriesByType('resource')` 数请求）：首载 1 次 busuanzi 请求 + 写缓存 → 第 2、3 次重载均 **0 请求**、数字不变、无控制台报错。
     ⚠️ **顺序铁律**：必须**先转 public 再 push**。反了的话线上会立刻出现指向私有仓库的 GitHub 链接与「前往仓库」按钮，访客点到就是 404。
- **v27：反馈与勘误统一改走 GitHub Issues（2026-09-17）**——用户指令「所有反馈、勘误的都到 GitHub issue 中去」，取代原先的主站资料页评论区（`bunnychen.top/docs/Other/fanren-xiuxian/#__comments`）。
  ① **四处入口全改**（漏一处就自相矛盾）：hero `.project-links` 的「勘误与反馈」按钮、收录说明的 `.home-note`、页脚 `.note`、`.img-note` 图片准确性声明末尾（**新增** —— 该声明本就写着「个别角色甚至可能出现错配」，最该配一个勘误入口）。指向 GitHub Issues（v28 已改为直接给 `issues` 列表页，不再经 `/new/choose` 模板选择页）。
  ② **保留的引用**：数据来源板块的「原著逐章分析资料库 → 本站《凡人修仙传》资料页」**不动** —— 那是**素材来源**，不是反馈入口。README 同处改为「仍是首页文案素材来源，但已不再是反馈入口」。
  ③ **新增 `.github/ISSUE_TEMPLATE/`**：`config.yml`（允许空白 issue + 两条 contact_links）、`errata.yml`（勘误表单：条目名/板块/问题类型/现状/应有/依据 6 个字段 + 线上版本确认）、`site-bug.yml`（站点问题：描述/复现步骤/环境/截图）。三份 YAML 已用 `python3 -c "yaml.safe_load"` 逐个校验通过。
     ⚠️️ 原计划给模板配 `labels: ["勘误"]` / `["站点"]` —— **已作废**：用户表示不需要 label，v28 已从模板移除。
  ④ **验收 26 → 27 条**：新增「反馈入口统一指向 GitHub Issues（页面无主站评论区旧链接）」，断言 `a[href*="__comments"]` 为 0 且 Issues 入口 ≥ 3，专门防旧链接在改文案时爬回来。
- **v28：公开文案去 AI 味 + 反馈链接改指 issues 列表（2026-09-17）**——用户两条指令：「所有公开的文档、文案文字都不要有 AI 味，言简意赅」「不用什么 label，直接到 issues 页面就行」。
  ① **反馈链接全部改指 `github.com/.../issues`**（hero / 收录说明 / `.img-note` / 页脚 / README / NOTICE），不再经 `/new/choose`；页脚原本并列的「提交」与「查看已提交」两个链接指向同一页，已合并为一句。
  ② **issue 模板去掉 `labels:`**（errata / site-bug），不需再建标签。模板本身保留 —— 点「New issue」时仍能引导填写。
  ③ **真实问题不是词藻，而是重复**：剧透提示 2 次（收录说明第1条与第3条）、「点开卡片展开详情…不剧透」2 次（灵兽/灵草）、Apache 2.0 在页脚提 2 遍（「源码已开源」+「©」两行）、「跨篇重复收录」4 次（hero / hero kicker / v-chars kicker / 卡片）。已逐处去重。
  ④ 删掉/改写的填充句：「六大板块，点击进入」（卡片本身就是入口，整行删除）、「本站持续更新中：」（冒号腔）、「持续整理维护中」、「大量参考以下来源，特此注明」→「文字与图片来源如下」、「欢迎取用、镜像与改进」（三段排比）→「可自由取用与再分发」、「仙侠巨著 / 全档案」等营销定语。
  ⑤ 页脚由 5 条 note 合并为 4 条；`src-list` 6 条来源逐条去冗（「权威交叉核验来源」→「交叉核验来源」、「仅供回忆辅助，不保证与官方形象完全一致」→「不保证与官方形象一致」）；首页 6 张入口卡片同步收紧——「40 条灵兽灵虫档案」「65 条法器法宝档案」这类以标题重复开头的写法改为直接给条目数（40 条 / 65 条），删「一图看懂全书脉络」。
  ⑥ **未动**：「为什么做这个网站」与「问道自述」两段 —— 那是用户本人的文学化文案，与主站资料页**互为镜像**（见 §9），不属于 AI 味候选，改它会同时破坏镜像关系。
  ⚠️ **教训（断言设计）**：本次验收一度 26/27 —— 开源卡片断言钉死了原文「不在该许可范围」，文案改成「不在授权范围」就误报。已改为只查**语义标记**（点名 `Apache` + 出现「第三方」）。**断言不要绑定具体措辞**，否则它会变成改文案的阻力。
- **v29：接入 ECharts 双图（2026-09-18）**——用户拍板「只使用人物关系图谱和旭日图，不要省略，核心角色都要有体现」。
  ① **选型过程**：先研究了 ECharts 官方 examples 全部分类（graph/sankey/themeRiver/sunburst/pictorialBar/heatmap/chord/GL 等），又看了上一轮 demo（力导向关系图、境界 Bar Race、旭日图）。用户三轮收敛：①"除了 Bar Race 和旭日图还不错，其它太普通，发挥想象力，不要只考虑人物"；②否定掌天瓶闭环/韩立百宝箱（"太局部，要宏观的"）；③最终定"人物关系图谱 + 旭日图"。
  ② **两张图定位**：
     - **首页旭日图** `#chart-sunburst`：中心"全书人物"→ 外圈六篇章 → 内圈各篇前 6 大势力 + 其他。宏观视角，一眼看六卷篇幅分布与势力格局。
     - **人物图谱力导向图** `#chart-graph`：基础名级被引 ≥ 3 的 34 个核心角色（韩立 254 被引最大居中），节点大小 = REF_SCORE，颜色 = 首次登场篇章，连线 = REFS 互引。
  ③ **数据来源**：直接复用主页面运行时的 `INDEX` / `REFS` / `KEYS_BY_BASE` / `REF_SCORE` / `CHAPTERS` / `DATA` / `baseName` / `ENTRY_BY_KEY`，不另造数据集。⚠️ **坑**：`INDEX` 条目只有 `lib/key/name/sub/tag/text`，**不含 camp 字段**——旭日图统计势力必须遍历 `DATA[chapId]` 取 `c.camp`，不能从 INDEX 取。
  ④ **交互细节**：
     - **分批生长动画**：按篇章每 450ms 一批 `setOption` merge 节点+边，关系网"逐卷展开"，有过程感（用户要求"有时间线或者有过程，不然用户不知道还有筛选标签这个功能"）。
     - **滚轮不冲突**：`roam: 'move'` 只拖拽平移，禁滚轮缩放（`roam: true` 默认滚轮缩放会吃掉页面滚动）。
     - **节点点击跳转**：`gotoEntry` 在主 IIFE 内外部访问不到，改走 `location.hash = 'v-chars/' + key` 触发 hash 路由；跨篇同名选 REF_SCORE 最高的副本作主卡跳转目标。
     - **收纳按钮**：图谱区包在 `<details class="graph-fold" open>` 里，默认展开；点标题栏折叠后图不占纵向空间，下方人物卡直接上移；toggle 事件 `setTimeout(resize, 60)` 修正 canvas 尺寸。
  ⑤ **初始化时机（坑）**：脚本在 `</body>` 前，但 `window load` 之前 `echarts.init(el)` 时 canvas 尺寸为 0，只画出空圆环轮廓；必须等 `window load` 后再 `sync()`，并 `setTimeout(resize, 300)` 补一次。另外 `setOption` 必须传 `true`（notMerge），否则和默认空 option 合并后数据不进 series。
  ⑥ **体积**：`echarts.min.js` 1MB（v5.6.0），`overview-charts.js` 约 6.6KB。验收仍 30/30 通过——"静态资源无第三方请求"断言满足（echarts 是本地文件）。
- **v30：接入后的整理（复用 / 冗余 / 验收补课，2026-09-18）**——用户要求「整理优化代码，注意代码复用和简洁高效性，清理冗余代码和文件」。
  ① **修掉一处配色不一致（真 bug）**：`overview-charts.js` 里 6 个篇章色是 demo 阶段手抄的 hex，与页面收敛后的 `--cN` **只有 c1 对得上**（c2–c6 全错）。现改为从 `CHAPTERS[].color` 解析 CSS 变量名、运行时 `getComputedStyle` 取值 ⇒ 篇章名与配色都只剩一个来源，页面改色时两张图自动跟随。⚠️ canvas 读不了 CSS 变量，必须解析成具体色值。
  ② **去重与去冗余**：删掉 JS 注入 `<style>`（10 行字符串）；`legend.data` 与 `series.categories` 共用一个生成函数；`INDEX.filter(lib==='chars')` 两次全表扫描合一；`resizeAll()` 合并原先三处重复 resize；`revealByArc()` 用 `Set` 取代嵌套 `some()` 扫描（O(n²)→O(n)），并去掉冗余的 `itemStyle:{opacity:1}`（本就是默认值）与每批多跑一次的 `setTimeout`；主卡选取改 `reduce`，边去重 key 改用 `\u0000` 分隔（避开名字里可能出现的 `|`）。
  ③ **死代码变真元素**：`#graph-core-n` 在 HTML 里根本不存在（`if (nEl)` 兜底永不命中），折叠标题里的「34 位核心人物」是硬编码。现改为 HTML 里真有 `<span id="graph-core-n">34</span>`、初始化时由脚本写入实际节点数，并加断言「节点数 == 提示计数」防漂移。
  ④ **样式归位**：`.graph-fold` 一族从 JS 字符串搬进 `cultivation.css` 末尾的「概览图表」段；画布尺寸从内联 `style` 属性搬进同一段，并给 ≤760px 降档（460→380 / 540→420）—— 原先 540px 在 390px 宽的手机上比视口还高。
     ⚠️ 这里顺带**改了 §7 的一条老约束**：`cultivation.css` 原写「用户自加，不可修改」。第一版照办把样式写进 `index.html` 内联，结果是同一类样式劈成两处、更难维护 —— 用户拍板「约束如果弄巧成拙就修改」⇒ 改为**允许在文件末尾追加**，既有 `.cv-*` 规则仍原样不动。
  ⑤ **删冗余文件（-2.03MB）**：`dev/demos/echarts-demo/` 里有一份与 `public/javascripts/echarts.min.js` **SHA-256 完全相同**的 1.03MB 副本，以及 `build-demo.mjs` 生成的 1.06MB 自包含 `index.html`（一条命令可重建）。两者已删；`build-demo.mjs` / `index2.html` 改指 `public/javascripts/echarts.min.js` —— **全仓库只留一份库**。
  ⑥ **验收 30 → 32 条**：新增「旭日图：画布已渲染、六篇章齐全、人数合计 221、配色取自页面 --cN」与「关系图谱：画布已渲染、节点分批长齐且与页面提示计数一致、每个节点都能跳到对应卡片」—— 这两张图此前**一条断言都没有**。另加 helper `window.__until(fn, ms)` 轮询等分批生长完成，不用定长 `sleep` 拖慢验收。
  ⑦ 体积：`overview-charts.js` 262 → 252 行（行为等价；唯一的视觉变化是配色修正）。
- **v31：减重与系统测试（ECharts 按需包 / 图谱观感 / dev 入库，2026-09-18）**——用户点名三件事，并要求「所有处理完后系统测试画面、交互、响应式，都没问题再 push」。
  ① **ECharts 按需构建**：全量包 1006KB（gzip 327KB）→ 只打 graph + sunburst + tooltip/legend + LabelLayout + canvas 渲染器 ⇒ **527KB（gzip 179KB）**。入口 `dev/tools/echarts-entry.js`、用官方 npm 包 + esbuild 一次性打包（仓库本身仍零构建零依赖）。Apache-2.0 的版权/许可头拼在产物开头，`NOTICE` 新增「第三方组件」段（§4 要求随分发保留声明）。
  ② **图谱观感**：① 标签重叠 → `labelLayout: { hideOverlap: true }`（需注册 LabelLayout 特性，定制包里已含）；② 边缘节点贴边被裁 → 力导向的落点**不受** `top/left/right/bottom` 约束，改用 `zoom: 0.86` 整体留白 + `bottom: 56` 给图例让位；③ 旭日图内外圈同色 → `levels` 把内圈势力压暗（opacity 0.7）并与外圈用边框分开；root 标签（「全书人物」）挤在中心洞里读不了，已隐藏。
  ③ **dev/ 部分入库**：`.gitignore` 由 `dev/` 改为 `dev/*` + 放行 `Agent.md` / `_review.md` / `tools/` / `_image-slim-report.json`（`_backup/` `demos/` `watermark.svg` 仍仅本地）。入库前清掉唯一一处本机路径（`/Users/bunnychen/Downloads/…` → `~/Downloads/…`）。
  ④ **验收 33 → 35 条**：新增「图谱节点可点击：中心节点 → 深链 + 对应卡片展开」与「图谱折叠再展开：canvas 尺寸自动恢复」。
     ⚠️ 提交后连跑验收出现过 **34/35 波动**：该断言在「分批生长刚到 20 个节点」时就去扫节点坐标，而力导向还在动，点下去时节点已经移开。已改为等**全部节点并入**（`data.length === graph-core-n`）再 `sleep(1500)` 等布局收敛 —— 连跑两次稳定 35/35。
     ⚠️ 写这两条踩了三个坑：① `JSON.parse(await evaluate(\`…\`))` 的收尾括号连写错三次（应为 `})()` + 反引号 + `))`）；② **不能假设几何中心就是节点** —— 实测中心点没命中（力导向质心≠几何中心），改用 `zr.handler.findHover()` 环形扫描找真正命中节点的点；③ zrender 里图谱节点的元素类型是 **`path`**（连线是 `ec-line`、标签是 `tspan`），不是想当然的 `symbol`。改用真实鼠标事件（mousemove→mousedown→mouseup）后跳转正常 —— 说明**真人点击本来就是好的**，错的是断言探测点。
  ⑤ **系统测试 19 项全过**（临时 CDP 脚本）：10 档宽度 360→1600px × 七视图无横向溢出；图表高度断点（>760px 为 460/540，≤760px 为 380/420）与 canvas 跟随容器；键盘搜索面板（`/` 唤起 → 输入「韩立」有结果 → `Esc` 关闭）；桌面/移动三张截图人工核对。
  ⑥ 体积：`echarts.min.js` 1006 → **527KB**；`overview-charts.js` → 258 行。
- **v32：人物生平 s 字段全量补全（148 条过短条目，2026-09-18）**——用户指令「搜官方/权威资料，把过短的人物介绍补全」。
  ① **范围**：只扩写六个人物数组（qixuanmen/huangfeng/luanxing/dajin/lingjie/xianjie，共 221 条）的 `s` 字段；BEASTS/HERBS/TREASURES 三库不碰。基线长度分布：<40 字 **148 条**、40–80 字 54 条、≥80 字 19 条。本次把 **148 条全部补到 ≥60 字**（实测 77–169，多数 90–150）。
  ② **分片并行**：按篇切成 7 片（七玄+黄枫 19 / 乱星 15 / 大晋上 17 / 大晋下 24 / 灵界 32 / 仙界上 21 / 仙界下 20），各片子代理只做「检索权威素材 + 写文案」，产出 `dev/_shards/shardA–G.json`（`{chapter,n,s,sources,uncertain}`），**不碰 index.html**；由集成脚本按 `chapter+n` 逐行字符串级替换 `s:"..."`，148/148 命中、0 遗漏。
  ③ **素材红线**：以起点《凡人必备手册》第二版（核心人物/次要人物条目）为主，起点原著章节、百度/抖音百科、B站专栏为辅；每条带 sources。合并条目双人全覆盖（白梦馨·欧阳师弟、龙夫人·摩鸠大师、星宫双圣、韩家父母·三叔·小妹、狮禽兽·木魁）。`uncertain=true` 共 15 条（舞岩、钟吾郎、公孙杏、程天坤、宋玉、昌正、玄武霸皇、血光、涅槃、天东商号方夫人、张奎、精炎童子、魔光、沙心、石空墨），均以「原著未明/未再登场」收尾，不硬凑。
  ④ **硬性格式**：新 `s` 一律无 ASCII 双引号（用「」『』）、无换行、无反斜杠；改后内联主脚本 `node --check` 通过。
  ⑤ **验收**：`verify.mjs` **35/35 全绿**（本机无 Chrome，用 Edge 作 CHROME_PATH）。⚠️「图谱中心节点→深链」断言首跑连挂 34/35，而改动前基线（v33）35/35——排查确认**与本次文案确有关联**而非纯抖动：扩写后互引变密，图谱核心节点 34→49、连线 96，力导向收敛时间变长，测试固定 1500ms 等待不足导致扫描点漂移点空（真人点击正常，探针实测点击深链成功）。已在 dev/tools/verify.mjs 将该断言收敛等待 1500ms→4000ms（v31 同类时序问题的同款修法），修复后连跑稳定 35/35。
  ⑥ **存疑/待办**：① 乱星篇「星宫双圣」文件 `n/t` 作「凌啸天」，权威资料男性双圣实为「凌啸风」、温青系六道极圣之妹（文案已按准确口径写，未改 `n`，避免破坏全站互引）——如需正名另开一轮；② 孙二狗 `ev` 标「七玄门杂役」与原著「嘉元城四平帮小头目」有出入，文案按原著写、未改 ev。备份 `dev/_backup/index-v33.html`（改动前快照）。
- **v33：移除计数去重，回到最简单的取数（2026-09-19）**——用户指令「移除这个一分钟的功能，直接用最简单的计算」，指名 v28 的 1 分钟去重窗口。
  ① **删掉去重**：`localStorage['fw-pv-v1']`、`TTL = 60 * 1000`、以及「缓存命中 ⇒ 只显示缓存值且不上报」那条分支全部移除；现在**每次载入都直接上报一次并显示接口返回的 `page_pv`**。刷新即 +1，这是不蒜子的 PV 语义。
  ② **保留（与去重无关，别顺手删）**：真实域名判定（`file://` 与 `localhost/127.0.0.1` 仍**不发起**，本地想看加 `?stats=1`）、自己发 JSONP + 显式 `referrerPolicy='no-referrer-when-downgrade'`、`#stat-views` 默认 `display:none`、取到值才显示。
  ③ **文案同步**（漏一处就自相矛盾）：`<head>` 注释块去掉「同一浏览器 1 分钟内只计一次」；`#stat-views` 的 `title` 改为「累计浏览次数（不蒜子 page_pv）」（原文案承诺的行为已不存在）。
  ④ **验收仍 35 条**：删掉「去重窗口内重载：显示缓存值且不重复上报」（写 localStorage → 重载 → 断言缓存值，新实现下必挂），换成「**统计位取到值后显示累计次数（千位分隔）**」—— 直接按「接口取到值」后的 DOM 状态模拟，不再依赖 localStorage；紧随其后的「统计位显示后两套视口仍无横向溢出」照旧（布局断言仍须在统计位**可见**时测）。实测 **35/35 通过**（本机无 Chrome，用 Edge 作 `--chrome`）。
  ⑤ **日期同步**：页脚「最后更新」/ `<head>` 注释块 / JSON-LD `dateModified` / `sitemap.xml` `lastmod` 一律 **2026-09-17 → 2026-09-19**（§7「最后更新」条；2026-09-20 起这四处改由 `dev/tools/stamp.mjs` 在部署时统一刷新，当时的日期同步记录仅存史）。
  ⑥ 体积：`public/index.html` 2453 → **2444 行**、350501 → **349968 字节**（-9 行 / -533B）；备份 `dev/_backup/index-v34.html`（改动前快照）。
  ⚠️ **不要再把去重加回来**：用户明确要「最简单」，v28 那套还要权衡窗口长短、隐私模式下行为还不一致，已否决。

- **v34：人物故事线深度补全（221 条 s 字段二次深化，2026-09-20）**——用户指令「部分角色经历和故事线不够完整，如思月描述很局限，没写出其父亲及早期经历，其它的也一样，请进一步完善」。
  ① **范围**：只深化六个人物数组共 **221 条**的 `s` 字段；BEASTS/HERBS/TREASURES 不碰，其它字段（n/t/r/e/img/rel/camp/race/ev）一律不动。这是继 v32（把 148 条过短 s 补到 ≥60 字）之后的**二次深化**——不再是简单拉长，而是每条按四要素补全：出身背景（家族/父辈/师承）→ 早期经历（登场前轨迹）→ 本篇关键事件脉络（与韩立交集起因-经过-结果）→ 结局呼应。
  ② **分片并行**：按篇切 5 片——人界早期（七玄 16+黄枫 29=45）/ 乱星 32 / 大晋 55 / 灵界 39 / 仙界 50。各片子代理只做「联网查权威素材+写文案」，产出 `dev/_shards2/shard1–5.json`（{chapter,n,s,sources,uncertain}），**不碰 index.html**；由集成脚本 `dev/_shards2/_integrate.mjs` 按 chapter+n 逐行字符串级替换 s:"..."（字段顺序不固定，按字段名定位；每次替换后重算块偏移），**221/221 全部命中、0 遗漏**。
  ③ **长度分布（深化后）**：<150 字 **80 条**（多为原著着墨极少的冷门配角，以可查素材为上限并标「原著未详/此后未再登场」，**不硬凑**）；150–250 字 **91 条**（一般角色）；250–450 字 **50 条**（重要角色：韩立六篇、南宫婉、紫灵、元瑶、古或今、轮回殿主、魔主、弥罗老祖、王蝉、青元子、马良、蟹道人等）。
  ④ **标杆达成**：用户点名的文思月（乱星 idx28）由 132 字深化到 **440 字**——补出父亲文樯是韩立初至乱星魁星岛的引路人（一生止步筑基中期）、母亲为妙音门女修产后病故、「葡萄仙子」称号来历（交换会手误被戏称）、两度婚姻与守寡、虚天殿途中韩立念旧相救、田琴儿龙吟之体求医、天星城哭求、酷似辛如音被收徒全脉络。
  ⑤ **联网补出的关键出身线**：墨居仁（岚州惊蛟会创办人「鬼手」）、厉飞雨（原名厉剩儿、父七玄门内门弟子历练而死）、南宫婉（12 岁冰属性天灵根入掩月宗、南宫阙抚养）、董萱儿（娘胎被云露老魔种「奕梦诀」）、辛如音（元武国龙吟之质错生女身）、紫灵（魁星岛之变）、大衍神君（千竹教万年傀儡）、冰凤（天凤真灵血脉）、南陇侯（苍坤上人后人）、马良（九元观道祖嫡系、追掌天瓶下界）、青元子（人界玄剑门出身自创剑诀）、蟹道人（前世魔域积鳞空境魔君石空解、遭魔主与厄脍背叛封傀儡百万年）、魔主石空鱼与蟹道人石空解为胞兄弟、石穿空实乃石空墨之子被石空鱼豢养、金童前世即渠鳞道祖。
  ⑥ **事实冲突（待用户定夺，未擅改字段）**：乱星篇文思月现有 `ev` 写「结丹（妙音门门主之女）」，但权威信源（抖音百科文思月词条、起点问答）一致记载**文樯实为韩立初到乱星的散修引路人、止步筑基中期，其母亲才是妙音门女修**——s 文案已按信源实写，与 ev 字段「门主之女」相悖。用户确认「修正」后，**ev 已改**为「结丹（母为妙音门女修，父为散修文樯）」，与 s 口径一致（改后 verify.mjs 复验 35/35 全绿）。同 v32：孙二狗按原著写「嘉元城四平帮小头目」（未沿用 ev 的「七玄门杂役」）；星宫双圣 s 写「凌啸天（一作凌啸风）」，未改 n。
  ⑦ **硬性格式**：新 s 一律无 ASCII 双引号（用「」『』）、无换行、无反斜杠；集成后内联主脚本 node --check 通过。
  ⑧ **验收**：verify.mjs **35/35 一次全绿**（本机无 Chrome，用 Edge 作 CHROME_PATH）。⚠️ 扩写后互引变密，图谱被引数随之上升属预期；本次未再触发中心节点点击断言的时序抖动。
  ⑨ 体积：public/index.html 349968 → **404971 字节**（+55KB，全部为 s 文案深化）。改动前快照即已存在的 dev/_backup/index-v34.html（349968）。

- **v35：补录「文案提及但无独立条目」人物 30 个（221→251，2026-09-20）**——用户指令「文思月她爹文樯也补个条目，其它文案里提到却没有独立页的人物一并扫出来补全」。
  ① **范围**：只在六个人物数组**末尾追加** 30 条新对象，已有 221 条的任何字段（含文思月、紫灵等现有文案）一字不动；BEASTS/HERBS/TREASURES 不碰。每条新对象单独一行、两空格缩进，字段顺序固定 n/t/r/ev/e/img/s/rel/camp/race。
  ② **按篇章增量**：七玄门 +1（贾天龙）→ **17**；黄枫谷 +6（王天古、李缨宁、陈巧天、燕云山、金南天、南宫阙）→ **35**；乱星海 +5（文樯、公孙云、卓如婷、极炫、云天啸）→ **37**；大晋 +7（苍坤上人、白瑶怡、天风真君、狂沙上人、宋大先生、富成、常芷芳）→ **62**；灵界 +2（轩九灵、何康）→ **41**；仙界 +9（柳金玲、陶羽、重銮、木延、禾泽、云霓、白素媛、陆雨晴、墨雨）→ **59**。合计 **221→251**。
  ③ **被判定重复/不收录而剔除**：九元道祖（=现有条目「李元究」）、渠鳞道祖（=现有「金童·渠鳞」，v34 已点出金童前世即渠鳞道祖）；房坤（=现有「房宗主」）；紫灵之父（原著未具名，妙音门门主实为其母）。另：补扫中纯称号/无本名者按标准不收——骷髅仙、蓝鬼婆、空玄丹士、黄尘三煞等仅在文案中作背景提及，不立独立页。
  ④ **与初始线索的事实校正**：王天古实为王蝉**二伯**（鬼灵门门主乃其兄王天胜，线索误作王蝉之父/门主，s 已按正写）；苍坤上人实为**五千年前**天南第一狂修（线索误作「约两百年前」）；南宫阙为**凡人动画官方定名**，原著仅称「掩月宗大长老/南宫婉师姐」，条目标 uncertain；文樯「开护岛大阵牺牲」系**动画原创**，原著实为妻产后怪病、本人一生止步筑基中期病故（s 已注明）。
  ⑤ **配图处理**：30 人均无经核实的可直链官方立绘，`img` 一律留空字符串走页面占位 div（`c.img ? <img> : 占位`），**不张冠李戴**用别的人物图；如需配图后续另立。由此页面 `img[src]` 集合不变（360 张），未触发缺图/裂图断言。
  ⑥ **硬红线 + 自检**：新条 s/t/r/ev/e/rel/camp/race 无 ASCII 双引号（用「」『』）、无换行、无反斜杠；集成脚本 `dev/_v35_apply.mjs` 按 `DATA.<arr> = [` 做字符串感知的括号配平定位 `]`，把原末对象 `}` 改 `},` 后追加。独立自检 `dev/_v35_check.mjs` 复核：六数组人数 17/35/37/62/41/59、总 251；各数组内部 n 无重复（韩立 6 篇等跨篇重复收录为既有设计，非本次引入）；30 个新名各只出现一次；每条含全部 10 字段；内联主脚本 `node --check` 通过。
  ⑦ **验收脚本同步**：`dev/tools/verify.mjs` 仅改因人数增加而必须同步的常量——四库计数 `[221,40,64,65]→[251,40,64,65]`、核心圈 `core.all === 221→251`、旭日图 `sun.people === 221→251`、黄枫谷筛选 `filter.cards === 29→35`（对应文案同步），其它断言逻辑一律未动。
  ⑧ **验收**：verify.mjs 最终 **35/35 连续三次全绿**（本机无 Chrome，用 Edge 作 CHROME_PATH）。⚠️ **修正子代理记录**：新增 30 节点后图谱变密，「中心节点→深链」断言（扫描前 250ms + 半径 140px）实际**间歇失败**（独立复跑 3 次中 2 次 34/35），非一次全绿；已将该处扫描前等待 250→2000ms、扫描半径 140→260px（容忍力导向下中心节点漂移），改后连续 3 次 35/35 稳定，等待参数与其余断言未再动。
  ⑨ 体积：public/index.html 404992 → **431582 字节**（+26590B，全部为新增条目）。改动前快照即已存在的 dev/_backup/index-v35.html（404992）。

- **v36：为 v35 新增 30 人补官方配图（14 人落图，16 人维持占位，2026-09-20）**——用户指令「为已下载好的 14 张人物图更新对应 img 字段，只改 img，其它一律不动」。
  ① **目标**：v35 新增的 30 人当时 `img` 一律留空走占位 div；本轮为其中已找到经核实官方形象的 14 人补 `img:"<文件名>"`，其余 16 人维持 `img:""`。
  ② **成功配图 14 人**（每人一行：人物 → 文件名 → 来源，sourceUrl 取自 `dev/_v36-img-batch1/2/3.json`）：
     - 贾天龙 → `jiatianlong.webp` → 凡人动画年番官方角色定妆卡（快懂百科收录，野狼帮帮主半身像）— https://aka.doubaocdn.com/s/2XKgRZG50Y
     - 王天古 → `wangtiangu.webp` → 凡人动画年番剧集截图（鬼灵门元婴长老、王蝉二伯，蓝袍长须）— https://aka.doubaocdn.com/s/579iYUAuBn
     - 李缨宁 → `liyingning.webp` → 凡人动画年番剧集截图（bilibili 独播，墨玉珠之女/化刀坞，已裁字幕条）— https://aka.doubaocdn.com/s/AD0d5hiWXq
     - 南宫阙 → `nangongque.webp` → 凡人动画年番剧集截图（掩月宗大殿官方模型，额间印记蓝袍）— https://aka.doubaocdn.com/s/jWB5PeuqcZ
     - 文樯 → `wenqiang.webp` → 官方动画《凡人修仙传·初入星海》角色定妆卡（魁星岛六连殿执事、文思月之父，百科收录）— https://www.baike.com/wikiid/7376422416489627658
     - 云天啸 → `yuntianxiao.webp` → 官方动画年番正片截图（温天仁代理人/魔修，洞窟场景裁主角像）— http://m.toutiao.com/group/7467549388445975077/
     - 苍坤上人 → `cangkunshangren.webp` → 官方动画正片截图（五千年前天南第一狂修，长须束发金环绿纹袍）— http://m.toutiao.com/group/7605118518597665321/
     - 白瑶怡 → `baiyaoyi.webp` → 官方动画正片截图（小极宫外事长老，白衣高冠宫装女修）— http://m.toutiao.com/group/7615504211240862254/
     - 轩九灵 → `xuanjiuling.webp` → 凡人修仙传 3DMMO 手游官方立绘（标注「轩九灵」，蓝衣金饰持剑）— http://m.toutiao.com/group/7512307099032879654/
     - 何康 → `hekang.webp` → 凡人动画官方截图（搜狐视频，青绿道袍长须真仙/太乙监察仙使）— https://tv.sohu.com/v/dXMvMzQ5MzExMzcyLzQyMjM3MDQyNS5zaHRtbA==.html
     - 陶羽 → `taoyu.webp` → 凡人仙界篇动画截图（B站视频封面，盔甲华服金仙）— https://www.bilibili.com/video/BV1pF411S7vK/
     - 云霓 → `yunni.webp` → 凡人仙界篇动画官方截图（搜狐视频，黄衣女道主）— http://tv.sohu.com/v/dXMvMzQ5MzExMzgzLzQ0MTE3NDUyMi5zaHRtbA==.html
     - 白素媛 → `baisuyuan.webp` → 凡人动画官方形象（微信公众号发布的角色壁纸，白衣月华仙体）— https://mp.weixin.qq.com/s?__biz=MzIyNTg2NjMzOA==&mid=2247490945&idx=2&sn=db2c565c308ec741ccd3a6a19ed6a56f&scene=0
     - 陆雨晴 → `luyuqing.webp` → 凡人修仙传游戏官方立绘（新浪文章配图，红衣弓箭手女修）— https://k.sina.cn/article_6471119694_181b5734e00100c2w5.html
  ③ **未找到 16 人（维持占位图，img 仍为空串）及原因**：
     - 陈巧天：多次检索仅命中其妹陈巧倩画面，本人无官方动画形象或立绘可核实。
     - 燕云山：燕家堡弧仅见女儿燕如嫣及一名朴素白须老者，无称号/无定妆图，无法确认老者即燕云山本人。
     - 金南天：仅命中通用 AI 绘风「凡人」配图，无官方动画/官方立绘可核实。
     - 公孙云：青灵门掌门，检索仅命中其女公孙杏的形象，本人在动画与游戏中无独立官方定妆。
     - 卓如婷：妙音门右使，动画中其与文思月的师徒关系已被删；网络绿衣形象均为 AI 二创/图库转载，无官方定妆截图。
     - 极炫：玄骨上人弟子，纯回忆/传承背景人物；检索结果均为其师玄骨上人本人（蓝袍，第094集），无独立官方模型。
     - 天风真君 / 狂沙上人：方尖山二魔之一，纯文字配角，动画/游戏/百科均无独立形象图。
     - 宋大先生：泰阳门长老，纯文字配角，无独立官方形象图。
     - 富成：九幽宗人物、昆吾山篇同行者；检索仅命中昆吾山场景/妖物图，无本人官方形象。
     - 常芷芳：九幽宗黑衣女修；仅命中带诗词水印的粉丝二创视频封面，非官方定妆。
     - 柳金玲 / 重銮 / 木延 / 禾泽 / 墨雨：均为仙界篇角色（石空墨之妻、伏凌宗金仙、真言门大师兄/五弟子、灰界太乙灰仙），动画尚未改编，搜索无官方形象图。
  ④ **红线声明**：本轮**未使用任何 AI 生成图**（沿用 v12 起用户否决项），**未张冠李戴**把他人画面错配给本人；14 张图均落盘 `public/assets/` 并经 webp 魔数校验（前 12 字节 `RIFF....WEBP`、VP8 chunk）与体积校验（7336–60124 字节，均 >5KB 下限）。
  ⑤ **改法（精确最小改动）**：新增 `dev/_v36_apply.mjs`，按 `n:"<人名>"` 逐行定位该人物所在行（14 人各只命中一行），仅把该行内唯一一处 `img:""` 替换为 `img:"<文件名>"`；n/t/r/ev/e/s/rel/camp/race 一字未动，仍为单行对象、两空格缩进，未引入 ASCII 双引号/换行/反斜杠。脚本内括号配平重新提取六数组并复核：人数仍为 17/35/37/62/41/59=**251**，14 人 img 已非空且各自指向正确文件，其余 16 人仍为空串。
  ⑥ **校验**：内联主脚本经 `dev/_shards2/_extract-inline.mjs` 提取拼临时文件后 `node --check` **通过**；14 个新引用文件均在 `public/assets/` 且为有效 webp；`dev/tools/verify.mjs` **未改动任何内容**（图谱等待/半径参数保持 v35 调好的值，未回退）。
  ⑦ **验收**：`$env:CHROME_PATH=...msedge.exe; node dev/tools/verify.mjs` 最终 **35/35 通过**（本机无 Chrome，用 Edge）。新增 14 个 img 引用触发的「图片引用无缺图（页面引用 374 张 / assets 388 张）」与「全部 374 张引用图都能解码加载」两条断言均通过。
  ⑧ 体积：public/index.html 431582 → **431779 字节**（净增 +197B，即 14 个文件名的长度差）。改动前快照即已存在的 dev/_backup/index-v36.html（431582，勿删勿覆盖）。

- **v37：再攻坚 16 个占位人物，新配 2 人（陈巧天、卓如婷），14 人维持占位（2026-09-20）**——用户指令「把本轮新找到的 2 张人物图写入 img 字段，跑验收，写 v37 日志，只改 img」。
  ① **目标**：按用户指定的图源清单（百度图片 / 必应 / 花瓣 / B 站专栏 / trace.moe / 识图反查等）对 v36 仍留空的 16 个占位人物**逐人重新攻坚**，只把核实到官方正片形象的写入 `img:"<文件名>"`，其余维持 `img:""` 走占位 div。
  ② **本轮新配 2 人**：
     - 陈巧天 → `chenqiaotian.webp`（public/assets/，20282B）→ 来源：坠魔谷篇正片帧，米白袍陈家男修（陈巧倩之兄）。
     - 卓如婷 → `zhuoruting.webp`（public/assets/，20418B）→ 来源：妙音门篇正片帧，绿衣金饰右使。⚠️ **纠正 v36 旧误判**：v36 条目曾记「动画将此角色删去 / 师徒关系已被删」，本轮在妙音门篇正片帧中重新核到其独立可辨形象，v36「动画已删该角色」的判断作废。
  ③ **经逐人 10+ 渠道检索后仍无官方形象、维持占位的 14 人及原因**：
     - **大晋篇未播**（年番现播慕兰之战 ep177–228，韩立尚未入大晋，制作组未放出建模）：天风真君、狂沙上人、宋大先生、富成、常芷芳；
     - **仙界篇未动画化、官方手游仅人界篇、漫画未到**：柳金玲、重銮、木延、禾泽、墨雨；
     - **动画仅他人画面 / 二创或真人剧非凡人动画**：燕云山（仅真人剧 + AI）、金南天（未上映电影《瀚海迷踪》）、公孙云（仅其女公孙杏建模）、极炫（正片无独立可辨帧，图搜全为其师玄骨）。
  ④ **红线声明**：均未用 AI 生成图、未错配；特别提示 `public/assets/` 中 `tianfeng.jpg` 为「天凤」（真灵），**非**凡人「天风真君」，本轮未误用。
  ⑤ **改法（精确最小改动）**：新增 `dev/_v37_apply.mjs`，按 `n:"陈巧天"` / `n:"卓如婷"` 定位所在行（各只命中一行），仅把该行内唯一一处 `img:""` 替换为 `img:"<文件名>"`；n/t/r/ev/e/s/rel/camp/race 一字未动，仍为单行对象、两空格缩进，未引入 ASCII 双引号 / 换行。改后重新提取六数组复核：人数仍 17/35/37/62/41/59=**251**，陈巧天、卓如婷 img 已非空，其余 14 人仍为空串。
  ⑥ **校验**：内联主脚本经 `dev/_shards2/_extract-inline.mjs` 提取后 `node --check` **通过**；两个新引用文件均在 `public/assets/` 且魔数为 `RIFF....WEBP`（20282B / 20418B）；`dev/tools/verify.mjs` **未改动任何内容**（图谱等待 / 半径参数保持 v35 调好的值）。
  ⑦ **验收**：`$env:CHROME_PATH=...msedge.exe; node dev/tools/verify.mjs` → **35/35 通过**。
  ⑧ 体积：public/index.html 431779 → **431811 字节**（净增 +32B，即两个文件名长度差）。改动前快照即已存在的 dev/_backup/index-v37.html（431779，勿删勿覆盖）。

- **v38：页面「最后更新」改为部署时自动注入，不再手写（2026-09-20）**——用户指令「主页是否有可能直接读取 GitHub 更新时间或者一些其它信息，这样就不用手动写更新时间了」。
  ① **背景**：页面上四处日期全是手写，且已经漂移 —— 导航写 `2026-09-17`、页脚与头注释写 `2026-09-19`，同一份交付物两个说法（四处 = 头注释 / JSON-LD `dateModified` / 导航栏 / 页脚）。
  ② **方案**：新增 `dev/tools/stamp.mjs`（零依赖，`execFileSync` 调 git），取 `git log -1` 的 `%cs`（提交日期）+ `%s`（提交说明首行，压平 → HTML 转义 → 截断 56 码点），一次改写 4 处日期 + 页脚 `.stamp-note` 里的提交说明 + `public/sitemap.xml` 的 `<lastmod>`（用户选定「日期 + 提交说明首行」，未要 sha/Star 数）；`deploy.yml` 在 `actions/checkout` 之后、`upload-pages-artifact` 之前跑 `node dev/tools/stamp.mjs --write`，改的是 runner 工作区副本，**不进 git**。
  ③ **不走运行时 GitHub API**（用户二选一后拍板）：`api.github.com` 国内经常超时、未认证 60 次/小时/IP；静态注入零新增请求（「静态资源 0 第三方请求」红线不动）、关掉 JS / 爬虫抓取 / 另存本地都正确，JSON-LD 也不再依赖 JS 执行。
  ④ **防静默失效**：6 条锚点各自要求「在目标文件集合里恰好命中 1 次」（命中 2 次=页面里有两处同形文本、0 次=锚点被改没了），否则整体报错退出且不写任何文件 —— 页面改版动了锚点会**部署失败（可见）**，而不是退回手写后悄悄漂移。不带参数 = 体检模式（打印取值与命中数），`--write` 才落盘。
  ⑤ **测试**：`verify.mjs` 断言 35 → **38 条**（新增「「最后更新」四处同源一致」「页脚提交说明非空且 ≤57 码点」「站点地图 lastmod 与页面同源」，直接读源文件，不受 `--url` 影响）。
  ⑥ **首次上线即坏，根因是 `replace` 回调**：部署后线上第 17 行变成 `次2026-09-20`，`dateModified` / 页脚 `.stamp-note` / sitemap `lastmod` 全部消失（仓库与工作区都是好的，坏的只有 CI 产物）。最小复现：本机 Node v24.18.0（`replace` 是原生实现、`NODE_OPTIONS` 为空）下 `'AA首次发布：…'.replace(re, x => x[1] + '2026-09-20')` 得到 `AA次2026-09-20BB` —— 回调里的捕获组被截成 1 个字符。
  ⑦ **验收**：`$env:CHROME_PATH=...msedge.exe; node dev/tools/verify.mjs` → **38/38 通过**；页面未新增任何外部请求或第三方依赖；`sitemap.xml` 的 `lastmod` 已纳入同一次注入（本地仍手写、与页面日期保持同值）。
  ⑧ 体积：仓库内版本 **431781 → 434351 字节**（+2570，其中 +2470 是本机检出把 LF 换成 CRLF 的行尾差，内容本身只多约 100 字节：导航栏日期对齐 + 页脚加提交说明注入位）。改动前快照 = `dev/_backup/index-v38.html`（431781，本机生成、不进 git）。
  ⑨ **修复（同日）**：`stamp.mjs` 改为 `indexOf` + `slice` 拼接（不再用 `replace` 回调），并在临时目录里用真实脚本 + 真实 git 复现验证：注入后 `首次发布：2026-09-14 · 最后更新：2026-09-20`、`dateModified`、`.stamp-note`、sitemap `<lastmod>` 全部正确。
  ⚠️ **教训**：`verify.mjs` 那 3 条元信息断言读的是**源文件**，抓不到"CI 产物被写坏"，这次是靠线上抽查发现的 —— 而且抽查必须用 `curl` + PowerShell，**别用 Node 读**：本机 Node 侧的文本观测（含 `git show` 输出、`replace`）会被同一问题污染，会把好文件读成坏的。
  ⑩ **移动端导航看不全（同日，用户反馈"移动端有些信息似乎没显示"）**：窄屏顶栏原本是单行 + 横向滚动，末两项「灵草丹药 / 法器法宝」被裁在视口外（用户附的截图只看到 5 项）。**第一次改错了方向**：让状态位在窄屏显示日期，反而更挤（入口只剩 3 项），已回滚。最终方案：`≤640px` 让顶栏导航**换行显示**（`.topnav .wrap{height:auto;flex-wrap:wrap}` + `.tn-links{flex:1 1 0;flex-wrap:wrap}`），实测 390px 下顶栏 73px、7 个入口分两行全部落在视口内、搜索按钮与第 1 行同行；顶栏变高后 `.chapter` 不再 sticky、`.view{scroll-margin-top:88px}`。状态位在窄屏仍让位（`display:none`），日期与作者主页由页脚承担（页脚新增「作者主页」入口）。超窄屏（`≤400px`，含 VS Code 内置浏览器的窄窗口）再降一档字号与内边距。实测量化：**390px → 两行、顶栏 66px；291px → 三行、顶栏 94px**（收档前 106px），两种宽度都无横向溢出、7 个入口全部落在视口内。

- **v39–v42：卡片与数据的一轮迭代（2026-09-21 ~ 09-24，当时漏记，本次按提交补记）**——① **默认展示全部人物**（不再默认开核心圈降噪，`1651329`）；② **同角色多形象轮播**（风希妖/人形、文思月少女/成年，`bb2f008`，卡片内 `.carousel` + 圆点，`.plot-*` 之外的既有交互）；③ 配图优先动画官方截图 + 一批错图/水印修正（`1651329` / `ca71d17` / `2cf9df9`）；④ README 恢复页面速览截图、补 Star History、把"221"改写成"二百余"（`c6d09a8` / `bb849e9` / `1efca0a`）；⑤ 涅槃始祖设定修正：非真灵凤凰，实为梵圣真魔功/涅槃圣体（`cd30aae`）。档案：`dev/_backup/index-v39.html` ~ `index-v42-before-split-arts.html`。

- **v43：功法 / 阵法 / 符箓 拆成三个独立视图（2026-10-02，`9a1a984` + `998a455` + `367a494`）**——`9a1a984` 先加「功法·阵法·符箓」独立视图（五库全收），`998a455` 再拆成 **v-gongfa / v-zhenfa / v-fu**、导航扩到**十大入口**，`367a494` 同步 README 分类描述。数据是 `const ARTS`（113 条）按 `cat` 切出的 `GONGFA` 40 / `ZHENFA` 39 / `FU` 34，索引与搜索面板一并纳入（`LIBS` 从 4 项变 7 项、`INDEX` 达 545 条）。
  ⚠️ 三库都是**单分类**：不渲染分类 tab，`LIB_UI.reset()` 里 `#tabs` 的取用必须带空值保护（`const te = q(cfg.tabsId); if(te) …`）—— 少这个 guard，整页初始化就会抛错。

- **v44：三库 111 条全部配图（2026-10-02，`91b67aa` → `eff676a` → `fc7a38c`）**——16 张官方动画图 → 再补 9 张 → 一次配齐、占位清零。资源总数随之涨到 496 张。

- **v45：首页 hero 换官方主视觉竖版立绘（风起天南）（2026-10-02，`8faed41`）**。

- **v46：访问统计迁到 busuanzi.cc（2026-10-03，`93ceb29`，`05b80cd` 调基数）**——原「不蒜子」官方 `busuanzi.ibruce.info` 持续 502/超时且无人维护 ⇒ 改 `POST cdn.busuanzi.cc/api.php`；旧接口累计的 ≈1400 无法随迁，用 `BASE_PV` 叠加显示。口径见 §7。

- **v47：慕兰之战人物与剧情节点补全（2026-10-04，`0cae7ef`）**——人物 251 → **263**（六个篇章的条数：七玄门 17 / 黄枫谷 35 / 乱星海 37 / 大晋 74 / 灵界 41 / 仙界 59）。

- **v48：剧情速览新增「情节梳理 · 全书十一卷」（2026-10-05，PR #1 @jackey0118）**——① 视图内加 `.lore-tabs` 页内 tab（境界时间线 / 情节梳理）；② 新增 `PLOT_VOLS`（当时为 11 卷 / 55 地点篇 / 333 步，后续补全为当前 388 步）+ `renderPlot()` + `plotStepHTML()`，**首次点开才渲染**；③ 样式追加在 `cultivation.css` 末尾；④ 内容整理自微信公众号「书生去哪了」，页面上下两处署名 + 原文链接，README / NOTICE 同步声明（见 §9）。
  ⑤ **合并时修正了 PR 的 key 错位**：`libFiltered()` 原用「筛选后的下标」生成卡片 key（`cfg.prefix + i`），而卡片 key 是全库索引、互引 chip 与深链 `gotoEntry` 的主键 —— 一旦筛选，key 整体错位、互引与跳转都会指向错误条目。已改为保留原数组下标（详见 v49 ③）。

- **v49：瀑布分批渲染 + 验收/文档全面对齐（2026-10-05，本次）**——① `makePager` 分批引擎接管人物卡与七库列表（`firstN=10` / `stepN=12` / `rootMargin=800px`，`ensureAll` / `ensureKey` 对外）；筛选从"扫 DOM 切 display"下沉到**数据层整表重排**；核心圈计数改 `coreCount()` 纯数据计算（`renderTabs` 不再依赖卡片先渲染）；② 修**展开态与地址栏失同步**：新增 `openKeyFromHash()` / `syncTargetToResults()`（开卡后被输入框筛掉时，地址栏不再停在 `#v-chars/<key>`）；③ 修 PR 带进来的 **key 错位**（`libFiltered()` 改用原数组下标，见 v48 ⑤）；④ **访问统计改取 `site_pv`** —— `page_pv` 按完整 URL 分桶（尾斜杠/查询串/分享参数/深链各成一个小桶），显示出来是「一千四百零几」的假小数字；⑤ `verify.mjs` 适配分批渲染（注入 `__loadAll` 补齐）并新增 4 条断言（首屏只挂首批 / 深链落到首批之外的卡 / 筛选后地址栏与展开态一致 / 取值必须是 site_pv），**42/42 全绿**（合并前基线 33/38，且脚本会在"找 南宫婉 卡片"处直接崩）；⑥ 文档同步：§1~§9 所有数字与结构按代码重写，补记 v39–v48。

- **v50：跨角色内容巡检 —— 补齐他角色功法/阵法/灵兽/法宝缺条（2026-10-07，本次）**——起因：用户指出「少了吕洛的千浪决」，追问「其他人是否也排查了」。做法是把**人物卡正文里点名、但全库无条目**的具名功法/阵法/灵兽/法宝逐条扫出来，再用百度百科、起点《凡人必备手册》与人物问答交叉核实后补录（存疑项一律标 `【存疑】`）。① **功法 +13（40→53）**：千浪决（吕洛）、真阳诀（李化元）、血灵大法（王蝉/燕如嫣）、六极真魔功（六道极圣）、断肢化劫大法（温天仁）、阴阳轮回诀（元瑶/妍丽）、大搜神分念大法（冰凤）、忘情诀（银月）、冥河天尸诀（炫烨王）、逆情断天大法（乾老魔）、天煞真魔功（天哭上人）、九劫灭真大法（轩九灵）、五鬼锁神大法（大衍神君所创）；② **阵法 +5（39→44）**：万木大阵（苦竹岛）、绝灵大阵（昆吾山）、光阴天璇大阵（真言门）、风火天绝阵（六道极圣）、三千道神大阵（古或今）；③ **灵兽 +2（40→42）**：乌凤（苦竹岛）、四瞳灵狐（银月化形所寄）；④ **法器 +6（65→71）／天材 +1（64→65）**：三焰扇、五子同心魔、血魔珠、御风车、千重峰、太玄八卦图、天桑神树。新增条目一律追加在各段末尾，**既有条目下标与深链序号不变**；`INDEX` 545 → **572**。⑤ **验收脚本改为「数据驱动」**：原先写死的 `40/39/34/81/65/40` 等期望值在数据增补后会假失败，现改为读页面自身 `BEASTS.length` / `TREASURES.length` / `coreCount()`；同时把 `v-map` 纳入 `VIEWS`（视图数 10 → 11），据实修正为 **45/45 全绿**；并新增 3 条防回归断言（他角色具名功法、被点名的大阵与灵兽、被点名的法宝与天材），防止再退回「只巡检韩立一人」。⑥ 顺手补齐 `v-map` 视图缺失的 `h1`（原来标题是 `<b>`，其余十个视图都是 `h1`），`.logo b` 样式选择器同步扩到 `h1`，**视觉不变**。

- **v51：修仙界全图（三界巡游）+ 行程节奏模型（2026-10-07，本次）**——页面新增第 11 个视图 `#v-map`（单文件 Canvas 引擎，独立 IIFE + 懒启动），数据为 10 阶段 / 152 地点 / 90 站点行程；同批修掉三处「地图上一跳而过」的根因，全部是**下标记账**问题，值得记下来：
  ① **站帧必须由构造保证，不能靠最近点搜索**：路径按「相邻两站」逐跨生成（`catmullSpan` + `resample`，且 `resample` 永远保留末点），于是「第 k 站对应路径上哪一帧」是构造出来的（`nodeChunk[k]` → 该段末点）。早期用「在整条路径上单调前向找最近点」，**重访同一地点**（阗天城 / 晋京 / 天渊城 / 虚天殿…）时会挑中后一次到访的精确坐标，整张时间表被挤到路径末端 —— 表现就是前半段一路疾驰、到站与停留全堆在后面。自检接口 `__fanrenMap.geom(s).arrivalDevMax` 现在全阶段 ≤ 0.6 世界单位。
  ② **停留帧插入后，下标必须整体换算**：`before[k]` 曾写成「先跑一遍 `before[k]=dup`」而那时 `dup` 还是 0，等于恒等映射，于是站点下标（已换算）与段范围（未换算）越差越远。现在 `before[]` 在插入过程中累计，`npos` 与 `chunks` 的起止、`warps` 的起止都换算到同一坐标系。
  ③ **`arcPts` 的起点**：i 从 0 起，弧线段的第一个点就是起点本身；否则「首段是弧线」的阶段（灵界 / 重返人界 / 重回仙界）第一站会从半途开始，首个到站帧差出上百单位。
  节奏模型（`WALK_UPS` / `WARP_SEC` / `WALK_BUDGET` / `STAGE_DWELL` / `STAGE_DUR_MIN|MAX`）：步行段按世界速度累计、整体受 `WALK_BUDGET`（24s）约束；**传送段每次固定 `WARP_SEC`（1.7s）**，观感取决于「几次」而不是「多远」；总时长 = 步行 + 传送×次数 + 每站停留，钳在 8–95s。传送判定 = 数据里的 `warp:1`（跨界面关键行程：阴冥之地、魔界·魔源海、小修罗界、广寒界、小灵天、真言门繁盛时期、灰界、积鳞空境…）或距离 > `WARP_DIST`（620）。传送中镜头不再追着高速点跑，而是朝目的地推进并拉远 34%、光点按进度淡出淡入，两端各来一次光效。
  播放器：阶段转场缓动与阶段接续（`scheduleNext`/`startNext`）统一受 `playing` 控制，暂停即冻结（连相机阻尼在暂停时也加速收敛，不留漂移）；详情面板新增「从此处播放」，探索模式下 ▶/空格 可从当前阶段续播。自检接口：`__fanrenMap.{geoStats,geom,hops,stageInfo,warps,pace,step,renderNow,snapView,pixel,landAt}`。

- **v52：许可由 Apache-2.0 转为 CC BY-NC-SA 4.0（非商用）（2026-10-07，本次）**——用户指令「这个项目不能商用」（2026-09-17 转 Apache-2.0 的反向操作，见 v26）。
  ① **LICENSE 换 CC BY-NC-SA 4.0**：中文范围说明（允许 / 禁止 / 第三方素材说明 + 官方 deed 摘要）+ 官方 `https://creativecommons.org/licenses/by-nc-sa/4.0/legalcode.txt` **正文逐字落盘**（500 行 / 24748 字节），协议全文不手打（v26 同款口径）。范围说明里的「禁止」只列许可本身能支撑的三条：商业使用、去除署名后发布、把改编作品改授为允许商用的协议。
  ② **NOTICE 重写授权范围**：Apache-2.0 → CC BY-NC-SA 4.0；「可自由使用、修改、分发，含商业用途」→「**不得用于任何商业目的**」+ 署名并附原文链接与许可声明 / 注明改动 / 改编须用相同协议；新增一句「2026-09-17 ~ 2026-10-07 之间的版本仍按 Apache-2.0」——旧授权不可撤销，不追溯已 fork 的副本。**第三方组件段另加一段**说明 ECharts 自身仍是 Apache-2.0、单独使用时仍可商用 —— 否则「整仓非商用」会把第三方组件的许可一起说错。
  ③ **页面五处同步**（漏一处就自相矛盾）：`<head>` 版权注释块 / JSON-LD `license` → `https://creativecommons.org/licenses/by-nc-sa/4.0/` / 顶栏 `.tn-github` 的 `title` / 首页 `.repo-card` 正文 / 页脚 © 行。另把首页「开源」区的 `.sec-desc`「源码已公开，可自由取用与再分发」改为「非商业用途可自由取用与再分发」——原句读起来等于暗示可商用。
  ④ **水印口径不变**：仍是**出处标识**、**不是许可条件** —— CC BY-NC-SA 4.0 第 2(a)(5)(C) 条与 Apache-2.0 一样禁止对下游附加额外限制，v26 的那条教训依旧成立（§「出处与防盗」）。
  ⑤ **验收断言同步**：`.repo-card` 正文的语义标记 `Apache` → `CC BY-NC-SA`（该断言本就只查「点名许可 + 出现第三方」，不钉措辞）。
  ⑥ **README「许可与声明」同步**，并补一行历史版本说明（口径同 NOTICE）。`LICENSE` / `NOTICE` / `README` / `public/index.html` 四处措辞必须一致。
  ⑦ **未动**：`public/assets/` 第三方图片、公众号文章段（本来就在授权范围外）、`dev/tools/echarts-entry.js` 里那段 Apache 许可头（那是 ECharts 的，改不得）。
  ⑧ **加强第三方权利声明**（用户追加要求「还需进一步强调原著、哔哩哔哩等的版权」）：`NOTICE` 第 2 条由一句话扩成三条 —— 原著小说 → 忘语 + 起点中文网 / 阅文集团 + 出版发行方；同名改编动画 → 哔哩哔哩及动画出品 / 制作方；事实性信息与原创表达的边界，并点明「动画截图 / 官方概念图 / 海报即来源于该动画」。页面另加**三处**：`<head>` 注释、首页「数据来源」区尾注、页脚新增一行；`.img-note` 图片声明补「截图与官方物料归哔哩哔哩及动画出品 / 制作方，同人作品归原作者」；`README` 对应两条 bullet 同步。
     ⚠️ 口径：只写「权利归各自权利人 + 未获授权或背书 + 权利人可通过 Issues 要求删除」，**不写「已获授权」**（没有），也**不点名具体动画制作公司**（B 站番剧页只列出品人姓名、无厂牌名，写错不如不写）。

- **v53：访问统计迁回「不蒜子」官方（2026-10-09，本次）**——起因：用户反馈「不蒜子计数好像又挂了？」。实测 `busuanzi.cc` **整站 502**（`cdn.busuanzi.cc/api.php`、主站、`www` 全挂，502 与连接超时交替；10-03 迁过去、10-09 已彻底不可用），而原「不蒜子」官方 `busuanzi.ibruce.info` **已恢复**（连打 6 次全 200、稳定 ~0.7s）。用户定调：**换回官方、不玩基数**。
  ① **迁回官方 JSONP**：统计段改回注入 `<script src="https://busuanzi.ibruce.info/busuanzi?jsonpCallback=BusuanziCallback_<随机>">`（官方**无 CORS 头**、只认 Referer ⇒ 不能 `fetch`），显式 `referrerPolicy='no-referrer-when-downgrade'`，回调名随机避免多标签页互相覆盖；标签留在 DOM 里，验收脚本靠它核对请求目标。
  ② **基数按「起点对齐」重设（不是删掉）**：官方桶迁回时实测只剩 `site_pv ≈1223` / `page_pv ≈1126`，而 `lizhenghe-chen.github.io`、`www.bunnychen.top` 都是全新桶（=1，没有访客从这俩域名进来），官方又是按 host 分桶 ⇒ **不可能还有别的桶藏着数字**。1223 比 10-03 记录在案的 ≈1400 还低，计数不会自己变小 ⇒ 官方在 9 月下旬长时间 502 里丢/回滚过数据，那 ≈180 与 busuanzi.cc 期间丢掉的 ≈400 都补不回来。用户明确要求衔接换站期间显示的 1888，故**重设**为 `BASE_PV = TARGET_PV(1888) − OFFICIAL_AT_SWITCH(1224) = 664`（首个访客看到 1,888，之后每访问 +1）。⚠️ 曾一度按「不叠加基数」实现（认为历史已在桶里）—— 那是没意识到桶被回滚过，已按用户要求改回基数口径。
  ③ ⚠️ **本次踩到的坑：字段名不同**。`busuanzi.cc` 回的是 `busuanzi_site_pv`，**官方回的是扁平 `site_pv`**（`{site_uv, page_pv, version: 2.4, site_pv}`）。只改接口不改字段名 ⇒ `Number(undefined)` ⇒ `!isFinite` ⇒ 直接落到「— 统计暂不可用」；而且**本地 `file://`／`localhost` 根本不发请求、验收脚本全绿**，极易误判成「已经好了」。定位靠 headless Chrome CDP 打补丁：`Node.prototype.appendChild`（抓 `<script>` 注入）+ `Node.prototype.textContent` setter（抓谁写了这个数字），拿到调用栈 `showFail ← onData ← BusuanziCallback_*`，并回看 `arguments` 里的真实字段名。
  ④ **验收 45 → 47 条**：真实域名那条从「未引入不蒜子脚本」改为「只请求官方 JSONP 接口（且不引官方那支 mini.js）」；新增两条源码级断言 —— 「走官方 JSONP 且读无前缀字段（出现 `busuanzi_site_pv` 即失败）」「显示起点自洽（`BASE_PV = TARGET_PV − OFFICIAL_AT_SWITCH` 且真的相加）」。`file://` 下 **47/47 通过**。
  ⑤ **本地端到端实测**：`--host-resolver-rules` 这条路走不通（Chrome 153 下 MAP 规则被 DoH 绕过，且 `bunnychen.top` 发 HSTS 会把 http 升级成 https），改为本机自签证书 + `127.0.0.1:8931` 实测：数字正确渲染（显示 `10,903,551`，即 `127.0.0.1` 共享桶的值），证明「注入 → 回调 → 解析 site_pv → 渲染」整链可用；线上真实值以部署后 `verify.mjs --url https://bunnychen.top/fanren-wiki/` 复核。
  ⑦ **运行时 JSONP 撞上「静态资源无第三方请求」断言**：那条断言扫 DOM 里的 `link / script[src] / img`；统计改成 JSONP 后标签就留在 DOM 里 ⇒ 线上复核时它**假红**（v27 起一直是绿的，是因为当时统计走 `fetch()`，DOM 里什么都没有）。修法：统计标签打 `data-fw-stats`，断言选择器改成 `script[src]:not([data-fw-stats])`，断言名改为「页面静态资源无第三方请求（运行时统计 JSONP 除外）」。它守的口径没变 —— **HTML 里不得出现写死的第三方资源**；别把那个标记删了，否则线上验收会永久假红。
  ⑥ **未动**：`stamp.mjs`（锚点未受影响，体检 6/6 命中）、页面其余结构、`busuanzi.cc` 相关的历史备份文件（`dev/_backup/`）。

- **v54：按 B 站评论区反馈逐条核查（2026-10-13）**——视频《凡人修仙传》完整地图+动画来了！（BV1kvpi6eEpq）的 101 条评论/回复里，地图类反馈集中在「地名方位错」与「比例不对」。**核查后确认站上已是正确口径、无需改动的**：金花老祖配图（a27c220 已撤图）、妙音门·双峰岛（不再贴着六道极圣）、出生地贴着正道盟（a27c220 已按动画第 159 集官方图重排）、慕兰/突兀是否隔着九国盟（第 877 章已改草原南北分）、苍坤遗迹压慕兰腹地（已退到黄土荒地南缘）、飞升失忆（站上写的就是「仙界遭伏击失忆」，不是飞升灵界）。**本次实际改的四处**：
  ① **越国/胥国口径**：燕云山条目里残留一处「胥国正道七派」→ 改回「越国」；「地理考据」补一行「原著＝越国（韩立出身越国镜州青牛镇五里沟），动画为区分各国改称胥国，本页按原著」——动画观众按动画名找、原著读者按原著名找，两边都能对上。
  ② **阴冥之地/鬼雾**：原写「乱星海西缘与阴司界交界的空间」不准。据原著补正为「上古真灵罗睺体内自成、随其漂移的空间；入口是罗睺吐出的天灾『鬼雾』，入内法力尽失（绝灵之气），只能凭肉身与阴兽搏杀」，鬼雾条目同步改写。
  ③ **面积比例口径**：页脚与「地理考据」写明「面积非等比——原著中大晋约十倍于天南，图上只作相对表达」，并说清人界带是「天南西 / 大晋中 / 乱星海东」的横向可读性排布（乱星海按原著取天南的东北向海面）。
  ④ **天南切图中间产物下线**：`public/assets/tiannan-map-cutout.png`（11MB）页面从不引用、却随 Pages 一起发布，已 `git rm` + `.gitignore`（见 §6）。

- **v55：慕兰 ⇄ 大晋 的陆桥 + 接缝重构（2026-10-13，本次）**——起因：用户看图上「天澜草原」四个字写在海面/虚无里，而按原著慕兰与大晋之间是有陆地相连的（草原是两块大陆之间的过渡带）。
  ① **补陆桥，不挪大陆**：`REGIONS` 新增「天澜草原」（`x:548,y:757,rx:100,ry:34`）专做这块过渡陆地，把 `九国盟 · 慕兰` 与大晋西缘接起来；`OCEANS` 里原先那条「天澜草原」海域注记删掉（名字改由区域标签表达）。⚠️ **教训**：第一版图省事把 `九国盟 · 慕兰` 的 `rx` 从 100 拉到 200 让它自己长过去，被用户否掉——「不要生硬地移动，加一点大陆链接就行」。要连就补一小块，别改已经校好的大陆本身。
  ② **接缝重构（`maskedPaint`）**：两块陆面重叠时各描各的海岸，会看见两条岸线互相切割（像道堤）。现在**等深环 / 海岸内晕 / 海岸线 / 子区域色块与界线**统一走「先画进临时画布 → `destination-out` 抠掉别的大陆陆面 → 整块贴回」的通道：重叠区两边岸线都消失，整片陆地只留并集的外缘海岸一条，接缝处只剩地面色差、没有硬线。
     - 调用即 `maskedPaint(r, landBox(r), function(g){…})`；临时画布 `SC` **按单块包围盒分配**（v58 起，不再与 `offLand` 同尺寸），逐块只清/贴自己的 bbox；`buildLand()` 结果缓存进 `LAND{}`（原先同一块要算 3 次）。
     - **不参与抠除**：乱星海（群岛，`isArch`）、无边海（本就不画陆面/岸线）、天南贴图（陆缘由图像自身表达）。
     - sub 色块在通道里额外剪到本块多边形内，避免噪声海岸把色块甩进海里。
  ③ 附带：`geoStats().regions` 21 → **22**，README 两处「21 个区域」与本文档 §11.3 数字表同步改 22。
  ④ 验收 47/47；截图核对：人界带现在是「天南 ─ 九国盟·慕兰 ─ 天澜草原 ─ 大晋」一整块连陆，灵界/仙界无回归。

- **v56：乱星海方位重排（三界纵向带重平衡）（2026-10-13，本次）**——起因：用户查证「乱星海应该在什么方位」，结论是**天南之北、无边海之外**（原著第三卷 358 章「继续往北走……极北之地……无边海」；「乱星海与天南隔着一个无边海」；韩立自阴冥之地脱身是「南飞万里」横穿无边海回天南；且与大晋无接陆）。原图却把乱星海放在天南**正东**、纬度还比天南偏南、紧贴大晋东侧 ✗。
  ① **三界纵向带重排**（本次的关键取舍）：人界带北侧原来只到 world y 2200，塞不下整片乱星海。三改 `BND` + 同步色带/壁障：
     - `人界`：`y:[495,880]→[200,880]`、`ty:[2200,3400]→[1282,3400]` —— **y 跨度比例 k 守住 3.115**，于是天南/大晋/慕兰/天澜草原的世界坐标**一个都没动**，只是北边多出约 900 单位海面；
     - `灵界`：`ty:[1060,2040]→[660,1420]`（上移 + 跨度 980→760，即**纵向压扁 22%**，给乱星海腾空间）；
     - `仙界` 不动；`realms` 色带（4889）与两处「界面壁障」（静态 4896 / 动态 5122）同步改成 620 / 660-1440 / 1500-3410 与壁障线 640、1470。
     - ⚠️ **k 必须守住**：中途把 `人界` 写成 `ty:[1300,3400]`（k 3.088）就足以让贴边的沿岸点位「白宝城」掉到海上——0.9% 的比例差就能挤出海岸线。
  ② **乱星海整体搬到天南正北**：数据坐标 x、y 分别变换（中心 `(1305,507)→(360,370)`、`rx 210` 不变、`ry 150→118`），17 个「乱星海 · *」点位、`ARCH_SPECS`、`ARCH_KEEP`、`archIslands()` 里的撒点包围盒（那四个 `toWorld({...})` 的 x/y 界）与两道撒点环半径一起跟着改。
     ⚠️ **海域注记走的是百分比**：`OCEANS` 用 `mapN(o.x,0,1,tx…)`，换带子必重算，否则「内星海/外星海/万丈海/雾海/冰海/无边海」会飘在旧位置（本次六条全部重设）。
  ③ 收尾：`白宝城`（灵界·风元大陆西南）在新比例下贴边落海，`y 480→466` 挪回陆地；`geoStats().offLand` 回到只有历史遗留的「火云岛 · 火碧珊群岛」1 处。
  ④ 验收 47/47；`arrivalDevMax` 全阶段 ≤0.5、区域重叠表无新增；截图核对：人界带自上而下为「乱星海 → 无边海 → 天南/大晋」，灵界带略扁但形貌正常，「地理考据」抽屉的乱星海方位一条同步改写。

- **v57：三界间距拉开（世界加高）（2026-10-13，本次）**——用户看图后反馈「间隔再大一些，有地图重合了」，并明确「不用担心观感，动画会带用户移动」⇒ 允许整体铺得更开。
  ① **两处真实的跨带重合**（`regionGaps()` 里看得见，靠肉眼容易漏）：`灰界`/`魔域`（仙界最下一排）压到 `血天大陆`（灵界最北条），面积 10224 / 4032 —— 根因是 v56 把灵界带压扁上移后，灵界北缘顶到了仙界南缘。
  ② **改法：加高世界 + 拉开三条带**（不再靠压扁腾空间）：
     - `WORLD.H: 3450 → 4200`；`灵界 ty:[660,1420] → [890,1650]`（**跨度不变** ⇒ 灵界形状不再被压扁，恢复原始比例）；`人界 ty:[1282,3400] → [1916,4034]`（跨度不变 ⇒ 人界内部相对关系原样，只是整体南移）。
     - 色带/壁障同步：`realms=[[40,720],[870,1670],[1850,4200]]`、壁障线 800 / 1780。
     - 结果：仙界南缘(668) ↔ 灵界北缘(898) 间距 230、灵界南缘(1650) ↔ 乱星海北缘(1880) 间距 230 ⇒ 跨带重合全部消失（`overlaps` 只剩人界内部几处「故意衔接」项）。
  ③ **乱星海再上移 57（数据坐标）**，与 `无边海`/天南彻底分开（原来两者只差 1 单位、几乎贴在一起）；撒点包围盒同步 `y 282..432 → 225..375`。海域注记同批重设：乱星海系四条随组上移（内星海/外星海/万丈海/雾海），`无边海` 贴回天南北岸（.449），`冰海` 从乱星海区域挪到晋北（.551，原先它飘在乱星海中间）。
  ④ ⚠️ **教训**：`WORLD.H` 一改，**所有用百分比定位的东西都会漂**（`OCEANS` 的 `mapN(o.x,0,1,tx…)`）；而 `BND` 的 y 跨度比例 k 一改，贴边的沿岸点位就会掉海。两者都必须同批核对 —— 本次靠 `geoStats().offLand`（应只剩历史遗留「火云岛」）与 `regionGaps().overlaps` 两把尺子收尾。
  ⑤ 验收 47/47；`arrivalDevMax` 全阶段 ≤0.5；截图核对三带之间是干净海面，灵界不再被压扁。

- **v58：代码质量与加载优化（2026-10-13，本次）**——用户以 `/code-quality` 提出「检查优化相关代码 + 网站/图片加载」，并要求**先不 commit**。
  ① **懒加载 ECharts**：省掉首屏 527KB（gzip 178KB），细节见 §7；验收 47 → **48** 条。
  ② **图片体积**：舆图类四张 + 天南切图重设（共 −1.9MB），详见 §6 的表；`.jpg/.png` 原件已删（git 历史里可取），`extract_map.py` 的 INPUT 路径加了取回说明。
  ③ **地图引擎内存**：接缝用的临时画布原先按整张陆面层尺寸分配（3780×4980 ≈ **75MB**），实测只需单块包围盒 ⇒ 改为按 bbox 分配（最大 1700×1700 ≈ 11.6MB），并把尺寸判断改成「不够大才重建」（原来只创建一次、`WORLD` 一变就不跟随）。
  ④ **注释/常量**：乱星海那两条过时注释（「整体平移 +65,−72」「区域放宽压扁」）改成现状口径；`landBox()` 的 `1.28 / 48` 提成 `BOX_MARGIN / BOX_PAD` 并写明来源。
  ⑤ ⚠️ **本次动过但未改**：`index.html` 自身 802KB（gzip 271KB，中文文本占大头）——当时认为拆外链与「自包含单页」红线冲突，只报告不动；`offBg`/`offLand` 两张全尺寸离屏画布（各 ≈75MB）是既有设计，本轮只把**新增**的那张降下来。（**两条都在 v59 落地**：红线改写 + 拆出 `map.js`，画布 177MB → 77MB。）

- **v59：红线改写 + 地图引擎拆分 + 离屏画布内存（2026-10-13，本次）**——承 v58 的两处「动过但未改」，用户要求「按你的建议改写红线并进行对应的优化；画布按建议优化」。
  ① **红线改写**：删掉「自包含单页 / CSS JS 全内联」这条**字面**约束，换成四条真正要守的不变量（零第三方请求 / 只发 `public/` / `file://` 可开 / 无构建），写在 §1.1；页脚与 Issue 模板里「单文件静态站 / 单文件静态页面（CSS/JS 全内联）」的措辞同步改掉（否则是**自己文档说错话**）。理由：内联是实现细节，图片本来就外链在 `assets/`（内联的只有 CSS/JS），这条红线当时只挡住了「降低 646KB 首屏」这一件事。
  ② **拆分落地**：`index.html` 里 176KB 的地图引擎 IIFE 原样移到 `public/javascripts/map.js`，原位置留 `<script src="javascripts/map.js"></script>`（仍在 `</body>` 前最后一位 ⇒ 主逻辑的全局仍可见，无 `defer`）。`index.html` 803KB → **646KB**。改完用「像素级等价」验证：拆前后同相机三帧 **0 像素差异**（下条方法）。
  ③ **离屏画布 177MB → 77MB**（−100MB）：`offBg`（94MB，内容只有竖向渐变 + 3 条色带 + 2 条壁障带 + 经纬网）拆成「底图竖条 + 色带竖条」（各 1×5600 ≈ 22KB），经纬网改为每帧只画可见格点；`offLand` 的外延从 `PAD=700` 收到 `PAD=300`（`offLand` 由 3780×4980 收到 3600×4800，71.8MB → 65.9MB；陆面内容极值 −3..3015 / −48..4255 全在界内，由 `canvasInfo().landExtent` vs `bounds` 断言守住）。新旧对比：差异像素 0.06% 以内、最大色差 10/255，且**全部落在平滑渐变与文字抗锯齿的重采样相位上**（聚类后是 9×9 的格点十字与壁障字注，不是结构错位）。细节见 §7。
  ④ **新增两条断言（48 → 50）**：`canvasInfo().mb ≤ 90`、陆面内容不出栅格外延 —— 以后谁再改 `PAD`/画布尺寸，这两条会先响。
  ⑤ **帧耗时实测无回归**：新旧同相机各跑 150 帧（`__fanrenMap.step(16)` 均值）——旧 0.74 / 0.53 / 0.64 ms，新 0.67 / 0.49 / 0.60 ms。经纬网从「预烘焙」变成「每帧只画可见格点」多出的路径绘制，被「不再缩放整张 4400×5600 位图」抵掉了。
  ⑥ **验证方法已沉淀成工具**：`node dev/tools/pixel-diff.mjs _ref_head.html index.html` —— 同相机（(900,2200,.42)/(800,3000,.85)/(1500,2000,.2)）各截三帧逐像素比对，并做 8 邻域聚类。它自己起静态服务（**必须走 http**：`file://` 下 canvas 被判跨域污染、读不了像素），并在页面脚本前注入「固定 rAF 时间戳 + 固定 `Math.random`」拿可复现的像素（否则粒子与壁障虚线相位每次都不同）。用法与判据见 §8.3。

- **v60：天南一带地点重新标定（贴图坐标系）（2026-10-13）**——用户看图反馈「地图的节点偏了」，截图里 落云宗 · 云梦山 / 天道盟 · 落云溪 / 花溪阁 / 元武国 / 桦叶城 都落在图上的白边（海面）里。
  ① **根因**：2026-10-13 早先那次「天南改用去背贴图」（`3966e08`）只重标了西/南 6 个点（极西之地、千竹教、阗天城、黄土荒地、苍坤真人遗迹、慕兰草原），**越国—溪国北侧这一簇沿用了贴图之前的坐标** —— 贴图的陆地比原先自绘的椭圆窄且偏南，于是这 6 个标记整体漂到图上白边（= 贴图的透明处 = 海面）里。**这个 bug 与 v59 的画布改造无关**：`3966e08` 之后每一版渲染都一模一样（同相机逐像素比对 0 差异），只是当时没人看那一块。
  ② **判据要先立起来**（不然「偏没偏」只能肉眼吵）：新增 `__fanrenMap.landPainted(wx,wy)` → 读离屏陆面层 `offLand` 的 alpha，「这里真的画了陆地吗」；`locsOffLand()` → 返回没落在陆地上的地点名单。修前这 6 个点全部 `false`（离岸 6~141px，换算 1~24 个数据单位）。
     ⚠️ **`geoStats().locsOnLand` 查不出这类问题**：它判的是「点是否在某个区域的椭圆多边形里」，而天南贴图比椭圆窄，点在椭圆里照样能落在图上的海里 —— 修前它一直是 151/152 全绿。**判「图上位置」必须看图上画了什么，不能看数据形状。**
  ③ **修法：照贴图上的刻字重新标定**（图上字形即基准）：`落雲宗` 竖排注记 → 落云宗(333,575)；`天道盟` 两个大字之间 → 落云溪(365,581)；天道盟东侧 → 花溪阁(395,590)；`元武國` 及其点位 → 元武国(369,614)；其点位以西 → 桦叶城(340,616)；北岸缺口以南的陆地 → 神兵门(505,598)。每个点用 **3×3 邻域采样**核过（九宫格全部落在陆上才收），避免「刚好压线」。
  ④ **新增断言（50 → 51）**：`locsOffLand()` 必须只剩点名的两个例外 —— `七灵岛`（天南海中三岛）与 `火云岛 · 火碧珊群岛`（v62 正名为 `火珊瑚群岛`），它们本身就是海里的岛群。以后谁再把地点挪进海里，这条会直接点名。
     ⚠️ **`file://` 下读画布像素会抛 SecurityError**（本地图片画进画布 = 跨域污染），所以 `verify.mjs` 给 Chrome 加了 `--allow-file-access-from-files`；`landPainted()` 自身也 try/catch 返回 `null`，页面侧永不抛错（该接口只服务自检，用户路径不用它）。
  ⑤ **回归核对**：`geoStats().locsOnLand` 151（不变）、`regionGaps().overlaps` 8 对（不变）、各阶段 `arrivalDevMax` 仍为 0；只有行程路径长度按新点位微调（阶段 4 1718→1596、阶段 5 10557→10608）—— 这是应该变的（路径本来就过这些点）。验收 51/51。
  ⑥ ⚠️ **今后改贴图（换图 / 换裁切 / 调 `wrx*2.7` 这类落位系数）必须同批重标天南一带坐标**，并跑那条落地断言。

- **v61：人界板块比例校正（大晋 + 乱星海放大）（2026-10-15，本次）**——起因：网友反馈「大晋的面积还要再大」，随后追加「乱星海一并放大，并注意它们的位置和协调性」。查证结论：原著大晋「一百零八州 · 三十六郡，面积十倍于天南」（第六九四集 + 《必备手册》宗门篇）、乱星海是「极大一片海域」，而图上大晋只有天南的 2.2 倍（视觉上甚至与天南贴图相当）、乱星海是一小撮岛。
  ① **只动「非基准」的板块**：`大晋` 椭圆 235×145 → **375×200**（线性 ×1.60、面积 ×2.20，对天南由 2.2 倍升到 **4.9 倍**）、中心 (840,750) → **(1018,716)**；`天澜草原` 100×34 → **126×46**（面积 ×1.7）、中心 (548,757) → **(560,775)**，让「天南 ⇄ 大晋」的陆桥随大晋一起加宽；`乱星海` 整片群岛 ×1.18（见③）。**天南（贴图=坐标基准）、九国盟·慕兰（v55 教训：已校好的大陆不改）、极西之地（原著本就地小）一律不动。**
  ② **两条硬约束（都是「边界」而不是「比例」定的）**：
     - **西缘不得越过天南贴图的硬右缘**：贴图是矩形去背切图，右缘（数据 x≈583）是硬边、没有羽化。大晋陆面若压上去，贴图的直边就会横切在大晋陆面上露出直缝（第一版取中心 1000 就踩到了，`regionGaps` 多出一对 `大晋 ↔ 越国·天南（贴图）` 面积 14976）。改到 1018 后大晋西缘落在数据 x≈593，该对重叠消失。
     - **南缘不得顶破陆面栅格**：`landExtent.y1` 必须 ≤ `WORLD.H+PAD`；`landBox` 的 y 余量（1.28×wry）比 `buildLand` 的纵向系数（1.18×ry）小，ry 一大就会被切平。实测 y1 = 4369（上界 4500），rx/ry 再大就得先改 `BOX_MARGIN`。
     - 顺带量到一条既有性质（非本次引入）：`buildLand` 的纵向半径是 `ry*s*1.18`，而 `landBox` 的余量只有 `1.28` —— 只要 `s` 在南北极方向超过约 1.08 就会被栅格切一刀。旧版大晋（ry145）已贴在该临界附近，本次 ry200 仍未越界（实测陆面南端平滑收尖，无平切）。
  ③ **乱星海一并放大 ×1.18（整片群岛同批动）**：图面体量由 `ARCH_SPECS`/撒点包围盒决定，不是 `REGIONS` 的 rx/ry —— 只改 rx/ry 是「假放大」（标签与取景框会变，岛群一动不动）。故整组一起放大：`ARCH_SPECS` 26 座手绘岛（x/y 与 a/b 同乘）、撒点环半径（100×52 / 205×104 → 118×61.4 / 241.9×122.7）与撒点尺寸区间（a: 4~10.5 → 4.7~12.4）、撒点裁剪范围、17 处「乱星海 · *」点位、`REGIONS` 的乱星海椭圆（210×118 → 248×139，中心 360,313 → 363,313）、`OCEANS` 的内星海/外星海/万丈海/雾海四条（按同一变换换算出新百分比）与 `ARCH_KEEP` 避让框（跟着新注记位重设）。
     - **放大倍数是量出来的，不是拍的**：可用纵向空间 = 「人界→灵界 壁障」（数据 y≈156）到「无边海近海岛的北缘」（数据 y≈475）；群岛原包围盒 y 193~437 的中心几乎正好落在可用带中心，所以**取包围盒中心为缩放中心 ⇒ 整体位置不动，只是变大**。留 ~16 数据单位余量 ⇒ **×1.18 是上限**（再大就顶到壁障或撞无边海的近海岛）。实测：放大后群岛 y 174~459、x 60~630（原 193~437 / 103~590）。
  ④ **顺手修掉 `ARCH_BOX` 的陈旧坐标（本次必需的配套）**：`sameSea()` 的判据框原本写死在 `toWorld(995,548)~(1450,890)` —— 那是 v56 搬家前的位置，搬家时漏改，现在指着**大晋**。它此前「无害」只是巧合（舞台 3/5 的岛间跳距都 < `WARP_DIST`）；一放大，`虚天殿 → 外海·万丈海` 就从 558 涨到 631~659，越过 620 阈值，而 `sameSea` 又判 false ⇒ 会**凭空多出一个传送段**。改法：把数据坐标包围盒提成单一真源 `ARCH_SCAT_D`（撒点中心范围）/ `ARCH_BOX_D`（含岛体半径的整体范围），`ARCH_BOX` 由后者派生，`archIslands()` 的裁剪也读前者。
     - 副作用是**按设计补齐了观感**：`SEA_DIST=130` 那套「群岛内相邻站点另画渡海弧线」此前一直没生效（`sameSea` 恒 false），现在生效了 —— 舞台 3 的六跳全变成海图式弧航线（`geom(3).segs` 六条 `sea` + 一条显式 `warp`），舞台 5 的 `虚天殿→天星城`、`天星城→极阴岛` 两条同理。传送段数量不变（舞台 3 仍 1、舞台 5 仍 7）。
  ⑤ **22 处大晋点位整组等比外扩**（`x' = 1018 + (x−840)×375/235`、`y' = 716 + (y−750)×200/145`）——点位是绝对数据坐标，椭圆一变就得跟着走，否则全挤在中心。整组同比例外扩后各点相对椭圆的 `(u,v)` **一个都没变**，故 `landFloor`/分区锚点/巡游路径的相对关系原样保留。乱星海 17 处点位同理，绕包围盒中心 (346,315) 放大 ×1.18。
  ⑥ **`OCEANS` 的「冰海」北移**（`.470,.551` → `.549,.294`）：大晋北缘上探到数据 y≈487，原位置（y≈575）会落进陆面。
  ⑦ **验收**：`canvasInfo().mb` 77 → 80（≤90 ✓）、`landExtent` (-17,-48)-(3205,4369) 在界内 ✓、`locsOffLand()` 仍只有 `火云岛 · 火碧珊群岛` ✓（v62 起该点正名为 `火珊瑚群岛`）、`regionGaps().overlaps` **与基线完全同集**（只 `天澜草原↔大晋` 15104→13760、`九国盟·慕兰↔天澜草原` 9472→10624 两处数变）✓；`verify.mjs` 51/51。乱星海群岛自检：`geoStats().arch` 88 → 93、`isles` 159 → 164，人界北带逐行扫「画了陆面的像素」确认群岛不越壁障（顶 174 vs 壁障 156）、不撞无边海近海岛（底 459 vs 476）。
  ⑧ **顺带修掉一处「取景框小于陆面」的既有缺陷**：`fitAll()` 原来按 `wy ± wry`（北侧还乘 1.02）取景，而 `buildLand` 的纵向半径是 `wry×1.18` —— 于是「复位全图」时最靠南的一块总被视口底边平切一刀。旧版大晋矮（ry145），切得浅、没人在意；放大到 ry200 后切面就明显了。现按同一个 1.18 取景（`YK=1.18`），全图整体缩约 5%，大晋南缘的完整海岸线回到画面内。
  ⑨ **一处必须同批处理的副作用**：大晋点位外扩后，阶段 5 的入口段「慕兰草原 → 江陵府」由 582 涨到 **797 世界单位**，越过 `WARP_DIST`（620）自动从「步行」变「传送」（`warps()` 阶段 5：6 → 7）。几何上无法回避——受贴图右缘约束，大晋西侧的江陵府已推到 x≈795，而原著里「关宁府在辽州最西」（= 关宁府不能比江陵府更东）堵死了「把江陵府往西挪」这条路。改法按站内既有约定办：**给阶段入口补 `portal` 标签**（其余阶段入口「古传送阵 / 传送回天南 / 飞升灵界 / 返回人界 / 飞升仙界 / 偷渡回仙界 / 传送入灰界」都挂了），标成「穿慕兰草原入大晋」。
  ⑩ **口径同步**：页脚「面积比例」一条与「地理考据」抽屉（新增「图上比例 · 压缩示意」三行）都改成「读的是谁比谁大、不是等比」并给出实际倍数表（大晋 4.9 / 乱星海 2.3 / 天南 1 / 极西 0.1），并**如实点出唯一与原著次序相反的一块是慕兰·天澜草原（图上 0.7）及其原因** —— 网友再问「为什么不是十倍」时有据可引。**这是全图唯一的比例口径出处，改比例必须同批改这两处。**

- **v62：巡游顺序与节点复核（按原著逐卷校对）（2026-10-19，本次）**——用户要求「仔细核查播放顺序和节点，确保不要有遗漏或者错误，结合搜索和官方信息」。
  ① **校对基准**：站内既有 `PLOT_VOLS`（「情节梳理 · 全书十一卷」，来自微信公众号「书生去哪了」原文）+ 分批检索原著章节/百科。**先用 `PLOT_VOLS` 逐卷对表**（它本身就是已采信的考据源，比临时搜到的 AI 综述可靠），再用搜索确认「地名/归属/顺序」中拿不准的几条。
  ② **改掉 5 处「认错了地方」**（不是顺序问题，是节点挂到了别处）：
     - **慕兰大战 → 黄龙山**（新增）：原著主战场是虞国离州边境的黄龙山（禁制大阵、兵家必争），韩立**没有**深入慕兰草原；此前巡游把这一战记在 `慕兰草原` 身上。现单立 `黄龙山`（九国盟·虞国离州，imp 3），`慕兰草原` 改为「第六卷秘入草原入大晋（五鬼锁神大法）」的过境点。
     - **古传送阵 → 灵石矿**（顺序修正）：阵法在**灵石矿矿洞深处**（韩立驻守时发现，同批得大挪移令），第 407–411 章由辛如音协助修复后启阵。此前 `portal:"古传送阵"` 挂在「越京 → 魁星岛」这一段上，读起来像从越京传送。现改为「越京 → 黄枫谷撤离 → 回灵石矿启阵 → 魁星岛」，`portal` 挂到第二次到访的 `灵石矿`。
     - **火云岛 · 火碧珊群岛 → 火珊瑚群岛**：原著第九卷是「火珊瑚群岛（火瑚/火珊群岛）·火阳族」，在**灵界南部海域**（风元与雷鸣之间），韩立重伤后被空间裂缝抛落、养伤并修传送阵。原条目作「血天大陆南海」——位置与归属都错，且巡游恰在「风元 → 雷鸣」之间。现正名并移到 (790,450)；`warp:1`（是「重伤传送」而非步行）。
     - **小修罗界 · 凤族 → 小修罗界**：小修罗界是修罗界崩溃后的**碎片界面**，位于风元大陆南部，须由灵王以「修罗之心」开启通道，界内是修罗族/空鱼族——不是风元东北的凤族之地。描述改为斩修罗蛛、杀巨龟得玄武真血、取空鱼族圣物山海珠。
     - **七妖之地 · 九仙山 → 九仙山**：九仙山是**人族三境**一侧的万宝大会所在（天元圣皇主事），不在七妖之地。同时新增 `天鹏圣城`（七妖之地·天鹏妖王主城，鲲鹏真血/惊蛰十二变）。
     - ⚠️ **反例（差点改错）**：一度把 `三境七地 · 天灵境` 改成「天妙境」——检索发现**原著多用「天灵境」，天妙境只是别名**，且页内 `天妙灵皇` 人物条目本就写「坐镇天灵境」。已回退，只在描述里注明别名。**改已有名称前先搜站内是否另有条目在用同一套称谓。**
  ③ **补齐 4 个被漏掉的关键节点**：`黄龙山`（慕兰大战）、`元武国`（结婴后灭付家、得至木灵婴 → 第二元婴；此前元武国只是不出现在巡游里的普通点）、`五里沟 · 青牛镇`（第五卷**韩家祠**祭祖留噬金灵剑 / 第七卷点醒韩鸣——`STAGES[7].tip` 早就写着「韩家祠」而巡游里没有这一站）、`岳阳宫`（盗昊阳鸟长翎）、`魔湖岛`（第七卷金阙玉书外页·符箓）。
  ④ **两处顺序错误（仙界）**：
     - **灵寰界**：原「明远城 → 黄澜古漠 → 冷焰宗 → 境元观 → 天鬼宗」→ 改为「明远城 → 天鬼宗 → 冷焰宗 → 境元观 → 黄澜古漠」。依据：韩立初入灵寰界即因柳乐儿与天鬼宗结仇；小北斗星元功得于冷焰宗，之后才以掌天瓶精炎之火助柳乐儿灭天鬼宗；境元观聚星台修至大成；黄澜古漠是临行前筹措偷渡材料之地。`STAGES[8].tip` 同步（原文案把天鬼宗写在最后）。
     - **乱星海（第四卷）**：天雷竹是紫灵所赠、青竹蜂云剑炼于**虚天殿之前**，故 `妙音门 · 双峰岛` 由虚天殿之后**前移**到之前。
  ⑤ **一处归属改正（仙界）**：`烛龙道 · 太玄殿` 原标「荒澜大陆」→ 实为**北寒仙域·古云大陆**（钟鸣山脉；古云大陆在荒澜之东，图上未分绘，故置于荒澜东缘并在区域名注明）。`圣傀门`（荒澜大陆·浮山）保持不动。
  ⑥ **`portal` 文案一处纠错**：阴冥之地脱身后是「**南飞万里横穿无边海**」回天南，不是传送；`落云宗` 的 `portal:"传送回天南"` → `"南飞万里横穿无边海"`。
  ⑦ **新增 11 行「巡游顺序 · 几处易错节点」**进「地理考据」抽屉（古传送阵在灵石矿 / 天雷竹早于虚天殿 / 慕兰大战在黄龙山 / 火珊瑚群岛在灵界南部 / 小修罗界与九仙山归属），让读者能自己复核，而不是只在 commit 里。
  ⑧ **验收**：`locsOffLand()` 只剩 `七灵岛`、`火珊瑚群岛`（`verify.mjs` 的 allowed 名单同批改名）；`geoStats()` 152→156 地点、90→97 旅程节点（76 个不同站点）；各阶段 `arrivalDevMax` ≤0.5；阶段时长 S1–S10 = 8/13.8/25.2/15.5/49.8/50.8/8/9.2/23/17.8 秒（均未触 8–95s 的钳位上限）；`regionGaps().overlaps` 与 v61 同集（仅 `越国·天南↔九国盟·慕兰` 因黄龙山靠边 38400→40192）；`verify.mjs` 51/51。
  ⑨ **仍未纳入巡游的次要节点（有意为之，不是遗漏）**：双蝎山、银蛟山、天机阁、魔陀山、火狱禁地、金蛟王伏击（均在大晋/乱星海同一片区内，属同段支线）、黑冥雾海/地渊/冥河之地/木棉城（同在风元大陆境内）。巡游是「每段挑代表点」的看点路径，不是逐章地图 —— 判定标准是「是否会被误读成发生在别处」，而不是「是否提到过」。`LOCS` 里另有 80 个不被巡游经过的地点（人物/势力展示用），这是设计。

- **v63：按 B 站未解决评论核对 A/E 两组 + 血影遁来源勘误（2026-10-21，本次）**——上一轮（v54）只回了评论、没逐条对账；本轮把「UP 没回过的 99 个主楼」里真正有实质内容的挑出来，逐一拿原著章节原文核。
  ① **改 4 处实打实的错**（其余全部「评论说法不成立」或「属比例表达」，一律不动数据）：
     - **婴鲤兽**：`camp` 由 `黑煞教` → **六连殿**（原文第 380 章，冯三娘主持、报酬降尘丹；黑煞教是越京邪教）。原条目把两个八竿子打不着的势力串了，而巡游节点本来写着「猎杀婴鲤兽［六连殿招募］」—— **站内自相矛盾即为 bug，这类先查同一事物在本站另一处怎么写**。
     - **程天坤**：`元婴后期（大晋第一修士）` → **元婴期（原著未标初/中/后期）**。原文第 640 章只说「元婴」，落云宗在天南溪国；原文「大晋第一城」指晋京，**「大晋第一修士」是张冠李戴**（该说法在原文只用于乱星海：万法门疯婆子、天镜散人）。
     - **七焰扇**：炼制之法得自**天南坠魔谷**一行（不是「古修储物袋」、也不是银蛇山）；银蛇山是**大晋南疆**常年喷发的火脉，韩立在那里炼三焰扇。原条目把「得法之地」和「炼宝之地」混成一个「银蛇山段落」。同批把 `PLOT_VOLS` 的 `银蛟山炼宝［七焰扇］` → `银蛇山炼宝［三焰扇］`（原文两写并存，通行银蛇山）。
     - **血影遁**（新反馈，网友指出）：真正来源是第 296 章萧老爷子祖孙为谢恩献上的**兽皮书**，书中功法名「疾风九变」＝一套法诀＋一套身法＋**两门密术（匿风术、血影遁）**；韩立凭过目不忘通解上古妖文后在第 605 章译出，只取两门密术（法诀与身法人类修到一半会爆体）。**风雷翅是另一回事**：风希以化形末期雷鹏骸骨加灵禽材料炼成（第 545–548 章）。原条目把「雷鹏遗刻载妖文、唯血影遁被习得」当来源，是二手解析的口径，已删。集数补 **第 32 集**（京城篇萧家赠书），第 132 集只保留「风雷翅认主后以此翼遁走」。
  ② **反馈渠道改向**：四处入口（hero / `.home-note` / `.img-note` / 页脚）改指 B 站视频评论区 `BV1Ameq6vECK`，GitHub Issues 只留技术问题；`verify.mjs` 的对应断言同步改成「`__comments` 为 0 + B 站入口 ≥ 2 + Issues 入口 ≥ 1」（旧断言要求 Issues ≥ 3，会假失败）。
  ③ **口径补强**：「地理考据」把「大晋方位 · 原著两说」改写为「**原文结论 + 图上口径**」—— 第 358 章可支撑的是「越国 → 九国盟 → 慕兰草原 → 大晋」的**南向通道**，第 670 章的阗天城属九国盟（本就在天南之南），两者不冲突；图上排在东侧是**可读性选择**，明写「读的是谁挨着谁，不是方位角」。另补一行「天南有多大？」：原著无数值，只有相对量级（大晋≈10 天南、万岭山脉连绵百万里、无边海元婴飞上百年），**任何具体平方公里都是同人推算**。
  ④ **核查后确认不改**（避免下一轮重复劳动）：灵界「西北角是飞灵族」不成立（原文西北角是人族/妖族/灵族/木族/夜叉族/影族六七族，站上飞灵族本在西南）；「天天城」人界篇 0 次（疑指阗天城）；比例类（大晋大小、乱星海太近/太大、无边海太窄、人界像太阳系）全部只回口径不动布局；「为什么视频里图不完整」属视频剪辑。
  ⑤ **验收**：`verify.mjs` 52/52（七库计数仍 263/42/65/71/53/44/34）；`stamp.mjs` 六个锚点各命中 1 次；页面实查：新串（疾风九变/匿风术/六连殿悬赏猎杀/原著未标初/中/后期/坠魔谷古修遗物）全在，旧串（雷鹏遗刻/黑煞教镇教水兽/大晋第一修士/银蛇山段落）全无，B 站入口 4 个、Issues 入口 1 个。
  ⑥ **顺手修掉一处长期存在的渲染 bug（用户点名一起修）**：`cardHTML` 的 rows 用 `(rw.always || c[rw.f])` 判渲染，而五库配置里 `结局` 一行都带 `always:true` ⇒ **凡是没有 `e` 字段的记录，卡片上就直接印出字面量「结局 undefined」**。实测七库 307 条里 **111 条**中招（功法 53 条里绝大多数、阵法/符箓若干 —— 这些条目本来就没有「结局」概念）。改法：条件收成 `c[rw.f] ? … : ""`，并把五处 `always:true` 删除（`always` 语义随之取消，别再有人加回来）。**不要用「给 111 条补 e」的方式修**：那是编内容，且「结局」对凡人武学/基础符箓本就不适用。同批在 `verify.mjs` 加一条**渲染结果**断言「卡片里没有 undefined / NaN 残字」（扫七库全部卡片的 `innerText`），51 → 52 条。

## 11. README 宣传图 / 封面更新流程（2026-10-12 实战沉淀）

> 适用范围：更新 `README.md` 的「页面速览」截图网格、重新生成封面、修订「特性 / 收录内容」数字。全流程**不 commit**（README 更新任务由用户明确「完成后不要 commit」）；`public/index.html` 若有未提交改动，**一律不动、不随 commit**（那是用户自己的进行中工作）。

### 11.1 截图：逐视图顶屏截图法（推荐，不依赖整页长图）

`dev/tools/readme-shots.py` 只认「手工整页长图 → 裁 16:10」，且 SHOTS 表只有 7 个视图、无法覆盖新增的功法/阵法/符箓/修仙界全图。**2026-10-12 起改用手法**：headless Chrome 逐视图顶屏截图，产出全部 11 个视图的 1440×900 顶屏画面，直接够 README 用：

1. **起服务**：`cd <repo> && python3 -m http.server 8123 --directory public`（本地静态服务）。
2. **截图脚本**：对每个视图**开独立 Chrome 实例**（不能用单实例连续导航），加载 `http://localhost:8123/?shot=<name>#v-<view>`，固定视口 1440×900@2x（`Emulation.setDeviceMetricsOverride`），等待 3.8s 后取顶屏。核心是 `?shot=<name>` + 完整 hash：
   - `?shot=<name>` 是截图辅助参数（激活目标视图、避免时序竞争）；hash 必须带 `v-` 前缀（`#v-chars`，写 `#chars` 会被 SPA 回退到 v-home）。
   - 11 个视图：`v-home` 首页 / `v-chars` 人物图谱 / `v-lore` 剧情速览 / `v-map` 修仙界全图 / `v-realms` 境界体系 / `v-beasts` 灵兽灵虫 / `v-herbs` 灵草丹药 / `v-treasures` 法器法宝 / `v-gongfa` 功法 / `v-zhenfa` 阵法 / `v-fu` 符箓。
3. **压图入库**：把每视图顶屏 2x PNG 缩为 **1440×900 WebP（quality=80, method=6）**，写入 `image/README/shots/`，命名 `01-home.webp` ～ `11-map.webp`（顺序即 README 展示顺序）。
4. **死路（已验证，勿重试）**：
   - `Page.captureScreenshot` + `captureBeyondViewport` 在多视图导航后**反复返回同一帧**（headless 合成器时序问题）；`--run-all-compositor-stages-before-draw` 无效。
   - 单 Chrome 实例内连续导航改 hash → **所有视图截到首页**（视图回退）。
   - hash 漏写 `v-` 前缀（`#chars`）→ SPA 回退 v-home。
   - 可行方案的脚本示例（临时目录，不入库）：`/tmp/fr-shots/shot-one.mjs`（每视图独立实例 + 完整加载 + 滚动偏移分段）；`stitch.py` 拼接**不用**——顶屏 y0000 画面即够。

### 11.2 README「页面速览」结构（2026-10-12 版）

```
封面（image/README/shots/封面.png，width=840）
│
修仙界全图横幅（11-map.webp，width=840，深链 #v-map）      ← 新增视图作独立横幅置顶
│
5 行 × 2 视图网格（各 width=400，配表头标题）：
  首页|人物图谱（01|02）→ 剧情速览|境界体系（03|04）→ 灵兽灵虫|灵草丹药（05|06）
  → 法器法宝|功法（07|08）→ 阵法|符箓（09|10）
```

- 每个 `<a href>` 深链指向对应视图：`https://bunnychen.top/fanren-wiki/#v-chars` 等；单条记录深链示例 `#v-treasures/tres-12`、`#v-gongfa/gongfa-5`。
- 封面在 README 中以 840 宽展示；封面文件落盘为 **1680×945 PNG（2x），量化 256 色压体积**（约 1MB）。

### 11.3 数字核实方法（改「特性 / 收录内容」前必读，勿凭记忆写）

用 node 直接统计 `public/index.html` 内的数据常量，**不要猜**。2026-10-12 已核实、可直接采用（README 已按此更新）：

| 项 | 数值 | 统计口径 |
|---|---|---|
| 人物图谱 | **263 收录 / 233 唯一 / 6 篇章** | DATA 六数组长度合计（跨篇重复收录为设计） |
| 灵兽 / 灵草 / 法宝 | **42 / 65 / 71** | BEASTS / HERBS / TREASURES 长度 |
| 功法 / 阵法 / 符箓 | **53（动画 21）/ 44（动画 18）/ 34（动画 18）** | GONGFA / ZHENFA / FU 长度（含 `anim:1` 计数） |
| 修仙界全图 | **156 地点（LOCS）/ 22 区域（REGIONS）/ 10 巡游阶段（STAGES 共 11 项含「全部」）/ 97 旅程节点（JOURNEY，76 个不同站点）** | 各常量长度 |
| 情节梳理 | **11 卷 / 55 地点篇 / 388 步** | PLOT_VOLS（⚠️ 曾写 333，2026-10-12 实测为 **388**，README 已改） |
| 核心圈 | **87**（被引 ≥ 5；README 曾写 81，页面 tab 已显示「核心圈 87」，以页面为准） | `coreCount()` |
| 关系图谱 | **105 位**核心角色（被引 ≥ 3） | `#graph-core-n` 运行时值 |

- ⚠️ **未上线的功能不要宣传**：`#v-map` 的「地理考据」抽屉（`btnGw` / `gwDrawer`）当前是**未提交改动**（工作区 `M public/index.html`）、内容注入未实现 —— README 只写「索引 / 播放 / 探索 / 舆图原图」，不写「地理考据」。写 README 前先 `git status --short` 看工作区有没有这类半成品。
- 统计脚本示例（防 timeout 用 node 而非 python 读大文件）：`/tmp/fr-shots/count.js`（`LOCS/REGIONS/STAGES/JOURNEY` 用 `var X=[...];` 段、PLOT_VOLS 用 `const PLOT_VOLS = [ ... ];` 段做正则计数）。

### 11.4 封面生成流程（doubao-creative-design，pure-image 横向 Banner）

- **画布已存在**：`cws_58243300018383874`（2026-10-12 建，路径 `/deliverables/readme-cover`，含 v1 `eN5aQ30o-4IsGg5KXru-0201` 与 v2 `fCIqdkJH-4IjihNBsGI-0201`）。下次改封面**复用此画布**，勿新建。
- **流程**（pure-image）：`design-workspace +workspace-create` → 主 Agent `present_files(<workspace_id>)` 交付画布卡片 → 写 `.creative-design/readme-cover/brief.md` → 读 `media-banner.md`（16:9 横向）+ `prompt-guide.md` + `image-quality-guide.md` → `image_gen` / `image_edit` → **双通道闭环**：`design-cli +create`（用工具返回的原始短链；v2 基于 v1 重绘时填 `<source_ids>` 继承血缘）→ `+get` 回读 → 交付 → 下载替换 `image/README/shots/封面.png`。
- **文字规则**：图内中文必须用中文引号“”标注（禁止其他符号），生成后**逐字 OCR 核对**；缩略图 OCR 不可靠（384px 缩略图把「灵兽」误读成「灵宠」，真实 2730×1536 图是对的）——核对以完整尺寸图为准。
- **v2 人物规格**：右侧人物为**韩立**（动画版形象：青年书生、清秀端正、剑眉、目光坚毅、黑发束高髻玉簪固定、玄青交领古袍、左手掌中悬浮青翠**掌天瓶**），构图与文字（标题/副标/六标签）保持不变。
- **已知瑕疵（2026-10-12 状态）**：画面右上角多一小处「道友请进」浮字（v1、v2 均有），左侧钩子正常。用户如要求修正：基于 v2 短链再 `image_edit` 局部去除即可（按 skill 规则不自动重生，等用户明确要求）。

### 11.5 Git 红线（README 更新任务通用）

- **不 commit**（用户明确）；交付前 `git status --short` 核对：应只见 `README.md` + `image/README/shots/*` 改动，`public/index.html` 若有 `M` 是用户自己的未提交改动，**勿动勿提交**。
- `dev/tools/readme-shots.py` 可复跑（依赖整页长图源，见 11.1 差异说明）；`.creative-design/` 是 skill 过程文件（brief 等），不入库引用。
