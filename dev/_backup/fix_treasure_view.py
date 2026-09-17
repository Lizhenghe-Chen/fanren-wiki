# -*- coding: utf-8 -*-
"""修复 v-treasures 构建：补全 HERBS 补充数据、TREASURES 数据、渲染函数、VIEWS 路由"""
import io, re

P = r"/Users/bunnychen/Documents/GitProjects/Lizhenghe-Chen.github.io/docs/docs/Other/fanren-characters/index.html"
TREASURES_DATA = r"/Users/bunnychen/Documents/GitProjects/Lizhenghe-Chen.github.io/docs/docs/Other/fanren-characters/_backup/treasures_data.js"
HERBS_V2 = r"/Users/bunnychen/Documents/GitProjects/Lizhenghe-Chen.github.io/docs/docs/Other/fanren-characters/_backup/herbs_data_v2.js"

html = io.open(P, encoding="utf-8").read()
treasures_js = io.open(TREASURES_DATA, encoding="utf-8").read()
herbs_v2_js = io.open(HERBS_V2, encoding="utf-8").read()

# ========== 1. 将 herbs_data_v2.js 的14条追加到 HERBS 数组 ==========
v2_match = re.search(r'const HERBS_V2_SUPPLEMENT = \[(.*?)\];', herbs_v2_js, re.DOTALL)
if v2_match:
    v2_elements = v2_match.group(1).strip()
    # HERBS 数组在 const HERB_RAIL 之前结束，格式为 ];\n\n\n/* ===== 韩立境界时间轴
    # 找到 HERBS 数组的最后一个元素（回阳真水配方）之后的 ];
    herbs_end = html.find('];\n\n\n/* ===== 韩立境界时间轴 ===== */')
    if herbs_end > 0:
        insert_text = '\n  /* ===== v2 补充（复查新增） ===== */\n' + v2_elements + '\n'
        html = html[:herbs_end] + insert_text + html[herbs_end:]
        print("1. ✅ HERBS 数组追加14条补充数据")
    else:
        print("1. ❌ 未找到 HERBS 数组结束位置")
else:
    print("1. ❌ 未找到 HERBS_V2_SUPPLEMENT 数组")

# ========== 2. 添加 TREASURE_CATS/TREASURE_RAIL/TREASURES 数据 ==========
cats_match = re.search(r'(const TREASURE_CATS = \[.*?\];)', treasures_js, re.DOTALL)
rail_match = re.search(r'(const TREASURE_RAIL = \[.*?\];)', treasures_js, re.DOTALL)
treasures_match = re.search(r'(const TREASURES = \[.*?\];)', treasures_js, re.DOTALL)

if cats_match and rail_match and treasures_match:
    js_data = '\n\n' + cats_match.group(1) + '\n\n' + rail_match.group(1) + '\n\n' + treasures_match.group(1) + '\n'
    
    # 检查是否已经添加过
    if 'const TREASURE_CATS' not in html:
        # 插入到 HERBS 数组之后、韩立境界时间轴之前
        anchor = '\n\n\n/* ===== 韩立境界时间轴 ===== */'
        if anchor in html:
            html = html.replace(anchor, js_data + anchor, 1)
            print("2. ✅ TREASURE_CATS/TREASURE_RAIL/TREASURES 数据已添加")
        else:
            print("2. ❌ 未找到数据插入锚点")
    else:
        print("2. = 数据已存在，跳过")
else:
    print("2. ❌ 数据提取失败")

# ========== 3. 添加渲染函数 ==========
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

if 'function renderTreasureRail' not in html:
    # 在 switchView 函数之前插入（注意有缩进）
    switchview_pattern = r'(\n  function switchView\(id\)\{)'
    m = re.search(switchview_pattern, html)
    if m:
        html = html[:m.start()] + treasures_render_js + html[m.start():]
        print("3. ✅ 渲染函数已添加")
    else:
        print("3. ❌ 未找到 switchView 插入点")
else:
    print("3. = 渲染函数已存在，跳过")

# ========== 4. VIEWS 数组添加 v-treasures ==========
views_pattern = r'var VIEWS = \["v-chars","v-lore","v-realms","v-beasts","v-herbs"\];'
m = re.search(views_pattern, html)
if m:
    html = html.replace(views_pattern, 'var VIEWS = ["v-chars","v-lore","v-realms","v-beasts","v-herbs","v-treasures"];', 1)
    print("4. ✅ VIEWS 路由已添加 v-treasures")
else:
    # 检查是否已经包含
    if '"v-treasures"' in html or "'v-treasures'" in html:
        print("4. = VIEWS 已包含 v-treasures")
    else:
        print("4. ⚠️ 未找到 VIEWS 数组")

# ========== 5. 确认 footer 更新时间行 ==========
if '最后更新：2026-09-16' in html:
    print("5. ✅ footer 更新时间行保留完好")
else:
    print("5. ⚠️ footer 更新时间行未找到！")

io.open(P, "w", encoding="utf-8").write(html)
print("\n✅ index.html 修复完成")
