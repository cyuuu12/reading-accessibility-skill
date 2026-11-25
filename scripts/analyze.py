#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
analyze.py — 统一处理层（V2.3.2）

三层分工：
- Agent（宿主模型）：根据全文上下文判断语义功能与阅读优先级，按 schema 输出结构化分析。
- Python（本模块）：原文切分、数据结构、边界校验、保真校验、结果整合、诊断统计。
- HTML：只呈现与交互，不重新判断语义重要性。

无 LLM 语义分析时 → 保守模式：全文按原文呈现，不贴标签，不折叠。

零依赖。
"""
import re

_SENT_SPLIT = re.compile(r'([。！？；.!?])')


def split_sentences(text):
    """按全角/半角句末标点切句，保留原标点。"""
    parts = _SENT_SPLIT.split(text)
    out, buf = [], ""
    for p in parts:
        if not p:
            continue
        if _SENT_SPLIT.fullmatch(p):
            buf += p
            if buf.strip():
                out.append(buf)
            buf = ""
        else:
            if buf.strip():
                out.append(buf)
            buf = p
    if buf.strip():
        out.append(buf)
    return [s.strip() for s in out if s.strip()] or [text.strip()]


def split_paragraphs(text):
    return [s.strip() for s in re.split(r'\n\s*\n', text.strip()) if s.strip()]


def _nonws(s):
    return re.sub(r'\s', '', s)


# ── 保守模式 ──────────────────────────────────────
def _conservative_route(text, paras, high_risk=False):
    """无 LLM 语义分析时：全文按原文呈现，不贴标签，不折叠。"""
    segments = []
    for i, p in enumerate(paras, 1):
        sents = split_sentences(p)
        segments.append({
            "seg_no": i,
            "priority": None,          # 无标签
            "role": None,
            "reason": None,
            "preview": None,
            "original": p,
            "sentences": sents,
            "blocks": [{"text": p, "role": None, "priority": None,
                        "sentences": sents, "preview": None}],
            "foldable": False,
        })
    return {
        "title": "阅读辅助",
        "mode": "完整阅读" if high_risk else "聚焦阅读",
        "high_risk": high_risk,
        "modules": [],
        "segments": segments,
        "original_text": text,
        "conservative": True,
        "_meta": {"goal": "general", "diagnostic": None, "problem_paras": []},
    }


# ── Agent 分析结果校验 ────────────────────────────
def _validate_blocks(blocks, original):
    """校验三硬约束：
    1. 每个 block 的 text 能在原文中精确定位
    2. block 之间互不重叠
    3. 全部 block 覆盖原文无遗漏（非空白字符一致）
    返回 (ok, problem_msg)
    """
    if not blocks:
        return False, "无 block"
    # 约束1：每个 block.text 能在原文中找到
    pos = 0
    spans = []
    for b in blocks:
        bt = b.get("text", "").strip()
        if not bt:
            return False, "空 block"
        idx = original.find(bt, pos)
        if idx < 0:
            # 从头找
            idx = original.find(bt)
            if idx < 0:
                return False, f"block 无法定位: {bt[:20]}..."
        spans.append((idx, idx + len(bt)))
        pos = idx + len(bt)
    # 约束2：不重叠
    spans.sort()
    for j in range(1, len(spans)):
        if spans[j][0] < spans[j - 1][1]:
            return False, "block 重叠"
    # 约束3：覆盖完整（非空白字符一致）
    covered = _nonws("".join(b.get("text", "") for b in blocks))
    if covered != _nonws(original):
        return False, "block 未覆盖全文"
    return True, None


# ── 语义块构建（合并相邻同类句） ──────────────────
def _build_blocks_from_analysis(paragraph, analysis_blocks):
    """从 Agent 分析结果构建语义块；emphasis 随后统一校验。"""
    blocks = []
    for b in analysis_blocks:
        text = b.get("text", "").strip()
        sents = split_sentences(text)
        blocks.append({
            "text": text,
            "role": b.get("role", "陈述"),
            "priority": b.get("priority", "速览"),
            "sentences": sents,
            "preview": b.get("preview"),
            "emphasis": b.get("emphasis") or [],
        })
    return blocks


def _sanitize_emphasis(blocks, full_text):
    """校验并裁剪局部强调，不影响正文或阅读策略。

    区间为相对 block.text 的 Python 字符区间 [start, end)。非法、越界、
    原文不匹配、重叠、单处超 15 字者丢弃；每块按 score 至多保留 3 处，
    全文再按 score 截断到非空白正文字符的 5%。返回诊断，不阻断输出。
    """
    diagnostics = {"accepted": 0, "characters": 0, "limit": 0,
                   "dropped": [], "ratio": 0.0}
    total_chars = len(_nonws(full_text))
    budget = int(total_chars * 0.05)
    diagnostics["limit"] = budget
    candidates = []
    for bi, block in enumerate(blocks):
        text = block.get("text", "")
        raw = block.get("emphasis") or []
        if not isinstance(raw, list):
            diagnostics["dropped"].append({"block": bi, "reason": "emphasis_not_list"})
            raw = []
        for ei, item in enumerate(raw):
            base = {"block": bi, "item": ei}
            if not isinstance(item, dict):
                diagnostics["dropped"].append(dict(base, reason="invalid_item"))
                continue
            start, end = item.get("start"), item.get("end")
            if (not isinstance(start, int) or isinstance(start, bool)
                    or not isinstance(end, int) or isinstance(end, bool)
                    or start < 0 or end <= start or end > len(text)):
                diagnostics["dropped"].append(dict(base, reason="invalid_span"))
                continue
            fragment = text[start:end]
            if item.get("text") is not None and item["text"] != fragment:
                diagnostics["dropped"].append(dict(base, reason="text_mismatch"))
                continue
            if len(fragment) > 15:
                diagnostics["dropped"].append(dict(base, reason="over_15_chars"))
                continue
            try:
                score = float(item.get("score", 0))
            except (TypeError, ValueError):
                score = 0.0
            candidates.append({"start": start, "end": end, "text": fragment,
                               "score": score, "block": bi, "item": ei,
                               "length": len(_nonws(fragment))})

    kept = []
    for bi, block in enumerate(blocks):
        mine = sorted((c for c in candidates if c["block"] == bi),
                      key=lambda c: (-c["score"], c["start"], c["item"]))
        block_kept = []
        for c in mine:
            reason = None
            if len(block_kept) >= 3:
                reason = "over_3_per_block"
            elif any(c["start"] < k["end"] and k["start"] < c["end"]
                     for k in block_kept):
                reason = "overlap"
            if reason:
                diagnostics["dropped"].append({"block": bi, "item": c["item"],
                                               "reason": reason})
            else:
                block_kept.append(c)
                kept.append(c)

    selected = []
    used = 0
    for c in sorted(kept, key=lambda c: (-c["score"], c["block"], c["start"])):
        if used + c["length"] <= budget:
            selected.append(c)
            used += c["length"]
        else:
            diagnostics["dropped"].append({"block": c["block"], "item": c["item"],
                                           "reason": "over_5_percent"})
    for block in blocks:
        block["emphasis"] = []
    for c in sorted(selected, key=lambda c: (c["block"], c["start"], c["end"])):
        blocks[c["block"]]["emphasis"].append({
            "start": c["start"], "end": c["end"], "text": c["text"],
            "score": c["score"]})
    diagnostics["accepted"] = len(selected)
    diagnostics["characters"] = used
    diagnostics["ratio"] = round(used / total_chars, 5) if total_chars else 0.0
    return diagnostics


def _merge_adjacent_skip_blocks(blocks):
    """合并相邻的跳读块（同主题），减少折叠按钮数量。
    跨主题的跳读块不合并（role 不同时不合并）。"""
    if not blocks:
        return blocks
    merged = [blocks[0]]
    for b in blocks[1:]:
        prev = merged[-1]
        if (prev["priority"] == "跳读" and b["priority"] == "跳读"
                and prev["role"] == b["role"]):
            # 合并
            prev["text"] = prev["text"] + b["text"]
            prev["sentences"] = prev["sentences"] + b["sentences"]
            if prev.get("preview") and b.get("preview"):
                prev["preview"] = prev["preview"]  # 保留第一个预览
        else:
            merged.append(b)
    return merged


# ── 段级策略聚合 ──────────────────────────────────
def _seg_priority_from_blocks(blocks):
    pris = [b["priority"] for b in blocks if b["priority"]]
    if "精读" in pris:
        return "精读"
    if "速览" in pris:
        return "速览"
    if "跳读" in pris:
        return "跳读"
    return None


# ── 诊断统计（不阻断） ────────────────────────────
def _diagnostic(segments):
    """统计精读占比、段内切分率、单标签整段占比、问题段落。不阻断输出。"""
    total, focus = 0, 0
    for seg in segments:
        n = len(_nonws(seg["original"]))
        total += n
        if seg["priority"] == "精读":
            focus += n
    ratio = focus / total if total else 0
    n_blocks = sum(len(s["blocks"]) for s in segments)
    n_sents = sum(len(s.get("sentences", [])) for s in segments)
    return {
        "focus_ratio": round(ratio, 3),
        "focus_ratio_exceeded": ratio > 0.6,
        "total_blocks": n_blocks,
        "total_sentences": n_sents,
        "merge_effective": n_blocks < n_sents if n_sents > 0 else False,
    }


# ── 模块化理解框架 ────────────────────────────────
def _build_modules(segments):
    seen, modules = set(), []
    for seg in segments:
        for b in seg["blocks"]:
            role = b.get("role")
            if not role or role in seen:
                continue
            seen.add(role)
            modules.append({"title": role, "content": b["text"][:60] + ("…" if len(b["text"]) > 60 else "")})
    return modules[:6]


# ── 主入口 ────────────────────────────────────────
def route_text(text, goal="general", high_risk=False, analysis=None):
    """统一处理入口。

    参数:
      text: 原文
      goal: 阅读目标（完整阅读/聚焦阅读/快速浏览），影响块合并边界与优先级
      high_risk: 高风险文本（默认完整阅读，不折叠）
      analysis: Agent 语义分析结果（dict），按 routing.md schema。
                None 时退回保守模式。

    返回 dict，供 build_reader.py 和 Markdown 共用。
    """
    paras = split_paragraphs(text)

    # 无 Agent 分析 → 保守模式
    if analysis is None:
        return _conservative_route(text, paras, high_risk)

    # 有 Agent 分析 → 构建语义块 + 校验
    analysis_blocks = analysis.get("blocks", [])
    segments = []
    problem_paras = []

    # 按 para_idx 分组
    para_blocks = {}
    for b in analysis_blocks:
        pi = b.get("para_idx", 0)
        para_blocks.setdefault(pi, []).append(b)

    for i, p in enumerate(paras, 1):
        pblocks_raw = para_blocks.get(i - 1, [])
        if not pblocks_raw:
            # 该段无分析 → 保守
            sents = split_sentences(p)
            segments.append({
                "seg_no": i, "priority": None, "role": None, "reason": None,
                "preview": None, "original": p, "sentences": sents,
                "blocks": [{"text": p, "role": None, "priority": None,
                            "sentences": sents, "preview": None}],
                "foldable": False,
            })
            problem_paras.append(i)
            continue

        # 校验
        ok, msg = _validate_blocks(pblocks_raw, p)
        if not ok:
            # 重试一次：用原文整段作为单块
            sents = split_sentences(p)
            segments.append({
                "seg_no": i, "priority": None, "role": None, "reason": None,
                "preview": None, "original": p, "sentences": sents,
                "blocks": [{"text": p, "role": None, "priority": None,
                            "sentences": sents, "preview": None}],
                "foldable": False,
            })
            problem_paras.append(i)
            continue

        # 构建语义块
        blocks = _build_blocks_from_analysis(p, pblocks_raw)
        blocks = _merge_adjacent_skip_blocks(blocks)
        pri = _seg_priority_from_blocks(blocks)
        sents = split_sentences(p)

        # foldable: 仅跳读块可折叠
        has_skip = any(b["priority"] == "跳读" for b in blocks)
        segments.append({
            "seg_no": i,
            "priority": pri,
            "role": blocks[0].get("role") if blocks else None,
            "reason": None,  # V2.3: 不显示判断理由
            "preview": blocks[0].get("preview") if blocks else None,
            "original": p,
            "sentences": sents,
            "blocks": blocks,
            "foldable": has_skip,
        })

    all_blocks = [b for seg in segments for b in seg["blocks"]]
    emphasis_diagnostic = _sanitize_emphasis(all_blocks, text)
    diagnostic = _diagnostic(segments)
    diagnostic["emphasis"] = emphasis_diagnostic
    modules = _build_modules(segments)
    mode = "完整阅读" if high_risk else (goal if goal in ("完整阅读", "聚焦阅读", "快速浏览") else "聚焦阅读")

    return {
        "title": "阅读辅助",
        "mode": mode,
        "high_risk": high_risk,
        "modules": modules,
        "segments": segments,
        "original_text": text,
        "conservative": False,
        "_meta": {"goal": goal, "diagnostic": diagnostic, "problem_paras": problem_paras},
    }


if __name__ == "__main__":
    import sys, json
    if len(sys.argv) < 2:
        print("用法: analyze.py input.txt [analysis.json]  →  输出 JSON")
        sys.exit(1)
    with open(sys.argv[1], 'r', encoding='utf-8') as f:
        txt = f.read()
    analysis = None
    if len(sys.argv) >= 3:
        with open(sys.argv[2], 'r', encoding='utf-8') as f:
            analysis = json.load(f)
    print(json.dumps(route_text(txt, analysis=analysis), ensure_ascii=False, indent=2))
