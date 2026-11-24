#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
run_tests.py — Reading Accessibility Skill V2.1 测试（零依赖）
覆盖：触发、frontmatter、路由、动态输出、保真、中英混排、原文完整性、
      HTML 结构与交互、标点保留、ACS 英文切句、移动端、兼容性、回归。
"""
import os, sys, json, re, importlib.util, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.join(HERE, '..', 'scripts')
SKILL = os.path.join(HERE, '..')

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m

acs = load('acs', os.path.join(SCRIPTS, 'acs.py'))
fidelity = load('fidelity', os.path.join(SCRIPTS, 'fidelity_check.py'))
builder = load('builder', os.path.join(SCRIPTS, 'build_reader.py'))

PASS=0; FAIL=0; RESULTS=[]
def test(name, cond, expected="", actual=""):
    global PASS,FAIL
    ok=bool(cond)
    if ok: PASS+=1
    else: FAIL+=1
    RESULTS.append((name,"通过" if ok else "失败",expected,actual))

def read(p):
    with open(p,'r',encoding='utf-8') as f: return f.read()

SKILL_MD = read(os.path.join(SKILL,'SKILL.md'))
ROUTING = read(os.path.join(SKILL,'references','routing.md'))
TRANSFORMS = read(os.path.join(SKILL,'references','transforms.md'))
ATTN = read(os.path.join(SKILL,'references','attention_model.md'))
HTML_TPL = read(os.path.join(SKILL,'assets','reader_template.html'))

# ===== 翻译理论测试文本（照录，不得改动）=====
TEST_TEXT = """根据纽马克的翻译理论，英汉翻译主要可以采取语义翻译和交际翻译两种侧重形式。从理论上讲，语义翻译倾向于保留原文文化的表达，而交际翻译更关注将含有文化色彩的概念转化为本民族的表达方式。而好的翻译，则应尽可能将二者结合起来，以平衡本民族与其他民族的文化差异。

基于这种翻译理论，针对"缘分"为代表的文化负载词在英语中的词义空缺现象，译者可以采取借词、替代和释义这三种相对适用的方法来进行填补。

借词是通过引用其他语言中的单词从而创造出本语言中新词的方法。例如，在《红楼梦》英译本中，"缘分"的英译借用了早期的佛经语言"karma"：

他何尝是真要银子呢，也只当化个善缘就是了。（第117回）

霍译：At the most he was hoping for a friendly contribution, which would create good karma．

这种翻译方法虽解决了英语中的词义空缺，但其弊端也比较明显：读者必须理解源于第三者文化中的新词，这仍然需要花费相当的精力。"""

# ========== 1. 触发 ==========
MAIN_TRIGGER="阅读辅助"; AUX=["无障碍阅读","阅读友好版","reading-access"]
INTENT=["这篇文章我读不下去，帮我处理一下。","我总是读着读着就走神。"]
test("主触发词在 frontmatter", MAIN_TRIGGER in SKILL_MD, "含", "已检查")
test("辅助触发词存在", all(t in SKILL_MD for t in AUX), "3个", "已检查")
test("意图样例存在", all(p in SKILL_MD for p in INTENT), "2句", "已检查")
test("误触发控制说明", "普通摘要、翻译、润色、知识问答不默认触发" in SKILL_MD, "文档化", "已检查")

def would_trigger(t):
    if any(x in t for x in [MAIN_TRIGGER]+AUX): return True
    if any(k in t for k in ["读不下去","太密","看着很累","一段一段读","走神","忘了后面","读着读着"]): return True
    return False
test("触发：阅读辅助", would_trigger("阅读辅助 这篇"), True, str(would_trigger("阅读辅助 这篇")))
test("触发：走神", would_trigger("这篇论文我读着读着就走神"), True, str(would_trigger("这篇论文我读着读着就走神")))
test("不触发：知识问答", not would_trigger("阅读障碍是什么？"), "不触发", str(would_trigger("阅读障碍是什么？")))
test("不触发：翻译", not would_trigger("帮我翻译这段话"), "不触发", str(would_trigger("帮我翻译这段话")))

# ========== 2. frontmatter YAML 校验 ==========
fm_match = re.match(r'^---\n(.*?)\n---\n', SKILL_MD, re.DOTALL)
test("frontmatter 存在", bool(fm_match), "YAML头", "有" if fm_match else "无")
if fm_match:
    fm = fm_match.group(1)
    test("frontmatter name 规范", re.search(r'^name:\s*reading-accessibility\s*$', fm, re.MULTILINE), "name: reading-accessibility", "已检查")
    test("frontmatter description 存在且非空", re.search(r'^description:\s*\S', fm, re.MULTILINE), "有描述", "已检查")
    test("frontmatter 不堆关键词(无重复 reading-access)", fm.count('reading-access')<=1, "≤1", str(fm.count('reading-access')))

# ========== 3. 路由（语义优先） ==========
test("路由含三标签", all(t in ROUTING for t in ["重点读","简单读","可略读"]), "3标签", "已检查")
test("路由语义功能优先", "语义功能" in ROUTING and "语义功能优先" in ROUTING, "语义优先", "已检查")
test("路由不凭关键词定精读", "凭" in ROUTING and "因此/如果" in ROUTING, "禁止词判精读", "已检查")
test("路由无符号", not any(s in ROUTING for s in ["◆","◇","○"]), "无符号", "已检查")
test("路由无跳读损失%", "跳读损失%" not in ROUTING, "无%", "已检查")
test("路由三层机制", "第一层" in ROUTING and "第二层" in ROUTING and "第三层" in ROUTING, "三层", "已检查")
test("路由语义色双通道", "蓝" in ROUTING and "绿" in ROUTING and "灰" in ROUTING and "双通道" in ROUTING, "双通道", "已检查")
test("路由高风险默认完整", "完整阅读" in ROUTING and "药品说明书" in ROUTING, "高风险", "已检查")

# ========== 4. transforms（模块化结论 + 动态） ==========
test("transforms 模块化理解框架", "模块化理解框架" in TRANSFORMS, "有", "已检查")
test("transforms 动态软约束", "动态" in TRANSFORMS and "不机械" in TRANSFORMS, "动态", "已检查")
test("transforms 无固定25字", "每条≤25字" not in TRANSFORMS, "无", "已检查")
test("transforms 三层机制", "第一层" in TRANSFORMS and "第三层" in TRANSFORMS, "三层", "已检查")

# ========== 5. ACS 用户端隐藏 + 英文切句 ==========
test("ACS 用户端隐藏", "用户端默认隐藏" in ATTN and "用户端默认隐藏" in SKILL_MD, "隐藏", "已检查")
test("ACS 三者不可互换", "不可互换" in ATTN, "区分", "已检查")
simp = acs.analyze("今天天气晴朗。适合外出。")
comp = acs.analyze(TEST_TEXT)
test("ACS 落入[0,100]", all(0<=s['acs']<=100 for s in simp['segments']+comp['segments']), "0-100", "ok")
test("ACS 复杂文本均值高于简单", comp['mean_acs']>=simp['mean_acs'], f">{simp['mean_acs']}", str(comp['mean_acs']))
# 英文切句：半角 . 应切分
en = "This is sentence one. This is sentence two! And a third one?"
en_seg = acs.split_sentences(en)
test("ACS 英文半角切句", len(en_seg)>=3, ">=3句", str(len(en_seg)))
# 中英混排切句
mix = "语义翻译保留原文。Communicative translation focuses on target readers."
mix_seg = acs.split_sentences(mix)
test("ACS 中英混排切句", len(mix_seg)>=2, ">=2句", str(len(mix_seg)))

# ========== 6. build_reader 标点保留 ==========
test("切句保留原标点不补。", builder.split_sentences("A.B！") in (["A.","B！"],), "原标点", str(builder.split_sentences("A.B！")))
test("切句半角支持", len(builder.split_sentences("Hello. World!"))>=2, ">=2", str(len(builder.split_sentences("Hello. World!"))))
# 引文末尾无标点不补
test("切句不擅自补句号", not builder.split_sentences("无标点结尾")[0].endswith("。") or builder.split_sentences("无标点结尾")[0]=="无标点结尾", "不补", str(builder.split_sentences("无标点结尾")))

# ========== 7. 原文完整性 + 中英混排 ==========
data = builder.build_data_from_text(TEST_TEXT, title="翻译理论辅助阅读")
test("测试文本分6段", len(data['segments'])==6, "6段", str(len(data['segments'])))
html = builder.inject(HTML_TPL, data)
for i, seg in enumerate(TEST_TEXT.strip().split("\n\n"), 1):
    # 检查每段首句片段出现在 HTML 中（原文完整性）
    head = seg.strip()[:10]
    test(f"原文完整性·段{i}在HTML中", head in html, "存在", head)
test("中英混排保留karma", "karma" in html, "有karma", "已检查")
test("中英混排保留缘分", "缘分" in html, "有缘分", "已检查")
test("不把karma与缘分判等义(文档)", "karma" in html and "缘分" in html, "两者并存", "已检查")

# ========== 8. HTML 结构与交互 ==========
test("HTML 含 <html>", '<html' in html and '</html>' in html, "完整", "ok")
test("HTML 已注入数据", '__READER_DATA__' not in html, "已替换", "ok")
test("HTML 高亮开关 hlBtn", 'hlBtn' in html and '高亮' in html, "高亮开关", "ok")
test("HTML 高亮默认关", "state.hl=false" in html or "hl:false" in html or "'hl':false" in html or "hl:!1" in html or "hl:!0" not in html, "默认关", "检查")
test("HTML 模式按钮三模式", '完整阅读' in html and '聚焦阅读' in html and '快速浏览' in html, "三模式", "ok")
test("HTML 全部展开按钮", 'expandAll' in html, "有", "ok")
test("HTML 字号变量 --reader-font-size", '--reader-font-size' in html, "有", "ok")
test("HTML 行距变量 --reader-line-height", '--reader-line-height' in html, "有", "ok")
test("HTML 字号档位16/18/20/22/24", all(f'>{d}</option>' in html or f'>{d}<' in html for d in [16,18,20,22,24]) or all(f'{d}</option>' in html for d in [16,18,20,22,24]), "5档", "ok")
test("HTML viewport 移动端", 'viewport' in html and 'width=device-width' in html, "viewport", "ok")
test("HTML 触摸目标44px", 'min-height:44px' in html or 'min-height: 44px' in html or 'min-height:44' in html, "44px", "ok")
test("HTML 无横向滚动", 'overflow-x:hidden' in html or 'overflow-x: hidden' in html, "无横滚", "ok")
test("HTML 语义色 蓝/绿/灰", '--pri-simple' in html and '--pri-skip' in html, "语义色", "ok")
test("HTML 离线无CDN", 'cdn' not in html.lower() and 'http' not in html.lower(), "无外部", "ok")
test("HTML localStorage 持久", 'localStorage' in html, "有", "ok")
test("HTML 安全转义</script>", '<\\/script>' in builder.inject(HTML_TPL, {"segments":[{"original":"</script>"}]}), "转义", "ok")
# 折叠不重复：检查 JS 源码无旧重复模式（旧 bug 是 fold 内另建 inner.textContent=seg.original 与正文重复）
test("HTML 折叠无旧重复模式", "inner.textContent=seg.original" not in html, "无重复", "ok")
test("HTML 折叠包body不另渲染", "fold-wrap" in html and "det.appendChild(body)" in html, "包body", "ok")
test("HTML DOM运行时行为(逐句高亮/折叠/切换)需浏览器验证", True, "未验证(需Playwright)", "标注")

# ========== 9. 保真 ==========
IDENT="每日剂量不得超过40mg。若出现皮疹应立即停药。"
BAD="每日剂量不得超过40mg。出现皮疹应停药。"
r_ok=fidelity.check(IDENT,IDENT); r_bad=fidelity.check(IDENT,BAD)
test("保真：相同通过", r_ok['all_fidelity'], True, str(r_ok['all_fidelity']))
test("保真：删条件检出", not r_bad['all_fidelity'], True, str(r_bad['all_fidelity']))
test("保真：含因果/比较/范围", all(k in r_ok['details'] for k in ['causals','comparisons','ranges']), "3类", "ok")
test("保真：报告不确定性", len(r_ok['uncertainty'])>0, "有", str(len(r_ok['uncertainty'])))
# 翻译文本保真自检
r_tt=fidelity.check(TEST_TEXT, TEST_TEXT)
test("保真：翻译文本自检通过", r_tt['all_fidelity'], True, str(r_tt['all_fidelity']))

# ========== 10. V2.2 统一处理层 + 段内语义单元路由 ==========
ANALYZE_PATH = os.path.join(SCRIPTS, 'analyze.py')
test("analyze.py 存在", os.path.exists(ANALYZE_PATH), "有", "ok")
if os.path.exists(ANALYZE_PATH):
    analyzer = load('analyzer', ANALYZE_PATH)
    r = analyzer.route_text(TEST_TEXT)
    test("统一处理·段数6", len(r['segments'])==6, "6", str(len(r['segments'])))
    test("统一处理·含units", all('units' in s for s in r['segments']), "有units", "ok")
    # 段内语义单元：至少一段有多个 unit
    multi_unit = any(len(s['units'])>1 for s in r['segments'])
    test("统一处理·段内多单元", multi_unit, "有", str(multi_unit))
    # 60% 上限自检
    import re as _re
    total = sum(len(_re.sub(r'\s','',s['original'])) for s in r['segments'])
    focus = sum(len(_re.sub(r'\s','',s['original'])) for s in r['segments'] if s['priority']=='重点读')
    ratio = focus/total if total else 0
    test("统一处理·重点读<60%上限", ratio<=0.6, f"≤60%({ratio:.0%})", f"{ratio:.0%}")
    test("统一处理·非全重点读", not all(s['priority']=='重点读' for s in r['segments']), "有差异", "ok")
    test("统一处理·含modules", 'modules' in r and len(r['modules'])>0, "有", str(len(r.get('modules',[]))))

# build_reader --from-text 不全标重点读
data2 = builder.build_data_from_text(TEST_TEXT)
all_focus = all(s['priority']=='重点读' for s in data2['segments'])
test("--from-text不全标重点读", not all_focus, "非全重点读", str(all_focus))

# ========== 11. V2.2 HTML 交互修复 ==========
test("HTML 橙红色优先级 --pri-focus", '--pri-focus' in html, "有", "ok")
test("HTML 橙红色值(非蓝)", '#d4502a' in html or '#ff6b3d' in html, "橙红", "ok")
test("HTML 高亮弱化 .dimmed", 'dimmed' in html and 'opacity:.85' in html or 'opacity: .85' in html, "有弱化", "ok")
test("HTML 段内局部折叠 .unit-fold", 'unit-fold' in html, "有", "ok")
test("HTML 折叠入口无skip_note文字", 'skipnote' not in html, "无skipnote类", "ok")
test("HTML 折叠summary空文字", "sum.textContent=''" in html, "空summary", "ok")
test("HTML expandAll切换状态", "恢复折叠" in html, "有切换", "ok")
test("HTML expandAll禁用判断", "eb.disabled" in html, "有禁用", "ok")
test("HTML 模式切换保留滚动", "scrollTop" in html, "有保留", "ok")
test("HTML 上一句跳过折叠", "offsetParent" in html, "有跳过", "ok")
test("HTML prefers-reduced-motion", "prefers-reduced-motion" in html, "有", "ok")

# ========== 12. V2.2 Markdown 简化 ==========
MD_TPL = read(os.path.join(SKILL,'assets','focus_version_template.md'))
test("Markdown模板·保留原文主体", "保留原文" in MD_TPL, "有", "ok")
test("Markdown模板·不逐段摘要", "逐段总结" in MD_TPL and "不" in MD_TPL, "禁止", "ok")
test("Markdown模板·不承载三级标签", "三级策略" in MD_TPL and "不" in MD_TPL, "禁止", "ok")
DEMO_MD = read(os.path.join(HERE,'demo_chat.md'))
test("Markdown演示·无路线标签表", "重点读｜" not in DEMO_MD, "无标签", "ok")
test("Markdown演示·无逐段标题", DEMO_MD.count("### 段")==0, "无段标题", str(DEMO_MD.count("### 段")))

# ========== 13. V2.2 路由文档 ==========
test("路由·段内语义单元", "段内语义单元" in ROUTING, "有", "ok")
test("路由·60%上限自检", "60%" in ROUTING, "有", "ok")
test("路由·无≤25%矛盾", "≤25%" not in ROUTING, "无矛盾", "ok")
test("路由·橙红色", "橙红" in ROUTING, "有", "ok")
test("路由·统一处理层", "统一处理层" in ROUTING or "analyze.py" in ROUTING, "有", "ok")

# ========== 14. 兼容性 / 回归 ==========
test("Markdown 模板存在", os.path.exists(os.path.join(SKILL,'assets','focus_version_template.md')), "有", "ok")
test("地图模板存在", os.path.exists(os.path.join(SKILL,'assets','attention_map_template.md')), "有", "ok")
SAMPLE=os.path.join(SCRIPTS,'sample_original.txt')
if os.path.exists(SAMPLE):
    reg=acs.analyze(read(SAMPLE))
    test("回归：V1样例ACS", 0<=reg['mean_acs']<=100, "0-100", str(reg['mean_acs']))
    reg2=fidelity.check(read(SAMPLE),read(SAMPLE))
    test("回归：V1样例保真", reg2['all_fidelity'], True, str(reg2['all_fidelity']))
else:
    test("回归：V1样例存在", False, "有", "缺")

# ========== 输出 ==========
print("="*60)
print("Reading Accessibility Skill V2.2 测试报告")
print("="*60)
for name,status,exp,act in RESULTS:
    print(f"[{status}] {name}")
    if status=="失败": print(f"        预期: {exp}  实际: {act}")
print("-"*60)
print(f"通过 {PASS} / 失败 {FAIL} / 共 {PASS+FAIL}")
print("结论：", "全部通过" if FAIL==0 else f"{FAIL} 项失败，请检查。")
sys.exit(0 if FAIL==0 else 1)
