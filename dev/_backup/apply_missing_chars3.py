# -*- coding: utf-8 -*-
"""补入苦竹老人（大晋篇，冰凤之后）+ 更新.asset-manifest。"""
import io

SRC = r"C:\Users\lizhe\OneDrive\我的工作文档\BunnyChen.github.io\docs\docs\Other\fanren-characters\index.html"
html = io.open(SRC, encoding="utf-8").read()

# 苦竹老人（大晋篇，放在冰凤之后、田不缺之前）
kuchu = '{n:"苦竹老人", t:"大晋海外苦竹岛岛主", r:"元婴中期巅峰（万木大阵内可接近元婴后期）", e:"与韩立斗法落败交出乌凤翎；后寿元耗尽坐化", s:"大晋海外苦竹岛岛主，元婴中期巅峰，豢养七级乌凤。苦竹岛设有万木大阵，以岛上天桑神树为阵眼，笼罩全岛，外人入岛实力遭大阵压制，苦竹老人在阵内战力可接近元婴后期。韩立为炼制三焰扇所需乌凤翎前往苦竹岛，提出以物换物被拒，遂约定斗法决定归属。苦竹老人施展剑阵攻击，被韩立新炼成的元婴后期傀儡轻松抵挡，金雷竹小箭尚未出手便直接认输，将乌凤翎交出。一生困于元婴中期巅峰，最终寿元耗尽遗憾坐化。", rel:"有交集的散修", camp:"苦竹岛·海外散修", race:"人族"},\n  '

anchor = 'ev:"元婴后期（压境不化神）→化神→炼虚→合体→大乘"},\n  {n:"田不缺"'
assert anchor in html, "冰凤->田不缺锚点未找到"
html = html.replace(anchor, 'ev:"元婴后期（压境不化神）→化神→炼虚→合体→大乘"},\n  ' + kuchu + '{n:"田不缺"', 1)
print("1. 苦竹老人补入完成（大晋篇）")

# 更新 .asset-manifest（添加 wansangu_luanxing.jpg）
manifest_anchor = 'url("assets/jinkui_luanxing.jpg"),'
assert manifest_anchor in html, "asset-manifest 金魁锚点未找到"
html = html.replace(manifest_anchor, manifest_anchor + '\n  url("assets/wansangu_luanxing.jpg"),', 1)
print("2. .asset-manifest 更新完成")

io.open(SRC, "w", encoding="utf-8").write(html)
print("\n全部完成")
