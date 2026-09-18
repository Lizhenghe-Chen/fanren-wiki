# fanren-wiki

《凡人修仙传》百科 · 全篇资料图谱 —— 自包含单页静态站。

线上地址：**https://bunnychen.top/fanren-wiki/**

## 这是什么

一个手写单页 HTML 的《凡人修仙传》资料可视化站点：6 个篇章 **221 条人物记录**，另有灵兽灵虫 40 条、灵草丹药 64 条、法器法宝 65 条，含境界演进与命运结局。

- **无构建、无依赖**：原生 JS + 手写 CSS，无构建步骤；页面本体（样式与主脚本）内联在 `public/index.html`，图表脚本与样式为同目录文件，`file://` 双击即可打开
- **数据内联**：所有条目数据在该文件的 `<script>` 常量里，没有外部数据文件
- **配图相对引用**：`<img src="assets/…">`

## 目录结构

```
public/                     ← 唯一发布目录（Pages 只上传这里）
├── index.html              # 交付物：单文件页面（内联 CSS/JS）
├── cultivation.css         # 图表样式（境界阶梯 / 关系图谱 / 旭日图）
├── javascripts/
│   ├── cultivation-chart.js # 境界阶梯图
│   ├── echarts.min.js      # ECharts 5.6.0 本地库（按需构建，527KB，零 CDN）
│   └── overview-charts.js  # 人物关系图谱（力导向）+ 篇章×势力旭日图
├── assets/                 # 374 张发布图
├── sitemap.xml
└── robots.txt
```

仓库只发布 `public/`，根目录另有 `LICENSE`、`NOTICE`、`README.md`、`.github/workflows/deploy.yml`。开发资料在 `dev/`：**只跟踪开发文档与工具**（`Agent.md`、`_review.md`、`tools/`），迭代备份与实验产物仅本地保留。

> 图片已统一瘦身：卡片实际只显示 180–240px 宽，发布图压到**长边 ≤ 800px / JPEG q76**（90MB → 20MB）。

## 本地预览

```bash
cd public && python3 -m http.server 8123   # 打开 http://127.0.0.1:8123/
```

或直接双击 `public/index.html`（图片为相对路径，`file://` 可用）。

## 改完先过验收

验收脚本位于本地 `dev/tools/verify.mjs`（属开发资料，不随仓库发布）：

```bash
node dev/tools/verify.mjs                                        # 默认 file:// 直开 public/index.html
node dev/tools/verify.mjs --url http://localhost:8123/index.html # 或指定地址
```

35 条断言，每条只查一件事：七视图容器与唯一 h1、四库卡片数（221/40/64/65）、图片无缺图且全部可解码、互引网络规模、开源与反馈入口、核心圈默认生效、双视口（桌面 1440×900 / 移动 390×844）无横向溢出与竖条文本、篇章与三库筛选、搜索与定位、互引跳转、返回顶部、深链冷启动与 URL 同步、浏览器返回后路由一致、两张概览图表（旭日图 / 关系图谱）渲染且配色取自页面 CSS 变量、悬浮详情、图谱节点点击跳转、折叠展开后画布尺寸恢复、无第三方请求、无控制台报错。失败会打印实测值并以非 0 退出码结束。

零依赖：只需 **Node ≥ 22**（内建 WebSocket/fetch）与**本机 Chrome**，不需要 `npm install`；Chrome 不在默认位置时用 `--chrome <路径>` 或 `CHROME_PATH` 指定。

用 CDP 而非 puppeteer，避免引入 node_modules；脚本在 `dev/`，不影响 `public/` 的零构建交付。

## 发布

推送到 `main` → GitHub Actions 只把 `public/` 上传为 Pages 产物。需在仓库 **Settings → Pages → Source** 选 **GitHub Actions**；自定义域名继承自用户站，项目页落在 `bunnychen.top/fanren-wiki/`，本仓库不需要 `CNAME`。

## 来历

原为 `Lizhenghe-Chen.github.io` 仓库下的静态目录（`docs/docs/Other/fanren-characters/`，2026-09-14 起随主站发布），2026-09-17 拆分独立，**git 提交历史完整保留**。主站旧路径保留跳转桩指向本站。

反馈与勘误：[https://github.com/Lizhenghe-Chen/fanren-wiki/issues](https://github.com/Lizhenghe-Chen/fanren-wiki/issues)（附原著章节、《凡人必备手册》或动画集数等依据更好核对）。

首页文案的素材来源是主站资料页 [https://bunnychen.top/docs/Other/fanren-xiuxian/](https://bunnychen.top/docs/Other/fanren-xiuxian/)。

## 许可

**Apache License 2.0**，全文见 `LICENSE`；授权范围与第三方素材声明见 `NOTICE`。

- **原创部分**（页面代码、资料编排、页面设计与文案）：可自由使用、修改、分发，含商业用途。条件：保留版权与许可声明、保留 `NOTICE`、修改处注明改动
- **角色图片不在授权范围内**（网络检索素材），版权归各自权利人，本仓库不主张任何权利；权利人可要求删除
- **非官方项目**：原著及衍生作品的权利归原作者忘语与出版方，本项目与其无关联，未获授权或背书
