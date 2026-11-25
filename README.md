# 阅读辅助 Skill（Reading Accessibility）V2.3.2

面向“阅读困难”的文本辅助工具（非医学诊断）。Agent 负责全文语义分析与阅读策略，Python 负责切分、校验、保真和诊断，HTML 只负责呈现与交互。

V2.3.2 在 V2.3 基础上增量优化视觉与操作：统一强度连续视觉区域、区域起点间隙、局部关键文字强调、速览零信息损失基准态、深色聚焦高亮、全局原文逐字恢复且无辅助视觉残留，并新增真实 Chrome 浏览器验收。

## 三种阅读行为

| 行为 | 呈现 |
|---|---|
| 精读 | 低饱和暖底、橙红区域边框、局部 `<strong>`；不整段加粗或染色 |
| 速览 | 无填充、蓝灰细边、正常正文色和字重；不删字、不改写，默认直接可读 |
| 跳读 | 中性灰底、始终可见的内容预览、可逆折叠；同主题相邻块合并 |

连续同策略块共享视觉区域。精读背景保持统一强度，不做衰减；每个区域起点保留 10px 间隙，边框自然收口，无外框、阴影或卡片化。标题、列表、引文、对照、表格和分隔线按 Agent 角色信息断区；合并不改变原文顺序、语义块数据或策略。

## Agent 语义分析与 emphasis

第一步语义分析由宿主模型完成，不得用关键词规则或脚本替代。schema 详见 `references/routing.md`。

可选 `emphasis` 使用相对语义块的 `[start,end)` 精确字符区间：
- Python 校验原文匹配、越界、重叠和块内归属。
- 每块最多 3 处，每处最多 15 字，全文最多 5%，超限按 `score` 截断。
- HTML 用文本节点与 `<strong>` 安全插入，不把原文拼成 HTML。
- 无有效强调时保持普通正文，不强行制造重点。

## 聚焦与原文

- 高亮默认关闭；开启后点句聚焦，当前句跨行连续高亮，其他块通过 `--fg-dim` 减淡。
- 聚焦时静态暖底/灰底让位，避免背景叠加；关闭后完整恢复。
- 白色、深色、护眼主题均要求高亮和减淡文字对比度 ≥4.5:1。
- 导航跳过折叠/隐藏内容；折叠、展开、模式及原文切换后清理或恢复焦点。
- 取消逐段“查看原文”；全局原文模式与输入逐字一致、恢复分段并包含全部折叠内容。
- 保留字号、行距、主题、三种模式、全部展开/恢复折叠、离线阅读和移动端适配。

## 文件结构

```text
reading_accessibility/
├── SKILL.md
├── references/   attention_model.md · transforms.md · routing.md
├── assets/       attention_map_template.md · focus_version_template.md · reader_template.html
├── scripts/      acs.py · analyze.py · fidelity_check.py · build_reader.py
└── tests/
    ├── run_tests.py                 # 零依赖静态/数据测试
    ├── browser_test.mjs             # Node + Chrome CDP 真实交互测试
    ├── analysis_v23.json            # Agent 分析与 emphasis 示例
    ├── test_text_v23.txt
    ├── demo_reader_v232.html        # V2.3.2 演示阅读器
    └── browser_artifacts/           # 浏览器结果 JSON、截图、长区域 fixture
```

## 使用

```bash
python scripts/acs.py input.txt
python scripts/fidelity_check.py original.txt rewritten.txt
python scripts/analyze.py input.txt analysis.json
python scripts/build_reader.py --from-text input.txt output.html analysis.json
python tests/run_tests.py
node tests/browser_test.mjs   # 需本机 Chrome/Edge；可用 CHROME_PATH 指定
```

浏览器测试使用 Node 内置 WebSocket 和 Chrome DevTools Protocol，不需要 Playwright、Selenium 或 npm 第三方包。它检查 computed style、实际鼠标点击、键盘导航、三主题对比度、原文逐字一致与无视觉残留、长区域统一填充和 390px 移动端布局，并输出截图。

## 验证结果

- 静态/数据自动化：**137 通过 / 0 失败**。
- 真实 Chrome：**40 通过 / 0 失败**，结果见 `tests/browser_artifacts/browser_results.json`。
- 截图：浅色初始、深色聚焦、390px 护眼移动端。
- Markdown 保持 V2.2 的轻量方案，不模拟复杂交互，不承载三级标签。

## 边界

- 不诊断、不承诺疗效；ACS 只表示文本结构复杂度，用户端默认隐藏数值。
- 无 Agent 分析时进入保守模式：全文呈现、不贴标签、不折叠。
- 能力检测按序降级：原生组件 → HTML 预览 → 独立 HTML 文件 → 仅文件链接 → 仅 Markdown／纯文本。
- frontmatter 保持 `name: reading-accessibility`。
- 浏览器验收覆盖 Chromium；Firefox、Safari 和真实触屏设备尚未逐一验证。
- 结构边界依赖 Agent 的语义块/角色信息，复杂标题、表格和原文译文对照尚无独立结构类型。

## 许可
MIT
