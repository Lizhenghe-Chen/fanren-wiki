# -*- coding: utf-8 -*-
"""
v-treasures 第六视图综合构建脚本
1. 将 herbs_data_v2.js 的14条补充追加到 HERBS 数组
2. 添加 v-treasures CSS
3. 添加 v-treasures HTML 视图
4. 添加导航链接
5. 添加 JS 数据（TREASURE_CATS/TREASURE_RAIL/TREASURES）
6. 添加渲染函数
7. 添加启动调用 + VIEWS 路由
8. 更新 asset-manifest
"""
import io, re

P = r"/Users/bunnychen/Documents/GitProjects/Lizhenghe-Chen.github.io/docs/docs/Other/fanren-characters/index.html"
TREASURES_DATA = r"/Users/bunnychen/Documents/GitProjects/Lizhenghe-Chen.github.io/docs/docs/Other/fanren-characters/_backup/treasures_data.js"
HERBS_V2 = r"/Users/bunnychen/Documents/GitProjects/Lizhenghe-Chen.github.io/docs/docs/Other/fanren-characters/_backup/herbs_data_v2.js"

html = io.open(P, encoding="utf-8").read()
treasures_js = io.open(TREASURES_DATA, encoding="utf-8").read()
herbs_v2_js = io.open(HERBS_V2, encoding="utf-8").read()

# ========== 1. 将 herbs_data_v2.js 的14条追加到 HERBS 数组 ==========
# 提取 HERBS_V2_SUPPLEMENT 数组中的元素（去掉 const 和数组包装）
v2_match = re.search(r'const HERBS_V2_SUPPLEMENT = \[(.*?)\];', herbs_v2_js, re.DOTALL)
if v2_match:
    v2_elements = v2_match.group(1).strip()
    # 找到 HERBS 数组的结束位置（在 const HERB_RAIL 之前）
    # HERBS 数组以 ]; 结束，后面紧跟 const HERB_RAIL
    herbs_end_pattern = r'(const HERBS = \[.*?\n\];)\n\nconst HERB_RAIL'
    m = re.search(herbs_end_pattern, html, re.DOTALL)
    if m:
        # 在 HERBS 数组的 ]; 之前插入 v2 元素
        herbs_array_end = m.end(1) - 2  # 位置在 ]; 之前
        # 确保 v2_elements 以逗号开头或前面有逗号
        insert_text = '\n  /* ===== v2 补充 ===== */\n' + v2_elements + '\n'
        html = html[:herbs_array_end] + insert_text + html[herbs_array_end:]
        print("1. ✅ HERBS 数组追加14条补充数据")
    else:
        print("1. ❌ 未找到 HERBS 数组结束位置")
else:
    print("1. ❌ 未找到 HERBS_V2_SUPPLEMENT 数组")

# ========== 2. 添加 v-treasures CSS ==========
treasures_css = '''
/* ===== v-treasures 法器法宝 ===== */
#v-treasures .treasure-rail{display:flex;gap:8px;margin:18px 0 12px;flex-wrap:wrap}
#v-treasures .treasure-rail .rail-item{flex:1;min-width:110px;background:linear-gradient(160deg,rgba(212,168,67,.12),rgba(212,168,67,.04));border:1px solid rgba(212,168,67,.3);border-radius:10px;padding:10px 12px;text-align:center}
#v-treasures .treasure-rail .rail-lv{font-size:15px;font-weight:700;color:var(--gold)}
#v-treasures .treasure-rail .rail-realm{font-size:11px;color:var(--ink3);margin-top:3px}
#v-treasures .treasure-tabs{display:flex;gap:6px;margin:14px 0;flex-wrap:wrap}
#v-treasures .treasure-tabs .tab{padding:6px 14px;border-radius:20px;border:1px solid rgba(255,255,255,.15);cursor:pointer;font-size:13px;color:var(--ink2);transition:all .2s}
#v-treasures .treasure-tabs .tab.active{background:var(--gold);color:#1a1a2e;border-color:var(--gold);font-weight:700}
#v-treasures .treasure-search{width:100%;max-width:400px;padding:9px 14px;border-radius:8px;border:1px solid rgba(255,255,255,.15);background:rgba(0,0,0,.3);color:var(--ink);font-size:14px;margin:10px 0}
#v-treasures .treasure-search:focus{outline:none;border-color:var(--gold)}
#v-treasures .treasure-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:14px;margin-top:14px}
#v-treasures .treasure-card{background:linear-gradient(160deg,rgba(30,30,50,.8),rgba(20,20,35,.9));border:1px solid rgba(255,255,255,.08);border-radius:12px;overflow:hidden;cursor:pointer;transition:all .25s}
#v-treasures .treasure-card:hover{border-color:rgba(212,168,67,.5);transform:translateY(-2px);box-shadow:0 8px 24px rgba(0,0,0,.4)}
#v-treasures .treasure-card .tc-img{width:100%;height:160px;object-fit:cover;background:#1a1a2e}
#v-treasures .treasure-card .tc-body{padding:12px 14px}
#v-treasures .treasure-card .tc-name{font-size:16px;font-weight:700;color:var(--gold);margin-bottom:4px}
#v-treasures .treasure-card .tc-title{font-size:12px;color:var(--ink3);margin-bottom:6px}
#v-treasures .treasure-card .tc-meta{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:6px}
#v-treasures .treasure-card .tc-tag{font-size:11px;padding:2px 8px;border-radius:10px;background:rgba(212,168,67,.15);color:var(--gold)}
#v-treasures .treasure-card .tc-realm{font-size:11px;padding:2px 8px;border-radius:10px;background:rgba(111,168,220,.15);color:#6fa8dc}
#v-treasures .treasure-card .tc-end{font-size:12px;color:var(--ink2);margin-top:4px;font-style:italic}
#v-treasures .treasure-detail{display:none;padding:12px 14px;border-top:1px solid rgba(255,255,255,.08);font-size:13px;color:var(--ink2);line-height:1.7}
#v-treasures .treasure-card.open .treasure-detail{display:block}
#v-treasures .treasure-detail .dl-row{margin-bottom:6px}
#v-treasures .treasure-detail .dl-label{color:var(--gold);font-weight:600;margin-right:6px}
'''

# 在 </style> 之前插入 CSS
if 'v-treasures .treasure-rail' not in html:
    html = html.replace('</style>', treasures_css + '\n</style>', 1)
    print("2. ✅ v-treasures CSS 已添加")
else:
    print("2. = v-treasures CSS 已存在，跳过")

# ========== 3. 添加 v-treasures HTML 视图 ==========
treasures_html = '''
  <!-- ===== v-treasures 法器法宝 ===== -->
  <section id="v-treasures" class="view">
    <div class="wrap">
      <h2 class="section-title">法器法宝 <span class="sub">Treasures & Artifacts</span></h2>
      <div class="note" style="margin-bottom:10px">收录《凡人修仙传》全篇重要法器法宝，按品阶与类型分类。数据依据起点《凡人必备手册》第二版+原著情节+多源交叉验证。</div>
      <div class="treasure-rail" id="treasureRail"></div>
      <div class="treasure-tabs" id="treasureTabs"></div>
      <input type="text" class="treasure-search" id="treasureSearchInput" placeholder="搜索法器法宝名称、持有者、出处...">
      <div class="stats" style="margin:8px 0;font-size:13px;color:var(--ink3)">
        共 <span id="treasure-total" style="color:var(--gold);font-weight:700">0</span> 件 · 有图 <span id="treasure-img" style="color:var(--gold);font-weight:700">0</span> 件
      </div>
      <div class="treasure-grid" id="treasureGrid"></div>
    </div>
  </section>
'''

# 在 </main> 之前插入 HTML 视图（如果不存在）
if 'id="v-treasures"' not in html:
    html = html.replace('</main>', treasures_html + '\n</main>', 1)
    print("3. ✅ v-treasures HTML 视图已添加")
else:
    print("3. = v-treasures HTML 已存在，跳过")

# ========== 4. 添加导航链接 ==========
if 'v-treasures' not in html.split('<nav>')[1].split('</nav>')[0] if '<nav>' in html else True:
    # 找到导航中的最后一个链接，在其后添加
    nav_pattern = r'(<a href="#v-herbs"[^>]*>.*?</a>)'
    m = re.search(nav_pattern, html)
    if m:
        nav_link = '\n      <a href="#v-treasures" data-view="v-treasures">法器法宝</a>'
        html = html[:m.end()] + nav_link + html[m.end():]
        print("4. ✅ 导航链接已添加")
    else:
        print("4. ⚠️ 未找到导航插入点")
else:
    print("4. = 导航链接已存在，跳过")

# ========== 5. 添加 JS 数据（TREASURE_CATS/TREASURE_RAIL/TREASURES）==========
# 从 treasures_data.js 中提取数据（去掉注释和 const 包装）
# 提取 TREASURE_CATS
cats_match = re.search(r'(const TREASURE_CATS = \[.*?\];)', treasures_js, re.DOTALL)
rail_match = re.search(r'(const TREASURE_RAIL = \[.*?\];)', treasures_js, re.DOTALL)
treasures_match = re.search(r'(const TREASURES = \[.*?\];)', treasures_js, re.DOTALL)

if cats_match and rail_match and treasures_match:
    js_data = '\n\n' + cats_match.group(1) + '\n\n' + rail_match.group(1) + '\n\n' + treasures_match.group(1) + '\n'
    
    # 定位到 HERBS 数据之后、韩立境界时间轴之前插入
    # 必须匹配整段避免 CSS 区撞车
    anchor = '];\n\n/* ===== 韩立境界时间轴 ===== */\nconst TL = ['
    if anchor in html:
        html = html.replace(anchor, js_data + anchor, 1)
        print("5. ✅ TREASURE_CATS/TREASURE_RAIL/TREASURES 数据已添加")
    else:
        print("5. ❌ 未找到数据插入锚点")
else:
    print("5. ❌ 数据提取失败")

# ========== 6. 添加渲染函数 ==========
treasures_render_js = '''
/* ===== v-treasures 渲染函数 ===== */
function renderTreasureRail(){
  const rail=document.getElementById("treasureRail");
  rail.innerHTML=TREASURE_RAIL.map(r=>`<div class="rail-item"><div class="rail-lv">${r.lv}</div><div class="rail-realm">${r.realm}</div></div>`).join("");
}
function renderTreasureTabs(){
  const tabs=document.getElementById("treasureTabs");
  tabs.innerHTML=TREASURE_CATS.map(c=>`<div class="tab${c.id==="all"?" active":""}" data-cat="${c.id}">${c.name}</div>`).join("");
  tabs.querySelectorAll(".tab").forEach(t=>t.addEventListener("click",()=>{
    tabs.querySelectorAll(".tab").forEach(x=>x.classList.remove("active"));
    t.classList.add("active");
    applyTreasureFilter();
  }));
}
function renderTreasures(list){
  const grid=document.getElementById("treasureGrid");
  if(!list.length){grid.innerHTML='<div class="note" style="grid-column:1/-1;text-align:center;padding:40px">未找到匹配的法器法宝</div>';return;}
  grid.innerHTML=list.map(t=>{
    const cat=TREASURE_CATS.find(c=>c.id===t.cat);
    const imgHtml=t.img?`<img class="tc-img" src="assets/${t.img}" alt="${t.n}" loading="lazy">`:`<div class="tc-img" style="display:flex;align-items:center;justify-content:center;font-size:48px;color:var(--gold);opacity:.3">${t.n[0]}</div>`;
    return `<div class="treasure-card" data-name="${t.n}">
      ${imgHtml}
      <div class="tc-body">
        <div class="tc-name">${t.n}</div>
        <div class="tc-title">${t.t}</div>
        <div class="tc-meta">
          <span class="tc-tag" style="background:${cat?cat.color+"22":"rgba(212,168,67,.15)"};color:${cat?cat.color:"var(--gold)"}">${cat?cat.name:t.cat}</span>
          <span class="tc-realm">${t.r}</span>
        </div>
        <div class="tc-end">${t.e}</div>
      </div>
      <div class="treasure-detail">
        <div class="dl-row"><span class="dl-label">来历：</span>${t.s}</div>
        <div class="dl-row"><span class="dl-label">持有者：</span>${t.rel}</div>
        <div class="dl-row"><span class="dl-label">出处：</span>${t.camp}</div>
      </div>
    </div>`;
  }).join("");
  grid.querySelectorAll(".treasure-card").forEach(c=>c.addEventListener("click",()=>c.classList.toggle("open")));
  document.getElementById("treasure-total").textContent=list.length;
  document.getElementById("treasure-img").textContent=list.filter(t=>t.img).length;
}
function applyTreasureFilter(){
  const cat=document.querySelector("#treasureTabs .tab.active").dataset.cat;
  const q=document.getElementById("treasureSearchInput").value.toLowerCase();
  let list=TREASURES;
  if(cat!=="all")list=list.filter(t=>t.cat===cat);
  if(q)list=list.filter(t=>(t.n+t.t+t.rel+t.camp+t.s).toLowerCase().includes(q));
  renderTreasures(list);
}
'''

# 在 switchView 函数之前插入渲染函数
if 'function renderTreasureRail' not in html:
    switchview_pattern = r'(\nfunction switchView\()'
    m = re.search(switchview_pattern, html)
    if m:
        html = html[:m.start()] + treasures_render_js + html[m.start():]
        print("6. ✅ 渲染函数已添加")
    else:
        print("6. ⚠️ 未找到 switchView 插入点")
else:
    print("6. = 渲染函数已存在，跳过")

# ========== 7. 添加启动调用 + VIEWS 路由 ==========
# 在 DOMContentLoaded 中添加 v-treasures 启动
if 'renderTreasureRail()' not in html:
    init_pattern = r'(renderHerbRail\(\);)'
    m = re.search(init_pattern, html)
    if m:
        init_code = '\n  renderTreasureRail();\n  renderTreasureTabs();\n  applyTreasureFilter();\n  document.getElementById("treasureSearchInput").addEventListener("input",applyTreasureFilter);'
        html = html[:m.end()] + init_code + html[m.end():]
        print("7a. ✅ 启动调用已添加")
    else:
        print("7a. ⚠️ 未找到启动调用插入点")

# VIEWS 数组添加 v-treasures
if '"v-treasures"' not in html and "'v-treasures'" not in html:
    views_pattern = r'(VIEWS\s*=\s*\[[^\]]*"v-herbs"[^\]]*)\]'
    m = re.search(views_pattern, html)
    if m:
        html = html[:m.end(1)] + ',"v-treasures"]' + html[m.end():]
        print("7b. ✅ VIEWS 路由已添加")
    else:
        # 尝试另一种格式
        views_pattern2 = r'(VIEWS\s*=\s*\[[^\]]*v-herbs[^\]]*)\]'
        m2 = re.search(views_pattern2, html)
        if m2:
            html = html[:m2.end(1)] + ',"v-treasures"]' + html[m2.end():]
            print("7b. ✅ VIEWS 路由已添加（格式2）")
        else:
            print("7b. ⚠️ 未找到 VIEWS 数组")
else:
    print("7b. = VIEWS 路由已存在，跳过")

# ========== 8. 更新 asset-manifest ==========
# 收集所有 treasures 和 herbs_v2 的 img 文件名
all_new_imgs = []
# treasures 的 img
for m in re.finditer(r'img:"([^"]+\.jpg)"', treasures_js):
    all_new_imgs.append(m.group(1))
# herbs_v2 的 img
for m in re.finditer(r'img:"([^"]+\.jpg)"', herbs_v2_js):
    all_new_imgs.append(m.group(1))

# 去重
all_new_imgs = list(set(all_new_imgs))

manifest_pattern = re.compile(r'(\.asset-manifest\{display:none;background-image:)([^}]*)(;\})')
m = manifest_pattern.search(html)
if m:
    existing_urls = m.group(2)
    to_add = []
    for f in all_new_imgs:
        if f'assets/{f}' not in existing_urls:
            to_add.append(f)
    if to_add:
        new_urls = "".join([f'url("assets/{f}"),' for f in to_add])
        html = html[:m.end(2)] + new_urls + html[m.end(2):]
        print(f"8. ✅ asset-manifest 新增登记 {len(to_add)} 个文件")
    else:
        print("8. = asset-manifest 所有文件已登记")
else:
    print("8. ❌ asset-manifest 块未找到")

# ========== 9. 确认 footer 更新时间行 ==========
if '最后更新：2026-09-16' in html:
    print("9. ✅ footer 更新时间行保留完好")
else:
    print("9. ⚠️ footer 更新时间行未找到！")

io.open(P, "w", encoding="utf-8").write(html)
print("\n✅ index.html 已更新（v-treasures 第六视图构建完成）")
