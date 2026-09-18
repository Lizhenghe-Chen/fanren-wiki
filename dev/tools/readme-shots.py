#!/usr/bin/env python3
"""README 宣传图准备：把站点原始截图压成适合 README 展示的图片。

约定
----
- 原始截图放在 `image/README/`（体积大、是整页长图，本地保留，不入库）
- 加工结果写到 `image/README/shots/`（入库，README 只引用这一份）
- 逐图决策记录写在 `dev/_readme-shots-report.json`

为什么不用 dev/tools/image-slim.py
--------------------------------
那份脚本是给 `public/assets/` 的角色图做「逐图取最优（JPEG/WebP 择优 + SSIM 门槛）」的，
依赖 numpy 且绑定 git 历史里的高清原图；README 宣传图是一次性的截图加工，目标不同
（统一宽度、统一格式、便于手工挑选），所以单独成篇。

用法
----
    python3 dev/tools/readme-shots.py --contact dev/_contact.jpg   # 拼联络表，挑图/定名用
    python3 dev/tools/readme-shots.py --dry-run                    # 只打印计划
    python3 dev/tools/readme-shots.py --apply                      # 落地到 shots/

依赖：Pillow（仅此一个）。
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "image" / "README"
OUT = SRC / "shots"
REPORT = ROOT / "dev" / "_readme-shots-report.json"

# 源文件名 → 输出名 → 裁切起点（占原图高的比例）
# 顺序即 README 中的展示顺序。原始截图是**整页长图**（最长 1249×3377），
# 整张塞进 README 会拖出几个屏幕的空滚，所以统一裁成 16:10 横幅，
# 起点按各视图「最有信息量的那一段」人工指定（见下方注释）。
SHOTS: list[tuple[str, str, float]] = [
    ("屏幕截图_18-9-2026_21518_bunnychen.top.jpeg", "01-home.webp", 0.00),       # hero + 统计 + 旭日图
    ("屏幕截图_18-9-2026_215342_bunnychen.top.jpeg", "02-characters.webp", 0.105),  # 人物关系图谱
    ("屏幕截图_18-9-2026_215353_bunnychen.top.jpeg", "03-lore.webp", 0.06),        # 境界演进时间轴 + 故事脉络
    ("屏幕截图_18-9-2026_21540_bunnychen.top.jpeg", "04-realms.webp", 0.09),       # 十三境总览 + 实力解构
    ("屏幕截图_18-9-2026_215424_bunnychen.top.jpeg", "05-beasts.webp", 0.08),      # 妖兽等级制度 + 分类
    ("屏幕截图_18-9-2026_215454_bunnychen.top.jpeg", "06-herbs.webp", 0.08),       # 灵药年份等级 + 分类
    ("屏幕截图_18-9-2026_215514_bunnychen.top.jpeg", "07-treasures.webp", 0.08),   # 法宝品阶体系 + 分类
]

CROP_ASPECT = 10 / 16  # 裁成 16:10（高/宽）；--no-crop 可关掉

EXT = (".jpeg", ".jpg", ".png", ".webp")
BG = (14, 16, 22)      # 与站点 --bg 一致，联络表底色
INK = (233, 228, 216)  # 与站点 --ink 一致
GOLD = (212, 175, 106)


def font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for p in (
        "C:/Windows/Fonts/msyh.ttc",
        "C:/Windows/Fonts/simhei.ttf",
        "/System/Library/Fonts/PingFang.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    ):
        if Path(p).exists():
            try:
                return ImageFont.truetype(p, size)
            except OSError:
                pass
    return ImageFont.load_default()


def sources() -> list[Path]:
    return sorted(p for p in SRC.iterdir() if p.is_file() and p.suffix.lower() in EXT)


def contact(path: Path, cols: int = 4, cell: int = 420) -> None:
    """把全部原图缩成缩略图拼成一张联络表：便于一次看全、决定取舍与命名。"""
    files = sources()
    if not files:  # 已加工过：退回看 shots/
        files = sorted(p for p in OUT.iterdir() if p.is_file()) if OUT.exists() else []
    rows = (len(files) + cols - 1) // cols
    lab_h, pad = 34, 10
    sheet = Image.new("RGB", (cols * cell + pad * (cols + 1), rows * (cell + lab_h) + pad * (rows + 1)), BG)
    d = ImageDraw.Draw(sheet)
    f_lab = font(18)
    for i, f in enumerate(files):
        im = Image.open(f).convert("RGB")
        w0, h0 = im.size
        im.thumbnail((cell, cell * 2), Image.LANCZOS)
        r, c = divmod(i, cols)
        x = pad + c * (cell + pad)
        y = pad + r * (cell + lab_h + pad)
        d.text((x, y), f"{i + 1}. {f.name}  ({w0}×{h0}, {f.stat().st_size // 1024}KB)",
               font=f_lab, fill=GOLD)
        sheet.paste(im, (x, y + lab_h))
    sheet.save(path, quality=88, optimize=True)
    print(f"联络表 → {path}  ({sheet.width}×{sheet.height}, {len(files)} 张)")


def crop_box(w: int, h: int, y_frac: float, crop: bool) -> tuple[int, int, int, int]:
    """按比例取一条 16:10 横幅（起点为原图高的 y_frac），并夹在原图范围内。"""
    if not crop:
        return (0, 0, w, h)
    ch = round(w * CROP_ASPECT)
    y0 = min(max(0, round(h * y_frac)), max(0, h - ch))
    return (0, y0, w, min(h, y0 + ch))


def plan(max_w: int, crop: bool = True) -> list[dict]:
    rows = []
    for src_name, out_name, y_frac in SHOTS:
        p = SRC / src_name
        if not p.exists():
            rows.append({"src": src_name, "error": "源文件不存在"})
            continue
        with Image.open(p) as im:
            w, h = im.size
        bx0, by0, bx1, by1 = crop_box(w, h, y_frac, crop)
        cw, chh = bx1 - bx0, by1 - by0
        scale = min(1.0, max_w / cw)
        rows.append({
            "src": src_name,
            "out": out_name,
            "src_size": [w, h],
            "crop": [bx0, by0, bx1, by1],
            "crop_frac": round(by0 / h, 3),
            "out_size": [round(cw * scale), round(chh * scale)],
            "src_kb": round(p.stat().st_size / 1024, 1),
        })
    return rows


def apply(max_w: int, quality: int, method: int, crop: bool = True) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    report = []
    for row in plan(max_w, crop):
        if "error" in row:
            print(f"  跳过 {row['src']}：{row['error']}")
            continue
        im = Image.open(SRC / row["src"]).convert("RGB")
        im = im.crop(tuple(row["crop"]))
        if im.width > max_w:
            im = im.resize((max_w, round(im.height * max_w / im.width)), Image.LANCZOS)
        dst = OUT / row["out"]
        im.save(dst, "WEBP", quality=quality, method=method)
        kb = dst.stat().st_size / 1024
        row["out_kb"] = round(kb, 1)
        row["saved"] = f"{100 - kb / row['src_kb'] * 100:.0f}%"
        report.append(row)
        print(f"  {row['out']:<18} {row['src_kb']:>6}KB → {row['out_kb']:>5}KB  (-{row['saved']:>4})"
              f"  {im.width}×{im.height}  裁切起点 y={row['crop_frac']:.0%}")
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    total = sum(r["out_kb"] for r in report)
    print(f"\n{len(report)} 张，合计 {total / 1024:.2f}MB → {OUT}\n报告 → {REPORT}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--contact", type=Path, help="拼联络表到指定路径")
    ap.add_argument("--apply", action="store_true", help="写出 shots/")
    ap.add_argument("--max-w", type=int, default=1440, help="长边目标宽度（默认 1440，够 2x 屏）")
    ap.add_argument("--quality", type=int, default=80, help="WebP 质量（默认 80）")
    ap.add_argument("--method", type=int, default=6, help="WebP 压缩方法 0-6（默认 6，最省体积）")
    ap.add_argument("--no-crop", action="store_true", help="保留整页长图，不裁 16:10")
    a = ap.parse_args()
    crop = not a.no_crop

    if a.contact:
        contact(a.contact)
    if a.apply:
        apply(a.max_w, a.quality, a.method, crop)
    if not a.contact and not a.apply:
        for r in plan(a.max_w, crop):
            print(r)


if __name__ == "__main__":
    main()
