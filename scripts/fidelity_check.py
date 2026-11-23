#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fidelity_check.py — 保真校验（V2.0）
零依赖。对比原文与改写后文本，检查：
  数字 / 单位 / 否定 / 限定 / 条件 / 因果 / 比较 / 数量范围
并报告无法自动确认的部分（不确定性），不一律声称 100% 保真。

用法:
    python fidelity_check.py <原文> <改写后>
输出: JSON + 人读摘要
"""
import sys
import json
import re
from collections import Counter

# 数字：阿拉伯数字序列、中文数字、百分数
NUM_RE = re.compile(r'\d+(?:\.\d+)?%?|[零一二三四五六七八九十百千万亿]+')

UNITS = ['mg', 'g', 'kg', 'ml', 'L', 'mm', 'cm', 'm', 'km', '秒', '分', '时', '日',
         '天', '周', '月', '年', '次', '粒', '片', '支', '瓶', '盒', '克', '毫克',
         '毫升', '升', '个', '人', '元', '角', '度', '倍', '‰']

NEGATIONS = ['不', '没', '无', '非', '未', '勿', '别', '莫', '否', '免', '禁', '防止', '避免', '拒绝', '停止']

LIMITERS = ['仅', '只', '仅限', '唯有', '唯一', '必须', '务必', '不得', '不可', '不能',
            '不超过', '不少于', '至少', '至多', '最多', '最少', '上限', '下限', '限']

CONDITIONS = ['如果', '若', '假如', '倘若', '只要', '只有', '除非', '否则', '一旦', '当']

CAUSALS = ['因为', '所以', '由于', '因此', '因而', '之所以', '导致', '引起', '故']

COMPARISONS = ['比', '相比', '相对', '高于', '低于', '大于', '小于', '等于', '不如', '更', '最']

# 数量范围：数字+单位 组合（如 40mg、30分钟）—— 抽取"数字+紧邻单位"片段
RANGE_RE = re.compile(r'(\d+(?:\.\d+)?%?)\s*(mg|g|kg|ml|L|mm|cm|m|km|秒|分|时|日|天|周|月|年|次|粒|片|支|瓶|盒|克|毫克|毫升|升|个|人|元|度|倍)')


def extract_all(text):
    return {
        "numbers": NUM_RE.findall(text),
        "units": [u for u in UNITS for _ in range(text.count(u))],
        "negations": [n for n in NEGATIONS for _ in range(text.count(n))],
        "limiters": [l for l in LIMITERS for _ in range(text.count(l))],
        "conditions": [c for c in CONDITIONS for _ in range(text.count(c))],
        "causals": [c for c in CAUSALS for _ in range(text.count(c))],
        "comparisons": [c for c in COMPARISONS for _ in range(text.count(c))],
        "ranges": RANGE_RE.findall(text),
    }


def multiset_diff(a, b):
    ca, cb = Counter(a), Counter(b)
    missing = {}
    extra = {}
    for k, v in ca.items():
        lack = v - cb.get(k, 0)
        if lack > 0:
            missing[k] = lack
    for k, v in cb.items():
        ex = v - ca.get(k, 0)
        if ex > 0:
            extra[k] = ex
    return missing, extra


def check(original, rewritten):
    o = extract_all(original)
    r = extract_all(rewritten)
    details = {}
    all_ok = True
    for key in o:
        miss, extra = multiset_diff(o[key], r[key])
        ok = not miss
        if not ok:
            all_ok = False
        orig_n = len(o[key])
        fidelity = 1.0 if orig_n == 0 else round(1 - sum(miss.values()) / orig_n, 3)
        details[key] = {
            "original_count": orig_n,
            "rewritten_count": len(r[key]),
            "missing": miss,
            "added": extra,
            "fidelity": fidelity,
            "ok": ok,
        }
    # 不确定性：以下无法仅靠关键词计数自动确认，须人工复核
    uncertainty = [
        "语义等价性（关键词计数相同不保证语义相同）",
        "因果方向是否保持（因/果是否颠倒）",
        "比较对象是否一致（'A 比 B 高' 是否被改为 'B 比 A 低'）",
        "条件与结论的对应关系是否保持",
        "范围边界是否含等号（'不超过' vs '小于'）",
    ]
    return {
        "all_fidelity": all_ok,
        "details": details,
        "uncertainty": uncertainty,
        "summary": summarize(details, all_ok, uncertainty),
    }


def summarize(details, all_ok, uncertainty):
    lines = []
    for k, v in details.items():
        status = "✓ 保真" if v["ok"] else f"✗ 缺失 {v['missing']}"
        if v["added"]:
            status += f"  新增 {v['added']}"
        lines.append(f"- {k}: {status}（原文{v['original_count']} / 改写{v['rewritten_count']}）")
    lines.append("")
    lines.append("未自动验证（须人工复核）：")
    for u in uncertainty:
        lines.append(f"  · {u}")
    return "\n".join(lines)


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    with open(sys.argv[1], 'r', encoding='utf-8') as f:
        original = f.read()
    with open(sys.argv[2], 'r', encoding='utf-8') as f:
        rewritten = f.read()
    out = check(original, rewritten)
    print(json.dumps(out, ensure_ascii=False, indent=2))
    print("\n—— 人读摘要 ——")
    print(out["summary"])
    print("\n结论：", "关键词级保真通过；但存在未自动验证项，请人工复核后再发布。" if out['all_fidelity'] else "存在关键词缺失，请逐条回滚核对；另有未自动验证项。")


if __name__ == '__main__':
    main()
