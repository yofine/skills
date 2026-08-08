#!/usr/bin/env python3
"""Verify a rendered arxiv-paper-report v3 HTML artifact without network access."""

from __future__ import annotations

import argparse
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from validate_report_data import load_report, validate_report


PLACEHOLDERS = (
    "[THIS_SKILL_DIR]",
    "[OUTPUT_DIR]",
    "[RUN_DIR]",
    "[ARXIV_SKILL_DIR]",
    "{{PLACEHOLDER}}",
    "Lorem ipsum",
    "TODO:",
    "TBD:",
)
RESOURCE_TAGS = {"audio", "embed", "iframe", "img", "object", "script", "source", "video"}
FORBIDDEN_TAGS = {
    "audio",
    "base",
    "button",
    "canvas",
    "embed",
    "form",
    "iframe",
    "image",
    "img",
    "input",
    "math",
    "object",
    "script",
    "source",
    "svg",
    "template",
    "textarea",
    "track",
    "video",
    "foreignobject",
}
VOID_TAGS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}
REQUIRED_HEADINGS = {
    "direct-answer": "直接回答与证据上限",
    "knowledge-state": "当前知识状态",
    "capability-frontier": "当前能力边界与就绪缺口",
    "mechanism-model": "来源与分析者机制模型",
    "technical-options": "技术选项与可比性",
    "submission-signals": "提交信号与可证伪方向",
    "maturity-assessment": "五维成熟度",
    "decision-consequences": "决策后果与研究议程",
    "monitoring": "领先指标与监测触发",
    "evidence-base": "证据基础与审计附录",
    "papers": "代表论文档案",
    "proposition-index": "命题编号索引",
    "evidence-ledger": "原子证据账本",
}
LEGACY_SECTION_IDS = {
    "frontier-brief",
    "field-definition",
    "historical-baseline",
    "research-landscape",
    "authoritative-views",
    "frontier-directions",
    "trend-judgments",
    "controversies",
    "bottlenecks",
    "outlook",
    "technical-bets",
    "transition-theses",
}


def safe_token(value: Any) -> str:
    token = re.sub(r"[^a-z0-9-]+", "-", str(value).strip().lower()).strip("-")
    return token or "unknown"


def anchor(prefix: str, value: Any) -> str:
    return prefix + "-" + safe_token(value)


def is_safe_hyperlink(value: str) -> bool:
    if value.startswith("#"):
        return bool(value[1:])
    parsed = urlsplit(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc) and not parsed.username


class ReportHTMLParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.errors: list[str] = []
        self.ids: set[str] = set()
        self.links: list[str] = []
        self.title_parts: list[str] = []
        self.style_parts: list[str] = []
        self.headings: dict[str, str] = {}
        self.in_title = False
        self.in_style = False
        self.heading_tag = ""
        self.heading_target = ""
        self.heading_parts: list[str] = []
        self.container_stack: list[tuple[str, str]] = []
        self.open_tags: list[str] = []
        self.reasoning_bounds: list[dict[str, Any]] = []
        self.main_count = 0
        self.style_count = 0
        self.has_charset = False
        self.has_viewport = False
        self.viewport_content = ""
        self.html_lang = ""
        self.class_counts: dict[str, int] = {}
        self.boundary_evidence_ids: list[str] = []
        self.observed_failure_evidence_ids: list[list[str]] = []

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        values = {key.lower(): value or "" for key, value in attrs}
        tag = tag.lower()
        classes = set(values.get("class", "").split())
        for class_name in classes:
            self.class_counts[class_name] = self.class_counts.get(class_name, 0) + 1
        if tag not in VOID_TAGS:
            self.open_tags.append(tag)

        if tag == "html":
            self.html_lang = values.get("lang", "")
        elif tag == "main":
            self.main_count += 1
        elif tag == "title":
            self.in_title = True
        elif tag == "style":
            self.style_count += 1
            self.in_style = True
        elif tag == "meta":
            self.has_charset = self.has_charset or values.get("charset", "").lower() == "utf-8"
            if values.get("name", "").lower() == "viewport":
                self.has_viewport = True
                self.viewport_content = values.get("content", "")
            if values.get("http-equiv"):
                self.errors.append("http-equiv meta elements are not allowed")
        elif tag == "link":
            self.errors.append("link elements are not allowed; presentation must be embedded")

        if tag in FORBIDDEN_TAGS:
            self.errors.append(f"forbidden element <{tag}>")

        element_id = values.get("id")
        if element_id:
            if element_id in self.ids:
                self.errors.append(f"duplicate element id: {element_id}")
            self.ids.add(element_id)
            self.container_stack.append((tag, element_id))

        if tag in {"h2", "h3"}:
            self.heading_tag = tag
            self.heading_target = self.container_stack[-1][1] if self.container_stack else ""
            self.heading_parts = []

        if "reasoning-bound" in classes:
            self.reasoning_bounds.append(
                {
                    "tag": tag,
                    "depth": len(self.open_tags),
                    "found": False,
                    "id": values.get("id", ""),
                }
            )

        if "boundary-evidence-item" in classes:
            evidence_id = values.get("data-evidence-id", "")
            if not evidence_id:
                self.errors.append("boundary-evidence-item is missing data-evidence-id")
            else:
                self.boundary_evidence_ids.append(evidence_id)

        if "observed-failure-item" in classes:
            evidence_ids = values.get("data-evidence-ids", "").split()
            if not evidence_ids:
                self.errors.append("observed-failure-item is missing data-evidence-ids")
            self.observed_failure_evidence_ids.append(evidence_ids)

        href = values.get("href")
        if href is not None:
            self.links.append(href)
            if not is_safe_hyperlink(href):
                self.errors.append(f"unsafe or unsupported hyperlink: {href}")
            if href.startswith("#evidence-") or href.startswith("#proposition-"):
                for bound in self.reasoning_bounds:
                    bound["found"] = True

        if tag in RESOURCE_TAGS:
            for attribute in ("src", "data", "poster", "srcset"):
                value = values.get(attribute)
                if value:
                    self.errors.append(f"resource reference on <{tag}>: {attribute}={value}")

        if "style" in values:
            self.errors.append("inline style attributes are not allowed")
        if "hidden" in values:
            self.errors.append("hidden content is not allowed")
        for name, value in values.items():
            if name.startswith("on") and value:
                self.errors.append(f"inline event handler is not allowed: {name}")

        if tag == "details" and "abstract-source" not in classes:
            self.errors.append("only original abstracts may be placed in <details>")

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag == "title":
            self.in_title = False
        elif tag == "style":
            self.in_style = False

        if self.heading_tag == tag:
            heading = "".join(self.heading_parts).strip()
            if self.heading_target and self.heading_target not in self.headings:
                self.headings[self.heading_target] = heading
            self.heading_tag = ""
            self.heading_target = ""
            self.heading_parts = []

        if (
            self.reasoning_bounds
            and self.reasoning_bounds[-1]["tag"] == tag
            and self.reasoning_bounds[-1]["depth"] == len(self.open_tags)
        ):
            bound = self.reasoning_bounds.pop()
            if not bound["found"]:
                suffix = f"#{bound['id']}" if bound["id"] else f"<{tag}>"
                self.errors.append(
                    f"reasoning-bound {suffix} has no proposition or evidence link"
                )

        if self.container_stack and self.container_stack[-1][0] == tag:
            self.container_stack.pop()
        if self.open_tags and self.open_tags[-1] == tag:
            self.open_tags.pop()

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.title_parts.append(data)
        if self.in_style:
            self.style_parts.append(data)
        if self.heading_tag:
            self.heading_parts.append(data)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", required=True, type=Path)
    parser.add_argument("--html", required=True, type=Path)
    return parser.parse_args()


def verify(data: dict[str, Any], document: str) -> list[str]:
    errors = validate_report(data)
    if errors:
        return [f"data: {error}" for error in errors]

    if not re.match(r"^\s*<!doctype html>", document, flags=re.IGNORECASE):
        errors.append("html: missing HTML5 doctype")
    for placeholder in PLACEHOLDERS:
        if placeholder.lower() in document.lower():
            errors.append(f"html: unresolved placeholder {placeholder}")

    parser = ReportHTMLParser()
    try:
        parser.feed(document)
        parser.close()
    except Exception as exc:
        errors.append(f"html: parser error: {exc}")
        return errors

    errors.extend(f"html: {error}" for error in parser.errors)
    css = "".join(parser.style_parts)
    if re.search(r"@import\s|url\s*\(|expression\s*\(", css, flags=re.IGNORECASE):
        errors.append("html: CSS must not import, fetch, or execute external content")
    if re.search(r"linear-gradient|radial-gradient|conic-gradient", css, flags=re.IGNORECASE):
        errors.append("html: gradients are outside the academic visual contract")
    if parser.html_lang != "zh-CN":
        errors.append("html: root language must be zh-CN")
    if not parser.has_charset:
        errors.append("html: missing UTF-8 charset")
    if not parser.has_viewport:
        errors.append("html: missing viewport meta")
    elif "width=device-width" not in parser.viewport_content.replace(" ", "").lower():
        errors.append("html: viewport meta must use width=device-width")
    if parser.main_count != 1:
        errors.append(f"html: expected one <main>, found {parser.main_count}")
    if parser.style_count != 1:
        errors.append(f"html: expected one embedded <style>, found {parser.style_count}")

    report = data["report"]
    if "".join(parser.title_parts).strip() != report["title_zh"]:
        errors.append("html: document title does not match report.title_zh")

    for element_id, expected_heading in REQUIRED_HEADINGS.items():
        if element_id not in parser.ids:
            errors.append(f"html: missing required v3 section id {element_id}")
        elif not parser.headings.get(element_id, "").startswith(expected_heading):
            errors.append(
                f"html: heading for {element_id!r} must start with {expected_heading!r}, "
                f"found {parser.headings.get(element_id)!r}"
            )
    for element_id in sorted(LEGACY_SECTION_IDS & parser.ids):
        errors.append(f"html: legacy v2 section id is not allowed in v3: {element_id}")

    for href in parser.links:
        if href.startswith("#") and href[1:] not in parser.ids:
            errors.append(f"html: broken internal link {href}")

    expected_counts = {
        "decision-context-header": 1,
        "epistemic-ceiling-item": 3,
        "proposition-row": len(report.get("propositions", [])),
        "proposition-index-row": len(report.get("propositions", [])),
        "mechanism-stage": len(report.get("mechanism_model", {}).get("stages", [])),
        "mechanism-edge": len(report.get("mechanism_model", {}).get("edges", [])),
        "edge-support": len(report.get("mechanism_model", {}).get("edges", [])),
        "mechanism-bottleneck": len(report.get("mechanism_model", {}).get("bottlenecks", [])),
        "model-provenance": 1,
        "technical-option": len(report.get("technical_options", [])),
        "comparison-note": len(report.get("technical_options", [])),
        "capability": len(report.get("capability_frontier", {}).get("capabilities", [])),
        "boundary-evidence-item": sum(
            len(capability.get("strongest_evidence_ids", []))
            for capability in report.get("capability_frontier", {}).get("capabilities", [])
        ),
        "observed-failure-item": sum(
            len(capability.get("observed_failures", []))
            for capability in report.get("capability_frontier", {}).get("capabilities", [])
        ),
        "readiness-gap": len(report.get("capability_frontier", {}).get("readiness_gaps", [])),
        "transition": len(report.get("transition_theses", [])),
        "maturity-dimension": len(report.get("maturity_assessment", [])),
        "decision": len(report.get("decision_consequences", [])),
        "indicator": len(report.get("leading_indicators", [])),
        "threshold-rule": len(report.get("leading_indicators", [])),
        "paper-record": len(report.get("papers", [])),
        "evidence-record": len(report.get("evidence", [])),
    }
    for class_name, expected in expected_counts.items():
        actual = parser.class_counts.get(class_name, 0)
        if actual != expected:
            errors.append(f"html: {class_name} count {actual} does not match data count {expected}")

    expected_boundary_evidence_ids = [
        evidence_id
        for capability in report.get("capability_frontier", {}).get("capabilities", [])
        for evidence_id in capability.get("strongest_evidence_ids", [])
    ]
    if parser.boundary_evidence_ids != expected_boundary_evidence_ids:
        errors.append(
            "html: capability boundary evidence does not exactly match strongest_evidence_ids"
        )
    expected_observed_failure_evidence_ids = [
        failure.get("evidence_ids", [])
        for capability in report.get("capability_frontier", {}).get("capabilities", [])
        for failure in capability.get("observed_failures", [])
    ]
    if parser.observed_failure_evidence_ids != expected_observed_failure_evidence_ids:
        errors.append(
            "html: observed-failure evidence does not exactly match capability data"
        )
    if re.search(r">\s*[PE]0[0-9]+\s*<", document):
        errors.append("html: main references must use short P1/E1 ordinals without zero padding")

    for proposition in report.get("propositions", []):
        proposition_id = proposition["id"]
        proposition_id_anchor = anchor("proposition", proposition_id)
        if proposition_id_anchor not in parser.ids:
            errors.append(f"html: missing proposition anchor {proposition_id_anchor}")
        if f"#{proposition_id_anchor}" not in parser.links:
            errors.append(f"html: proposition {proposition_id} is never used outside the knowledge matrix")

    mechanism = report.get("mechanism_model", {})
    for stage in mechanism.get("stages", []):
        stage_anchor = anchor("stage", stage["id"])
        if stage_anchor not in parser.ids:
            errors.append(f"html: missing mechanism stage anchor {stage_anchor}")
    for option in report.get("technical_options", []):
        option_anchor = anchor("option", option["id"])
        if option_anchor not in parser.ids:
            errors.append(f"html: missing technical option anchor {option_anchor}")
    for capability in report.get("capability_frontier", {}).get("capabilities", []):
        capability_anchor = anchor("capability", capability["id"])
        if capability_anchor not in parser.ids:
            errors.append(f"html: missing capability anchor {capability_anchor}")
    for gap in report.get("capability_frontier", {}).get("readiness_gaps", []):
        gap_anchor = anchor("readiness-gap", gap["id"])
        if gap_anchor not in parser.ids:
            errors.append(f"html: missing readiness-gap anchor {gap_anchor}")
    for indicator in report.get("leading_indicators", []):
        indicator_anchor = anchor("indicator", indicator["id"])
        if indicator_anchor not in parser.ids:
            errors.append(f"html: missing leading-indicator anchor {indicator_anchor}")

    for paper in report.get("papers", []):
        paper_id = paper["arxiv_id"]
        paper_id_anchor = anchor("paper", paper_id)
        if paper_id_anchor not in parser.ids:
            errors.append(f"html: missing paper anchor {paper_id_anchor}")
        for key in ("source_url", "pdf_url"):
            if paper[key] not in parser.links:
                errors.append(f"html: missing {key} for {paper_id}")
        for url in paper.get("external_verification", {}).get("source_urls", []):
            if url not in parser.links:
                errors.append(f"html: missing external verification source for {paper_id}: {url}")

    for evidence in report.get("evidence", []):
        evidence_id = evidence["id"]
        evidence_id_anchor = anchor("evidence", evidence_id)
        if evidence_id_anchor not in parser.ids:
            errors.append(f"html: missing evidence ledger anchor {evidence_id_anchor}")
        if f"#{evidence_id_anchor}" not in parser.links:
            errors.append(f"html: evidence record {evidence_id} is never cited from the analysis")
        source_url = evidence.get("source_url")
        if source_url and source_url not in parser.links:
            errors.append(f"html: missing external evidence source for {evidence_id}: {source_url}")

    return errors


def main() -> int:
    args = parse_args()
    try:
        data = load_report(args.data)
        document = args.html.read_text(encoding="utf-8")
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"verify_report: {exc}", file=sys.stderr)
        return 1

    errors = verify(data, document)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"Verification failed with {len(errors)} error(s).", file=sys.stderr)
        return 1

    print(
        f"Verified standalone v3 decision-intelligence HTML with "
        f"{len(data['report']['propositions'])} proposition(s), "
        f"{len(data['report']['papers'])} paper(s), and "
        f"{len(data['report']['evidence'])} evidence record(s): {args.html}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
