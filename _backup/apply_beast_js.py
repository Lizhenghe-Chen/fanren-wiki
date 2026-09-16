# -*- coding: utf-8 -*-
"""第四视图：插入 JS 数据 + 渲染函数 + 路由。"""
import io

P = r"/Users/bunnychen/Documents/GitProjects/Lizhenghe-Chen.github.io/docs/docs/Other/fanren-characters/index.html"
html = io.open(P, encoding="utf-8").read()

# ========== 1. 数据（插入在时间轴定义之前） ==========
data_js = """
/* ===== 灵兽灵虫数据：n名称 / t身份 / r等级（对应修为）/ e结局 / img配图 / s生平 / rel归属 / camp来源 / race种族 / cat类别 / ev演进 ===== */
const BEAST_CATS = [
  {id:"all",   name:"全部",     color:"var(--gold)"},
  {id:"chong", name:"灵虫",     color:"#7fb3d9"},
  {id:"shou",  name:"灵兽",     color:"#6fa8dc"},
  {id:"yao",   name:"妖兽妖修", color:"#b06ad4"},
  {id:"zhen",  name:"真灵·神兽", color:"#4ec9a0"},
  {id:"lian",  name:"炼尸魔物", color:"#e07b54"}
];
const BEAST_RAIL = [
  {lv:"一级",     realm:"≈ 炼气期",       note:"初启灵智，体型稍大于野兽。双瞳鼠、云翅鸟等。"},
  {lv:"二~四级",  realm:"≈ 筑基期",       note:"灵智渐开，可修初级妖术。墨蛟（二级）、金丝蚕等。"},
  {lv:"五~七级",  realm:"≈ 结丹期",       note:"凝聚妖丹，神通初成。婴鲤兽、六翼霜蜈（七级）等。"},
  {lv:"八~十级",  realm:"≈ 元婴期",       note:"化形期，可化人形、灵智大开。金蛟王、雷鹏、圭灵等。"},
  {lv:"十一~十三级", realm:"≈ 化神—合体", note:"掌握空间/时间类神通，多为灵界大妖。"},
  {lv:"真灵级",   realm:"≈ 大乘—真仙",    note:"上古真灵，横扫同阶。游天鲲鹏、罗睺、五光孔雀等。"}
];
const BEASTS = [
  {n:"噬金虫（金童）", t:"韩立本命灵虫 · 虫族共主转世", cat:"chong", r:"低阶虫群 → 噬金仙 → 太乙 → 恢复吞噬道祖修为", e:"与韩立联手斩杀轩辕杰成道祖，后与韩立别过、驻守魔域", img:"jintong_lingjie.jpg", s:"韩立乱星海所得的本命灵虫，无物不噬、水火不侵，群攻无双。从低阶虫群一路进化，灵界末进阶噬金仙，仙界化形为女童「金童」，觉醒前世真魂记忆——原是虫族共主道祖「渠鳞」。曾助韩立灭杀真仙马良，最终与韩立联手斩杀轩辕杰、恢复道祖修为，与韩立别过后驻守魔域。", rel:"韩立本命", camp:"韩立附属→魔域", race:"灵虫·噬金虫", ev:"虫群→噬金仙→太乙→吞噬道祖（金童）"},
  {n:"血玉蜘蛛", t:"奇虫榜第108位 · 虚天鼎关键灵宠", cat:"chong", r:"四级顶峰 → 七级（一雌一雄方可进阶）", e:"虚天殿中一雌被星宫长老击杀，另一只无法进阶，被韩立安置养老", img:"xueyuzhizhu.jpg", s:"韩立筑基期在燕家矿洞斩四阶巅峰母蛛后得两枚卵，孵化为一雌一雄，滴血认主、以饲灵丸培育至四级顶峰。蛛丝不惧乾蓝冰焰，可克制噬金虫，是韩立取出第一件通天灵宝虚天鼎的关键。虚天殿一役雌蛛被星宫长老斩杀，仅剩雄蛛无法进阶，韩立将其安顿养老，此后未再登场。", rel:"韩立灵宠", camp:"韩立附属", race:"灵虫·血玉蜘蛛"},
  {n:"六翼霜蜈", t:"奇虫榜第18位 · 冰属性真龙血脉", cat:"chong", r:"幼虫 → 四级（四翼）→ 七级 → 大乘（成熟六翼真灵）", e:"灵界十二条合一进化六翼霜蜈后叛逃，修至大乘，韩立重逢后放其自由", img:"liuyishuangwu.jpg", s:"韩立从柳玉处得来的奇虫卵，以霓裳草、雪魄丸、灵泉催育，育出十二条四翼霜蜈，联手可冰封元婴修士风希。灵界青罗沙漠十二条合一、背生六翼进化为成熟体六翼霜蜈，趁韩立法力尽失时叛逃，此后击杀冰属性妖兽强化自身，几乎与韩立同期踏入大乘。韩立重逢后放其自由，与之交易千年。", rel:"韩立灵虫→叛逃", camp:"韩立附属", race:"灵虫·冰蜈"},
  {n:"云翅鸟", t:"传讯灵禽", cat:"chong", r:"三级灵禽", e:"随韩立辗转，后续下落未明", s:"墨大夫传于韩立的传讯灵禽，可高空侦查、千里传讯，是韩立早期少有的灵宠之一；后期韩立手段渐多后未再提及。", rel:"韩立灵禽", camp:"墨大夫→韩立", race:"灵禽"},
  {n:"金背妖螂", t:"御灵宗妖虫", cat:"chong", r:"五级妖虫（≈结丹初期）", e:"背景设定角色，未展开结局", s:"御灵宗驯养的金背螳螂类妖虫，刀臂锋利、速度极快，属奇虫榜有名之虫；仅作背景设定出现，未直接与韩立交手。", rel:"宗门妖虫", camp:"御灵宗", race:"妖虫"},

  {n:"啼魂（刑兽）", t:"刑兽后裔 · 冥王转世", cat:"shou", r:"灵兽 → 噬魂真灵 → 合体飞升 → 太乙 → 大罗", e:"与阴丞全决裂，吞噬鬼王进阶大罗，闭关苦修", img:"tihun_lingjie.jpg", s:"青阳门血祭秘法召唤来的非神非人非鬼生灵，韩立自元瑶处讨得。专噬精魂、克制炼尸鬼物，是人界到仙界一路相伴的核心灵宠；真身为冥界冥王转世，比韩立更早飞升仙界，仙界篇与阴丞全决裂、吞噬鬼王进阶大罗，最终留在幽冥界独自修炼。", rel:"韩立伴身灵兽", camp:"韩立附属", race:"灵兽·刑兽", ev:"灵兽→噬魂真灵→合体期飞升→太乙→大罗"},
  {n:"双瞳鼠", t:"一级中阶妖兽 · 天生神目", cat:"shou", r:"一级中阶（≈炼气期）", e:"韩立逃离黄枫谷时被留在洞府，此后未再登场", img:"shuangtongshu.jpg", s:"形似普通老鼠的一级妖兽，天生神目，双瞳能轻易看穿障碍、透视迷雾河流树木，喜在灵气稠密处做窝，是韩立的寻宝侦察小灵兽。韩立被南宫婉吸干法力逃离黄枫谷时走得仓促，将它留在了洞府（动画结局），原著后续亦未再登场。", rel:"韩立灵兽", camp:"韩立附属", race:"灵兽·鼠"},
  {n:"土甲龙", t:"寻宝灵兽 · 昆吾山所得", cat:"shou", r:"七级灵兽（≈结丹后期）", e:"助韩立取得伏魔阵钥匙，韩立偷渡灵界前留给人界南宫婉", s:"昆吾山一役韩立得到的寻宝灵兽，天赋神通可感应灵物、助韩立取得伏魔阵钥匙。韩立偷渡灵界前将其留给南宫婉，此后未再登场。", rel:"韩立→南宫婉", camp:"韩立附属", race:"灵兽·土甲龙"},
  {n:"豹鳞兽", t:"变异灵兽 · 风遁神通", cat:"shou", r:"真灵级（变异风遁）", e:"落日之墓收服，随韩立闯荡，结局未明", s:"韩立在落日之墓收服的变异灵兽，身具风遁神通、速度极快，属真灵级变异个体；随韩立闯荡多年，后期戏份渐少，结局未明。", rel:"韩立灵兽", camp:"韩立附属", race:"灵兽·豹鳞"},
  {n:"圭灵", t:"十级玄岩龟", cat:"shou", r:"十级妖修（≈元婴后期）", e:"被迫认韩立为主，后死于空间裂缝", img:"guiling.jpg", s:"十级玄岩龟，防御力可硬抗化神一击。昆吾山附近被韩立制服，被迫认主；后随韩立行动，最终死于空间裂缝。", rel:"契约灵兽", camp:"韩立附属", race:"妖族·玄岩龟"},
  {n:"蟹道人（石空解）", t:"魔域魔君 · 傀儡道祖", cat:"shou", r:"伪仙儡（实力≈大乘）→ 傀儡法则道祖", e:"与魔主内战后随韩立隐居黑土仙域", img:"xiedaoren_lingjie.jpg", s:"原名石空解，魔域石家魔君、空间道祖魔主之弟，以伪仙儡形态与韩立签订契约随行，一路同闯灵界仙界，记忆渐复、重证傀儡法则道祖之位；与魔主（兄长）内战后随韩立隐居黑土仙域。", rel:"契约伙伴", camp:"魔域·石家", race:"傀儡·仙族", ev:"伪仙儡（实力≈大乘）→傀儡法则道祖"},
  {n:"墨小白", t:"墨眼貔貅", cat:"shou", r:"大罗初期", e:"韩立契约灵兽，存活", s:"墨眼貔貅、大罗初期，韩立在仙界收服的契约灵兽，随韩立行动，最终存活。", rel:"契约灵兽", camp:"韩立附属", race:"妖族·墨眼貔貅"},
  {n:"精炎童子", t:"精炎之灵化形", cat:"shou", r:"真仙—太乙", e:"随韩立至仙界，结局未明", s:"精炎之灵化形的童子，自人界随韩立至仙界，是韩立的伴生灵物之一，结局未明。", rel:"伴生灵物", camp:"韩立附属", race:"精炎之灵"},
  {n:"九曲灵参", t:"灵药化形 · 幻术精怪", cat:"shou", r:"灵药成精（擅幻术）", e:"虚天殿所得，随韩立，后续未再详述", s:"虚天殿中的灵药化形精怪，可施展幻术（曾幻化成兔子）；玄骨上人曾以之为筹码，后归韩立，属灵药成精的异类灵物。", rel:"韩立所得", camp:"虚天殿", race:"精怪·灵参"},

  {n:"墨蛟", t:"血色禁地恶蛟 · 韩立与南宫婉的"媒人"", cat:"yao", r:"二级妖兽（筑基期）", e:"被韩立与南宫婉联手击杀，淫囊令二人结缘", img:"mojiao.jpg", s:"血色禁地深处的恶蛟，由黑鳞蟒进化而来，鳞甲防御惊人、淫囊可致幻。韩立为筑基丹入禁地撞上，与压制修为的南宫婉联手将其击杀；南宫婉收取其元神与淫囊，二人因触碰淫囊而结为道侣，墨蛟因此被戏称为韩立的"修仙锦鲤"。", rel:"野生妖兽", camp:"血色禁地", race:"妖兽·蛟"},
  {n:"婴鲤兽", t:"黑煞教镇教水兽", cat:"yao", r:"五级水兽（≈结丹初期）", e:"被韩立借曲魂挡下，最终被除，结局未细述", s:"黑煞教供奉的水域凶兽，婴啼摄魂、水战极强。韩立曾以曲魂作挡箭牌应对，最终将其除去。", rel:"敌兽", camp:"黑煞教", race:"水兽·婴鲤"},
  {n:"雷鹏", t:"风雷阁灵禽 · 雷遁极速", cat:"yao", r:"十级灵禽（≈元婴后期）", e:"背景设定级大妖，未与韩立直接交手，结局未明", s:"风雷阁相关的高阶灵禽，雷遁极速、瞬息千里，为十级化形大妖；仅在设定中出现，未与韩立直接交手。", rel:"野生大妖", camp:"风雷阁", race:"灵禽·雷鹏"},
  {n:"金蛟王", t:"外星海妖修", cat:"yao", r:"十级妖修（≈元婴后期）", e:"与韩立结怨夺灵石矿，被韩立斩杀取内丹", img:"jinjiaowang.jpg", s:"乱星海外星海妖修、十级化形大妖，与韩立结怨争夺灵石矿，被韩立斩杀并取其内丹。", rel:"仇敌", camp:"外星海妖族", race:"妖族·蛟龙"},
  {n:"风希（裂风兽）", t:"裂风兽妖修 · 风雷翅原主", cat:"yao", r:"九级妖修（≈元婴中期）", e:"炼风雷翅时胁迫韩立，后被韩立灭杀，妖魂被四翅蜈蚣吞噬", img:"fengxi.jpg", s:"裂风兽妖修、九级化形大妖，以自身本命神通炼制风雷翅时被韩立窃走灵羽；多年后联手金蛟王围攻韩立，被八灵尺定身、六翼霜蜈冰封、飞剑斩成数截，妖魂被四翅蜈蚣吞噬，形神俱灭。", rel:"仇敌", camp:"外星海妖族", race:"妖族·裂风兽"},
  {n:"冰凤", t:"冰海之主 · 天凤血脉", cat:"yao", r:"元婴后期（压境不化神）→ 化神 → 炼虚 → 合体 → 大乘", e:"韩立飞升时留驻青元宫，未入仙界", img:"bingfeng_lingjie.jpg", s:"冰海之主、十级妖修，身具天凤血脉与空间神通，通体雪白。与小极宫混战被困虚天殿八十年，后与韩立结缘、随其偷渡灵界，入青元宫修至大乘；韩立飞升时留驻青元宫。", rel:"红颜盟友", camp:"青元宫", race:"妖族·冰凤", ev:"元婴后期（压境不化神）→化神→炼虚→合体→大乘"},
  {n:"银月（玲珑）", t:"银月狼族圣女 · 虚天鼎器灵", cat:"yao", r:"器灵 → 化形 → 炼虚 → 合体 → 大乘", e:"破除心魔、觉醒七星月体，修至大乘统领妖族；韩立飞升时留在灵界", img:"yinyue_lingjie.jpg", s:"银月狼族敖啸老祖孙女、真名玲珑，原为虚天鼎器灵，认韩立为主成为本命飞剑器灵，后夺舍四瞳灵狐化形。一路伴随韩立闯荡，破除忘情诀心魔、觉醒七星月体，修至大乘统领灵界妖族；韩立飞升时留在灵界。", rel:"红颜挚友", camp:"天狼族·妖族", race:"妖族·银月狼族", ev:"器灵（≈结丹/元婴战力）→夺舍灵狐→化形→炼虚→合体→大乘"},
  {n:"敖啸", t:"妖族唯一大乘 · 银月祖父", cat:"yao", r:"大乘", e:"第22次大天劫陨落，临终将银月托付韩立", img:"aoxiao.jpg", s:"灵界妖族唯一大乘、银月狼族老祖，银月祖父。与韩立结盟，第22次大天劫时陨落，临终将银月托付韩立照拂。", rel:"盟友前辈", camp:"灵界妖族", race:"妖族·狼族"},
  {n:"天奎狼王", t:"天狼族妖王 · 银月名义前夫", cat:"yao", r:"合体", e:"死于魔界入侵大战", s:"天狼族妖王，曾与银月有名义婚约，与韩立敌对；死于魔界入侵灵界的大战。", rel:"敌对", camp:"天狼族", race:"妖族·狼族"},
  {n:"螟虫之母", t:"角蚩族始祖 · 灵界大敌", cat:"yao", r:"大乘巅峰", e:"被韩立联合诸大乘斩杀", img:"mingchongzhimu.jpg", s:"角蚩族始祖、大乘巅峰，虫潮席卷灵界的大敌，曾逼得人族唯一大乘莫简离以身为印封印；最终被韩立联合诸大乘斩杀。", rel:"仇敌", camp:"角蚩族", race:"妖族·螟虫"},
  {n:"火须子", t:"火中圣兽 · 韩立灵界伙伴", cat:"yao", r:"大乘（火中圣兽）", e:"随韩立飞升仙界", s:"韩立在灵界的伙伴、火中圣兽，大乘修为；曾评价韩立「若当初马良法力受压制，几个照面就被你斩杀」。韩立渡飞升劫时在场，随韩立飞升仙界。", rel:"伙伴", camp:"韩立麾下", race:"妖族·火圣兽"},
  {n:"花石老祖", t:"蛮荒水域妖修 · 韩立半个弟子", cat:"yao", r:"合体初期 → 合体中期（韩立指点丹药）", e:"随韩立入青元宫，以弟子身份侍奉，结局未明", s:"蛮荒世界水属性妖修，占据万余里水域，合体初期称霸一方。被韩立强行征召带路后折服，主动自称半个弟子、口称韩师，得韩立赐丹点拨，短短大半年突破至合体中期；入青元宫后为韩立处理水域事务，是韩立非正式弟子中最忠心的一位。", rel:"半个弟子", camp:"青元宫", race:"妖族·水属性"},

  {n:"游天鲲鹏", t:"上古真灵 · 风系至强", cat:"zhen", r:"真灵级（≈大乘—真仙）", e:"背景设定级存在，未正面登场", s:"上古真灵，风属性、体长数千丈，与罗睺为宿敌；为真灵级天花板存在，仅作背景设定。", rel:"野生真灵", camp:"灵界海空", race:"真灵·鲲鹏"},
  {n:"罗睺", t:"真灵魔兽 · 吞食日月", cat:"zhen", r:"真灵级（≈大乘—真仙）", e:"背景设定级存在，藏身海底", s:"上古真灵魔兽，吞食日月、可穿梭界面，藏身海底，为游天鲲鹏之死敌；仅作背景设定。", rel:"野生真灵", camp:"海底", race:"真灵·魔兽"},
  {n:"离火麒麟", t:"麒麟真火 · 离火焚天", cat:"zhen", r:"真灵级", e:"背景设定，居灵界火狱", s:"上古真灵麒麟，离火焚天、麒麟真火可焚万物，居于灵界火狱；仅作背景设定。", rel:"野生真灵", camp:"灵界火狱", race:"真灵·麒麟"},
  {n:"五光孔雀", t:"五色神光 · 刷落万物", cat:"zhen", r:"真灵级", e:"背景设定，居孔雀山", s:"上古真灵孔雀，五色神光可刷落万物、无宝不落，居于孔雀山；仅作背景设定。", rel:"野生真灵", camp:"孔雀山", race:"真灵·孔雀"},
  {n:"金乌", t:"太阳真火 · 化日神通", cat:"zhen", r:"真灵级（神禽）", e:"背景设定，金乌族镇族真灵", s:"上古真灵神禽，太阳真火、可化日而行，为金乌族镇族真灵；仅作背景设定。", rel:"野生真灵", camp:"金乌族", race:"真灵·金乌"},
  {n:"天凤（彩凤）", t:"涅槃之火 · 重生之能", cat:"zhen", r:"真灵级（天凤血脉）", e:"背景设定，居天凤宫", s:"上古真灵天凤，涅槃之火赋予其重生之能，天凤血脉为冰凤等后裔源头；居天凤宫，仅作背景设定。", rel:"野生真灵", camp:"天凤宫", race:"真灵·天凤"},
  {n:"真龙（金龙）", t:"龙族真灵 · 空间禁锢", cat:"zhen", r:"真灵级", e:"背景设定，居龙岛（仙界篇陈如烟即上古真龙化身）", s:"上古真灵真龙，龙息、真龙鳞、空间禁锢俱全，居龙岛；仙界篇天道七君中的陈如烟（水之本源道祖）即上古真龙化身。", rel:"野生真灵", camp:"龙岛", race:"真灵·真龙"},
  {n:"玄武", t:"玄龟真灵 · 绝对防御", cat:"zhen", r:"真灵级", e:"背景设定，居北冥岛", s:"上古真灵玄武，绝对防御、玄冰重水，居北冥岛；仅作背景设定。", rel:"野生真灵", camp:"北冥岛", race:"真灵·玄武"},
  {n:"烛九阴", t:"时间真龙 · 烛照九阴", cat:"zhen", r:"真灵级（时间法则）", e:"背景设定，居仙界光阴长河", s:"上古真灵时间龙，烛照九阴、可令时间停止，居仙界光阴长河；仅作背景设定。", rel:"野生真灵", camp:"仙界光阴长河", race:"真灵·时间龙"},

  {n:"曲魂", t:"张铁所化炼尸 · 韩立身外化身", cat:"lian", r:"炼尸（结煞丹）", e:"被玄骨上人夺舍，虚天殿中被乾蓝冰焰熔化而毁", img:"quhun.jpg", s:"韩立师弟张铁被墨大夫炼成无魂尸人，韩立以引魂钟收服、改名曲魂作为身外化身；虚天殿一役被玄骨上人夺舍，最终被乾蓝冰焰熔化。", rel:"身外化身", camp:"韩立附属", race:"炼尸"},
  {n:"银翅夜叉", t:"空玄丹士所化炼尸", cat:"lian", r:"元后顶峰（十级炼尸）", e:"死于元刹魔像之手", img:"yinchiyecha.jpg", s:"空玄丹士所化的十级炼尸，风土双遁、银瞳幻术，为炼尸中的巅峰个体；死于元刹魔像之手。", rel:"散修炼尸", camp:"散修·炼尸", race:"炼尸"},
  {n:"天都妖尸", t:"极阴祖师炼尸 · 天都尸火", cat:"lian", r:"九级炼尸（≈元婴中期）", e:"背景设定角色，未细述结局", s:"极阴祖师所炼的高阶炼尸，身怀天都尸火、可焚魂蚀骨；仅作背景设定。", rel:"魔道炼尸", camp:"极阴岛", race:"炼尸"},
  {n:"尸魈", t:"极阴岛元婴尸 · 怨气不灭", cat:"lian", r:"十级炼尸（≈元婴后期）", e:"背景设定角色，未细述结局", s:"极阴岛以元婴修士炼制的高阶炼尸，木土双灵根、怨气不灭；仅作背景设定。", rel:"魔道炼尸", camp:"极阴岛", race:"炼尸"},
  {n:"金身月尸", t:"化神级炼尸 · 金遁瞬移", cat:"lian", r:"十级炼尸（化神级）", e:"背景设定角色，未细述结局", s:"炼尸链顶端的化神级金身月尸，金遁瞬移、肉身坚不可摧；仅作背景设定。", rel:"无主炼尸", camp:"无", race:"炼尸"}
];
"""
anchor_data = "/* ===== 韩立境界时间轴 ===== */"
assert anchor_data in html, "数据锚点未找到"
html = html.replace(anchor_data, data_js + "\n" + anchor_data, 1)
print("1. 数据插入完成")

# ========== 2. 渲染函数（插入在启动之前） ==========
render_js = """
/* ===== 灵兽灵虫渲染 ===== */
let beastTab = "all";
function renderBeastRail(){
  const el = document.getElementById("beastRail");
  if(!el) return;
  el.innerHTML = BEAST_RAIL.map(function(r){
    return '<div class="beast-node"><b>' + esc(r.lv) + '</b><span class="bl">' + esc(r.realm) + '</span><span>' + esc(r.note) + '</span></div>';
  }).join("");
}
function renderBeastTabs(){
  const el = document.getElementById("beastTabs");
  if(!el) return;
  const cnt = function(id){ return id==="all" ? BEASTS.length : BEASTS.filter(function(b){return b.cat===id;}).length; };
  el.innerHTML = BEAST_CATS.map(function(c){
    return '<button class="beast-tab' + (c.id===beastTab ? " active" : "") + '" data-cat="' + c.id + '">' + esc(c.name) + '<span class="cnt">' + cnt(c.id) + '</span></button>';
  }).join("");
}
function renderBeasts(){
  const el = document.getElementById("beasts");
  if(!el) return;
  el.innerHTML = BEASTS.map(function(c){
    const safeName = escapeAttr(c.n || "");
    const safeTitle = escapeAttr(c.t || "");
    const fallbackLetter = escapeAttr(((c.n || "")[0]) || "?");
    const img = c.img
      ? '<img class="card-img" src="assets/' + escapeAttr(c.img) + '" alt="' + safeName + '" loading="lazy">'
      : '<div class="ph">' + fallbackLetter + '</div>';
    const cat = BEAST_CATS.find(function(x){return x.id===c.cat;}) || BEAST_CATS[0];
    return '<div class="card" data-name="' + safeName + '" data-aka="' + safeTitle + '" data-cat="' + c.cat + '">' +
      '<div class="card-top">' + img + '<span class="beast-cat-tag" style="color:' + cat.color + ';border-color:' + cat.color + '">' + esc(cat.name) + '</span></div>' +
      '<div class="card-body">' +
        '<div class="card-name"><h3>' + esc(c.n) + '</h3>' + (c.t?'<span class="aka">' + esc(c.t) + '</span>':"") + '</div>' +
        ((c.rel||c.camp||c.race)?'<div class="card-chips">' +
          (c.rel?'<span class="chip rel" title="归属">' + esc(c.rel) + '</span>':"") +
          (c.camp?'<span class="chip camp" title="来源势力">' + esc(c.camp) + '</span>':"") +
          (c.race?'<span class="chip race" title="种族">' + esc(c.race) + '</span>':"") +
        '</div>':"") +
        '<div class="card-row realm"><span class="lb">等级</span><span class="tx">' + esc(c.r) + '</span></div>' +
        '<div class="card-extra">' +
          '<div class="card-row"><span class="lb">结局</span><span class="tx">' + esc(c.e) + '</span></div>' +
          (c.ev?'<div class="card-row"><span class="lb">修为演进</span><span class="tx">' + esc(c.ev) + '</span></div>':"") +
          (c.s?'<div class="card-row"><span class="lb">生平</span><span class="tx">' + esc(c.s) + '</span></div>':"") +
        '</div>' +
        '<div class="card-hint"><span class="chev">▾</span>点击展开详情</div>' +
      '</div>' +
    '</div>';
  }).join("");
  el.querySelectorAll(".card-img").forEach(function(img){
    img.addEventListener("error", function(){
      const cardTop = img.parentElement;
      if (!cardTop || cardTop.querySelector(".ph")) return;
      cardTop.innerHTML = '<div class="ph">' + esc((img.alt || "?").charAt(0)) + '</div>' + cardTop.querySelector(".beast-cat-tag").outerHTML;
    });
  });
}
function applyBeastFilter(){
  const cards = document.querySelectorAll("#beasts .card");
  let visible = 0;
  cards.forEach(function(card){
    const show = beastTab==="all" || card.dataset.cat===beastTab;
    card.style.display = show ? "" : "none";
    if(show) visible++;
  });
  document.getElementById("beastEmpty").classList.toggle("show", visible===0);
}
document.getElementById("beastTabs").addEventListener("click", function(e){
  const btn = e.target.closest(".beast-tab");
  if(!btn) return;
  document.querySelectorAll(".beast-tab").forEach(function(t){t.classList.remove("active");});
  btn.classList.add("active");
  beastTab = btn.dataset.cat;
  applyBeastFilter();
});
document.getElementById("beasts").addEventListener("click", function(event){
  const card = event.target.closest(".card");
  if (!card) return;
  card.classList.toggle("open");
});

"""
anchor_render = "/* ===== 启动 ===== */"
assert anchor_render in html, "渲染锚点未找到"
html = html.replace(anchor_render, render_js + anchor_render, 1)
print("2. 渲染函数插入完成")

# ========== 3. 启动调用 ==========
old_boot = "renderTimeline();\nrenderTabs();\nrenderBars();\nrenderLegend();\nrenderMain();\napplyFilter();"
new_boot = old_boot + """
document.getElementById("beast-total").textContent = BEASTS.length;
document.getElementById("beast-img").textContent = new Set(BEASTS.filter(function(c){return c.img;}).map(function(c){return c.img;})).size;
renderBeastRail();
renderBeastTabs();
renderBeasts();
applyBeastFilter();"""
assert old_boot in html, "启动锚点未找到"
html = html.replace(old_boot, new_boot, 1)
print("3. 启动调用插入完成")

# ========== 4. 路由 VIEWS ==========
old_views = 'var VIEWS = ["v-chars","v-lore","v-realms"];'
new_views = 'var VIEWS = ["v-chars","v-lore","v-realms","v-beasts"];'
assert old_views in html, "VIEWS 锚点未找到"
html = html.replace(old_views, new_views, 1)
print("4. 路由更新完成")

io.open(P, "w", encoding="utf-8").write(html)
print("已写回 index.html")
