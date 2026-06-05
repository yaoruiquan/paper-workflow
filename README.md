# paper-workflow

`paper-workflow` 是一个论文全流程管理 skill，用阶段产物和关卡检查推进选题、实验设计、实验运行、大纲、写作和审查。它适合需要把论文过程沉淀成可维护项目的人使用，而不是只在聊天里临时讨论。

## 安装位置

当前 skill 源目录：

```text
/Users/yao/.claude/skills/paper-workflow
```

Codex 安装位置：

```text
/Users/yao/.codex/skills/paper-workflow
```

如果通过软链接安装，修改 `.claude/skills/paper-workflow` 会同步反映到 Codex。重启 Codex 后，新会话会重新加载 skill。

## 什么时候使用

- 你有论文想法，需要交互式收敛题目。
- 你要设计实验，并希望项目目录、数据、结果和图表可追溯。
- 你要检查实验数据是否合理，包括缺失值、离群值、多随机种子稳定性和显著性。
- 你要按页数或投稿格式规划大纲。
- 你要按 `v1`、`v2`、`v3` 迭代写草稿。
- 你要审查论文格式、逻辑闭环、实验完整性和语言质量。

## 初始化论文项目

在 skill 目录下运行：

```bash
python3 scripts/init_paper.py "<project_dir>" --title "<论文标题>" --target-venue "<会议或期刊>" --pages 8 --field "<研究领域>"
```

初始化后会生成：

```text
project/
├── .paper-workflow.env
├── PAPER.md
├── bibliography/
├── experiment/
│   ├── configs/
│   ├── data/
│   ├── src/
│   ├── scripts/
│   ├── results/
│   ├── figures/
│   └── logs/
└── stage/
    ├── 1-topic/
    ├── 2-experiment-design/
    ├── 3-experiment-run/
    ├── 4-outline/
    ├── 5-writing/
    ├── 6-review/
    └── rollback/
```

## 常用命令

查看项目状态：

```bash
python3 scripts/status.py "<project_dir>"
```

检查某阶段关卡：

```bash
python3 scripts/gate_check.py "<project_dir>" --stage 3
```

创建回退记录：

```bash
python3 scripts/rollback.py "<project_dir>" --from-stage 6 --to-stage 3 --reason "<回退原因>"
```

检查实验结果：

```bash
python3 scripts/check_stat.py "<project_dir>/experiment/results"
python3 scripts/check_seed_stability.py "<csv_path>" --group-col experiment --metric-col metric --seed-col seed --value-col value
python3 scripts/summarize_results.py "<project_dir>/experiment/results"
python3 scripts/sign_test.py "<csv_path>" --baseline-col baseline --method-col method
```

## 配置说明

`.env.example` 是 `.paper-workflow.env` 的配置参考。核心字段：

- `PAPER_TITLE`：论文标题。
- `TARGET_VENUE`：目标会议、期刊或交付格式。
- `PAGE_LIMIT`：页数限制。
- `FIELD`：研究领域。
- `CURRENT_STAGE`：当前阶段编号。
- `CURRENT_STAGE_NAME`：当前阶段中文名称。
- `AUTHOR_MODE`：作者模式，默认 `single`。
- `EXPERIMENT_TRACKING`：实验追踪方式，默认 `local`。

## 工作原则

- 所有重要结论必须写入阶段文件，不能只留在聊天记录。
- 进入下一阶段前必须检查当前阶段关卡。
- 实验必须记录数据、配置、随机种子、代码提交、输出路径和异常。
- 写作前必须建立章节-实验证据映射。
- 审查顺序固定为：格式、逻辑和实验完整性、语言。
- 如果后续阶段发现证据不足，先回退，再继续写作。

## 参考文件

- `references/workflow.md`：总流程。
- `references/stage-gates.md`：阶段关卡。
- `references/experiment-project.md`：实验项目规范。
- `references/writing-outline.md`：大纲和写作。
- `references/review-protocol.md`：审查协议。
- `references/gate-protocol.md`：关卡判定。
- `references/rollback-protocol.md`：回退协议。
