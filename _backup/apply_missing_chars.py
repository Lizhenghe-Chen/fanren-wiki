# -*- coding: utf-8 -*-
"""补入遗漏角色：金魁（乱星海）、花石老祖（灵界）；更正白道友->白老鬼并丰富生平；更新.asset-manifest。"""
import io, re

SRC = r"C:\Users\lizhe\OneDrive\我的工作文档\BunnyChen.github.io\docs\docs\Other\fanren-characters\index.html"
html = io.open(SRC, encoding="utf-8").read()

# ========== 1. 更正：白道友 -> 白老鬼（丰富生平） ==========
old_bai = '{n:"白道友", t:"太一门主", r:"化神", e:"未随飞升，坐化于下界", img:"baiyoudao.jpg", s:"太一门主、化神修士，未随飞升，坐化于下界。", rel:"前辈", camp:"太一门", race:"人族"},'
new_bai = '{n:"白老鬼", t:"太一门老祖（人称白道友）", r:"化神初期 → 吞火精枣短暂突破化神中期", e:"拒绝偷渡灵界，生服火精枣强行突破，因人界灵气匮乏无法飞升，灵力燃尽坐化于人界", img:"baiyoudao.jpg", s:"太一门老祖、化神初期，大晋正道第一宗门太一门的支柱。与向之礼、呼庆雷、风老怪交好，但不看好偷渡灵界，选择以正统方式突破。为破化神瓶颈生服天地奇物火精枣，强行点燃一身法力，短暂踏入化神中期，却因人界灵气枯竭无法再进，最终灵力燃尽坐化。", rel:"前辈", camp:"太一门", race:"人族"},'
assert old_bai in html, "白道友条目未找到"
html = html.replace(old_bai, new_bai, 1)
print("1. 白老鬼更正完成")

# ========== 2. 补入：金魁（乱星海篇，放在星宫双圣之前） ==========
jinkui = '{n:"金魁", t:"星宫大长老（六大长老之首）", r:"元婴中期巅峰（冲击元婴后期失败）", e:"与韩立结怨，虚天殿后被韩立斩杀", img:"jinkui_luanxing.jpg", s:"星宫大长老、六大长老之首，地位仅次于天星双圣，双圣闭关时全权执掌星宫军政。修为元婴中期巅峰，肉身与神通双强，修炼星宫镇派功法天星诀，实力稳压同阶蛮胡子、万天明一头。首次出场便独闯极阴岛，以绝对压制震慑极阴老祖。给紫灵虚天残图，在虚天殿搅弄风云、算计正魔两道，后与韩立结怨，最终被韩立斩杀。注：动漫原创强化角色，原著中星宫大长老存在感较弱。", rel:"仇敌", camp:"星宫", race:"人族"},\n  '
# 插入到星宫双圣之前
anchor_xinggong = '{n:"星宫双圣"'
assert anchor_xinggong in html, "星宫双圣条目未找到"
html = html.replace(anchor_xinggong, jinkui + anchor_xinggong, 1)
print("2. 金魁补入完成（乱星海篇）")

# ========== 3. 补入：花石老祖（灵界篇，放在器灵子之前） ==========
huashi = '{n:"花石老祖", t:"蛮荒水域妖修 · 韩立半个弟子", r:"合体初期 → 合体中期（韩立指点丹药）", e:"随韩立入青元宫，以弟子身份侍奉，结局未明（预计修至合体后期）", s:"蛮荒世界水属性妖修，占据万余里水域，合体初期称霸一方。韩立寻找小灵天入口时将其强行征召带路，被韩立实力折服，主动自称半个弟子、口称韩师，随韩立离开蛮荒。韩立赐下高阶丹药并点拨修炼瓶颈，短短大半年便突破至合体中期。忠心耿耿，为韩立处理水域事务、送宝物给冰凤等，后入青元宫，是韩立非正式弟子中最忠心的一位。", rel:"半个弟子", camp:"青元宫", race:"妖族·水属性"},\n  '
anchor_qilingzi = '{n:"器灵子"'
assert anchor_qilingzi in html, "器灵子条目未找到"
html = html.replace(anchor_qilingzi, huashi + anchor_qilingzi, 1)
print("3. 花石老祖补入完成（灵界篇）")

# ========== 4. 更新 .asset-manifest（添加 jinkui_luanxing.jpg） ==========
# 找到 .asset-manifest 的 background-image 行，在末尾追加
manifest_anchor = 'url("assets/zhonglingdao_huangfeng.jpg"),'
# 在最后一个 url 后面追加（zhonglingdao 是最后一个新增图，在它后面加）
assert manifest_anchor in html, "asset-manifest 末尾锚点未找到"
html = html.replace(manifest_anchor, manifest_anchor + '\n  url("assets/jinkui_luanxing.jpg"),', 1)
print("4. .asset-manifest 更新完成")

io.open(SRC, "w", encoding="utf-8").write(html)
print("\n全部修改完成，已写回 index.html")
