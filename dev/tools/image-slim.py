#!/usr/bin/env python3
"""图片瘦身：在「画质不降级」的前提下，逐图决定是否改用 WebP。

思路
----
WebP 并不总是比 JPEG 小。本仓库的图已在 2026-09-17 统一压过（长边 ≤800px / JPEG q76），
其中一部分已经接近无损，硬转 WebP 反而更大（实测最大 +13.7%）。

所以采取**逐图取最优**：每张图尝试若干 WebP 质量档，取「满足画质门槛 且 明显更小」的
最小档；没有档位达标的图就保留原 JPEG —— 最终是混合格式，但每张图都是它自己的最优解。

画质门槛（两条路径）
------------------
1. 有高清原图（git 历史 commit REF_COMMIT 里同名文件）：
   把原图 LANCZOS 降到当前尺寸当作参考 ref，门槛 = 当前 JPEG 相对 ref 的 SSIM − 0.002。
   即「WebP 不能比现在的 JPEG 更偏离真值」。
2. 历史里没有原图（如后来补的图）：门槛 = WebP 相对当前 JPEG 的 SSIM ≥ 0.99。
   即「WebP 必须是当前 JPEG 的高保真再编码」。

用法
----
    python3 dev/tools/image-slim.py --dry-run   # 只出报告，不动任何文件
    python3 dev/tools/image-slim.py --apply     # 落地：写 .webp、删 .jpg、改 index.html

报告写在 dev/_image-slim-report.json。
"""

from __future__ import annotations

import argparse
import io
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "public" / "assets"
INDEX = ROOT / "public" / "index.html"
REPORT = ROOT / "dev" / "_image-slim-report.json"

REF_COMMIT = "143a8c9"  # 瘦身前的提交：保留着高清原图
CANDIDATE_Q = (60, 66, 72, 78, 84)
SEARCH_METHOD = "4"  # 试档用较快的方法
FINAL_METHOD = "6"  # 最终编码用最慢（最省体积）的方法
SSIM_TOLERANCE = 0.002  # 相对 JPEG 允许的画质浮动
MIN_GAIN = 0.03  # 至少小 3% 才值得换格式，避免无意义改动


def ssim(a: np.ndarray, b: np.ndarray) -> float:
    """灰度图的 SSIM（8×8 均值窗，用积分图加速）。"""
    a = a.astype(np.float64)
    b = b.astype(np.float64)
    c1, c2 = (0.01 * 255) ** 2, (0.03 * 255) ** 2

    def box(x: np.ndarray, k: int = 8) -> np.ndarray:
        pad = k // 2
        xp = np.pad(x, ((pad, pad), (pad, pad)), mode="reflect")
        c = np.cumsum(np.cumsum(xp, 0), 1)
        c = np.pad(c, ((1, 0), (1, 0)))
        return (c[k:, k:] - c[:-k, k:] - c[k:, :-k] + c[:-k, :-k]) / (k * k)

    mu1, mu2 = box(a), box(b)
    s1, s2 = box(a * a) - mu1 * mu1, box(b * b) - mu2 * mu2
    s12 = box(a * b) - mu1 * mu2
    m = ((2 * mu1 * mu2 + c1) * (2 * s12 + c2)) / ((mu1**2 + mu2**2 + c1) * (s1 + s2 + c2))
    return float(m.mean())


def gray(im: Image.Image) -> np.ndarray:
    return np.asarray(im.convert("L"))


def git_show(path: str) -> bytes:
    r = subprocess.run(["git", "show", path], capture_output=True, cwd=ROOT)
    return r.stdout if r.returncode == 0 else b""


def encode_webp(src: Path, q: int, method: str, dst: Path) -> int:
    subprocess.run(
        ["cwebp", "-quiet", "-q", str(q), "-m", method, "-mt", str(src), "-o", str(dst)],
        check=True,
    )
    return dst.stat().st_size


def prepare_source(path: Path, name: str, tmpdir: Path, jpeg: Image.Image) -> tuple[Path, np.ndarray, float | None, str]:
    """产出「编码用的无损源 PNG」与「画质比较基准」。

    有高清原图（git 历史 REF_COMMIT）时，以「原图 LANCZOS 降到当前尺寸」为编码源 —— 与当初瘦身
    管线的输入等价，避免在已经压过的 JPEG 上二次编码（会同时损失画质和体积）。
    历史里没有的图，才退回拿当前 JPEG 当源，基准也随之变成 JPEG 自身。
    """
    w, h = jpeg.size
    src_png = tmpdir / f"{path.stem}.png"
    ref_src = git_show(f"{REF_COMMIT}:public/assets/{name}")
    if ref_src:
        ref = Image.open(io.BytesIO(ref_src)).convert("RGB").resize((w, h), Image.LANCZOS)
        ref.save(src_png)
        g_ref = gray(ref)
        return src_png, g_ref, ssim(g_ref, gray(jpeg)), "ref"
    jpeg.convert("RGB").save(src_png)
    return src_png, gray(jpeg), None, "jpeg"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="落地转换（默认只出报告）")
    ap.add_argument("--from-report", action="store_true", help="跳过分析，直接按已有报告落地（配 --apply）")
    args = ap.parse_args()

    decisions: list[dict] = []
    tmpdir = Path(tempfile.mkdtemp())
    files: list[Path] = []
    if args.from_report:
        if not REPORT.exists():
            print("没有报告可复用，请先跑一次 dry-run")
            return 1
        decisions = json.loads(REPORT.read_text(encoding="utf-8"))
        print(f"复用报告：{len(decisions)} 张\n", flush=True)
    else:
        files = sorted(p for p in ASSETS.iterdir() if p.suffix.lower() in {".jpg", ".jpeg"})
        if args.limit:
            files = files[: args.limit]
        print(f"待处理 {len(files)} 张，当前合计 {sum(p.stat().st_size for p in files) / 1e6:.1f} MB\n", flush=True)

    for i, path in enumerate(files, 1):
        name = path.name
        jbytes = path.stat().st_size
        jpeg = Image.open(path)
        src_png, cmp_ref, s_jpeg, mode = prepare_source(path, name, tmpdir, jpeg)
        bar = (s_jpeg - SSIM_TOLERANCE) if s_jpeg is not None else 0.99

        best = None
        for q in CANDIDATE_Q:
            out = tmpdir / f"q{q}.webp"
            n = encode_webp(src_png, q, SEARCH_METHOD, out)
            s = ssim(cmp_ref, gray(Image.open(out)))
            if s >= bar and (best is None or n < best[1]):
                best = (q, n, s)

        row = {
            "name": name,
            "jpeg_bytes": jbytes,
            "jpeg_ssim": round(s_jpeg, 4) if s_jpeg is not None else None,
            "mode": mode,
            "webp": None,
        }
        if best and best[1] < jbytes * (1 - MIN_GAIN):
            q, n, s = best
            row["webp"] = {"q": q, "bytes": n, "ssim_vs_ref": round(s, 4), "gain_pct": round(100 * (n - jbytes) / jbytes, 1)}
        decisions.append(row)

        if i % 25 == 0 or i == len(files):
            done = [d for d in decisions if d["webp"]]
            saved = sum(d["jpeg_bytes"] - d["webp"]["bytes"] for d in done)
            print(f"  {i}/{len(files)}  已定转换 {len(done)} 张，累计省 {saved / 1e6:.2f} MB", flush=True)

    convert = [d for d in decisions if d["webp"]]
    total_j = sum(d["jpeg_bytes"] for d in decisions)
    saved = sum(d["jpeg_bytes"] - d["webp"]["bytes"] for d in convert)
    after = total_j - saved
    print(f"\n=== 结果 ===")
    print(f"转换 {len(convert)} 张，保留 JPEG {len(decisions) - len(convert)} 张")
    print(f"图片合计 {total_j / 1e6:.1f} MB → {after / 1e6:.1f} MB ({100 * (after - total_j) / total_j:+.1f}%)")
    if convert:
        gains = sorted(d["webp"]["gain_pct"] for d in convert)
        print(f"单张收益：中位 {gains[len(gains) // 2]:+.1f}% / 最好 {gains[0]:+.1f}% / 最差 {gains[-1]:+.1f}%")

    REPORT.write_text(json.dumps(decisions, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"报告：{REPORT.relative_to(ROOT)}")

    if not args.apply:
        print("\n（dry-run，未改动文件；加 --apply 落地）")
        return 0

    # --- 落地 ---
    html = INDEX.read_text(encoding="utf-8")
    renamed: dict[str, str] = {}
    for d in convert:
        path = ASSETS / d["name"]
        stem = path.stem
        out = ASSETS / f"{stem}.webp"
        # ⚠️ 必须用与试档时相同的无损源，不能直接拿已压过的 JPEG 再编码
        src_png, _, _, _ = prepare_source(path, d["name"], tmpdir, Image.open(path))
        encode_webp(src_png, d["webp"]["q"], FINAL_METHOD, out)
        assert out.stat().st_size <= d["webp"]["bytes"] * 1.05, f"{stem}: 最终编码异常"
        renamed[d["name"]] = f"{stem}.webp"

    if renamed:
        pat = re.compile(
            r"(?<![A-Za-z0-9_.-])(" + "|".join(re.escape(n) for n in renamed) + r")(?![A-Za-z0-9])"
        )
        html, cnt = pat.subn(lambda m: renamed[m.group(1)], html)
        print(f"index.html 替换引用 {cnt} 处")

    for d in convert:
        (ASSETS / d["name"]).unlink()
    INDEX.write_text(html, encoding="utf-8")

    left = sorted(p.name for p in ASSETS.iterdir())
    print(f"落地完成：assets 现 {len(left)} 个文件（{sum(1 for n in left if n.endswith('.webp'))} webp / "
          f"{sum(1 for n in left if n.endswith('.jpg'))} jpg）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
