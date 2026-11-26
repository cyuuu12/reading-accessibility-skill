#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""media.py — 结构化媒体数据接口与校验（V4.1）

定义图片/表格/公式/公式的统一数据形态,供宿主 Agent 填充、analyze.py 校验、
reader_template.html 渲染。内容类型(kind)与语义角色(role)、阅读优先级(priority)
三者独立:图片不等于跳读,公式不等于精读。

零依赖,仅标准库。
"""
import re

KINDS = {"text", "image", "table", "formula"}

# 公式源形态
FORMULA_FORMS = {"latex_inline", "latex_block", "mathml", "unicode"}


def normalize_media_block(raw):
    """规范化一个媒体/公式块。返回 (block, error)。

    block 携带 kind 与载体字段;error 非空时调用方应回退为文本并记录。
    """
    out = dict(raw)
    kind = out.get("kind")
    if kind not in KINDS:
        return out, "unknown kind: %r" % (kind,)

    if kind == "image":
        src = out.get("src")
        if not src:
            return out, "image without src"
        # 只允许 data: URI 或本地相对路径,禁止运行时联网
        if not (src.startswith("data:image/") or _is_relative_path(src)):
            return out, "image src must be data URI or relative path"
        out.setdefault("alt", "")
        out.setdefault("caption", None)

    elif kind == "table":
        rows = out.get("rows")
        if not isinstance(rows, list) or not rows or not all(isinstance(r, list) for r in rows):
            return out, "table rows must be list of lists"
        header = out.get("header")
        if header is not None and (not isinstance(header, list)):
            return out, "table header must be list or null"
        out.setdefault("caption", None)

    elif kind == "formula":
        form = out.get("form")
        if form not in FORMULA_FORMS:
            return out, "formula form must be one of %s" % (sorted(FORMULA_FORMS),)
        src = out.get("latex") or out.get("mathml") or out.get("text")
        if not src:
            return out, "formula without source"
        out.setdefault("alt", None)

    return out, None


def _is_relative_path(src):
    if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", src) or src.startswith("//"):
        return False
    if re.match(r"^[a-zA-Z]:[\\/]", src) or src.startswith("/"):
        return False
    return bool(re.match(r"^[\w./~-]+$", src))


def latex_to_mathml(latex):
    """极小 LaTeX→MathML 转换器,只覆盖常见结构;无法转换时返回 None。

    支持:^ 上标 _ 下标 \frac{}{} \sqrt{} 希腊字母 \pm \times \cdot \int \sum
    常见二元关系 = < > \le \ge \ne \approx。不做完整 LaTeX 解析;
    不确定时返回 None,由调用方回退为可复制原始文本。
    """
    if latex is None or not latex.strip():
        return None
    if "\\begin{align" in latex or "&" in latex:
        return None  # 多行对齐公式暂不转换,走回退路径
    pos = [0]
    src = latex.strip()

    greek = {
        "alpha": "α", "beta": "β", "gamma": "γ", "delta": "δ", "epsilon": "ε",
        "zeta": "ζ", "eta": "η", "theta": "θ", "iota": "ι", "kappa": "κ",
        "lambda": "λ", "mu": "μ", "nu": "ν", "xi": "ξ", "pi": "π", "rho": "ρ",
        "sigma": "σ", "tau": "τ", "phi": "φ", "chi": "χ", "psi": "ψ", "omega": "ω",
        "Gamma": "Γ", "Delta": "Δ", "Theta": "Θ", "Lambda": "Λ", "Pi": "Π",
        "Sigma": "Σ", "Phi": "Φ", "Psi": "Ψ", "Omega": "Ω",
    }
    ops = {"pm": "±", "times": "×", "cdot": "·", "le": "≤", "ge": "≥",
           "ne": "≠", "approx": "≈", "infty": "∞", "propto": "∝"}
    fences = {"left": "", "right": ""}

    def parse_group():
        """读取一个 {...} 组或单个 token;返回 (kind, value)。"""
        skip_spaces()
        if pos[0] < len(src) and src[pos[0]] == "{":
            depth = 0
            start = pos[0]
            while pos[0] < len(src):
                c = src[pos[0]]
                if c == "{":
                    depth += 1
                elif c == "}":
                    depth -= 1
                    if depth == 0:
                        inner = src[start + 1:pos[0]]
                        pos[0] += 1
                        return ("group", parse_sequence(inner))
                pos[0] += 1
            return (None, None)
        return parse_token()

    def parse_token():
        skip_spaces()
        if pos[0] >= len(src):
            return (None, None)
        c = src[pos[0]]
        if c == "\\":
            m = re.match(r"\\([a-zA-Z]+)", src[pos[0]:])
            if m:
                name = m.group(1)
                pos[0] += m.end()
                if name in greek:
                    return ("mi", greek[name])
                if name in ops:
                    return ("mo", ops[name])
                if name in ("frac", "sqrt"):
                    return ("op-" + name, None)
                if name in fences:
                    return ("skip", None)
                if name == ",":
                    return ("space", None)
                if name == "left" or name == "right":
                    return ("skip", None)
                return ("mi", name)
            m2 = re.match(r"\\([{}])", src[pos[0]:])
            if m2:
                pos[0] += 2
                return ("mi", m2.group(1))
            return (None, None)
        if c.isdigit() or (c == "." and pos[0] + 1 < len(src) and src[pos[0] + 1].isdigit()):
            m = re.match(r"[0-9.]+", src[pos[0]:])
            pos[0] += m.end()
            return ("mn", m.group(0))
        if c.isalpha():
            m = re.match(r"[a-zA-Z]+", src[pos[0]:])
            pos[0] += m.end()
            return ("mi", m.group(0))
        if c in "=<>+-":
            pos[0] += 1
            return ("mo", c)
        if c in "()[]|":
            pos[0] += 1
            return ("mo", c)
        if c == ",":
            pos[0] += 1
            return ("mo", ",")
        pos[0] += 1
        return ("mi", c)

    def skip_spaces():
        while pos[0] < len(src) and src[pos[0]] == " ":
            pos[0] += 1

    def parse_sequence(fragment):
        nodes = []
        i = 0
        pos[0] = 0
        local = src
        # 用局部解析:直接对 fragment 递归
        return _parse_fragment(fragment)

    def _parse_fragment(fragment):
        nodes = []
        i = 0
        n = len(fragment)
        while i < n:
            c = fragment[i]
            if c == " ":
                i += 1
                continue
            if c == "\\":
                m = re.match(r"\\([a-zA-Z]+)(\{)?", fragment[i:])
                if not m:
                    i += 1
                    continue
                name = m.group(1)
                i += m.end(0)
                if m.group(2):  # takes {..}
                    grp, ni = _read_group(fragment, i)
                    if grp is None:
                        return None
                    i = ni
                    if name == "frac":
                        grp2, ni2 = _read_group(fragment, i)
                        if grp2 is None:
                            return None
                        i = ni2
                        num = _parse_fragment(grp)
                        den = _parse_fragment(grp2)
                        if num is None or den is None:
                            return None
                        nodes.append("<mfrac>%s%s</mfrac>" % (num, den))
                    elif name == "sqrt":
                        inner = _parse_fragment(grp)
                        if inner is None:
                            return None
                        nodes.append("<msqrt>%s</msqrt>" % inner)
                    else:
                        inner = _parse_fragment(grp)
                        if inner is None:
                            return None
                        nodes.append("<mrow>%s</mrow>" % inner)
                else:
                    if name in greek:
                        nodes.append("<mi>%s</mi>" % greek[name])
                    elif name in ops:
                        nodes.append("<mo>%s</mo>" % ops[name])
                    elif name in ("int", "sum", "prod", "lim", "log", "ln", "sin", "cos", "tan", "exp", "max", "min"):
                        nodes.append("<mo>%s</mo>" % name)
                    elif name in ("left", "right"):
                        # optional delimiter follows
                        if i < n and fragment[i] in ".([|":
                            i += 1
                    elif name == ",":
                        pass
                    else:
                        nodes.append("<mi>%s</mi>" % name)
                continue
            if c.isdigit():
                m = re.match(r"[0-9.]+", fragment[i:])
                nodes.append("<mn>%s</mn>" % m.group(0))
                i += m.end()
                continue
            if c.isalpha():
                m = re.match(r"[a-zA-Z]+", fragment[i:])
                nodes.append("<mi>%s</mi>" % m.group(0))
                i += m.end()
                continue
            if c in "^_":
                i += 1
                if i < n and fragment[i] == "{":
                    grp, ni = _read_group(fragment, i + 1)
                    if grp is None:
                        return None
                    i = ni
                    inner = _parse_fragment(grp)
                else:
                    m = re.match(r"[0-9a-zA-Z]+", fragment[i:])
                    if not m:
                        return None
                    inner = "<mi>%s</mi>" % m.group(0) if fragment[i].isalpha() else "<mn>%s</mn>" % m.group(0)
                    i += m.end()
                tag = "msup" if c == "^" else "msub"
                if not nodes:
                    return None
                base = nodes.pop()
                # 组合 base(可能是复合 mrow)
                base_full = base if base.startswith("<mrow>") or len(base) < 200 else "<mrow>%s</mrow>" % base
                nodes.append("<%s>%s%s</%s>" % (tag, base, inner, tag))
                continue
            if c in "=<>+-*/":
                nodes.append("<mo>%s</mo>" % c)
                i += 1
                continue
            if c in "()[]|":
                nodes.append("<mo>%s</mo>" % c)
                i += 1
                continue
            if c == ",":
                nodes.append("<mo>%s</mo>" % c)
                i += 1
                continue
            i += 1
        return "".join(nodes) if nodes else None

    def _read_group(fragment, start):
        """读取一个 {...} 组;start 可指向 '{' 本身或其后一位。返回 (内容, 新索引)。"""
        i = start
        if i < len(fragment) and fragment[i] == "{":
            i += 1
        depth = 1
        while i < len(fragment):
            if fragment[i] == "{":
                depth += 1
            elif fragment[i] == "}":
                depth -= 1
                if depth == 0:
                    return fragment[start:i].lstrip("{"), i + 1
            i += 1
        return None, start

    result = _parse_fragment(src)
    return result


def formula_display(formula_block):
    """决定公式的渲染路径:mathml / fallback-text。返回 dict。"""
    form = formula_block.get("form")
    latex = formula_block.get("latex")
    mathml = formula_block.get("mathml")
    alt = formula_block.get("alt") or formula_block.get("text")
    if form == "mathml" and mathml:
        return {"mode": "mathml", "mathml": mathml, "alt": alt, "source": mathml}
    if latex:
        converted = latex_to_mathml(latex)
        if converted:
            return {"mode": "mathml", "mathml": converted, "alt": alt, "source": latex}
        # 回退:保留原始 LaTeX,可复制
        return {"mode": "fallback-text", "source": latex, "alt": alt}
    if alt:
        return {"mode": "fallback-text", "source": alt, "alt": alt}
    return {"mode": "empty"}


if __name__ == "__main__":
    tests = [
        ("E=mc^2", "msup"),
        ("x=\\frac{-b\\pm\\sqrt{b^2-4ac}}{2a}", "mfrac"),
        ("\\int_0^1 x^2\\,dx=\\frac13", "msub"),
    ]
    for latex, expect in tests:
        r = latex_to_mathml(latex)
        ok = r is not None and expect in r
        print(("OK " if ok else "FAIL ") + latex + " -> " + (r or "None")[:80])
