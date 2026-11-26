---
name: reading-accessibility
description: 阅读困难辅助工具。当用户阅读长文或密集文本感到吃力、走神、读不下去，或明确说"阅读辅助/无障碍阅读/阅读友好版"时使用。对文本做结构简化、阅读优先级标注、逐段辅助和保真校验，输出更易集中注意力阅读的版本，可生成离线 HTML 专注阅读器。不做医学诊断，不承诺疗效。普通摘要、翻译、润色、知识问答不默认触发。
---

# 阅读辅助 Skill（Reading Accessibility）V4.0

面向阅读困难的文本辅助，不做医学诊断，不承诺疗效。文本结构复杂度、用户主观阅读负荷、内容重要性不可互换；ACS 由脚本计算，用户端默认隐藏。

## 1. 何时触发

- 主触发：`阅读辅助`；辅助触发：`无障碍阅读` / `阅读友好版` / `reading-access`。
- 具体阅读意图："这篇文章我读不下去，帮我处理一下。"、"我总是读着读着就走神。"、"这段话太密了，看着很累。"、"帮我一段一段读。"、"我读完前面就忘了后面。"
- 普通摘要、翻译、润色、知识问答不默认触发；"阅读障碍是什么？"等知识问答不调用。

## 2. Markdown / HTML 选择

按以下顺序判断，用户明确选择优先：

1. 用户明确要求 Markdown，或当前环境无法展示/交付 HTML → **Markdown**。
2. 用户明确要求 HTML、专注阅读器，或需要逐句高亮、折叠、字号/行距/主题调整 → **HTML**。
3. 短文本、普通段落、简单长句拆解 → **Markdown**。
4. 复杂长文、需要持续定位或分块阅读 → 建议并默认 **HTML**；用户拒绝 HTML 时用 Markdown。

两种输出共用同一份结构化分析结果，包含原文与标题结构、精读/速览/跳读判断、emphasis 和保真结果。切换格式不得重新分析全文。Markdown 使用标题、段落和少量加粗，不模拟动态高亮、折叠或控件；HTML 按 `references/reader.md` 呈现。

## 3. 日常路径（默认）

```text
原文输入
→ scripts/acs.py 计算结构指标（无需读取算法文档）
→ Agent 一次全文语义分析
→ scripts/analyze.py 一次生成 route_data.json（校验、统计、模块数据共用）
→ 必要定向复核
→ scripts/fidelity_check.py 与原文完整性检查
→ 同一份 route_data.json 生成 Markdown 或 HTML
→ 直接交付，不附开发诊断
```

- **第一步语义分析由你（模型）完成**，按 `references/routing.md` 的 schema 输出，不得用关键词规则或脚本代替。
- 一次阅读任务只进行一次完整语义分析。块划分以意义完整为准，不为追求细粒度逐句拆块，不默认逐段生成解释。
- Markdown 使用 `scripts/build_markdown.py route_data.json output.md`；HTML 使用 `scripts/build_reader.py route_data.json output.html`。两者不得分别重新路由原文。
- 精读超阈值、长文零跳读或文本校验失败时，只复核异常块及必要上下文；确需改变全局理解才重新分析全文。最多两次复核，例外保留必须记录原因。
- 复核通过 `analysis.review` / `analysis.skip_review` 传回同一 `analyze.py` 入口，不能绕过比例、emphasis、边界和原文定位校验。
- 不默认输出 ACS 数值、开发者诊断、冗长报告；不启动 Chrome、CDP、截图或完整回归测试。

## 4. 不可跳过的质量底线

- 保留标题层级和全部原文；不删数字、单位、否定、限定、条件、因果、比较、范围，不合并两个否定。
- 速览不删减、不改写；跳读仅用于非必要补充，保留预览与完整展开。
- 精读比例、零跳读适用性按 `routing.md` 复核；不得为降比例牺牲必要定义、推理、证据、反例或结论。
- emphasis 必须落在同一块内：每块至多 3 处、每处至多 15 字、全文非空白字符至多 5%。
- 药品说明书、合同、法律等高风险文本默认全文可见，不折叠警示、限定和关键条件。
- 全局原文必须与输入逐字一致并恢复原始分段。保真工具无法确认的语义等价性须标为未自动验证，不声称绝对保真。
- 未获授权不公开网页、不部署 Pages、不推送远程仓库；原文和敏感内容不发往第三方。

## 5. 按需读取文件

| 文件 | 何时读取 |
|---|---|
| `references/routing.md` | Agent 语义分析、异常复核时的唯一语义/schema 权威来源 |
| `references/transforms.md` | 需要文字变换或生成 Markdown 时 |
| `references/reader.md` | 生成、修改或验收 HTML 阅读器时 |
| `references/attention_model.md` | 仅调试 ACS 公式、阈值或已知限制时 |
| `README.md` / `tests/` / `CHANGELOG.md` | 仅开发、版本核对或用户明确要求时 |

## 6. 开发测试路径（仅用户明确要求）

运行 `python tests/run_tests.py` 和必要的 `node tests/browser_test.mjs`，记录真实 computed style、截图、性能及失败原因。开发与日常路径共用 `analyze.py`、`build_markdown.py`、`build_reader.py`，不另建语义规则。
