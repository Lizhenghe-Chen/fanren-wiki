# -*- coding: utf-8 -*-
"""修复 v-treasures 数据位置：删除CSS区域错误插入的数据，正确插入到JS区域"""
import io, re

P = r"/Users/bunnychen/Documents/GitProjects/Lizhenghe-Chen.github.io/docs/docs/Other/fanren-characters/index.html"
TREASURES_DATA = r"/Users/bunnychen/Documents/GitProjects/Lizhenghe-Chen.github.io/docs/docs/Other/fanren-characters/_backup/treasures_data.js"

html = io.open(P, encoding="utf-8").read()
treasures_js = io.open(TREASURES_DATA, encoding="utf-8").read()

# ========== 1. 删除CSS区域中错误插入的TREASURE数据 ==========
# CSS区域的错误数据从 const TREASURE_CATS = [ 开始，到 ]; 结束（在 .timeline-sec 之前）
# 精确匹配：从 line 94 的 const TREASURE_CATS 到 line 190 的 ];
css_error_pattern = r'\nconst TREASURE_CATS = \[.*?\];\n\nconst TREASURE_RAIL = \[.*?\];\n\nconst TREASURES = \[.*?\];\n\n\n\n'
m = re.search(css_error_pattern, html, re.DOTALL)
if m:
    html = html[:m.start()] + '\n' + html[m.end():]
    print("1. ✅ 已删除CSS区域错误插入的TREASURE数据")
else:
    print("1. ⚠️ 未找到CSS区域错误数据，尝试其他模式...")
    # 尝试更宽松的匹配
    css_error_pattern2 = r'\nconst TREASURE_CATS = \[.*?const TREASURES = \[.*?\];\n'
    m2 = re.search(css_error_pattern2, html, re.DOTALL)
    if m2:
        # 找到结束位置（]; 后面的空行）
        end_pos = m2.end()
        # 跳过后面的空行
        while end_pos < len(html) and html[end_pos] in '\n':
            end_pos += 1
        html = html[:m2.start()] + '\n' + html[end_pos:]
        print("1. ✅ 已删除CSS区域错误插入的TREASURE数据（模式2）")
    else:
        print("1. ❌ 未找到CSS区域错误数据")

# ========== 2. 将TREASURE数据正确插入到JS区域 ==========
cats_match = re.search(r'(const TREASURE_CATS = \[.*?\];)', treasures_js, re.DOTALL)
rail_match = re.search(r'(const TREASURE_RAIL = \[.*?\];)', treasures_js, re.DOTALL)
treasures_match = re.search(r'(const TREASURES = \[.*?\];)', treasures_js, re.DOTALL)

if cats_match and rail_match and treasures_match:
    js_data = '\n\n' + cats_match.group(1) + '\n\n' + rail_match.group(1) + '\n\n' + treasures_match.group(1) + '\n'
    
    # 检查是否已经在JS区域存在
    if 'const TREASURE_CATS' not in html:
        # JS区域的锚点：在 v2 补充之后、JS区域的韩立境界时间轴之前
        # JS区域的韩立境界时间轴在 line 1254 左右，前面是 HERBS 数组的 ];
        # 精确匹配：v2 补充的最后一个元素（魔髓钻）之后的 ]; 然后是 JS区域的韩立境界时间轴
        js_anchor = r'\];\n\n/\* ===== 韩立境界时间轴 ===== \*/\nconst TL = \['
        m = re.search(js_anchor, html)
        if m:
            html = html[:m.start()] + js_data + html[m.start():]
            print("2. ✅ TREASURE数据已正确插入到JS区域")
        else:
            print("2. ❌ 未找到JS区域插入锚点")
    else:
        print("2. = TREASURE数据已在JS区域存在，跳过")
else:
    print("2. ❌ 数据提取失败")

# ========== 3. 确认 footer 更新时间行 ==========
if '最后更新：2026-09-16' in html:
    print("3. ✅ footer 更新时间行保留完好")
else:
    print("3. ⚠️ footer 更新时间行未找到！")

io.open(P, "w", encoding="utf-8").write(html)
print("\n✅ index.html 数据位置修复完成")
