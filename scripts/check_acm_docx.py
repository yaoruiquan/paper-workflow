#!/usr/bin/env python3
"""Audit ACM Word submission-template details in a DOCX file."""

from __future__ import annotations

import argparse
import html
import re
import zipfile
from dataclasses import dataclass
from pathlib import Path
from xml.etree import ElementTree as ET


NS = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "wp": "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing",
}

AUTHOR_PLACEHOLDERS = [
    "First Author's Name*",
    "First author's affiliation, an Institution with a very long name, xxxx@gmail.com",
    "Second Author's Name",
    "Second author's affiliation, possibly the same institution, xxxx@gmail.com",
    "Third Author's Name",
    "Third author's affiliation, possibly the same institution, xxxx@gmail.com",
]

FORBIDDEN_PLACEHOLDERS = [
    "Insert your first CCS term here",
    "Insert your second CCS term here",
    "Insert your third CCS term here",
    "Insert comma delimited author-supplied keyword list",
    "Keyword number 2",
    "Keyword number 3",
    "Keyword number 4",
]


@dataclass
class Paragraph:
    style: str
    text: str


@dataclass
class CitationRun:
    text: str
    superscript: bool
    half_points: int | None


def read_zip_text(path: Path, name: str) -> str:
    with zipfile.ZipFile(path) as archive:
        return archive.read(name).decode("utf-8")


def read_optional_zip_text(path: Path, name: str) -> str:
    with zipfile.ZipFile(path) as archive:
        if name not in archive.namelist():
            return ""
        return archive.read(name).decode("utf-8")


def root_from_xml(xml: str) -> ET.Element:
    return ET.fromstring(xml.encode("utf-8"))


def qn(ns: str, name: str) -> str:
    return f"{{{NS[ns]}}}{name}"


def paragraph_style(p: ET.Element) -> str:
    p_style = p.find("./w:pPr/w:pStyle", NS)
    if p_style is None:
        return ""
    return p_style.attrib.get(qn("w", "val"), "")


def text_of(element: ET.Element) -> str:
    parts: list[str] = []
    for node in element.findall(".//w:t", NS):
        if node.text:
            parts.append(node.text)
    return "".join(parts)


def paragraphs(doc_root: ET.Element) -> list[Paragraph]:
    result: list[Paragraph] = []
    for p in doc_root.findall(".//w:body/w:p", NS):
        result.append(Paragraph(style=paragraph_style(p), text=text_of(p).strip()))
    return result


def citation_runs(doc_root: ET.Element) -> list[CitationRun]:
    runs: list[CitationRun] = []
    for run in doc_root.findall(".//w:body//w:r", NS):
        text = text_of(run).strip()
        if not re.fullmatch(r"\[\d+\]", text):
            continue
        vert = run.find("./w:rPr/w:vertAlign", NS)
        sz = run.find("./w:rPr/w:sz", NS)
        half_points: int | None = None
        if sz is not None:
            raw = sz.attrib.get(qn("w", "val"))
            if raw and raw.isdigit():
                half_points = int(raw)
        runs.append(
            CitationRun(
                text=text,
                superscript=vert is not None and vert.attrib.get(qn("w", "val")) == "superscript",
                half_points=half_points,
            )
        )
    return runs


def style_index(paragraphs_: list[Paragraph], style: str) -> int | None:
    for idx, paragraph in enumerate(paragraphs_):
        if paragraph.style == style:
            return idx
    return None


def text_index(paragraphs_: list[Paragraph], text: str) -> int | None:
    for idx, paragraph in enumerate(paragraphs_):
        if paragraph.text == text:
            return idx
    return None


def reference_entries(paragraphs_: list[Paragraph]) -> list[Paragraph]:
    ref_start = None
    for idx, paragraph in enumerate(paragraphs_):
        if paragraph.style == "ReferenceHead" or paragraph.text.upper() == "REFERENCES" or paragraph.text == "参考文献":
            ref_start = idx
            break
    if ref_start is None:
        return []
    return [
        paragraph
        for paragraph in paragraphs_[ref_start + 1 :]
        if paragraph.text and paragraph.style in {"Bibentry", "Bib_entry"}
    ]


def body_text_before_references(paragraphs_: list[Paragraph]) -> str:
    texts: list[str] = []
    for paragraph in paragraphs_:
        if paragraph.style == "ReferenceHead" or paragraph.text.upper() == "REFERENCES" or paragraph.text == "参考文献":
            break
        texts.append(paragraph.text)
    return "\n".join(texts)


def count_header_footer_text(path: Path) -> tuple[int, list[str]]:
    texts: list[str] = []
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        parts = [name for name in names if re.fullmatch(r"word/(header|footer)\d+\.xml", name)]
        for part in parts:
            xml = archive.read(part).decode("utf-8")
            texts.append(text_of(root_from_xml(xml)).strip())
    return len(texts), texts


def has_page_field(doc_xml: str) -> bool:
    return bool(re.search(r"<w:instrText[^>]*>[^<]*(PAGE|NUMPAGES)[^<]*</w:instrText>", doc_xml, flags=re.I))


def table_blocks(doc_xml: str) -> list[str]:
    return re.findall(r"<w:tbl\b.*?</w:tbl>", doc_xml, flags=re.S)


def table_grid_issues(doc_xml: str) -> list[str]:
    issues: list[str] = []
    tables = table_blocks(doc_xml)
    for idx, table in enumerate(tables, start=1):
        if "TableGrid" in table or "Table Grid" in table:
            issues.append(f"table {idx}: uses TableGrid style instead of a three-line table")
        for edge in ("left", "right", "insideV"):
            if re.search(rf"<w:{edge}\b[^>]*w:val=\"single\"", table):
                issues.append(f"table {idx}: has vertical/grid border {edge}=single")
        if not re.search(r"<w:top\b[^>]*w:val=\"single\"", table):
            issues.append(f"table {idx}: missing top rule")
        if len(re.findall(r"<w:bottom\b[^>]*w:val=\"single\"", table)) < 2:
            issues.append(f"table {idx}: expected header and final bottom rules")
        first_row_match = re.search(r"<w:tr\b.*?</w:tr>", table, flags=re.S)
        if not first_row_match or "<w:tblHeader" not in first_row_match.group(0):
            issues.append(f"table {idx}: first row is not marked as a repeated header row")
    return issues


def paragraph_has_page_break(paragraph: ET.Element) -> bool:
    return any(
        br.attrib.get(qn("w", "type")) == "page"
        for br in paragraph.findall(".//w:br", NS)
    )


def normalize_heading_for_check(text: str) -> str:
    text = re.sub(r"^\s*\d+(\.\d+)*\s+", "", text.strip())
    return re.sub(r"\s+", " ", text).upper()


def page_break_before_heading(doc_root: ET.Element, heading: str) -> bool | None:
    target = normalize_heading_for_check(heading)
    previous: ET.Element | None = None
    for paragraph in doc_root.findall(".//w:body/w:p", NS):
        if normalize_heading_for_check(text_of(paragraph)) == target:
            return paragraph_has_page_break(paragraph) or (
                previous is not None and paragraph_has_page_break(previous)
            )
        previous = paragraph
    return None


def audit(path: Path, args: argparse.Namespace) -> tuple[dict[str, object], list[str]]:
    doc_xml = read_zip_text(path, "word/document.xml")
    doc_root = root_from_xml(doc_xml)
    paras = paragraphs(doc_root)
    full_text = "\n".join(paragraph.text for paragraph in paras)
    refs = reference_entries(paras)
    citations = citation_runs(doc_root)
    body_text = body_text_before_references(paras)
    body_citation_nums = sorted(set(int(match) for match in re.findall(r"\[(\d+)\]", body_text)))
    header_footer_count, header_footer_texts = count_header_footer_text(path)

    summary: dict[str, object] = {
        "paragraphs": len(paras),
        "tables": doc_xml.count("<w:tbl>"),
        "figures": doc_xml.count("<wp:inline") + doc_xml.count("<wp:anchor"),
        "reference_entries": len(refs),
        "body_citations": ",".join(map(str, body_citation_nums)) or "-",
        "citation_runs": len(citations),
        "citation_superscript": sum(1 for run in citations if run.superscript),
        "citation_small": sum(1 for run in citations if run.half_points is not None and run.half_points <= args.max_citation_half_points),
        "header_footer_parts": header_footer_count,
        "header_footer_nonempty": sum(1 for text in header_footer_texts if text),
        "table_repeated_headers": sum(
            1
            for table in table_blocks(doc_xml)
            if (first_row := re.search(r"<w:tr\b.*?</w:tr>", table, flags=re.S))
            and "<w:tblHeader" in first_row.group(0)
        ),
    }

    issues: list[str] = []

    for heading in args.require_page_break_before_heading or []:
        found = page_break_before_heading(doc_root, heading)
        summary[f"page_break_before_{normalize_heading_for_check(heading).lower().replace(' ', '_')}"] = (
            "missing-heading" if found is None else str(found)
        )
        if found is None:
            issues.append(f"heading not found for required page break: {heading}")
        elif not found:
            issues.append(f"missing page break before heading: {heading}")

    if args.expect_single_column:
        for section in re.findall(r"<w:sectPr\b.*?</w:sectPr>", doc_xml, flags=re.S):
            match = re.search(r"<w:cols\b[^>]*w:num=\"([^\"]+)\"", section)
            if match and match.group(1) != "1":
                issues.append(f"section columns: expected 1, got {match.group(1)}")

    if not args.allow_missing_author_placeholders:
        for placeholder in AUTHOR_PLACEHOLDERS:
            if placeholder not in full_text:
                issues.append(f"missing author placeholder: {placeholder}")

    for placeholder in FORBIDDEN_PLACEHOLDERS:
        if placeholder in full_text:
            issues.append(f"template placeholder remains: {placeholder}")

    title_idx = style_index(paras, "Titledocument")
    first_author_idx = text_index(paras, AUTHOR_PLACEHOLDERS[0])
    abstract_idx = style_index(paras, "Abstract")
    ccs_idx = style_index(paras, "CCSDescription")
    keywords_idx = style_index(paras, "KeyWords")
    first_head_idx = style_index(paras, "Head1")
    ordered = [idx for idx in [title_idx, first_author_idx, abstract_idx, ccs_idx, keywords_idx, first_head_idx] if idx is not None]
    if len(ordered) != 6 or ordered != sorted(ordered):
        issues.append("front matter order should be title -> author placeholders -> abstract -> CCS -> keywords -> first heading")

    ccs_texts = [p.text for p in paras if p.style == "CCSDescription"]
    if not ccs_texts:
        issues.append("missing CCSDescription paragraph")
    elif not ccs_texts[0].startswith("CCS CONCEPTS"):
        issues.append("CCSDescription should start with 'CCS CONCEPTS'")

    keyword_texts = [p.text for p in paras if p.style == "KeyWords"]
    if not keyword_texts:
        issues.append("missing KeyWords paragraph")
    elif not keyword_texts[0].startswith("Additional Keywords and Phrases:"):
        issues.append("KeyWords should start with 'Additional Keywords and Phrases:'")

    if len(refs) < args.min_references:
        issues.append(f"references: expected at least {args.min_references}, got {len(refs)}")
    duplicate_text_labels = [ref.text for ref in refs if re.match(r"^\[\d+\]\s+", ref.text)]
    if duplicate_text_labels:
        issues.append(f"reference entries contain source-side text labels: {len(duplicate_text_labels)}")

    if args.require_citation_coverage and refs:
        expected_nums = set(range(1, len(refs) + 1))
        actual_nums = set(body_citation_nums)
        missing = sorted(expected_nums - actual_nums)
        undefined = sorted(actual_nums - expected_nums)
        if missing:
            issues.append(f"references not cited in body: {missing}")
        if undefined:
            issues.append(f"body citations without reference entries: {undefined}")

    if not citations:
        issues.append("no bracket citation runs found")
    else:
        not_superscript = [run.text for run in citations if not run.superscript]
        not_small = [
            run.text
            for run in citations
            if run.half_points is None or run.half_points > args.max_citation_half_points
        ]
        if not_superscript:
            issues.append(f"citation runs are not superscript: {len(not_superscript)}")
        if not_small:
            issues.append(f"citation runs exceed {args.max_citation_half_points / 2:.1f}pt or lack explicit size: {len(not_small)}")

    if args.require_three_line_tables:
        issues.extend(table_grid_issues(doc_xml))

    if not args.allow_header_footer_text:
        nonempty = [text for text in header_footer_texts if text]
        if nonempty:
            issues.append(f"header/footer text should be empty, found: {nonempty}")

    if has_page_field(doc_xml):
        issues.append("page number field found in document body")

    return summary, issues


def markdown(path: Path, summary: dict[str, object], issues: list[str]) -> str:
    lines = [
        "# ACM DOCX 专项审计",
        "",
        f"**文件**: `{path}`",
        f"**状态**: {'PASS' if not issues else 'BLOCK'}",
        "",
        "## 摘要",
        "",
        "| 项目 | 数值 |",
        "|---|---:|",
    ]
    for key, value in summary.items():
        lines.append(f"| {html.escape(str(key))} | {html.escape(str(value))} |")
    lines.extend(["", "## 问题", ""])
    if issues:
        lines.extend(f"- {issue}" for issue in issues)
    else:
        lines.append("- 无")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="检查 ACM Word submission template 常见格式问题")
    parser.add_argument("docx_path")
    parser.add_argument("--output", help="将 Markdown 审计报告写入指定路径")
    parser.add_argument("--min-references", type=int, default=10)
    parser.add_argument("--max-citation-half-points", type=int, default=17, help="引用字号上限，Word half-points；17 = 8.5pt")
    parser.add_argument("--allow-missing-author-placeholders", action="store_true")
    parser.add_argument("--allow-header-footer-text", action="store_true")
    parser.add_argument("--no-citation-coverage", dest="require_citation_coverage", action="store_false")
    parser.add_argument("--no-three-line-tables", dest="require_three_line_tables", action="store_false")
    parser.add_argument("--no-single-column-check", dest="expect_single_column", action="store_false")
    parser.add_argument(
        "--require-page-break-before-heading",
        action="append",
        help="Require a real Word page break before the named heading; may be passed multiple times",
    )
    parser.set_defaults(require_citation_coverage=True, require_three_line_tables=True, expect_single_column=True)
    args = parser.parse_args()

    path = Path(args.docx_path).expanduser().resolve()
    summary, issues = audit(path, args)
    text = markdown(path, summary, issues)
    if args.output:
        Path(args.output).expanduser().write_text(text, encoding="utf-8")
    print(text)
    return 0 if not issues else 2


if __name__ == "__main__":
    raise SystemExit(main())
