# V3.2.4 定向修复报告

## 0. 报告产物核对

仓库内未找到下列原始测试产物：

- `skill-test/input.txt`
- `skill-test/analysis.json`
- `skill-test/route_result.json`
- `skill-test/reader.html`

因此本报告不能复算“28 个语义块：精读 18、速览 10、跳读 0”的原始构成，也不能把 64.3% 或 48.8% 当作已验证数字。为避免臆造数据：

- 已把可复现机制写入 `tests/run_tests.py`，使用小型受控文本断言。
- 色差用例只使用用户给出的两个文字锚点构造：`tests/color_case_text_v324.txt` / `tests/color_case_analysis_v324.json`。
- 可用“缘分”文本的块构成输出在 `tests/block_stats_v324.json`，仅作机制示例，不是原始 28 块报告。

## 1. 精读占比与超阈值复核

### 根因

旧 `_diagnostic()` 按自然段聚合：只要段内出现精读块，就把整段字符计入精读，因此无法衡量真实精读文本比例。块数量占比和字符占比本就不等价；若“块占比 64.3%、字符占比 48.8%”属实，更可能说明精读块平均较短、长论证段被整段降级，而不是简单“精读标太多”。

### 修复

`scripts/analyze.py`：

- 直接遍历语义块，按块级 `priority` 计算非空白字符。
- 按 `role` / `structure` / `heading_level` 过滤标题、分隔符等结构性块。
- 输出 `focus_char_ratio`、`focus_block_ratio`、`skip_char_ratio`、`skip_block_count`、`content_block_count`、`structural_block_count`、`threshold`。
- 输出 `block_lengths`（每块字符数、句数、角色、是否结构性块）。
- 保留旧 `focus_ratio`，并明确标注为段级聚合兼容口径。
- 默认阈值 0.60，可用 `analysis.focus_threshold` 或 `route_text(focus_threshold=...)` 配置。
- 超阈值返回 `blocked_pending_agent_review`；Agent 复核结果通过 `analysis.review` 传入，最多两次。
- 复核后仍超阈值必须记录 `exception_reason`，状态为 `exception_retained`；无例外原因为 `exception_missing`，不得伪装合格。

测试文本 `tests/analysis_v23.json` 的精读字符占比为 66.667%，已按机制记录复核例外，而不是降级必要论证或提高阈值。

## 2. 零跳读适用性复核

### 根因

零跳读本身不能证明分类错误。可能原因包括：例证与解释被过度合并、重复例子未独立成块、背景确实必要、看似举例实为关键论证，或长段被整段降级。

### 修复

- 较长正文（非空白字符 ≥1000）且 `skip_block_count == 0` 触发复核。
- Agent 复核后仍为零跳读，必须通过 `analysis.skip_review.exception_reason` 记录原因。
- 没有合理跳读内容时允许零跳读；不会自动制造跳读块。
- 回归覆盖两个分支：长文零跳读触发复核；短文零跳读不误判。

## 3. 标题层级

### 根因

旧 schema 只有策略角色，标题会被当作普通块进入视觉区域；保守模式也没有结构识别。

### 修复

`scripts/analyze.py`：

- 新增 `role:"标题"`、`heading_level`；0 为文档主标题，1 为一级章节，2 为二级章节。
- Agent 误给标题 priority 时，Python 强制置空。
- 标题不参与统计、不合并跳读、不进精读比例。
- 保守模式只识别独立成行、明确编号/章节结构的标题；书名引文不误判。

`assets/reader_template.html`：

- `heading_level 0/1/2/3+` 渲染 `<h1>`/`<h2>`/`<h3>`/更深层级。
- 标题不加区域底色、不折叠，并作为结构边界。
- 原文模式保留原始标题文字、顺序和换行。

## 4. 空白/Esc 取消聚焦

### 根因

已有 `clearFocus()`，但没有任何用户入口；原文视图也未实现逐句高亮。

### 修复

- 阅读区空白点击判定固定为：事件目标是 `#root` 本身，且不命中 `.sent`、`details`、`[data-control]`，且无文字选区。
- 点击空白清除当前句聚焦、减淡和 `body.focus-active`，高亮功能保持开启。
- Esc 只清除聚焦，不改字号、主题、模式或滚动位置。
- 原文视图用 sentence span 提供点击目标，只叠加视觉层；`textContent` diff 仍逐字一致。
- 跳读预览点击只展开/收起，不聚焦。
- 浏览器真实操作覆盖：句子聚焦 → 空白取消 → 重新聚焦 → Esc；工具栏、折叠、原文切换、移动端触摸均有测试。

## 5. 指定区间色差

### 排查结论

当前 GitHub 模板已经不是四级衰减，而是统一 `--focus-fill`。原始报告四件套缺失，无法定位原始 28 块中的真实区间。

按用户给出的文字锚点构造受控用例：

- 区间起点锚点：`为了说明表述能够指向对象`
- 区间终点锚点：`胡塞尔的分析并没有彻底解决这些问题`
- 两端分别位于两个连续精读块，中间无标题或结构性边界。

真实 Chrome computed style 记录在 `tests/browser_artifacts/color_case_styles.json`：

| 主题 | 起点/终点 background-color | border-left-color | opacity | --focus-fill | 同区 |
|---|---|---|---|---|---|
| 白色 | `rgb(255, 242, 233)` / 同值 | `rgb(204, 100, 55)` | 1 | `#FFF2E9` | 是 |
| 深色 | `rgb(58, 42, 30)` / 同值 | `rgb(228, 138, 95)` | 1 | `#3A2A1E` | 是 |
| 护眼 | `rgb(239, 224, 200)` / 同值 | `rgb(157, 91, 53)` | 1 | `#EFE0C8` | 是 |

状态检查：

- 高亮关闭：两块背景一致。
- 高亮开启未选中：不进入 `focus-active`，背景一致。
- 高亮开启且选中：两块同步让位为 `rgba(0,0,0,0)`。
- 模式切换后恢复：两块背景仍一致。

因此未重新引入衰减，也未强行统一所有分类；如原始文本后续出现真实色差，应先检查 Agent 的块分类、结构边界或聚焦状态，不能先改样式。

局部截图：

- `tests/browser_artifacts/04-color-case-light.png`
- `tests/browser_artifacts/05-color-case-dark.png`
- `tests/browser_artifacts/06-color-case-sepia.png`

## 6. 可用文本统计对照

`tests/block_stats_v324.json` 是仓库内“缘分”文本的核对清单，不是原始哲学论文 28 块数据：

- 总块数 7；结构性块 0；带 priority 正文块 7。
- 精读 4、速览 1、跳读 2。
- `focus_char_ratio` 0.66667；`focus_block_ratio` 0.57143。
- `skip_char_ratio` 0.24113；`skip_block_count` 2。
- 块长度（字符/句）：
  - 理论定义 精读 126/3
  - 方法论 精读 66/1
  - 概念定义 精读 30/1
  - 例证 速览 39/1
  - 引文 跳读 28/2
  - 引文 跳读 74/1
  - 局限 精读 60/1

## 7. 修改文件

- `scripts/analyze.py`
- `assets/reader_template.html`
- `references/routing.md`
- `SKILL.md`
- `README.md`
- `tests/run_tests.py`
- `tests/browser_test.mjs`
- `tests/analysis_v23.json`
- `tests/color_case_text_v324.txt`
- `tests/color_case_analysis_v324.json`
- `tests/color_case_reader_v324.html`
- `tests/block_stats_v324.json`

## 8. 测试结果

- 静态/数据自动化：**161 通过 / 0 失败**。
- 真实 Chrome：**54 通过 / 0 失败**。
- 浏览器机器结果：`tests/browser_artifacts/browser_results.json`。
- 覆盖块级统计、标题、复核、例外、零跳读、空白/Esc、原文聚焦、色差三主题、移动端触摸和既有回归。

## 9. 尚未解决与限制

- 原始哲学论文 28 块数据缺失，无法还原报告中的块构成和真实色差上下文。
- 色差用例是受控 fixture，不声称已复现原始论文渲染。
- 复核仍由 Agent 发起并提交结果；Python 记录和校验状态，不代替 Agent 判断语义。
- 零跳读长文阈值目前固定为 1000 个非空白字符，后续如需按文本类型调整，应记录依据。
- 浏览器验证覆盖 Chromium；未覆盖 Firefox、Safari 和真实触屏设备。
