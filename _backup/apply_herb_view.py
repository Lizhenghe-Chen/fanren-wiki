# -*- coding: utf-8 -*-
"""第五视图：灵草丹药 v-herbs — 综合构建脚本（CSS+HTML+导航+JS数据+渲染+启动+路由+manifest）"""
import io, re, os

P = r"/Users/bunnychen/Documents/GitProjects/Lizhenghe-Chen.github.io/docs/docs/Other/fanren-characters/index.html"
DATA = r"/Users/bunnychen/Documents/GitProjects/Lizhenghe-Chen.github.io/docs/docs/Other/fanren-characters/_backup/herbs_data.js"
ASSETS = r"/Users/bunnychen/Documents/GitProjects/Lizhenghe-Chen.github.io/docs/docs/Other/fanren-characters/assets"

html = io.open(P, encoding="utf-8").read()
data_js = io.open(DATA, encoding="utf-8").read()

# ========== 提取数据并过滤 img 字段 ==========
# 提取 HERB_CATS
cats_match = re.search(r'const HERB_CATS = \[(.*?)\];', data_js, re.DOTALL)
herb_cats = cats_match.group(0)

# 提取 HERB_RAIL
rail_match = re.search(r'const HERB_RAIL = \[(.*?)\];', data_js, re.DOTALL)
herb_rail = rail_match.group(0)

# 提取 HERBS 并过滤 img 字段（只保留实际存在的文件）
herbs_match = re.search(r'const HERBS = \[(.*?)\];', data_js, re.DOTALL)
herbs_raw = herbs_match.group(0)

# 获取实际存在的灵草丹药图片文件
existing_imgs = set()
for f in os.listdir(ASSETS):
    if f.endswith('.jpg'):
        existing_imgs.add(f)

# 过滤 HERBS 中的 img 字段：不存在的文件移除 img 字段
def filter_herb_imgs(text):
    # 匹配 img:"xxx.jpg" ，如果文件不存在则移除
    def replace_img(m):
        fname = m.group(1)
        if fname in existing_imgs:
            return m.group(0)
        return ''  # 移除不存在的 img 字段
    return re.sub(r'img:"([^"]+)",?\s*', replace_img, text)

herbs_filtered = filter_herb_imgs(herbs_raw)

# 统计有图的条目
img_count = len(re.findall(r'img:"([^"]+)"', herbs_filtered))
print(f"HERBS 数据: {herbs_filtered.count('{n:')} 条, 其中 {img_count} 条有图")

# 获取新增的图片文件列表（用于 manifest）
herb_img_files = sorted(set(re.findall(r'img:"([^"]+)"', herbs_filtered)))
print(f"新增图片文件: {herb_img_files}")

# ========== 1. 插入 CSS ==========
css = """
/* ===== 灵草丹药视图 ===== */
.herb-rail-sec{padding:4px 0 8px}
.herb-rail{display:grid;grid-template-columns:repeat(6,minmax(150px,1fr));gap:8px;overflow-x:auto;padding:4px 0 12px}
.herb-node{min-width:150px;padding:14px 12px;border-top:3px solid var(--gold);background:rgba(255,255,255,.035);border-radius:0 0 10px 10px}
.herb-node:nth-child(-n+2){border-color:#7ec97e}
.herb-node:nth-child(n+3):nth-child(-n+4){border-color:#d4a843}
.herb-node:nth-child(n+5){border-color:#e06060}
.herb-node:nth-child(n+6){border-color:#b06ad4}
.herb-node b{display:block;font-family:"Noto Serif SC",serif;font-size:15px;white-space:nowrap}
.herb-node .bl{display:block;color:var(--gold);font-size:12px;margin-top:3px;font-weight:600}
.herb-node span{display:block;color:var(--ink3);font-size:11px;margin-top:5px;line-height:1.65}
.herb-tabs{display:flex;flex-wrap:wrap;gap:8px;margin:8px 0 12px}
.herb-tab{padding:7px 15px;border:1px solid var(--line);border-radius:999px;background:rgba(255,255,255,.03);color:var(--ink2);font-size:13px;cursor:pointer;transition:.18s;letter-spacing:.03em}
.herb-tab:hover{color:var(--gold);border-color:rgba(212,175,106,.5)}
.herb-tab.active{background:var(--gold);border-color:var(--gold);color:#14161d;font-weight:700}
.herb-tab .cnt{font-size:11px;opacity:.75;margin-left:4px}
.herb-grid{margin-bottom:30px}
.herb-cat-tag{position:absolute;top:10px;left:10px;z-index:2;font-size:11px;padding:3px 9px;border-radius:999px;background:rgba(14,16,22,.82);border:1px solid rgba(212,175,106,.4);color:var(--gold);letter-spacing:.04em}
.herb-search-row{display:flex;gap:10px;margin-bottom:14px;align-items:center}
.herb-search-box{flex:1;display:flex;align-items:center;gap:8px;padding:9px 14px;border:1px solid var(--line);border-radius:999px;background:rgba(255,255,255,.03);transition:.18s}
.herb-search-box:focus-within{border-color:rgba(212,175,106,.5)}
.herb-search-box svg{flex-shrink:0;opacity:.5}
.herb-search-box input{flex:1;background:transparent;border:none;outline:none;color:var(--ink1);font-size:14px;font-family:inherit}
.herb-search-box input::placeholder{color:var(--ink3)}
@media (max-width:760px){
  .herb-rail{grid-template-columns:repeat(3,minmax(140px,1fr))}
  .herb-search-row{flex-direction:column}
}
"""
anchor_css = "@media (prefers-reduced-motion:reduce){"
assert anchor_css in html, "CSS 锚点未找到"
html = html.replace(anchor_css, css + "\n" + anchor_css, 1)
print("1. CSS 插入完成")

# ========== 2. 插入 HTML 视图（footer 之前） ==========
view_html = """
<div class="view" id="v-herbs">
<!-- ===== 灵草丹药 Hero ===== -->
<section class="hero">
  <div class="wrap hero-inner">
    <div class="hero-copy">
      <div class="hero-title"><h1>灵草丹药<br><span class="accent">修仙资源图鉴</span></h1><span class="kicker">灵草 · 天材 · 丹药 · 丹方</span></div>
      <p class="hero-sub">韩立修仙路上的灵草灵药、天材地宝、突破丹药与辅助丹方，按类别与年份等级归档整理。灵药年份与人界境界的对应关系见下方「灵药年份等级」。数据依据起点《凡人必备手册》及原著情节交叉验证。</p>
      <div class="stats">
        <div class="stat"><b id="herb-total">0</b><span>收录条目</span></div>
        <div class="stat"><b>5</b><span>类别</span></div>
        <div class="stat"><b id="herb-img">0</b><span>配图条目</span></div>
      </div>
    </div>
    <div class="hero-cover"><img src="assets/zhangtianping.jpg" alt="掌天瓶"></div>
  </div>
</section>

<!-- ===== 灵药年份等级 ===== -->
<section class="herb-rail-sec">
  <div class="wrap">
    <div class="sec-title">灵药年份等级</div>
    <div class="sec-desc">原著灵药按年份与品阶划分，对应修士境界用途。普通草药至百年灵药供炼气筑基使用，千年灵药可炼制结丹级丹药，万年灵药为元婴级奇珍，灵界奇珍与仙界仙药为更高层次资源。本图鉴按此归档。</div>
    <div class="herb-rail" id="herbRail"></div>
  </div>
</section>

<!-- ===== 分类浏览 ===== -->
<section class="beast-main-sec">
  <div class="wrap">
    <div class="sec-title">灵草丹药图谱</div>
    <div class="sec-desc">点击卡片展开详情（含结局与相关事件），默认仅显示类别与等级、不剧透。图片为中国风插画（动画未具象化的道具以插画呈现），冷门条目以首字占位，形象可能与官方设定存在偏差，请以文字资料为准。</div>
    <div class="herb-search-row">
      <div class="herb-search-box">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4"><circle cx="11" cy="11" r="7"/><path d="M20 20l-3.5-3.5"/></svg>
        <input id="herbSearchInput" type="text" placeholder="搜索灵草丹药…" autocomplete="off">
      </div>
    </div>
    <div class="herb-tabs" id="herbTabs"></div>
    <div class="grid herb-grid" id="herbs"></div>
    <div class="empty-tip" id="herbEmpty">该类别暂无条目。</div>
  </div>
</section>

</div>
"""
anchor_footer = "<footer>"
assert anchor_footer in html, "footer 锚点未找到"
html = html.replace(anchor_footer, view_html + anchor_footer, 1)
print("2. HTML 视图插入完成")

# ========== 3. 导航新增第五项 ==========
nav_old = '<a href="#v-beasts" data-view="v-beasts">灵兽灵虫</a>'
nav_new = nav_old + '\n    <a href="#v-herbs" data-view="v-herbs">灵草丹药</a>'
assert nav_old in html, "导航锚点未找到"
html = html.replace(nav_old, nav_new, 1)
print("3. 导航更新完成")

# ========== 4. 插入 JS 数据（时间轴定义之前，用精确锚点避免CSS撞车） ==========
data_block = "\n" + herb_cats + "\n\n" + herb_rail + "\n\n" + herbs_filtered + "\n"
anchor_data = "\n\n/* ===== 韩立境界时间轴 ===== */\nconst TL = ["
assert anchor_data in html, "数据锚点未找到（精确匹配）"
html = html.replace(anchor_data, data_block + anchor_data, 1)
print("4. JS 数据插入完成")

# ========== 5. 插入渲染函数（启动之前） ==========
render_js = """
/* ===== 灵草丹药渲染 ===== */
let herbTab = "all";
let herbKeyword = "";
function renderHerbRail(){
  const el = document.getElementById("herbRail");
  if(!el) return;
  el.innerHTML = HERB_RAIL.map(function(r){
    return '<div class="herb-node"><b>' + esc(r.lv) + '</b><span class="bl">' + esc(r.realm) + '</span><span>' + esc(r.note) + '</span></div>';
  }).join("");
}
function renderHerbTabs(){
  const el = document.getElementById("herbTabs");
  if(!el) return;
  const cnt = function(id){ return id==="all" ? HERBS.length : HERBS.filter(function(b){return b.cat===id;}).length; };
  el.innerHTML = HERB_CATS.map(function(c){
    return '<button class="herb-tab' + (c.id===herbTab ? " active" : "") + '" data-cat="' + c.id + '">' + esc(c.name) + '<span class="cnt">' + cnt(c.id) + '</span></button>';
  }).join("");
}
function renderHerbs(){
  const el = document.getElementById("herbs");
  if(!el) return;
  el.innerHTML = HERBS.map(function(c){
    const safeName = escapeAttr(c.n || "");
    const safeTitle = escapeAttr(c.t || "");
    const fallbackLetter = escapeAttr(((c.n || "")[0]) || "?");
    const img = c.img
      ? '<img class="card-img" src="assets/' + escapeAttr(c.img) + '" alt="' + safeName + '" loading="lazy">'
      : '<div class="ph">' + fallbackLetter + '</div>';
    const cat = HERB_CATS.find(function(x){return x.id===c.cat;}) || HERB_CATS[0];
    return '<div class="card" data-name="' + safeName + '" data-aka="' + safeTitle + '" data-cat="' + c.cat + '">' +
      '<div class="card-top">' + img + '<span class="herb-cat-tag" style="color:' + cat.color + ';border-color:' + cat.color + '">' + esc(cat.name) + '</span></div>' +
      '<div class="card-body">' +
        '<div class="card-name"><h3>' + esc(c.n) + '</h3>' + (c.t?'<span class="aka">' + esc(c.t) + '</span>':"") + '</div>' +
        ((c.rel||c.camp)?'<div class="card-chips">' +
          (c.rel?'<span class="chip rel" title="相关人物">' + esc(c.rel) + '</span>':"") +
          (c.camp?'<span class="chip camp" title="来源出处">' + esc(c.camp) + '</span>':"") +
        '</div>':"") +
        '<div class="card-row realm"><span class="lb">等级</span><span class="tx">' + esc(c.r) + '</span></div>' +
        '<div class="card-extra">' +
          '<div class="card-row"><span class="lb">结局</span><span class="tx">' + esc(c.e) + '</span></div>' +
          (c.s?'<div class="card-row"><span class="lb">详情</span><span class="tx">' + esc(c.s) + '</span></div>':"") +
        '</div>' +
        '<div class="card-hint"><span class="chev">▾</span>点击展开详情</div>' +
      '</div>' +
    '</div>';
  }).join("");
  el.querySelectorAll(".card-img").forEach(function(img){
    img.addEventListener("error", function(){
      const cardTop = img.parentElement;
      if (!cardTop || cardTop.querySelector(".ph")) return;
      const tag = cardTop.querySelector(".herb-cat-tag");
      cardTop.innerHTML = '<div class="ph">' + esc((img.alt || "?").charAt(0)) + '</div>' + (tag ? tag.outerHTML : "");
    });
  });
}
function applyHerbFilter(){
  const cards = document.querySelectorAll("#herbs .card");
  let visible = 0;
  const kw = herbKeyword.trim().toLowerCase();
  cards.forEach(function(card){
    const catOk = herbTab==="all" || card.dataset.cat===herbTab;
    const name = (card.dataset.name + " " + card.dataset.aka).toLowerCase();
    const kwOk = !kw || name.indexOf(kw) >= 0;
    const show = catOk && kwOk;
    card.style.display = show ? "" : "none";
    if(show) visible++;
  });
  document.getElementById("herbEmpty").classList.toggle("show", visible===0);
}
document.getElementById("herbTabs").addEventListener("click", function(e){
  const btn = e.target.closest(".herb-tab");
  if(!btn) return;
  document.querySelectorAll(".herb-tab").forEach(function(t){t.classList.remove("active");});
  btn.classList.add("active");
  herbTab = btn.dataset.cat;
  applyHerbFilter();
});
document.getElementById("herbSearchInput").addEventListener("input", function(e){
  herbKeyword = e.target.value;
  applyHerbFilter();
});
document.getElementById("herbs").addEventListener("click", function(event){
  const card = event.target.closest(".card");
  if (!card) return;
  card.classList.toggle("open");
});

"""
anchor_render = "/* ===== 启动 ===== */"
assert anchor_render in html, "渲染锚点未找到"
html = html.replace(anchor_render, render_js + anchor_render, 1)
print("5. 渲染函数插入完成")

# ========== 6. 启动调用 ==========
old_boot = "renderBeastRail();\nrenderBeastTabs();\nrenderBeasts();\napplyBeastFilter();"
new_boot = old_boot + """
document.getElementById("herb-total").textContent = HERBS.length;
document.getElementById("herb-img").textContent = new Set(HERBS.filter(function(c){return c.img;}).map(function(c){return c.img;})).size;
renderHerbRail();
renderHerbTabs();
renderHerbs();
applyHerbFilter();"""
assert old_boot in html, "启动锚点未找到"
html = html.replace(old_boot, new_boot, 1)
print("6. 启动调用插入完成")

# ========== 7. 路由 VIEWS ==========
old_views = 'var VIEWS = ["v-chars","v-lore","v-realms","v-beasts"];'
new_views = 'var VIEWS = ["v-chars","v-lore","v-realms","v-beasts","v-herbs"];'
assert old_views in html, "VIEWS 锚点未找到"
html = html.replace(old_views, new_views, 1)
print("7. 路由更新完成")

# ========== 8. 更新 .asset-manifest ==========
# 在 manifest 最后追加新增图片
manifest_add = "  " + ", ".join([f'url("assets/{f}")' for f in herb_img_files]) + ",\n"
# 找到 manifest 中最后一个 url() 行（shuangtongshu 之后）
manifest_pattern = re.compile(
    r'(url\("assets/mojiao\.jpg"\), url\("assets/liuyishuangwu\.jpg"\), url\("assets/xueyuzhizhu\.jpg"\), url\("assets/shuangtongshu\.jpg"\),\n)'
    r'((?:url\("assets/[^"]+"\),\n)*)'
    r'(;})'
)
m = manifest_pattern.search(html)
if m:
    # 在已有新增行之后、;} 之前插入
    existing_new = m.group(2)
    html = html[:m.start(2)] + existing_new + manifest_add + html[m.end(2):]
    print(f"8. asset-manifest 更新完成（新增 {len(herb_img_files)} 个文件）")
else:
    # 备用：直接在 shuangtongshu 行后插入
    alt = 'url("assets/shuangtongshu.jpg"),\n'
    if alt in html:
        html = html.replace(alt, alt + manifest_add, 1)
        print(f"8. asset-manifest 更新完成（备用方式，新增 {len(herb_img_files)} 个文件）")
    else:
        print("8. ⚠️ asset-manifest 更新失败！")

io.open(P, "w", encoding="utf-8").write(html)
print("\n✅ index.html 已更新（v-herbs 第五视图构建完成）")
