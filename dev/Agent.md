# 《凡人修仙传》百科 · 全篇资料图谱 — 开发文档

> 本文档供后续 LLM（或开发者）快速理解本项目并上手开发。先读本节即可动手，细节按需跳读。

## 1. 项目是什么

一个**自包含单页 HTML** 的《凡人修仙传》全篇资料可视化站点，用户用于回忆剧情、检索人物、理解境界体系、查灵兽/丹药/法宝。

- **默认首页（v-home）**：百科式介绍页——网站命名《凡人修仙传》百科，含"为什么做这个网站"（`<details class="home-why">` 折叠，摘要一句话 + "展开全文"，默认收起以缩首屏）、六大收录板块入口卡片、"问道自述"、"收录说明"、"数据来源"。用户明确要求"首页不要开门见山放人物图鉴"。（2026-09-17 已删掉"页面包含"功能清单区块——功能靠界面自身说明，不再用一段清单复述。）
- **降噪优先**：人物图谱默认只显示「核心圈」（被引 ≥ 5 的条目），其余 200 余位路人不喧宾夺主；`#tabs` 内的分段选择器一键切「核心圈 N / 全部 221」。互引网络与定位能力见 §5。
- 收录 **6 个篇章、221 条人物记录**（跨篇章重复出现的角色按"出现即写"重复收录，如韩立 6 篇、南宫婉 4 篇）+ **灵兽灵虫 40 条**（第四视图）+ **灵草丹药 64 条**（第五视图）+ **法器法宝 65 条**（第六视图）。
- 每人默认卡片显示：**头像图、名字、身份、本篇修为、关系/势力/种族标签**；点击展开显示**生平梗概与结局**（默认不剧透）。**修为演进 ev 字段已全量补齐（221/221）**，卡片修为行显示本篇内的境界变化（如"炼气→筑基→结丹后期"）。
- 页面支持 **人物图片**（优先动画形象）、**境界图表**（外部 cultivation-chart.js）、**妖兽等级制度**与**灵药年份等级**对照区块。

## 2. 目录结构

```
fanren-wiki/                # 独立仓库（2026-09-17 从主站拆出，git 历史保留）
├── public/                 # ← 唯一发布目录，GitHub Actions 只上传这里
│   ├── index.html          # 唯一交付物（自包含：内联 CSS/JS + 相对路径图片）
│   ├── cultivation.css     # 图表样式（境界阶梯【用户自加部分原样不改】+ 末尾追加的概览图表，见 §7）
│   ├── javascripts/
│   │   ├── cultivation-chart.js   # 境界阶梯图（本站自持，不再依赖主站）
│   │   ├── echarts.min.js         # ECharts 5.6.0 **按需构建包**（527KB，零 CDN，可重建）
│   │   └── overview-charts.js     # 人物关系图谱（力导向）+ 篇章×势力旭日图
│   ├── assets/             # 374 张图：360 张被引用（.webp/.jpg 混合，逐图最优）+ 14 张实名备用图，见 §6
│   ├── sitemap.xml
│   └── robots.txt
└── dev/                    # 开发资料：永不上站；只跟踪文档与工具（见下方说明）
    ├── Agent.md            # 本文档
    ├── _review.md          # 数据审校笔记
    ├── tools/              # 在用的工具：image-slim.py（图片瘦身，见 §6）、verify.mjs（零依赖验收，见 §8.3）、echarts-entry.js（ECharts 按需构建入口，见 §7）、readme-shots.py（README 宣传图：整页截图 → 16:10 缩略图，输出 image/README/shots/，原图被 .gitignore 忽略）、stamp.mjs（部署时把「最后更新」+ 提交说明注入 index.html、把 lastmod 注入 sitemap.xml，见 §7「元数据」）
    ├── _image-slim-report.json  # 瘦身逐图决策记录（体积/SSIM/所选质量档）
    ├── _backup/            # 历史堆积：index-vNN.html 版本次级（21 个）+ 一次性的 migrate 脚本（apply_*/add_*/fix_*/sync_*）+ meta/stories/ev/herbs_data/treasures_data 等中间数据
    └── watermark.svg       # 仅供 _backup/index-v*.html 引用的水印瓦片（当前页面已内联 base64）
```

- `_backup/` 里的脚本不参与运行、也不要“顺手执行”：它们是当时的字符串级插入脚本，路径写死在旧仓库（`Lizhenghe-Chen.github.io/...`）。要重跑得先把路径改回来。
- ⚠️ `dev/unused-assets/` **已不存在**：那批备用图已全部清理到归档目录（见 §6 原图备份）。目前未被引用的 14 张实名图留在 `public/assets/` 里，由验收脚本作为提示列出（见 §6）。

- 工作目录：`~/Documents/GitProjects/fanren-wiki/`（原地址 `Lizhenghe-Chen.github.io/docs/docs/Other/fanren-characters/` 已停用，主站只留跳转桩）；早期旧版在 `~/Doubao/chats/2026-09-14/new-chat/fanren-characters/`（仅参照）。
- 线上地址：`https://bunnychen.top/fanren-wiki/`（项目页，继承用户站自定义域名，本仓库无需 CNAME）。
- 参考资料页仍在主站：`https://bunnychen.top/docs/Other/fanren-xiuxian/`（**仅作首页介绍文案的素材来源**）。
- **反馈 / 勘误统一走 GitHub Issues**（2026-09-17 起）：`https://github.com/Lizhenghe-Chen/fanren-wiki/issues` —— **直接给 issues 列表页**，不用 `/new/choose` 模板选择页（用户明确「不用什么 label，直接到 issues 页面就行」）。⚠️ **主站评论区已不再是反馈入口**，不要再把勘误/反馈链接指回 `bunnychen.top/docs/.../#__comments`。
- **开发资料一律放进 `dev/`**：发布边界由目录决定（只上传 `public/`），不要把 `_backup/`、自检截图、笔记放进 `public/`。
- ⚠️ **`dev/` 的跟踪策略（2026-09-18 调整）**：**只跟踪「活文档 + 工具」**（`Agent.md`、`_review.md`、`tools/`、`_image-slim-report.json`），`_backup/`、`demos/`、`watermark.svg` 仍在 `.gitignore` 里（仅本地保留）。理由是前者没有版本历史就只能靠本机磁盘活着、且与 `public/` 的改动一一对应；后者要么 git 历史里本来就有一份（`_backup/index-vNN.html` 就是各次提交的副本），要么是一次性产物。
  ⚠️ **`dev/` 仍然不会上站**（CI 只传 `public/`）：公开可见 ≠ 交付物，README 里不要把 `dev/` 当交付物引用。

## 3. 页面结构：七视图 + hash 路由

页面**不是单页长滚**，而是**页内多视图切换**（用户明确要求"分页面"，否决过"左右分栏"）：

```
<body>
  <div class="asset-manifest"></div>          # 图片引用隐藏清单（见 §6）
  <nav class="topnav">                        # 顶部主导航（sticky top:0，48px 内容高+1px 边框=49px）：首页 | 人物图谱 | 剧情速览 | 境界体系 | 灵兽灵虫 | 灵草丹药 | 法器法宝 + 搜索按钮 + **GitHub 图标（≥1100px 才显示，见下）** + 持续更新·作者主页·日期
  <div class="view" id="v-home">              # 视图0 首页（默认）
    hero（标题/统计/按钮） → 为什么做这个网站（<details class="home-why">，默认收起） → **篇章×势力旭日图 #chart-sunburst**（ECharts sunburst，首页"收录内容"之前） → 收录内容 6 卡 → 问道自述（.home-quest） → 收录说明 → 数据来源（.src-list） → **开源（.repo-card）**
  </div>
  <div class="view" id="v-chars">             # 视图1 人物图谱
    .page-head（紧凑页头，含唯一的 h1 + 统计） → sticky .navbar（top:49px：.tabs 篇章 tab + .seg 核心圈切换 + 搜索框） → .img-note 图片准确性声明（<details>，默认收起） → **人物关系图谱 <details class="graph-fold">**（ECharts 力导向 #chart-graph，默认展开，可折叠） → 卡片区 <main id="characters">
  </div>
  <div class="view" id="v-lore">              # 视图2 剧情速览（约 1 屏）
    .page-head（h1 + 统计 #lore-nodes） → 韩立境界演进时间轴 #timeline → 故事脉络 6 卡 → 双韩立因果闭环
  </div>
  <div class="view" id="v-realms">            # 视图3 境界体系（约 1 屏）
    .page-head → 境界 rail → 3 个 data-cultivation 图表 → 各篇人数柱状 → 图例
  </div>
  <div class="view" id="v-beasts">            # 视图4 灵兽灵虫（约 3 屏）
    .page-head（含 .ph-lead 一句话引导） → 妖兽等级制度 rail #beastRail → 分类 tab #beastTabs → 共用搜索框 .lib-search（#beastSearchInput） → 卡片区 <div class="grid beast-grid" id="beasts">
  </div>
  <div class="view" id="v-herbs">             # 视图5 灵草丹药（约 2-3 屏）
    .page-head → 灵药年份等级 rail #herbRail → 分类 tab #herbTabs → 共用搜索框 .lib-search（#herbSearchInput） → 卡片区 <div class="grid herb-grid" id="herbs">
  </div>
  <div class="view" id="v-treasures">         # 视图6 法器法宝（约 2-3 屏）
    .page-head → 法宝品阶 rail #treasureRail → 分类 tab #treasureTabs → 共用搜索框 .lib-search（#treasureSearchInput） → 展示计数 #treasureShown → 卡片区 #treasureGrid
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
- **新增视图**：加一个 `<div class="view" id="v-xxx">`（内部只放一个 `h1`），在 `VIEWS` 数组里登记，topnav 加链接即可。
- **移动端**：`@media (max-width:640px)` 下 topnav 允许横向滚动（隐藏 `.tn-update`）、`.navbar{top:45px}`、`.tabs` 保持单行横向滚动（历史教训：窄屏换行成两行 = 109px 常驻高度）。
- **⚠ 锚点注释会撞车**：`/* ===== 韩立境界时间轴 ===== */` 在 `<style>`（`.timeline-sec` 注释）与 `<script>`（`const TL` 前）各出现一次——脚本插入若用该注释定位 JS 数据，会误命中 CSS 区导致 `BEASTS is not defined`。定位 JS 数据应匹配 `];\n\n/* ===== 韩立境界时间轴 ===== */\nconst TL = [` 整段。历史修复：`_backup/fix_beast_data_pos.py`。

## 4. 数据模型（`const DATA`）

`DATA` 是 6 键对象，键 = 篇章 id，值 = 人物数组：

| 键 | 篇章 | 条数 |
|---|---|---|
| `qixuanmen` | 七玄门 | 16 |
| `huangfeng` | 黄枫谷 | 29 |
| `luanxing` | 乱星海 | 32 |
| `dajin` | 大晋 | 55 |
| `lingjie` | 灵界 | 39 |
| `xianjie` | 仙界 | 50 |

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
| `ev` | 本篇修为演进 | **2026-09-16 已全量补齐 221/221**（v16），如"炼气→筑基→结丹后期（天灵根）"；凡人角色写"凡人"或"凡人（无灵根）" |

**新增/修改人物**：直接在 `DATA` 对应数组追加/编辑对象即可；跨篇角色在每篇各自收录（可各自配不同图片，如韩立每篇不同形象）。
**批量补 ev 参考**：`/tmp/add_ev.py`（173 条映射表 + 字符串级精确插入逻辑，含"数花括号深度找记录闭合"的方法，可复用）。

### 条目标识（`data-key`）与四库统一

- 四库记录在渲染时都带 **`data-key`**，是深链与互引网络的主键：人物 `"<篇章id>-<序号>"`（如 `qixuanmen-0`）、灵兽 `beast-0`、灵草 `herb-0`、法宝 `tres-12`。**分隔符是 `-`，不能用 `#`**（`#` 会把 URL 截断，深链传不到）。
- 四库在 `LIBS` 里各占一项（`id/label/prefix/…`），搜索面板、互引 chip、`gotoEntry` 都靠它统一分发到对应视图与渲染函数。
- 人物图谱另有 **核心圈降噪**：`CORE_MIN = 5`（被引 ≥ 5 才入圈）。依据是实测分布——互引网络里 381 条有 208 条被引为 0、仅 38 条 ≥ 5，长尾极端；默认只显示核心圈，顶栏分段选择器可一键回全部。

### 灵兽灵虫数据（`BEASTS` / `BEAST_CATS` / `BEAST_RAIL`）

| 常量 | 含义 | 备注 |
|---|---|---|
| `BEASTS` | 40 条灵兽灵虫 | 字段同人物（`n/t/r/e/img/s/rel/camp/race/ev`），另加 `cat` 分类键 |
| `BEAST_CATS` | 5 类 + 全部 | `chong`灵虫 / `shou`灵兽 / `yao`妖兽妖修 / `zhen`真灵·神兽 / `lian`炼尸魔物 |
| `BEAST_RAIL` | 妖兽等级制度 6 格 | 原著 1-13 级 + 真灵级，对应人界修士境界（见页面说明） |

- `r` 字段在此处为**妖兽等级**（如"二级妖兽（筑基期）""十级妖修（≈元婴后期）"），部分带 `ev` 演进（如噬金虫"虫群→噬金仙→太乙→吞噬道祖"）。
- 等级制度口径：一级≈炼气 / 二~四级≈筑基 / 五~七级≈结丹（凝妖丹）/ 八~十级≈元婴（化形期）/ 化神级及以上≈化神—大乘（十级后不再用数字等级，直接以修士境界命名）。

### 灵草丹药数据（`HERBS` / `HERB_CATS` / `HERB_RAIL`）

| 常量 | 含义 | 备注 |
|---|---|---|
| `HERBS` | **64 条**灵草丹药 | 字段同灵兽（`n/t/r/e/img/s/rel/camp`），另加 `cat` 分类键，无 `race/ev` |
| `HERB_CATS` | 5 类 + 全部 | `lingcao`灵草灵药 / `tiancai`天材地宝 / `tupo`突破丹药 / `fuzhu`辅助丹药 / `danfang`丹方·主材 |
| `HERB_RAIL` | 灵药年份等级 6 格 | 普通草药≈凡人—炼气 / 百年≈炼气—筑基 / 千年≈筑基—结丹 / 万年≈结丹—元婴 / 灵界奇珍≈化神—大乘 / 仙界仙药≈真仙—道祖 |

- `r` 字段在此处为**灵药年份/品阶/对应境界用途**（如"千年灵药（≈结丹—元婴用途）""百年灵药（≈筑基用途）"）。
- 数据来源：起点《凡人必备手册》第二版（最权威）+ 原著情节 + 本地资料库交叉验证，全部标注"已查证"。
- 关键核查结论：筑基丹三大主药=玉髓芝+紫猴花+天灵果（三源一致）；"生生造化丹"官方名为造化丹（灵烛果为主材）；用户清单中"元婴丹/化神丹/大衍丹/洗髓丹/回春丹"等为原著不存在或别名，已按原著名称收录或拒绝。

### 法器法宝数据（`TREASURES` / `TREASURE_CATS` / `TREASURE_RAIL`）

| 常量 | 含义 | 备注 |
|---|---|---|
| `TREASURES` | 65 条法器法宝 | 字段同灵草（`n/t/r/e/s/rel/camp` + `cat`），记录前有分类注释 `/* ===== xxx ===== */` |
| `TREASURE_CATS` | 6 类 + 全部 | `xuanbao`玄天之宝·至宝 / `benming`本命法宝 / `tongji`神通秘术 / `gongfa`功法秘典 / `fulu`符箓·阵法 / `qita`其他法宝 |
| `TREASURE_RAIL` | 法宝品阶 5 格 | 法器→灵器→法宝→仙器→玄天之宝（近似境界对照） |

- **⚠ 配图未完成**：v-treasures 数据中原含 `img` 字段引用（如 `xuantianhulu.jpg`、`balinchi.jpg`），因用户 2026-09-16 叫停图片工作，**61 个指向不存在文件的 img 字段已被移除**（见 §10 待补清单），渲染自动回退首字占位。后续恢复图片时：下载文件到 assets/ → 数据补 `img:"文件名"` → manifest 登记 → 自检。

## 5. 关键函数与交互

文件末尾初始化：`renderTabs(); renderMain(); applyFilter();` + 视图切换 IIFE + 各视图渲染函数。

| 函数 | 作用 |
|---|---|
| `renderTimeline()` | 渲染韩立境界时间轴（`TL` 数据，14 节点；`#lore-nodes` 填节点数） |
| `renderTabs()` | 生成篇章 tab + 核心圈「核心圈 N / 全部 221」分段选择器（`.seg`） |
| `renderMain()` | 遍历 `DATA` 生成卡片 DOM（含图片/占位/标签/修为 ev/展开区/互引区） |
| `renderBars()` | 各篇人数柱状图 |
| `renderLegend()` | 图例 |
| `toggleCard(el)` | 点击卡片展开/收起生平（默认收起不剧透）；同时把 URL 同步成深链（可复制分享） |
| `applyFilter()` | 人物卡三条件过滤：篇章 tab + 搜索关键词 + 核心圈降噪（`coreOk`）；无可见卡的篇章区块整块隐藏 |
| `isCore(key)` / `coreCount()` / `CORE_MIN` | 核心圈判定与计数（被引 ≥ 5） |
| `haystack(o)` | 三库**统一的命中范围**：名称/称号/等级/结局/演进/生平/关系/出处/种族 —— 与全库搜索面板同一套字段。改搜索命中范围就改这一处 |
| `initCardLib(cfg)` + `BEAST_LIB` / `HERB_LIB` | 灵兽、灵草**共用的一套实现**（配置驱动：库 id、数据、分类、文案、字段差异全在配置里）。实例按库 id 存进 `LIB_UI`，`gotoEntry` 用它复位筛选。改一库行为就是改这一处 |
| `renderTreasureRail()` / `renderTreasureTabs()` / `renderTreasures(list)` / `applyTreasureFilter()` | 法宝视图（**不并入上面的工厂**：它按筛选结果整表重渲染、卡片结构也不同） |
| `switchView(id)` | 切视图（同步 topnav 高亮；非法 id 回退 v-home） |
| `parseHash()` / `setHash(view,target,replace)` | 读写地址（深链的真相源） |
| `applyHash()` | `hashchange` + `popstate` 的统一入口：切视图 + 有 target 则展开定位 |
| `gotoEntry(key, keepHash)` | 跨库定位：切库/清筛选（**并退出核心圈降噪**）/展开目标卡/滚到 sticky 顶栏之下（双 rAF 延后，等视图切换的重排完成） |
| `INDEX` / `ENTRY_BY_KEY` / `REFS` / `REF_SCORE` / `LIBS` | 跨库索引与互引网络：一次正则扫过全部文本（长名优先匹配，`baseName()` 合并同名，如韩立 6 篇合成一个被引数） |
| `refCount(key)` / `refsBlock(key)` / `refBadge(key)` | 互引展示：「相关条目」/「被引用于」 chip（各取前 8 + `+N`）与「被引 N」徽记 |
| `spotOpen/spotRender/spotMove/spotClose` | 全站搜索面板（`⌘K` / `Ctrl+K` / `/` 唤起；390 条、跨库分组、关键词高亮、方向键+Enter 定位） |
| `back-top` 逻辑 | 滚过 700px 后 `.show` → 点击回顶（尊重 `prefers-reduced-motion`）；圆环 `strokeDashoffset = C × (1 − 已滚比例)`（`C = 2πr`，r 取 `<circle>` 的 21），监听 `scroll` / `resize` + `hashchange`（切视图后文档总高会变、滚动位置不变，**不会触发 scroll**，所以必须补一次） |

搜索框匹配卡片 `data-name` / `data-aka`（别名）。

**启动顺序**（文件末尾 IIFE，顺序有依赖，别乱动）：互引索引构建（`INDEX`→`ENTRY_BY_KEY`→`REFS`→`REF_SCORE`）→ 搜索面板接线 → 首页统计（读 DATA/BEASTS/HERBS/TREASURES 长度填 `#home-st-chars` 等）→ 各视图渲染 → `renderMain()` **然后** `renderTabs()`（「核心圈 N」计数依赖本轮渲染出的被引数，**顺序颠倒会把计数算成 0**）→ `applyHash()`。

## 6. 图片体系（重要红线）

- **图片文件**：`public/assets/<拼音名>[_<篇章>].<ext>`，跨篇同角色可不同文件（如 `hanli_qixuanmen.webp` / `hanli_xianjie.webp`）。
  **扩展名不固定**：`.webp` 或 `.jpg` 都可能，**以文件实际存在为准，不要凭名字猜**（见下方「体积规范」）。
- **⚠️ 引用分两种，统计时必须都算**：① 页面里的字面量 `assets/xxx.ext`；② **数据里的 `img:"xxx.ext"` 字段**（渲染时才拼成路径，如丹药/灵草/法宝的 `img`）。
  只查字面量会漏掉大量图（`img` 字段引用有 **359** 处，渲染时才拼成路径）。当前真实引用 **360** 张、目录共 374 张（另 14 张为实名备用图）。曾因此误删了 5 张被数据引用的丹药图（`dan_blue/gold/green/purple/red.jpg`）。
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
  ③ 反向的“目录里有、页面没用”只打印提示、不判失败：当前有 14 张这样的实名备用图（bingfeng / dayan / dongxuaner / jintong / linghu / lingyuling / nangongwan / tihun / wangchan / xiangzhili / yinyue / yuanyao / yunlulaomo / ziling）。
  ⚠️ 其中多数**不在归档原图备份里**（那批是 143a8c9 时的 302 张），所以不要为了“干净”去删它们 —— 删了就丢唯一副本。
- **无图角色**：不硬凑图，卡片显示姓氏首字占位（渲染逻辑：`c.img ? '<img …>' : '<div class="ph">首字</div>'`）。
- **准确性声明**：页面已含多处声明（v-home 收录说明、hero 副标题、v-chars 卡片区上方橙色警示框、页脚）——图片是网络检索素材（动画截图/官方概念图/百科插画/同人立绘），受动画进度限制（播至人界篇·慕兰之战），灵界/仙界多数角色未在动画登场，**可能与官方形象存在偏差甚至错配**。此声明是用户明确要求，勿删除。
- **找图规范**：优先动画形象 → 官方概念图 → 百科插画 → 同人图；下载后必须用读图能力逐张核对角色身份、清晰度、无水印，错配宁可不用。用户提供图源优先级：百度图片 / 必应图片 / 搜狗图片 / 花瓣网 / B站专栏 / 豆瓣剧照 / 站酷 / trace.moe 识图。
- **删除图片引用的注意**：移除数据内 `img` 字段时，若字段在记录末尾会留下 `, }` 孤立逗号导致 JS SyntaxError；manifest 删除 url 会留下 `,,`。必须做全局清理：`re.sub(r',\s*}', '}')` + **循环** `re.sub(r',\s*,', ',')`（多层逗号需多次）+ `re.sub(r',\s*;', ';')`。

## 7. 样式与外部依赖

- 色板：深色底 + 金色（`--gold: #d4af6a` 系）+ oklch 派生，详见 `<style>` 顶部 CSS 变量。
- `cultivation-chart.js`（境界阶梯图的渲染逻辑）：**用户项目自带，不改**；图表用 `data-cultivation` 属性 + IntersectionObserver 延迟初始化，视图隐藏时切回会自动重播，**无需适配**。
- `cultivation.css`：**允许追加**（2026-09-18 改，原写「用户项目自带，不可修改」）。它是全站**唯一的外链样式表**、职责就是图表，把概览图表样式塞进 `index.html` 内联会把同一类东西劈成两处（图表样式一半在外链表、一半在内联），属于约束反噬；用户拍板「约束如果弄巧成拙就修改」。
  ✅ **追加规矩：只在文件末尾新增 `/* ===== 概览图表 ===== */` 段；不重排、不删改上方任何 `.cv-*` 规则**（那是用户原样的境界阶梯样式），并保持该文件的压缩单行风格。
- **ECharts 5.6.0 按需构建包**（`javascripts/echarts.min.js`，**527KB**；官方全量包 1006KB，本站只用到 graph + sunburst 两种图，故按需打包，入口与重建命令见 `dev/tools/echarts-entry.js`，许可头写在产物开头、`NOTICE` 有「第三方组件」段 —— 换版本或加图型必须同步改这两处）：零 CDN、零第三方请求，满足"静态资源无第三方请求"硬约束。配套 `javascripts/overview-charts.js`（IIFE 包裹，约 6.6KB）画两张图：
  - **首页旭日图** `#chart-sunburst`：中心"全书人物"→ 六篇章 → 各篇前 6 大势力 + 其他。数据直接复用主页面运行时的 `CHAPTERS` / `DATA[chapId]`，按 `camp` 字段统计（INDEX 条目不含 camp，必须遍历 DATA）。
  - **人物图谱力导向图** `#chart-graph`：基础名级被引 ≥ 3 的 34 个核心角色，节点大小 = `REF_SCORE`，颜色 = 首次登场篇章，连线 = `REFS[].out` 互引。分批生长动画（按篇章每 450ms 一批 setOption merge），`roam: 'move'` 只拖拽平移（禁滚轮缩放，避免和页面滚动冲突）。节点 click 通过改 `location.hash = 'v-chars/<key>'` 跳人物卡（`gotoEntry` 在主 IIFE 内外部访问不到，走 hash 路由）。
  - **初始化时机**：脚本在 `</body>` 前，但必须等 `window load` 后再 `sync()`，否则 echarts.init 时 canvas 尺寸为 0 只画出空圆环；`setTimeout(…, 300)` 再补一次 `resize()`。
  - **折叠**：图谱区包在 `<details class="graph-fold" open>` 里，默认展开；toggle 事件里 `setTimeout(resize, 60)` 修正收起后展开的 canvas 尺寸。
  - **配色只有一个来源**：篇章名与色值都取自 `CHAPTERS`（其 `color` 形如 `var(--c1)`）→ 运行时用 `getComputedStyle` 解析成具体色值（canvas 读不了 CSS 变量）。**不要在 JS 里再手抄一份 hex**：2026-09-18 之前那份就是这么来的，与页面 `--cN` 只有 c1 对得上（c2–c6 全错）。
  - **样式归属**：`.graph-fold` 一族与 `#chart-sunburst` / `#chart-graph` 的尺寸（含 ≤760px 降档）都在 `cultivation.css` 末尾的「概览图表」段。**画布高度不要再写回内联 `style`**。
- 字体：**纯系统字体栈**（`--font-serif` 优先 Songti SC / STSong，`--font-sans` 优先 PingFang SC / Microsoft YaHei，逐级回退）。2026-09-17 已移除 `miaoda.feishu.cn` 的 Noto 字体 CDN（省 11.35MB）：**静态资源 0 第三方请求**（唯一例外见下条「访问统计」），离线/`file://` 打开外观完全一致，**不要再引入外部字体**。
- **访问统计（不蒜子）**：首页 hero 统计行末的「次浏览」= `page_pv`，是全页唯一的外部请求。由 `public/index.html` 里一小段内联代码在**真实域名下**才发起（`file://` 与 `localhost/127.0.0.1` **不发起** ⇒ 本地预览零外部请求、也不会把调试流量写进线上计数）；本地想看效果加 `?stats=1`。
  · **口径**：每次载入都**直接上报一次并显示接口返回的累计值** —— 不写本地缓存、不做去重窗口（v28 那套「1 分钟内只计一次」已按用户要求移除，见 v33；**不要再加回来**）。刷新即 +1，这是不蒜子的 PV 语义，用户已接受。
  · **失败降级**：`#stat-views` 默认 `display:none`，取到值才显示 ⇒ 服务挂掉时首页不留空洞。
  · ⚠️ **自己发 JSONP**（`busuanzi.ibruce.info/busuanzi?jsonpCallback=__fwPv`）而**不是**引它那支 1.9KB 的 `busuanzi.pure.mini.js`：少一个请求，且能显式声明 `referrerPolicy='no-referrer-when-downgrade'` —— 默认的 `strict-origin-when-cross-origin` **只发 origin**，服务端拿不到路径，页面计数会退化成站点计数。
  ⚠️ **实测口径（2026-09-17）**：接口 `https://busuanzi.ibruce.info/busuanzi?jsonpCallback=cb` **只认 Referer**（不带 Referer 直接返回 `Bad Request`）；site 键 = Referer 的 host、page 键 = **host + 路径**（**查询串不参与**，fragment 不发）。
  ⚠️ **`site_uv` 不可信，所以只展示 PV、不展示「访客数」**：同 IP 同 UA 连打 3 次，`site_uv` 5→6→7 逐次递增（根本没去重）。
  ⚠️ `127.0.0.1` 是**全服共享桶**（实测 site_pv 已 1,079 万+、page_pv 37 万+），本地预览看到的大数字与本页无关，别当真。
- 无任何构建工具，原生 JS，`file://` 可直接打开（图片为相对路径，**转发时需连同 assets/ 一起**）。
- 首页样式类：`.home-section` / `.home-why`（`<details>` 折叠） / `.home-cards` / `.home-card` / `.home-note` / `.home-quest`（问道自述） / `.src-list`（数据来源）（`/* ===== 首页 ===== */` 段）。
- 全局复用类：`.page-head`（紧凑页头，内含唯一的 `h1` + `.stats` + `.ph-lead` 一句话引导；≤640px 收窄内边距） / `.seg`+`.seg-btn`（分段选择器） / `.lib-search`（三库共用搜索框，胶囊，与分类 tab 同一套形态与 10/12px 外边距） / `.ref-chips`+`.ref-chip`（互引 chip） / `.spot*`（搜索面板一整套） / `.back-top` / `.img-note`（`<details>` 免责声明）。

### 出处与防盗（改动前必读）

> ⚠️ **许可已改为 Apache-2.0（2026-09-17）**，水印的性质随之改变：它现在是**出处标识**，**不再是「禁止去除」的许可条件** —— Apache-2.0 不允许对下游附加额外限制（原文的“禁止商业使用”“禁止去除署名与水印”已删除）。页脚文案已同步为“欢迎保留”。**不要再把水印写回成强制条款。**
> 但“不在卡片图上盖章”这条**依然成立** —— 理由不变（图不是你画的），且第三方图片**本来就不在 Apache-2.0 范围内**。

- **全页水印**：`.watermark`（`position:fixed` 全屏平铺）的背景图**已内联为 base64 data URI**，不再引用 `watermark.svg`——`dev/watermark.svg` 仅为 `dev/_backup/index-v*.html` 保留，**勿删**（删了旧备份开出来就没水印）。改水印要改那段 base64，别改回外部文件引用。
- **无 `@media print` 例外**：打印/导出 PDF 也带水印（`position:fixed` 在分页媒体里逐页重复），别再加 `display:none` 把它关掉。
- **不在卡片图片上盖章**：曾经加过 `.card-top::after{content:"bunnychen.top"}` 的右下角标，**已移除且不要再加**——图片本身是网络检索的第三方素材，不是本站作品，在别人的图上盖自己的出处站不住脚（真有争议时也不占理）。图片区保持干净。
- **元数据**：`<head>` 里三件套——版权注释块（含版本/日期/仓库地址，抄整页的人会把出处一起带走）、`<link rel="canonical">`、JSON-LD（author / datePublished / dateModified / license / isBasedOn）。**改版必须同步**。许可字段当前为 `https://www.apache.org/licenses/LICENSE-2.0`。
- **「最后更新」四处 + 两处元信息：全部自动注入，不要手写**（`dev/tools/stamp.mjs`，2026-09-20 起）。四处 = 页脚「最后更新」/ 头注释 / JSON-LD `dateModified` / 导航栏「更新 YYYY-MM-DD」，另加页脚 `.stamp-note` 里的本次提交说明首行（压平 → HTML 转义 → 截断 56 码点）与 `public/sitemap.xml` 的 `<lastmod>`。取值 = `git log -1` 的 `%cs` + `%s`；GitHub Actions 在 `upload-pages-artifact` **之前**跑 `node dev/tools/stamp.mjs --write`，改的是 runner 工作区里的 `public/index.html` 与 `public/sitemap.xml`，**不进 git**。
  · **为什么不做成页面运行时拉 `api.github.com`**（2026-09-20 用户二选一后拍板 CI 注入）：国内经常超时（本站读者大多在国内）+ 未认证限流 60 次/小时/IP；静态注入零新增请求（不动「静态资源 0 第三方请求」红线），关掉 JS / 爬虫抓取 / 另存到本地日期与 JSON-LD 都是对的。
  · **锚点必须恰好命中 1 次**，否则脚本报错退出且不写文件：动这些锚点（尤其页脚 `.stamp-note` 那个 `<span>`）就要同步改 `stamp.mjs` 的 `RULES`，宁可部署失败也不要静默退回手写（v38 之前手写就漂移过：导航 09-17 / 页脚 09-19 打架）。
  · ⚠️ **本地不要对 `public/index.html` 跑 `--write`**（2026-09-20 实测坑）：VS Code 编辑器缓冲区会把它自己那份内容回写，把脚本写入的结果覆盖成"吞字"的坏文本（`<span …>` 变 `s`、`最后更新：` 整段消失），脚本自己的读回校验都查不出来，只能 `git checkout` 恢复。本地要动这四处日期就用编辑工具手改、保持同值（部署时会被刷成最新）；不带参数的体检模式只读不写，本地可放心跑。
- **明确不做**：禁用右键/选择、JS 混淆、反调试——伤体验与无障碍、几秒可绕过，已否决。

## 8. 开发流程（照做）

1. **先备份**：`cp public/index.html dev/_backup/index-vX.html`（版本号递增，防改坏）。
2. 小改动直接改；大改（结构/批量数据）参照"对象级替换 + 章节标记定位"脚本模式。**改 JS 数据用字符串级精确插入**（数花括号深度找记录闭合，避免 to_json 全量重排破坏格式；`DATA.xxx` 段正则 `(DATA\.%s = \[)(.*?)(\];)`）。
3. **自检（唯一验收方式，改完必须全绿）**：
   ```bash
   node dev/tools/verify.mjs                                   # 默认验 ./public/index.html（file://）
   node dev/tools/verify.mjs --url http://localhost:8899/index.html   # 也可指定 URL
   ```
   **零依赖**：Node ≥ 22 内置 `WebSocket`/`fetch` + 本机 Chrome，自己拉起 headless Chrome 走 CDP，**不装 puppeteer/playwright**。当前 35 条断言：七视图容器、四库卡片数（221/40/64/65）、**图片引用无缺图 + 全部能解码**、互引网络规模、**每个视图有且仅有一个 h1**、**开源入口齐全（顶栏图标 / hero / 首页卡片 / 页脚同指一仓）**、**反馈入口统一指向 GitHub Issues**、核心圈默认生效且可切回全部、桌面 1440×900 与移动 390×844 双视口的横向溢出与"竖条文本"、篇章筛选、**三库分类筛选（含 tab 计数一致性）与三库搜索**、搜索定位、互引 chip 跳转、返回顶部与进度环、深链冷启动、点卡片同步 URL、浏览器返回后视图与地址一致、**静态资源无第三方请求**、**统计位默认隐藏 + 本地不发起上报 + 取到值后显示累计次数（千位分隔）+ 统计位可见时双视口无溢出**、**两张概览图表渲染与配色来源 + 悬浮详情 + 图谱节点点击跳转 + 折叠展开后 canvas 尺寸恢复**、0 控制台报错。
   - 断言失败先看输出里打印的**实际值**再动代码（有 3 条断言曾是自己写错：阈值拍脑袋、期望值写反、把 `<link rel=canonical>` 当资源请求）。
   - ⚠️ **视口用 `Emulation.setDeviceMetricsOverride` 设置**：VS Code 内置浏览器**无视** `setViewportSize()`（请求 1440 实得 729），别拿它做响应式验收，也别用 iframe 顶替（Promises 会永不 resolve）。
   - 快速 JS 语法检查：提取内联 `<script>` 块逐个 `node --check`。
   - ⚠️ **不要用 `perl -0pi` 改校验脚本**：`@` 在 perl 双引号串里会当数组插值，实测把 `history.length` 改成了 `history.length` 缺字符的语法错。要改就用编辑工具。
4. **交付**：唯一产物就是 `public/index.html`（自包含）。
5. **发布**：`git push origin main` → GitHub Actions 先跑 `node dev/tools/stamp.mjs --write` 把「最后更新」、提交说明与 `sitemap.xml` 的 `lastmod` 刷成本次提交（见 §7），再只把 `public/` 上传为 Pages 产物（线上 `https://bunnychen.top/fanren-wiki/`）。**提交时不必再手动改这些日期。**首次需在仓库 **Settings → Pages → Source** 选 **GitHub Actions**。推完等约 30s，用 `curl -sI` 看体积/状态码再抽查关键标记（`gh` CLI 未安装，Actions API 未鉴权返回 404，一律以线上地址为准）。
6. **文档同步（交付的一部分）**：结构性改动、新增函数/常量、流程变化都要顺手更新本文档（§3 结构、§5 函数表、§10 迭代日志至少各改一处），别让它烂掉。

## 9. 数据来源与已核验事实

- 用户提供分析资料库：`~/Downloads/fanren-xiuxian-zhuan-analysis-master/`（人物谱系 73 人/故事梗概/社会结构/小说概述资料库/时间关系图/README，声称基于原著 20 卷 532,528 行逐段验证、结局带原文行号）。曾据此：新增 17 位谱系角色、丰富 17 处核心角色生平、纠错"王婵→王蝉"（全站已统一）。
- 关键剧情设定（已在页面"剧情速览"呈现）：双韩立因果闭环——A 韩立=轮回殿主（时间道祖→败古或今→散尽时间法则铸掌天瓶→穿越远古→改修轮回→创轮回殿→妻甘如霜=南宫婉前世→联手 B 击败古或今→陨落）；B 韩立=本线主角（捡瓶→大罗→放弃道祖→掌天瓶返回过去救元瑶/帮厉飞雨结仙缘/踢瓶给少年自己→因果闭环→隐居黑土仙域）；掌天瓶=唯一逆转时空之物。
- 首页"为什么做这个网站"文案来源：`../fanren-xiuxian.md`（境界差距感悟 + 映照现实 + 统一资料集定位 + 页面包含 + 问道自述）——2026-09-17 已把该页文字**整体并入首页正文**，两边互为镜像，改一处要同步另一处。

## 10. 已知限制与迭代历史摘要

**限制**
- 部分冷门角色无可靠图片（页面保留首字占位），后续有官方设定图可继续补；曲魂/极阴祖师等已按用户反馈迭代修正。
- **法宝/灵草配图待补（61 个文件名）**：2026-09-16 用户叫停图片工作后，已移除 61 个指向不存在文件的 img 引用（数据文字完整）。待补清单（拼音文件名）：`balinchi biyanjiu chuwudai dayanrenxingkuilei diandaowuxingzhen dulongdan ganyingling guiluofan hanyuanren haoyuandan heifengqi hongxiandunguangzhen hualingubao huanglinjia huazhou hunyuanbo jiangyundan jinfuzimuren jingangzhao juguiikuilei langshoukuilei langshouyuruyi lingshouhuan liudaolunhuipan luohunsha lvhuangjian miechendan minghunzhu molongren mosuiduan qiankunta qianlanbingyan qingmingzhen qingxudan qiyanshan renhuyaokuilei sheweikuilei shiling taiyangjingshi tanyaofan tianluyin tianshizhu wanyaofan wuxinghuan wuyulingcha xiusuidan xuanhuangjing xuantianhulu xuantianzhanlingjian xuantiefeitiandun xuelingshui xueningsowuxingdan xueqidan xuhuangding yingyuehuan yuanmingdeng yuanyingjikuilei zhangtianyin zhenhaizhong zhuquehuan ziyinwan`（.jpg，对应 TREASURES/HERBS 中的法宝丹药）。恢复图片流程见 §4 TREASURES 小节。
- 图片可能错配（已有声明）；用户曾要求逐张核对，历史轮次修过多处错图（陈巧倩↔董萱儿、风希、尸魈、曲魂、极阴祖师等）。
- 卡片区 221 张卡较长（约 2 万 px）——已用「核心圈」默认降噪（被引 ≥ 5，约 38 条）+ 篇章 tab + 全站搜索缓解；「全部 221」随时可切。
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
  ⑥ **本地不要跑 `--write`**（2026-09-20 实测坑）：VS Code 编辑器缓冲区会把它自己那份内容回写，把脚本写入的结果覆盖成"吞字"的坏文本（`<span …>` 变 `s`、`最后更新：` 整段消失），脚本自身的读回校验也查不出来 —— 只能 `git checkout` 恢复。CI 在 runner 上跑、没有编辑器，安全。
  ⑦ **验收**：`$env:CHROME_PATH=...msedge.exe; node dev/tools/verify.mjs` → **38/38 通过**；页面未新增任何外部请求或第三方依赖；`sitemap.xml` 的 `lastmod` 已纳入同一次注入（本地仍手写、与页面日期保持同值）。
  ⑧ 体积：仓库内版本 **431781 → 434351 字节**（+2570，其中 +2470 是本机检出把 LF 换成 CRLF 的行尾差，内容本身只多约 100 字节：导航栏日期对齐 + 页脚加提交说明注入位）。改动前快照 = `dev/_backup/index-v38.html`（431781，本机生成、不进 git）。
