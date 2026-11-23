# 阅读辅助 Skill（Reading Accessibility）V2.0

面向"阅读困难"的文本辅助工具（非医学诊断）。以可计算的**文本结构复杂度（ACS）**为底座，对文本做结构简化、阅读优先级标注、逐段辅助与保真校验，输出更易集中注意力阅读的版本。

## 核心定位
- **文本结构复杂度**（ACS，客观可计算）≠ **用户主观阅读负荷**（因人而异）≠ **阅读优先级**（内容结构 + 用户目标）。三者分开处理。
- 不做诊断，不承诺疗效，不将所有阅读困难归因于注意力。

## 功能
- 双层触发：`阅读辅助` / `无障碍阅读` / `阅读友好版` / `reading-access` + 自然语言意图识别；第二层 `专注阅读`/`打开阅读器` 触发 HTML 阅读器。
- ACS 结构复杂度评分（零依赖，内置 GB2312 一级字库 3755 字作常用字表）。
- 阅读路由：**重点读** / **简单读** / **可略读**（加粗标签 + 通俗原因，无符号）。
- 动态软约束：取消固定字数硬限，按语义完整性动态调整。
- 保真校验：数字/单位/否定/限定/条件/因果/比较/范围 + 不确定性报告。
- HTML 交互阅读器：逐句高亮、字号/行距/背景调节、原文↔辅助版切换、折叠、进度定位、键盘操作、离线无依赖。
- 三种阅读模式：完整阅读 / 聚焦阅读 / 快速浏览。

## 文件结构
```
reading_accessibility/
├── SKILL.md
├── references/   attention_model.md · transforms.md · routing.md
├── assets/       attention_map_template.md · focus_version_template.md · reader_template.html
├── scripts/      acs.py · fidelity_check.py · build_reader.py
└── tests/        run_tests.py + 样例
```

## 快速开始
```bash
python scripts/acs.py input.txt                              # 结构复杂度
python scripts/fidelity_check.py original.txt rewritten.txt  # 保真校验
python scripts/build_reader.py data.json output.html         # 生成 HTML 阅读器
python tests/run_tests.py                                    # 运行 37 项测试
```

## 测试
```bash
python tests/run_tests.py
# 通过 37 / 失败 0
```

## 环境限制
- HTML 阅读器生成独立 `.html` 文件供浏览器打开；Skill 无法控制宿主聊天界面渲染。
- ACS 自动预检测采用方案B（description 智能匹配 + Skill 内建议），不声称自动监听。

## 许可
MIT
