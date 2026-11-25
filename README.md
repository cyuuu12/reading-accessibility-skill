# 阅读辅助 Skill（Reading Accessibility）V3.2.4

面向“阅读困难”的文本辅助工具（非医学诊断）。Agent 负责全文语义分析与阅读策略，Python 负责切分、校验、保真、统计与复核状态，HTML 只负责呈现与交互。

V3.2.4 修复哲学论文测试报告暴露的五类问题：块级统计口径、超阈值与零跳读复核、标题层级、空白/Esc 取消聚焦、色差区间定位。保留 V2.3.2 的统一视觉区域、emphasis、原文逐字恢复、三主题与移动端能力。

## 阅读策略与统计

| 行为 | 呈现 |
|---|---|
| 精读 | 低饱和暖底、橙红区域边框、局部 `<strong>`；不整段加粗或染色 |
| 速览 | 无填充、蓝灰细边、正常正文色和字重；不删字、不改写，默认直接可读 |
| 跳读 | 中性灰底、始终可见的内容预览、可逆折叠；同主题相邻块合并 |
| 标题/分隔符 | 结构，不参与策略比例；标题渲染 h1/h2/h3 并断开视觉区域 |

块级诊断输出：
- `focus_char_ratio`：精读非空白字符 / 带 priority 的正文非空白字符。
- `focus_block_ratio`：精读块数 / 带 priority 的正文块数。
- `skip_char_ratio`、`skip_block_count`、`content_block_count`、`structural_block_count`。
- `block_lengths`：每块字符数、句数、角色和是否结构性块，用于识别长论证段被误降级。
- `focus_ratio` 仅保留旧版段级聚合结果作兼容对照，不再用于阈值判断。

默认阈值 `0.60`，可配置。超阈值时 `output_status=blocked_pending_agent_review`；Agent 最多复核两次，仍超阈值必须记录 `exception_reason`。长文零跳读触发适用性复核，复核后仍为零必须记录原因；不得机械降级，也不得强制制造跳读。

## 标题层级

- Agent schema 使用 `role:"标题"` + `heading_level`；0 为文档主标题，1 为一级章节，2 为二级章节，3+ 按实际递增。
- 标题 `priority` 由 Python 强制置空，不进精读比例，不自动折叠，不加精读暖底或速览边框。
- HTML 渲染 `<h1>`/`<h2>`/`<h3>`，作为连续视觉区域边界。
- 保守模式只识别独立成行且编号/章节结构明确的标题；不确定时保留原文。
- 全局原文模式保留原始标题文字、顺序和换行。

## 聚焦与原文

- 高亮默认关闭；开启后点句聚焦，再次点句重新聚焦。
- 点击阅读区空白、按 Esc 或移动端 tap 空白可取消聚焦；高亮功能保持开启。
- 空白判定固定为：事件目标在 `#root` 本身，且不命中 `.sent`、`details`、`[data-control]`，且无文字选区。
- 辅助视图和原文视图都支持逐句聚焦；原文视图只叠加视觉层，不改文本节点。
- 聚焦时静态暖底/灰底让位；关闭或取消后完整恢复。
- 全局原文与输入逐字一致、恢复分段，并清除加粗、强调色、填充、边框和区域标记。
- 保留字号、行距、主题、三种模式、全部展开/恢复折叠、离线阅读和移动端适配。

## 文件结构

```text
reading_accessibility/
├── SKILL.md
├── references/   attention_model.md · transforms.md · routing.md
├── assets/       attention_map_template.md · focus_version_template.md · reader_template.html
├── scripts/      acs.py · analyze.py · fidelity_check.py · build_reader.py
└── tests/
    ├── run_tests.py                    # 零依赖静态/数据测试
    ├── browser_test.mjs                # Node + Chrome CDP 真实交互测试
    ├── analysis_v23.json               # 缘分文本 Agent 分析与复核例外示例
    ├── color_case_text_v324.txt        # 色差区间受控 fixture
    ├── color_case_analysis_v324.json
    ├── color_case_reader_v324.html
    ├── block_stats_v324.json           # 可用文本块构成与长度分布
    ├── V324_FIX_REPORT.md              # 本次五项修复报告
    ├── demo_reader_v232.html           # 演示阅读器
    └── browser_artifacts/              # 浏览器结果、样式记录、截图、fixtures
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

浏览器测试使用 Node 内置 WebSocket 和 Chrome DevTools Protocol，不依赖 Playwright、Selenium 或 npm 第三方包。它执行真实鼠标、键盘、触摸事件，读取 computed style，检查三主题对比度、标题层级、原文 diff、无残留切换、色差区间和 390px 移动端布局，并输出截图。

## 验证结果

- 静态/数据自动化：**161 通过 / 0 失败**。
- 真实 Chrome：**54 通过 / 0 失败**，结果见 `tests/browser_artifacts/browser_results.json`。
- 色差样式记录与局部截图：`tests/browser_artifacts/color_case_styles.json`、`04-color-case-light.png`、`05-color-case-dark.png`、`06-color-case-sepia.png`。
- Markdown 保持轻量方案，不模拟复杂交互，不承载三级标签。

## 边界

- 原始哲学论文报告的 `skill-test/input.txt`、`analysis.json`、`route_result.json`、`reader.html` 不在仓库中；无法复算报告中的 28 块构成。色差用例使用用户给出的两个文字锚点构造，不冒充原始数据。
- 不诊断、不承诺疗效；ACS 只表示文本结构复杂度，用户端默认隐藏数值。
- 无 Agent 分析时进入保守模式：全文呈现、不贴标签、不折叠。
- 能力检测按序降级：原生组件 → HTML 预览 → 独立 HTML 文件 → 仅文件链接 → 仅 Markdown／纯文本。
- frontmatter 保持 `name: reading-accessibility`。
- 浏览器验收覆盖 Chromium；Firefox、Safari 和真实触屏设备尚未逐一验证。

## 许可
MIT
