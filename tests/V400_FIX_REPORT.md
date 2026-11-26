# V4.0 修复与验收报告：运行效率、双输出与底部导航

日期：2026-11-26
状态：仅本地修改与测试，未提交、未推送 GitHub。

## 1. 修复前核对与耗时归因

### 结构核对

- `SKILL.md` 同时包含触发、HTML 视觉细节、全部硬约束、目录、命令和版本历史，日常入口加载了非高频信息。
- `routing.md` 同时包含 Agent schema 与 HTML 视觉/交互规则；`transforms.md` 再次概述三层机制，存在重复说明。
- `route_text()` 已是统一结构化入口；原构建路径一次调用只分析一次，没有发现同一 HTML 构建中重复分析全文的证据。
- 原 Markdown 没有独立的统一数据渲染入口，容易让 Agent 在切换格式时重新组织全文。
- 固定底栏关联共 19 处：`footerEl`、`updatePos()`、`#prev/#next/#pos`、动态 `--bottom-gap`、footer `ResizeObserver` 和滚动安全区。
- 浏览器测试属于开发验收，不应由日常阅读默认触发。

### 脚本基线（447 字符现有样本，30 次中位数）

| 阶段 | V3.2.5 基线 |
|---|---:|
| ACS | 0.135 ms |
| `route_text()` | 0.252 ms |
| HTML 注入 | 0.065 ms |
| 原文保真检查 | 0.257 ms |

这些均为亚毫秒级，不能未经测量就把主要耗时归因于某个 Python 文件。主要可优化对象是模型需要读取的重复规范和重复语义组织；模型推理与 Work 调度耗时在当前环境无法直接测量。

## 2. 入口与高频文件长度对比

| 文件 | 修改前 | 修改后 | 用途变化 |
|---|---:|---:|---|
| `SKILL.md` | 5,202 字符 / 187 行 | **2,502 字符 / 69 行** | 仅保留触发、输出路由、单次分析、质量底线、按需文件表 |
| `references/routing.md` | 5,253 字符 / 193 行 | **3,768 字符 / 156 行** | 仅保留语义分析、schema、比例复核、标题和高风险规则 |
| `references/transforms.md` | 2,159 字符 / 102 行 | **2,089 字符 / 100 行** | 删除重复三层概述，仅保留变换与 Markdown |
| `references/reader.md` | 不存在 | **1,499 字符 / 38 行** | 仅 HTML 生成/验收时加载 |
| `references/attention_model.md` | 1,765 字符 / 77 行 | 不变 | 仅 ACS 调试时加载 |

按旧入口需要处理 SKILL + routing + transforms + attention 的口径，合计由 **14,379 字符**降为日常核心 SKILL + routing 的 **6,270 字符**，文本规模减少 **56.4%**。该比例是文档规模变化，不是运行速度提升比例。

## 3. 删除或合并的重复步骤

1. 从 SKILL 删除版本历史、完整目录、视觉细节和重复硬约束，保留必要质量底线。
2. 将 HTML 视觉、聚焦和滚动规范从 routing 移至 reader.md；语义与 HTML 不再混读。
3. 合并 transforms 与 routing 对三层机制的重复描述，语义规则只由 routing 定义。
4. Markdown 与 HTML 统一消费 `route_data.json`，不再分别组织或分析同一篇文章。
5. 日常流程不自动执行完整静态测试、CDP、截图和冗长开发报告。
6. 明确按意义完整划分语义块，不默认逐段生成解释；异常复核优先定向到异常块与相关上下文。
7. 删除 footer 高度测量、footer ResizeObserver、底栏阅读位置更新和按钮事件。

语义分析、比例复核、标题识别、原文保真和高风险文本保护未删除。

## 4. Markdown / HTML 最终触发规则

按优先级执行：

1. 用户明确要求 Markdown，或环境无法展示/交付 HTML → Markdown。
2. 用户明确要求 HTML、专注阅读器，或需要逐句高亮、折叠、字号/行距/主题调整 → HTML。
3. 短文本、普通段落、简单长句拆解 → Markdown。
4. 复杂长文、需要持续定位或分块阅读 → 建议并默认 HTML；用户拒绝 HTML 时用 Markdown。

两种输出共享原文与标题结构、Agent 阅读优先级、emphasis、保真结果及同一份结构化数据。Markdown 不模拟 HTML 控件。

### 实际双输出

只调用一次 `route_text()` 生成：

- `tests/route_data_v400.json`
- SHA-256：`28fa49cf831fa5f7bfefc53f1834667734bf9da2ca11b2cf99e887c0b9080244`

再由同一文件生成：

- `tests/demo_v400.md`
- `tests/demo_reader_v400.html`

新增 `scripts/build_markdown.py` 不导入 `analyze.py`，也不调用 `route_text()`，从代码路径上避免第二次全文分析。首次静态验收发现段间多了一个换行，已修正组装逻辑；随后验证 Markdown 正文去掉标题/加粗标记后与输入逐字一致。

## 5. 底部固定导航删除

已完整删除：

- `<footer id="readerFooter">`、`#prev`、`#next`、`#pos` 及 footer CSS。
- `footerEl` 和其 `ResizeObserver`。
- 上下句按钮事件和 `#pos` 文本更新。
- `updatePos()`，改为只更新顶部进度条的 `updateProgress()`。
- footer 顶线参与的安全视口计算。

保留：

- 点击句子聚焦、真实空白取消、Esc 清除、折叠、原文切换和三主题。
- 桌面方向键直接调用 `moveFocus(1/-1)`，不通过按钮；输入控件中不拦截按键。

底部留白改为 `--bottom-gap:calc(32px + env(safe-area-inset-bottom,0px))`。聚焦定位仅使用 header 底线与 `window.innerHeight - 8`，不再为固定底栏增加动态大留白。

## 6. 实际验收结果

### 静态与数据测试

**181 通过 / 0 失败**。覆盖原有语义规则、复核、保真，以及新增的无 footer、键盘直调、双输出同源、Markdown 逐字一致、标题、emphasis、无二次分析和日常/开发路径检查。

### 真实 Chrome 浏览器

**67 通过 / 0 失败**，全程无 JavaScript 异常。

| 验收项 | 实测证据 |
|---|---|
| 无遗留控件 | `footer/#readerFooter/#prev/#next/#pos` 均不存在；`main` padding-bottom = 32px |
| 桌面末行 | 48 句、24px、2.0 行距：末行 bottom = **827px**，视口 **900px**；完整可见 |
| 桌面末句聚焦 | `cur=47/48`，末句完整可见且不被 header 遮挡 |
| 390px 末行 | 末行 bottom = **771px**，视口 **844px**；无横向滚动 |
| 390px 末句聚焦 | `cur=47/48`，完整可见 |
| iframe 桌面 | 同源 srcdoc 宿主可访问，bottom = **827px**，无 footer |
| iframe 手机 | bottom = **771px**，无 footer、无横向溢出 |
| 原文保真 | `textContent === DATA.original_text`，无 strong、无辅助视觉残留 |
| 原文聚焦减淡 | dim = `rgb(95,95,95)`，active = `rgb(26,26,26)`，实际 computed color |
| 原有交互 | 点击句子、空白取消、Esc、折叠展开、原文切换、键盘导航、移动触摸均通过 |
| 三主题 | 白色、深色、护眼填充、减淡、对比度、字号调整均通过 |

结果与截图：`tests/browser_artifacts/browser_results.json`、`07-v400-mobile-scroll.png` 等。

iframe 测试是**浏览器同源宿主近似验证**，不是对 Work 专用预览容器的直接验证。

## 7. 实测性能

### 48 句 / 2,677 字符长文 fixture，20 次中位数

| 阶段 | 实测耗时 |
|---|---:|
| ACS | 2.574 ms |
| 一次 `route_text()` | 2.133 ms |
| Markdown（复用数据） | 0.293 ms |
| HTML（复用数据） | 0.963 ms |
| 原文保真检查 | 1.199 ms |

修改后小样本中，Markdown 渲染中位数 0.055ms，核心文档实际读取中位数 0.236ms。脚本测量受当前机器和运行噪声影响，不据此宣称端到端速度提升比例。

**无法测量部分**：Work 的 Agent 全文语义分析时间、模型读取长文档的实际推理时间、宿主调度与远程工具启动时间。上述数字只覆盖本地 Python、文件读取和模板渲染。

## 8. 尚未验证的问题

1. 用户已明确选择“暂时跳过”《声音与现象》论文样本步骤；本报告未将该论文或其他文本冒充指定样本。当前验收使用纽马克样例和 48 句合成 fixture。
2. 未直接控制 Work 专用内嵌预览；仅验证独立 Chromium、390px 移动视口和同源 iframe。若宿主禁止滚动或跨域限制 DOM，应提供独立 HTML 文件，不继续增加 padding 假装修复。
3. Firefox、Safari、真实移动设备及跨域宿主未逐一验证。
4. 未取得模型推理与 Work 调度的分阶段计时，不能声称具体端到端提速百分比。

## 9. 本地变更

- 入口与规范：`SKILL.md`、`README.md`、`references/routing.md`、`references/transforms.md`、新增 `references/reader.md`、`assets/focus_version_template.md`、`CHANGELOG.md`。
- 输出与交互：`assets/reader_template.html`、新增 `scripts/build_markdown.py`。
- 测试与产物：`tests/run_tests.py`、`tests/browser_test.mjs`、双输出 demo、route_data、浏览器结果与 V4.0 fixtures。
- 未修改 `scripts/analyze.py` 的语义分析、比例复核和块级统计实现。
- 未提交、未推送远程 GitHub。
