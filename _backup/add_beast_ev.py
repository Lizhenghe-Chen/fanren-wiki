# -*- coding: utf-8 -*-
"""为 BEASTS 缺 ev 的条目补写等级演进"""
import io, re

PATH = '/Users/bunnychen/Documents/GitProjects/Lizhenghe-Chen.github.io/docs/docs/Other/fanren-characters/index.html'
s = io.open(PATH, encoding='utf-8').read()

BEV = {
  '血玉蜘蛛': '虫卵→四级顶峰→七级（一雌一雄方可进阶）',
  '六翼霜蜈': '幼虫→四级（四翼）→七级→大乘（成熟六翼真灵）',
  '云翅鸟': '三级灵禽（云翅代步）',
  '金背妖螂': '妖虫五级（≈结丹初期）',
  '双瞳鼠': '一级中阶（≈炼气期）',
  '土甲龙': '七级灵兽（≈结丹后期）',
  '豹鳞兽': '真灵级（变异风遁，速度型）',
  '圭灵': '十级妖修（≈元婴后期）',
  '墨小白': '大罗初期',
  '精炎童子': '真仙—太乙',
  '九曲灵参': '灵药成精（擅幻术）',
  '墨蛟': '二级妖兽（筑基期，墨蛟旗器灵）',
  '婴鲤兽': '五级水兽（≈结丹初期）',
  '雷鹏': '十级灵禽（≈元婴后期）',
  '金蛟王': '化形→九级→十级妖修（≈元婴后期）',
  '风希（裂风兽）': '化形→九级妖修（≈元婴中期）',
  '敖啸': '大乘（真龙一族老祖）',
  '天奎狼王': '合体（狼族，与银月敌对）',
  '螟虫之母': '大乘巅峰',
  '火须子': '大乘（火中圣兽）',
  '花石老祖': '合体初期→合体中期（韩立指点丹药）',
  '游天鲲鹏': '真灵级（≈大乘—真仙）',
  '罗睺': '真灵级（≈大乘—真仙）',
  '离火麒麟': '真灵级',
  '五光孔雀': '真灵级',
  '金乌': '真灵级（神禽）',
  '天凤（彩凤）': '真灵级（天凤血脉）',
  '真龙（金龙）': '真灵级',
  '玄武': '真灵级',
  '烛九阴': '真灵级（时间法则）',
  '曲魂': '炼尸之身（韩立以结煞丹炼制，元婴期战力）',
  '银翅夜叉': '元婴后期顶峰（十级炼尸）',
  '天都妖尸': '九级炼尸（≈元婴中期）',
  '尸魈': '十级炼尸（≈元婴后期）',
}

def esc(ev):
    return ev.replace('\\', '\\\\').replace('"', '\\"')

st = s.find('const BEASTS = [')
arr_start = st + len('const BEASTS = [')
p = s.find('\n];', arr_start)
if p < 0:
    p = s.find('];', arr_start)
arr_end = p + 2
seg = s[arr_start:arr_end]

def cb(m):
    raw = m.group(0)
    nm = re.search(r'\bn:"([^"]*)"', raw)
    if not nm: return raw
    ev = BEV.get(nm.group(1))
    if ev is None: return raw
    if re.search(r'\bev:"', raw): return raw
    rm = re.search(r'(\br:"(?:[^"\\]|\\.)*")', raw)
    if rm:
        return raw[:rm.end()] + ',ev:"' + esc(ev) + '"' + raw[rm.end():]
    return raw[:1] + 'ev:"' + esc(ev) + '",' + raw[1:]

before = seg.count('ev:"')
newseg = re.sub(r'\{n:.*?(?=\n  \{n:|\];)', cb, seg, flags=re.S)
after = newseg.count('ev:"')
s = s[:arr_start] + newseg + s[arr_end:]
io.open(PATH, 'w', encoding='utf-8').write(s)
print('BEASTS ev:', before, '->', after, '(+%d)' % (after-before))
