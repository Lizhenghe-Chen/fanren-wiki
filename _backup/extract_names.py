# -*- coding: utf-8 -*-
"""提取 index.html 中 DATA 的所有角色名，按篇章分组，并检查关键遗漏角色。"""
import io, re, json

SRC = r"C:\Users\lizhe\OneDrive\我的工作文档\BunnyChen.github.io\docs\docs\Other\fanren-characters\index.html"
html = io.open(SRC, encoding="utf-8").read()

# 定位 const DATA = { ... };
m = re.search(r'const DATA\s*=\s*\{(.*?)\n\};', html, re.DOTALL)
if not m:
    print("未找到 DATA")
    raise SystemExit(1)
data_str = m.group(1)

# 按篇章键切分
chapters = {}
# 匹配 qixuanmen: [ ... ],  huangfeng: [ ... ], 等
for cm in re.finditer(r'(\w+)\s*:\s*\[(.*?)\](?=\s*,?\s*\w+\s*:|\s*$)', data_str, re.DOTALL):
    ch_id = cm.group(1)
    block = cm.group(2)
    # 提取每个对象的 n 字段
    names = re.findall(r'n\s*:\s*["\']([^"\']+)["\']', block)
    chapters[ch_id] = names

print("=== 各篇章角色数 ===")
total = 0
for ch, names in chapters.items():
    print(f"{ch}: {len(names)} 人")
    total += len(names)
print(f"合计: {total} 人")

print("\n=== 关键遗漏检查 ===")
checks = ["金魁", "白老鬼", "海大少", "白果儿", "花石老祖", "冰魄仙子", "敖啸", "乾老魔", "温夫人", "天悟子"]
all_names = set()
for names in chapters.values():
    all_names.update(names)
for name in checks:
    found = name in all_names
    print(f"  {name}: {'已收录' if found else '【缺失】'}")

print("\n=== 各篇章完整角色列表 ===")
for ch, names in chapters.items():
    print(f"\n[{ch}] ({len(names)}人):")
    print("  " + "、".join(names))
