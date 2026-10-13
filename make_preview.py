import cv2
img = cv2.imread(r"D:\GitProjects\fanren-wiki\public\assets\tiannan-map-cutout.png", cv2.IMREAD_UNCHANGED)
h, w = img.shape[:2]
scale = 800 / w
small = cv2.resize(img, (800, int(h*scale)))
cv2.imwrite(r"D:\GitProjects\fanren-wiki\preview-cutout.png", small)
print("preview saved")
