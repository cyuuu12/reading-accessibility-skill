#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
acs.py — 注意力成本分（ACS）计算器
零依赖，仅用 Python 标准库。

ACS = 40·S_sentence + 25·S_vocab + 15·S_pronoun + 10·S_nest + 10·S_line
详见 references/attention_model.md

用法:
    python acs.py <文本文件>
    python acs.py -              # 从 stdin 读
    echo "文本" | python acs.py -
输出: JSON
"""
import sys
import json
import re

# ---------------------------------------------------------------------------
# 3500 常用字表：用 GB2312 一级字库（3755 个常用汉字）作为零依赖近似来源。
# GB2312 一级字库即国家常用汉字集，覆盖《现代汉语常用字表》3500 字的绝大部分。
# ---------------------------------------------------------------------------
def build_common_chars():
    chars = set()
    for lead in range(0xB0, 0xD8):          # GB2312 一级常用字库 0xB0A1..0xD7FE（3755 字，近似3500常用字表）
        for trail in range(0xA1, 0xFF):
            try:
                ch = bytes([lead, trail]).decode("gb2312")
            except UnicodeDecodeError:
                continue
            if '\u4e00' <= ch <= '\u9fff':
                chars.add(ch)
    return chars

COMMON_CHARS = build_common_chars()

# 句子切分：。！？；
SENT_SPLIT = re.compile(r'[。！？；]')
# 代词
PRONOUNS = ['它', '它们', '其', '该', '此', '这', '那', '上述', '本人', '自己', '他', '她', '他们', '她们']
# 嵌套标记
NEST_MARKERS = ['因为', '所以', '虽然', '但是', '尽管', '可是', '既然', '如果', '若', '只要', '只有', '无论']
# 限定/条件/否定（供 fidelity_check 用，此处仅注释）


def clamp(x, lo=0.0, hi=1.0):
    return max(lo, min(hi, x))


def split_segments(text):
    """按空行分段；无空行则整篇为一段。"""
    raw = re.split(r'\n\s*\n', text.strip())
    segs = [s.strip() for s in raw if s.strip()]
    if not segs:
        segs = [text.strip()]
    return segs


def split_sentences(seg):
    parts = SENT_SPLIT.split(seg)
    return [p.strip() for p in parts if p.strip()]


def score_sentence(seg, sents):
    if not sents:
        return 0.0
    avg_len = sum(len(s) for s in sents) / len(sents)
    return clamp((avg_len - 15) / 25)


def score_vocab(seg):
    chars = [c for c in seg if '\u4e00' <= c <= '\u9fff']
    if not chars:
        return 0.0
    oov = sum(1 for c in chars if c not in COMMON_CHARS)
    ratio = oov / len(chars)
    return clamp(ratio / 0.10)


def score_pronoun(seg):
    max_dist = 0
    for p in PRONOUNS:
        idx = 0
        while True:
            pos = seg.find(p, idx)
            if pos < 0:
                break
            # 先行词距离：向前找最近的中文字，距离=pos-前一个词末尾
            back = seg[:pos]
            # 取前 60 字窗口内最近非空字距离
            dist = 0
            for j in range(pos - 1, -1, -1):
                dist += 1
                if '\u4e00' <= seg[j] <= '\u9fff':
                    break
                if dist > 60:
                    break
            if dist > max_dist:
                max_dist = dist
            idx = pos + len(p)
    return clamp(max_dist / 60)


def score_nest(seg):
    depth = 0
    # 括号层级
    cur = 0
    for c in seg:
        if c in '（(':
            cur += 1
            depth = max(depth, cur)
        elif c in '）)':
            cur = max(0, cur - 1)
    # 从句标记
    marker_count = sum(seg.count(m) for m in NEST_MARKERS)
    depth = max(depth, min(marker_count, 4))
    return clamp((depth - 1) / 3)


def score_line(seg, limit=40):
    lines = seg.split('\n')
    total = sum(len(l) for l in lines)
    if total == 0:
        return 0.0
    over = sum(max(0, len(l) - limit) for l in lines)
    return clamp((over / total) / 0.20)


def segment_acs(seg):
    sents = split_sentences(seg)
    s1 = score_sentence(seg, sents)
    s2 = score_vocab(seg)
    s3 = score_pronoun(seg)
    s4 = score_nest(seg)
    s5 = score_line(seg)
    acs = 40 * s1 + 25 * s2 + 15 * s3 + 10 * s4 + 10 * s5   # 权重和=100，s∈[0,1] → ACS∈[0,100]
    return {
        "acs": round(acs),
        "detail": {
            "sentence": round(s1, 3),
            "vocab": round(s2, 3),
            "pronoun": round(s3, 3),
            "nest": round(s4, 3),
            "line": round(s5, 3),
        },
    }


def analyze(text):
    segs = split_segments(text)
    results = []
    for i, s in enumerate(segs, 1):
        r = segment_acs(s)
        r["seg_no"] = i
        r["chars"] = len(s)
        results.append(r)
    mean_acs = round(sum(r["acs"] for r in results) / len(results)) if results else 0
    return {
        "segments": results,
        "mean_acs": mean_acs,
        "suggest_split": mean_acs > 45,
        "common_chars_size": len(COMMON_CHARS),
    }


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    path = sys.argv[1]
    if path == '-':
        text = sys.stdin.read()
    else:
        with open(path, 'r', encoding='utf-8') as f:
            text = f.read()
    out = analyze(text)
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
