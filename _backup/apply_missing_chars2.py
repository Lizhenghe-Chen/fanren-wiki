# -*- coding: utf-8 -*-
"""补入第二轮遗漏角色：万三姑（乱星海）、易洗天/碧月禅师/苦竹老人（大晋）。"""
import io

SRC = r"C:\Users\lizhe\OneDrive\我的工作文档\BunnyChen.github.io\docs\docs\Other\fanren-characters\index.html"
html = io.open(SRC, encoding="utf-8").read()

# ========== 1. 万三姑（乱星海篇，放在万天明之前） ==========
wansangu = '{n:"万三姑", t:"万法门总护法 · 逆星盟正道领袖", r:"元婴后期", e:"天星双圣潜入逆星盟总部自爆，当场被炸死；尸体被六道极圣捡回制成炼尸傀儡", img:"wansangu_luanxing.jpg", s:"万法门总护法、乱星海正道第一人，元婴后期大修士，性格冲动暴躁，人称"疯婆子"。与魔道魁首六道极圣齐名，联手整合正魔两道创立逆星盟，企图推翻星宫统治。法宝众多、神通广大，曾单挑星宫八大长老。天星双圣寿元将近时潜入逆星盟总部自爆，万三姑当场殒命，死后尸体被六道极圣制成炼尸傀儡，是乱星海结局最憋屈的元婴后期。", rel:"逆星盟领袖", camp:"万法门·逆星盟", race:"人族"},\n  '
anchor_wantianming = '{n:"万天明"'
assert anchor_wantianming in html, "万天明条目未找到"
html = html.replace(anchor_wantianming, wansangu + anchor_wantianming, 1)
print("1. 万三姑补入完成（乱星海篇）")

# ========== 2. 易洗天（大晋篇，放在白老鬼之后） ==========
yixitian = '{n:"易洗天", t:"大晋四大散修之首", r:"元婴后期巅峰（最有希望进阶化神）", e:"原著未正式登场，被九幽宗富成提起；终生潜修积攒底蕴，等待冲击化神的契机，结局未明", s:"大晋四大散修之首，元婴后期巅峰，与佛门碧月禅师并称大晋千年来最有希望进阶化神期的两人。实力极强，与向之礼、风老怪等化神修士并称却始终停留在元婴后期，并非实力不足，而是时机与机缘未到。不急于一时，在大晋深处潜修，一边探寻秘境遗宝，一边研究化神瓶颈，默默积攒底蕴等待冲击化神的契机。原著中未正式登场，仅被九幽宗元婴修士富成提起。", rel:"散修名宿", camp:"大晋散修", race:"人族"},\n  '
anchor_baigui_end = 'race:"人族"},\n  {n:"大衍神君"'
# 白老鬼条目以 race:"人族"}, 结束，后面是大衍神君
assert anchor_baigui_end in html, "白老鬼->大衍神君锚点未找到"
html = html.replace(anchor_baigui_end, 'race:"人族"},\n  ' + yixitian + '{n:"大衍神君"', 1)
print("2. 易洗天补入完成（大晋篇）")

# ========== 3. 碧月禅师（大晋篇，放在易洗天之后） ==========
biyue = '{n:"碧月禅师", t:"佛门净火宗长老 · 万年天纵之才", r:"元婴后期顶尖（最有希望进阶化神）", e:"四百余年进阶元婴后期，修仙界公认万年一出的天纵之才；与易洗天并称大晋最有希望化神的两人，结局未明（疑似冲击化神失败或坐化）", s:"佛门净火宗（净宗）长老，元婴后期顶尖，修仙界万年一出的天纵之才，仅花费四百余年便进阶元婴后期（常人苦修千年堪堪摸到元婴门槛）。作为佛门极为稀少的护法金刚，一身银袍僧人形象，三十许岁模样，十分儒雅，持有万年火珊瑚炼制的法宝。修行速度与战斗技巧在大晋元婴后期修士中名列前茅，是正道除太一门外的重要战力。与易洗天并称大晋千年来最有希望进阶化神期的两人。", rel:"佛门名宿", camp:"净火宗·佛门", race:"人族"},\n  '
anchor_yixitian_end = 'race:"人族"},\n  {n:"大衍神君"'
# 现在易洗天后面直接是大衍神君，把碧月禅师插在中间
assert anchor_yixitian_end in html, "易洗天->大衍神君锚点未找到"
html = html.replace(anchor_yixitian_end, 'race:"人族"},\n  ' + biyue + '{n:"大衍神君"', 1)
print("3. 碧月禅师补入完成（大晋篇）")

# ========== 4. 苦竹老人（大晋篇，放在冰凤之后） ==========
kuchu = '{n:"苦竹老人", t:"大晋海外苦竹岛岛主", r:"元婴中期巅峰（万木大阵内可接近元婴后期）", e:"与韩立斗法落败交出乌凤翎；后寿元耗尽坐化", s:"大晋海外苦竹岛岛主，元婴中期巅峰，豢养七级乌凤。苦竹岛设有万木大阵，以岛上天桑神树为阵眼，笼罩全岛，外人入岛实力遭大阵压制，苦竹老人在阵内战力可接近元婴后期。韩立为炼制三焰扇所需乌凤翎前往苦竹岛，提出以物换物被拒，遂约定斗法决定归属。苦竹老人施展剑阵攻击，被韩立新炼成的元婴后期傀儡轻松抵挡，金雷竹小箭尚未出手便直接认输，将乌凤翎交出。一生困于元婴中期巅峰，最终寿元耗尽遗憾坐化。", rel:"有交集的散修", camp:"苦竹岛·海外散修", race:"人族"},\n  '
anchor_bingfeng_end = 'race:"妖族·冰凤"},\n  {n:"田不缺"'
assert anchor_bingfeng_end in html, "冰凤->田不缺锚点未找到"
html = html.replace(anchor_bingfeng_end, 'race:"妖族·冰凤"},\n  ' + kuchu + '{n:"田不缺"', 1)
print("4. 苦竹老人补入完成（大晋篇）")

# ========== 5. 更新 .asset-manifest（添加 wansangu_luanxing.jpg） ==========
manifest_anchor = 'url("assets/jinkui_luanxing.jpg"),'
assert manifest_anchor in html, "asset-manifest 金魁锚点未找到"
html = html.replace(manifest_anchor, manifest_anchor + '\n  url("assets/wansangu_luanxing.jpg"),', 1)
print("5. .asset-manifest 更新完成")

io.open(SRC, "w", encoding="utf-8").write(html)
print("\n全部修改完成，已写回 index.html")
