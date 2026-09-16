# -*- coding: utf-8 -*-
"""全量图片更新后的数据同步脚本：添加img字段 + 更新asset-manifest"""
import io, re

P = r"/Users/bunnychen/Documents/GitProjects/Lizhenghe-Chen.github.io/docs/docs/Other/fanren-characters/index.html"
html = io.open(P, encoding="utf-8").read()

# ========== 1. BEASTS 花石老祖添加img字段 ==========
old_huashi = '{n:"花石老祖", t:"合体期妖修 · 青阳城之主", cat:"yao", r:"合体期妖修", e:"背景设定角色", s:"灵界小灵界青阳城之主，合体期妖修，中年男子形象、青色鱼鳞甲。与韩立有交集，仅作背景设定。", rel:"散修妖修", camp:"小灵界·青阳城", race:"妖族"}'
new_huashi = '{n:"花石老祖", t:"合体期妖修 · 青阳城之主", cat:"yao", r:"合体期妖修", e:"背景设定角色", img:"huashilaozu.jpg", s:"灵界小灵界青阳城之主，合体期妖修，中年男子形象、青色鱼鳞甲。与韩立有交集，仅作背景设定。", rel:"散修妖修", camp:"小灵界·青阳城", race:"妖族"}'
if old_huashi in html:
    html = html.replace(old_huashi, new_huashi, 1)
    print("1. BEASTS 花石老祖 img 字段已添加")
else:
    print("1. ⚠️ 花石老祖条目未精确匹配，尝试模糊匹配...")
    # 模糊匹配：找到花石老祖条目，在e字段后插入img
    pattern = r'(\{n:"花石老祖"[^}]*e:"[^"]*")'
    m = re.search(pattern, html)
    if m:
        html = html[:m.end()] + ', img:"huashilaozu.jpg"' + html[m.end():]
        print("1. BEASTS 花石老祖 img 字段已添加（模糊匹配）")
    else:
        print("1. ❌ 花石老祖条目未找到")

# ========== 2. HERBS 27个条目添加img字段 ==========
herb_img_map = {
    # 灵草灵药
    "血灵草": "xuellincao.jpg",
    "寿元果": "shouyuanguo.jpg",
    "天元果": "tianyuanguo.jpg",
    "补天芝": "butianzhi.jpg",
    "赤精芝": "chijingzhi.jpg",
    "阴凝草": "yinningcao.jpg",
    "玄天仙藤": "xuanxantianteng.jpg",
    # 天材地宝
    "灵眼之泉": "lingyanzhiquan.jpg",
    "暖阳宝玉": "nuanyangbaoyu.jpg",
    "醇液": "chunye.jpg",
    "明清灵水": "mingqilingshui.jpg",
    "回阳真水": "huiyangzhenshui.jpg",
    # 突破丹药
    "九曲灵参丹": "jiuqulinshendan.jpg",
    "降尘丹": "jiangchendan.jpg",
    "长生丹": "changshengdan.jpg",
    "补天丹": "butiandan.jpg",
    "培婴丹": "peiyingdan.jpg",
    # 辅助丹药
    "黄龙丹·金髓丸": "huanglongdan.jpg",
    "雪魄丸": "xuepowan.jpg",
    "定颜丹": "dingyandan.jpg",
    "清灵散": "qinglingsan.jpg",
    "回煞丸": "huishawan.jpg",
    # 丹方·主材
    "筑基丹丹方（三大主药）": "zhujidan_fang.jpg",
    "造化丹丹方": "zaohuadan_fang.jpg",
    "九曲灵参丹丹方": "jiuqulinshendan_fang.jpg",
    "定灵丹丹方": "dinglingdan_fang.jpg",
    "回阳真水配方": "huiyangzhenshui_fang.jpg",
}

added = 0
for herb_name, img_file in herb_img_map.items():
    # 匹配 HERBS 中的条目：在 e:"..." 之后插入 img 字段
    # 模式：{n:"药名", ..., e:"结局", s:"..." 或 e:"结局"}
    # 更精确：找到 n:"药名" 的条目，在 e 字段值后插入 img
    pattern = r'(\{n:"' + re.escape(herb_name) + r'"[^}]*?e:"[^"]*")'
    m = re.search(pattern, html)
    if m:
        # 检查是否已有 img 字段
        entry_start = m.start()
        entry_end = html.find('}', entry_start)
        entry_text = html[entry_start:entry_end]
        if 'img:' not in entry_text:
            html = html[:m.end()] + ', img:"' + img_file + '"' + html[m.end():]
            added += 1
        else:
            print(f"  跳过（已有img）: {herb_name}")
    else:
        print(f"  ⚠️ 未找到条目: {herb_name}")

print(f"2. HERBS 添加了 {added}/27 个 img 字段")

# ========== 3. 更新 .asset-manifest ==========
# 找到 manifest 块，在最后追加28个新文件
new_manifest_files = [
    "huashilaozu.jpg",
    "xuellincao.jpg", "shouyuanguo.jpg", "tianyuanguo.jpg", "butianzhi.jpg",
    "chijingzhi.jpg", "yinningcao.jpg", "xuanxantianteng.jpg",
    "lingyanzhiquan.jpg", "nuanyangbaoyu.jpg", "chunye.jpg", "mingqilingshui.jpg", "huiyangzhenshui.jpg",
    "jiuqulinshendan.jpg", "jiangchendan.jpg", "changshengdan.jpg", "butiandan.jpg", "peiyingdan.jpg",
    "huanglongdan.jpg", "xuepowan.jpg", "dingyandan.jpg", "qinglingsan.jpg", "huishawan.jpg",
    "zhujidan_fang.jpg", "zaohuadan_fang.jpg", "jiuqulinshendan_fang.jpg", "dinglingdan_fang.jpg", "huiyangzhenshui_fang.jpg",
]

# 找到 manifest 中最后一个 url() 行，在 ;} 之前插入
# manifest 格式：.asset-manifest{display:none;background-image:url("assets/a.jpg"),url("assets/b.jpg"),...;}
manifest_pattern = re.compile(r'(\.asset-manifest\{display:none;background-image:)([^}]*)(;\})')
m = manifest_pattern.search(html)
if m:
    existing_urls = m.group(2)
    # 检查哪些文件已登记
    to_add = []
    for f in new_manifest_files:
        if f'assets/{f}' not in existing_urls:
            to_add.append(f)
    if to_add:
        new_urls = "".join([f'url("assets/{f}"),' for f in to_add])
        html = html[:m.end(2)] + new_urls + html[m.end(2):]
        print(f"3. asset-manifest 新增登记 {len(to_add)} 个文件")
    else:
        print("3. asset-manifest 所有文件已登记，无需新增")
else:
    print("3. ❌ asset-manifest 块未找到")

# ========== 4. 确认 footer "最后更新" 行存在 ==========
if '最后更新：2026-09-16' in html:
    print("4. ✅ footer '最后更新：2026-09-16' 行保留完好")
else:
    print("4. ⚠️ footer '最后更新' 行未找到！")

io.open(P, "w", encoding="utf-8").write(html)
print("\n✅ index.html 已更新（img字段 + asset-manifest）")
