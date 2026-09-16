# -*- coding: utf-8 -*-
import io, re
s = io.open('../index.html', encoding='utf-8').read()
src = io.open('add_person_ev.py', encoding='utf-8').read()
ev_src = src[src.find('EV = {'):src.find('def esc')]
ns = {}; exec(ev_src, ns); EV = ns["EV"]

def esc(ev):
    return ev.replace('\\', '\\\\').replace('"', '\\"')

total = 0
