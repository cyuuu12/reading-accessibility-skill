# 阅读辅助 Skill（Reading Accessibility）V2.3

面向"阅读困难"的文本辅助工具（非医学诊断）。以可计算的**文本结构复杂度（ACS）**为底座，对文本做结构简化、阅读优先级标注、逐段辅助与保真校验，输出更易集中注意力阅读的版本。

V2.3 在 V2.2 基础上：语义分析由 Agent（宿主模型）完成并按 schema 输出，Python 只做切分/校验/呈现；语义块替代逐句切分；60% 降为诊断不阻断；HTML 去标签视觉分层；减淡用颜色变量替代 opacity；跳读预览 + 相邻折叠合并；Merriam-Webster 误判防护。

## 核心定位
- **文本结构复杂度**（ACS，客观可计算）≠ **用户主观阅读负荷**（因人而异）≠ **阅读优先级**（内容结构 + 用户目标）。三者分开处理，不可互换。
- 不做诊断，不承诺疗效，不将所有阅读困难归因于注意力。
- 用户端不暴露 ACS 数值、公式、权重、日志等开发者指标；只给自然语言提示。

## 三层分工（V2.3）
| 层 | 职责 | 禁止 |
|----|------|------|
| **Agent**（宿主模型） | 根据全文上下文、论证关系和阅读目标判断语义功能及优先级 | 不得用关键词规则或脚本代替 |
| **Python**（analyze.py） | 原文切分、数据结构、边界校验、保真校验、诊断统计 | 不判断语义重要性 |
| **HTML** | 呈现与交互 | 不重新判断语义重要性 |

## 三种阅读行为
- **精读**：完整保留原文，核心论点适度加粗，不默认改写。
- **速览**：默认直接显示，保留核心意思，不等于折叠或逐段摘要。
- **跳读**：仅用于非必要的重复例证/次要背景，显示结构性预览（"这块是什么"），可展开原文，相邻同主题合并折叠。

## 功能
- 双层触发：`阅读辅助` / `无障碍阅读` / `阅读友好版` / `reading-access` + 自然语言意图识别。
- ACS 结构复杂度评分（零依赖，内置 GB2312 一级字库 3755 字）。
- Agent 语义分析 schema：blocks 含 para_idx/text/role/priority/preview；Python 校验三硬约束（精确定位/不重叠/全覆盖）。
- 语义块切分：一个块可含多句，相邻同类合并，默认不跨自然段；记录块数与句数供测试判定。
- 保守模式：无 Agent 分析时全文按原文呈现，不贴标签，不折叠。
- 60% 诊断不阻断：继续统计精读占比/段内切分率/问题段落，超阈值输出诊断但不阻断输出。
- 保真校验：数字/单位/否定/限定/条件/因果/比较/范围/关键定义/文学引文与译文 + 不确定性报告。
- HTML 视觉分层：无标签，精读橙红细边/速览正常/跳读灰色预览；减淡用 `--fg-dim` 颜色变量（非 opacity），对比度 ≥ 4.5:1。
- 聚焦高亮：默认关闭，开启后点句聚焦，当前句背景高亮，其他块减淡，导航跳过不可见内容。
- 字号 16/18/20/22/24px、行距、三主题背景、原文↔辅助版切换、全部展开/恢复折叠、localStorage 持久、键盘+触摸操作、viewport 移动端、离线无依赖。

## 文件结构
```
reading_accessibility/
├── SKILL.md
├── references/   attention_model.md · transforms.md · routing.md
├── assets/       attention_map_template.md · focus_version_template.md · reader_template.html
├── scripts/      acs.py · analyze.py · fidelity_check.py · build_reader.py
└── tests/        run_tests.py · analysis_v23.json · test_text_v23.txt · demo_reader_v23.html · demo_chat.md
```

## 快速开始
```bash
python scripts/acs.py input.txt                              # 结构复杂度
python scripts/fidelity_check.py original.txt rewritten.txt  # 保真校验
python scripts/analyze.py input.txt analysis.json            # 语义路由（需Agent分析JSON）
python scripts/build_reader.py --from-text input.txt output.html analysis.json  # 生成HTML阅读器
python tests/run_tests.py                                    # 运行 119 项测试
```

## 演示
```bash
# HTML 阅读器：用浏览器打开
tests/demo_reader_v23.html
# 聊天内辅助：Markdown 输出
tests/demo_chat.md
```

## 测试
```bash
python tests/run_tests.py
# 通过 119 / 失败 0 / 共 119
```
覆盖：frontmatter 校验、触发、Agent 语义分析 schema、语义块切分粒度、保守模式、诊断不阻断、Merriam-Webster 误判防护、原文完整性、中英混排、HTML 视觉分层（无标签/颜色变量减淡/跳读预览）、三模式差异、保真、Markdown 简化、V1 回归。

浏览器交互验证（高亮/减淡/折叠/导航）需人工或 Playwright，测试中已标注。

## 环境限制
- HTML 阅读器生成独立 `.html` 文件供浏览器打开；Skill 无法控制宿主聊天界面渲染。
- ACS 自动预检测采用方案B（description 智能匹配 + Skill 内建议），不声称自动监听。
- 降级优先级：原生组件 → HTML 预览 → 独立 HTML 文件 → 仅文件链接 → Markdown/纯文本。
- Agent 语义分析质量取决于宿主模型能力；无 LLM 时退回保守模式。

## 许可
MIT
