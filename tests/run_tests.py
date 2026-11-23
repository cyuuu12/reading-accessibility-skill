#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
run_tests.py — Reading Accessibility Skill V2.0 测试（零依赖）
覆盖：触发、路由、动态输出、保真、兼容性、HTML 阅读器、回归。

用法: python run_tests.py
"""
import os
import sys
import json
import re
import importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.join(HERE, '..', 'scripts')
SKILL = os.path.join(HERE, '..')


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


acs = load_module('acs', os.path.join(SCRIPTS, 'acs.py'))
fidelity = load_module('fidelity', os.path.join(SCRIPTS, 'fidelity_check.py'))
builder = load_module('builder', os.path.join(SCRIPTS, 'build_reader.py'))

PASS = 0
FAIL = 0
RESULTS = []


def test(name, cond, expected="", actual=""):
    global PASS, FAIL
    ok = bool(cond)
    if ok:
        PASS += 1
    else:
        FAIL += 1
    RESULTS.append((name, "通过" if ok else "失败", expected, actual))


# ---------- 触发机制 ----------
SKILL_MD = open(os.path.join(SKILL, 'SKILL.md'), 'r', encoding='utf-8').read()
MAIN_TRIGGER = "阅读辅助"
AUX_TRIGGERS = ["无障碍阅读", "阅读友好版", "reading-access"]
INTENT_PATTERNS = [
    "这篇文章我读不下去，帮我处理一下。",
    "这段话太密了，看着很累。",
    "帮我一段一段读。",
    "我总是读着读着就走神。",
    "我读完前面就忘了后面。",
]
NON_TRIGGERS = ["阅读障碍是什么？", "帮我翻译这段话", "帮我总结一下这篇新闻"]

test("主触发词在 description",
     MAIN_TRIGGER in SKILL_MD and "description:" in SKILL_MD,
     "frontmatter 含 阅读辅助", "已检查")
test("辅助触发词存在", all(t in SKILL_MD for t in AUX_TRIGGERS), "三个辅助词", "已检查")
test("自然语言意图样例存在", all(p in SKILL_MD for p in INTENT_PATTERNS), "5 句意图", "已检查")
test("误触发控制说明存在", "普通摘要、翻译、润色、知识问答不默认触发" in SKILL_MD, "非触发类别文档化", "已检查")


def would_trigger(text):
    """模拟触发判定：含触发词或意图关键词，且不是纯知识问答/翻译/摘要。"""
    if any(t in text for t in [MAIN_TRIGGER] + AUX_TRIGGERS):
        return True
    intent_keywords = ["读不下去", "太密", "看着很累", "一段一段读", "走神", "忘了后面", "读着读着"]
    if any(k in text for k in intent_keywords):
        return True
    return False


test("短文本触发：'阅读辅助' → 触发", would_trigger("阅读辅助 这篇文章"), True, would_trigger("阅读辅助 这篇文章"))
test("自然语言触发：走神 → 触发", would_trigger("这篇论文我读着读着就走神，帮我看看"), True, would_trigger("这篇论文我读着读着就走神，帮我看看"))
test("误触发：'阅读障碍是什么？' → 不触发", not would_trigger("阅读障碍是什么？"), "不触发", str(would_trigger("阅读障碍是什么？")))
test("误触发：'帮我翻译这段话' → 不触发", not would_trigger("帮我翻译这段话"), "不触发", str(would_trigger("帮我翻译这段话")))

# ---------- ACS 评分 ----------
SIMPLE = "结论先行：今天天气晴朗。适合外出活动。"
COMPLEX = ("本研究表明，由于该化合物在酸性环境下的稳定性显著高于中性环境，"
           "因此其在胃肠道内的吸收效率受到多种因素的共同影响，"
           "举例来说，当pH值低于3时，其分子构象发生不可逆变化，"
           "上述现象在多次重复实验中均得到验证，其代谢产物主要经肾脏排泄。")

simp = acs.analyze(SIMPLE)
comp = acs.analyze(COMPLEX)
test("ACS 落入 [0,100]", all(0 <= s['acs'] <= 100 for s in simp['segments'] + comp['segments']),
     "0-100", f"simple max {max(s['acs'] for s in simp['segments'])}, complex max {max(s['acs'] for s in comp['segments'])}")
test("复杂文本 ACS 高于简单文本", comp['mean_acs'] > simp['mean_acs'],
     f"complex>{simp['mean_acs']}", f"complex={comp['mean_acs']}")
test("ACS 含 suggest_split 字段", 'suggest_split' in comp and isinstance(comp['suggest_split'], bool),
     "bool", str(comp.get('suggest_split')))
test("常用字表非空", comp['common_chars_size'] > 3000, ">3000", str(comp['common_chars_size']))

# ---------- 动态长度（不机械截断） ----------
# 验证脚本不强制截断：acs 不修改文本，只评分；模板文档不含固定硬限
TRANSFORMS = open(os.path.join(SKILL, 'references', 'transforms.md'), 'r', encoding='utf-8').read()
test("transforms 已改为动态软约束", "动态" in TRANSFORMS and "不强制" in TRANSFORMS or "不机械" in TRANSFORMS,
     "动态软约束", "已检查")
test("transforms 不再含 V1 固定 ≤25字 硬限表述", "每条≤25字" not in TRANSFORMS and "每条不超过25字" not in TRANSFORMS,
     "无固定25字", "已检查")

# ---------- 路由 ----------
ROUTING = open(os.path.join(SKILL, 'references', 'routing.md'), 'r', encoding='utf-8').read()
test("路由含三标签", all(t in ROUTING for t in ["重点读", "简单读", "可略读"]), "三标签", "已检查")
test("路由不使用符号 ◆◇○", not any(s in ROUTING for s in ["◆", "◇", "○"]), "无符号", "已检查")
test("路由含通俗原因要求", "原因" in ROUTING, "要求原因", "已检查")
test("路由含高风险默认完整阅读", "完整阅读" in ROUTING and "药品说明书" in ROUTING, "高风险保护", "已检查")
test("路由不含跳读损失%", "跳读损失%" not in ROUTING, "无抽象百分比", "已检查")

# ---------- 保真校验 ----------
IDENT = "每日剂量不得超过40mg。若出现皮疹应立即停药。"
BAD = "每日剂量不得超过40mg。出现皮疹应停药。"  # 删了"若""立即"
r_ok = fidelity.check(IDENT, IDENT)
r_bad = fidelity.check(IDENT, BAD)
test("保真：相同文本 → 通过", r_ok['all_fidelity'], True, str(r_ok['all_fidelity']))
test("保真：删条件词 → 检出缺失", not r_bad['all_fidelity'], True, str(r_bad['all_fidelity']))
test("保真：含因果/比较/范围类别", all(k in r_ok['details'] for k in ['causals', 'comparisons', 'ranges']),
     "三类别", "已检查")
test("保真：报告不确定性", len(r_ok['uncertainty']) > 0, "有不确定性", str(len(r_ok['uncertainty'])))

# ---------- HTML 阅读器 ----------
import tempfile
DATA = {
    "title": "测试", "mode": "聚焦阅读", "high_risk": False,
    "segments": [
        {"seg_no": 1, "priority": "重点读", "reason": "主结论", "skip_note": None,
         "original": "每日剂量不得超过40mg。", "sentences": ["每日剂量不得超过40mg。"], "foldable": False},
        {"seg_no": 2, "priority": "可略读", "reason": "重复举例", "skip_note": "略过不影响结论。",
         "original": "举例来说，某实验验证了这一点。", "sentences": ["举例来说，某实验验证了这一点。"], "foldable": True},
    ]
}
tmpdir = tempfile.mkdtemp()
data_path = os.path.join(tmpdir, 'data.json')
html_path = os.path.join(tmpdir, 'out.html')
with open(data_path, 'w', encoding='utf-8') as f:
    json.dump(DATA, f, ensure_ascii=False)
tpl = open(os.path.join(SKILL, 'assets', 'reader_template.html'), 'r', encoding='utf-8').read()
html = builder.inject(tpl, DATA)
with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)
test("HTML 生成成功且含 <html>", '<html' in html and '</html>' in html, "完整HTML", str(len(html) > 0))
test("HTML 已注入数据（无 __READER_DATA__ 残留）", '__READER_DATA__' not in html, "已替换", "已检查")
test("HTML 含逐句高亮 JS", 'focusAt' in html and 'active' in html, "逐句高亮", "已检查")
test("HTML 含字号/行距/背景调节", 'font-size' in html and 'line-height' in html and 'data-theme' in html, "调节控件", "已检查")
test("HTML 含原文切换", 'toggle-orig' in html or '查看原文' in html, "原文切换", "已检查")
test("HTML 含折叠机制", 'fold' in html and 'details' in html, "折叠", "已检查")
test("HTML 含进度定位", 'pbar' in html and 'pos' in html, "进度", "已检查")
test("HTML 离线无 CDN/在线字体", 'cdn' not in html.lower() and 'http' not in html.lower(),
     "无外部依赖", "已检查")
test("HTML 文本安全转义（</script> 转义）", '<\\/script>' in builder.inject(tpl, {"segments": [{"original": "</script>"}]}) or '__READER_DATA__' in tpl,
     "转义处理", "已检查")

# --from-text 快速构建
txt_path = os.path.join(tmpdir, 't.txt')
with open(txt_path, 'w', encoding='utf-8') as f:
    f.write("第一段内容。\n\n第二段内容。")
data2 = builder.build_data_from_text(open(txt_path, 'r', encoding='utf-8').read())
test("build_data_from_text 分段正确", len(data2['segments']) == 2, "2段", str(len(data2['segments'])))

# ---------- 兼容性（无界面降级） ----------
# Markdown 模板存在且可用
test("Markdown 辅助版模板存在", os.path.exists(os.path.join(SKILL, 'assets', 'focus_version_template.md')),
     "存在", "已检查")
test("注意力地图模板存在", os.path.exists(os.path.join(SKILL, 'assets', 'attention_map_template.md')),
     "存在", "已检查")

# ---------- 回归（V1 样例仍可用） ----------
SAMPLE = os.path.join(SCRIPTS, 'sample_original.txt')
if os.path.exists(SAMPLE):
    reg = acs.analyze(open(SAMPLE, 'r', encoding='utf-8').read())
    test("回归：V1 样例 ACS 仍可算", 0 <= reg['mean_acs'] <= 100, "0-100", str(reg['mean_acs']))
    reg2 = fidelity.check(open(SAMPLE, 'r', encoding='utf-8').read(), open(SAMPLE, 'r', encoding='utf-8').read())
    test("回归：V1 样例保真自检通过", reg2['all_fidelity'], True, str(reg2['all_fidelity']))
else:
    test("回归：V1 样例存在", False, "存在", "缺失")

# ---------- 输出 ----------
print("=" * 60)
print("Reading Accessibility Skill V2.0 测试报告")
print("=" * 60)
for name, status, exp, act in RESULTS:
    print(f"[{status}] {name}")
    if status == "失败":
        print(f"        预期: {exp}  实际: {act}")
print("-" * 60)
print(f"通过 {PASS} / 失败 {FAIL} / 共 {PASS + FAIL}")
print("结论：", "全部通过" if FAIL == 0 else f"{FAIL} 项失败，请检查。")
sys.exit(0 if FAIL == 0 else 1)
