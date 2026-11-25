#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_reader.py — HTML 交互阅读器生成器（V2.3.2，零依赖）
读取语义分析数据 JSON + HTML 模板，注入安全转义后的数据，生成可离线打开的独立 HTML。

核心数据：title、mode、segments[].blocks、original_text、conservative。
每个 block 包含 text、role、priority（精读/速览/跳读）、sentences、preview，
以及可选 emphasis（相对本块的 start/end/text/score 区间）。
原文模式使用 original_text 逐字恢复；辅助版只生成一份文本 DOM。

用法:
    python build_reader.py data.json output.html
    python build_reader.py data.json output.html path/to/reader_template.html
    python build_reader.py --from-text input.txt output.html   # 从纯文本快速构建（自动切句，全标重点读）
"""
import sys
import os
import json
import re

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_TEMPLATE = os.path.join(HERE, '..', 'assets', 'reader_template.html')
SENT_SPLIT = re.compile(r'([。！？；.!?])')


def split_sentences(text):
    """按全角/半角句末标点切句，保留原标点，不替换不补加。"""
    parts = SENT_SPLIT.split(text)
    out = []
    buf = ""
    for p in parts:
        if not p:
            continue
        if SENT_SPLIT.fullmatch(p):
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


def build_data_from_text(text, title="阅读辅助", analysis=None):
    """从纯文本构建数据：调用统一处理层 analyze.route_text（V2.3）。
    有 Agent analysis 时用语义路由；无则保守模式（全文呈现，不贴标签，不折叠）。"""
    try:
        import importlib.util as _ilu
        _ap = os.path.join(HERE, 'analyze.py')
        _spec = _ilu.spec_from_file_location('analyze', _ap)
        _am = _ilu.module_from_spec(_spec); _spec.loader.exec_module(_am)
        result = _am.route_text(text, analysis=analysis)
        result["title"] = title
        result.pop("_meta", None)
        return result
    except Exception:
        segs_raw = [s.strip() for s in re.split(r'\n\s*\n', text.strip()) if s.strip()]
        segments = []
        for i, s in enumerate(segs_raw, 1):
            segments.append({
                "seg_no": i, "priority": None, "reason": None,
                "original": s, "sentences": split_sentences(s),
                "blocks": [{"text": s, "role": None, "priority": None,
                            "sentences": split_sentences(s), "preview": None}],
                "foldable": False,
            })
        return {"title": title, "mode": "聚焦阅读", "high_risk": False,
                "segments": segments, "original_text": text, "conservative": True}


def inject(template_html, data):
    """把 data 以 JSON 形式注入模板的 __READER_DATA__ 占位符。"""
    # 用 json.dumps(ensure_ascii=False) 后再转义 </script> 防止破出脚本块
    raw = json.dumps(data, ensure_ascii=False)
    safe = raw.replace('</script>', '<\\/script>')
    if '__READER_DATA__' not in template_html:
        raise ValueError("模板中未找到 __READER_DATA__ 占位符")
    return template_html.replace('__READER_DATA__', safe)


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(1)

    if args[0] == '--from-text':
        if len(args) < 3:
            print("用法: build_reader.py --from-text input.txt output.html [analysis.json] [template]")
            sys.exit(1)
        with open(args[1], 'r', encoding='utf-8') as f:
            text = f.read()
        analysis = None
        if len(args) > 3 and not args[3].endswith('.html'):
            with open(args[3], 'r', encoding='utf-8') as f:
                analysis = json.load(f)
        data = build_data_from_text(text, analysis=analysis)
        out_path = args[2]
        tpl_idx = 4 if analysis else 3
        tpl_path = args[tpl_idx] if len(args) > tpl_idx else DEFAULT_TEMPLATE
    else:
        if len(args) < 2:
            print("用法: build_reader.py data.json output.html [template]")
            sys.exit(1)
        with open(args[0], 'r', encoding='utf-8') as f:
            data = json.load(f)
        out_path = args[1]
        tpl_path = args[2] if len(args) > 2 else DEFAULT_TEMPLATE

    with open(tpl_path, 'r', encoding='utf-8') as f:
        template = f.read()
    html = inject(template, data)
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"已生成 HTML 阅读器：{out_path}")
    print(f"  段数：{len(data.get('segments', []))}  模式：{data.get('mode','?')}")
    print("  用浏览器打开即可使用；离线运行，无需联网。")


if __name__ == '__main__':
    main()
