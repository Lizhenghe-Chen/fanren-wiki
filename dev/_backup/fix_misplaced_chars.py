# -*- coding: utf-8 -*-
"""修复：将易洗天/碧月禅师从乱星海篇移到大晋篇白老鬼之后。"""
import io, re

SRC = r"C:\Users\lizhe\OneDrive\我的工作文档\BunnyChen.github.io\docs\docs\Other\fanren-characters\index.html"
html = io.open(SRC, encoding="utf-8").read()

# 1. 从乱星海篇删除易洗天和碧月禅师（它们在青易居士之后、乱星海大衍神君之前）
# 乱星海大衍神君的 t 字段是 "千竹教始祖 · 大衍诀创造者"
pattern_luanxing = re.compile(
    r'  \{n:"易洗天".*?\},\n  \{n:"碧月禅师".*?\},\n  \{n:"大衍神君", t:"千竹教始祖 · 大衍诀创造者"',
    re.DOTALL
)
match = pattern_luanxing.search(html)
if match:
    html = html[:match.start()] + '  {n:"大衍神君", t:"千竹教始祖 · 大衍诀创造者"' + html[match.end():]
    print("1. 已从乱星海篇删除易洗天和碧月禅师")
else:
    print("1. 乱星海篇未找到易洗天/碧月禅师（可能已删除）")

# 2. 在大晋篇白老鬼之后插入易洗天和碧月禅师
# 大晋篇大衍神君的 img 是 "dayan_dajin.jpg"
yixitian = '{n:"易洗天", t:"大晋四大散修之首", r:"元婴后期巅峰（最有希望进阶化神）", e:"原著未正式登场，被九幽宗富成提起；终生潜修积攒底蕴，等待冲击化神的契机，结局未明", s:"大晋四大散修之首，元婴后期巅峰，与佛门碧月禅师并称大晋千年来最有希望进阶化神期的两人。实力极强，与向之礼、风老怪等化神修士并称却始终停留在元婴后期，并非实力不足，而是时机与机缘未到。不急于一时，在大晋深处潜修，一边探寻秘境遗宝，一边研究化神瓶颈，默默积攒底蕴等待冲击化神的契机。原著中未正式登场，仅被九幽宗元婴修士富成提起。", rel:"散修名宿", camp:"大晋散修", race:"人族"},\n  '
biyue = '{n:"碧月禅师", t:"佛门净火宗长老 · 万年天纵之才", r:"元婴后期顶尖（最有希望进阶化神）", e:"四百余年进阶元婴后期，修仙界公认万年一出的天纵之才；与易洗天并称大晋最有希望化神的两人，结局未明（疑似冲击化神失败或坐化）", s:"佛门净火宗（净宗）长老，元婴后期顶尖，修仙界万年一出的天纵之才，仅花费四百余年便进阶元婴后期（常人苦修千年堪堪摸到元婴门槛）。作为佛门极为稀少的护法金刚，一身银袍僧人形象，三十许岁模样，十分儒雅，持有万年火珊瑚炼制的法宝。修行速度与战斗技巧在大晋元婴后期修士中名列前茅，是正道除太一门外的重要战力。与易洗天并称大晋千年来最有希望进阶化神期的两人。", rel:"佛门名宿", camp:"净火宗·佛门", race:"人族"},\n  '

anchor_dajin = 'race:"人族"},\n  {n:"大衍神君", t:"千竹教始祖", r:"化神（附身傀儡）", e:"韩立炼成元后傀儡后，安然坐化", img:"dayan_dajin.jpg"'
if anchor_dajin in html and 'n:"易洗天"' not in html.split('dayan_dajin')[0].split('白老鬼')[-1]:
    html = html.replace(anchor_dajin, 'race:"人族"},\n  ' + yixitian + biyue + '{n:"大衍神君", t:"千竹教始祖", r:"化神（附身傀儡）", e:"韩立炼成元后傀儡后，安然坐化", img:"dayan_dajin.jpg"', 1)
    print("2. 已在大晋篇白老鬼之后插入易洗天和碧月禅师")
else:
    print("2. 大晋篇锚点未找到或已存在")

io.open(SRC, "w", encoding="utf-8").write(html)
print("\n修复完成")
