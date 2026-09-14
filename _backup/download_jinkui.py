# -*- coding: utf-8 -*-
"""下载金魁动画形象图到 assets/。"""
import urllib.request, os, ssl

url = "https://aka.doubaocdn.com/s/0HLpZkJmjF"
dst = r"C:\Users\lizhe\OneDrive\我的工作文档\BunnyChen.github.io\docs\docs\Other\fanren-characters\assets\jinkui_luanxing.jpg"

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
with urllib.request.urlopen(req, context=ctx, timeout=30) as resp:
    data = resp.read()
with open(dst, "wb") as f:
    f.write(data)
print(f"下载完成: {dst} ({len(data)} bytes)")
