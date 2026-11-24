# 阅读辅助 Skill（Reading Accessibility）V2.1

面向"阅读困难"的文本辅助工具（非医学诊断）。以可计算的**文本结构复杂度（ACS）**为底座，对文本做结构简化、阅读优先级标注、逐段辅助与保真校验，输出更易集中注意力阅读的版本。

V2.1 在 V2.0 基础上做增量修复：段落丢失与模式失效、三层阅读机制重建、模块化理解框架、语义优先路由、交互修复、移动端适配、ACS 用户端隐藏、测试增强。

## 核心定位
- **文本结构复杂度**（ACS，客观可计算）≠ **用户主观阅读负荷**（因人而异）≠ **阅读优先级**（内容结构 + 用户目标）。三者分开处理，不可互换。
- 不做诊断，不承诺疗效，不将所有阅读困难归因于注意力。
- 用户端不暴露 ACS 数值、公式、权重、日志等开发者指标；只给自然语言提示。

## 三层阅读机制
1. **整篇模式**：完整阅读（全展示）/ 聚焦阅读（重点突出、低优先级可折叠但须提示）/ 快速浏览（结论先行、压缩处留展开入口）。
2. **段落级策略**：重点读（精读，保留论据/定义/结论/限定/反例）/ 简单读（速览）/ 可略读（按需跳读，原文可恢复）。不强制每篇三标签，不强制重点读占比。
3. **注意力辅助**：逐句高亮（默认关闭）、上一句/下一句、字号、行距、背景、折叠、原文↔辅助版切换、进度定位。全部独立于阅读策略运行。

## 功能
- 双层触发：`阅读辅助` / `无障碍阅读` / `阅读友好版` / `reading-access` + 自然语言意图识别；第二层 `专注阅读`/`打开阅读器` 触发 HTML 阅读器。
- ACS 结构复杂度评分（零依赖，内置 GB2312 一级字库 3755 字作常用字表）；支持中文、英文、中英混排切句。
- 语义优先路由：先判语义功能 → 评估重要性 → 检查定义/条件/结论/论据 → 结合上下文定级；不凭"因此/如果/更/不"等词直接定精读。
- 模块化理解框架：按语义结构组织互相关联模块（理论依据/核心问题/解决方法/方法局限等），不机械套"背景—问题—方法—结论"。
- 动态软约束：取消固定字数硬限，按语义完整性动态调整。
- 保真校验：数字/单位/否定/限定/条件/因果/比较/范围/关键定义/文学引文与译文 + 不确定性报告。
- HTML 交互阅读器：全段渲染、折叠去重、模式行为差异、逐句高亮（默认关）、字号 16/18/20/22/24px、行距、三主题背景、原文↔辅助版切换、一键展开全部、localStorage 持久、键盘+触摸操作、viewport 移动端、离线无依赖。
- 双模式输出：模式A 聊天内辅助（Markdown）/ 模式B 专注阅读器（独立 HTML）。

## 文件结构
```
reading_accessibility/
├── SKILL.md
├── references/   attention_model.md · transforms.md · routing.md
├── assets/       attention_map_template.md · focus_version_template.md · reader_template.html
├── scripts/      acs.py · fidelity_check.py · build_reader.py
└── tests/        run_tests.py · demo_data.json · demo_reader.html · demo_chat.md
```

## 快速开始
```bash
python scripts/acs.py input.txt                              # 结构复杂度
python scripts/fidelity_check.py original.txt rewritten.txt  # 保真校验
python scripts/build_reader.py data.json output.html         # 生成 HTML 阅读器
python tests/run_tests.py                                    # 运行 71 项测试
```

## 演示
```bash
# HTML 阅读器（模式B）：用浏览器打开
tests/demo_reader.html
# 聊天内辅助（模式A）：Markdown 输出
tests/demo_chat.md
```

## 测试
```bash
python tests/run_tests.py
# 通过 71 / 失败 0 / 共 71
```
覆盖：frontmatter 校验、触发、路由语义优先、三层机制、ACS 用户端隐藏、ACS 中英混排切句、切句保留原标点、测试文本 6 段、原文完整性、中英混排保留 karma/缘分、HTML 数据结构/字号变量/viewport/触摸目标/语义色/离线/localStorage/安全转义/折叠去重、保真（条件/因果/比较/范围/不确定性/翻译文本）、Markdown 与地图模板、V1 回归。

DOM 运行时行为（逐句高亮/折叠/切换）需浏览器验证，测试中已标注。

## 环境限制
- HTML 阅读器生成独立 `.html` 文件供浏览器打开；Skill 无法控制宿主聊天界面渲染。
- ACS 自动预检测采用方案B（description 智能匹配 + Skill 内建议），不声称自动监听。
- 不假设手机聊天框能运行任意 HTML/CSS/JS；没有能力不伪造，不把 Markdown 说成 HTML 阅读器。
- 降级优先级：原生组件 → HTML 预览 → 独立 HTML 文件 → Markdown。

## 许可
MIT
