#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, re, sys

base = "/Users/bunnychen/Library/CloudStorage/OneDrive-Personal/我的工作文档/BunnyChen.github.io/docs/docs/Other/fanren-characters"
stories = {}
for f in ["stories1.json", "stories2.json", "stories3.json"]:
    with open(f"{base}/_backup/{f}", encoding="utf-8") as fh:
        stories.update(json.load(fh))

html = open(f"{base}/index.html", encoding="utf-8").read()

# 逐章节处理
total_matched, total_missing = 0, []
for key, sdict in stories.items():
    m = re.search(r'(DATA\.' + key + r' = \[)(.*?)(\];)', html, re.S)
    if not m:
        print(f"[WARN] chapter block not found: {key}")
        continue
    body = m.group(2)
    # 切分每条记录
    items = re.split(r'(?<=\}),\s*(?=\{)', body)
    out_items = []
    for it in items:
        it = it.strip()
        nm = re.search(r'n:"([^"]*)"', it)
        if not nm:
            out_items.append(it)
            continue
        name = nm.group(1)
        name_key = name.replace(" ", "")
        if name_key in sdict:
            s = sdict[name_key].replace('"', "'").replace("\\", "\\\\")
            # 在记录末尾 } 前插入 , s:"..."
            it = it.rstrip()
            assert it.endswith("}"), f"record not ending with }}: {it[-80:]}"
            it = it[:-1].rstrip()
            if it.endswith(","):
                it = it[:-1].rstrip()
            it += f', s:"{s}"' + "}"
            total_matched += 1
        else:
            total_missing.append(f"{key}/{name}")
        out_items.append(it)
    new_body = ",\n  ".join(out_items)
    html = html[:m.start(2)] + new_body + html[m.end(2):]

open(f"{base}/index.html", "w", encoding="utf-8").write(html)
print(f"matched: {total_matched}")
print(f"missing ({len(total_missing)}): {total_missing}")
