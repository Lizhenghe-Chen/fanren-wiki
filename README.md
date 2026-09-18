<div align="center">
  <a href="https://bunnychen.top/fanren-wiki/"><img src=".github/assets/logo.svg" alt="《凡人修仙传》百科 · 全篇资料图谱" width="88" height="88"></a>

  <h1 align="center">《凡人修仙传》百科 · 全篇资料图谱</h1>

  <p>六个篇章 <b>221</b> 位人物 · 灵兽灵虫 / 灵草丹药 / 法器法宝 <b>169</b> 条<br>
  自包含单页静态站 —— 零构建 · 零依赖 · 零 CDN</p>

  <p><b>在线访问</b> → <a href="https://bunnychen.top/fanren-wiki/">bunnychen.top/fanren-wiki</a></p>
</div>

## 页面速览

<p align="center">
  <a href="https://bunnychen.top/fanren-wiki/"><img src="image/README/shots/01-home.webp" alt="首页" width="840"></a>
</p>

| 人物图谱 | 剧情速览 |
| :---: | :---: |
| <a href="https://bunnychen.top/fanren-wiki/#v-chars"><img src="image/README/shots/02-characters.webp" alt="人物图谱" width="400"></a> | <a href="https://bunnychen.top/fanren-wiki/#v-lore"><img src="image/README/shots/03-lore.webp" alt="剧情速览" width="400"></a> |

| 境界体系 | 灵兽灵虫 |
| :---: | :---: |
| <a href="https://bunnychen.top/fanren-wiki/#v-realms"><img src="image/README/shots/04-realms.webp" alt="境界体系" width="400"></a> | <a href="https://bunnychen.top/fanren-wiki/#v-beasts"><img src="image/README/shots/05-beasts.webp" alt="灵兽灵虫" width="400"></a> |

| 灵草丹药 | 法器法宝 |
| :---: | :---: |
| <a href="https://bunnychen.top/fanren-wiki/#v-herbs"><img src="image/README/shots/06-herbs.webp" alt="灵草丹药" width="400"></a> | <a href="https://bunnychen.top/fanren-wiki/#v-treasures"><img src="image/README/shots/07-treasures.webp" alt="法器法宝" width="400"></a> |

## 特性

- **七大视图**：首页 / 人物图谱 / 剧情速览 / 境界体系 / 灵兽灵虫 / 灵草丹药 / 法器法宝 页内切换，单条记录可深链直达（如 `#v-treasures/tres-12`）。
- **关系图谱**：ECharts 力导向图，默认只显示核心圈（被引 ≥ 5）降噪，可一键切回全部 221 条，节点可点进对应卡片。
- **全站搜索**：`Ctrl/⌘ + K` 唤起，跨四库命中、关键词高亮、方向键定位。
- **跨库互引**：四库记录统一编号，卡片互挂「相关条目 / 被引用于」，人物与三库条目互相跳转。
- **默认不剧透**：卡片只显示身份与本篇修为，展开后才看生平与结局。
- **零外部依赖**：ECharts 本地按需构建，`file://` 双击即开；全页唯一外部请求是首页的浏览计数。

## 收录内容

| 板块 | 条数 | 内容 |
| --- | ---: | --- |
| 人物图谱 | **221** | 六个篇章：七玄门 16 / 黄枫谷 29 / 乱星海 32 / 大晋 55 / 灵界 39 / 仙界 50 |
| 灵兽灵虫 | **40** | 灵虫 / 灵兽 / 妖兽妖修 / 真灵·神兽 / 炼尸魔物 |
| 灵草丹药 | **64** | 灵草灵药 / 天材地宝 / 突破丹药 / 辅助丹药 / 丹方·主材 |
| 法器法宝 | **65** | 玄天之宝·至宝 / 本命法宝 / 神通秘术 / 功法秘典 / 符箓阵法 / 其他 |
| 配图 | **360** | `public/assets/`，另有 14 张备用素材 |

数据来源：起点官方《凡人必备手册》第二版 + 原著与公开资料交叉验证。

## 本地运行

```bash
cd public && python3 -m http.server 8123   # 打开 http://127.0.0.1:8123/
```

也可以直接双击 `public/index.html`（不需要构建与依赖，`file://` 可用）。

## 项目结构

```
fanren-wiki/
├── public/                  # 唯一发布目录（整目录即成品）
│   ├── index.html           # 页面本体（内联 CSS/JS 与全部条目数据）
│   ├── cultivation.css      # 图表样式
│   ├── javascripts/         # 境界阶梯图 / 关系图谱 + 旭日图 / 本地 ECharts
│   └── assets/              # 374 张配图（同目录另有 sitemap.xml、robots.txt）
├── dev/                     # 开发资料，不进发布产物
│   ├── Agent.md             # 开发文档：架构、数据模型、交互与踩坑
│   └── tools/               # verify.mjs / image-slim.py / readme-shots.py / echarts-entry.js
├── image/README/shots/      # 本 README 的页面截图
├── .github/                 # 发布工作流 / Issue 模板 / README 图标
├── LICENSE
├── NOTICE
└── README.md
```

## 开发与验收

条目数据内联在 `public/index.html`（`DATA` / `BEASTS` / `HERBS` / `TREASURES` 四个常量），新增记录＝往对应数组加一个对象；字段口径与踩坑见 [`dev/Agent.md`](dev/Agent.md)。

改完跑一次验收：

```bash
node dev/tools/verify.mjs
```

35 条断言覆盖结构 / 布局 / 交互 / 图表 / 网络，只需 **Node ≥ 22** 与本机 Chrome，不需要 `npm install`。

## 反馈与勘误

勘误与建议请提 [Issue](https://github.com/Lizhenghe-Chen/fanren-wiki/issues)，附原著章节或动画集数等依据更好核对。

## 许可与声明

**Apache License 2.0**，全文见 [`LICENSE`](LICENSE)；授权范围与第三方素材声明见 [`NOTICE`](NOTICE)。

- **原创部分**（页面代码、资料编排、页面设计与文案）：可自由使用、修改、分发，含商业用途。条件：保留版权与许可声明、保留 `NOTICE`、修改处注明改动
- **角色图片不在授权范围内**（网络检索素材），版权归各自权利人，本仓库不主张任何权利；权利人可通过 Issues 要求删除
- **非官方项目**：原著及衍生作品的权利归原作者忘语与出版方，本项目与其无关联，未获授权或背书

## 致谢

原著作者**忘语**与起点《凡人必备手册》提供事实依据；图表由 [Apache ECharts](https://echarts.apache.org/)（Apache-2.0）渲染。
