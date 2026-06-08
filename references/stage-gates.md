# 阶段关卡检查清单

## 阶段 1：选题关卡

必需产物：

- `artifacts/topic-proposal.md`
- `artifacts/gap-analysis.md`
- `artifacts/literature-survey.md`
- `artifacts/core-refs.bib`
- `artifacts/feasibility-check.md`

出现以下情况应阻塞：

- 贡献点只是换了应用领域，没有方法或证据层面的新意。
- 贡献点只是调参。
- 核心数据或算力预算不可行。
- 预期主张无法被评估。

## 阶段 2：实验设计关卡

必需产物：

- `artifacts/experiment-design.md`
- `artifacts/evaluation-protocol.md`
- `artifacts/baseline-plan.md`
- `artifacts/project-check.md`

出现以下情况应阻塞：

- 基线无法运行。
- 指标定义不清晰。
- 缺少随机种子、配置或代码提交记录。
- 预计计算成本超过可用时间。

## 阶段 3：实验运行关卡

通用必需产物：

- `artifacts/main-results/`
- `artifacts/experiment-log.md`
- `artifacts/anomaly-report.md`

按 `PAPER_PROFILE` 增加以下必需产物：

| Profile | 追加必需产物 |
|---|---|
| `generic` | `artifacts/statistical-tests/` |
| `ml-experiment` | `artifacts/statistical-tests/`, `artifacts/seed-stability-report.md` |
| `simulation` | `artifacts/validation-report.md`, `artifacts/result-audit.md` |
| `engineering-design` | `artifacts/constraint-check.md`, `artifacts/sensitivity/` |
| `review` | `artifacts/evidence-table.md`, `artifacts/source-quality-check.md` |

出现以下情况应阻塞：

- 主结果包含未解释的 `NaN` 或无穷值。
- 缺少关键表格或图。
- 多随机种子方差没有解释。
- 结果不支持核心主张，且没有回退记录。

## 阶段 4：大纲关卡

必需产物：

- `artifacts/outline.md`
- `artifacts/page-budget.md`
- `artifacts/storyline.md`
- `artifacts/section-experiment-map.md`
- `artifacts/artifact-plan.md`

出现以下情况应阻塞：

- 任一主要主张没有映射到实验、图、表或引用。
- 页数预算与会议或期刊约束冲突。
- 大纲中没有体现实验内容。

## 阶段 5：写作关卡

必需产物：

- `drafts/v1/`
- `drafts/v2/`
- `drafts/v3/`
- `checkpoints/content-freeze.md`

出现以下情况应阻塞：

- 任一章节为空。
- 草稿包含占位图或未解决的 `[TODO]`。
- 章节之间术语不一致。
- 关键证据缺失时仍要求内容冻结。

## 阶段 6：审查关卡

必需产物：

- `artifacts/review-1-format/report.md`
- `artifacts/review-2-logic/report.md`
- `artifacts/review-3-language/report.md`
- `artifacts/final-check/submission-ready.md`

出现以下情况应阻塞：

- 格式审查发现参考文献、公式、图或表与模板要求不一致。
- 逻辑审查发现无证据支撑的主张。
- 实验完整性审查发现缺少基线、消融或统计检验。
- 试图用语言润色掩盖未解决的证据问题。
