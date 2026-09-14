#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, re

base = "/Users/bunnychen/Library/CloudStorage/OneDrive-Personal/我的工作文档/BunnyChen.github.io/docs/docs/Other/fanren-characters"
meta = {}
for f in ["meta1.json", "meta2.json", "meta3.json"]:
    with open(f"{base}/_backup/{f}", encoding="utf-8") as fh:
        meta.update(json.load(fh))
ev = json.load(open(f"{base}/_backup/ev.json", encoding="utf-8"))
ev = {k.replace(" ", ""): v for k, v in ev.items()}

html = open(f"{base}/index.html", encoding="utf-8").read()
chapters = ["qixuanmen", "huangfeng", "luanxing", "dajin", "lingjie", "xianjie"]

def esc(s):
    return s.replace('"', "'").replace("\\", "\\\\")

total = 0
for key in chapters:
    m = re.search(r'(DATA\.' + key + r' = \[)(.*?)(\];)', html, re.S)
    body = m.group(2)
    items = re.split(r'(?<=\}),\s*(?=\{)', body)
    out = []
    for it in items:
        it = it.strip()
        nm = re.search(r'n:"([^"]*)"', it)
        if not nm:
            out.append(it)
            continue
        nk = nm.group(1).replace(" ", "")
        extra = []
        if nk in meta.get(key, {}):
            md = meta[key][nk]
            extra.append(f'rel:"{esc(md["rel"])}"')
            extra.append(f'camp:"{esc(md["camp"])}"')
            extra.append(f'race:"{esc(md["race"])}"')
        if nk in ev:
            extra.append(f'ev:"{esc(ev[nk])}"')
        if extra:
            it = it.rstrip()
            assert it.endswith("}"), it[-60:]
            it = it[:-1].rstrip()
            if it.endswith(","):
                it = it[:-1].rstrip()
            it += ", " + ", ".join(extra) + "}"
            total += 1
        out.append(it)
    html = html[:m.start(2)] + ",\n  ".join(out) + html[m.end(2):]

open(f"{base}/index.html", "w", encoding="utf-8").write(html)
print(f"updated records: {total}")
