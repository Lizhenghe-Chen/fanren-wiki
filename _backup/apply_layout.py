# -*- coding: utf-8 -*-
"""页面布局优化：
1) hero 压缩；2) 韩立时间轴 + 故事脉络合并为左右两栏速览区；3) 后续区块 padding 微调。
"""
import io

SRC = "/Users/bunnychen/Library/CloudStorage/OneDrive-Personal/我的工作文档/BunnyChen.github.io/docs/docs/Other/fanren-characters/index.html"
html = io.open(SRC, encoding="utf-8").read()

# ---------- 1. hero 压缩 ----------
hero_css = [
  ('.hero{position:relative;padding:64px 0 46px;overflow:hidden}',
   '.hero{position:relative;padding:30px 0 20px;overflow:hidden}'),
  ('.hero-sub{margin-top:14px;color:var(--ink2);font-size:15px;max-width:640px}',
   '.hero-sub{margin-top:10px;color:var(--ink2);font-size:13.5px;max-width:640px}'),
  ('.project-links{display:flex;gap:10px;flex-wrap:wrap;margin-top:24px}',
   '.project-links{display:flex;gap:10px;flex-wrap:wrap;margin-top:16px}'),
  ('.stats{display:flex;gap:26px;margin-top:26px;flex-wrap:wrap}',
   '.stats{display:flex;gap:20px;margin-top:16px;flex-wrap:wrap}'),
  ('.hero-cover{flex:0 0 240px;position:relative}',
   '.hero-cover{flex:0 0 170px;position:relative}'),
]
for old, new in hero_css:
    assert html.count(old) == 1, "hero CSS 未匹配: " + old[:40]
    html = html.replace(old, new, 1)
print("hero 压缩完成")

# ---------- 2. timeline + lore -> 两栏速览 ----------
OLD_BLOCK_START = "<!-- ===== 韩立境界时间轴 ===== -->"
OLD_BLOCK_END = "</section>\n\n<!-- ===== 导航 ===== -->"
si = html.index(OLD_BLOCK_START)
ei = html.index(OLD_BLOCK_END)
new_block = '''<!-- ===== 世界观速览：韩立时间轴 + 故事脉络 ===== -->
<section class="ov-sec">
  <div class="wrap">
    <div class="ov-grid">
      <div class="ov-col ov-tl-col">
        <div class="sec-title">韩立 · 境界演进时间轴</div>
        <div class="sec-desc">凡人 → 炼气 → 筑基 → 结丹 → 元婴 → 化神 → 炼虚 → 合体 → 大乘 → 真仙 → 金仙 → 太乙 → 大罗 → 道祖（自降大罗巅峰归隐）</div>
        <div class="tl" id="timeline"></div>
      </div>
      <div class="ov-col ov-lore-col">
        <div class="sec-title">故事脉络 · 核心因果链</div>
        <div class="sec-desc">六篇章主线推进，最终完成时空因果闭环</div>
        <div class="lore-grid">
          <div class="lore-card"><div class="lc-stage">七玄门 · 凡人起点</div><div class="lc-realm">炼气</div><div class="lc-note">入七玄门 → 得掌天瓶 → 反噬墨大夫与余子童 → 灭金光上人获升仙令 → 告别凡俗</div></div>
          <div class="lore-card"><div class="lc-stage">黄枫谷 · 筑基</div><div class="lc-realm">炼气 → 筑基</div><div class="lc-note">升仙令免试入门 → 血色禁地筑基、结缘南宫婉 → 正魔大战 → 辛如音修古传送阵 → 被吸干修为入乱星海</div></div>
          <div class="lore-card"><div class="lc-stage">乱星海 · 结丹结婴</div><div class="lc-realm">结丹 → 元婴</div><div class="lc-note">虚天殿夺宝 → 窃风雷翅 → 银月化形 → 落云宗结婴 → 大衍神君传大衍诀</div></div>
          <div class="lore-card"><div class="lc-stage">大晋 · 化神飞升</div><div class="lc-realm">元婴 → 化神</div><div class="lc-note">通天灵宝之争 → 斩风希与金蛟王 → 向之礼指引化神之秘 → 闯空间节点飞升灵界</div></div>
          <div class="lore-card"><div class="lc-stage">灵界 · 大乘渡劫</div><div class="lc-realm">化神 → 大乘</div><div class="lc-note">失忆归零、金刚诀重修 → 灵界百族争锋 → 魔界之战 → 大乘 → 渡飞升天劫</div></div>
          <div class="lore-card"><div class="lc-stage">仙界 · 道祖之战</div><div class="lc-realm">真仙 → 大罗</div><div class="lc-note">北寒仙域 → 灰界 → 轮回之秘（双韩立揭晓）→ 联手轮回殿主斩古或今 → 放弃道祖 → 时空回溯 → 隐居黑土仙域</div></div>
        </div>
        <div class="causality">
          <div class="causality-title">双韩立 · 因果闭环 <span>（唯一时间线，无平行时空）</span></div>
          <div class="causality-row">
            <div class="causality-card ca-a">
              <div class="cc-tag">A 韩立 · 轮回殿主</div>
              <p>原始时间道祖：时间法则大成，挑战古或今落败 → 散尽毕生时间法则注入掌天瓶 → 携女甘九真穿越远古 → 改修轮回法则成就道祖、创立轮回殿 → 妻甘如霜（南宫婉前世）在追杀中牺牲 → 与 B 韩立联手击败古或今 → 陨落</p>
            </div>
            <div class="causality-arrow" aria-hidden="true">⇄</div>
            <div class="causality-card ca-b">
              <div class="cc-tag">B 韩立 · 本线主角</div>
              <p>山边小村诞生、捡到掌天瓶 → 凡人修仙（本故事主线）→ 成就大罗、放弃道祖之位 → 击败古或今 → 用掌天瓶返回过去：救元瑶、帮厉飞雨结仙缘、踢瓶给少年自己 → 瓶碎、因果闭环 → 与南宫婉隐居黑土仙域</p>
            </div>
          </div>
          <p class="causality-note">掌天瓶 = A 韩立毕生时间法则之力所铸，是唯一能逆转时空之物；B 韩立返回过去确保少年自己捡到瓶，时空因果完美咬合——不存在第三条时间线。</p>
        </div>
      </div>
    </div>
  </div>
</section>

<!-- ===== 导航 ===== -->'''
html = html[:si] + new_block + html[ei:]
print("两栏速览区完成")

# ---------- 3. 后续区块 padding 微调 ----------
minor = [
  ('.lore-sec{padding:34px 0 8px}', '.lore-sec{padding:0}'),
  ('.realm-sec{padding:38px 0 10px;border-top:1px solid var(--line)}',
   '.realm-sec{padding:26px 0 8px;border-top:1px solid var(--line)}'),
  ('.bar-sec{padding:26px 0 10px}', '.bar-sec{padding:18px 0 8px}'),
  ('.legend-sec{padding:20px 0 10px}', '.legend-sec{padding:14px 0 8px}'),
]
for old, new in minor:
    if old in html:
        html = html.replace(old, new, 1)
    else:
        print("minor 未匹配:", old[:40])
print("padding 微调完成")

# ---------- 4. 新增两栏 CSS ----------
OV_CSS = '''
/* ===== 世界观速览（两栏） ===== */
.ov-sec{padding:26px 0 10px}
.ov-grid{display:grid;grid-template-columns:minmax(0,2fr) minmax(0,3fr);gap:28px;align-items:start}
.ov-col .sec-desc{margin-bottom:16px}
.ov-tl-col{padding-top:2px}
.ov-tl-col .tl-row{grid-auto-columns:minmax(66px,1fr);min-width:920px}
.ov-lore-col .lore-grid{grid-template-columns:repeat(2,1fr);gap:12px;margin:14px 0 18px}
.ov-lore-col .lore-card{padding:13px 14px 11px}
.ov-lore-col .lc-stage{font-size:14px}
.ov-lore-col .lc-note{font-size:12.5px;line-height:1.7}
.ov-lore-col .causality{margin-bottom:6px;padding:14px 16px 12px}
.ov-lore-col .causality-card{padding:11px 13px}
.ov-lore-col .causality-card p{font-size:12.5px;line-height:1.75}
.ov-lore-col .causality-note{margin-top:10px;font-size:12px;padding-top:9px}
@media (max-width:1000px){
  .ov-grid{grid-template-columns:1fr;gap:18px}
  .ov-tl-col .tl-row{grid-auto-columns:minmax(82px,1fr);min-width:1148px}
  .ov-lore-col .lore-grid{grid-template-columns:repeat(2,1fr)}
}
@media (max-width:600px){
  .ov-lore-col .lore-grid{grid-template-columns:1fr}
}
'''
css_anchor = "/* ===== 图例与页脚 ===== */"
assert css_anchor in html
html = html.replace(css_anchor, OV_CSS + "\n" + css_anchor, 1)
print("两栏 CSS 完成")

io.open(SRC, "w", encoding="utf-8").write(html)
print("写回完成")
