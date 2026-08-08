# arXiv Paper Report

`arxiv-paper-report` is an arXiv-centered field-intelligence skill. It is designed for vertical-domain and technology research where the output must change a belief or inform a concrete research, architecture, product, or due-diligence decision.

It does not treat paper summaries as the final product. The skill follows this derivation chain:

```text
atomic evidence
  -> source-grounded facts
  -> testable propositions
  -> current knowledge state
  -> capability frontier and readiness gaps
  -> source-supported or analyst-labeled mechanism model
  -> technical options and comparability
  -> transition theses
  -> five-dimensional maturity
  -> decision consequences
  -> leading indicators
```

## What it produces

- A strict, schema-validated JSON research record.
- A deterministic standalone HTML report with restrained Chinese/English typography.
- Explicit authority, trend, and capability evidence ceilings.
- Source-bound observed failures separated from analyst-anticipated risks.
- A capability frontier that preserves benchmark, controlled-study, and deployment boundaries.
- Technical options labeled as alternatives, complementary modules, baselines, or hybrids, with comparability made explicit.
- One primary decision that answers whether to invest, validate or productize, what to prioritize, and what not to do.
- Leading indicators that define what future observation should change the belief or decision.

## Dependencies

- The separately installed `literature-search-arxiv` skill for arXiv discovery and full-text retrieval.
- `uv` for the upstream arXiv search helper.
- Python 3 for normalization, validation, rendering, and verification.

The skill requires compliant, sequential arXiv requests and at least three seconds between separate API invocations. Preserve raw responses and follow each paper's license conditions.

## Package structure

| Path | Purpose |
|------|---------|
| `SKILL.md` | Complete agent workflow and acceptance contract |
| `references/report.schema.json` | Strict v3 JSON Schema |
| `references/analysis-rubric.md` | Proposition, evidence, frontier, maturity, and decision rules |
| `scripts/normalize_arxiv_stream.py` | Normalize preserved search streams |
| `scripts/validate_report_data.py` | Schema and semantic graph validation |
| `scripts/render_report.py` | Deterministic standalone HTML renderer |
| `scripts/verify_report.py` | Offline HTML integrity and safety verification |
| `assets/report.css` | Academic Decision Dossier visual system |
| `examples/sample-report.json` | Six-paper, abstract-only example research record |
| `examples/sample-report.html` | Generated example report |

## Validate the included example

```bash
python3 scripts/validate_report_data.py examples/sample-report.json

python3 scripts/render_report.py \
  --input examples/sample-report.json \
  --output /tmp/arxiv-paper-report.html

python3 scripts/verify_report.py \
  --data examples/sample-report.json \
  --html /tmp/arxiv-paper-report.html
```

Two renders from unchanged JSON should be byte-identical. The renderer has no CDN, JavaScript, or external asset dependency.

## Example evidence boundary

The included proactive-agent sample is intentionally conservative: it covers six 2026 arXiv preprints at abstract depth, without full-text review, external verification, or a historical anchor. Its valid top answer is therefore that no authoritative field view or historical trend can yet be established; demonstrated capability reaches benchmark level, not longitudinal deployment.

## Source and license notice

Skill code and original documentation follow the repository's license. Paper titles, abstracts, metadata, and linked research results remain the property of their respective authors and are not relicensed by this repository. Review the license attached to each arXiv paper before reuse or redistribution.
