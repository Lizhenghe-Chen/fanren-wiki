# -*- coding: utf-8 -*-
"""修复：将误插入 CSS 的 BEASTS 数据块移到 JS 正确位置。"""
import io, re

P = r"/Users/bunnychen/Documents/GitProjects/Lizhenghe-Chen.github.io/docs/docs/Other/fanren-characters/index.html"
s = io.open(P, encoding="utf-8").read()

# 1. 从 CSS 中提取误插入的数据块（从"灵兽灵虫数据"注释到 BEASTS 数组结束的 ];）
pat = re.compile(
    r'/\* ===== 灵兽灵虫数据：.*?\];\n\n/\* ===== 韩立境界时间轴 ===== \*/',
    re.S
)
m = pat.search(s)
if not m:
    print("ERROR: 未找到 CSS 中的误插入数据块")
    raise SystemExit(1)
data_block = m.group(0)
# 数据块 = 注释开头到 BEASTS 数组的 ];
end_marker = data_block.rfind("];") + 2
data_only = data_block[:end_marker]
print("提取数据块长度:", len(data_only))
# 校验数据块包含 BEASTS
assert "const BEASTS" in data_only, "数据块缺少 BEASTS"

# 2. 从 CSS 中删除数据块，恢复原注释
s = s[:m.start()] + "/* ===== 韩立境界时间轴 ===== */" + s[m.end():]
print("1. 已从 CSS 删除误插入数据块")

# 3. 将数据块插入 JS 正确位置（DATA.xianjie 结束的 ]; 之后、const TL 之前）
anchor_js = '];\n\n/* ===== 韩立境界时间轴 ===== */\nconst TL = ['
assert anchor_js in s, "JS 锚点未找到"
s = s.replace(anchor_js, "];\n\n" + data_only + "\n\n/* ===== 韩立境界时间轴 ===== */\nconst TL = [", 1)
print("2. 已插入 JS 正确位置")

io.open(P, "w", encoding="utf-8").write(s)
print("修复完成，已写回")
