<div align="center">
  <img src=".github/assets/logo.svg" alt="fanren-wiki logo" width="88" height="88">

  <h1 align="center">《凡人修仙传》百科 · 全篇资料图谱</h1>

  <p>
    六个篇章 <b>221</b> 位人物 · 灵兽灵虫 / 灵草丹药 / 法器法宝 <b>169</b> 条 · 含境界演进与命运结局<br>
    自包含单页静态站 —— <b>零构建 · 零依赖 · 零 CDN</b>
  </p>

  <p>
    <a href="https://github.com/Lizhenghe-Chen/fanren-wiki/actions/workflows/deploy.yml"><img src="https://github.com/Lizhenghe-Chen/fanren-wiki/actions/workflows/deploy.yml/badge.svg" alt="deploy"></a>
    <a href="LICENSE"><img src="https://img.shields.io/badge/license-Apache--2.0-blue.svg" alt="license"></a>
    <a href="https://bunnychen.top/fanren-wiki/"><img src="https://img.shields.io/badge/%E5%9C%A8%E7%BA%BF-bunnychen.top%2Ffanren--wiki-d4af6a.svg" alt="website"></a>
    <a href="#快速开始"><img src="https://img.shields.io/badge/dependencies-0-brightgreen.svg" alt="dependencies"></a>
    <a href="https://github.com/Lizhenghe-Chen/fanren-wiki/issues"><img src="https://img.shields.io/badge/%E5%8B%98%E8%AF%AF-GitHub%20Issues-2f81f7.svg" alt="issues"></a>
  </p>

  <p><b>在线访问</b> → <a href="https://bunnychen.top/fanren-wiki/">bunnychen.top/fanren-wiki</a></p>
</div>

## 目录

- [特性](#特性)
- [收录内容](#收录内容)
- [快速开始](#快速开始)
- [项目结构](#项目结构)
- [数据组织](#数据组织)
- [验收](#验收)
- [部署](#部署)
- [反馈与勘误](#反馈与勘误)
- [许可与声明](#许可与声明)
- [项目由来](#项目由来)
- [致谢](#致谢)

## 特性

- **七大视图 + hash 路由**：首页 / 人物图谱 / 剧情速览 / 境界体系 / 灵兽灵虫 / 灵草丹药 / 法器法宝 页内切换；`#v-chars` 切视图，`#v-treasures/tres-12` 直达并展开单条记录，地址栏即真相源，可复制分享。
- **人物关系图谱**：ECharts 力导向图，默认只显示「核心圈」（被引 ≥ 5 的条目）以降噪，一键切回全部 221 条；节点可点击跳进对应卡片。
- **全站搜索**：`Ctrl/⌘ + K`（或 `/`）唤起，跨四库分组命中、关键词高亮、方向键 + Enter 定位。
- **跨库互引网络**：四库记录统一编号（`data-key`），卡片互挂「相关条目 / 被引用于」chip，221 位人物与三库条目之间可互相跳转。
- **图表化梳理**：韩立境界演进时间轴、篇章 × 势力旭日图、境界阶梯图，以及妖兽等级 / 灵药年份 / 法宝品阶三张对照档位。
- **默认不剧透**：卡片只显示头像、身份、本篇修为与标签，展开后才呈现生平与结局。
- **移动端适配**：桌面 1440×900 与移动 390×844 双视口均无横向溢出、无竖条文本。
- **零外部依赖**：字体走系统栈，ECharts 5.6.0 按需构建为本地文件，`file://` 双击即可打开；全页唯一外部请求是首页的「次浏览」计数（不写 cookie、不采集个人标识，`file://` 与本地预览不发起）。

## 收录内容

| 板块 | 条数 | 分类与说明 |
| --- | ---: | --- |
| 人物图谱 | **221** | 六个篇章：七玄门 16 / 黄枫谷 29 / 乱星海 32 / 大晋 55 / 灵界 39 / 仙界 50。跨篇角色按「出现即写」重复收录，并按篇标注该篇修为演进 |
| 灵兽灵虫 | **40** | 灵虫 / 灵兽 / 妖兽妖修 / 真灵·神兽 / 炼尸魔物 |
| 灵草丹药 | **64** | 灵草灵药 / 天材地宝 / 突破丹药 / 辅助丹药 / 丹方·主材 |
| 法器法宝 | **65** | 玄天之宝·至宝 / 本命法宝 / 神通秘术 / 功法秘典 / 符箓阵法 / 其他 |
| 配图 | **360** | `public/assets/` 共 374 张，另 14 张为实名备用素材（未被引用只作提示、不判失败） |

数据来源：起点中文网官方《凡人必备手册》第二版、原著情节与公开百科多源交叉验证。

## 快速开始

不需要任何构建与依赖，`public/index.html` 就是交付物。

```bash
# 方式一：本地静态服务（推荐）
cd public && python3 -m http.server 8123
# 打开 http://127.0.0.1:8123/
```

方式二：直接双击 `public/index.html`。样式、脚本与数据都内联在页面里，配图走相对路径，`file://` 打开可用。

## 项目结构

```
fanren-wiki/
├── public/                       # 唯一发布目录，GitHub Actions 只上传这里
│   ├── index.html                # 交付物：单文件页面（内联 CSS/JS 与全部条目数据）
│   ├── cultivation.css           # 图表样式（境界阶梯 / 关系图谱 / 旭日图）
│   ├── javascripts/
│   │   ├── cultivation-chart.js  # 境界阶梯图
│   │   ├── echarts.min.js        # ECharts 5.6.0 按需构建包（graph + sunburst，527KB）
│   │   └── overview-charts.js    # 人物关系图谱（力导向）+ 篇章 × 势力旭日图
│   ├── assets/                   # 374 张配图
│   ├── sitemap.xml
│   └── robots.txt
├── dev/                          # 开发资料，随仓库跟踪但永不进发布产物
│   ├── Agent.md                  # 开发文档：架构、数据模型、交互与踩坑记录（先读这个）
│   ├── _review.md                # 数据审校笔记
│   ├── _image-slim-report.json   # 图片瘦身逐图决策记录
│   └── tools/                    # verify.mjs / image-slim.py / echarts-entry.js
├── .github/
│   ├── assets/logo.svg           # 本 README 顶部图标（与站点 favicon 同设计，不发布）
│   ├── ISSUE_TEMPLATE/           # 勘误纠错 / 站点问题模板
│   └── workflows/deploy.yml      # Pages 发布链路
├── LICENSE
├── NOTICE
└── README.md
```

配图已统一瘦身：卡片实际只显示 180–240px 宽，发布图压到**长边 ≤ 800px / JPEG q76**（90MB → 20MB）。

## 数据组织

全部条目以 JS 常量内联在 `public/index.html` 中，没有外部数据文件：

- `DATA` —— 6 个篇章 → 人物数组，字段：`n` 名字 / `t` 身份称号 / `r` 本篇修为 / `e` 本篇结局 / `s` 生平梗概 / `img` 配图 / `rel` 与韩立关系 / `camp` 势力 / `race` 种族 / `ev` 本篇修为演进（已全量补齐 221/221）
- `BEASTS` · `HERBS` · `TREASURES` —— 另外三库，字段同人物并各带 `cat` 分类键

新增一条记录 = 在对应数组里追加一个对象：渲染、检索、互引与深链会自动带上它。详细的字段口径、函数索引与踩坑记录见 [`dev/Agent.md`](dev/Agent.md)。

## 验收

改完页面先跑一遍验收脚本（随仓库跟踪，但不进发布产物）：

```bash
node dev/tools/verify.mjs                                        # 默认 file:// 直开 public/index.html
node dev/tools/verify.mjs --url http://localhost:8123/index.html # 或指定地址
```

35 条断言，每条只查一件事，失败时打印实测值并以非 0 退出码结束：

- **结构** —— 七视图容器与唯一 `h1`、四库卡片数（221/40/64/65）、图片无缺图且全部可解码、互引网络规模、开源与反馈入口
- **布局** —— 双视口（桌面 1440×900 / 移动 390×844）无横向溢出与竖条文本，统计位显示后再复测一次
- **交互** —— 核心圈默认生效、篇章与三库筛选、搜索与定位、互引跳转、返回顶部（进度环随滚动补满）、深链冷启动与 URL 同步、浏览器返回后路由一致
- **图表** —— 旭日图 / 关系图谱渲染、配色取自页面 CSS 变量、悬浮详情、节点点击跳转、折叠展开后画布尺寸恢复
- **网络** —— 无第三方请求、无控制台报错

零依赖：只需 **Node ≥ 22**（内建 WebSocket / fetch）与**本机 Chrome**，不需要 `npm install`；Chrome 不在默认位置时用 `--chrome <路径>` 或 `CHROME_PATH` 指定。用 CDP 直接驱动浏览器而非 puppeteer，正是为了不引入 `node_modules`。

## 部署

推送到 `main` 即触发 [`.github/workflows/deploy.yml`](.github/workflows/deploy.yml)：Actions 只把 `public/` 上传为 Pages 产物，`dev/` 永不进站。

首次部署需在仓库 **Settings → Pages → Source** 选择 **GitHub Actions**。自定义域名继承自用户站，项目页落在 `bunnychen.top/fanren-wiki/`，本仓库不需要 `CNAME`。

## 反馈与勘误

勘误与建议统一走 GitHub Issues → <https://github.com/Lizhenghe-Chen/fanren-wiki/issues>（已配 [Issue 模板](.github/ISSUE_TEMPLATE)：勘误纠错 / 站点问题）。附上原著章节、《凡人必备手册》或动画集数等依据，核对更快。

## 许可与声明

**Apache License 2.0**，全文见 [`LICENSE`](LICENSE)；授权范围与第三方素材声明见 [`NOTICE`](NOTICE)。

- **原创部分**（页面代码、资料编排、页面设计与文案）：可自由使用、修改、分发，含商业用途。条件：保留版权与许可声明、保留 `NOTICE`、修改处注明改动
- **角色图片不在授权范围内**（网络检索素材），版权归各自权利人，本仓库不主张任何权利；权利人可通过 Issues 要求删除
- **非官方项目**：原著及衍生作品的权利归原作者忘语与出版方，本项目与其无关联，未获授权或背书

## 项目由来

原为 `Lizhenghe-Chen.github.io` 仓库下的静态目录（`docs/docs/Other/fanren-characters/`，2026-09-14 起随主站发布），2026-09-17 拆分独立，**git 提交历史完整保留**，主站旧路径保留跳转桩指向本站。首页文案的素材来源为主站资料页 <https://bunnychen.top/docs/Other/fanren-xiuxian/>。

## 致谢

- 原著《凡人修仙传》作者 **忘语**，及起点中文网官方《凡人必备手册》
- [Apache ECharts](https://echarts.apache.org/)（Apache-2.0）——本站在其按需构建产物上渲染图表，重建入口见 `dev/tools/echarts-entry.js`
- [GitHub Pages](https://pages.github.com/) 提供托管与发布
