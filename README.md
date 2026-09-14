# 凡人修仙传 · 全篇人物图谱 — 开发文档

> 本文档供后续 LLM（或开发者）快速理解本项目并上手开发。先读本节即可动手，细节按需跳读。

## 1. 项目是什么

一个**自包含单页 HTML** 的《凡人修仙传》全篇人物可视化图谱，用户用于回忆剧情、检索人物、理解境界体系。

- 收录 **6 个篇章、215 条人物记录**（跨篇章重复出现的角色按"出现即写"重复收录，如韩立 6 篇、南宫婉 4 篇）。
- 每人默认卡片显示：**头像图、名字、身份、本篇修为、关系/势力/种族标签**；点击展开显示**生平梗概与结局**（默认不剧透）。
- 页面支持 **人物图片**（优先动画形象）与 **境界图表**（外部 cultivation-chart.js）。

## 2. 目录结构

```
fanren-characters/
├── index.html          # 唯一交付物（自包含：内联 CSS/JS + 相对路径图片）
├── cultivation.css     # 【用户自加，不可改动】境界图表样式
├── assets/             # 189 张角色图片（动画截图/概念图/同人图，命名见 §6）
└── _backup/            # 迭代备份与脚本（v1~v5 基线 + apply_*.py + json），非交付物
```

- 境界图表脚本在页面外：`../../../javascripts/cultivation-chart.js`（相对页面路径，项目内勿移动）。
- 主工作区：`BunnyChen.github.io/docs/docs/Other/fanren-characters/`；早期旧版在 `~/Doubao/chats/2026-09-14/new-chat/fanren-characters/`（仅参照）。

## 3. 页面结构：三视图 + hash 路由

页面**不是单页长滚**，而是**页内多视图切换**（用户明确要求"分页面"，否决过"左右分栏"）：

```
<body>
  <div class="asset-manifest"></div>          # 图片引用隐藏清单（见 §6）
  <nav class="topnav">                        # 顶部主导航：人物图谱 | 剧情速览 | 境界体系
  <div class="view" id="v-chars">             # 视图1 人物图谱（默认）
    hero（标题/统计/按钮） → 篇章 tab+搜索 → 图片准确性声明 → 卡片区 <main id="characters">
  </div>
  <div class="view" id="v-lore">              # 视图2 剧情速览（约 1 屏）
    韩立境界演进时间轴 #timeline → 故事脉络 6 卡 → 双韩立因果闭环
  </div>
  <div class="view" id="v-realms">            # 视图3 境界体系（约 1 屏）
    境界 rail → 3 个 data-cultivation 图表 → 各篇人数柱状 → 图例
  </div>
  <footer>…</footer>
  <script>…</script>
```

- **切换机制**：顶部 `.topnav a[href="#v-xxx"]` + `hashchange` 监听 + `switchView(id)`（文件末尾 IIFE）。`.view{display:none}`，`.view.active{display:block}`。
- **默认视图**：读 `location.hash`，无 hash 或非法时回退 `v-chars`。
- **新增视图**：加一个 `<div class="view" id="v-xxx">`，在 `switchView` 的 `VIEWS` 数组里登记，topnav 加链接即可。

## 4. 数据模型（`const DATA`）

`DATA` 是 6 键对象，键 = 篇章 id，值 = 人物数组：

| 键 | 篇章 | 条数 |
|---|---|---|
| `qixuanmen` | 七玄门 | 16 |
| `huangfeng` | 黄枫谷 | 29 |
| `luanxing` | 乱星海 | 30 |
| `dajin` | 大晋 | 52 |
| `lingjie` | 灵界 | 38 |
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
| `ev` | 跨篇修为演进 | 仅跨篇角色有，如 `"qixuanmen":["凡人→炼气"]` |

**新增/修改人物**：直接在 `DATA` 对应数组追加/编辑对象即可；跨篇角色在每篇各自收录（可各自配不同图片，如韩立每篇不同形象）。

## 5. 关键函数与交互

文件末尾初始化：`renderTabs(); renderMain(); applyFilter();` + 视图切换 IIFE。

| 函数 | 作用 |
|---|---|
| `renderTimeline()` | 渲染韩立境界时间轴（`TL` 数据，14 节点） |
| `renderTabs()` | 生成篇章 tab（全部/七玄门/…，带人数） |
| `renderMain()` | 遍历 `DATA` 生成卡片 DOM（含图片/占位/标签/修为/展开区） |
| `renderBars()` | 各篇人数柱状图 |
| `renderLegend()` | 图例 |
| `toggleCard(el)` | 点击卡片展开/收起生平（默认收起不剧透） |
| `applyFilter()` | tab + 搜索框双条件过滤卡片（`currentTab` + `keyword`） |
| `switchView(id)` | 视图切换（IIFE 内） |

搜索框匹配卡片 `data-name` / `data-aka`（别名）。

## 6. 图片体系（重要红线）

- **图片文件**：`assets/<拼音名>_<篇章>.jpg`，跨篇同角色可不同文件（如 `hanli_qixuanmen.jpg` / `hanli_xianjie.jpg`）。
- **引用方式（发布链路硬规则）**：图片路径只能出现在 **`<img src="assets/…">`** 或 **CSS `url()`** 中。JS 常量数组、`data-src` 等一律发布后裂图。
- **隐藏清单**：`<style>` 内 `.asset-manifest{display:none;background-image:url("assets/…"),…}` 列出**所有**被引用的图片。**新增图片必须同步追加登记**，否则发布后裂图（`publishBrokenAssets` 规则只认 src 与 CSS url() 静态引用）。
- **无图角色**：不硬凑图，卡片显示姓氏首字占位。
- **准确性声明**：页面已含三处声明（hero 副标题、卡片区上方橙色警示框、页脚）——图片是网络检索素材（动画截图/官方概念图/百科插画/同人立绘），受动画进度限制（播至人界篇·慕兰之战），灵界/仙界多数角色未在动画登场，**可能与官方形象存在偏差甚至错配**。此声明是用户明确要求，勿删除。
- **找图规范**：优先动画形象 → 官方概念图 → 百科插画 → 同人图；下载后必须用读图能力逐张核对角色身份、清晰度、无水印，错配宁可不用。

## 7. 样式与外部依赖

- 色板：深色底 + 金色（`--gold: #d4af6a` 系）+ oklch 派生，详见 `<style>` 顶部 CSS 变量。
- `cultivation.css` 与 `cultivation-chart.js`：**用户项目自带，不可修改**；图表用 `data-cultivation` 属性 + IntersectionObserver 延迟初始化，视图隐藏时切回会自动重播，**无需适配**。
- 字体：`miaoda.feishu.cn` 镜像的 Noto Serif SC / Noto Sans SC。
- 无任何构建工具，原生 JS，`file://` 可直接打开（图片为相对路径，**转发时需连同 assets/ 一起**）。

## 8. 开发流程（照做）

1. **先备份**：`cp index.html _backup/index-vX.html`（版本号递增，防改坏）。
2. 小改动直接改；大改（结构/批量数据）参照 `_backup/apply_*.py` 的"对象级替换 + 章节标记定位"脚本模式（标记如 `<!-- ===== 视图：xxx ===== -->`、`<!-- ===== 篇章 ===== -->`）。
3. **自检**（html skill 专用，禁止其他校验方式）：
   ```bash
   python3 "/Users/bunnychen/Library/Application Support/Doubao/Default/.doubao/agent_mode/workspace/.skills/html/scripts/shot.py" index.html
   ```
   看 `publishBrokenAssets`（必须 0）、`consoleErrors`、截图；`_shots/` 用完清理。
   - 验证非默认视图：复制一份临时文件到项目内（保证 assets 相对路径可用），把 `switchView(fromHash())` 临时改为 `switchView("v-lore")` 再截图，改完删除临时文件。
4. **交付**：`present_files` 交付 `index.html`（同一产物只交付一个 html）。

## 9. 数据来源与已核验事实

- 用户提供分析资料库：`/Users/bunnychen/Downloads/fanren-xiuxian-zhuan-analysis-master/`（人物谱系 73 人/故事梗概/社会结构/小说概述资料库/时间关系图/README，声称基于原著 20 卷 532,528 行逐段验证、结局带原文行号）。曾据此：新增 17 位谱系角色、丰富 17 处核心角色生平、纠错"王婵→王蝉"（全站已统一）。
- 关键剧情设定（已在页面"剧情速览"呈现）：双韩立因果闭环——A 韩立=轮回殿主（时间道祖→败古或今→散尽时间法则铸掌天瓶→穿越远古→改修轮回→创轮回殿→妻甘如霜=南宫婉前世→联手 B 击败古或今→陨落）；B 韩立=本线主角（捡瓶→大罗→放弃道祖→掌天瓶返回过去救元瑶/帮厉飞雨结仙缘/踢瓶给少年自己→因果闭环→隐居黑土仙域）；掌天瓶=唯一逆转时空之物。

## 10. 已知限制与迭代历史摘要

**限制**
- 部分冷门角色无可靠图片（约 28 个，页面保留首字占位），后续有官方设定图可继续补。
- 图片可能错配（已有声明）；用户曾要求逐张核对，历史轮次修过 3 处错图。
- 卡片区 215 张卡较长（约 2 万 px），属主体内容，用户可接受（有篇章 tab 过滤）。

**历史迭代**（备份文件即版本节点）
- v1：六篇章全量人物表格 → v2：+故事脉络/双韩立因果闭环 → v3：+rel/camp/race 三标签 + 修为演进 ev → v4：+点击展开生平、默认不剧透、修为行上卡片、图片准确性声明 → v5：+分析资料库补充（17 新角色、王蝉纠错、5 张新图、.asset-manifest 登记）→ 当前：三视图分页重构（apply_pages.py）。
- 中途否决方案：**左右分栏**（用户不喜欢，改"分页面"）；已废弃脚本 `_backup/apply_layout.py`（分栏死路，勿再引用）。
