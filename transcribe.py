import re
import json

from collections import Counter


def reverse(d):
    d_reversed = {v: k for k, v in d.items()}
    return d_reversed

def upper(d):
    d_upper = {}
    for k, v in d.items():
        if k in l2s_base:
            d_upper[k.upper()] = f"·{v}"
        else:
            d_upper[f"·{k}"] = v.upper()
    return d_upper

with open("base.json", "r", encoding="utf-8") as f:
    l2s_base = json.load(f)
    s2l_base = reverse(l2s_base)

with open("reform.json", "r", encoding="utf-8") as f:
    l2s_reform = json.load(f)
    s2l_reform = reverse(l2s_reform)

L2S = [upper(l2s_reform), upper(l2s_base), l2s_reform, l2s_base]
S2L = [upper(s2l_reform), upper(s2l_base), s2l_reform, s2l_base]

def detect_ws(text):
    counter = Counter(text)
    shavian_counter, latin_counter = 0, 0
    for k, v in l2s_base.items():
        latin_counter += counter[k]
        shavian_counter += counter[v]
    ws = "shavian" if shavian_counter >= latin_counter else "latin"
    return ws

def substitute(text, d):
    for k, v in d.items():
        text = re.sub(k, v, text)
    return text

def latinise(text):
    for step in S2L:
        text = substitute(text, step)
    return text

def shavise(text):
    for step in L2S:
        text = substitute(text, step)
    return text
