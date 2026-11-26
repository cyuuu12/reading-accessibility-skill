#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build_markdown.py — 从统一 route_data.json 生成轻量 Markdown。

只消费 analyze.route_text 已生成的结构化结果，不重新进行语义分析。
保留标题层级、原文顺序和已校验的局部 emphasis，不模拟 HTML 控件。

用法:
    python build_markdown.py route_data.json output.md
"""
import json
import sys


def render_block_text(block):
    """在原文块内插入已校验 emphasis；除 Markdown 标记外不修改字符。"""
    text = block.get("text") or ""
    points = {0, len(text)}
    for item in block.get("emphasis") or []:
        start = max(0, int(item.get("start", 0)))
        end = min(len(text), int(item.get("end", 0)))
        if start < end:
            points.add(start)
            points.add(end)
    ordered = sorted(points)
    ranges = block.get("emphasis") or []
    parts = []
    for left, right in zip(ordered, ordered[1:]):
        if left == right:
            continue
        value = text[left:right]
        emphasized = any(
            int(item.get("start", 0)) <= left and right <= int(item.get("end", 0))
            for item in ranges
        )
        parts.append(f"**{value}**" if emphasized else value)
    return "".join(parts)


def render_segment(segment):
    blocks = segment.get("blocks") or []
    if len(blocks) == 1 and blocks[0].get("heading_level") is not None:
        level = max(0, min(6, int(blocks[0]["heading_level"])))
        prefix = "#" * min(6, level + 1)
        return f"{prefix} {blocks[0].get('text') or ''}"

    original = segment.get("original") or ""
    cursor = 0
    parts = []
    for block in blocks:
        text = block.get("text") or ""
        at = original.find(text, cursor)
        if at < 0:
            at = original.find(text)
        if at < 0:
            parts.append(render_block_text(block))
            continue
        if at > cursor:
            parts.append(original[cursor:at])
        parts.append(render_block_text(block))
        cursor = at + len(text)
    if cursor < len(original):
        parts.append(original[cursor:])
    return "".join(parts) if parts else original


def render_markdown(data, include_modules=True):
    sections = [f"# {data.get('title') or '阅读辅助'}"]
    modules = data.get("modules") or []
    if include_modules and modules:
        module_parts = ["## 理解框架"]
        for module in modules:
            module_parts.append(f"### {module.get('title') or '内容模块'}\n\n{module.get('content') or ''}")
        sections.append("\n\n".join(module_parts))
    body = "\n\n".join(render_segment(segment) for segment in data.get("segments") or [])
    sections.append("## 辅助阅读正文\n\n" + body)
    return "\n\n".join(sections).rstrip() + "\n"


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    with open(sys.argv[1], "r", encoding="utf-8") as file:
        data = json.load(file)
    markdown = render_markdown(data)
    with open(sys.argv[2], "w", encoding="utf-8", newline="\n") as file:
        file.write(markdown)
    print(f"已生成 Markdown：{sys.argv[2]}")
    print(f"  段数：{len(data.get('segments') or [])}（复用统一分析数据）")


if __name__ == "__main__":
    main()
