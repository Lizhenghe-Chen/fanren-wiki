# -*- coding: utf-8 -*-
"""页面重构：垂直单页 -> 页内多视图（hash 路由切换）。
视图1 人物图谱（hero+篇章导航+卡片区）；视图2 剧情速览（时间轴+故事脉络）；视图3 境界体系（境界+统计+图例）。
"""
import io, re

SRC = "/Users/bunnychen/Library/CloudStorage/OneDrive-Personal/我的工作文档/BunnyChen.github.io/docs/docs/Other/fanren-characters/index.html"
html = io.open(SRC, encoding="utf-8").read()

def cut(html, start_mark, end_mark):
    si = html.index(start_mark)
    ei = html.index(end_mark, si)
    return html[si:ei], html[:si] + html[ei:]

# ---- 1. 切分各块 ----
hero_blk, html = cut(html, "<!-- ===== Hero ===== -->", "<!-- ===== 韩立境界时间轴 ===== -->")
tl_blk,   html = cut(html, "<!-- ===== 韩立境界时间轴 ===== -->", "<!-- ===== 故事脉络 · 核心因果链 ===== -->")
lore_blk, html = cut(html, "<!-- ===== 故事脉络 · 核心因果链 ===== -->", "<!-- ===== 导航 ===== -->")
nav_blk,  html = cut(html, "<!-- ===== 导航 ===== -->", "<!-- ===== 篇章 ===== -->")
note_blk, html = cut(html, "<!-- ===== 篇章 ===== -->", '<main class="wrap" id="characters">')
main_blk, html = cut(html, '<main class="wrap" id="characters">', "<!-- ===== 境界体系 ===== -->")
realm_blk,html = cut(html, "<!-- ===== 境界体系 ===== -->", "<!-- ===== 各篇人数分布 ===== -->")
bar_blk,  html = cut(html, "<!-- ===== 各篇人数分布 ===== -->", "<!-- ===== 图例 ===== -->")
legend_blk,html = cut(html, "<!-- ===== 图例 ===== -->", "<footer>")
footer_blk, html = cut(html, "<footer>", "<script>")

print("hero:", len(hero_blk), "| tl:", len(tl_blk), "| lore:", len(lore_blk),
      "| nav:", len(nav_blk), "| note:", len(note_blk), "| main:", len(main_blk),
      "| realm:", len(realm_blk), "| bar:", len(bar_blk), "| legend:", len(legend_blk),
      "| footer:", len(footer_blk), "| rest:", len(html[:100]))

# ---- 2. hero 链接改为视图 hash ----
hero_blk = hero_blk.replace('href="#characters"', 'href="#v-chars"').replace('href="#realms"', 'href="#v-realms"')

# ---- 3. 组装新 body ----
topnav = '''<!-- ===== 主导航（视图切换） ===== -->
<nav class="topnav">
  <div class="wrap">
    <span class="tn-brand">凡人修仙传 · 人物图谱</span>
    <a href="#v-chars" data-view="v-chars" class="active">人物图谱</a>
    <a href="#v-lore" data-view="v-lore">剧情速览</a>
    <a href="#v-realms" data-view="v-realms">境界体系</a>
  </div>
</nav>

'''
v_chars = '<div class="view" id="v-chars">\n' + hero_blk + nav_blk + note_blk + main_blk + '</div>\n'
v_lore  = '<div class="view" id="v-lore">\n' + tl_blk + lore_blk + '</div>\n'
v_realms= '<div class="view" id="v-realms">\n' + realm_blk + bar_blk + legend_blk + '</div>\n'

# 插入位置：在 body 内的 asset-manifest 之后
anchor = '<div class="asset-manifest"></div>'
si = html.index(anchor)
new_body = html[:si+len(anchor)] + "\n" + topnav + v_chars + v_lore + v_realms + footer_blk + "<script>"
html = new_body + html[html.index("<script>")+len("<script>"):]

# ---- 4. CSS ----
CSS = '''
/* ===== 顶部主导航 ===== */
.topnav{background:linear-gradient(180deg,rgba(12,14,20,.98),rgba(12,14,20,.9));border-bottom:1px solid rgba(212,175,106,.18)}
.topnav .wrap{display:flex;gap:4px;align-items:center;height:48px;flex-wrap:nowrap}
.tn-brand{margin-right:14px;font-weight:800;color:var(--gold);font-size:14.5px;letter-spacing:.08em;white-space:nowrap}
.topnav a{display:inline-flex;align-items:center;padding:6px 16px;font-size:13.5px;color:var(--ink2);border-radius:8px;transition:.2s;letter-spacing:.04em;white-space:nowrap}
.topnav a:hover{color:var(--gold)}
.topnav a.active{color:#14161d;background:var(--gold);font-weight:700}
/* ===== 视图切换 ===== */
.view{display:none}
.view.active{display:block}
@media (max-width:640px){
  .tn-brand{display:none}
  .topnav .wrap{height:44px}
  .topnav a{padding:6px 11px;font-size:12.5px}
}
'''
css_anchor = "/* ===== 图例与页脚 ===== */"
assert css_anchor in html
html = html.replace(css_anchor, CSS + "\n" + css_anchor, 1)

# ---- 5. JS 视图切换（追加到现有初始化之后） ----
view_js = '''
/* ===== 视图切换（hash 路由） ===== */
(function(){
  var VIEWS = ["v-chars","v-lore","v-realms"];
  function switchView(id){
    if (VIEWS.indexOf(id) < 0) id = "v-chars";
    document.querySelectorAll(".view").forEach(function(v){ v.classList.toggle("active", v.id === id); });
    document.querySelectorAll(".topnav a").forEach(function(a){ a.classList.toggle("active", a.getAttribute("data-view") === id); });
  }
  function fromHash(){ return (location.hash || "").replace("#", ""); }
  window.addEventListener("hashchange", function(){ switchView(fromHash()); });
  switchView(fromHash());
})();
'''
# 追加到 </script> 前
html = html.replace("</script>", view_js + "\n</script>", 1)

io.open(SRC, "w", encoding="utf-8").write(html)
print("分页重构完成")
