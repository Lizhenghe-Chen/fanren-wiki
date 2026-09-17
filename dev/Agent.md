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
│   ├── cultivation.css     # 【用户自加，不可改动】境界图表样式
│   ├── javascripts/cultivation-chart.js   # 图表脚本（本站自持，不再依赖主站）
│   ├── assets/             # 374 张图：360 张被引用（.webp/.jpg 混合，逐图最优）+ 14 张实名备用图，见 §6
│   ├── sitemap.xml
│   └── robots.txt
└── dev/                    # 开发资料，永不上站
    ├── Agent.md            # 本文档
    ├── _review.md          # 数据审校笔记
    ├── tools/              # 在用的工具：image-slim.py（图片瘁身，见 §6）、verify.mjs（零依赖验收，见 §8.3）
    ├── _image-slim-report.json  # 瘦身逐图决策记录（体积/SSIM/所选质量档）
    ├── _backup/            # 历史堆积：index-vNN.html 版本次级（21 个）+ 一次性的 migrate 脚本（apply_*/add_*/fix_*/sync_*）+ meta/stories/ev/herbs_data/treasures_data 等中间数据
    └── watermark.svg       # 仅供 _backup/index-v*.html 引用的水印瓦片（当前页面已内联 base64）
```

- `_backup/` 里的脚本不参与运行、也不要“顺手执行”：它们是当时的字符串级插入脚本，路径写死在旧仓库（`Lizhenghe-Chen.github.io/...`）。要重跑得先把路径改回来。
- ⚠️ `dev/unused-assets/` **已不存在**：那批备用图已全部清理到归档目录（见 §6 原图备份）。目前未被引用的 14 张实名图留在 `public/assets/` 里，由验收脚本作为提示列出（见 §6）。

- 工作目录：`~/Documents/GitProjects/fanren-wiki/`（原地址 `Lizhenghe-Chen.github.io/docs/docs/Other/fanren-characters/` 已停用，主站只留跳转桩）；早期旧版在 `~/Doubao/chats/2026-09-14/new-chat/fanren-characters/`（仅参照）。
- 线上地址：`https://bunnychen.top/fanren-wiki/`（项目页，继承用户站自定义域名，本仓库无需 CNAME）。
- 参考资料页仍在主站：`https://bunnychen.top/docs/Other/fanren-xiuxian/`（首页介绍文案素材来源 + 评论区入口）。
- **开发资料一律放进 `dev/`**：发布边界由目录决定（只上传 `public/`），不要把 `_backup/`、自检截图、笔记放进 `public/`。

## 3. 页面结构：七视图 + hash 路由

页面**不是单页长滚**，而是**页内多视图切换**（用户明确要求"分页面"，否决过"左右分栏"）：

```
<body>
  <div class="asset-manifest"></div>          # 图片引用隐藏清单（见 §6）
  <nav class="topnav">                        # 顶部主导航（sticky top:0，49px）：首页 | 人物图谱 | 剧情速览 | 境界体系 | 灵兽灵虫 | 灵草丹药 | 法器法宝 + 搜索按钮 + 持续更新·作者主页·日期
  <div class="view" id="v-home">              # 视图0 首页（默认）
    hero（标题/统计/按钮） → 为什么做这个网站（<details class="home-why">，默认收起） → 收录内容 6 卡 → 问道自述（.home-quest） → 收录说明 → 数据来源（.src-list）
  </div>
  <div class="view" id="v-chars">             # 视图1 人物图谱
    .page-head（紧凑页头，含唯一的 h1 + 统计） → sticky .navbar（top:49px：.tabs 篇章 tab + .seg 核心圈切换 + 搜索框） → .img-note 图片准确性声明（<details>，默认收起） → 卡片区 <main id="characters">
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
- `cultivation.css` 与 `cultivation-chart.js`：**用户项目自带，不可修改**；图表用 `data-cultivation` 属性 + IntersectionObserver 延迟初始化，视图隐藏时切回会自动重播，**无需适配**。
- 字体：**纯系统字体栈**（`--font-serif` 优先 Songti SC / STSong，`--font-sans` 优先 PingFang SC / Microsoft YaHei，逐级回退）。2026-09-17 已移除 `miaoda.feishu.cn` 的 Noto 字体 CDN（省 11.35MB）：**全站 0 第三方请求**，离线/`file://` 打开外观完全一致，**不要再引入外部字体**。
- 无任何构建工具，原生 JS，`file://` 可直接打开（图片为相对路径，**转发时需连同 assets/ 一起**）。
- 首页样式类：`.home-section` / `.home-why`（`<details>` 折叠） / `.home-cards` / `.home-card` / `.home-note` / `.home-quest`（问道自述） / `.src-list`（数据来源）（`/* ===== 首页 ===== */` 段）。
- 全局复用类：`.page-head`（紧凑页头，内含唯一的 `h1` + `.stats` + `.ph-lead` 一句话引导；≤640px 收窄内边距） / `.seg`+`.seg-btn`（分段选择器） / `.lib-search`（三库共用搜索框，胶囊，与分类 tab 同一套形态与 10/12px 外边距） / `.ref-chips`+`.ref-chip`（互引 chip） / `.spot*`（搜索面板一整套） / `.back-top` / `.img-note`（`<details>` 免责声明）。

### 出处与防盗（改动前必读）

- **全页水印**：`.watermark`（`position:fixed` 全屏平铺）的背景图**已内联为 base64 data URI**，不再引用 `watermark.svg`——`dev/watermark.svg` 仅为 `dev/_backup/index-v*.html` 保留，**勿删**（删了旧备份开出来就没水印）。改水印要改那段 base64，别改回外部文件引用。
- **无 `@media print` 例外**：打印/导出 PDF 也带水印（`position:fixed` 在分页媒体里逐页重复），别再加 `display:none` 把它关掉。
- **不在卡片图片上盖章**：曾经加过 `.card-top::after{content:"bunnychen.top"}` 的右下角标，**已移除且不要再加**——图片本身是网络检索的第三方素材，不是本站作品，在别人的图上盖自己的出处站不住脚（真有争议时也不占理）。图片区保持干净。
- **元数据**：`<head>` 里三件套——版权注释块（含版本/日期/仓库地址，抄整页的人会把出处一起带走）、`<link rel="canonical">`、JSON-LD（author / datePublished / dateModified / license / isBasedOn）。**改版必须同步**。
- **三处日期要一致**：页脚"最后更新"、注释块、JSON-LD `dateModified`。
- **明确不做**：禁用右键/选择、JS 混淆、反调试——伤体验与无障碍、几秒可绕过，已否决。

## 8. 开发流程（照做）

1. **先备份**：`cp public/index.html dev/_backup/index-vX.html`（版本号递增，防改坏）。
2. 小改动直接改；大改（结构/批量数据）参照"对象级替换 + 章节标记定位"脚本模式。**改 JS 数据用字符串级精确插入**（数花括号深度找记录闭合，避免 to_json 全量重排破坏格式；`DATA.xxx` 段正则 `(DATA\.%s = \[)(.*?)(\];)`）。
3. **自检（唯一验收方式，改完必须全绿）**：
   ```bash
   node dev/tools/verify.mjs                                   # 默认验 ./public/index.html（file://）
   node dev/tools/verify.mjs --url http://localhost:8899/index.html   # 也可指定 URL
   ```
   **零依赖**：Node ≥ 22 内置 `WebSocket`/`fetch` + 本机 Chrome，自己拉起 headless Chrome 走 CDP，**不装 puppeteer/playwright**。当前 24 条断言：七视图容器、四库卡片数（221/40/64/65）、**图片引用无缺图 + 全部能解码**、互引网络规模、**每个视图有且仅有一个 h1**、核心圈默认生效且可切回全部、桌面 1440×900 与移动 390×844 双视口的横向溢出与"竖条文本"、篇章筛选、**三库分类筛选（含 tab 计数一致性）与三库搜索**、搜索定位、互引 chip 跳转、返回顶部与进度环、深链冷启动、点卡片同步 URL、浏览器返回后视图与地址一致、0 第三方请求、0 控制台报错。
   - 断言失败先看输出里打印的**实际值**再动代码（有 3 条断言曾是自己写错：阈值拍脑袋、期望值写反、把 `<link rel=canonical>` 当资源请求）。
   - ⚠️ **视口用 `Emulation.setDeviceMetricsOverride` 设置**：VS Code 内置浏览器**无视** `setViewportSize()`（请求 1440 实得 729），别拿它做响应式验收，也别用 iframe 顶替（Promises 会永不 resolve）。
   - 快速 JS 语法检查：提取内联 `<script>` 块逐个 `node --check`。
   - ⚠️ **不要用 `perl -0pi` 改校验脚本**：`@` 在 perl 双引号串里会当数组插值，实测把 `history.length` 改成了 `history.length` 缺字符的语法错。要改就用编辑工具。
4. **交付**：唯一产物就是 `public/index.html`（自包含）。
5. **发布**：`git push origin main` → GitHub Actions 只把 `public/` 上传为 Pages 产物（线上 `https://bunnychen.top/fanren-wiki/`）。首次需在仓库 **Settings → Pages → Source** 选 **GitHub Actions**。推完等约 30s，用 `curl -sI` 看体积/状态码再抽查关键标记（`gh` CLI 未安装，Actions API 未鉴权返回 404，一律以线上地址为准）。
6. **文档同步（交付的一部分）**：结构性改动、新增函数/常量、流程变化都要顺手更新本文档（§3 结构、§5 函数表、§10 迭代日志至少各改一处），别让它烂掉。

## 9. 数据来源与已核验事实

- 用户提供分析资料库：`/Users/bunnychen/Downloads/fanren-xiuxian-zhuan-analysis-master/`（人物谱系 73 人/故事梗概/社会结构/小说概述资料库/时间关系图/README，声称基于原著 20 卷 532,528 行逐段验证、结局带原文行号）。曾据此：新增 17 位谱系角色、丰富 17 处核心角色生平、纠错"王婵→王蝉"（全站已统一）。
- 关键剧情设定（已在页面"剧情速览"呈现）：双韩立因果闭环——A 韩立=轮回殿主（时间道祖→败古或今→散尽时间法则铸掌天瓶→穿越远古→改修轮回→创轮回殿→妻甘如霜=南宫婉前世→联手 B 击败古或今→陨落）；B 韩立=本线主角（捡瓶→大罗→放弃道祖→掌天瓶返回过去救元瑶/帮厉飞雨结仙缘/踢瓶给少年自己→因果闭环→隐居黑土仙域）；掌天瓶=唯一逆转时空之物。
- 首页"为什么做这个网站"文案来源：`../fanren-xiuxian.md`（境界差距感悟 + 映照现实 + 统一资料集定位 + 页面包含 + 问道自述）——2026-09-17 已把该页文字**整体并入首页正文**，两边互为镜像，改一处要同步另一处。

## 10. 已知限制与迭代历史摘要

**限制**
- 部分冷门角色无可靠图片（页面保留首字占位），后续有官方设定图可继续补；曲魂/极阴祖师等已按用户反馈迭代修正。
- **法宝/灵草配图待补（61 个文件名）**：2026-09-16 用户叫停图片工作后，已移除 61 个指向不存在文件的 img 引用（数据文字完整）。待补清单（拼音文件名）：`balinchi biyanjiu chuwudai dayanrenxingkuilei diandaowuxingzhen dulongdan ganyingling guiluofan hanyuanren haoyuandan heifengqi hongxiandunguangzhen hualingubao huanglinjia huazhou hunyuanbo jiangyundan jinfuzimuren jingangzhao juguiikuilei langshoukuilei langshouyuruyi lingshouhuan liudaolunhuipan luohunsha lvhuangjian miechendan minghunzhu molongren mosuiduan qiankunta qianlanbingyan qingmingzhen qingxudan qiyanshan renhuyaokuilei sheweikuilei shiling taiyangjingshi tanyaofan tianluyin tianshizhu wanyaofan wuxinghuan wuyulingcha xiusuidan xuanhuangjing xuantianhulu xuantianzhanlingjian xuantiefeitiandun xuelingshui xueningsowuxingdan xueqidan xuhuangding yingyuehuan yuanmingdeng yuanyingjikuilei zhangtianyin zhenhaizhong zhuquehuan ziyinwan`（.jpg，对应 TREASURES/HERBS 中的法宝丹药）。恢复图片流程见 §4 TREASURES 小节。
- 图片可能错配（已有声明）；用户曾要求逐张核对，历史轮次修过多处错图（陈巧倩↔董萱儿、风希、尸魈、曲魂、极阴祖师等）。
- 卡片区 221 张卡较长（约 2 万 px）——已用「核心圈」默认降噪（被引 ≥ 5，约 38 条）+ 篇章 tab + 全站搜索缓解；「全部 221」随时可切。
- 未做（按需）：人物总览页（把韩立 6 张卡合成生命周期视图，`ev` 字段已有全集）、展开卡改为侧边抽屉（现在是原位摊开、把下方内容顶下去）、3–4 张带第三方水印/游戏 UI 的法宝图待换（如 `liudaolunhuipan.webp` 带 NGA 水印与「无法转赠」框）、`.asset-manifest`（300 行，注释写 302 实为 374）应移到 `dev/` 校验脚本（浏览器从不加载它）。

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
