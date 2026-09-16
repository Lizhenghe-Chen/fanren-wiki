#!/usr/bin/env python3
"""批量更新 index.html：为 BEASTS 条目添加 img 字段，并更新 .asset-manifest"""
import re

HTML = "/Users/bunnychen/Documents/GitProjects/Lizhenghe-Chen.github.io/docs/docs/Other/fanren-characters/index.html"

# 生物名 -> 图片文件名映射（花石老祖跳过）
BEAST_IMGS = {
    "云翅鸟": "yunchiniao.jpg",
    "金背妖螂": "jinbeiyaolang.jpg",
    "土甲龙": "tujialong.jpg",
    "豹鳞兽": "baolinshou.jpg",
    "墨小白": "moxiaobai.jpg",
    "精炎童子": "jingyantongzi.jpg",
    "九曲灵参": "jiuqulingshen.jpg",
    "婴鲤兽": "yinglishou.jpg",
    "雷鹏": "leipeng.jpg",
    "天奎狼王": "tiankuilangwang.jpg",
    "火须子": "huoxuzi.jpg",
    "游天鲲鹏": "youtiankunpeng.jpg",
    "罗睺": "luohou.jpg",
    "离火麒麟": "lihuuoqilin.jpg",
    "五光孔雀": "wuguangkongque.jpg",
    "金乌": "jinwu.jpg",
    "天凤（彩凤）": "tianfeng.jpg",
    "真龙（金龙）": "zhenlong.jpg",
    "玄武": "xuanwu.jpg",
    "烛九阴": "zhujiuyin.jpg",
    "天都妖尸": "tianduyaoshi.jpg",
    "尸魈": "shixiao.jpg",
    "金身月尸": "jinshenyueshi.jpg",
}

with open(HTML, "r", encoding="utf-8") as f:
    content = f.read()

original = content
updated_count = 0

# 为每个 BEASTS 条目添加 img 字段
# 匹配模式：{n:"名字", ... , e:"...", s:"  -> 在 s: 前插入 img:"xxx.jpg",
for beast_name, img_file in BEAST_IMGS.items():
    # 构建匹配：找到包含 n:"名字" 的行，在该行的 s:" 前插入 img
    # 使用正则匹配该行
    pattern = re.compile(
        r'(\{n:"' + re.escape(beast_name) + r'"[^}]*?)(, s:")'
    )
    replacement = r'\1, img:"' + img_file + r'", s:"'
    new_content, count = pattern.subn(replacement, content)
    if count > 0:
        content = new_content
        updated_count += 1
        print(f"  ✅ {beast_name} -> {img_file}")
    else:
        print(f"  ❌ {beast_name} -> 未匹配到！")

print(f"\nBEASTS img 字段更新: {updated_count}/{len(BEAST_IMGS)}")

# 更新 .asset-manifest：在最后一个 url() 后添加新文件
# 找到 manifest 结束位置（在 ;} 之前）
new_files = sorted(BEAST_IMGS.values())
manifest_addition = "  " + ", ".join([f'url("assets/{f}")' for f in new_files]) + ",\n"

# 在 manifest 的最后一行（url("assets/ziling.jpg"), 或类似）之后插入
# 找到 .asset-manifest 块中最后一个 url() 行
manifest_end_pattern = re.compile(
    r'(url\("assets/mojiao\.jpg"\), url\("assets/liuyishuangwu\.jpg"\), url\("assets/xueyuzhizhu\.jpg"\), url\("assets/shuangtongshu\.jpg"\),\n)(;})'
)
if manifest_end_pattern.search(content):
    content = manifest_end_pattern.sub(
        r'\1' + manifest_addition + r'\2', content
    )
    print(f"asset-manifest: 已添加 {len(new_files)} 个新文件")
else:
    print("⚠️ 未找到 manifest 结束位置，尝试备用匹配...")
    # 备用：在 ;} 前的最后一个 url 行后添加
    alt_pattern = re.compile(
        r'(url\("assets/shuangtongshu\.jpg"\),\n)(;})'
    )
    if alt_pattern.search(content):
        content = alt_pattern.sub(
            r'\1' + manifest_addition + r'\2', content
        )
        print(f"asset-manifest (备用): 已添加 {len(new_files)} 个新文件")
    else:
        print("❌ asset-manifest 更新失败！")

# 写回
if content != original:
    with open(HTML, "w", encoding="utf-8") as f:
        f.write(content)
    print("\n✅ index.html 已更新")
else:
    print("\n⚠️ 内容未变化")
