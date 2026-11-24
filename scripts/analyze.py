#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
analyze.py — 统一处理层（V2.2）

原文输入 → 语义结构分析 → 阅读策略分配（段内语义单元）→ 60% 上限自检 → 保真校验

HTML 阅读器、Markdown 输出、宿主原生组件共用本模块的同一份分析结果，
避免各端各自执行不同内容处理逻辑。

零依赖。可被 build_reader.py --from-text 和 Markdown 生成逻辑共同调用。
"""
import re

# ── 切句 ──────────────────────────────────────────
_SENT_SPLIT = re.compile(r'([。！？；.!?])')


def split_sentences(text):
    """按全角/半角句末标点切句，保留原标点，不替换不补加。"""
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


# ── 段落切分 ──────────────────────────────────────
def split_paragraphs(text):
    """按空行分段，保留顺序。"""
    return [s.strip() for s in re.split(r'\n\s*\n', text.strip()) if s.strip()]


# ── 段内语义单元 ──────────────────────────────────
# 语义单元 = 段内按"论点/例证/限定/过渡"切出的句组
# 边界优先落在句号、分号、转折词处；最小一句，最长不超过整段。

_TRANSITION_WORDS = ("然而", "但是", "不过", "另一方面", "反之", "尽管如此")
_DEFINE_MARKERS = ("是指", "称为", "叫做", "指的是", "定义为", "是通过")
_CONDITION_MARKERS = ("如果", "只有", "除非", "前提是", "条件下", "当且仅当")
_CONCLUSION_MARKERS = ("因此", "所以", "表明", "说明", "可见", "由此", "综上", "总之")
_EXAMPLE_MARKERS = ("例如", "比如", "譬如", "实例", "英译本中")
_LIMIT_MARKERS = ("其弊端", "弊端", "局限", "不足", "缺陷", "代价", "然而", "但是")


def _classify_unit(unit, idx_in_seg, n_units, is_last, is_intro_seg=False):
    """对单个语义单元分类，返回 (role, priority, reason)。
    语义功能优先，关键词仅辅助。"""
    u = unit.strip()

    # 限定/反例/弊端 — 重点读
    for w in _LIMIT_MARKERS:
        if w in u:
            return "限定", "重点读", "指出局限或反例，影响结论成立条件。"
    # 条件 — 重点读
    for w in _CONDITION_MARKERS:
        if w in u:
            return "条件", "重点读", "给出必要条件，略过会漏推理前提。"
    # 定义/概念 — 重点读
    for w in _DEFINE_MARKERS:
        if w in u:
            return "定义", "重点读", "概念定义，是后续分析基础。"
    # 结论 — 重点读
    for w in _CONCLUSION_MARKERS:
        if w in u:
            return "结论", "重点读", "核心结论或推理结果。"
    # 举例 — 简单读
    for w in _EXAMPLE_MARKERS:
        if w in u:
            return "例证", "简单读", "举例说明，可速览。"
    # 过渡 — 简单读
    for w in _TRANSITION_WORDS:
        if w in u:
            return "过渡", "简单读", "过渡或转折，可速览。"

    # 位置启发：仅前两段（引言/理论）段首为论点→重点读；其余段首→简单读
    if idx_in_seg == 0 and n_units > 1 and is_intro_seg:
        return "论点", "重点读", "引言论点，提出全文主旨。"
    if is_last and n_units > 2:
        return "收束", "简单读", "段末收束，可速览。"

    return "陈述", "简单读", "支撑性陈述，可速览。"


def split_semantic_units(paragraph, seg_idx=0):
    """将一个自然段切为若干语义单元（句组）。
    最小一句，最长整段。按句切分后逐句分类，相邻同类可合并（简化：逐句为单元）。"""
    is_intro_seg = seg_idx < 2
    sents = split_sentences(paragraph)
    if len(sents) <= 1:
        # 单句段：短句默认速览，含高价值标记才精读
        u0 = sents[0]
        role, pri, reason = _classify_unit(u0, 0, 1, True, is_intro_seg)
        if pri == "重点读":
            return [{"text": u0, "role": role, "priority": "重点读", "reason": reason}]
        return [{"text": u0, "role": "陈述", "priority": "简单读", "reason": "单句段，可速览。"}]
    units = []
    n = len(sents)
    for i, s in enumerate(sents):
        role, pri, reason = _classify_unit(s, i, n, i == n - 1, is_intro_seg)
        units.append({"text": s, "role": role, "priority": pri, "reason": reason})
    return units


# ── 段级策略聚合 ──────────────────────────────────
def _seg_priority_from_units(units):
    """段级策略由段内单元聚合：含重点读单元→重点读；否则取最高。"""
    pris = [u["priority"] for u in units]
    if "重点读" in pris:
        return "重点读"
    if "简单读" in pris:
        return "简单读"
    return "可略读"


# ── 60% 上限自检 ──────────────────────────────────
def _nonws_len(s):
    return len(re.sub(r'\s', '', s))


def _check_focus_ratio(segments, threshold=0.6):
    """重点读非空白字符超过 threshold 视为路由失败，返回 True。"""
    total, focus = 0, 0
    for seg in segments:
        n = _nonws_len(seg["original"])
        total += n
        if seg["priority"] == "重点读":
            focus += n
    if total == 0:
        return False
    return focus / total > threshold


def _demote_for_ratio(segments):
    """路由失败回退：将"段首论点"类重点读降为简单读，保留定义/条件/结论/限定。"""
    for seg in segments:
        if seg["priority"] != "重点读":
            continue
        # 保留真正高价值的单元
        keep_focus = any(u["role"] in ("定义", "条件", "结论", "限定") for u in seg["units"])
        if not keep_focus:
            seg["priority"] = "简单读"
            seg["reason"] = "经上限自检降级：支撑性内容，可速览。"
            for u in seg["units"]:
                if u["role"] not in ("定义", "条件", "结论", "限定"):
                    u["priority"] = "简单读"


# ── 模块化理解框架 ────────────────────────────────
def _build_modules(segments):
    """按语义功能组织模块（理解框架，不替代正文）。"""
    role_map = {"定义": "理论依据", "论点": "核心问题", "结论": "核心结论",
                "限定": "方法局限", "条件": "前提条件", "例证": "实例说明",
                "过渡": "过渡", "陈述": "补充说明", "收束": "收束"}
    seen, modules = set(), []
    for seg in segments:
        for u in seg["units"]:
            title = role_map.get(u["role"], "补充")
            if title in seen:
                continue
            seen.add(title)
            modules.append({"title": title, "content": u["text"][:60] + ("…" if len(u["text"]) > 60 else "")})
    return modules[:6]  # 不固定数量，上限 6


# ── 主入口 ────────────────────────────────────────
def route_text(text, goal="general", high_risk=False, force_full_read=False):
    """统一处理：原文 → 语义结构分析 → 策略分配 → 60% 自检 → 结构化结果。

    返回 dict，可被 build_reader.py 和 Markdown 生成逻辑共用。
    """
    paras = split_paragraphs(text)
    segments = []
    for i, p in enumerate(paras, 1):
        units = split_semantic_units(p, seg_idx=i - 1)
        pri = _seg_priority_from_units(units)
        # 可略读启发：纯例证/过渡段
        if pri == "简单读" and all(u["role"] in ("例证", "过渡", "收束") for u in units):
            pri = "可略读"
        foldable = pri in ("可略读", "简单读")
        segments.append({
            "seg_no": i,
            "priority": pri,
            "reason": units[0]["reason"] if units else "",
            "skip_note": "略过会少了解支撑性内容，不影响核心结论。" if pri == "可略读" else None,
            "original": p,
            "sentences": [u["text"] for u in units],
            "units": units,
            "foldable": foldable,
        })

    # 60% 上限自检（高风险/强制全文精读/条款式不适用）
    ratio_exceeded = False
    if not high_risk and not force_full_read and _check_focus_ratio(segments):
        ratio_exceeded = True
        _demote_for_ratio(segments)

    modules = _build_modules(segments)
    mode = "完整阅读" if high_risk else "聚焦阅读"

    return {
        "title": "阅读辅助",
        "mode": mode,
        "high_risk": high_risk,
        "modules": modules,
        "segments": segments,
        "_meta": {"ratio_exceeded": ratio_exceeded, "goal": goal},
    }


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("用法: analyze.py input.txt  →  输出 JSON 分析结果")
        sys.exit(1)
    with open(sys.argv[1], 'r', encoding='utf-8') as f:
        txt = f.read()
    import json
    print(json.dumps(route_text(txt), ensure_ascii=False, indent=2))
