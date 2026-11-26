#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""sentence_splitter.py — 统一上下文感知断句器（V4.1）

acs.py / analyze.py / build_reader.py 共同调用，替代各自独立的正则分句。

设计原则：
- 小数字间的句点（3.14）不是句末；正负数、百分比、科学计数法（1.2e-3）同样保留。
- 已知缩写（Dr./e.g./i.e./et al./Fig. 等）后的句点按上下文处理。
- 版本号、网址、邮箱、IP 内部句点不断句。
- 全角标点（。！？；）与半角 (!?;) 仍正常断句；英文句点仅在“真正结束句子”时断句。
- 输出句子片段含精确区间 [start,end)，拼接后与原文逐字一致，不做 strip 破坏还原。

零依赖：仅 Python 标准库。
"""
import re
from collections import namedtuple

Span = namedtuple("Span", ["text", "start", "end"])

# ── 1. 先扫描“保护区间”：这些区间内的 . 不可能是句末 ──────────────

_PROTECTED_PATTERNS = [
    # 顺序敏感：先匹配更长更具体的模式
    re.compile(r"https?://[^\s]+", re.I),                    # 网址 http(s)
    re.compile(r"(?:mailto:)?[\w.+-]+@[\w-]+(?:\.[\w-]+)+"),  # 邮箱
    re.compile(r"(?<![\d.])(?:\d{1,3}\.){3}\d{1,3}(?![\d.])"),  # IPv4
    re.compile(r"(?<!\w)(?:[0-9a-fA-F]{1,4}:){2,7}[0-9a-fA-F]{1,4}(?!\w)"),  # IPv6 粗略
    re.compile(r"\d+(?:\.\d+)+(?:[a-zA-Z][\w.-]*)?"),         # 版本号 3.2.5 / 2.0.0-beta.1
]

# 数字：整数、小数、正负、百分比、科学计数法（前后可带 +/-）
_NUMBER = r"(?:[+-]?(?:\d+\.\d+|\d+)(?:[eE][+-]?\d+)?)"

_NUM_CTX = re.compile(
    r"(?<![\w.])" + _NUMBER + r"(?![\w.])"          # 裸数字/小数
)

# 已知缩写表：句点前为这些 token 时，是否句末取决于后续上下文
_ABBRS = {
    "dr", "mr", "mrs", "ms", "prof", "sr", "jr", "st",
    "e.g", "i.e", "cf", "vs", "etc", "al",          # et al. 的 al
    "fig", "eq", "no", "no.", "approx", "dept", "univ", "inc", "ltd", "co",
    "jan", "feb", "mar", "apr", "jun", "jul", "aug", "sep", "sept", "oct", "nov", "dec",
    "a.m", "p.m", "u.s", "u.k", "ph.d", "m.d",
}

_SENT_ENDS_FULLWIDTH = "。！？；"
_HALF_ENDS = "!?;"


def _merge(intervals):
    """合并重叠区间。"""
    if not intervals:
        return []
    intervals = sorted(intervals)
    out = [list(intervals[0])]
    for s, e in intervals[1:]:
        if s <= out[-1][1]:
            out[-1][1] = max(out[-1][1], e)
        else:
            out.append([s, e])
    return [tuple(x) for x in out]


def _protected_ranges(text):
    ranges = []
    for pat in _PROTECTED_PATTERNS:
        for m in pat.finditer(text):
            e = m.end()
            s = m.start()
            # trailing '.' followed by whitespace + sentence-start (uppercase letter) is not part of the number
            if text[s:e].endswith('.') and e - 1 > s:
                nxt, _ = _next_nonspace(text, e - 1)
                if nxt and (nxt.isupper() or not nxt.isascii()):
                    e = e - 1
            ranges.append((s, e))
    for m in _NUM_CTX.finditer(text):
        ranges.append((m.start(), m.end()))
    return _merge(ranges)


def _is_decimal_point(text, i):
    """text[i] == '.' 且两侧均为数字字符 → 小数/版本内部点。"""
    if i == 0 or i >= len(text) - 1:
        return False
    left = text[i - 1]
    right = text[i + 1]
    return (left.isdigit() and right.isdigit())


def _prev_word(text, i):
    j = i - 1
    while j >= 0 and (text[j].isalpha()):
        j -= 1
    raw = text[j + 1:i]
    # 支持带内点的缩写:向前扩展,把 e.g. / et al. / U.S. 之类整段取出
    k = j
    while k >= 0 and (text[k].isalpha() or text[k] == '.'):
        k -= 1
    raw2 = text[k + 1:i]
    # 若 raw2 以字母开头、以字母结尾、中间只含字母与点,且末尾不是单点(排除数字),取 raw2
    if raw2 and raw2[0].isalpha() and raw2[-1].isalpha():
        raw = raw2
    word = raw.lower()
    return word, (i - len(raw))


def _is_leading_decimal(text, i):
    """'.05' 形式的前置小数点：'.' 前非字母数字、后为数字。"""
    if not (i + 1 < len(text) and text[i + 1].isdigit()):
        return False
    if i == 0:
        return True
    prev = text[i - 1]
    return not (prev.isalnum() or prev == ".")


def _next_nonspace(text, i):
    """'.' 后第一个非空白字符及其索引。"""
    j = i + 1
    while j < len(text) and text[j] in " \t":
        j += 1
    if j >= len(text):
        return "", len(text)
    return text[j], j


def _in_ranges(pos, ranges):
    lo, hi = 0, len(ranges)
    while lo < hi:
        mid = (lo + hi) // 2
        s, e = ranges[mid]
        if pos < s:
            hi = mid
        elif pos >= e:
            lo = mid + 1
        else:
            return True
    return False


def _sentence_end_here(text, i, ranges):
    """判断位置 i 的标点是否为句子终点。text[i] 已是候选标点。"""
    ch = text[i]
    if ch in _SENT_ENDS_FULLWIDTH:
        # 全角问号/叹号后跟全角引号等收尾标点的情况在主循环处理
        return True
    if ch in _HALF_ENDS:
        # 半角 !?; 后若是字母数字前有空格 → 结束（5!5 之类无空格不断）
        nxt, _ = _next_nonspace(text, i)
        if nxt and (nxt.isalnum() or nxt in "\"'”"):
            # ! 直接贴着下一个词（如 "really!Next"）罕见，保守判断为结束
            prev = text[i - 1] if i > 0 else ""
            if prev and not prev.isspace():
                return True
            return True
        return True
    if ch == ".":
        if _in_ranges(i, ranges):
            return False
        if _is_decimal_point(text, i):
            return False
        # 前置小数点 .05 → 非句末
        if _is_leading_decimal(text, i):
            return False
        # 连续句点：省略号/句点群
        if i + 1 < len(text) and text[i + 1] == ".":
            return False  # 由省略号处理逻辑在主循环统一收尾
        word, wstart = _prev_word(text, i)
        nxt, npos = _next_nonspace(text, i)
        # 行尾 → 句末
        if not nxt:
            return True
        # 缩写判定：前词在缩写表
        if word in _ABBRS:
            # 中文等非拉丁字符紧随 → 非句末
            if nxt and not nxt.isascii():
                return False
            # 缩写 + 小写字母开头 → 不是句末（Dr. Smith 除外：人名首字母大写）
            if nxt.islower():
                return False
            if word in ("mr", "mrs", "ms", "dr", "prof", "sr", "jr", "st"):
                # Dr. Smith → 非句末（人名）
                return False
            # e.g. We → 多为句末（etc. 后大写常为句末）
            if word in ("e.g", "i.e", "cf", "vs", "etc", "al"):
                # et al. Next 大写 → 句末；e.g. This → 常仍是列举,保守非句末
                return True if word in ("etc", "al") else False
            return False
        # 单字母大写词（人名首字母 "J."）后跟大写词 → 非句末
        if len(word) == 1 and len(text[wstart:i]) == 1 and text[wstart].isupper():
            return False
        # 数字结尾（“ended at 3.”）→ 句末
        if i > 0 and text[i - 1].isdigit():
            if not _in_ranges(i - 1, ranges):
                # “3.” 且 3 不在保护区间 → 普通句末数字
                nxtc = nxt
                if nxtc and (nxtc.isupper() or nxtc.isdigit() or not nxtc.isalpha()):
                    return True
                return True
        # 普通单词 + 空格 + 大写/数字/引号 → 句末
        if nxt.isupper() or nxt.isdigit() or nxt in "(\"'“":
            return True
        if nxt.islower():
            # 词. 小写 → 多为缩写（未登录），保守不断句
            return False
        return True
    return False


def split_sentences_spans(text):
    """主入口：返回 [Span(text,start,end)]，按原文顺序、含终点标点。

    拼接所有 span.text == text（当无跳过空白时）。
    本函数不修改任何字符；句子含尾随空格时由调用方决定 strip。
    """
    if not text:
        return []
    ranges = _protected_ranges(text)
    n = len(text)
    spans = []
    start = 0
    i = 0
    while i < n:
        ch = text[i]
        # 收尾标点跟随：句末标点后紧跟的收尾符号（引号/括号）并入当前句
        if ch in _SENT_ENDS_FULLWIDTH + "!?.;":
            # 省略号群
            if ch == "." and i + 1 < n and text[i + 1] == ".":
                j = i
                while j < n and text[j] == ".":
                    j += 1
                # 省略号后按整体处理：判断 j-1 处是否句末（省略号视为句末标点群）
                # 中文省略号…… 直接整体结束
                nxt, _ = _next_nonspace(text, j - 1)
                is_end = True if (j - i) >= 3 else _sentence_end_here(text, j - 1, ranges)
                if is_end:
                    # 吸收后随收尾标点
                    k = j
                    while k < n and text[k] in "\"'”’）)":
                        k += 1
                    spans.append(Span(text[start:k], start, k))
                    start = k
                i = j
                continue
            if ch in "…" + _SENT_ENDS_FULLWIDTH + "!?;" or (ch == "." and _sentence_end_here(text, i, ranges)):
                # 检查是否真句末
                if ch in _SENT_ENDS_FULLWIDTH:
                    end = True
                elif ch in "!?;":
                    end = True
                else:
                    end = _sentence_end_here(text, i, ranges)
                if end:
                    k = i + 1
                    # 吸收收尾引号/括号
                    while k < n and text[k] in "\"'”’）)":
                        k += 1
                    # 吸收尾随空格之外不吞并下一句内容：保留标点后直接切
                    spans.append(Span(text[start:k], start, k))
                    start = k
                i += 1 if ch not in "…" else 1
                continue
        i += 1
    if start < n:
        spans.append(Span(text[start:n], start, n))
    return spans


def split_sentences(text):
    """兼容旧接口：返回句子文本列表（含终点标点），strip 空白句。

    保证："".join(spans 未 strip 版) 与原文逐字一致。
    """
    spans = split_sentences_spans(text)
    out = []
    for sp in spans:
        t = sp.text
        if t.strip():
            out.append(t)
    # 不 strip 内容本身，保留原始空格（定位需要）；仅在输出层做可见性过滤
    return out or ([text] if text else [])


def split_sentences_stripped(text):
    """旧调用方使用的形态：句子已 strip，仍可通过区间还原。"""
    return [sp.text.strip() for sp in split_sentences_spans(text) if sp.text.strip()] or ([text.strip()] if text.strip() else [])


if __name__ == "__main__":
    import json
    samples = [
        "The result was 3.14.",
        "The p-value was 0.05, not 0.5.",
        "The temperature dropped to -2.75°C.",
        "The value was 1.2e-3.",
        "Version 3.2.5 was released.",
        "Dr. Smith reported the result.",
        "The difference was significant (p < 0.001).",
        "The experiment ended at 3. The next began at 4.",
        "The average score increased from 3.14 to 4.25. This difference was significant (p = 0.03).",
        "See https://example.com/page.html for details. Contact admin@example.org for help.",
        "例如 Dr. Lee 测得 3.14 与 0.5。这很重要！e.g. 值 1.2e-3 保留。",
    ]
    result = {}
    for s in samples:
        spans = split_sentences_spans(s)
        joined = "".join(sp.text for sp in spans)
        result[s] = {
            "sentences": [sp.text for sp in spans if sp.text.strip()],
            "count": len([sp for sp in spans if sp.text.strip()]),
            "roundtrip_ok": joined == s,
        }
    print(json.dumps(result, ensure_ascii=False, indent=2))
