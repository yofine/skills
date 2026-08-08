---
name: arxiv-paper-report
description: "Search arXiv and, when needed, verify external academic sources to update field beliefs and one primary decision through testable propositions, capability frontiers, explicitly labeled mechanism models, technical options, transition theses, five-dimensional maturity, leading indicators, and a restrained bilingual standalone HTML report. Use for vertical-domain or technology research, literature landscapes, frontier scans, research or architecture decisions, due diligence, or HTML field-intelligence reports."
---

# arXiv Decision Intelligence Report

Research a vertical field or technology through papers, then convert the corpus
into updated field beliefs and explicit decisions. Deliver a validated v3 JSON
record and a deterministic standalone HTML report. Chinese is the primary
editorial language; preserve original English titles and precise technical terms.

The report's value is **not** paper summaries, section completeness, or evidence
traceability. Those are audit infrastructure. The value is a defensible answer to:

1. What should the reader believe about the field now?
2. What has actually been demonstrated, and where is the capability boundary?
3. Which technical mechanisms and options could move that boundary?
4. Is the field undergoing a structural transition or only a cluster of signals?
5. How mature is the field scientifically, technically, operationally, and in
   governance?
6. Should the decision-maker invest now, validate or productize, in what priority
   order, what should they not do, and what observation should change that choice?

If the corpus cannot support those answers, say that the evidence is insufficient.
Do not fill the report with plausible synthesis to simulate insight.

## Required derivation chain

Follow this chain in order. A later object must be derived from earlier objects:

```text
atomic evidence
  -> mechanism and experimental facts
  -> testable field propositions
  -> current knowledge state
  -> capability frontier and readiness gaps
  -> source-supported mechanism or analyst reference architecture
  -> technical options and their comparability
  -> transition theses
  -> five-dimensional maturity
  -> decision consequences
  -> leading indicators and belief-update triggers
```

In the v3 contract, `propositions` and their statuses form the current knowledge
state. Paper-level `analysis.mechanism`, `analysis.evaluation`, and
`analysis.key_findings` preserve the mechanism and experimental facts from which
the field model is built. `field_thesis` records the direct answer and explicit
belief updates that follow from those propositions. Do not skip from abstracts
directly to strategy prose.

## Non-negotiable contract

1. Treat this workflow as **arXiv-centered, not arXiv-only**. Use the installed
   `literature-search-arxiv` skill for discovery and full-text retrieval. Read its
   complete `SKILL.md` first and obey its license notification, rate limit,
   URL-listing, download, and safe-extraction rules.
2. Never issue arXiv requests in parallel. Use the supplied helper and leave at
   least three seconds between separate invocations.
3. Preserve every raw search response. Normalize it with
   `scripts/normalize_arxiv_stream.py`; never hand-rewrite source metadata.
4. Analyze into the exact v3 contract in `references/report.schema.json`. HTML is
   a deterministic view of the JSON, never a second analysis pass.
5. Record exact discovery queries, query layer, sort, limit, and date boundary.
   A list of already-known arXiv IDs is not a reproducible discovery query.
6. Build an atomic `evidence` ledger. Every proposition and model judgment must
   resolve through IDs to appropriate source evidence and locators.
7. Distinguish `metadata`, `abstract`, `full_text`, and `external` evidence.
   Apply an honest `evidence_ceiling`; missing depth cannot be repaired by prose.
8. Distinguish **shared narrative** from **independent validation**. Several
   papers repeating the same premise show framing convergence, not that the
   premise has been independently tested or reproduced.
9. Do not claim peer review, publication, citation impact, influence, replication,
   adoption, or authority without external academic verification. Record source,
   URL, access date, and the exact verified fact.
10. Preserve original English titles. `title_zh` is editorial analysis, not source
    metadata. Separate author statements, measured results, and analyst inference.
11. List the arXiv URL of every analyzed paper in the report and final response.
12. Frame one primary decision maker, choice, and time horizon. Secondary contexts
    may receive subordinate consequences but may not become co-equal report goals.

## Evidence ceilings and interpretive boundaries

- **Latest is not frontier.** Frontier requires a demonstrated boundary and a
  bounded delta from it.
- **Shared language is not validation.** Independent groups must directly test a
  compatible proposition under interpretable conditions.
- **One paper is not a transition.** A single work is a signal regardless of
  novelty or headline result.
- **Submission volume is not prevalence or adoption.** Search counts describe
  this retrieval only.
- **A benchmark win is not deployment readiness.** Preserve the demonstration
  context and generalization ceiling.
- **Prestige is not evidence.** Author, lab, venue, affiliation, citations, or
  recency never replace direct evidence.
- **Current-year-only abstract scans produce signal hypotheses only.** They may
  describe recent submissions, but cannot establish historical change,
  `established` propositions, `structural` transitions, validated maturity, or
  real-world capability. Mark the missing anchor/full-text/external layers.
- **Coverage is not a scientific result.** “This search found no deployment
  evidence” belongs in coverage gaps and the epistemic ceiling, not in a field
  proposition claiming the technology has no deployments.
- **Modules are not automatically alternatives.** Memory, gating, feedback, and
  execution may be complementary stages. Rank only options that address the same
  choice under genuinely comparable conditions.
- **Analyst design is not source mechanism.** Label a reference architecture and
  every design-completion edge visibly; never let a useful synthesis inherit the
  authority of its source papers.

Read `references/analysis-rubric.md` completely before screening or synthesis.

## Defaults

- Decision context: exactly one primary research agenda, technology strategy,
  architecture, product, or due-diligence decision; optional secondary contexts
  remain subordinate.
- Corpus layers: historical anchor, counterevidence, recent frontier from roughly
  12–24 months, and emerging signal from roughly 3–6 months.
- Search breadth: 4–8 real query families, normally 5–20 results each; paginate.
- Report corpus: normally 10–25 papers; prefer mechanism and negative-evidence
  coverage over a target count.
- Evidence: abstracts for discovery; full text for decisive mechanisms,
  comparisons, results, and limitations; external sources for scholarly status,
  replication, adoption, and real-world claims.
- Language/output: `zh-CN`, exact English titles, plus
  `<topic-slug>-field-report.{json,html}` unless otherwise requested.

## Workflow

### 1. Frame the decision before the search

Populate `scope` with the operational field boundary and one structured
`decision_context`:

- `primary` decision type;
- one `decision_maker`, one `choice_at_stake`, and one `time_horizon`;
- optional `secondary` contexts that remain subordinate to the primary choice;
- current or prior belief that may be updated;
- operational definition and unit of analysis;
- preferred, adjacent, and historical terminology;
- inclusion, exclusion, date, and category boundaries;
- what evidence would change the decision;
- report `as_of` date.

The schema-valid decision types are `research_agenda`, `technology_strategy`,
`architecture`, `product`, and `due_diligence`. Listing several secondary uses
does not make them co-equal; only the primary choice controls scope and the top
answer. Record `scope.coverage_gaps` rather than burying known omissions in final
caveats.

The research question must contain a decision consequence. “有哪些论文” is a
search request, not a field-intelligence question.

### 2. Build a four-layer corpus

Create `scope.corpus_layers` entries with an `id`, `role`, `status`, dates,
purpose, and an honest `coverage_note`. Use `searched`, `partial`, or
`not_searched` for status:

1. **Historical anchor** — actual earlier papers, surveys, paradigms, benchmarks,
   or capability records needed to define the prior state.
2. **Counterevidence** — failures, critiques, negative results, robustness gaps,
   competing mechanisms, and boundary conditions.
3. **Recent frontier** — work that may move a capability, mechanism, evaluation,
   engineering, deployment, or governance boundary.
4. **Emerging signal** — very recent or isolated work that suggests a hypothesis
   but is not yet a transition.

Missing layers remain explicit. Never derive a historical baseline solely from
recent papers describing their own novelty. A failure paper found incidentally is
not a dedicated counterevidence search; if none was run, keep that layer `partial`
or `not_searched` in the Decision Brief and Evidence Boundary.

Build complementary title/abstract, mechanism, benchmark, application, failure,
and replication queries. In `scope.queries`, preserve the exact query string and
reference its `layer_id`. Distinguish genuine discovery queries from later ID-based
metadata retrieval. Enforce date windows both in the query where supported and
again against normalized API dates during screening.

### 3. Search arXiv compliantly

Resolve `literature-search-arxiv` from the active skill list and run its bundled
search helper from that skill directory. Redirect every response to a dedicated
run directory.

The dependency requests `uv`. If no `uv` skill is exposed, check `uv --version`.
Continue when the executable exists and document the fallback. If it is absent,
stop and report the missing prerequisite; do not replace the helper.

```bash
uv run "[ARXIV_SKILL_DIR]/scripts/search_arxiv.py" \
  --query "[QUERY]" --max_results 10 \
  --sort_by relevance --sort_order descending \
  > "[RUN_DIR]/raw/query-01.jsonstream"
```

Normalize each stream:

```bash
python3 "[THIS_SKILL_DIR]/scripts/normalize_arxiv_stream.py" \
  --input "[RUN_DIR]/raw/query-01.jsonstream" \
  --output "[RUN_DIR]/normalized/query-01.json" \
  --query-label "Historical anchor — canonical mechanism"
```

Deduplicate by base arXiv ID, retain the newest retrieved version and all query
provenance, and use supplied dates rather than inferring dates from IDs.

### 4. Screen for field value, not topical resemblance

Screen in two passes:

1. **Topical fit** — the title and abstract satisfy the operational definition.
2. **Model value** — the paper supplies an anchor, mechanism, experiment,
   capability demonstration, counterexample, comparison, or signal needed by the
   field model.

Assign one primary corpus role: `anchor`, `frontier`, `signal`, or
`counterevidence`. Preserve exclusion reasons for borderline and high-salience
papers. Record retrieved, deduplicated, screened, and included counts in
`scope.screening`; record full-text and external coverage in `evidence_coverage`.
Counts, query logs, and layer coverage must reconcile.

### 5. Enrich papers that control the answer

Retrieve full text whenever a decisive proposition depends on architecture,
mechanism, experimental conditions, exact comparisons, figures, tables, author
limitations, or claimed novelty. Record section/page/table/figure locators.

Use official venue/publisher records, DOI/Crossref, OpenAlex, Semantic Scholar,
official project or replication records, or another primary academic source for
external verification. Search snippets are discovery aids, not evidence.

### 6. Build atomic evidence and paper facts

Create one `evidence` record per indivisible source fact. Separate author framing,
measured result, negative result, replication, derived comparison, analyst
inference, and external validation. External evidence requires `source_url`. Do
not combine a mechanism claim and several metrics into one evidence record. Each
paper `metric` must have its own unique `evidence_id`; never reuse one compound
evidence record for two values.

For each paper, populate `analysis.research_object`, `analysis.mechanism`,
`analysis.evaluation`, `analysis.key_findings`,
`analysis.author_stated_limitations`, and
`analysis.analyst_inferred_limitations`. Use `model_links` to connect the paper to
relevant `stage_ids`, `option_ids`, `capability_ids`, and `proposition_ids`.
Preserve `abstract_original`; keep it out of the main decision narrative. Assign an
`independence_cluster_id` so overlapping labs, author groups, and companion work
cannot be miscounted as independent validation.

Reconcile `evidence_coverage` with the included papers and evidence records.

### 7. Form testable propositions and the field thesis

Write propositions before conclusions. Every item in `propositions` must contain:

- `statement`, `proposition_type`, `status`, and `scope_conditions`;
- supporting and counter evidence IDs plus `alternative_explanations`;
- `evidence_ceiling`, `confidence`, `uncertainty`, and
  `what_would_change`;
- `decision_relevance`;
- an `evidence_profile` covering `directness`, `consistency`,
  `external_validity`, `reproducibility`, and `rationale`.

Apply the exact status rules in the rubric. A repeated author claim can be
`multi_source_aligned` while remaining an unvalidated shared narrative.
Corpus coverage statements such as “this scan found no deployment paper” are not
scientific propositions. Keep them in `scope.coverage_gaps`,
`evidence_coverage`, report limitations, and the thesis ceiling.

Derive `field_thesis` from the completed propositions. Populate `direct_answer`,
`field_stage`, `stage_rationale`, `bottom_line_proposition_ids`,
`belief_updates`, `decision_relevance`, and `epistemic_ceiling`. Every belief update must state
`prior_belief`, `updated_belief`, and the proposition IDs that justify the change.
Allowed field stages are `pre_paradigm`, `emerging`, `consolidating`, `maturing`,
and `deployed`. Do not choose a stage from paper volume or recency.

Set `epistemic_ceiling.authority`, `.trend`, `.capability`, and `.rationale`
before writing `direct_answer`. When the authority ceiling is `none`, the valid
top answer is “当前没有可成立的 authoritative field view”; do not manufacture an
authoritative-view section. With a current-year abstract corpus and no searched
or partial anchor layer, set trend to `signals_only` and keep every transition at
`signal` or `insufficient_evidence`.

### 8. Establish the capability frontier before explaining mechanisms

Populate `capability_frontier.overall_statement` and each capability's
`current_boundary`, `demonstration_context`, `strongest_evidence_ids`,
`frontier_level`, `observed_failures`, `anticipated_risks`, `generalization_ceiling`,
`unresolved_requirements`, `next_boundary`, and `proposition_ids`.

Every observed failure contains `statement` and nonempty, unique `evidence_ids`;
it must be directly source-bound. `anticipated_risks` are explicitly analyst inference.
Never relabel an unmeasured concern or coverage gap as an observed failure.

Put unachieved desired capabilities in `readiness_gaps`, not in the demonstrated
frontier. Each gap records its identity and labels, `current_state`,
`blocking_evidence`, `what_would_close`, and `proposition_ids`. State when the
strongest evidence is benchmark-only and show its exact result, baseline, task,
and simultaneous failure in the main narrative.

### 9. Build a labeled mechanism model and technical options

Only after the capability boundary is explicit, build `mechanism_model`:

- choose `model_type` as `source_synthesized` or `analyst_reference` and set its
  `epistemic_status`;
- `system_statement` defines the functional boundary;
- `stages` state purpose, inputs, outputs, current methods, failure modes, and
  linked propositions;
- every edge records its relation and `support_type`: `source_supported`,
  `cross_paper_inference`, or `analyst_design_completion`;
- `critical_path_stage_ids` and `critical_path_note` explain which stages are
  necessary and why;
- structured `bottlenecks` bind a stage, statement, propositions, and confidence;
- `model_limitations` state omissions and analyst completion.

An analyst reference architecture must be visibly labeled in JSON and HTML. Do
not present analyst-added authorization, rollback, memory, or control relations as
source-supported mechanisms.

Populate `technical_options`, not a generic list of competing approaches. Each
option states its `technical_bet`, `relationship`, `comparison_status`,
`comparison_note`, mechanism stages, hypothesis, representative papers,
advantages, costs, failures, validity conditions, supporting propositions, and
falsifiers. Use `alternative` only for substitutable choices that address the same
stage and objective. Use `complementary`, `baseline`, or `hybrid` honestly.
Rank options only when `comparison_status` is `comparable`; partially comparable
or non-comparable options may be contrasted but never ranked.
When the primary decision compares architectures, include material static-rule,
end-to-end LLM, human-confirmation, or mixed-initiative baselines as applicable.
Mark unevaluated baselines `baseline` / `not_comparable`; never invent a direct
comparison, result, or paper support.

### 10. Derive transitions, maturity, decisions, and indicators

A `transition_theses` item must specify `from_state`, `to_state`, the
`old_constraint`, drivers, time window, status, supporting and counter
propositions through `supporting_proposition_ids` and
`counter_proposition_ids`, plural `alternative_explanations`, falsifiers, linked
leading indicators, and confidence. Submission clustering alone yields `signal`,
not a structural transition.

Create exactly one `maturity_assessment` entry for each dimension:

- `scientific_mechanism`
- `benchmark`
- `engineering`
- `deployment`
- `governance`

Each entry requires a level, bounded statement, proposition links, blockers, and
upgrade conditions. Never average the five dimensions into a decorative score.

Every `decision_consequences` item must identify `decision_type`, `audience`, the
actual `decision`, a concrete `action`, `because_proposition_ids`, conditions,
risks, `reversibility`, and confidence. Generic “值得关注” prose is invalid.
The first and strongest consequence must answer the primary decision context;
secondary consequences must be visibly subordinate and may not redefine the
choice or time horizon. It explicitly states: invest now or not; fund validation
or productization; the ordered priorities; and what must not be done in this
horizon. A reversible validation investment is not production authorization.
When `scope.decision_context` includes `technology_strategy`, express its concrete
consequences through the schema's `research_agenda`, `architecture`, `product`,
or `due_diligence` decision types rather than inventing a fifth value.

Every `leading_indicators` item must define a label, observable event or measure,
`current_baseline`, `threshold_or_trigger`, `threshold_basis`,
`threshold_rationale`, `data_source`, `observation_window`, affected propositions,
interpretation if met and missed, and the resulting `decision_trigger`. Mark a
threshold invented for an internal decision rule as `analyst_policy`; never imply
that “two teams” or “four weeks” came from literature unless `source_derived` is
actually supported. “更多研究出现” is not an indicator unless the unit, source,
threshold, and belief update are explicit.

### 11. Validate the v3 research record

```bash
python3 "[THIS_SKILL_DIR]/scripts/validate_report_data.py" \
  "[OUTPUT_DIR]/<topic-slug>-field-report.json"
```

Fix every error. Never weaken validation to accommodate incomplete analysis.

Required negative-test classes include:

- duplicate IDs, unknown fields, dangling evidence/model references, duplicate
  base arXiv IDs, impossible dates, and inconsistent coverage counts;
- missing/ambiguous primary decision context or co-equal secondary contexts;
- a thesis that outruns its propositions or `epistemic_ceiling`, including a
  manufactured authoritative view when authority is `none`;
- a coverage gap encoded as a scientific proposition;
- non-atomic evidence, two metrics sharing one evidence ID, full-text evidence
  without a locator, or external facts without URL/access date;
- an `established` proposition supported only by metadata/abstracts or shared
  narrative;
- false independent validation from overlapping authors/labs or repeated claims;
- a capability level beyond its context, an unmet capability modeled as
  demonstrated, legacy `common_failures`, an unreferenced observed failure, or
  an analyst risk mislabeled as observed;
- an analyst reference model presented as source-synthesized, an unlabeled
  design-completion edge, or an unsupported bottleneck/critical path;
- complementary modules labeled as alternatives, a non-comparable option ranked,
  or a technical option without conditions, costs, failures, and falsifiers;
- a transition without a historical state, independent sequence,
  counterpropositions, alternatives, falsifiers, or linked indicators;
- maturity above its evidence ceiling or without blockers/upgrade conditions;
- a decision without proposition support, conditions, risks, or reversibility;
- an indicator without threshold basis/rationale or an internally invented
  threshold not marked `analyst_policy`;
- a current-year abstract fixture without an anchor that is not capped at
  `signals_only`, or that claims established/structural/validated/mature,
  real-world, longitudinal, or independent reproduction.

Run representative mutations from these classes and confirm rejection for the
expected reason, not merely a generic parse failure.

### 12. Render an outcome-first HTML report

```bash
python3 "[THIS_SKILL_DIR]/scripts/render_report.py" \
  --input "[OUTPUT_DIR]/<topic-slug>-field-report.json" \
  --output "[OUTPUT_DIR]/<topic-slug>-field-report.html"
```

Do not hand-edit generated HTML. The fixed information architecture is:

1. **Decision Brief** — direct answer, visible authority/trend/capability ceiling,
   changed beliefs, and the primary decision.
2. **Current Field Beliefs** — proposition status, scope, uncertainty, and what
   would change each judgment.
3. **Capability Frontier** — demonstrated boundary, context, source-bound
   observed failures, analyst-inferred risks, ceiling, and next boundary.
4. **Mechanism Model & Technical Options** — source-supported versus analyst-added
   relations, option relationships, comparability, and actual technical bets.
5. **Transition Theses** — bounded from/to shifts, alternatives, and falsifiers.
6. **Five-Dimensional Maturity** — separate scientific, benchmark, engineering,
   deployment, and governance readiness.
7. **Decision Consequences** — act, conditions, risks, and reversibility.
8. **Leading Indicators** — measurable belief and decision update triggers.
9. **Evidence Boundary** — coverage, missing layers, and material uncertainty.
10. **Evidence Appendix** — paper dossiers, evidence ledger, exact search method,
    exclusions, external verification, and all source URLs.

Evidence chips and paper cards must not interrupt the main reasoning. Main-view
citations use short stable ordinals such as `[E01]`; raw evidence IDs belong only
in the appendix and link target. Keep key qualifications visible, while detailed
dossiers, abstracts, records, and search logs remain in the appendix.

### 13. Verify artifact and research acceptance

```bash
python3 "[THIS_SKILL_DIR]/scripts/verify_report.py" \
  --data "[OUTPUT_DIR]/<topic-slug>-field-report.json" \
  --html "[OUTPUT_DIR]/<topic-slug>-field-report.html"
```

Acceptance requires all of the following:

1. JSON validation and semantic cross-reference checks pass.
2. Required negative mutations fail for the intended reasons.
3. Two renders of unchanged JSON have identical hashes.
4. HTML has doctype, UTF-8 charset, viewport, methodology, evidence ceiling,
   exact queries, external links, and every analyzed arXiv URL.
5. Desktop and narrow layouts are visually inspected; English titles do not
   overflow, Chinese text does not create awkward single-character wraps, and
   print remains legible.
6. A cold reader can answer the six value questions, including invest-now,
   validation-versus-productization, priority, and prohibition, without a dossier.
7. Every decision consequence names the propositions that justify it, and every
   leading indicator states how it changes a belief and decision.
8. The top answer remains valid when it says no authoritative view or no trend is
   currently supportable; no empty section is filled to imply otherwise.

## Editorial and visual voice

- Calm, restrained, professional, and outcome-first: an Academic Decision
  Dossier, not a dashboard, newsletter, or promotional page.
- Lead with bounded judgments and decisions, never “本文介绍了” or paper counts.
- Prefer mechanism diagrams, frontier matrices, technical-option tables, and
  indicator registers only when the structured relationships exist.
- Never manufacture numeric scores, maturity averages, or charts for decoration.
- Use off-white paper, near-black ink, cool-gray rules, and muted steel-blue; no
  gradients, glossy cards, decorative icons, or SaaS dashboard blue.
- Keep conclusions, scope conditions, uncertainty, and falsifiers visible. Put
  evidence details and original abstracts in the appendix.

## Included resources

- `references/report.schema.json` and `analysis-rubric.md` — v3 contract and rules.
- `scripts/` — normalization, validation, rendering, and artifact verification.
- `assets/report.css` and `examples/sample-report.json` — visual system and v3 example.

## Final response

State both skills used and link JSON/HTML; report date, primary decision, coverage,
investment/validation priority and prohibition, limitations, and every arXiv URL.
