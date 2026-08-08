#!/usr/bin/env python3
"""Normalize concatenated JSON emitted by literature-search-arxiv.

The upstream helper currently emits a cumulative JSON object after each parsed
paper. This utility accepts zero or many JSON values, selects the largest
successful envelope (favoring the latest on ties), normalizes identifiers, and
writes one deterministic JSON document.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


ARXIV_ID_RE = re.compile(r"^(?P<base>[0-9]{4}\.[0-9]{4,5})(?P<version>v[0-9]+)?$")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--query-label", default="")
    return parser.parse_args()


def decode_stream(raw: str) -> list[Any]:
    decoder = json.JSONDecoder()
    values: list[Any] = []
    cursor = 0
    length = len(raw)
    while cursor < length:
        while cursor < length and raw[cursor].isspace():
            cursor += 1
        if cursor >= length:
            break
        try:
            value, cursor = decoder.raw_decode(raw, cursor)
        except json.JSONDecodeError as exc:
            context = raw[max(0, exc.pos - 60) : exc.pos + 60]
            raise ValueError(
                f"Invalid JSON stream at character {exc.pos}: {exc.msg}; "
                f"context={context!r}"
            ) from exc
        values.append(value)
    return values


def clean_text(value: Any) -> str:
    if value is None:
        return ""
    return " ".join(str(value).split())


def normalize_paper(raw: dict[str, Any]) -> dict[str, Any]:
    raw_id = clean_text(raw.get("id"))
    match = ARXIV_ID_RE.fullmatch(raw_id)
    if not match:
        raise ValueError(f"Unexpected arXiv ID: {raw_id!r}")

    base_id = match.group("base")
    version = match.group("version") or "v1"
    authors = [clean_text(author) for author in raw.get("authors", [])]
    authors = [author for author in authors if author]
    published_raw = clean_text(raw.get("published"))

    return {
        "arxiv_id": base_id,
        "version": version,
        "title": clean_text(raw.get("title")),
        "authors": authors,
        "published": published_raw[:10],
        "summary": clean_text(raw.get("summary")),
        "primary_category": clean_text(raw.get("primary_category")),
        "doi": clean_text(raw.get("doi")),
        "journal_ref": clean_text(raw.get("journal_ref")),
        "comment": clean_text(raw.get("comment")),
        "source_url": f"https://arxiv.org/abs/{base_id}",
        "pdf_url": clean_text(raw.get("pdf_url"))
        or f"https://arxiv.org/pdf/{base_id}",
    }


def version_number(version: str) -> int:
    return int(version.removeprefix("v"))


def normalize(values: list[Any], query_label: str) -> dict[str, Any]:
    if not values:
        return {
            "query_label": query_label,
            "raw_json_values": 0,
            "results_count": 0,
            "papers": [],
        }

    envelopes = [
        value
        for value in values
        if isinstance(value, dict)
        and value.get("status") == "success"
        and isinstance(value.get("papers"), list)
    ]
    if not envelopes:
        raise ValueError("No successful arXiv result envelope found")

    _, final = max(
        enumerate(envelopes),
        key=lambda indexed: (len(indexed[1]["papers"]), indexed[0]),
    )
    deduplicated: dict[str, dict[str, Any]] = {}
    for item in final["papers"]:
        if not isinstance(item, dict):
            continue
        paper = normalize_paper(item)
        existing = deduplicated.get(paper["arxiv_id"])
        if existing is None or version_number(paper["version"]) > version_number(
            existing["version"]
        ):
            deduplicated[paper["arxiv_id"]] = paper

    papers = sorted(
        deduplicated.values(),
        key=lambda paper: (paper["published"], paper["arxiv_id"]),
        reverse=True,
    )
    return {
        "query_label": query_label,
        "raw_json_values": len(values),
        "results_count": len(papers),
        "papers": papers,
    }


def main() -> int:
    args = parse_args()
    try:
        values = decode_stream(args.input.read_text(encoding="utf-8"))
        result = normalize(values, args.query_label)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(result, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"normalize_arxiv_stream: {exc}", file=sys.stderr)
        return 1

    print(
        f"Normalized {result['results_count']} papers from "
        f"{result['raw_json_values']} JSON values -> {args.output}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
