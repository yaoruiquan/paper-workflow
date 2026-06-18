# Word/会议格式产物协议

用于会议论文、模板 Word、双栏排版、公式/图表/表格格式、中英文稿转换等任务。目标是避免“内容写了但格式不合格”的情况。

## 排版路径选择

Stage 6 默认以投稿事实源决定排版路径：

- 如果用户要求 Word、会议提供 Word 模板，或最终提交物是 `.docx`，以 Word/DOCX 为主路径。
- 如果用户明确要求 LaTeX、会议提供 `.tex`/`.cls` 模板，或最终提交物必须是 PDF/LaTeX 源码，才进入 LaTeX 主路径。
- 如果用户要求不导出 PDF，不得生成任何 PDF，包括正式 PDF、临时 PDF、渲染检查 PDF 和页数检查 PDF。

LaTeX 可以作为 Word 主路径的辅助工具，但不能替代 DOCX 审查：

- 可用于维护 BibTeX、核查 DOI 和参考文献元数据；
- 可用于推导复杂公式表达，再转换为真实 Word OMML 公式；
- 可用于会议同时提供 LaTeX 模板时生成备用稿；
- 可用于后续会议要求 PDF 或 LaTeX 投稿时另建分支。

不推荐把 `Markdown -> LaTeX -> PDF/Word` 作为 Word 模板投稿的默认流程，因为该路径容易丢失 Word 模板样式、表格宽度、标题层级、引用上标和作者区细节。Word 模板投稿的验收标准是 DOCX 结构和模板一致性，不是 LaTeX 是否能编译。

## 格式事实源

生成 Word 前先确定格式事实源，并写入审查记录：

- 会议模板 `.docx` 或官方 checklist；
- 会议提供的 `.tex`/`.cls` 模板，仅在用户或会议要求 LaTeX/PDF 投稿时作为主事实源；
- 已通过的参考论文 `.docx` / `.pdf`；
- 用户明确提出的页数、双栏、单栏标题区、是否导出 PDF 等要求。

如果模板和聊天记录冲突，以模板、checklist 和用户最新明确要求为准。

## Word 生成规则

- 不覆盖旧版本；输出使用 `vN` 或语义化版本名。
- 作者、单位和通讯作者信息只有在用户提供或明确授权占位时才写入。若用户要求暂不处理作者信息，先推进正文、引用、图表和模板预排版，并在最终检查中保留作者区待补项。
- 标题、作者和单位如模板要求为单栏，正文从 Abstract/摘要开始再切换双栏。
- 图和表必须按目标栏宽设置固定宽度；不要让表格自动撑出栏宽。
- 表格列宽固定，长文本先压缩或合并列，不用缩小到不可读字号解决所有问题。
- 所有可能跨页的 Word 表格必须将首行设置为“在各页顶端以标题行形式重复出现”（OOXML: `w:tblHeader`）；不要只靠手工复制表头文本。
- 用户要求某个章节另起一页时，必须插入真实 Word 分页符（OOXML: `w:br w:type="page"`），并用 XML/DOCX 审查确认；不要只靠空段落推挤版面。
- 公式必须是真实 Word 公式对象；不要用纯文本、截图或伪表格模拟公式。
- 公式编号通常作为普通文本放在公式对象外，按模板要求右对齐。
- 中英文稿分开保留 Markdown 源文件；翻译稿不得修改实验数据和结论数值。
- 用户说不导出 PDF 时，不要导出 PDF；只做 DOCX 结构检查。页数、分页和视觉渲染只能记录为“需 Word/WPS 人工确认”，不能通过临时 PDF 规避该要求。
- Word/WPS 页数以用户在 Word/WPS 中打开后的结果为最终事实源；LibreOffice/UNO 的页数、分页或渲染结果不能替代 Word/WPS 验收，除非用户明确要求用它做辅助参考。
- 使用 LaTeX 辅助公式或参考文献时，最终仍需把公式、引用和参考文献落回 Word 文档并重新审查 DOCX。

## 页数压缩和版本管理

当用户反馈 Word 页数超出目标时，使用可回退的压缩路线：

1. 保留当前完整稿，不直接覆盖唯一版本。
2. 新建短版源稿和短版 Word，例如 `paper-en-compact-short-8page.md` 与 `paper-en-acm-template-short-8page.docx`。
3. 记录压缩前后词数差；优先压缩重复解释、过长枚举、边界说明和可合并段落，不删除实验数据、图表、参考文献覆盖或核心结论。
4. 小步压缩：用户只要求“再压缩一些”时，优先每轮减少约 150-250 英文词，而不是一次大幅删减。
5. 每轮重新生成 DOCX 后，运行 `audit_docx_format.py` 和 `check_acm_docx.py`；如果有章节强制换页要求，增加 `--require-page-break-before-heading "<heading>"`。
6. 在报告中明确：未做 PDF/渲染检查时，最终页数仍需 Word/WPS 人工确认。

## ACM Word 稳定路线

当模板为 ACM Word submission template 或用户反馈 ACM 前置区、CCS、Keywords、引用、三线表等格式问题时，使用以下固定路线：

1. 复制原始 `.docx` 模板为输出文件，不直接从空白 Word 新建。
2. 先解析模板前置区并建立锚点表，至少包含 `Title_document`、`Short Title`、`Subtitle`、`Authors`、`Affiliation`、`Abstract`、`CCSDescription`、`KeyWords`、`ACMRefHead`、`ACMRef`、首个 `Head1`、`ReferenceHead` 和 `Bib_entry`。
3. 作者、单位和通讯作者信息未提供时，保留 ACM 模板作者占位段，不删除作者区；提供后只替换对应文本，不改变样式。
4. Abstract 后必须先写 `CCS CONCEPTS`，再写 `Additional Keywords and Phrases`；不得残留 `Insert your first CCS term here`、`Insert comma delimited author-supplied keyword list` 等模板假内容。
5. 正文引用若用户或会议要求右上角样式，必须写成真实 superscript run，并设置小字号；不能只写普通文本 `[n]`。
6. 参考文献段落使用 ACM `Bib_entry` 自动编号时，源稿中的 `[n]` 只能用于校验，写入 Word 时必须去掉，避免出现自动编号加纯文本编号的重复。
7. 表格必须按会议要求生成三线表时，禁止使用 `TableGrid` 样式；只保留表头上边线、表头下边线和表尾下边线，不保留竖线或内部网格线；首行必须设置 `w:tblHeader`，确保跨页后第二页自动重复表头。
8. 生成后必须先运行通用 DOCX 结构审查，再运行 ACM 专项审查：

```bash
python3 scripts/audit_docx_format.py "<paper.docx>" --output "<docx-audit.md>"
python3 scripts/check_acm_docx.py "<paper.docx>" --output "<acm-audit.md>"
python3 scripts/check_acm_docx.py "<paper.docx>" --require-page-break-before-heading "INTRODUCTION" --output "<acm-audit.md>"
```

`check_acm_docx.py` 未通过时，不能交付 Word；必须修复后重新生成和审查。

## Documents 插件配合

如果当前 Codex 会话暴露了 Documents 插件或本地 `openai-primary-runtime/documents` skill 包，可使用其脚本增强 Word 工作流，但不能绕过用户的输出要求：

- 可使用 Documents skill 的 OOXML、表格、样式、图片和 section 审查脚本作为辅助检查。
- 若用户明确“不用 PDF / 只要 Word”，不得使用 `render_docx.py --emit_pdf`，也不得生成 PDF 作为页数检查。
- 若用户允许视觉检查，可用 `render_docx.py` 只输出 PNG 页面图进行内部 QA；最终仍只交付 DOCX，并在报告中记录 PNG 渲染检查结果。
- 若当前会话没有直接暴露 `documents.*` 编辑工具，则使用本 skill 的脚本和 OOXML 检查实现同等审查，不声称调用了不可用的插件 API。

## 公式检查

对 DOCX 进行 XML 级检查，而不是只看“插入了公式对象”：

- `m:oMath` 存在，说明有 Word 数学对象；
- 分式应出现 `m:f`；
- 下标应出现 `m:sSub`；
- 上标或上下标应出现 `m:sSup` / `m:sSubSup`；
- 点号、帽号等重音符号应出现 `m:acc`；
- 检查线性占位符是否消失，例如 `P_load(t)`、`m_dot`、`Delta t`。

经验规则：线性文本包在公式编辑器里仍然是不合格公式。

推荐用脚本固化检查：

```bash
python3 scripts/audit_docx_format.py "<paper.docx>" --output "stage/6-review/artifacts/review-1-format/docx-audit.md"
```

## 图表检查

论文图不是“能看见”就合格。图表进入正文前检查：

- 架构图要有清晰层级、能量流/控制流方向和语义分组；
- 文本不能出框、重叠或被裁切；
- 图例、坐标轴、单位和正文术语一致；
- 单栏图按目标栏宽检查像素和物理尺寸；
- caption 位置、编号和正文引用一致；
- 每张图都应能对应一个实验结果、模型结构或方法步骤，不放装饰图。

## 实验与论文闭环

写入论文前必须确认：

- 主结果、敏感性分析、消融或对比实验均有实际数据文件支撑；
- 每个 claim 能映射到表、图、公式、配置或参考文献；
- 如果实验过于草率，先回退到实验设计/运行阶段，不要直接扩写论文；
- 结果审计通过后再更新论文表格和结论；
- 结论数字必须与结果文件一致。

## 审查记录

每轮修复后写 Markdown 记录，至少包含：

- 生成的 Word / Markdown / 图表路径；
- 本轮修复的问题；
- 运行的验证命令；
- 结构检查结果，例如 sections、tables、figures、equations；
- 剩余风险，例如按用户要求未做 PDF 渲染级检查，页数和分页需在 Word/WPS 中人工确认。
