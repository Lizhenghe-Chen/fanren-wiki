# -*- coding: utf-8 -*-
"""第二轮补图后的数据同步：给19个灵界仙界角色加img字段 + 更新asset-manifest"""
import io, re

P = r"/Users/bunnychen/Documents/GitProjects/Lizhenghe-Chen.github.io/docs/docs/Other/fanren-characters/index.html"
html = io.open(P, encoding="utf-8").read()

# ========== 1. 给19个灵界仙界角色加img字段 ==========
# 映射：角色名关键词 → 图片文件名
herb_img_map = [
    ("天妙灵皇", "tianmiaolinghuang.jpg"),
    ("六极", "liuji.jpg"),
    ("血光", "xueguang.jpg"),
    ("毒龙", "dulong.jpg"),
    ("胡俊", "hujun.jpg"),
    ("黛儿", "daier.jpg"),
    ("器灵子", "qilingzi.jpg"),
    ("方夫人", "fangfuren.jpg"),
    ("张奎", "zhangkui.jpg"),
    ("隐明", "yinming.jpg"),
    ("火炽子", "huohuozi.jpg"),
    ("封天都", "fengtiandu.jpg"),
    ("高升", "gaosheng.jpg"),
    ("沙心", "shaxin.jpg"),
    ("厄脍", "ekuai.jpg"),
    ("柳岐", "liuqi.jpg"),
    ("柳三省", "liusansheng.jpg"),
    ("厉飞羽", "lifeiyu_xianjie.jpg"),
    ("韩立之女", "hanling.jpg"),
]

added = 0
for keyword, img_file in herb_img_map:
    # 匹配 n:"包含关键词的角色名" 的条目，在 e:"..." 后插入 img
    # 使用非贪婪匹配找到该条目的 e 字段
    pattern = r'(\{n:"[^"]*' + re.escape(keyword) + r'[^"]*"[^}]*?e:"[^"]*")'
    m = re.search(pattern, html)
    if m:
        # 检查该条目是否已有 img 字段
        entry_start = m.start()
        entry_end = html.find('}', entry_start)
        entry_text = html[entry_start:entry_end]
        if 'img:' not in entry_text:
            html = html[:m.end()] + ', img:"' + img_file + '"' + html[m.end():]
            added += 1
            print(f"  + {keyword} → {img_file}")
        else:
            print(f"  = {keyword} 已有img字段，跳过")
    else:
        print(f"  ? {keyword} 未找到条目")

print(f"\n1. 共添加 {added}/19 个 img 字段")

# ========== 2. 确认花石老祖img字段 ==========
if 'n:"花石老祖"' in html and 'img:"huashilaozu.jpg"' in html:
    print("2. ✅ 花石老祖 img 字段已存在")
else:
    print("2. ⚠️ 花石老祖 img 字段缺失，尝试添加...")
    pattern = r'(\{n:"花石老祖"[^}]*?e:"[^"]*")'
    m = re.search(pattern, html)
    if m:
        html = html[:m.end()] + ', img:"huashilaozu.jpg"' + html[m.end():]
        print("2. ✅ 花石老祖 img 字段已添加")

# ========== 3. 更新 .asset-manifest ==========
new_files = [
    "tianmiaolinghuang.jpg", "liuji.jpg", "xueguang.jpg", "dulong.jpg",
    "hujun.jpg", "daier.jpg", "qilingzi.jpg", "fangfuren.jpg", "zhangkui.jpg",
    "yinming.jpg", "huohuozi.jpg", "fengtiandu.jpg", "gaosheng.jpg", "shaxin.jpg",
    "ekuai.jpg", "liuqi.jpg", "liusansheng.jpg", "lifeiyu_xianjie.jpg", "hanling.jpg",
]

manifest_pattern = re.compile(r'(\.asset-manifest\{display:none;background-image:)([^}]*)(;\})')
m = manifest_pattern.search(html)
if m:
    existing_urls = m.group(2)
    to_add = []
    for f in new_files:
        if f'assets/{f}' not in existing_urls:
            to_add.append(f)
    if to_add:
        new_urls = "".join([f'url("assets/{f}"),' for f in to_add])
        html = html[:m.end(2)] + new_urls + html[m.end(2):]
        print(f"3. asset-manifest 新增登记 {len(to_add)} 个文件")
    else:
        print("3. asset-manifest 所有文件已登记")
else:
    print("3. ❌ asset-manifest 块未找到")

# ========== 4. 确认footer更新时间行 ==========
if '最后更新：2026-09-16' in html:
    print("4. ✅ footer '最后更新：2026-09-16' 行保留完好")
else:
    print("4. ⚠️ footer 更新时间行未找到！")

io.open(P, "w", encoding="utf-8").write(html)
print("\n✅ index.html 已更新")
