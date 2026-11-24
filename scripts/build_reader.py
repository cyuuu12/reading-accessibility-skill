#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_reader.py — HTML 交互阅读器生成器（零依赖）
读取结构化阅读数据 JSON + HTML 模板，注入安全转义后的数据，生成可离线打开的独立 HTML。

数据 JSON schema:
{
  "title": "可选标题",
  "mode": "完整阅读|聚焦阅读|快速浏览",
  "high_risk": false,
  "segments": [
    {
      "seg_no": 1,
      "priority": "重点读|简单读|可略读",
      "reason": "一句通俗原因",
      "skip_note": "略过会…（可略读段才需要）或 null",
      "original": "原文段落",
      "sentences": ["句1","句2"],   // 辅助版逐句，用于逐句高亮
      "foldable": true
    }
  ]
}

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


def build_data_from_text(text, title="阅读辅助"):
    """从纯文本快速构建数据：按空行分段，全标重点读（保守默认）。"""
    segs_raw = [s.strip() for s in re.split(r'\n\s*\n', text.strip()) if s.strip()]
    segments = []
    for i, s in enumerate(segs_raw, 1):
        segments.append({
            "seg_no": i,
            "priority": "重点读",
            "reason": "自动构建，默认重点读，请按 routing.md 重新标注。",
            "skip_note": None,
            "original": s,
            "sentences": split_sentences(s),
            "foldable": False,
        })
    return {"title": title, "mode": "完整阅读", "high_risk": False, "segments": segments}


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
            print("用法: build_reader.py --from-text input.txt output.html [template]")
            sys.exit(1)
        with open(args[1], 'r', encoding='utf-8') as f:
            text = f.read()
        data = build_data_from_text(text)
        out_path = args[2]
        tpl_path = args[3] if len(args) > 3 else DEFAULT_TEMPLATE
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
