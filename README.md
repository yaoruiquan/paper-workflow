# paper-workflow

Codex/Claude 论文工作流 skill，用于把论文从选题、实验、写作推进到 Word 格式审查。

## 目录

- `SKILL.md`：入口规则和阶段流程
- `references/`：Stage-Gate、实验、写作、Word 格式和审查协议
- `scripts/`：项目初始化、实验检查、DOCX/ACM 格式审查脚本
- `assets/`：可复用模板和辅助资源

## 常用命令

```bash
python3 scripts/init_paper.py "<project>" --title "<title>" --target-venue "<venue>" --pages 8 --profile simulation
python3 scripts/status.py "<project>"
python3 scripts/gate_check.py "<project>" --stage 3
python3 scripts/audit_docx_format.py "<paper.docx>" --output "<docx-audit.md>"
python3 scripts/check_acm_docx.py "<paper.docx>" --output "<acm-audit.md>"
```

检查指定标题前是否有真实分页符：

```bash
python3 scripts/check_acm_docx.py "<paper.docx>" --require-page-break-before-heading "INTRODUCTION" --output "<acm-audit.md>"
```

## Word-only 规则

- 用户要求只要 Word 时，不生成 PDF，也不用 PDF 做页数或渲染检查。
- Word/WPS 页数以用户打开后的结果为准；LibreOffice/UNO 不能替代 Word/WPS 验收。
- 页数压缩要保留完整稿和短版稿，记录词数差，小步压缩后重新跑 DOCX/ACM 审查。
- 跨页表格必须设置重复表头：`w:tblHeader`。

## 本地校验

```bash
python3 -m py_compile scripts/*.py
python3 scripts/init_paper.py /private/tmp/paper-workflow-smoke --title "Smoke" --target-venue "Test" --pages 6 --profile simulation
python3 scripts/status.py /private/tmp/paper-workflow-smoke
```
