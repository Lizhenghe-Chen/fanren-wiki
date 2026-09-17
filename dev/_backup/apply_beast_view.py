# -*- coding: utf-8 -*-
"""第四视图：插入 CSS + HTML + 导航（灵兽灵虫）。"""
import io

P = r"/Users/bunnychen/Documents/GitProjects/Lizhenghe-Chen.github.io/docs/docs/Other/fanren-characters/index.html"
html = io.open(P, encoding="utf-8").read()

# ========== 1. 插入 CSS（水印样式之前） ==========
css = """
/* ===== 灵兽灵虫视图 ===== */
.beast-rail-sec{padding:4px 0 8px}
.beast-rail{display:grid;grid-template-columns:repeat(6,minmax(150px,1fr));gap:8px;overflow-x:auto;padding:4px 0 12px}
.beast-node{min-width:150px;padding:14px 12px;border-top:3px solid var(--gold);background:rgba(255,255,255,.035);border-radius:0 0 10px 10px}
.beast-node:nth-child(-n+2){border-color:#7fb3d9}
.beast-node:nth-child(n+3):nth-child(-n+4){border-color:#b06ad4}
.beast-node:nth-child(n+5){border-color:#4ec9a0}
.beast-node:nth-child(n+6){border-color:#e07b54}
.beast-node b{display:block;font-family:"Noto Serif SC",serif;font-size:15px;white-space:nowrap}
.beast-node .bl{display:block;color:var(--gold);font-size:12px;margin-top:3px;font-weight:600}
.beast-node span{display:block;color:var(--ink3);font-size:11px;margin-top:5px;line-height:1.65}
.beast-tabs{display:flex;flex-wrap:wrap;gap:8px;margin:8px 0 18px}
.beast-tab{padding:7px 15px;border:1px solid var(--line);border-radius:999px;background:rgba(255,255,255,.03);color:var(--ink2);font-size:13px;cursor:pointer;transition:.18s;letter-spacing:.03em}
.beast-tab:hover{color:var(--gold);border-color:rgba(212,175,106,.5)}
.beast-tab.active{background:var(--gold);border-color:var(--gold);color:#14161d;font-weight:700}
.beast-tab .cnt{font-size:11px;opacity:.75;margin-left:4px}
.beast-grid{margin-bottom:30px}
.beast-cat-tag{position:absolute;top:10px;left:10px;z-index:2;font-size:11px;padding:3px 9px;border-radius:999px;background:rgba(14,16,22,.82);border:1px solid rgba(212,175,106,.4);color:var(--gold);letter-spacing:.04em}
@media (max-width:760px){
  .beast-rail{grid-template-columns:repeat(3,minmax(140px,1fr))}
}
"""
anchor_css = "@media (prefers-reduced-motion:reduce){"
assert anchor_css in html, "CSS 锚点未找到"
html = html.replace(anchor_css, css + "\n" + anchor_css, 1)
print("1. CSS 插入完成")

# ========== 2. 插入 HTML 视图（footer 之前） ==========
view_html = """
<div class="view" id="v-beasts">
<!-- ===== 灵兽灵虫 Hero ===== -->
<section class="hero">
  <div class="wrap hero-inner">
    <div class="hero-copy">
      <div class="hero-title"><h1>灵兽灵虫<br><span class="accent">妖兽图鉴</span></h1><span class="kicker">灵宠 · 妖兽 · 真灵 · 魔物</span></div>
      <p class="hero-sub">韩立的本命灵虫与灵宠、乱星海大妖、灵界魔物与上古真灵，按类别与等级归档整理。妖兽等级与人界境界的对应关系见下方「等级制度」。</p>
      <div class="stats">
        <div class="stat"><b id="beast-total">0</b><span>收录条目</span></div>
        <div class="stat"><b>5</b><span>类别</span></div>
        <div class="stat"><b id="beast-img">0</b><span>配图条目</span></div>
      </div>
    </div>
    <div class="hero-cover"><img src="assets/jintong_lingjie.jpg" alt="噬金虫"></div>
  </div>
</section>

<!-- ===== 妖兽等级制度 ===== -->
<section class="beast-rail-sec">
  <div class="wrap">
    <div class="sec-title">妖兽等级制度</div>
    <div class="sec-desc">原著妖兽按 1—13 级划分（每级又分初/中/上阶），对应人界修士境界；十级之后直接以修士境界命名（化神妖兽、炼虚妖兽等）。本图鉴按此归档。</div>
    <div class="beast-rail" id="beastRail"></div>
  </div>
</section>

<!-- ===== 分类浏览 ===== -->
<section class="beast-main-sec">
  <div class="wrap">
    <div class="sec-title">灵兽灵虫图谱</div>
    <div class="sec-desc">点击卡片展开详情（含结局与生平），默认仅显示类别与等级、不剧透。图片为网络检索素材（动画截图/概念图/同人图），冷门角色以首字占位，形象可能与官方设定存在偏差，请以文字资料为准。</div>
    <div class="beast-tabs" id="beastTabs"></div>
    <div class="grid beast-grid" id="beasts"></div>
    <div class="empty-tip" id="beastEmpty">该类别暂无条目。</div>
  </div>
</section>

</div>
"""
anchor_footer = "<footer>"
assert anchor_footer in html, "footer 锚点未找到"
html = html.replace(anchor_footer, view_html + anchor_footer, 1)
print("2. HTML 视图插入完成")

# ========== 3. 导航新增第四项 ==========
nav_old = '<a href="#v-realms" data-view="v-realms">境界体系</a>'
nav_new = nav_old + '\n    <a href="#v-beasts" data-view="v-beasts">灵兽灵虫</a>'
assert nav_old in html, "导航锚点未找到"
html = html.replace(nav_old, nav_new, 1)
print("3. 导航更新完成")

io.open(P, "w", encoding="utf-8").write(html)
print("已写回 index.html")
