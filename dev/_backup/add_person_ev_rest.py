# -*- coding: utf-8 -*-
"""补写后3篇（dajin/lingjie/xianjie）人物 ev"""
import io, re
s = io.open('/Users/bunnychen/Documents/GitProjects/Lizhenghe-Chen.github.io/docs/docs/Other/fanren-characters/index.html', encoding='utf-8').read()
src = io.open('/Users/bunnychen/Documents/GitProjects/Lizhenghe-Chen.github.io/docs/docs/Other/fanren-characters/_backup/add_person_ev.py', encoding='utf-8').read()
ev_src = src[src.find('EV = {'):src.find('def esc')]
ns = {}; exec(ev_src, ns); EV = ns['EV']

def esc(ev):
    return ev.replace('\\', '\\\\').replace('"', '\\"')

total = 0
for key in ['dajin', 'lingjie', 'xianjie']:
    evmap = EV[key]
    anchor = f'DATA.{key} = ['
    st = s.find(anchor)
    arr_start = st + len(anchor)
    p = s.find('\n];', arr_start)
    if p < 0:
        print('结尾未找到', key); continue
    arr_end = p + 2
    seg = s[arr_start:arr_end]
    def cb(m, evmap=evmap):
        raw = m.group(0)
        nm = re.search(r'\bn:"([^"]*)"', raw)
        if not nm: return raw
        ev = evmap.get(nm.group(1))
        if ev is None: return raw
        if re.search(r'\bev:"', raw): return raw
        rm = re.search(r'(\br:"(?:[^"\\]|\\.)*")', raw)
        if rm:
            return raw[:rm.end()] + ',ev:"' + esc(ev) + '"' + raw[rm.end():]
        return raw[:1] + 'ev:"' + esc(ev) + '",' + raw[1:]
    before = seg.count('ev:"')
    newseg = re.sub(r'\{n:.*?(?=\n  \{n:|\];)', cb, seg, flags=re.S)
    after = newseg.count('ev:"')
    s = s[:arr_start] + newseg + s[arr_end:]
    print(f'{key}: ev {before}->{after} (+{after-before})')
    total += after - before

io.open('/Users/bunnychen/Documents/GitProjects/Lizhenghe-Chen.github.io/docs/docs/Other/fanren-characters/index.html', 'w', encoding='utf-8').write(s)
print('后3篇新增:', total)
