# V3.2.5 修复报告：交互修复、模式简化与性能优化

日期：2026-11-26
状态：本地交付，未推送远程仓库

## 测试结论

- 静态测试：**通过 170 / 失败 0 / 共 170**（`tests/run_tests.py`）
- 浏览器测试：**通过 64 / 失败 0 / 共 64**（`tests/browser_test.mjs`，真实 Chrome + CDP）
- 全程无浏览器脚本异常；截图与数据见 `tests/browser_artifacts/`。

## 一、文章末尾无法完整滚动

**根因**：`main` 固定 `padding-bottom:90px`，无法适配实际 footer 高度、字号、safe-area 与宿主容器；逐句聚焦使用 `scrollIntoView({block:'center'})` 不感知固定工具栏，末句/首句可能滚到栏下。

**修复**（`assets/reader_template.html`）：
1. CSS 自定义变量 `--bottom-gap` 兜底值 `calc(78px + env(safe-area-inset-bottom,0px))`；JS 用 `ResizeObserver` 监听 header/footer 实际尺寸，写入 `--bottom-gap` 与 `--header-height`，`main` 的 padding-bottom 与 `html` 的 `scroll-padding-bottom` 均引用该变量。
2. 删除 `scrollIntoView`，`focusAt` 改为安全视口定位：`safeTop=headerEl.getBoundingClientRect().bottom+8`、`safeBottom=footerEl.getBoundingClientRect().top-8`，用 `scrollBy` 平滑滚动；`.sent` 设置 `scroll-margin-top/bottom`。

**证据**（48 句滚动 fixture，24px 字号 + 2.0 行距）：
- 桌面 1280px：末句 `aboveFooter=true, belowHeader=true, right=true`，末 6 字"十像素留白。"完整可见；`--bottom-gap` 实测 `69px`（footer 实测 61px + 8，动态计算而非固定 78/90px）。
- 390px 手机模拟：同上全部通过，且 `scrollWidth≤clientWidth` 无横向滚动。
- 末句聚焦（cur=47/48）后 `aboveFooter=true`；首句聚焦（cur=0）不被工具栏遮挡。
- 截图：`browser_artifacts/07-v325-mobile-scroll.png` 等。

**环境限制**：若 ChatGPT 内嵌 iframe 预览禁止滚动（`scrolling=no` 或宿主裁剪），属宿主限制，阅读器无法覆盖；请将生成的 HTML 下载后独立在浏览器打开，功能完整。

## 二、取消三种阅读模式

**根因**：`完整阅读/聚焦阅读/快速浏览` 三模式未形成独立内容组织方式，聚焦与快速渲染逻辑基本相同。

**修复**：
1. 移除 `modeBtn` 与 `state.mode` 全部轮换逻辑；清理旧 localStorage（`delete savedState.mode`，不破坏其他键，升级无 JS 错误）。
2. 默认进入统一"辅助阅读"视图；精读/速览直接可见，跳读默认折叠并显示预览。
3. 保留"全部展开/恢复折叠"、"查看原文/返回辅助"、独立"逐句高亮"开关；三者可独立组合，互不冲突。

**证据**：静态测试 `V3.2.5·无模式按钮与旧模式逻辑`；浏览器测试 `统一视图无模式按钮`、`统一视图默认折叠跳读且原文/高亮可用`、`键盘导航不进入折叠内容`、`Esc清除聚焦且不修改设置`（原文/折叠/高亮/设置互不干扰）。

## 三、点击空白不能取消高亮

**根因**：`root` click 监听中 `if(ev.target!==root)return;` 只有点击 root 元素本身才触发；点击 `.block`/`.region`/正文留白均无效。此外初版修复用 `textHitAt`（caretRangeFromPoint）判断文字命中，但 caret API 在空白处会解析到"最近字符"，导致空白被误判为文字而无法清除。

**修复**（V3.2.5 最终方案，字符矩形验证）：
1. 删除 `ev.target!==root` 限制；交互控件（`.heading,summary,button,select,input,textarea,a,label,[data-control]`）提前返回。
2. `caretTextPos` + `charRectAt`：对 caret 解析到的字符构造 Range 取其实际矩形，仅当点击点落在字符矩形 ±2px 内才认定为"点了真实文字"；句子命中还需 `pointInRects` 验证点在 `.sent` 的行盒内。
3. 点击句子→聚焦；点击真实文字（含 `<strong>`、结构块文字）→不清除；点击正文空白、区域间距、阅读区边缘→`clearFocus()`；有选区（拖选）→不动作；Esc 保留。
4. 辅助视图与原文视图行为一致；触屏点击实测通过。

**证据**：浏览器测试 `真实空白点击清除聚焦但保留高亮功能`、`空白取消后可立即重新聚焦`、`移动端触摸聚焦后可点空白取消（mobileFocused/mobileCleared 均 true）`、`点击跳读预览只展开不进入聚焦`。

## 四、正文行宽不统一

**根因**：速览正文独立 `max-width:36em`，精读按父容器宽度布局，相邻段落行宽与左缘错位。另发现 `.region[data-pri="跳读"] .block` 是死规则（跳读块实际渲染在 `.skip-fold` 中，不在 region 内），skip 块 padding-left 只有 10px，文字起点与精读（3px 边框+10px=13px）、速览（2px+11px=13px）相差 1px。

**修复**：
1. 新增统一变量 `--body-max-width:36em`，`.block{max-width:var(--body-max-width)}` 对精读/速览/跳读一律生效；删除速览独立 max-width。
2. 死规则改为 `.skip-fold .block{padding-left:11px;background:transparent}`，三类正文文字左缘统一为距主容器 13px。

**证据**：浏览器测试 `普通正文统一列宽且左边缘对齐`：精读/速览/跳读 `left=280, textLeft=280, maxWidth=648px` 完全一致；18px/20px/24px 字号下 `--body-max-width` 为 em 单位随字号缩放，宽度基准一致。

## 五、原文视图高亮不减淡

**根因**：`#original-full .original-block{color:var(--fg)}` 选择器优先级高于 `.original-block.dimmed{color:var(--fg-dim)}`，减淡被覆盖；且原文容器存在未包裹在 `.original-block` 中的裸文本节点，仅给块加 `.dimmed` 无法覆盖全部正文。

**修复**：
1. 原文句子用 `.sent` span 包裹（纯视觉层），配合 `body.focus-active` 状态：`body.focus-active #original-full{color:var(--fg-dim)}` 统一减淡容器内全部文字（含裸文本节点），`body.focus-active #original-full .sent.active{color:var(--fg)}` 保持当前句正常色 + 柔和高亮背景。CSS 自定义变量管理，三主题各自取值，无内联样式。
2. 取消聚焦（空白点击/Esc/关高亮）后 `body.focus-active` 移除，全部文字恢复。
3. 只改 className 与 CSS，不改 `textContent`，逐字保真。

**证据**（实际 computed style，非类名判定）：
- 原文聚焦后：`dimColor=rgb(95,95,95)`（6 个块减淡）、`activeColor=rgb(26,26,26)`、`o.textContent===DATA.original_text` 逐字一致；Esc 后 `.sent.active,.original-block.dimmed` 归零。
- 对比度：浅色减淡 95/95/95 对白底 ≥4.5:1；深色减淡 rgb(163,163,163) 对深底 ≥4.5:1；护眼主题字号统一且 ≥4.5:1（浏览器测试逐项通过）。
- `切换原文定位当前阅读块而非页首`、`返回辅助版无重复渲染`、`原文模式无任何辅助标记或视觉残留` 均通过。

## 六、日常运行与开发测试的流程区别

| | 日常使用（默认） | 开发测试（需明确要求） |
|---|---|---|
| 语义分析 | 完整执行（精读比例、超阈值复核、零跳读复核、高风险保护不减） | 同左 |
| 仓库读取 | 不重复读取 GitHub 全部文件 | 按需比对版本 |
| 静态检查 | 仅跑输入/规则变化的项，已通过且未变的不重复 | 完整 170 项套件 |
| 浏览器验证 | 不默认启动 CDP/截图 | 完整 64 项交互验证 + 截图 + 数据记录 |
| 报告 | 结果简述 | 本报告级别的根因/证据/回归记录 |

对应描述已写入 `SKILL.md` / `README.md` / `references/routing.md` / `references/transforms.md`（静态测试 `V3.2.5·文档更新V3.2.5` 校验）。

## 七、新增回归测试

- 静态：V3.2.5 六项（无模式按钮/底部动态间距/安全视口定位/空白点击字符判定/交互控件豁免/原文 focus-active 减淡/统一列宽/文档更新）。
- 浏览器：统一视图、桌面与 390px 末句可见、首句不被遮挡、移动端触摸聚焦与空白取消、44px 触摸目标、三主题精读填充等。
- 测试材料：`tests/test_text_v23.txt`（纽马克翻译理论文本）+ 48 句滚动 fixture + 标题层级 fixture + 色差用例。《声音与现象》论文材料沿用同一模板管线，用户可直接用实际论文文本走 `build_reader.py --from-text` 生成。

## 八、尚未解决的问题

1. **宿主 iframe 滚动限制**：ChatGPT 等内嵌预览若禁用滚动，阅读器无法在宿主内滚动到底，需独立打开（见第一节说明）。
2. **caret 兼容性**：`caretRangeFromPoint`（Chromium/Blink）+ `caretPositionFromPoint`（Firefox）双路径已实现，但 Safari 旧版仅支持其中之一已覆盖；极老浏览器（IE）不在支持范围。
3. **跳读展开后的行宽**：已与精读/速览对齐（left=280 一致），但跳读内容展开时与折叠预览的视觉连续性仍可在未来打磨（预览行与正文行盒不同）。
4. **推送**：本次全部修改仅在本地（15 个文件修改 + 2 个新增），未 commit/未 push，等待用户授权。

## 修改文件清单

- `assets/reader_template.html` — 五项修复主体（CSS 变量、ResizeObserver、安全视口、字符矩形点击判定、统一列宽、原文减淡、模式删除）
- `scripts/build_reader.py` — except 分支增加 traceback 输出（便于诊断静默回退）
- `tests/run_tests.py` — V3.2.5 静态断言更新
- `tests/browser_test.mjs` — 主题状态恢复、列宽测量口径统一、末句测试 sents 引用修正、调试代码清理
- `tests/demo_reader_v232.html` — 用最新模板重新生成
- `SKILL.md` / `README.md` / `references/routing.md` / `references/transforms.md` — V3.2.5 描述同步
- 新增：`tests/browser_artifacts/scroll_fixture_v325.html`、`tests/browser_artifacts/07-v325-mobile-scroll.png`
