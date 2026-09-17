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
├── assets/                 # 302 张发布图
├── sitemap.xml
└── robots.txt

dev/                        ← 开发资料，永不上站
├── Agent.md                # 开发文档（改代码前先读）
├── _review.md              # 数据审校笔记
├── _backup/                # 迭代备份与脚本（index-vNN.html + apply_*.py）
├── unused-assets/          # 未被当前页面引用的历史素材（见下）
└── watermark.svg           # 仅供 _backup 旧版引用的水印瓦片
```

> `dev/unused-assets/` 里现存 67 张，是**未被当前页面引用的实名角色/法宝图**（曾被历史版本使用，或可作补图素材）。删除不影响线上站点。

## 本地预览

```bash
cd public && python3 -m http.server 8123   # 打开 http://127.0.0.1:8123/
```

或直接双击 `public/index.html`（图片为相对路径，`file://` 可用）。

## 发布

推送到 `main` → GitHub Actions 只把 **`public/`** 上传为 Pages 产物（`dev/` 永不上站）。

- 首次需要在仓库 **Settings → Pages → Source** 选择 **GitHub Actions**
- 自定义域名继承自用户站，项目页自动落在 `bunnychen.top/fanren-wiki/`，本仓库不需要 `CNAME` 文件

## 来历

原为 `Lizhenghe-Chen.github.io` 仓库下的静态目录（`docs/docs/Other/fanren-characters/`，2026-09-14 起随主站发布），2026-09-17 拆分独立，**git 提交历史完整保留**。主站旧路径保留跳转桩指向本站。

反馈入口（含评论区）仍在主站：https://bunnychen.top/docs/Other/fanren-xiuxian/

## 许可

- 页面原创整理内容：**署名 + 非商业**（见页面页脚与主站 https://bunnychen.top/about/LICENSE/ ）
- ⚠️ 仓库根目录的 `LICENSE` 目前是 **GPL-3.0**，与上述声明冲突（GPL 不允许附加非商业限制），**待统一**
- 角色图片为网络检索素材，版权归各自权利人


