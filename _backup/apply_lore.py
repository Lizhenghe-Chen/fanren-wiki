# -*- coding: utf-8 -*-
"""依据用户提供的分析资料库丰富人物图谱网站：
1) 新增 17 个谱系角色；2) 丰富/修正核心角色 s 生平；3) 王婵→王蝉；4) 新增故事脉络+双韩立因果闭环区块。
（本版将新增条目写成 JS 文本行，避免 Python 字典字面量问题）
"""
import re, io

SRC = "/Users/bunnychen/Library/CloudStorage/OneDrive-Personal/我的工作文档/BunnyChen.github.io/docs/docs/Other/fanren-characters/index.html"
html = io.open(SRC, encoding="utf-8").read()

# ---------- 1. 王婵 -> 王蝉 ----------
cnt_wc = html.count("王婵")
html = html.replace("王婵", "王蝉")
print("王婵→王蝉 替换处数:", cnt_wc)

# ---------- 2. 新增角色条目（JS 文本行） ----------
NEW = {
"huangfeng": [
  '{n:"钟灵道", t:"黄枫谷掌门", r:"筑基后期", e:"正魔大战后黄枫谷撤离越国，下落未详", img:"zhonglingdao_huangfeng.jpg", s:"黄枫谷掌门，以公正严明著称；为持升仙令入谷的韩立办理入门手续，收纳慕容兄弟等天才弟子；正魔大战后随黄枫谷撤离越国，下落未详。", rel:"掌门", camp:"黄枫谷", race:"人族"}',
  '{n:"马师伯", t:"百药园管理者", r:"筑基中期", e:"被选为火种弟子撤离越国，下落未详", img:"mashibo_huangfeng.jpg", s:"黄枫谷百药园管理者，外貌似枯瘦矮小老头，脾气古怪却面冷心热；考校韩立草药识别能力后将百药园交其管理，赠丹药助韩立参加血色禁地试炼；被选为火种弟子撤离，下落未详。", rel:"前辈", camp:"黄枫谷", race:"人族"}',
  '{n:"吴风", t:"传功弟子", r:"炼气期", e:"正魔大战后下落未详", img:"wufeng_huangfeng.jpg", s:"黄枫谷传功弟子，对低阶法术领悟极深，无私教授同门法术心得，韩立受益良多；向韩立讲解血色禁地试炼的残酷与筑基丹主药来源；正魔大战后下落未详。", rel:"同门", camp:"黄枫谷", race:"人族"}',
  '{n:"燕如嫣", t:"燕家天灵根 · 王蝉之妻", r:"天灵根（筑基 → 结丹后期）", e:"随王蝉入鬼灵门，王蝉被清算后下落未详", img:"yanruyan_huangfeng.jpg", s:"燕家万年难遇的天灵根子弟；燕家归附鬼灵门时被指定嫁给王蝉共修血灵大法，凭借天灵根短短十几年便从筑基突破至结丹后期；王蝉被清算后下落未详。", rel:"仇敌之妻", camp:"燕家→鬼灵门", race:"人族·天灵根"}',
  '{n:"林师兄", t:"千竹教前少教主", r:"筑基（携大衍诀前四层）", e:"困死于韩立洞府颠倒五行阵，元神被韩立捏碎，韩立得其大衍诀与傀儡术传承", s:"千竹教前少教主，其父被现任教主金南天暗算夺位，携大衍诀前四层口诀逃至越国隐姓埋名潜伏黄枫谷；大衍诀突破后联系旧部反遭出卖追杀，中蛊毒逃至韩立洞府附近困死于颠倒五行阵，元神欲夺舍韩立反被捏碎。", rel:"机缘故人", camp:"千竹教→黄枫谷", race:"人族"}',
  '{n:"武炫", t:"李化元七弟子", r:"筑基", e:"拒绝参战离去，被发现死于黑煞教密室，被血祭吸尽精血", img:"wuxuan_huangfeng.jpg", s:"李化元门下七师兄，容貌英俊；原被推荐与董萱儿双修，因红拂对英俊男子有偏见而改荐韩立，故对韩立心生敌意；黑煞教行动前拒绝参战独自离去，次日被发现死于冷宫密室，被血祭吸尽精血。", rel:"不睦同门", camp:"黄枫谷", race:"人族"}',
],
"dajin": [
  '{n:"田不缺", t:"合欢宗宗主次子", r:"筑基", e:"劫走董萱儿后未再出场", s:"合欢宗宗主第二子，心性狡诈多情，身上异香令韩立极为不适；燕翎堡夺宝大会期间率合欢宗弟子袭击王蝉、劫走董萱儿，董萱儿因此被带回合欢宗知晓身世；后续未再出场。", rel:"敌对", camp:"合欢宗", race:"人族"}',
  '{n:"合欢老魔", t:"天南三大修士 · 云露老魔师兄", r:"元婴后期", e:"后续未再出场", s:"合欢宗最高战力，相貌狰狞的黑袍大汉；天一城元婴聚会时作为天南三大修士之一主持大局，云露老魔对其十分敬畏；后续未再出场。", rel:"前辈·敌对", camp:"合欢宗", race:"人族"}',
  '{n:"姜云", t:"古剑门结丹修士", r:"结丹", e:"后续未出场", s:"古剑门试剑大会带队之人，说话尖刻；古剑门实力居云梦三宗之首，每次试剑大会均压倒落云宗与百巧院，收有九灵剑体弟子；后续未出场。", rel:"路人", camp:"古剑门", race:"人族"}',
  '{n:"昌正", t:"百巧院结丹长老", r:"结丹", e:"后续未出场", s:"百巧院负责试剑大会的结丹长老，与落云宗火云峰之主段姓修士有旧交；后续未出场。", rel:"路人", camp:"百巧院", race:"人族"}',
  '{n:"卫姓长老", t:"落云宗长老 · 天煞宗奸细", r:"结丹", e:"被落云宗生擒后杳无音信", s:"落云宗长老，实为天煞宗奸细；云长老待其如亲子、传授道法神通，身份暴露后被解除大权困守灵眼之树圣地；天煞宗派人夺灵树时只分醇液以报恩，被生擒后杳无音信。", rel:"敌对", camp:"落云宗→天煞宗", race:"人族"}',
],
"lingjie": [
  '{n:"胡俊", t:"人族大乘修士", r:"大乘", e:"灵界篇末继续修行", s:"人族万年内新进阶的大乘修士，曾在青元宫求得灵丹；灵界篇末继续修行。", rel:"前辈", camp:"人族·青元宫", race:"人族"}',
  '{n:"火须子", t:"韩立灵界伙伴", r:"大乘（火中圣兽）", e:"随韩立飞升仙界", s:"韩立在灵界的伙伴，火中圣兽；曾评价韩立\u201c若当初马良法力受压制，几个照面就被你斩杀\u201d；韩立渡飞升劫时在场，随韩立飞升仙界。", rel:"伙伴", camp:"韩立麾下", race:"妖族·火圣兽"}',
  '{n:"黛儿", t:"韩立义妹", r:"化神 → 炼虚 → 合体", e:"灵界篇末远远目送韩立飞升", s:"韩立在灵界认作的妹妹，对韩立有超越兄妹之情；灵界篇末远远目送韩立飞升。", rel:"义妹", camp:"韩立麾下", race:"人族"}',
  '{n:"器灵子", t:"韩立门下弟子", r:"合体期（篇末）", e:"灵界篇末已入合体期，继续修行", s:"韩立在灵界收的弟子，灵界篇末已入合体期。", rel:"弟子", camp:"韩立门下", race:"人族"}',
  '{n:"天东商号方夫人", t:"天东商号主事", r:"炼虚", e:"暂无后续信息", s:"天东商号主事，韩立初入灵界失忆时加入其护卫队；暂无后续信息。", rel:"故人", camp:"天东商号", race:"人族"}',
  '{n:"张奎", t:"天东商号护卫队领队", r:"炼虚", e:"暂无后续信息", s:"天东商号护卫队领队，韩立初入灵界时的同僚，参与安远城抵御兽潮；暂无后续信息。", rel:"故人", camp:"天东商号", race:"人族"}',
],
"xianjie": [
  '{n:"厉飞羽", t:"厉飞雨转世", r:"飞升者（初入仙界）", e:"被高升接引，对\u201c韩立\u201d之名有莫名熟悉感", s:"厉飞雨以凡人之躯终老后，数千万年转世为厉飞羽，自北风界飞升黑土仙域；韩立大结局以掌天瓶返回过去时曾将一道黑光射入少年厉飞雨眉心，此即其转世后获得修仙资质的仙缘；飞升时手持先天仙器黑刀\u201c飞羽\u201d，被高升接引，对\u201c韩立\u201d之名有莫名熟悉感。", rel:"前世挚友", camp:"真言门", race:"人族"}',
  '{n:"韩立之女", t:"韩立与南宫婉之女", r:"幼童", e:"在父母身边快乐成长", s:"仙界篇末尾出现，在凉亭外追逐木制玩具，于父母身边快乐成长。", rel:"家人", camp:"黑土仙域", race:"人族"}',
],
}

# ---------- 3. 丰富/修正现有角色 s ----------
S_UPD = {
("qixuanmen","余子童"):
  "原炼气七层修士，肉身被毁后元神寄生墨大夫体内，蛊惑其夺舍韩立，反被韩立吞噬大半元神；最终被七毒水喷淋、软剑追砍，拉开石门于阳光下形神俱灭。",
("qixuanmen","张铁"):
  "韩立同门师弟，忠厚勤勉，被墨大夫以象甲功融合炼尸术炼成无魂尸人\u201c铁奴\u201d；韩立以引魂钟收服、血祭认出好友真身，改名曲魂作为身外化身，最终在虚天殿中被乾蓝冰焰熔化。",
("qixuanmen","厉飞雨"):
  "韩立七玄门挚友，外号厉虎，为报家仇服抽髓丸透支寿元换得武功，后任外刃堂堂主、娶张袖儿为妻，以凡人之躯终老；大结局韩立以掌天瓶返回过去，将一道黑光射入少年厉飞雨眉心，数千万年后其转世厉飞羽自北风界飞升仙界。",
("qixuanmen","墨彩环"):
  "墨大夫幼女，情窦初开时爱慕韩立而不得，终身未嫁、孤独终老；其灵魂转世为乱星海妙音门紫灵，数千万年后紫灵于六道轮回盘觉醒前世记忆（\u201c一直在等一个人，从豆蔻年华等到花甲古稀\u201d）。",
("qixuanmen","野狼帮帮主"):
  "野狼帮帮主，实名贾天龙。倾全帮之力攻打七玄门，以三百张军用连珠弩全歼谈判队伍，花三千两黄金请金光上人助阵；死契血斗中全军覆没，被韩立以火弹术烧成灰烬。",
("huangfeng","辛如音"):
  "阵法天才，身负\u201c龙吟之质\u201d（男体错生女儿身、经脉渐萎）。恋人为付家所杀后守寡，将毕生阵法心得赠韩立换取复仇承诺，修复古传送阵耗尽精血而亡，与齐云霄合葬，韩立视其为恩人。",
("luanxing","温天仁"):
  "六道传人、乱星海结丹第一人，倨傲自负；阴冥之地被韩立飞剑穿喉击杀，储物袋与碧绿内甲等宝物尽归韩立。",
("luanxing","蛮胡子"):
  "托天魔功传人、元婴中期，寿元将尽时被六道极圣堵门打成重伤，逃出途中遭极阴祖师趁虚偷袭，苦战三天三夜肉身被毁、元婴被囚百年；与韩立交易吞噬极阴元婴，后坐化。",
("luanxing","风希"):
  "裂风兽妖修，炼制风雷翅时被韩立窃走，多年后联手金蛟王围攻韩立，被八灵尺定身、六翼霜蚣冰封、飞剑斩成七八截，妖魂被四翅蜈蚣吞噬，形神俱灭。",
("dajin","向之礼"):
  "大晋化神第一人，与风老怪、呼庆雷闯空间节点飞升灵界，肉身成功抵达但元神被血影邪物吞噬；后以血影附身形态出现在韩立面前，被韩立灭杀。",
("dajin","银月"):
  "银月狼族敖啸老祖孙女，真名玲珑；护韩立闯天南大晋，昆吾山吞噬元刹分魂（与珑梦融合），随韩立飞升灵界。",
("lingjie","银月"):
  "银月狼族敖啸老祖孙女，真名玲珑；破除忘情诀心魔、觉醒七星月体，修至大乘统领妖族。韩立飞升时留在灵界。",
("lingjie","元瑶"):
  "为复活师姐妍丽碎丹还魂，被阴风卷入灵界地渊拜入鬼婆门下，脱身后被青元子收为义女，助其渡过灵界大天劫，修至合体巅峰；飞升仙界时陨于天劫，被韩立以掌天瓶穿越时空救回。",
("xianjie","韩立"):
  "飞升仙界后失忆重修（化名厉飞雨），一路破境终成时间道祖；斩杀古或今与魔主后放弃道祖之位，以掌天瓶返回过去完成因果闭环（救元瑶、助厉飞雨结仙缘、踢瓶给少年自己），携南宫婉、紫灵、元瑶隐居黑土仙域。",
("xianjie","紫灵"):
  "于六道轮回盘觉醒前世记忆（前世为人界凡俗女子墨彩环，苦等韩立一生未果），受冲击跌境后精进至大罗中期；积磷空境脱困后随韩立周游仙域，终隐居黑土仙域。",
("xianjie","轮回殿主"):
  "A 韩立：原始时间道祖，败于古或今后散尽时间法则注入掌天瓶、携女甘九真穿越远古，改修轮回法则创立轮回殿；妻甘如霜（南宫婉前世）牺牲。终与 B 韩立联手击败古或今，以身殉道陨落。",
("xianjie","甘九真"):
  "轮回殿主（A 韩立）与甘如霜之女，随父穿越远古；以\u201c蛟三\u201d身份潜伏无常盟，赠韩立青风锁仙符，大结局继承轮回殿主衣钵。",
("xianjie","古或今"):
  "自远古便占据时间道祖之位，A 韩立挑战其几乎被杀；最终决战吸收混沌法则企图进阶混沌道祖，被 A 韩立、B 韩立与魔主联手击败。",
}

def update_s(seg, name, new_s):
    om = re.search(r'\{\s*n:"%s"[^}]*\}' % re.escape(name), seg)
    if not om:
        return seg, False
    obj = om.group(0)
    new_obj = re.sub(r's:"((?:[^"\\]|\\.)*)"', lambda m: 's:"%s"' % new_s, obj, count=1)
    if new_obj == obj:
        return seg, False
    return seg.replace(obj, new_obj, 1), True

all_ch = set(NEW.keys()) | set(k[0] for k in S_UPD)
pat = re.compile(r'(DATA\.(%s)\s*=\s*\[)(.*?)(\];)' % "|".join(re.escape(c) for c in all_ch), re.S)

def process(m):
    head, ch, body, tail = m.group(1), m.group(2), m.group(3), m.group(4)
    for (c, name), new_s in S_UPD.items():
        if c == ch:
            body, ok = update_s(body, name, new_s)
            if not ok:
                print("!! s更新失败:", ch, name)
    if ch in NEW and NEW[ch]:
        body = body.rstrip() + ",\n  " + ",\n  ".join(NEW[ch]) + "\n"
    return head + body + tail

html = pat.sub(process, html)
print("角色新增与s更新完成")

# ---------- 5. 新增故事脉络 + 双韩立因果闭环区块 ----------
LORE = '''
<!-- ===== 故事脉络 · 核心因果链 ===== -->
<section class="lore-sec" id="lore">
  <div class="wrap">
    <div class="sec-title">故事脉络 · 核心因果链</div>
    <div class="sec-desc">六篇章主线推进：凡人 → 炼气 → 筑基 → 结丹 → 元婴 → 化神 → 大乘 → 大罗，最终完成时空因果闭环</div>
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
</section>
'''
anchor = "<!-- ===== 导航 ===== -->"
if anchor in html:
    html = html.replace(anchor, LORE + "\n" + anchor, 1)
    print("故事脉络区块已插入")
else:
    print("!! 锚点未找到，未插入故事脉络")

# ---------- 6. CSS ----------
CSS = '''
.lore-sec{padding:34px 0 8px}
.lore-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin:20px 0 30px}
.lore-card{background:linear-gradient(160deg,rgba(255,255,255,.045),rgba(255,255,255,.015));border:1px solid rgba(212,175,110,.22);border-radius:12px;padding:16px 16px 14px;transition:border-color .25s}
.lore-card:hover{border-color:rgba(212,175,110,.55)}
.lc-stage{font-size:15px;font-weight:700;color:#e8c98a;letter-spacing:.5px}
.lc-realm{display:inline-block;margin:6px 0 8px;padding:2px 9px;border-radius:20px;font-size:12px;color:#f5ead2;background:rgba(212,175,110,.16);border:1px solid rgba(212,175,110,.35)}
.lc-note{font-size:13px;line-height:1.75;color:rgba(240,230,210,.82)}
.causality{margin:6px 0 26px;border:1px solid rgba(212,175,110,.28);border-radius:14px;background:linear-gradient(150deg,rgba(212,175,110,.07),rgba(120,90,40,.04));padding:18px 20px 16px}
.causality-title{font-size:16px;font-weight:800;color:#e8c98a;letter-spacing:1px;margin-bottom:14px}
.causality-title span{font-size:12px;font-weight:400;color:rgba(240,230,210,.6);margin-left:6px}
.causality-row{display:grid;grid-template-columns:1fr auto 1fr;gap:14px;align-items:stretch}
.causality-card{border-radius:10px;padding:14px 16px;border:1px solid rgba(212,175,110,.35)}
.causality-card p{margin:8px 0 0;font-size:13px;line-height:1.85;color:rgba(240,230,210,.86)}
.ca-a{background:rgba(140,80,120,.12);border-color:rgba(200,120,170,.35)}
.ca-b{background:rgba(70,110,160,.12);border-color:rgba(110,160,220,.35)}
.cc-tag{display:inline-block;font-size:13px;font-weight:700;color:#f5ead2;background:rgba(212,175,110,.18);padding:3px 12px;border-radius:20px;border:1px solid rgba(212,175,110,.4)}
.causality-arrow{display:flex;align-items:center;font-size:22px;color:#e8c98a;opacity:.9}
.causality-note{margin:14px 0 0;font-size:12.5px;line-height:1.7;color:rgba(240,230,210,.6);border-top:1px dashed rgba(212,175,110,.3);padding-top:12px}
@media (max-width:860px){
  .lore-grid{grid-template-columns:1fr 1fr}
  .causality-row{grid-template-columns:1fr}
  .causality-arrow{justify-content:center;transform:rotate(90deg)}
}
@media (max-width:560px){
  .lore-grid{grid-template-columns:1fr}
}
'''
css_anchor = "/* ===== 图例与页脚 ===== */"
if css_anchor in html:
    html = html.replace(css_anchor, CSS + "\n" + css_anchor, 1)
    print("CSS 已插入")
else:
    print("!! CSS锚点未找到")

io.open(SRC, "w", encoding="utf-8").write(html)
print("写回完成")
