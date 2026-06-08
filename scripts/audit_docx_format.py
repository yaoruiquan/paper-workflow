#!/usr/bin/env python3
"""Audit DOCX structure for conference-paper formatting checks."""

from __future__ import annotations

import argparse
import re
import zipfile
from pathlib import Path


def read_document_xml(path: Path) -> str:
    with zipfile.ZipFile(path) as archive:
        return archive.read("word/document.xml").decode("utf-8")


def count_section_columns(xml: str) -> list[str]:
    columns: list[str] = []
    for section in re.findall(r"<w:sectPr\b.*?</w:sectPr>", xml, flags=re.S):
        match = re.search(r"<w:cols\b[^>]*w:num=\"([^\"]+)\"", section)
        columns.append(match.group(1) if match else "1")
    return columns


def remove_math_zones(xml: str) -> str:
    return re.sub(r"<m:oMath\b.*?</m:oMath>", "", xml, flags=re.S)


def summarize(xml: str) -> dict[str, object]:
    outside_math = remove_math_zones(xml)
    equation_numbers = re.findall(r"<w:t>\((\d+)\)</w:t>", outside_math)
    return {
        "sections": xml.count("<w:sectPr"),
        "section_columns": count_section_columns(xml),
        "tables": xml.count("<w:tbl>"),
        "figures": xml.count("<wp:inline") + xml.count("<wp:anchor"),
        "omath": xml.count("<m:oMath>"),
        "fractions": xml.count("<m:f>"),
        "subscripts": xml.count("<m:sSub>"),
        "superscripts": xml.count("<m:sSup>"),
        "subsuperscripts": xml.count("<m:sSubSup>"),
        "accents": xml.count("<m:acc>"),
        "equation_numbers": equation_numbers,
        "east_asia_fonts": sorted(set(re.findall(r'w:eastAsia="([^"]+)"', xml))),
    }


def add_expectation_issue(issues: list[str], label: str, actual: object, expected: object) -> None:
    if actual != expected:
        issues.append(f"{label}: expected {expected}, got {actual}")


def audit(xml: str, args: argparse.Namespace) -> tuple[dict[str, object], list[str]]:
    summary = summarize(xml)
    issues: list[str] = []

    if args.expect_sections is not None:
        add_expectation_issue(issues, "sections", summary["sections"], args.expect_sections)
    if args.expect_tables is not None:
        add_expectation_issue(issues, "tables", summary["tables"], args.expect_tables)
    if args.expect_figures is not None:
        add_expectation_issue(issues, "figures", summary["figures"], args.expect_figures)
    if args.expect_equations is not None:
        add_expectation_issue(issues, "Word math objects", summary["omath"], args.expect_equations)
    if args.expect_section_columns:
        expected_columns = [item.strip() for item in args.expect_section_columns.split(",") if item.strip()]
        add_expectation_issue(issues, "section columns", summary["section_columns"], expected_columns)

    if args.min_fractions is not None and summary["fractions"] < args.min_fractions:
        issues.append(f"fractions: expected at least {args.min_fractions}, got {summary['fractions']}")
    if args.min_subscripts is not None and summary["subscripts"] < args.min_subscripts:
        issues.append(f"subscripts: expected at least {args.min_subscripts}, got {summary['subscripts']}")
    if args.require_structured_math and summary["omath"]:
        structured = sum(int(summary[key]) for key in ("fractions", "subscripts", "superscripts", "subsuperscripts", "accents"))
        if structured == 0:
            issues.append("equations are OMML objects but contain no structured math nodes")
    if args.require_equation_numbers and not summary["equation_numbers"]:
        issues.append("no equation numbers were found outside OMML math zones")
    if args.require_east_asia:
        accepted_fonts = set(args.require_east_asia)
        found_fonts = set(summary["east_asia_fonts"])
        if not accepted_fonts.intersection(found_fonts):
            issues.append(f"eastAsia font not found; accepted {sorted(accepted_fonts)}, got {sorted(found_fonts)}")

    for marker in args.forbid_linear:
        if marker and marker in xml:
            issues.append(f"linear formula marker found: {marker}")
    return summary, issues


def markdown(path: Path, summary: dict[str, object], issues: list[str]) -> str:
    lines = [
        "# DOCX 格式审计",
        "",
        f"**文件**: `{path}`",
        f"**状态**: {'PASS' if not issues else 'BLOCK'}",
        "",
        "## 结构摘要",
        "",
        "| 项目 | 数值 |",
        "|---|---:|",
    ]
    for key in [
        "sections",
        "tables",
        "figures",
        "omath",
        "fractions",
        "subscripts",
        "superscripts",
        "subsuperscripts",
        "accents",
    ]:
        lines.append(f"| {key} | {summary[key]} |")
    lines.extend(
        [
            f"| section_columns | {', '.join(summary['section_columns']) or '-'} |",
            f"| equation_numbers | {', '.join(summary['equation_numbers']) or '-'} |",
            f"| eastAsia_fonts | {', '.join(summary['east_asia_fonts']) or '-'} |",
            "",
            "## 问题",
            "",
        ]
    )
    if issues:
        lines.extend(f"- {issue}" for issue in issues)
    else:
        lines.append("- 无")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="审计 DOCX 会议论文格式结构")
    parser.add_argument("docx_path")
    parser.add_argument("--output", help="将 Markdown 审计报告写入指定路径")
    parser.add_argument("--expect-sections", type=int)
    parser.add_argument("--expect-section-columns", help="逗号分隔的分栏数，例如 1,2")
    parser.add_argument("--expect-tables", type=int)
    parser.add_argument("--expect-figures", type=int)
    parser.add_argument("--expect-equations", type=int)
    parser.add_argument("--min-fractions", type=int)
    parser.add_argument("--min-subscripts", type=int)
    parser.add_argument("--require-structured-math", action="store_true")
    parser.add_argument("--require-equation-numbers", action="store_true")
    parser.add_argument("--require-east-asia", action="append", default=[], help="要求出现指定 eastAsia 字体，可重复，例如 SimSun 或 宋体")
    parser.add_argument("--forbid-linear", action="append", default=[], help="禁止出现的线性公式占位文本，可重复")
    args = parser.parse_args()

    path = Path(args.docx_path).expanduser().resolve()
    xml = read_document_xml(path)
    summary, issues = audit(xml, args)
    text = markdown(path, summary, issues)
    if args.output:
        Path(args.output).expanduser().write_text(text, encoding="utf-8")
    print(text)
    return 0 if not issues else 2


if __name__ == "__main__":
    raise SystemExit(main())
