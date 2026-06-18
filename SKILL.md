---
name: paper-workflow
description: 管理论文从选题、文献调研、实验设计、实验运行、大纲规划、草稿迭代到格式/逻辑/语言审查的 Stage-Gate 工作流。适用于用户想交互式确定论文题目、设计可维护实验项目、初始化论文项目、检查实验数据或图表、按页数规划大纲、撰写版本化草稿、按模板审查论文格式、核查实验闭环、生成/审查 Word 双栏会议论文、公式/图表/表格格式或中英文稿。
---

# paper-workflow

论文工作流 skill。执行时以阶段产物、Gate 记录和实验输出为事实源，不依赖聊天记忆推进论文。

## 入口判断

- 选题：用户有初步想法，需要交互式收敛成论文题目。
- 实验设计：用户需要可维护、可追溯的实验项目。
- 实验检查：用户要求判断实验结果、seed 稳定性、统计数据或图表是否合理。
- 大纲规划：用户给出页数、会议/期刊格式或目标篇幅，需要规划章节。
- 草稿写作：用户要求写 `v1`、`v2`、`v3` 或继续迭代草稿。
- 论文审查：用户要求审查格式、写作逻辑、实验完整性或语言。
- 回退：用户发现结果不支持故事线、实验不足或需要重做某阶段。

## 必读引用

只读取当前任务需要的引用文件：

- 总流程：`references/workflow.md`
- 阶段 Gate：`references/stage-gates.md`
- 实验项目规范：`references/experiment-project.md`
- 大纲和写作：`references/writing-outline.md`
- 审查流程：`references/review-protocol.md`
- Word/会议格式产物：`references/word-format-protocol.md`
- Gate 判定：`references/gate-protocol.md`
- 回退流程：`references/rollback-protocol.md`

## 固定命令

所有脚本使用 `python3`。

初始化论文项目：

```bash
python3 scripts/init_paper.py "<project_dir-or-paper-name>" --title "<论文标题>" --target-venue "<会议或期刊>" --pages 8 --profile simulation
```

如果 skill 目录 `.env` 中设置了 `PAPER_WORKFLOW_ROOT`，`project_dir` 传相对路径或论文名时，会自动创建到该总目录下；绝对路径仍按原路径创建。

查看当前状态：

```bash
python3 scripts/status.py "<project_dir-or-paper-name>"
```

执行阶段 Gate 自检：

```bash
python3 scripts/gate_check.py "<project_dir-or-paper-name>" --stage 3
```

创建回退记录：

```bash
python3 scripts/rollback.py "<project_dir-or-paper-name>" --from-stage 6 --to-stage 3 --reason "<回退原因>"
```

检查实验数据：

```bash
python3 scripts/check_stat.py "<project_dir>/experiment/results"
python3 scripts/check_seed_stability.py "<csv_path>" --group-col experiment --metric-col metric --seed-col seed --value-col value --output "<report.md>"
python3 scripts/summarize_results.py "<project_dir>/experiment/results"
python3 scripts/sign_test.py "<csv_path>" --baseline-col baseline --method-col method --lower-is-better --output "<report.md>"
python3 scripts/audit_docx_format.py "<paper.docx>" --output "<format-audit.md>"
```

## 最短执行骨架

1. 检查目标目录是否存在 `.paper-workflow.env`。
2. 如果不存在，先运行 `scripts/init_paper.py` 初始化项目，再进入实质工作。
3. 读取 `.paper-workflow.env`、`PAPER.md` 和当前 stage 目录。
4. 进入下一阶段前，先运行或人工执行当前阶段 Gate 检查。
5. 所有重要产物必须写入阶段文件，不能只留在聊天记录。
6. 写草稿时，每个版本必须放入 `stage/5-writing/drafts/vN/`。
7. 审查时，每一遍审查都必须写入 `stage/6-review/artifacts/review-*/report.md`。
8. 如果后续阶段发现实验缺口、故事线弱或 claim 无证据支撑，先创建 rollback 记录，再继续处理。
9. 如果用户要求 Word、会议模板、双栏排版、公式/图表格式或中英文稿，读取 `references/word-format-protocol.md` 后再生成产物。
10. Stage 6 排版默认以投稿事实源为准：若用户要求 Word 或会议只提供 Word 模板，DOCX 是主产物路径；LaTeX 只能作为公式、BibTeX、参考文献、备用 `.tex` 模板或 PDF/LaTeX 投稿要求下的辅助/分支路径，不得替代 DOCX 模板审查。
11. 若用户明确说“不用 PDF”“不要 PDF”“只要 Word”或类似要求，Stage 6 禁止生成 PDF，包括临时 PDF、渲染检查 PDF 和页数检查 PDF；只做 DOCX 结构审查，并在报告中把页数/分页标记为需 Word/WPS 人工确认。

## 阶段规则

1. Stage 1 选题在用户想法模糊时必须交互推进，产出 `topic-proposal.md`、`gap-analysis.md`、`literature-survey.md` 和 `feasibility-check.md`。
2. Stage 2 实验设计必须产出可维护实验方案，并在 `experiment/` 下保留 `data/`、`src/`、`configs/`、`scripts/`、`results/`、`figures/`、`logs/` 等目录。
3. Stage 3 跑实验必须记录原始输出、处理后汇总、图表文件、seed/config/commit 元数据和异常说明；根据 `PAPER_PROFILE` 执行统计检验、仿真约束验证或来源质量检查。
4. Stage 4 大纲必须包含页数预算、每节字数预算、格式假设、章节-实验映射和图/表/公式/结果来源计划。
5. Stage 5 写作必须按版本迭代：`v1` 填满结构，`v2` 统一术语和图表，`v3` 提升可读性，`v4+` 解决审稿人视角问题。
6. Stage 6 审查必须按顺序执行：第一遍格式，第二遍逻辑和实验完整性，第三遍语言。每一遍都必须留下 `.md` 审查报告。若最终要求是 Word，Stage 6 必须输出并审查 DOCX；只有会议明确要求 LaTeX/PDF，或用户要求生成备用 LaTeX 稿时，才进入 LaTeX 编译分支。Word-only 场景下不做 PDF 生成或 PDF 渲染检查。

## 审查原则

- 第一遍格式审查必须先提取模板或投稿格式要求，再审论文。
- 格式审查必须检查图表边距、caption 位置、公式是否为真实公式而非纯文本、公式编号、DOI/参考文献格式和正文引用格式。
- 第二遍逻辑审查必须检查 claim-evidence 闭环、实验完整性、baseline、消融、局限性和结论是否有数据支撑。
- 第三遍语言审查不能掩盖逻辑或数据问题；如果逻辑被阻塞，先 rollback，不要直接润色。
- 每次格式或实验修复都必须生成版本化产物，并写入对应 `.md` 记录，说明修复项、验证命令、通过项和剩余风险。
- 不能因为“文档已生成”就宣称完成；必须至少完成结构检查、实验检查或渲染级检查中的相应最小验证。若用户要求不生成 PDF，则以 DOCX 结构检查作为格式最小验证，不能额外导出 PDF 作为渲染检查。

## 脚本职责

- `scripts/init_paper.py`：创建论文项目脚手架。
- `scripts/status.py`：打印当前 stage 和 Gate 状态。
- `scripts/gate_check.py`：检查阶段必需产物并写入 gate checklist。
- `scripts/rollback.py`：写入回退记录并更新当前阶段。
- `scripts/check_stat.py`：检测结果文件缺失值、NaN/inf 和数值离群。
- `scripts/check_seed_stability.py`：按实验计算 mean/std/CV，标记不稳定指标。
- `scripts/summarize_results.py`：把 CSV/JSON 实验结果汇总成 Markdown 表格。
- `scripts/sign_test.py`：对 baseline 和 method 列执行配对 sign test。
- `scripts/audit_docx_format.py`：检查 Word 文档分栏、图表、表格、公式 OMML 结构和线性公式占位符。

## 事实源规则

如果聊天记录、`PAPER.md`、阶段产物和脚本输出冲突，以脚本输出和显式阶段产物为准。没有 `GATE.md` 或清晰 Gate 决策时，禁止声称某阶段已通过。
