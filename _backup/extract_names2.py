# -*- coding: utf-8 -*-
"""提取 DATA 中所有角色名（逐键赋值格式）。"""
import io, re

SRC = r"C:\Users\lizhe\OneDrive\我的工作文档\BunnyChen.github.io\docs\docs\Other\fanren-characters\index.html"
html = io.open(SRC, encoding="utf-8").read()

chapters = {}
# 匹配 DATA.xxx = [ ... ];  （非贪婪，到下一个 DATA. 或 const 或文件尾）
for m in re.finditer(r'DATA\.(\w+)\s*=\s*\[(.*?)\]\s*;', html, re.DOTALL):
    ch_id = m.group(1)
    block = m.group(2)
    names = re.findall(r'n\s*:\s*"([^"]+)"', block)
    chapters[ch_id] = names

print("=== 各篇章角色数 ===")
total = 0
for ch, names in chapters.items():
    print(f"{ch}: {len(names)} 人")
    total += len(names)
print(f"合计: {total} 人")

print("\n=== 关键遗漏检查 ===")
checks = ["金魁", "白老鬼", "海大少", "白果儿", "花石老祖", "冰魄仙子", "敖啸", "乾老魔", "温夫人", "天悟子", "天星双圣", "凌啸风", "温青", "蛮胡子", "万天明", "六道极圣", "极阴祖师", "乌丑", "玄骨", "风老怪", "呼庆雷", "车老妖", "向之礼", "青元子", "莫简离", "器灵子"]
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
