#!/usr/bin/env python3
"""Validate v3 arXiv field-intelligence JSON and its evidence graph."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from typing import Any, Iterable, Iterator


ARXIV_ID_RE = re.compile(r"^[0-9]{4}\.[0-9]{4,5}$")
VERSION_RE = re.compile(r"^v[0-9]+$")
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
HTTP_RE = re.compile(r"^https?://")
UNSUPPORTED_SUPERLATIVE_RE = re.compile(
    r"(?:"
    r"最新|最权威|最具影响力|最先进|公认最佳|业界第一|世界第一|"
    r"业界领先|世界领先|领先于所有|"
    r"\blatest\b|\bnewest\b|\bmost\s+recent\b|"
    r"\bmost\s+authoritative\b|\bmost\s+influential\b|"
    r"\bstate[- ]of[- ]the[- ]art\b|\bSOTA\b|\bseminal\b|"
    r"\bdefinitive\b|\bbest[- ]in[- ]class\b"
    r")",
    re.IGNORECASE,
)
UNSUPPORTED_RANKING_RE = re.compile(
    r"(?:优于|劣于|胜过|排名(?:第一|最高)|"
    r"\bbetter\s+than\b|\bworse\s+than\b|\boutperform(?:s|ed|ing)?\b|"
    r"\bsuperior\s+to\b|\binferior\s+to\b|\bbest\b)",
    re.IGNORECASE,
)

PAPER_DEPTH = {"metadata": 0, "abstract": 1, "full_text": 2}
EVIDENCE_DEPTH = {"metadata": 0, "abstract": 1, "full_text": 2}
CONFIDENCE = {"high", "medium", "low"}
CORPUS_LAYERS = {"anchor", "frontier", "signal", "counterevidence"}
LAYER_STATUS = {"searched", "partial", "not_searched"}
DECISION_CONTEXTS = {
    "research_agenda",
    "technology_strategy",
    "architecture",
    "product",
    "due_diligence",
}
PROPOSITION_TYPES = {
    "mechanism",
    "capability",
    "evaluation",
    "deployment",
    "governance",
}
PROPOSITION_STATUS = {
    "established",
    "credible_emerging",
    "contested",
    "unknown",
    "weakened",
    "insufficient_evidence",
}
MATURITY_DIMENSIONS = {
    "scientific_mechanism",
    "benchmark",
    "engineering",
    "deployment",
    "governance",
}
CAPABILITY_LEVEL = {
    "conceptual": 0,
    "prototype": 1,
    "benchmark": 2,
    "controlled_user_study": 3,
    "longitudinal_deployment": 4,
}
OBSERVED_FAILURE_EVIDENCE_TYPES = {
    "author_claim",
    "measured_result",
    "negative_result",
    "replication",
    "external_validation",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    return parser.parse_args()


def load_report(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("top-level JSON value must be an object")
    return value


def reject_unknown(
    obj: dict[str, Any],
    allowed: set[str],
    path: str,
    errors: list[str],
    *,
    optional: set[str] | None = None,
) -> None:
    for key in sorted(set(obj) - allowed):
        errors.append(f"{path}.{key}: unknown field")
    required = allowed - (optional or set())
    for key in sorted(required - set(obj)):
        errors.append(f"{path}.{key}: missing required field")


def require_object(
    obj: dict[str, Any], key: str, path: str, errors: list[str]
) -> dict[str, Any]:
    value = obj.get(key)
    if not isinstance(value, dict):
        errors.append(f"{path}.{key}: expected object")
        return {}
    return value


def require_list(
    obj: dict[str, Any], key: str, path: str, errors: list[str]
) -> list[Any]:
    value = obj.get(key)
    if not isinstance(value, list):
        errors.append(f"{path}.{key}: expected array")
        return []
    return value


def require_string(
    obj: dict[str, Any], key: str, path: str, errors: list[str]
) -> str:
    value = obj.get(key)
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{path}.{key}: expected non-empty string")
        return ""
    return value.strip()


def require_slug(
    obj: dict[str, Any], key: str, path: str, errors: list[str]
) -> str:
    value = require_string(obj, key, path, errors)
    if value and not SLUG_RE.fullmatch(value):
        errors.append(f"{path}.{key}: expected lowercase kebab-case slug")
    return value


def require_enum(
    obj: dict[str, Any],
    key: str,
    choices: set[str],
    path: str,
    errors: list[str],
) -> str:
    value = obj.get(key)
    if value not in choices:
        errors.append(
            f"{path}.{key}: expected one of {', '.join(sorted(choices))}"
        )
        return ""
    return value


def require_nonnegative_int(
    obj: dict[str, Any], key: str, path: str, errors: list[str]
) -> int | None:
    value = obj.get(key)
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        errors.append(f"{path}.{key}: expected non-negative integer")
        return None
    return value


def validate_date(value: Any, path: str, errors: list[str]) -> date | None:
    if not isinstance(value, str):
        errors.append(f"{path}: expected YYYY-MM-DD string")
        return None
    try:
        parsed = date.fromisoformat(value)
    except ValueError:
        errors.append(f"{path}: invalid date {value!r}")
        return None
    if parsed.isoformat() != value:
        errors.append(f"{path}: expected zero-padded ISO date")
        return None
    return parsed


def validate_nullable_date(
    value: Any, path: str, errors: list[str]
) -> date | None:
    if value is None:
        return None
    return validate_date(value, path, errors)


def validate_nullable_string(value: Any, path: str, errors: list[str]) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{path}: expected non-empty string or null")
        return None
    return value.strip()


def validate_string_list(
    value: Any,
    path: str,
    errors: list[str],
    *,
    min_items: int = 0,
    unique: bool = False,
) -> list[str]:
    if not isinstance(value, list):
        errors.append(f"{path}: expected array")
        return []
    if len(value) < min_items:
        errors.append(f"{path}: expected at least {min_items} item(s)")
    valid: list[str] = []
    for index, item in enumerate(value):
        if not isinstance(item, str) or not item.strip():
            errors.append(f"{path}[{index}]: expected non-empty string")
        else:
            valid.append(item.strip())
    if unique and len(valid) != len(set(valid)):
        errors.append(f"{path}: duplicate items are not allowed")
    return valid


def validate_slug_list(
    value: Any,
    path: str,
    errors: list[str],
    *,
    min_items: int = 0,
) -> list[str]:
    values = validate_string_list(
        value, path, errors, min_items=min_items, unique=True
    )
    for item in values:
        if not SLUG_RE.fullmatch(item):
            errors.append(f"{path}: invalid slug {item!r}")
    return values


def validate_refs(
    value: Any,
    path: str,
    known: set[str],
    errors: list[str],
    *,
    min_items: int = 0,
    label: str = "ID",
) -> list[str]:
    values = validate_slug_list(value, path, errors, min_items=min_items)
    for value_id in values:
        if value_id not in known:
            errors.append(f"{path}: unknown {label} {value_id!r}")
    return values


def validate_paper_refs(
    value: Any,
    path: str,
    known: set[str],
    errors: list[str],
    *,
    min_items: int = 0,
) -> list[str]:
    values = validate_string_list(
        value, path, errors, min_items=min_items, unique=True
    )
    for paper_id in values:
        if not ARXIV_ID_RE.fullmatch(paper_id):
            errors.append(f"{path}: invalid arXiv ID {paper_id!r}")
        elif paper_id not in known:
            errors.append(f"{path}: unknown arXiv ID {paper_id!r}")
    return values


def ensure_unique_id(
    value: str, seen: set[str], path: str, errors: list[str]
) -> None:
    if not value:
        return
    if value in seen:
        errors.append(f"{path}: duplicate ID {value!r}")
    seen.add(value)


def walk_strings(value: Any, path: str) -> Iterator[tuple[str, str]]:
    if isinstance(value, str):
        yield path, value
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from walk_strings(item, f"{path}[{index}]")
    elif isinstance(value, dict):
        for key, item in value.items():
            yield from walk_strings(item, f"{path}.{key}")


def reject_unsupported_superlatives(
    value: Any, path: str, errors: list[str]
) -> None:
    for item_path, text in walk_strings(value, path):
        match = UNSUPPORTED_SUPERLATIVE_RE.search(text)
        if match:
            errors.append(
                f"{item_path}: unsupported recency/authority superlative "
                f"{match.group(0)!r}; state a dated, bounded observation instead"
            )


def validate_scope(
    report: dict[str, Any], as_of: date | None, errors: list[str]
) -> dict[str, Any]:
    scope = require_object(report, "scope", "report", errors)
    allowed = {
        "research_question",
        "decision_context",
        "operational_definition",
        "terminology",
        "date_from",
        "date_to",
        "categories",
        "corpus_layers",
        "queries",
        "inclusion_criteria",
        "exclusion_criteria",
        "coverage_gaps",
        "screening",
    }
    reject_unknown(scope, allowed, "report.scope", errors)
    require_string(scope, "research_question", "report.scope", errors)
    require_string(scope, "operational_definition", "report.scope", errors)

    decision_context = require_object(
        scope, "decision_context", "report.scope", errors
    )
    decision_path = "report.scope.decision_context"
    reject_unknown(
        decision_context,
        {
            "primary",
            "decision_maker",
            "choice_at_stake",
            "time_horizon",
            "secondary",
        },
        decision_path,
        errors,
    )
    primary = require_enum(
        decision_context,
        "primary",
        DECISION_CONTEXTS,
        decision_path,
        errors,
    )
    for key in ("decision_maker", "choice_at_stake", "time_horizon"):
        require_string(decision_context, key, decision_path, errors)
    secondary = validate_string_list(
        decision_context.get("secondary"),
        f"{decision_path}.secondary",
        errors,
        unique=True,
    )
    for context in secondary:
        if context not in DECISION_CONTEXTS:
            errors.append(
                f"{decision_path}.secondary: expected one of "
                f"{', '.join(sorted(DECISION_CONTEXTS))}, got {context!r}"
            )
    if primary and primary in secondary:
        errors.append(
            f"{decision_path}.secondary: must not repeat primary {primary!r}"
        )

    date_from = validate_date(scope.get("date_from"), "report.scope.date_from", errors)
    date_to = validate_date(scope.get("date_to"), "report.scope.date_to", errors)
    if date_from and date_to and date_from > date_to:
        errors.append("report.scope: date_from must not be after date_to")
    if date_to and as_of and date_to > as_of:
        errors.append("report.scope.date_to: must not be after report.as_of")

    validate_string_list(
        scope.get("categories"),
        "report.scope.categories",
        errors,
        unique=True,
    )
    validate_string_list(
        scope.get("inclusion_criteria"),
        "report.scope.inclusion_criteria",
        errors,
        min_items=1,
    )
    validate_string_list(
        scope.get("exclusion_criteria"),
        "report.scope.exclusion_criteria",
        errors,
    )
    validate_string_list(
        scope.get("coverage_gaps"),
        "report.scope.coverage_gaps",
        errors,
    )

    terminology = require_list(scope, "terminology", "report.scope", errors)
    if not terminology:
        errors.append("report.scope.terminology: at least one term required")
    seen_terms: set[str] = set()
    for index, item in enumerate(terminology):
        path = f"report.scope.terminology[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{path}: expected object")
            continue
        reject_unknown(item, {"term", "definition", "included_variants"}, path, errors)
        term = require_string(item, "term", path, errors)
        require_string(item, "definition", path, errors)
        validate_string_list(
            item.get("included_variants"),
            f"{path}.included_variants",
            errors,
            unique=True,
        )
        folded = term.casefold()
        if folded and folded in seen_terms:
            errors.append(f"{path}.term: duplicate term {term!r}")
        seen_terms.add(folded)

    layers = require_list(scope, "corpus_layers", "report.scope", errors)
    if not layers:
        errors.append("report.scope.corpus_layers: at least one layer required")
    layer_by_id: dict[str, dict[str, Any]] = {}
    layer_by_role: dict[str, dict[str, Any]] = {}
    layer_status: dict[str, str] = {}
    for index, layer in enumerate(layers):
        path = f"report.scope.corpus_layers[{index}]"
        if not isinstance(layer, dict):
            errors.append(f"{path}: expected object")
            continue
        reject_unknown(
            layer,
            {
                "id",
                "role",
                "status",
                "date_from",
                "date_to",
                "purpose",
                "coverage_note",
            },
            path,
            errors,
        )
        layer_id = require_slug(layer, "id", path, errors)
        role = require_enum(layer, "role", CORPUS_LAYERS, path, errors)
        status = require_enum(layer, "status", LAYER_STATUS, path, errors)
        require_string(layer, "purpose", path, errors)
        require_string(layer, "coverage_note", path, errors)
        if layer_id:
            if layer_id in layer_by_id:
                errors.append(f"{path}.id: duplicate layer ID {layer_id!r}")
            layer_by_id[layer_id] = layer
            layer_status[layer_id] = status
        if role:
            if role in layer_by_role:
                errors.append(f"{path}.role: duplicate corpus role {role!r}")
            layer_by_role[role] = layer

        layer_from = validate_nullable_date(
            layer.get("date_from"), f"{path}.date_from", errors
        )
        layer_to = validate_nullable_date(
            layer.get("date_to"), f"{path}.date_to", errors
        )
        if status in {"searched", "partial"} and not (layer_from and layer_to):
            errors.append(f"{path}: searched/partial layer requires a date window")
        if layer_from and layer_to and layer_from > layer_to:
            errors.append(f"{path}: date_from must not be after date_to")
        if date_from and layer_from and layer_from < date_from:
            errors.append(f"{path}.date_from: must be within report scope")
        if date_to and layer_to and layer_to > date_to:
            errors.append(f"{path}.date_to: must be within report scope")

    queries = require_list(scope, "queries", "report.scope", errors)
    if not queries:
        errors.append("report.scope.queries: at least one exact query required")
    query_counts: Counter[str] = Counter()
    seen_query_labels: set[str] = set()
    for index, query in enumerate(queries):
        path = f"report.scope.queries[{index}]"
        if not isinstance(query, dict):
            errors.append(f"{path}: expected object")
            continue
        reject_unknown(
            query, {"label", "query", "layer_id", "sort", "max_results"}, path, errors
        )
        label = require_string(query, "label", path, errors)
        if label in seen_query_labels:
            errors.append(f"{path}.label: duplicate query label {label!r}")
        seen_query_labels.add(label)
        require_string(query, "query", path, errors)
        layer_id = require_slug(query, "layer_id", path, errors)
        if layer_id not in layer_by_id:
            errors.append(f"{path}.layer_id: unknown corpus layer {layer_id!r}")
        elif layer_status.get(layer_id) == "not_searched":
            errors.append(f"{path}.layer_id: cannot target a not_searched layer")
        query_counts[layer_id] += 1
        require_enum(
            query,
            "sort",
            {"relevance", "lastUpdatedDate", "submittedDate"},
            path,
            errors,
        )
        max_results = query.get("max_results")
        if (
            isinstance(max_results, bool)
            or not isinstance(max_results, int)
            or not 1 <= max_results <= 100
        ):
            errors.append(f"{path}.max_results: expected integer from 1 to 100")
    for layer_id, status in layer_status.items():
        if status == "searched" and query_counts[layer_id] == 0:
            errors.append(
                f"report.scope.corpus_layers[{layer_id!r}]: {status} layer has no exact query"
            )
        if status == "not_searched" and query_counts[layer_id]:
            errors.append(
                f"report.scope.corpus_layers[{layer_id!r}]: not_searched layer has queries"
            )

    screening = require_object(scope, "screening", "report.scope", errors)
    reject_unknown(
        screening,
        {"retrieved", "deduplicated", "screened", "included"},
        "report.scope.screening",
        errors,
    )
    screening_counts: dict[str, int | None] = {}
    for key in ("retrieved", "deduplicated", "screened", "included"):
        screening_counts[key] = require_nonnegative_int(
            screening, key, "report.scope.screening", errors
        )
    included = screening_counts["included"]
    if included == 0:
        errors.append("report.scope.screening.included: expected at least one paper")
    for left, right in (
        ("retrieved", "deduplicated"),
        ("deduplicated", "screened"),
        ("screened", "included"),
    ):
        left_value = screening_counts[left]
        right_value = screening_counts[right]
        if left_value is not None and right_value is not None and left_value < right_value:
            errors.append(
                f"report.scope.screening: {left} must be greater than or equal to {right}"
            )

    return {
        "raw": scope,
        "date_from": date_from,
        "date_to": date_to,
        "layer_by_id": layer_by_id,
        "layer_by_role": layer_by_role,
        "screening": screening,
    }


def validate_papers(
    report: dict[str, Any],
    as_of: date | None,
    scope_info: dict[str, Any],
    errors: list[str],
) -> dict[str, Any]:
    raw_papers = require_list(report, "papers", "report", errors)
    if not raw_papers:
        errors.append("report.papers: at least one paper required")
    papers: list[dict[str, Any]] = []
    by_id: dict[str, dict[str, Any]] = {}
    dates: dict[str, date] = {}
    basis: dict[str, str] = {}
    clusters: dict[str, str] = {}
    roles: dict[str, str] = {}
    externally_verified: set[str] = set()
    allowed = {
        "arxiv_id",
        "version",
        "title",
        "title_zh",
        "authors",
        "published",
        "updated",
        "primary_category",
        "categories",
        "source_url",
        "pdf_url",
        "evidence_basis",
        "corpus_role",
        "independence_cluster_id",
        "abstract_original",
        "synopsis_zh",
        "external_verification",
        "analysis",
        "model_links",
        "metrics",
    }
    for index, paper in enumerate(raw_papers):
        path = f"report.papers[{index}]"
        if not isinstance(paper, dict):
            errors.append(f"{path}: expected object")
            continue
        papers.append(paper)
        reject_unknown(paper, allowed, path, errors)
        paper_id = require_string(paper, "arxiv_id", path, errors)
        if paper_id and not ARXIV_ID_RE.fullmatch(paper_id):
            errors.append(f"{path}.arxiv_id: invalid arXiv ID")
        if paper_id in by_id:
            errors.append(f"{path}.arxiv_id: duplicate {paper_id!r}")
        elif paper_id:
            by_id[paper_id] = paper

        version = require_string(paper, "version", path, errors)
        if version and not VERSION_RE.fullmatch(version):
            errors.append(f"{path}.version: expected vN")
        for key in (
            "title",
            "title_zh",
            "primary_category",
            "abstract_original",
            "synopsis_zh",
        ):
            require_string(paper, key, path, errors)
        authors = validate_string_list(
            paper.get("authors"), f"{path}.authors", errors, min_items=1, unique=True
        )
        if len(authors) != len(set(authors)):
            errors.append(f"{path}.authors: duplicate authors are not allowed")

        published = validate_date(paper.get("published"), f"{path}.published", errors)
        updated = validate_nullable_date(paper.get("updated"), f"{path}.updated", errors)
        if published and paper_id:
            dates[paper_id] = published
        if published and updated and updated < published:
            errors.append(f"{path}.updated: must not be before published")
        if updated and as_of and updated > as_of:
            errors.append(f"{path}.updated: must not be after report.as_of")
        if published and scope_info.get("date_from") and published < scope_info["date_from"]:
            errors.append(f"{path}.published: before report scope")
        if published and scope_info.get("date_to") and published > scope_info["date_to"]:
            errors.append(f"{path}.published: after report scope")

        categories = validate_string_list(
            paper.get("categories"),
            f"{path}.categories",
            errors,
            min_items=1,
            unique=True,
        )
        primary = paper.get("primary_category")
        if isinstance(primary, str) and primary not in categories:
            errors.append(f"{path}.categories: must include primary_category")
        source_url = require_string(paper, "source_url", path, errors)
        pdf_url = require_string(paper, "pdf_url", path, errors)
        if paper_id and source_url != f"https://arxiv.org/abs/{paper_id}":
            errors.append(f"{path}.source_url: must match arXiv ID")
        if paper_id and pdf_url not in {
            f"https://arxiv.org/pdf/{paper_id}",
            f"https://arxiv.org/pdf/{paper_id}.pdf",
        }:
            errors.append(f"{path}.pdf_url: must match arXiv ID")

        paper_basis = require_enum(paper, "evidence_basis", set(PAPER_DEPTH), path, errors)
        if paper_id and paper_basis:
            basis[paper_id] = paper_basis
        role = require_enum(paper, "corpus_role", CORPUS_LAYERS, path, errors)
        if paper_id and role:
            roles[paper_id] = role
        role_layer = scope_info.get("layer_by_role", {}).get(role)
        if role and role_layer is None:
            errors.append(f"{path}.corpus_role: no matching scope corpus layer")
        elif role_layer and role_layer.get("status") == "not_searched":
            errors.append(
                f"{path}.corpus_role: paper cannot belong to a not_searched {role!r} layer"
            )
        cluster = require_slug(paper, "independence_cluster_id", path, errors)
        if paper_id and cluster:
            clusters[paper_id] = cluster

        verification = require_object(paper, "external_verification", path, errors)
        verification_path = f"{path}.external_verification"
        reject_unknown(
            verification,
            {"publication_status", "venue", "verified_on", "source_urls"},
            verification_path,
            errors,
        )
        status = require_enum(
            verification,
            "publication_status",
            {"arxiv_preprint", "peer_reviewed", "unknown"},
            verification_path,
            errors,
        )
        venue = validate_nullable_string(
            verification.get("venue"), f"{verification_path}.venue", errors
        )
        verified_on = validate_nullable_date(
            verification.get("verified_on"),
            f"{verification_path}.verified_on",
            errors,
        )
        if verified_on and as_of and verified_on > as_of:
            errors.append(f"{verification_path}.verified_on: after report.as_of")
        source_urls = validate_string_list(
            verification.get("source_urls"),
            f"{verification_path}.source_urls",
            errors,
            unique=True,
        )
        for source in source_urls:
            if not HTTP_RE.match(source):
                errors.append(f"{verification_path}.source_urls: invalid URL {source!r}")
        if bool(verified_on) != bool(source_urls):
            errors.append(
                f"{verification_path}: verified_on and source_urls must be supplied together"
            )
        if venue is not None and not (verified_on and source_urls):
            errors.append(f"{verification_path}.venue: requires dated source verification")
        if status == "peer_reviewed" and not (venue and verified_on and source_urls):
            errors.append(
                f"{verification_path}: peer_reviewed requires venue and dated source verification"
            )
        if paper_id and verified_on and source_urls:
            externally_verified.add(paper_id)

        analysis = require_object(paper, "analysis", path, errors)
        analysis_path = f"{path}.analysis"
        reject_unknown(
            analysis,
            {
                "research_object",
                "mechanism",
                "evaluation",
                "key_findings",
                "author_stated_limitations",
                "analyst_inferred_limitations",
            },
            analysis_path,
            errors,
        )
        for key in ("research_object", "mechanism", "evaluation"):
            require_string(analysis, key, analysis_path, errors)
        for key in ("author_stated_limitations", "analyst_inferred_limitations"):
            validate_string_list(analysis.get(key), f"{analysis_path}.{key}", errors)
        findings = require_list(analysis, "key_findings", analysis_path, errors)
        for finding_index, finding in enumerate(findings):
            finding_path = f"{analysis_path}.key_findings[{finding_index}]"
            if not isinstance(finding, dict):
                errors.append(f"{finding_path}: expected object")
                continue
            reject_unknown(finding, {"statement", "evidence_ids"}, finding_path, errors)
            require_string(finding, "statement", finding_path, errors)
            validate_slug_list(
                finding.get("evidence_ids"),
                f"{finding_path}.evidence_ids",
                errors,
                min_items=1,
            )

        model_links = require_object(paper, "model_links", path, errors)
        links_path = f"{path}.model_links"
        reject_unknown(
            model_links,
            {"stage_ids", "option_ids", "capability_ids", "proposition_ids"},
            links_path,
            errors,
        )
        for key in ("stage_ids", "option_ids", "capability_ids", "proposition_ids"):
            validate_slug_list(model_links.get(key), f"{links_path}.{key}", errors)

        metrics = require_list(paper, "metrics", path, errors)
        for metric_index, metric in enumerate(metrics):
            metric_path = f"{path}.metrics[{metric_index}]"
            if not isinstance(metric, dict):
                errors.append(f"{metric_path}: expected object")
                continue
            reject_unknown(
                metric,
                {"name", "value", "context", "basis", "evidence_id"},
                metric_path,
                errors,
            )
            for key in ("name", "value", "context"):
                require_string(metric, key, metric_path, errors)
            require_enum(
                metric,
                "basis",
                {"metadata", "abstract", "full_text", "external"},
                metric_path,
                errors,
            )
            require_slug(metric, "evidence_id", metric_path, errors)

    return {
        "papers": papers,
        "by_id": by_id,
        "dates": dates,
        "basis": basis,
        "clusters": clusters,
        "roles": roles,
        "externally_verified": externally_verified,
    }


def validate_evidence(
    report: dict[str, Any], paper_info: dict[str, Any], errors: list[str]
) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    records = require_list(report, "evidence", "report", errors)
    if not records:
        errors.append("report.evidence: at least one atomic record required")
    by_id: dict[str, dict[str, Any]] = {}
    allowed = {
        "id",
        "paper_id",
        "source_depth",
        "locator",
        "evidence_type",
        "statement",
        "excerpt",
        "confidence",
        "source_url",
    }
    for index, record in enumerate(records):
        path = f"report.evidence[{index}]"
        if not isinstance(record, dict):
            errors.append(f"{path}: expected object")
            continue
        reject_unknown(record, allowed, path, errors, optional={"source_url"})
        evidence_id = require_slug(record, "id", path, errors)
        if evidence_id in by_id:
            errors.append(f"{path}.id: duplicate evidence ID {evidence_id!r}")
        elif evidence_id:
            by_id[evidence_id] = record
        paper_id = require_string(record, "paper_id", path, errors)
        if paper_id not in paper_info["by_id"]:
            errors.append(f"{path}.paper_id: unknown arXiv ID {paper_id!r}")
        depth = require_enum(
            record,
            "source_depth",
            {"metadata", "abstract", "full_text", "external"},
            path,
            errors,
        )
        evidence_type = require_enum(
            record,
            "evidence_type",
            {
                "author_claim",
                "measured_result",
                "negative_result",
                "replication",
                "external_validation",
                "analyst_inference",
                "derived_comparison",
            },
            path,
            errors,
        )
        require_string(record, "statement", path, errors)
        validate_nullable_string(record.get("excerpt"), f"{path}.excerpt", errors)
        require_enum(record, "confidence", CONFIDENCE, path, errors)

        locator = require_object(record, "locator", path, errors)
        locator_path = f"{path}.locator"
        reject_unknown(locator, {"type", "label"}, locator_path, errors)
        locator_type = require_enum(
            locator,
            "type",
            {"abstract", "section", "page", "table", "figure", "external"},
            locator_path,
            errors,
        )
        require_string(locator, "label", locator_path, errors)
        expected_locators = {
            "metadata": {"abstract"},
            "abstract": {"abstract"},
            "full_text": {"section", "page", "table", "figure"},
            "external": {"external"},
        }
        if depth and locator_type not in expected_locators.get(depth, set()):
            errors.append(
                f"{locator_path}.type: {locator_type!r} is invalid for {depth!r} evidence"
            )

        paper_level = PAPER_DEPTH.get(paper_info["basis"].get(paper_id, ""))
        if depth in EVIDENCE_DEPTH and paper_level is not None:
            if EVIDENCE_DEPTH[depth] > paper_level:
                errors.append(
                    f"{path}.source_depth: {depth} exceeds paper evidence basis "
                    f"{paper_info['basis'].get(paper_id)!r}"
                )

        if depth == "external":
            source_url = require_string(record, "source_url", path, errors)
            if source_url and not HTTP_RE.match(source_url):
                errors.append(f"{path}.source_url: expected HTTP(S) URL")
            if paper_id not in paper_info["externally_verified"]:
                errors.append(
                    f"{path}.source_depth: external evidence requires dated paper verification"
                )
            verification = paper_info["by_id"].get(paper_id, {}).get(
                "external_verification", {}
            )
            sources = verification.get("source_urls", []) if isinstance(verification, dict) else []
            if source_url and source_url not in sources:
                errors.append(
                    f"{path}.source_url: must appear in paper.external_verification.source_urls"
                )
        elif "source_url" in record:
            errors.append(f"{path}.source_url: allowed only for external evidence")
        if evidence_type == "external_validation" and depth != "external":
            errors.append(f"{path}.evidence_type: external_validation requires external depth")

    return records, by_id


def evidence_clusters(
    evidence_ids: Iterable[str],
    evidence_by_id: dict[str, dict[str, Any]],
    paper_clusters: dict[str, str],
) -> set[str]:
    clusters: set[str] = set()
    for evidence_id in evidence_ids:
        record = evidence_by_id.get(evidence_id)
        if not record:
            continue
        cluster = paper_clusters.get(record.get("paper_id", ""))
        if cluster:
            clusters.add(cluster)
    return clusters


def validate_propositions(
    report: dict[str, Any],
    evidence_by_id: dict[str, dict[str, Any]],
    paper_info: dict[str, Any],
    errors: list[str],
) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]], set[str]]:
    items = require_list(report, "propositions", "report", errors)
    if not items:
        errors.append("report.propositions: at least one proposition required")
    by_id: dict[str, dict[str, Any]] = {}
    referenced_evidence: set[str] = set()
    allowed = {
        "id",
        "statement",
        "proposition_type",
        "status",
        "scope_conditions",
        "supporting_evidence_ids",
        "counter_evidence_ids",
        "alternative_explanations",
        "evidence_ceiling",
        "confidence",
        "uncertainty",
        "what_would_change",
        "decision_relevance",
        "evidence_profile",
    }
    for index, item in enumerate(items):
        path = f"report.propositions[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{path}: expected object")
            continue
        reject_unknown(item, allowed, path, errors)
        proposition_id = require_slug(item, "id", path, errors)
        if proposition_id in by_id:
            errors.append(f"{path}.id: duplicate proposition ID {proposition_id!r}")
        elif proposition_id:
            by_id[proposition_id] = item
        require_string(item, "statement", path, errors)
        require_enum(item, "proposition_type", PROPOSITION_TYPES, path, errors)
        status = require_enum(item, "status", PROPOSITION_STATUS, path, errors)
        validate_string_list(item.get("scope_conditions"), f"{path}.scope_conditions", errors)
        support = validate_refs(
            item.get("supporting_evidence_ids"),
            f"{path}.supporting_evidence_ids",
            set(evidence_by_id),
            errors,
            label="evidence ID",
        )
        counter = validate_refs(
            item.get("counter_evidence_ids"),
            f"{path}.counter_evidence_ids",
            set(evidence_by_id),
            errors,
            label="evidence ID",
        )
        overlap = sorted(set(support) & set(counter))
        if overlap:
            errors.append(f"{path}: support and counter evidence overlap: {overlap}")
        referenced_evidence.update(support)
        referenced_evidence.update(counter)
        validate_string_list(
            item.get("alternative_explanations"),
            f"{path}.alternative_explanations",
            errors,
        )
        ceiling = require_enum(
            item,
            "evidence_ceiling",
            {"metadata", "abstract", "full_text", "external", "mixed"},
            path,
            errors,
        )
        confidence = require_enum(item, "confidence", CONFIDENCE, path, errors)
        require_string(item, "uncertainty", path, errors)
        validate_string_list(
            item.get("what_would_change"),
            f"{path}.what_would_change",
            errors,
            min_items=1,
        )
        require_string(item, "decision_relevance", path, errors)

        all_evidence = [evidence_by_id[value] for value in support + counter if value in evidence_by_id]
        depths = {record.get("source_depth") for record in all_evidence}
        expected_ceiling = "metadata"
        if len(depths) == 1:
            expected_ceiling = next(iter(depths))
        elif len(depths) > 1:
            expected_ceiling = "mixed"
        if ceiling and ceiling != expected_ceiling:
            errors.append(
                f"{path}.evidence_ceiling: expected {expected_ceiling!r} from referenced evidence"
            )

        profile = require_object(item, "evidence_profile", path, errors)
        profile_path = f"{path}.evidence_profile"
        reject_unknown(
            profile,
            {
                "directness",
                "consistency",
                "external_validity",
                "reproducibility",
                "rationale",
            },
            profile_path,
            errors,
        )
        directness = require_enum(
            profile,
            "directness",
            {"indirect", "author_claim", "measured", "replicated"},
            profile_path,
            errors,
        )
        consistency = require_enum(
            profile,
            "consistency",
            {"single_source", "multi_source_aligned", "mixed", "conflicting"},
            profile_path,
            errors,
        )
        external_validity = require_enum(
            profile,
            "external_validity",
            {"unknown", "benchmark_only", "controlled", "real_world", "longitudinal"},
            profile_path,
            errors,
        )
        reproducibility = require_enum(
            profile,
            "reproducibility",
            {"unknown", "materials_available", "independently_reproduced"},
            profile_path,
            errors,
        )
        require_string(profile, "rationale", profile_path, errors)

        support_records = [evidence_by_id[value] for value in support if value in evidence_by_id]
        support_clusters = evidence_clusters(
            support, evidence_by_id, paper_info["clusters"]
        )
        all_clusters = evidence_clusters(
            support + counter, evidence_by_id, paper_info["clusters"]
        )
        support_types = {record.get("evidence_type") for record in support_records}
        if not support and not counter and directness != "indirect":
            errors.append(f"{profile_path}.directness: evidence-free proposition must be indirect")
        if directness == "author_claim" and "author_claim" not in support_types:
            errors.append(f"{profile_path}.directness: author_claim requires author-claim support")
        if directness == "measured" and not support_types.intersection(
            {"measured_result", "negative_result", "replication"}
        ):
            errors.append(f"{profile_path}.directness: measured requires measured support")
        if directness == "replicated" and "replication" not in support_types:
            errors.append(f"{profile_path}.directness: replicated requires replication evidence")
        if consistency == "single_source" and len(all_clusters) > 1:
            errors.append(f"{profile_path}.consistency: multiple independent clusters are present")
        if consistency == "multi_source_aligned" and len(support_clusters) < 2:
            errors.append(
                f"{profile_path}.consistency: multi_source_aligned requires two clusters"
            )
        if consistency == "conflicting" and not counter:
            errors.append(f"{profile_path}.consistency: conflicting requires counter evidence")
        if reproducibility == "independently_reproduced":
            if "replication" not in support_types or len(support_clusters) < 2:
                errors.append(
                    f"{profile_path}.reproducibility: independently_reproduced requires "
                    "replication evidence across two clusters"
                )
        if external_validity in {"real_world", "longitudinal"} and not any(
            record.get("source_depth") in {"full_text", "external"}
            and record.get("evidence_type")
            in {"measured_result", "negative_result", "replication"}
            for record in support_records
        ):
            errors.append(
                f"{profile_path}.external_validity: {external_validity} requires "
                "measured full-text/external support"
            )

        if status not in {"unknown", "insufficient_evidence", "weakened"} and not support:
            errors.append(f"{path}.supporting_evidence_ids: required for status {status!r}")
        if status == "established":
            decisive_clusters = evidence_clusters(
                [
                    evidence_id
                    for evidence_id in support
                    if evidence_id in evidence_by_id
                    and evidence_by_id[evidence_id].get("source_depth")
                    in {"full_text", "external"}
                    and evidence_by_id[evidence_id].get("evidence_type")
                    in {"measured_result", "negative_result", "replication"}
                ],
                evidence_by_id,
                paper_info["clusters"],
            )
            if len(decisive_clusters) < 2:
                errors.append(
                    f"{path}.status: established requires decisive measured/replicated "
                    "full-text or external evidence from at least two independent clusters"
                )
            if directness not in {"measured", "replicated"}:
                errors.append(f"{profile_path}.directness: established must be measured/replicated")
            if consistency != "multi_source_aligned":
                errors.append(
                    f"{profile_path}.consistency: established must be multi_source_aligned"
                )
            if confidence != "high":
                errors.append(f"{path}.confidence: established proposition must be high")
        elif status == "credible_emerging":
            if len(support_clusters) < 2:
                errors.append(
                    f"{path}.status: credible_emerging requires at least two independent clusters"
                )
            if consistency == "single_source":
                errors.append(
                    f"{profile_path}.consistency: credible_emerging cannot be single_source"
                )
        elif status == "contested":
            if not support or not counter:
                errors.append(f"{path}.status: contested requires support and counter evidence")
            if consistency not in {"mixed", "conflicting"}:
                errors.append(
                    f"{profile_path}.consistency: contested must be mixed or conflicting"
                )
        elif status == "weakened" and not counter:
            errors.append(f"{path}.status: weakened requires counter evidence")

    return items, by_id, referenced_evidence


def validate_field_thesis(
    report: dict[str, Any],
    proposition_by_id: dict[str, dict[str, Any]],
    errors: list[str],
) -> dict[str, Any]:
    thesis = require_object(report, "field_thesis", "report", errors)
    path = "report.field_thesis"
    reject_unknown(
        thesis,
        {
            "direct_answer",
            "field_stage",
            "stage_rationale",
            "bottom_line_proposition_ids",
            "belief_updates",
            "decision_relevance",
            "epistemic_ceiling",
        },
        path,
        errors,
    )
    require_string(thesis, "direct_answer", path, errors)
    require_enum(
        thesis,
        "field_stage",
        {"pre_paradigm", "emerging", "consolidating", "maturing", "deployed"},
        path,
        errors,
    )
    require_string(thesis, "stage_rationale", path, errors)
    validate_refs(
        thesis.get("bottom_line_proposition_ids"),
        f"{path}.bottom_line_proposition_ids",
        set(proposition_by_id),
        errors,
        min_items=1,
        label="proposition ID",
    )
    require_string(thesis, "decision_relevance", path, errors)
    updates = require_list(thesis, "belief_updates", path, errors)
    for index, update in enumerate(updates):
        update_path = f"{path}.belief_updates[{index}]"
        if not isinstance(update, dict):
            errors.append(f"{update_path}: expected object")
            continue
        reject_unknown(
            update, {"prior_belief", "updated_belief", "proposition_ids"}, update_path, errors
        )
        require_string(update, "prior_belief", update_path, errors)
        require_string(update, "updated_belief", update_path, errors)
        validate_refs(
            update.get("proposition_ids"),
            f"{update_path}.proposition_ids",
            set(proposition_by_id),
            errors,
            min_items=1,
            label="proposition ID",
        )

    ceiling = require_object(thesis, "epistemic_ceiling", path, errors)
    ceiling_path = f"{path}.epistemic_ceiling"
    reject_unknown(
        ceiling,
        {"authority", "trend", "capability", "rationale"},
        ceiling_path,
        errors,
    )
    authority = require_enum(
        ceiling,
        "authority",
        {"none", "provisional", "supported", "established"},
        ceiling_path,
        errors,
    )
    require_enum(
        ceiling,
        "trend",
        {"none", "signals_only", "emerging", "structural"},
        ceiling_path,
        errors,
    )
    require_enum(
        ceiling,
        "capability",
        set(CAPABILITY_LEVEL),
        ceiling_path,
        errors,
    )
    require_string(ceiling, "rationale", ceiling_path, errors)
    if authority == "none" and any(
        proposition.get("status") == "established"
        for proposition in proposition_by_id.values()
    ):
        errors.append(
            f"{ceiling_path}.authority: none cannot coexist with an established proposition"
        )
    return ceiling


def validate_mechanism_model(
    report: dict[str, Any],
    proposition_by_id: dict[str, dict[str, Any]],
    errors: list[str],
) -> set[str]:
    model = require_object(report, "mechanism_model", "report", errors)
    path = "report.mechanism_model"
    proposition_ids = set(proposition_by_id)
    reject_unknown(
        model,
        {
            "model_type",
            "epistemic_status",
            "system_statement",
            "stages",
            "edges",
            "critical_path_stage_ids",
            "critical_path_note",
            "bottlenecks",
            "model_limitations",
        },
        path,
        errors,
    )
    model_type = require_enum(
        model,
        "model_type",
        {"source_synthesized", "analyst_reference"},
        path,
        errors,
    )
    epistemic_status = require_enum(
        model,
        "epistemic_status",
        {"established", "credible_emerging", "hypothesis", "design_completion"},
        path,
        errors,
    )
    require_string(model, "system_statement", path, errors)
    stages = require_list(model, "stages", path, errors)
    if not stages:
        errors.append(f"{path}.stages: at least one mechanism stage required")
    stage_ids: set[str] = set()
    model_proposition_ids: set[str] = set()
    for index, stage in enumerate(stages):
        stage_path = f"{path}.stages[{index}]"
        if not isinstance(stage, dict):
            errors.append(f"{stage_path}: expected object")
            continue
        reject_unknown(
            stage,
            {
                "id",
                "label_zh",
                "label_en",
                "purpose",
                "inputs",
                "outputs",
                "current_methods",
                "failure_modes",
                "proposition_ids",
            },
            stage_path,
            errors,
        )
        stage_id = require_slug(stage, "id", stage_path, errors)
        ensure_unique_id(stage_id, stage_ids, f"{stage_path}.id", errors)
        for key in ("label_zh", "label_en", "purpose"):
            require_string(stage, key, stage_path, errors)
        for key in ("inputs", "outputs", "current_methods", "failure_modes"):
            validate_string_list(stage.get(key), f"{stage_path}.{key}", errors)
        model_proposition_ids.update(validate_refs(
            stage.get("proposition_ids"),
            f"{stage_path}.proposition_ids",
            proposition_ids,
            errors,
            label="proposition ID",
        ))

    edges = require_list(model, "edges", path, errors)
    seen_edges: set[tuple[str, str]] = set()
    for index, edge in enumerate(edges):
        edge_path = f"{path}.edges[{index}]"
        if not isinstance(edge, dict):
            errors.append(f"{edge_path}: expected object")
            continue
        reject_unknown(
            edge,
            {
                "from_stage_id",
                "to_stage_id",
                "relation",
                "support_type",
                "proposition_ids",
            },
            edge_path,
            errors,
        )
        from_id = require_slug(edge, "from_stage_id", edge_path, errors)
        to_id = require_slug(edge, "to_stage_id", edge_path, errors)
        if from_id not in stage_ids:
            errors.append(f"{edge_path}.from_stage_id: unknown stage {from_id!r}")
        if to_id not in stage_ids:
            errors.append(f"{edge_path}.to_stage_id: unknown stage {to_id!r}")
        if from_id and from_id == to_id:
            errors.append(f"{edge_path}: self-loop is not allowed")
        edge_key = (from_id, to_id)
        if edge_key in seen_edges:
            errors.append(f"{edge_path}: duplicate directed edge {edge_key!r}")
        seen_edges.add(edge_key)
        require_string(edge, "relation", edge_path, errors)
        support_type = require_enum(
            edge,
            "support_type",
            {"source_supported", "cross_paper_inference", "analyst_design_completion"},
            edge_path,
            errors,
        )
        edge_props = validate_refs(
            edge.get("proposition_ids"),
            f"{edge_path}.proposition_ids",
            proposition_ids,
            errors,
            label="proposition ID",
        )
        model_proposition_ids.update(edge_props)
        if support_type in {"source_supported", "cross_paper_inference"} and not edge_props:
            errors.append(
                f"{edge_path}.proposition_ids: {support_type} edge requires proposition support"
            )
        if support_type == "analyst_design_completion" and epistemic_status == "established":
            errors.append(
                f"{edge_path}.support_type: established model cannot contain analyst design completion"
            )
    validate_refs(
        model.get("critical_path_stage_ids"),
        f"{path}.critical_path_stage_ids",
        stage_ids,
        errors,
        label="stage ID",
    )
    require_string(model, "critical_path_note", path, errors)

    bottlenecks = require_list(model, "bottlenecks", path, errors)
    for index, bottleneck in enumerate(bottlenecks):
        bottleneck_path = f"{path}.bottlenecks[{index}]"
        if not isinstance(bottleneck, dict):
            errors.append(f"{bottleneck_path}: expected object")
            continue
        reject_unknown(
            bottleneck,
            {"stage_id", "statement", "proposition_ids", "confidence"},
            bottleneck_path,
            errors,
        )
        stage_id = require_slug(bottleneck, "stage_id", bottleneck_path, errors)
        if stage_id not in stage_ids:
            errors.append(f"{bottleneck_path}.stage_id: unknown stage {stage_id!r}")
        require_string(bottleneck, "statement", bottleneck_path, errors)
        bottleneck_props = validate_refs(
            bottleneck.get("proposition_ids"),
            f"{bottleneck_path}.proposition_ids",
            proposition_ids,
            errors,
            min_items=1,
            label="proposition ID",
        )
        model_proposition_ids.update(bottleneck_props)
        require_enum(bottleneck, "confidence", CONFIDENCE, bottleneck_path, errors)

    limitations = validate_string_list(
        model.get("model_limitations"), f"{path}.model_limitations", errors
    )
    if (
        model_type == "analyst_reference"
        or epistemic_status in {"hypothesis", "design_completion"}
    ) and not limitations:
        errors.append(
            f"{path}.model_limitations: analyst-reference, hypothesis, or design-completion "
            "model requires explicit limitations"
        )
    if model_type == "analyst_reference" and epistemic_status == "established":
        errors.append(
            f"{path}.epistemic_status: analyst_reference model cannot be established"
        )
    if epistemic_status == "design_completion" and model_type != "analyst_reference":
        errors.append(
            f"{path}.model_type: design_completion requires analyst_reference"
        )
    if epistemic_status == "established" and not any(
        proposition_by_id[prop_id].get("status") == "established"
        for prop_id in model_proposition_ids
        if prop_id in proposition_by_id
    ):
        errors.append(
            f"{path}.epistemic_status: established model requires an established proposition"
        )
    return stage_ids


def validate_technical_options(
    report: dict[str, Any],
    stage_ids: set[str],
    paper_ids: set[str],
    proposition_ids: set[str],
    errors: list[str],
) -> set[str]:
    items = require_list(report, "technical_options", "report", errors)
    option_ids: set[str] = set()
    option_stage_ids: dict[str, set[str]] = {}
    comparable_options: list[tuple[str, str]] = []
    for index, item in enumerate(items):
        path = f"report.technical_options[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{path}: expected object")
            continue
        reject_unknown(
            item,
            {
                "id",
                "label_zh",
                "label_en",
                "technical_bet",
                "relationship",
                "comparison_status",
                "comparison_note",
                "mechanism_stage_ids",
                "core_hypothesis",
                "representative_paper_ids",
                "advantages",
                "costs",
                "failure_modes",
                "valid_when",
                "invalid_when",
                "supporting_proposition_ids",
                "falsifiers",
            },
            path,
            errors,
        )
        option_id = require_slug(item, "id", path, errors)
        ensure_unique_id(option_id, option_ids, f"{path}.id", errors)
        for key in (
            "label_zh",
            "label_en",
            "technical_bet",
            "core_hypothesis",
            "comparison_note",
        ):
            require_string(item, key, path, errors)
        require_enum(
            item,
            "relationship",
            {"alternative", "complementary", "baseline", "hybrid"},
            path,
            errors,
        )
        comparison_status = require_enum(
            item,
            "comparison_status",
            {"comparable", "partially_comparable", "not_comparable"},
            path,
            errors,
        )
        linked_stages = validate_refs(
            item.get("mechanism_stage_ids"),
            f"{path}.mechanism_stage_ids",
            stage_ids,
            errors,
            min_items=1,
            label="stage ID",
        )
        if option_id:
            option_stage_ids[option_id] = set(linked_stages)
            if comparison_status == "comparable":
                comparable_options.append((option_id, path))
        validate_paper_refs(
            item.get("representative_paper_ids"),
            f"{path}.representative_paper_ids",
            paper_ids,
            errors,
            min_items=1,
        )
        for key in (
            "advantages",
            "costs",
            "failure_modes",
            "valid_when",
            "invalid_when",
            "falsifiers",
        ):
            validate_string_list(item.get(key), f"{path}.{key}", errors)
        validate_refs(
            item.get("supporting_proposition_ids"),
            f"{path}.supporting_proposition_ids",
            proposition_ids,
            errors,
            min_items=1,
            label="proposition ID",
        )
        if comparison_status != "comparable":
            # Non-comparability notes and falsifiers may legitimately describe a
            # ranking that is absent today or would falsify the option.  Only an
            # asserted advantage is treated as an unsupported ranking claim.
            for value_path, text in walk_strings(
                item.get("advantages"), f"{path}.advantages"
            ):
                match = UNSUPPORTED_RANKING_RE.search(text)
                if match:
                    errors.append(
                        f"{value_path}: ranking language {match.group(0)!r} is unsupported "
                        f"when comparison_status is {comparison_status!r}"
                    )

    for option_id, path in comparable_options:
        stages = option_stage_ids.get(option_id, set())
        has_peer = any(
            other_id != option_id and bool(stages & other_stages)
            for other_id, other_stages in option_stage_ids.items()
        )
        if not has_peer:
            errors.append(
                f"{path}.comparison_status: comparable requires another technical option "
                "sharing at least one mechanism stage"
            )
    return option_ids


def validate_capability_frontier(
    report: dict[str, Any],
    evidence_by_id: dict[str, dict[str, Any]],
    proposition_ids: set[str],
    errors: list[str],
) -> tuple[set[str], set[str]]:
    frontier = require_object(report, "capability_frontier", "report", errors)
    path = "report.capability_frontier"
    reject_unknown(
        frontier,
        {"overall_statement", "capabilities", "readiness_gaps"},
        path,
        errors,
    )
    require_string(frontier, "overall_statement", path, errors)
    items = require_list(frontier, "capabilities", path, errors)
    if not items:
        errors.append(f"{path}.capabilities: at least one capability required")
    capability_ids: set[str] = set()
    referenced_evidence: set[str] = set()
    for index, item in enumerate(items):
        item_path = f"{path}.capabilities[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{item_path}: expected object")
            continue
        reject_unknown(
            item,
            {
                "id",
                "label_zh",
                "label_en",
                "current_boundary",
                "demonstration_context",
                "strongest_evidence_ids",
                "frontier_level",
                "observed_failures",
                "anticipated_risks",
                "generalization_ceiling",
                "unresolved_requirements",
                "next_boundary",
                "proposition_ids",
            },
            item_path,
            errors,
        )
        capability_id = require_slug(item, "id", item_path, errors)
        ensure_unique_id(capability_id, capability_ids, f"{item_path}.id", errors)
        for key in (
            "label_zh",
            "label_en",
            "current_boundary",
            "demonstration_context",
            "generalization_ceiling",
            "next_boundary",
        ):
            require_string(item, key, item_path, errors)
        strongest = validate_refs(
            item.get("strongest_evidence_ids"),
            f"{item_path}.strongest_evidence_ids",
            set(evidence_by_id),
            errors,
            min_items=1,
            label="evidence ID",
        )
        referenced_evidence.update(strongest)
        level = require_enum(
            item,
            "frontier_level",
            {
                "conceptual",
                "prototype",
                "benchmark",
                "controlled_user_study",
                "longitudinal_deployment",
            },
            item_path,
            errors,
        )
        observed_failures = require_list(
            item, "observed_failures", item_path, errors
        )
        for failure_index, failure in enumerate(observed_failures):
            failure_path = f"{item_path}.observed_failures[{failure_index}]"
            if not isinstance(failure, dict):
                errors.append(f"{failure_path}: expected object")
                continue
            reject_unknown(
                failure,
                {"statement", "evidence_ids"},
                failure_path,
                errors,
            )
            require_string(failure, "statement", failure_path, errors)
            failure_evidence = validate_refs(
                failure.get("evidence_ids"),
                f"{failure_path}.evidence_ids",
                set(evidence_by_id),
                errors,
                min_items=1,
                label="evidence ID",
            )
            referenced_evidence.update(failure_evidence)
            for evidence_id in failure_evidence:
                record = evidence_by_id.get(evidence_id)
                if not record:
                    continue
                if not isinstance(record.get("paper_id"), str) or not record.get(
                    "paper_id"
                ):
                    errors.append(
                        f"{failure_path}.evidence_ids: observed failure evidence "
                        f"{evidence_id!r} must be bound to a paper"
                    )
                evidence_type = record.get("evidence_type")
                if evidence_type not in OBSERVED_FAILURE_EVIDENCE_TYPES:
                    errors.append(
                        f"{failure_path}.evidence_ids: observed failure evidence "
                        f"{evidence_id!r} must be a paper-local source fact, got "
                        f"{evidence_type!r}"
                    )
        validate_string_list(
            item.get("anticipated_risks"),
            f"{item_path}.anticipated_risks",
            errors,
        )
        validate_string_list(
            item.get("unresolved_requirements"),
            f"{item_path}.unresolved_requirements",
            errors,
        )
        validate_refs(
            item.get("proposition_ids"),
            f"{item_path}.proposition_ids",
            proposition_ids,
            errors,
            min_items=1,
            label="proposition ID",
        )
        if level in {"controlled_user_study", "longitudinal_deployment"} and not any(
            evidence_by_id[evidence_id].get("source_depth") in {"full_text", "external"}
            for evidence_id in strongest
            if evidence_id in evidence_by_id
        ):
            errors.append(
                f"{item_path}.frontier_level: {level} requires full-text/external evidence"
            )

    readiness_gaps = require_list(frontier, "readiness_gaps", path, errors)
    gap_ids: set[str] = set()
    for index, gap in enumerate(readiness_gaps):
        gap_path = f"{path}.readiness_gaps[{index}]"
        if not isinstance(gap, dict):
            errors.append(f"{gap_path}: expected object")
            continue
        reject_unknown(
            gap,
            {
                "id",
                "label_zh",
                "label_en",
                "current_state",
                "blocking_evidence",
                "what_would_close",
                "proposition_ids",
            },
            gap_path,
            errors,
        )
        gap_id = require_slug(gap, "id", gap_path, errors)
        ensure_unique_id(gap_id, gap_ids, f"{gap_path}.id", errors)
        if gap_id in capability_ids:
            errors.append(
                f"{gap_path}.id: readiness gap ID must not reuse demonstrated capability ID"
            )
        for key in (
            "label_zh",
            "label_en",
            "current_state",
            "blocking_evidence",
        ):
            require_string(gap, key, gap_path, errors)
        validate_string_list(
            gap.get("what_would_close"),
            f"{gap_path}.what_would_close",
            errors,
            min_items=1,
        )
        validate_refs(
            gap.get("proposition_ids"),
            f"{gap_path}.proposition_ids",
            proposition_ids,
            errors,
            min_items=1,
            label="proposition ID",
        )
    return capability_ids, referenced_evidence


def validate_leading_indicators(
    report: dict[str, Any], proposition_ids: set[str], errors: list[str]
) -> set[str]:
    items = require_list(report, "leading_indicators", "report", errors)
    if not items:
        errors.append("report.leading_indicators: at least one indicator required")
    indicator_ids: set[str] = set()
    allowed = {
        "id",
        "label",
        "observation",
        "current_baseline",
        "threshold_or_trigger",
        "threshold_basis",
        "threshold_rationale",
        "data_source",
        "observation_window",
        "affects_proposition_ids",
        "interpretation_if_met",
        "interpretation_if_missed",
        "decision_trigger",
    }
    for index, item in enumerate(items):
        path = f"report.leading_indicators[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{path}: expected object")
            continue
        reject_unknown(item, allowed, path, errors)
        indicator_id = require_slug(item, "id", path, errors)
        ensure_unique_id(indicator_id, indicator_ids, f"{path}.id", errors)
        for key in (
            "label",
            "observation",
            "current_baseline",
            "threshold_or_trigger",
            "threshold_rationale",
            "data_source",
            "observation_window",
            "interpretation_if_met",
            "interpretation_if_missed",
            "decision_trigger",
        ):
            require_string(item, key, path, errors)
        require_enum(
            item,
            "threshold_basis",
            {"source_derived", "analyst_policy"},
            path,
            errors,
        )
        validate_refs(
            item.get("affects_proposition_ids"),
            f"{path}.affects_proposition_ids",
            proposition_ids,
            errors,
            min_items=1,
            label="proposition ID",
        )
    return indicator_ids


def proposition_support_evidence(
    proposition_ids: Iterable[str], proposition_by_id: dict[str, dict[str, Any]]
) -> list[str]:
    evidence_ids: list[str] = []
    for proposition_id in proposition_ids:
        proposition = proposition_by_id.get(proposition_id)
        if not proposition:
            continue
        support = proposition.get("supporting_evidence_ids")
        if isinstance(support, list):
            evidence_ids.extend(value for value in support if isinstance(value, str))
    return evidence_ids


def validate_transition_theses(
    report: dict[str, Any],
    proposition_by_id: dict[str, dict[str, Any]],
    evidence_by_id: dict[str, dict[str, Any]],
    paper_info: dict[str, Any],
    indicator_ids: set[str],
    scope_info: dict[str, Any],
    as_of: date | None,
    errors: list[str],
) -> set[str]:
    items = require_list(report, "transition_theses", "report", errors)
    transition_ids: set[str] = set()
    proposition_ids = set(proposition_by_id)
    allowed = {
        "id",
        "statement",
        "from_state",
        "to_state",
        "old_constraint",
        "drivers",
        "time_from",
        "time_to",
        "status",
        "supporting_proposition_ids",
        "counter_proposition_ids",
        "alternative_explanations",
        "falsifiers",
        "leading_indicator_ids",
        "confidence",
    }
    for index, item in enumerate(items):
        path = f"report.transition_theses[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{path}: expected object")
            continue
        reject_unknown(item, allowed, path, errors)
        transition_id = require_slug(item, "id", path, errors)
        ensure_unique_id(transition_id, transition_ids, f"{path}.id", errors)
        for key in ("statement", "from_state", "to_state", "old_constraint"):
            require_string(item, key, path, errors)
        for key in ("drivers", "alternative_explanations", "falsifiers"):
            validate_string_list(item.get(key), f"{path}.{key}", errors)
        time_from = validate_date(item.get("time_from"), f"{path}.time_from", errors)
        time_to = validate_date(item.get("time_to"), f"{path}.time_to", errors)
        if time_from and time_to and time_from > time_to:
            errors.append(f"{path}: time_from must not be after time_to")
        if time_to and as_of and time_to > as_of:
            errors.append(f"{path}.time_to: must not be after report.as_of")
        status = require_enum(
            item,
            "status",
            {"signal", "emerging", "structural", "reversal", "insufficient_evidence"},
            path,
            errors,
        )
        support_props = validate_refs(
            item.get("supporting_proposition_ids"),
            f"{path}.supporting_proposition_ids",
            proposition_ids,
            errors,
            label="proposition ID",
        )
        counter_props = validate_refs(
            item.get("counter_proposition_ids"),
            f"{path}.counter_proposition_ids",
            proposition_ids,
            errors,
            label="proposition ID",
        )
        if set(support_props) & set(counter_props):
            errors.append(f"{path}: supporting and counter propositions must be disjoint")
        validate_refs(
            item.get("leading_indicator_ids"),
            f"{path}.leading_indicator_ids",
            indicator_ids,
            errors,
            label="leading indicator ID",
        )
        confidence = require_enum(item, "confidence", CONFIDENCE, path, errors)

        support_evidence = proposition_support_evidence(support_props, proposition_by_id)
        clusters = evidence_clusters(
            support_evidence, evidence_by_id, paper_info["clusters"]
        )
        supporting_dates = sorted(
            {
                paper_info["dates"][record.get("paper_id")]
                for evidence_id in support_evidence
                if (record := evidence_by_id.get(evidence_id))
                and record.get("paper_id") in paper_info["dates"]
            }
        )
        temporal_spread = (
            len(supporting_dates) >= 2
            and supporting_dates[0] < supporting_dates[-1]
            and time_from is not None
            and time_to is not None
            and time_from < time_to
        )
        has_decisive_deep_support = any(
            evidence_by_id[evidence_id].get("source_depth") in {"full_text", "external"}
            and evidence_by_id[evidence_id].get("evidence_type")
            in {"measured_result", "negative_result", "replication"}
            for evidence_id in support_evidence
            if evidence_id in evidence_by_id
        )

        if status in {"signal", "emerging", "structural", "reversal"} and not support_props:
            errors.append(f"{path}.supporting_proposition_ids: required for status {status!r}")
        if status == "emerging":
            anchor = scope_info.get("layer_by_role", {}).get("anchor")
            if not anchor or anchor.get("status") not in {"searched", "partial"}:
                errors.append(
                    f"{path}.status: emerging requires a partial or searched anchor layer"
                )
            if len(clusters) < 2:
                errors.append(f"{path}.status: emerging requires at least two independent clusters")
            if not temporal_spread:
                errors.append(f"{path}.status: emerging requires temporal spread")
        elif status == "structural":
            anchor = scope_info.get("layer_by_role", {}).get("anchor")
            if not anchor or anchor.get("status") != "searched":
                errors.append(f"{path}.status: structural requires a searched anchor layer")
            if len(clusters) < 3:
                errors.append(f"{path}.status: structural requires at least three independent clusters")
            if not temporal_spread:
                errors.append(f"{path}.status: structural requires temporal spread")
            if not has_decisive_deep_support:
                errors.append(
                    f"{path}.status: structural requires decisive measured/replicated "
                    "full-text or external support"
                )
            if confidence != "high":
                errors.append(f"{path}.confidence: structural transition must be high")
            weak_statuses = {
                proposition_by_id[prop_id].get("status")
                for prop_id in support_props
                if prop_id in proposition_by_id
            } & {"unknown", "insufficient_evidence"}
            if weak_statuses:
                errors.append(
                    f"{path}.supporting_proposition_ids: structural transition cannot rely on "
                    f"{sorted(weak_statuses)}"
                )
        elif status == "reversal" and (not support_props or not counter_props):
            errors.append(f"{path}.status: reversal requires supporting and counter propositions")
    return transition_ids


def validate_epistemic_ceiling_alignment(
    report: dict[str, Any], ceiling: dict[str, Any], errors: list[str]
) -> None:
    path = "report.field_thesis.epistemic_ceiling"
    trend = ceiling.get("trend")
    allowed_transition_statuses = {
        "none": {"insufficient_evidence"},
        "signals_only": {"signal", "insufficient_evidence"},
        "emerging": {"signal", "emerging", "reversal", "insufficient_evidence"},
        "structural": {
            "signal",
            "emerging",
            "structural",
            "reversal",
            "insufficient_evidence",
        },
    }
    transitions = report.get("transition_theses")
    if isinstance(transitions, list) and trend in allowed_transition_statuses:
        disallowed = sorted(
            {
                item.get("status")
                for item in transitions
                if isinstance(item, dict)
                and item.get("status") not in allowed_transition_statuses[trend]
            }
        )
        if disallowed:
            errors.append(
                f"{path}.trend: {trend!r} ceiling cannot contain transition status(es) "
                f"{disallowed}"
            )

    frontier = report.get("capability_frontier")
    capabilities = frontier.get("capabilities") if isinstance(frontier, dict) else None
    demonstrated_levels = [
        item.get("frontier_level")
        for item in capabilities
        if isinstance(item, dict) and item.get("frontier_level") in CAPABILITY_LEVEL
    ] if isinstance(capabilities, list) else []
    if demonstrated_levels:
        expected = max(demonstrated_levels, key=CAPABILITY_LEVEL.__getitem__)
        if ceiling.get("capability") != expected:
            errors.append(
                f"{path}.capability: expected exact maximum demonstrated capability "
                f"{expected!r}, got {ceiling.get('capability')!r}; readiness gaps do not "
                "raise the demonstrated ceiling"
            )


def validate_maturity(
    report: dict[str, Any], proposition_by_id: dict[str, dict[str, Any]], errors: list[str]
) -> None:
    items = require_list(report, "maturity_assessment", "report", errors)
    if len(items) != 5:
        errors.append("report.maturity_assessment: exactly five dimensions required")
    seen: set[str] = set()
    for index, item in enumerate(items):
        path = f"report.maturity_assessment[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{path}: expected object")
            continue
        reject_unknown(
            item,
            {"dimension", "level", "statement", "proposition_ids", "blockers", "upgrade_conditions"},
            path,
            errors,
        )
        dimension = require_enum(item, "dimension", MATURITY_DIMENSIONS, path, errors)
        if dimension in seen:
            errors.append(f"{path}.dimension: duplicate {dimension!r}")
        seen.add(dimension)
        level = require_enum(
            item,
            "level",
            {"absent", "early", "emerging", "validated", "mature"},
            path,
            errors,
        )
        require_string(item, "statement", path, errors)
        refs = validate_refs(
            item.get("proposition_ids"),
            f"{path}.proposition_ids",
            set(proposition_by_id),
            errors,
            label="proposition ID",
        )
        for key in ("blockers", "upgrade_conditions"):
            validate_string_list(item.get(key), f"{path}.{key}", errors)
        if level != "absent" and not refs:
            errors.append(f"{path}.proposition_ids: non-absent maturity requires support")
        if level == "mature" and not any(
            proposition_by_id[prop_id].get("status") == "established"
            for prop_id in refs
            if prop_id in proposition_by_id
        ):
            errors.append(f"{path}.level: mature requires an established proposition")
    missing = sorted(MATURITY_DIMENSIONS - seen)
    if missing:
        errors.append(f"report.maturity_assessment: missing dimensions {missing}")


def validate_decision_consequences(
    report: dict[str, Any], proposition_ids: set[str], errors: list[str]
) -> set[str]:
    items = require_list(report, "decision_consequences", "report", errors)
    if not items:
        errors.append("report.decision_consequences: at least one consequence required")
    ids: set[str] = set()
    allowed = {
        "id",
        "decision_type",
        "audience",
        "decision",
        "action",
        "because_proposition_ids",
        "conditions",
        "risks",
        "reversibility",
        "confidence",
    }
    for index, item in enumerate(items):
        path = f"report.decision_consequences[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{path}: expected object")
            continue
        reject_unknown(item, allowed, path, errors)
        item_id = require_slug(item, "id", path, errors)
        ensure_unique_id(item_id, ids, f"{path}.id", errors)
        require_enum(
            item,
            "decision_type",
            {"research_agenda", "architecture", "product", "due_diligence"},
            path,
            errors,
        )
        for key in ("audience", "decision", "action"):
            require_string(item, key, path, errors)
        validate_refs(
            item.get("because_proposition_ids"),
            f"{path}.because_proposition_ids",
            proposition_ids,
            errors,
            min_items=1,
            label="proposition ID",
        )
        for key in ("conditions", "risks"):
            validate_string_list(item.get(key), f"{path}.{key}", errors)
        require_enum(
            item,
            "reversibility",
            {"reversible", "partially_reversible", "hard_to_reverse"},
            path,
            errors,
        )
        require_enum(item, "confidence", CONFIDENCE, path, errors)
    return ids


def validate_paper_links(
    paper_info: dict[str, Any],
    evidence_by_id: dict[str, dict[str, Any]],
    stage_ids: set[str],
    option_ids: set[str],
    capability_ids: set[str],
    proposition_ids: set[str],
    errors: list[str],
) -> set[str]:
    referenced_evidence: set[str] = set()
    metric_evidence_owner: dict[str, str] = {}
    evidence_by_paper: dict[str, set[str]] = defaultdict(set)
    for evidence_id, record in evidence_by_id.items():
        paper_id = record.get("paper_id")
        if isinstance(paper_id, str):
            evidence_by_paper[paper_id].add(evidence_id)

    for index, paper in enumerate(paper_info["papers"]):
        path = f"report.papers[{index}]"
        paper_id = paper.get("arxiv_id")
        if paper_id and not evidence_by_paper.get(paper_id):
            errors.append(f"{path}: included paper has no atomic evidence record")
        analysis = paper.get("analysis")
        if isinstance(analysis, dict):
            findings = analysis.get("key_findings")
            if isinstance(findings, list):
                for finding_index, finding in enumerate(findings):
                    if not isinstance(finding, dict):
                        continue
                    finding_path = f"{path}.analysis.key_findings[{finding_index}]"
                    refs = validate_refs(
                        finding.get("evidence_ids"),
                        f"{finding_path}.evidence_ids",
                        set(evidence_by_id),
                        errors,
                        min_items=1,
                        label="evidence ID",
                    )
                    for evidence_id in refs:
                        record = evidence_by_id.get(evidence_id)
                        if record and record.get("paper_id") != paper_id:
                            errors.append(
                                f"{finding_path}.evidence_ids: evidence {evidence_id!r} "
                                f"belongs to {record.get('paper_id')!r}, not {paper_id!r}"
                            )
                    referenced_evidence.update(refs)

        metrics = paper.get("metrics")
        if isinstance(metrics, list):
            for metric_index, metric in enumerate(metrics):
                if not isinstance(metric, dict):
                    continue
                metric_path = f"{path}.metrics[{metric_index}]"
                evidence_id = metric.get("evidence_id")
                if isinstance(evidence_id, str):
                    previous = metric_evidence_owner.get(evidence_id)
                    if previous is not None:
                        errors.append(
                            f"{metric_path}.evidence_id: metric evidence ID {evidence_id!r} "
                            f"is already bound to {previous}; use one atomic result evidence "
                            "record per metric"
                        )
                    else:
                        metric_evidence_owner[evidence_id] = metric_path
                record = evidence_by_id.get(evidence_id)
                if record is None:
                    errors.append(f"{metric_path}.evidence_id: unknown evidence ID {evidence_id!r}")
                    continue
                referenced_evidence.add(evidence_id)
                if record.get("paper_id") != paper_id:
                    errors.append(
                        f"{metric_path}.evidence_id: evidence belongs to "
                        f"{record.get('paper_id')!r}, not {paper_id!r}"
                    )
                basis = metric.get("basis")
                if basis != record.get("source_depth"):
                    errors.append(
                        f"{metric_path}.basis: expected {record.get('source_depth')!r} "
                        "from linked evidence"
                    )
                if record.get("evidence_type") not in {
                    "measured_result",
                    "negative_result",
                    "replication",
                }:
                    errors.append(
                        f"{metric_path}.evidence_id: metric requires measured/negative/replication evidence"
                    )
                if basis in EVIDENCE_DEPTH:
                    paper_level = PAPER_DEPTH.get(paper_info["basis"].get(paper_id, ""))
                    if paper_level is not None and EVIDENCE_DEPTH[basis] > paper_level:
                        errors.append(
                            f"{metric_path}.basis: exceeds paper evidence basis "
                            f"{paper_info['basis'].get(paper_id)!r}"
                        )

        links = paper.get("model_links")
        if isinstance(links, dict):
            validate_refs(
                links.get("stage_ids"),
                f"{path}.model_links.stage_ids",
                stage_ids,
                errors,
                label="stage ID",
            )
            validate_refs(
                links.get("option_ids"),
                f"{path}.model_links.option_ids",
                option_ids,
                errors,
                label="technical option ID",
            )
            validate_refs(
                links.get("capability_ids"),
                f"{path}.model_links.capability_ids",
                capability_ids,
                errors,
                label="capability ID",
            )
            validate_refs(
                links.get("proposition_ids"),
                f"{path}.model_links.proposition_ids",
                proposition_ids,
                errors,
                label="proposition ID",
            )
    return referenced_evidence


def validate_coverage(
    report: dict[str, Any],
    scope_info: dict[str, Any],
    paper_info: dict[str, Any],
    evidence: list[dict[str, Any]],
    errors: list[str],
) -> None:
    coverage = require_object(report, "evidence_coverage", "report", errors)
    path = "report.evidence_coverage"
    reject_unknown(
        coverage,
        {
            "papers_total",
            "metadata_only",
            "abstract_screened",
            "full_text_reviewed",
            "externally_verified",
            "evidence_records",
        },
        path,
        errors,
    )
    basis_counts = Counter(paper_info["basis"].values())
    expected = {
        "papers_total": len(paper_info["papers"]),
        "metadata_only": basis_counts["metadata"],
        "abstract_screened": basis_counts["abstract"],
        "full_text_reviewed": basis_counts["full_text"],
        "externally_verified": len(paper_info["externally_verified"]),
    }
    for key, expected_value in expected.items():
        actual = require_nonnegative_int(coverage, key, path, errors)
        if actual is not None and actual != expected_value:
            errors.append(f"{path}.{key}: expected {expected_value}, got {actual}")

    record_counts = require_object(coverage, "evidence_records", path, errors)
    records_path = f"{path}.evidence_records"
    reject_unknown(
        record_counts, {"metadata", "abstract", "full_text", "external"}, records_path, errors
    )
    actual_record_counts = Counter(
        record.get("source_depth") for record in evidence if isinstance(record, dict)
    )
    for key in ("metadata", "abstract", "full_text", "external"):
        actual = require_nonnegative_int(record_counts, key, records_path, errors)
        expected_value = actual_record_counts[key]
        if actual is not None and actual != expected_value:
            errors.append(f"{records_path}.{key}: expected {expected_value}, got {actual}")

    screening = scope_info.get("screening", {})
    if isinstance(screening, dict) and screening.get("included") != len(paper_info["papers"]):
        errors.append(
            "report.scope.screening.included: expected "
            f"{len(paper_info['papers'])} from included papers"
        )


def validate_report(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    reject_unknown(data, {"schema_version", "report"}, "root", errors)
    if data.get("schema_version") != "3.0":
        errors.append("schema_version: expected '3.0'")
    report = data.get("report")
    if not isinstance(report, dict):
        return errors + ["report: expected object"]
    report_fields = {
        "title_zh",
        "title_en",
        "topic",
        "as_of",
        "language",
        "scope",
        "evidence_coverage",
        "field_thesis",
        "propositions",
        "mechanism_model",
        "technical_options",
        "capability_frontier",
        "transition_theses",
        "maturity_assessment",
        "decision_consequences",
        "leading_indicators",
        "papers",
        "evidence",
        "report_limitations",
    }
    reject_unknown(report, report_fields, "report", errors)
    for key in ("title_zh", "title_en", "topic"):
        require_string(report, key, "report", errors)
    as_of = validate_date(report.get("as_of"), "report.as_of", errors)
    if report.get("language") != "zh-CN":
        errors.append("report.language: expected 'zh-CN'")

    scope_info = validate_scope(report, as_of, errors)
    paper_info = validate_papers(report, as_of, scope_info, errors)
    evidence, evidence_by_id = validate_evidence(report, paper_info, errors)
    _, proposition_by_id, proposition_evidence = validate_propositions(
        report, evidence_by_id, paper_info, errors
    )
    proposition_ids = set(proposition_by_id)
    epistemic_ceiling = validate_field_thesis(report, proposition_by_id, errors)
    stage_ids = validate_mechanism_model(report, proposition_by_id, errors)
    option_ids = validate_technical_options(
        report, stage_ids, set(paper_info["by_id"]), proposition_ids, errors
    )
    capability_ids, capability_evidence = validate_capability_frontier(
        report, evidence_by_id, proposition_ids, errors
    )
    indicator_ids = validate_leading_indicators(report, proposition_ids, errors)
    validate_transition_theses(
        report,
        proposition_by_id,
        evidence_by_id,
        paper_info,
        indicator_ids,
        scope_info,
        as_of,
        errors,
    )
    validate_epistemic_ceiling_alignment(report, epistemic_ceiling, errors)
    validate_maturity(report, proposition_by_id, errors)
    validate_decision_consequences(report, proposition_ids, errors)
    paper_evidence = validate_paper_links(
        paper_info,
        evidence_by_id,
        stage_ids,
        option_ids,
        capability_ids,
        proposition_ids,
        errors,
    )
    validate_coverage(report, scope_info, paper_info, evidence, errors)

    referenced_evidence = proposition_evidence | capability_evidence | paper_evidence
    orphan_evidence = sorted(set(evidence_by_id) - referenced_evidence)
    if orphan_evidence:
        errors.append(
            "report.evidence: orphan evidence record(s) are not referenced by a "
            "paper finding, metric, proposition, or capability: "
            f"{orphan_evidence}"
        )

    limitations = validate_string_list(
        report.get("report_limitations"),
        "report.report_limitations",
        errors,
        min_items=1,
    )
    if not limitations:
        errors.append("report.report_limitations: at least one limitation required")

    analytical_sections = {
        key: report.get(key)
        for key in (
            "title_zh",
            "title_en",
            "topic",
            "field_thesis",
            "propositions",
            "mechanism_model",
            "technical_options",
            "capability_frontier",
            "transition_theses",
            "maturity_assessment",
            "decision_consequences",
            "leading_indicators",
        )
    }
    reject_unsupported_superlatives(analytical_sections, "report", errors)
    return errors


def main() -> int:
    args = parse_args()
    try:
        data = load_report(args.input)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"validate_report_data: {exc}", file=sys.stderr)
        return 1

    errors = validate_report(data)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"Validation failed with {len(errors)} error(s).", file=sys.stderr)
        return 1

    paper_count = len(data["report"]["papers"])
    evidence_count = len(data["report"]["evidence"])
    print(
        f"Validated schema 3.0 report with {paper_count} paper(s) and "
        f"{evidence_count} evidence record(s): {args.input}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
