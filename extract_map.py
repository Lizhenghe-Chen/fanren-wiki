"""
v9: 修正版 - 只优化边缘，不改原图色彩
1. AI mask + 洪水填充清理背景
2. 只对alpha通道做边缘锐化/抗锯齿
3. 保留极西之地和慕蘭草原
"""
import cv2
import numpy as np
from rembg import remove

# ⚠️ 源图：public/assets/tiannan-map.png（3840×2160 高清原图）已于 2026-10-13 换成
# public/assets/tiannan-map.webp（2400px）以减体积；重跑本脚本前先用
# `git show <sha>:public/assets/tiannan-map.png > <路径>` 取回高清原图，再把 INPUT 指过去。
INPUT = r"D:\GitProjects\fanren-wiki\public\assets\tiannan-map.png"
OUTPUT = r"D:\GitProjects\fanren-wiki\public\assets\tiannan-map-cutout.png"

img = cv2.imread(INPUT, cv2.IMREAD_COLOR)
h, w = img.shape[:2]
print(f"Image size: {w}x{h}")

# === 1. AI 抠图 ===
print("Running rembg...")
result_rgba = remove(img)
ai_mask = result_rgba[:, :, 3]

# === 2. 定向洪水填充去背景 ===
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
sat = hsv[:, :, 1]

flood_mask = np.zeros((h + 2, w + 2), np.uint8)
flood_img = img.copy()

edge_points = []
for x in range(0, w, 3):
    edge_points.append((x, 0))      # 上
    edge_points.append((x, h - 1))  # 下
for y in range(0, h, 3):
    edge_points.append((w - 1, y))  # 右
# 左边只取上半部分，保留下半部分的极西之地
for y in range(0, int(h * 0.65), 3):
    edge_points.append((0, y))

lo_diff = (40, 40, 40)
hi_diff = (40, 40, 40)

for (x, y) in edge_points:
    if sat[y, x] < 90:
        cv2.floodFill(flood_img, flood_mask, (x, y), (0, 0, 255),
                      lo_diff, hi_diff,
                      cv2.FLOODFILL_MASK_ONLY | (255 << 8))

bg_from_flood = flood_mask[1:h+1, 1:w+1]

# === 3. 组合 ===
combined = cv2.bitwise_and(ai_mask, cv2.bitwise_not(bg_from_flood))
warm_fg = (sat > 35).astype(np.uint8) * 255
combined = cv2.bitwise_or(combined, warm_fg)

# === 4. 形态学清理 ===
kernel_close = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))
kernel_open = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
combined = cv2.morphologyEx(combined, cv2.MORPH_CLOSE, kernel_close, iterations=2)
combined = cv2.morphologyEx(combined, cv2.MORPH_OPEN, kernel_open, iterations=2)

# === 5. 保留最大连通域 ===
num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(combined, connectivity=8)
print(f"Components: {num_labels}")
if num_labels > 1:
    areas = stats[1:, cv2.CC_STAT_AREA]
    largest = 1 + np.argmax(areas)
    print(f"Largest: {areas.max()} px ({areas.max()/(h*w)*100:.1f}%)")
    main_mask = (labels == largest).astype(np.uint8) * 255
else:
    main_mask = combined

# === 6. 边缘处理（只针对alpha通道，不动RGB） ===
# 轻微腐蚀去毛边
kernel_erode = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))
main_mask = cv2.erode(main_mask, kernel_erode, iterations=1)
# 抗锯齿平滑
main_mask = cv2.GaussianBlur(main_mask, (3, 3), 0.7)

# === 7. 输出（原图RGB不动） ===
result = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)
result[:, :, 3] = main_mask

# 裁剪
coords = cv2.findNonZero(main_mask)
x, y, cw, ch = cv2.boundingRect(coords)
pad = 10
x0 = max(0, x - pad)
y0 = max(0, y - pad)
x1 = min(w, x + cw + pad)
y1 = min(h, y + ch + pad)
cropped = result[y0:y1, x0:x1]

cv2.imwrite(OUTPUT, cropped, [cv2.IMWRITE_PNG_COMPRESSION, 3])
print(f"Saved: {OUTPUT}")
print(f"Cropped: {x1-x0}x{y1-y0}")
