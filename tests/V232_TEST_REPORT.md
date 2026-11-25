# V2.3.2 测试与交付记录

## 结果

- `python tests/run_tests.py`：**136 通过 / 0 失败**。
- `node tests/browser_test.mjs`：**34 通过 / 0 失败**。
- 浏览器：本机 Chrome headless，通过 Chrome DevTools Protocol 启动和操作，不是静态 CSS 检查。
- 自动化原文 diff：全局原文 `textContent === DATA.original_text`，通过。
- 390px 护眼截图人工可见性检查：未见文字裁切、控件重叠或横向溢出。

## 真实浏览器覆盖

- computed style：精读 `#FFF2E9` 暖底、3px 橙红区域边框、局部 `font-weight:700`；速览正常正文色/400 字重/无填充。
- 文字完整性：速览 DOM 文本与语义块原文逐字一致；无信息删减。
- 区域：区域数少于语义块数；长精读 fixture 出现 4 级填充衰减，块边框为 0、区域边框保留 3px。
- 跳读：预览关闭时可见；同主题跨段合并，跨主题不合并；展开后原文完整。
- 操作：全部展开/恢复折叠按钮状态与实际一致；无逐段原文按钮。
- 聚焦：真实鼠标点句，当前句高亮、其他块减淡、静态块填充让位；点击空白不改变焦点；关闭后恢复。
- 对比度：浅色减淡、深色高亮、深色减淡、护眼正文均通过 ≥4.5:1 断言；深色高亮与页面背景有可测亮度差。
- 导航：真实 ArrowRight 键盘事件不进入折叠内容。
- 原文：逐字一致、分段保留、包含折叠内容、无强调标记或辅助文本副本；切换定位当前阅读块。
- 模式：快速浏览不默认减淡速览；完整阅读直接展示全部跳读；模式切换保留阅读位置。
- 移动端：390×844 视口无横向溢出，工具栏触摸目标 ≥44px。

## 浏览器发现并已修复的问题

1. `.sent.hl-on:hover` 的选择器优先级覆盖当前句高亮；改为排除 `.active` 并提高当前句选择器优先级。
2. 精读深度背景选择器比“聚焦时填充让位”更具体；调整选择器后，实际 computed background 在聚焦时变为透明。
3. 测试取色等待时间不足 CSS 过渡时间；改为等待过渡完成后取 computed style，没有放宽视觉断言。

## 产物

- 演示：`tests/demo_reader_v232.html`
- 浏览器机器结果：`tests/browser_artifacts/browser_results.json`
- 截图：`01-light-initial.png`、`02-dark-focus.png`、`03-mobile-sepia.png`
- 长区域 fixture：`tests/browser_artifacts/region_fixture.html`

## 限制

- 真实浏览器验证目前覆盖 Chromium；未覆盖 Firefox、Safari 和真实触屏设备。
- 视觉合并依据语义块与角色；标题、表格、列表、原文译文对照尚无独立结构类型，复杂结构仍需 Agent 正确标界。
- 背景衰减采用四级离散色阶，不是连续数学渐变；这是为了减少视觉噪声并保持各主题对比稳定。
- 未部署网站，未推送远程仓库。
