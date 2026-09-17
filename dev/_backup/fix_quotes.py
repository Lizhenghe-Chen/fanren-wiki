# -*- coding: utf-8 -*-
"""修复万三姑 s 字段中的英文引号问题。"""
import io

SRC = r"C:\Users\lizhe\OneDrive\我的工作文档\BunnyChen.github.io\docs\docs\Other\fanren-characters\index.html"
html = io.open(SRC, encoding="utf-8").read()

# 找到万三姑的 s 字段，检查引号类型
idx = html.find('n:"万三姑"')
segment = html[idx:idx+800]
print("当前片段（前300字符）:")
print(repr(segment[:300]))

# 替换 s 字段中的英文引号 "疯婆子" 为中文引号
# 精确匹配：人称"疯婆子"。  这里的 " 是英文引号 U+0022
old = '人称"疯婆子"。'
new = '人称\u201c疯婆子\u201d。'
if old in html:
    html = html.replace(old, new, 1)
    print("\n已替换英文引号为中文引号")
else:
    print("\n未找到英文引号，可能已经是中文引号")
    # 检查是否是中文引号
    if '人称\u201c疯婆子\u201d。' in html:
        print("确认已是中文引号")

io.open(SRC, "w", encoding="utf-8").write(html)
print("已写回")
