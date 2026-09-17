# fanren-wiki

《凡人修仙传》百科 · 全篇资料图谱 —— 自包含单页静态站。

线上地址：**https://bunnychen.top/fanren-wiki/**

## 这是什么

一个手写单页 HTML 的《凡人修仙传》资料可视化站点：6 个篇章 **221 条人物记录**，另有灵兽灵虫 40 条、灵草丹药 64 条、法器法宝 65 条，含境界演进与命运结局。

- **无构建、无依赖**：CSS/JS 全部内联在 `public/index.html`，原生 JS，`file://` 双击即可打开
- **数据内联**：所有条目数据在该文件的 `<script>` 常量里，没有外部数据文件
- **配图相对引用**：`<img src="assets/…">`

## 目录结构

```
public/                     ← 唯一发布目录（Pages 只上传这里）
├── index.html              # 交付物：单文件页面
├── cultivation.css         # 境界图表样式（外部依赖，勿改）
├── javascripts/cultivation-chart.js
├── assets/                 # 374 张发布图
├── sitemap.xml
└── robots.txt

dev/                        ← 开发资料，永不上站
├── Agent.md                # 开发文档（改代码前先读）
├── _review.md              # 数据审校笔记
├── _backup/                # 迭代备份与脚本（index-vNN.html + apply_*.py）
├── tools/
│   ├── image-slim.py       # 图片瘦身（逐图判定 WebP/JPEG）
│   └── verify.mjs          # 零依赖验收脚本（见下）
└── watermark.svg           # 仅供 _backup 旧版引用的水印瓦片
```

> 图片已统一瘦身：卡片实际只显示 180–240px 宽，发布图压到**长边 ≤ 800px / JPEG q76**（90MB → 20MB）。新增图片的标准做法与「取回原始高清图」的命令见 `dev/Agent.md` §6。

## 本地预览

```bash
cd public && python3 -m http.server 8123   # 打开 http://127.0.0.1:8123/
```

或直接双击 `public/index.html`（图片为相对路径，`file://` 可用）。

## 改完先过验收

```bash
node dev/tools/verify.mjs                                        # 默认 file:// 直开 public/index.html
node dev/tools/verify.mjs --url http://localhost:8123/index.html # 或指定地址
```

25 条断言，每条只查一件事：七个视图容器与各自的唯一 h1 / 四库卡片数（221/40/64/65）/ **图片引用无缺图且全部能解码** / 互引网络规模 / 核心圈默认生效且可一键切回全部 / 无横向溢出与无竖条文本（桌面 1440×900 与移动 390×844 各跑一遍）/ 篇章筛选 / 三库分类筛选与搜索（含搜索深度一致性）/ 搜索定位落点 / 卡片互引跳转 / 返回顶部与进度环 / 深链冷启动 / 点卡片同步 URL / 浏览器返回后视图与地址一致 / 无第三方资源请求 / 控制台无报错。失败会打印实测值并以非 0 退出码结束。

零依赖：只需 **Node ≥ 22**（内建 WebSocket/fetch）与**本机 Chrome**，不需要 `npm install`；Chrome 不在默认位置时用 `--chrome <路径>` 或 `CHROME_PATH` 指定。

用 CDP 而不是 puppeteer，是因为本仓库刻意不引入 node_modules —— 脚本挂在 `dev/` 下，不影响 `public/` 的零构建交付。

## 发布

推送到 `main` → GitHub Actions 只把 **`public/`** 上传为 Pages 产物（`dev/` 永不上站）。

- 首次需要在仓库 **Settings → Pages → Source** 选择 **GitHub Actions**
- 自定义域名继承自用户站，项目页自动落在 `bunnychen.top/fanren-wiki/`，本仓库不需要 `CNAME` 文件

## 来历

原为 `Lizhenghe-Chen.github.io` 仓库下的静态目录（`docs/docs/Other/fanren-characters/`，2026-09-14 起随主站发布），2026-09-17 拆分独立，**git 提交历史完整保留**。主站旧路径保留跳转桩指向本站。

反馈入口（含评论区）仍在主站：https://bunnychen.top/docs/Other/fanren-xiuxian/

## 许可

**CC BY-NC 4.0**（署名—非商业性使用 4.0 国际），全文见 `LICENSE`。

- 原创整理内容（资料的采集与编排、页面设计与文案）：允许署名非商业转载/镜像；禁止商业使用、禁止去除署名与水印后发布
- 角色图片为网络检索素材，**版权归各自权利人**，本仓库不主张权利，权利人可要求删除


