# Decision Intelligence Analysis Rubric

This rubric converts an arXiv-centered corpus into updated field beliefs and
decision consequences. Papers and evidence records are the audit trail; they are
not the research product. A report succeeds only when it states what is currently
believable, what remains unknown, where the demonstrated capability boundary is,
which technical bets compete, what decision follows, and what observation should
change that decision.

## 1. The unit of synthesis

The primary unit is a **testable field proposition**, not a paper and not a topic
cluster. Follow this derivation chain without skipping levels:

```text
evidence
  -> source-grounded mechanism and experimental facts
  -> propositions
  -> proposition statuses as the current knowledge state
  -> capability frontier and readiness gaps
  -> source-supported mechanism or analyst reference architecture
  -> technical options and their comparability
  -> transition theses
  -> five-dimensional maturity
  -> decision consequences
  -> leading indicators
```

Each arrow is an inference boundary. Preserve its assumptions and evidence
ceiling. Repeating one abstract across several report sections does not create
additional information.

Before accepting a synthesis, ask:

- Does it update a prior belief rather than merely describe papers?
- Is the proposition falsifiable and scoped?
- Is the demonstrated capability separated from the authors' aspiration?
- Are mechanism support types, technical-option relationships, and alternative
  explanations visible?
- Is the decision conditional, reversible where possible, and evidence-linked?
- Is there an observable future signal that will update the belief?

## 2. Decision frame and corpus coverage

The `scope.research_question` must state the choice the research will inform.
Populate one structured `scope.decision_context`:

- `primary` — one of `research_agenda`, `technology_strategy`, `architecture`,
  `product`, or `due_diligence`;
- `decision_maker` — one accountable audience;
- `choice_at_stake` — one concrete choice, commitment, or deferral;
- `time_horizon` — the window in which the choice must be made;
- `secondary` — optional subordinate contexts, never co-equal goals.

Secondary contexts may receive subordinate consequences, but may not redefine the
primary decision or time horizon. Even when several are listed, only one primary
choice controls search scope and the top answer. Record unresolved omissions in
`scope.coverage_gaps`.

Use four corpus layers. Every `scope.corpus_layers` record has an `id`, `role`,
date boundary, purpose, a `status` of `searched`, `partial`, or `not_searched`,
and a factual `coverage_note`:

1. **Historical anchor** — earlier paradigms, mechanisms, benchmark definitions,
   surveys, or capability records needed to define the prior state.
2. **Counterevidence** — negative results, failures, critiques, robustness gaps,
   failed replication, competing mechanisms, or boundary conditions.
3. **Recent frontier** — work that may move a technical, capability, evaluation,
   deployment, or governance boundary.
4. **Emerging signal** — recent or isolated work that suggests a hypothesis but
   cannot yet establish a transition.

Do not use recent papers' novelty framing as the only evidence for the historical
state. If an anchor or counterevidence search is missing, mark the layer incomplete
and lower every affected conclusion.

Finding a negative or failure paper incidentally does not count as a dedicated
counterevidence search. A dedicated search must explicitly target failures,
negative results, critiques, replication, robustness, or boundary conditions.
If no such query was run, keep the counterevidence layer `partial` or
`not_searched` and state that absence in its `coverage_note`, the Decision Brief,
and Evidence Boundary. An empty counterevidence array then means “not found in
this covered corpus,” never “no counterevidence exists.”

Corpus coverage is a property of this search, not a field proposition. “No
deployment paper was included” means the report cannot assess deployment; it does
not establish that the field has no deployments. Keep such statements in
`coverage_gaps`, `evidence_coverage`, limitations, and the thesis ceiling.

Every `scope.queries` record must preserve the exact query and its `layer_id`,
sort, result limit, and date boundary. A hand-picked list of paper IDs may be used
for metadata retrieval after discovery, but it is not a discovery query and must
not be presented as one. Screening counts must reconcile with preserved raw and
normalized responses.

## 3. Evidence depth and permitted claims

| Source depth | Permitted facts | Cannot establish by itself |
|---|---|---|
| `metadata` | title, authors, dates, categories, identifiers, source URLs | topical fit beyond provisional screening; mechanism, result, quality, field state |
| `abstract` | author-stated problem, high-level mechanism, headline result, explicit abstract limitation | detailed architecture, full experimental conditions, complete limitations, historical transition, real-world capability |
| `full_text` | located mechanism, study design, comparison, metric, table/figure result, author limitation | publication status, independent adoption, replication, or influence without separate verification |
| `external` | exact fact verified by an official venue, DOI record, replication record, deployment source, or other appropriate academic source | any paper-content claim absent from that external source |

Use `摘要未说明`, `全文未核验`, or `外部来源未核验` rather than inventing a
value. The report-level evidence coverage is descriptive, never aspirational.

A current-year-only abstract scan can produce only signal hypotheses. It must not
claim an `established` proposition, `structural` or `reversal` transition,
`validated` or `mature` maturity, `real_world` or `longitudinal` external validity,
or `independently_reproduced` reproducibility. Without a searched or partial
historical anchor, set `field_thesis.epistemic_ceiling.trend` to `signals_only`
and keep transition statuses at `signal` or `insufficient_evidence`.

## 4. Atomic evidence and paper facts

One `evidence` record supports one indivisible fact. It identifies the paper,
source depth, evidence type, exact locator, bounded statement, and confidence.
Do not bundle a mechanism statement, two outcomes, and a limitation into one
record merely because they occur in the same abstract sentence.

Keep these evidence types distinct:

- `author_claim` — what authors assert or frame;
- `measured_result` — what their reported evaluation measured;
- `negative_result` — a reported failure, null result, or adverse outcome;
- `replication` — a direct reproduction attempt and its result;
- `derived_comparison` — a transparent comparison of compatible source facts;
- `analyst_inference` — an interpretation not directly asserted by a source;
- `external_validation` — a fact checked outside the arXiv paper.

Analyst inference must state how it follows, preserve alternatives, and never be
presented as source fact. A high-confidence transcription of an abstract number
does not make its cross-setting interpretation high confidence.

For each paper, preserve source metadata separately from these exact analytical
fields:

- `analysis.research_object`
- `analysis.mechanism`
- `analysis.evaluation`
- `analysis.key_findings`
- `analysis.author_stated_limitations`
- `analysis.analyst_inferred_limitations`

Use `model_links` to connect the paper to stage, technical option, capability, and
proposition IDs through `stage_ids`, `option_ids`, `capability_ids`, and
`proposition_ids`. Preserve `abstract_original` as source material. It belongs in
the appendix, not the main decision narrative. Assign every paper an
`independence_cluster_id` based on author/lab/work-family overlap before counting
independent evidence.

Every paper metric must point to a unique atomic evidence record. That record
contains exactly the metric, value, comparison context, and source locator needed
for that row. Two metrics may not share one `evidence_id`, even when the abstract
reports them in the same sentence; split the evidence first.

## 5. Shared narrative versus independent validation

Treat independence conservatively. Overlapping authors, the same laboratory,
successive versions, companion papers, shared datasets, shared benchmarks, or
restated assumptions do not automatically constitute independent validation.

Classify the relationship explicitly:

- **Shared narrative** — multiple papers repeat a problem framing, design
  intuition, or desired direction. This can support `multi_source_aligned`
  consistency while directness remains `author_claim` and reproducibility remains
  `unknown`.
- **Independent measurement** — non-overlapping groups directly test the same
  bounded proposition with interpretable, sufficiently compatible outcomes.
- **Independent reproduction** — a separate group reproduces the relevant method
  or result rather than merely citing, extending, or applying it.
- **Cross-setting validation** — compatible evidence survives a materially
  different dataset, task, user population, or deployment setting.

Four independent teams sharing an untested premise are four sources of narrative
convergence, not four validations of the premise.

## 6. Testable propositions and status rules

Every `propositions` item requires:

- `id`, `statement`, `proposition_type`, `status`, and `scope_conditions`;
- `supporting_evidence_ids`, `counter_evidence_ids`, and
  `alternative_explanations`;
- `evidence_ceiling`, `confidence`, `uncertainty`, and `what_would_change`;
- `decision_relevance`;
- `evidence_profile` with `directness`, `consistency`, `external_validity`,
  `reproducibility`, and `rationale`.

Allowed `proposition_type` values are:

- `mechanism`
- `capability`
- `evaluation`
- `deployment`
- `governance`

Use proposition statuses as follows:

### `established`

A bounded proposition has multiple materially independent, direct evidence paths;
important conditions are understood; counterevidence does not invalidate the
bounded statement; and evidence depth is sufficient for the claim. Abstract-only
or narrative-only support can never qualify. “Established” is about the scoped
proposition, not the entire field.

### `credible_emerging`

Direct or measured evidence makes the proposition plausible and decision-relevant,
but breadth, duration, replication, comparability, or external validity remains
insufficient. Multiple aligned abstracts may reach this status only for a narrow
signal hypothesis, not detailed mechanism, deployment readiness, or historical
change.

### `contested`

Materially credible evidence supports incompatible answers, mechanisms, or scope
conditions. State each position and whether the conflict concerns definition,
mechanism, evaluation, generality, deployment, or values. Do not average the
positions into false agreement.

### `unknown`

The proposition is decision-relevant and well formed, but no direct evidence in
the corpus answers it. Absence of evidence is not negative evidence. State the
minimum observation that would begin to answer it.

### `weakened`

Direct counterevidence, failed replication, or a demonstrated boundary condition
materially lowers belief in a previously plausible proposition. State whether the
claim is weakened generally or only outside a narrower scope.

### `insufficient_evidence`

Relevant sources exist, but their depth, independence, comparability, or coverage
cannot support a more informative status. Use this rather than manufacturing a
balanced conclusion. `unknown` means the question is essentially untested in the
corpus; `insufficient_evidence` means available evidence cannot resolve it.

The status is the belief. `confidence` expresses confidence that this status is
correct, not confidence that the proposition itself is true.

## 7. Field thesis and explicit belief updates

`field_thesis` is the shortest defensible answer to the research question. It is
not a free-form executive summary and may not introduce claims absent from
`propositions`.

- `direct_answer` answers the decision-framed research question directly.
- `field_stage` uses `pre_paradigm`, `emerging`, `consolidating`, `maturing`, or
  `deployed`.
- `stage_rationale` explains the stage using proposition status, frontier level,
  and the five maturity dimensions, not publication volume.
- `bottom_line_proposition_ids` identifies the beliefs that carry the answer.
- Every `belief_updates` item states `prior_belief`, `updated_belief`, and the
  proposition IDs that caused the update.
- `decision_relevance` states why the answer changes a real choice.
- `epistemic_ceiling` states the maximum authority, trend, and capability claim
  permitted by this corpus, plus its `rationale`.

Use these ceiling values:

- authority: `none`, `provisional`, `supported`, `established`;
- trend: `none`, `signals_only`, `emerging`, `structural`;
- capability: `conceptual`, `prototype`, `benchmark`,
  `controlled_user_study`, `longitudinal_deployment`.

The ceiling is not the headline the analyst wishes to reach. It is the strongest
headline the evidence permits. When `authority` is `none`, `direct_answer` must
say that no authoritative field view is currently supportable. This negative
answer is a valid and often essential top answer. Do not generate an authoritative
view section merely to complete the layout. Stronger authority remains a property
of propositions that clear the evidence gates.

Interpret field stages conservatively:

- `pre_paradigm` — the field lacks a stable problem formulation or dominant
  mechanism and most decision-relevant propositions remain unknown or contested;
- `emerging` — credible mechanisms, prototypes, or benchmark signals exist, but
  the frontier and evaluation regime remain unstable;
- `consolidating` — multiple approaches and benchmarks are becoming comparable,
  with several propositions independently supported under bounded conditions;
- `maturing` — scientific, engineering, and deployment evidence is broad enough
  to support repeatable decisions, while remaining gaps are explicit;
- `deployed` — longitudinal real-world capability and governance evidence support
  sustained operational use, not merely isolated pilots.

A field with benchmark progress but no longitudinal deployment cannot be
`deployed`. A current-year-only abstract scan normally supports `pre_paradigm` or
`emerging` at most, and only when the scope is explicitly the observed submission
landscape; without an anchor its trend ceiling is `signals_only`.

## 8. Evidence profile and ceiling

Use the exact evidence-profile enums.

`directness`:

- `indirect` — related framing or proxy evidence;
- `author_claim` — explicitly asserted but not directly demonstrated in the
  reviewed evidence;
- `measured` — directly measured under stated conditions;
- `replicated` — independently reproduced for the bounded proposition.

`consistency`:

- `single_source`
- `multi_source_aligned`
- `mixed`
- `conflicting`

`external_validity`:

- `unknown`
- `benchmark_only`
- `controlled`
- `real_world`
- `longitudinal`

`reproducibility`:

- `unknown`
- `materials_available`
- `independently_reproduced`

`materials_available` requires verified availability of sufficient artifacts; a
repository link alone does not prove reproduction. `real_world` requires actual
use conditions, while `longitudinal` requires meaningful evidence across time.

Set `evidence_ceiling` to `metadata`, `abstract`, `full_text`, `external`, or
`mixed`. It records the strongest kind of support relevant to the proposition,
not a quality score. `mixed` means multiple source depths contribute; it does not
erase the weakest link in the inference.

## 9. Capability frontier and readiness gaps

`capability_frontier` answers what the field can currently demonstrate, under
which conditions, and what it cannot yet generalize. Its `overall_statement`
must distinguish the strongest demonstrated frontier from desired future ability.
Establish this boundary before constructing a mechanism model so an analyst's
architecture cannot inflate the apparent capability.

For every capability include:

- `current_boundary`;
- `demonstration_context`;
- `strongest_evidence_ids`;
- `frontier_level`;
- `observed_failures`;
- `anticipated_risks`;
- `generalization_ceiling`;
- `unresolved_requirements`;
- `next_boundary`;
- `proposition_ids`.

Interpret `frontier_level` as:

- `conceptual` — proposed model or principle without an adequate implementation
  demonstration;
- `prototype` — implemented in a limited or illustrative system;
- `benchmark` — measured on a defined offline task or benchmark;
- `controlled_user_study` — demonstrated with users under controlled conditions;
- `longitudinal_deployment` — demonstrated in sustained real use over time.

Never upgrade a level because a paper calls its system deployed or practical.
Preserve sample, duration, task, model, baseline, and failure conditions.

Every `observed_failures` item has a `statement` and one or more unique
`evidence_ids`. It reports a failure directly observed in the cited source and
within its stated demonstration context. `anticipated_risks` are analyst
inferences: label them as such and never render them as observed frequency,
prevalence, or measured failure. An unmeasured concern, readiness gap, or corpus
coverage omission is not an observed failure.

An unmet capability is not a conceptual frontier item merely because it is
important. Put it in `capability_frontier.readiness_gaps`. Every gap records `id`,
`label_zh`, `label_en`, `current_state`, `blocking_evidence`,
`what_would_close`, and `proposition_ids`. Readiness gaps make “not yet
demonstrated” useful without pretending it has been demonstrated.

## 10. Mechanism model and reference architecture

`mechanism_model` is either a source synthesis or an analyst reference
architecture. It is not automatically a validated causal model.

- Set `model_type` to `source_synthesized` only when papers support the system
  topology; otherwise use `analyst_reference`.
- Set `epistemic_status` to `established`, `credible_emerging`, `hypothesis`, or
  `design_completion` according to its weakest material relation.
- `system_statement` defines the system boundary and target outcome.
- Each stage records `id`, bilingual labels, purpose, inputs, outputs,
  `current_methods`, `failure_modes`, and `proposition_ids`.
- Every edge records `from_stage_id`, `to_stage_id`, `relation`, proposition IDs,
  and `support_type`: `source_supported`, `cross_paper_inference`, or
  `analyst_design_completion`.
- `critical_path_stage_ids` lists necessary stages; `critical_path_note` explains
  why the path is complete and which parts are inferred.
- Each structured `bottlenecks` item binds `stage_id`, `statement`,
  `proposition_ids`, and confidence.
- `model_limitations` records omissions, uncertainty, and design completion.

The HTML must label `analyst_reference`, `hypothesis`, and every
`analyst_design_completion` relation at the same visual level as the model title.
Do not allow a useful reference architecture to inherit authority from papers
that support only individual modules. A plausible pipeline is not proof that its
edges cause the target outcome.

## 11. Technical options and comparability

Each `technical_options` item represents a technical choice, module, baseline, or
hybrid, not a paper bucket. It must contain:

- `technical_bet`, `relationship`, `comparison_status`, `comparison_note`, and
  linked `mechanism_stage_ids`;
- `core_hypothesis`;
- `representative_paper_ids`;
- `advantages` and `costs`;
- `failure_modes`;
- `valid_when` and `invalid_when`;
- `supporting_proposition_ids`;
- concrete `falsifiers`.

Use `relationship` accurately: `alternative` for substitutable choices addressing
the same function; `complementary` for modules that can coexist; `baseline` for a
reference strategy; and `hybrid` for an explicit combination. Memory, gating,
feedback, and execution at different stages are normally complementary, not
competing routes.

Use `comparison_status` as `comparable`, `partially_comparable`, or
`not_comparable`. Comparable options must share a decision unit, target stage,
objective, evaluation context, and interpretable cost/quality measures. Only
`comparable` alternatives may be ranked or given a winner. Partially comparable
or non-comparable options may be described side by side, with `comparison_note`
stating the mismatch, but cannot support route selection by score.

When the primary decision asks which architecture or operating mode to fund,
include the material reference baselines needed to frame that choice: static
rules or user settings, an end-to-end LLM policy, and human-confirmation or
mixed-initiative control, as applicable. A baseline without direct evaluation in
the corpus remains `relationship: baseline` and
`comparison_status: not_comparable`. Its `comparison_note` must say what was not
directly evaluated; do not invent a head-to-head result, ranking, or paper support.

## 12. Transition theses

A transition thesis explains a directional move from one field state to another.
Every `transition_theses` item requires:

- `from_state` and `to_state`;
- the `old_constraint` that creates pressure to move;
- drivers and `time_from` / `time_to`;
- `supporting_proposition_ids` and `counter_proposition_ids`;
- plural `alternative_explanations`;
- falsifiers;
- linked `leading_indicator_ids`;
- confidence.

Use `status` as follows:

- `signal` — a recent cluster or isolated result suggests a possible direction,
  but historical sequence or independent validation is incomplete;
- `emerging` — a time sequence, anchor, and multiple independent evidence paths
  indicate movement, but persistence or cross-setting breadth remains uncertain;
- `structural` — sustained evidence across time, groups, and settings shows that
  the field's problem, mechanism, evaluation, infrastructure, deployment, or
  governance regime has materially changed;
- `reversal` — credible longitudinal evidence shows movement away from a prior
  direction or a return to a formerly displaced approach;
- `insufficient_evidence` — a from/to claim is relevant but the corpus cannot
  establish directional movement.

Paper-count growth, new terminology, a leaderboard burst, or multiple papers
sharing the same narrative can be a signal but not a structural transition.

## 13. Five-dimensional maturity

Create one `maturity_assessment` record for every dimension. Each requires
`dimension`, `level`, a bounded `statement`, linked `proposition_ids`, `blockers`,
and observable `upgrade_conditions`.

Dimensions:

- `scientific_mechanism` — causal or functional understanding and independent
  validation of why the approach works;
- `benchmark` — shared task definitions, metric validity, comparability, and
  robustness of evaluation;
- `engineering` — implementation stability, latency, cost, interfaces,
  observability, and reproducibility;
- `deployment` — controlled use, real users, longitudinal net value, and failure
  recovery;
- `governance` — consent, data boundaries, audit, correction, override, rollback,
  accountability, and policy readiness.

Levels:

- `absent` — no credible evidence for the dimension;
- `early` — isolated concepts, prototypes, or incomplete evidence;
- `emerging` — multiple relevant efforts and partial validation, with substantial
  unresolved blockers;
- `validated` — strong, direct evidence satisfies the dimension under bounded
  conditions;
- `mature` — sustained, independently validated evidence across relevant settings
  with operational norms and failure handling.

Do not average the dimensions. A benchmark-validated field may remain early in
deployment and absent in governance. Maturity reports readiness, not excitement.

## 14. Decision consequences

Every `decision_consequences` item must be a choice, not a generic implication.
Use exactly:

- `decision_type`: `research_agenda`, `architecture`, `product`, or
  `due_diligence`;
- `audience` — who owns the decision;
- `decision` — the commitment, selection, deferral, or boundary at stake;
- `action` — what to do now;
- `because_proposition_ids` — the beliefs that justify the action;
- `conditions` — when the recommendation applies;
- `risks` — material downside and uncertainty;
- `reversibility`: `reversible`, `partially_reversible`, or `hard_to_reverse`;
- `confidence`.

`technology_strategy` is valid in `scope.decision_context` but not as a
`decision_type`. Resolve it into the concrete `research_agenda`, `architecture`,
`product`, or `due_diligence` choice that the strategy must make.

The first and strongest consequence answers `decision_context.primary` for its
named decision maker, choice, and horizon. Secondary-context consequences are
explicitly subordinate; they may not turn the report back into a five-audience
list of generic cautions.

That first consequence and the Decision Brief must explicitly answer four things:

1. whether to invest now, defer, or decline;
2. whether the authorized step is validation or productization;
3. the ordered priority of work or commitments;
4. what must not be done within the stated horizon.

If evidence supports only signals, authorize at most bounded, reversible
validation. Investment in validation infrastructure is not authorization to
productize or deploy a high-impact autonomous system.

The action must not outrun the least mature dimension it depends on. Prefer a
reversible experiment when the key proposition is `credible_emerging`,
`contested`, `unknown`, `weakened`, or `insufficient_evidence`. State what not to
assume when the evidence ceiling is low.

## 15. Leading indicators

A leading indicator is an observable belief-update contract. Every
`leading_indicators` item requires:

- `label`;
- `observation` — the event or measure;
- `current_baseline`;
- `threshold_or_trigger`;
- `threshold_basis`: `source_derived` or `analyst_policy`;
- `threshold_rationale`;
- `data_source`;
- `observation_window`;
- `affects_proposition_ids`;
- `interpretation_if_met`;
- `interpretation_if_missed`;
- `decision_trigger`.

Good indicators are measurable before the final outcome, have a specified source
and horizon, and can change a proposition status, maturity level, transition
thesis, or decision. “More papers,” “better performance,” and “industry interest”
are invalid until the unit, denominator, threshold, and interpretation are stated.

Use `source_derived` only when the threshold itself follows from cited evidence
or an established external standard. Mark internal gates such as “two independent
teams,” “three adopters,” or “four weeks” as `analyst_policy` and explain in
`threshold_rationale` why that policy is proportionate to the decision's risk and
reversibility. A useful policy threshold is not a scientific finding.

Link every transition thesis to the indicators that could confirm, weaken, or
falsify it. Link every consequential unresolved proposition to at least one
indicator where an observable signal is possible.

## 16. Confidence, uncertainty, and change conditions

- `high` — the bounded status itself is supported by direct, sufficiently
  comparable, materially independent evidence and major scope conditions are
  understood;
- `medium` — relevant support exists, but depth, settings, independence,
  external validity, or alternatives remain material;
- `low` — sparse, indirect, very recent, conflicting, or inference-heavy evidence.

Always populate `uncertainty` and `what_would_change`. Confidence without an
update condition encourages false finality. Do not use unsupported causal,
general, production-ready, authoritative, or state-of-the-art language.

## 17. External verification

Prefer, when applicable:

1. official venue, proceedings, journal, or publisher record;
2. DOI landing page or Crossref metadata;
3. official artifact, benchmark, dataset, replication, or deployment record;
4. OpenAlex or Semantic Scholar for discovery and dated bibliometric context.

Record provider, URL, checked date, exact fact, and ambiguity. Citation counts
require a provider and `as_of` date and remain context, never authority by
themselves. Search-result snippets are not evidence.

## 18. Outcome-first HTML editorial rules

The main narrative must answer decisions before showing its audit trail:

1. Decision Brief, including the primary decision and visible epistemic ceiling
2. Current Field Beliefs
3. Capability Frontier
4. Mechanism Model & Technical Options
5. Transition Theses
6. Five-Dimensional Maturity
7. Decision Consequences
8. Leading Indicators
9. Evidence Boundary
10. Evidence appendix: paper dossiers, ledger, exact queries, screening,
    exclusions, verification, and source URLs

Do not lead with corpus counts, paper summaries, or evidence chips. Keep scope,
uncertainty, and falsifiers visible in the main flow, while detailed evidence and
abstracts belong in the appendix.

When no authoritative view or trend is supportable, say so in the Decision Brief
instead of rendering an empty authority/trend section. Show
`epistemic_ceiling.authority`, `.trend`, and `.capability` at the same visual level
as `direct_answer`. Label analyst reference architecture and design-completion
edges prominently. Render complementary/non-comparable options without rank.

Use short stable evidence ordinals such as `[E01]` in the main view. Keep raw
evidence IDs, long model IDs, locators, and full evidence statements in the
appendix; ordinals link there. Audit identifiers must not dominate the reader's
understanding of the field.

In Capability Frontier, render source-bound `observed_failures` with evidence
ordinals separately from `anticipated_risks`, which must carry an analyst-inference
label. In Decision Brief, keep a missing dedicated counterevidence search visible
and answer invest-now, validation-versus-productization, ordered priority, and
prohibition directly.

Use Chinese for reasoning and English for exact titles and precise terminology.
Preserve `title`; treat `title_zh` as editorial analysis. Use Chinese punctuation
in Chinese sentences and English punctuation inside fully English titles. Do not
insert spaces mechanically around every English token. Keep IDs, metrics, units,
and citations unbroken.

Visualizations must reveal a real relationship: capability boundaries, supported
versus analyst-added mechanism edges, option relationships, maturity, or indicator
triggers. Never create fake precision, maturity averages, decorative charts, or
visual prominence unrelated to evidence strength.

## 19. Analyst acceptance checklist

Before rendering, confirm:

- one primary decision maker, choice, and horizon governs the report;
- the four corpus layers and exact discovery queries are auditable;
- absence of a dedicated counterevidence query remains visible and limits claims;
- every decisive mechanism or experimental fact has appropriate source depth;
- each metric has a unique atomic evidence record;
- every proposition has counterevidence, alternatives, uncertainty, and an
  update condition, even when the relevant arrays are honestly empty;
- coverage conclusions remain outside scientific propositions;
- shared narrative is not described as independent validation;
- the thesis explicitly says when authority is `none` and trend is `signals_only`;
- capability levels match demonstrations and unmet abilities are readiness gaps;
- observed failures cite one or more unique evidence records; anticipated risks
  remain visibly analyst inference;
- validation rejects legacy `common_failures`, unreferenced observed failures,
  and analyst-derived or cross-paper failures presented as source observations;
- analyst reference architecture and inferred/design-completion edges are visible;
- technical options expose relationships and comparability; only comparable
  alternatives are ranked;
- transition theses have real anchors, temporal sequence, alternatives, and
  indicators;
- all five maturity dimensions are separately assessed;
- decisions cite propositions and state risks and reversibility;
- the top decision answers invest now, validation versus productization, ordered
  priorities, and what not to do;
- indicators contain baseline, threshold, basis/rationale, source, window,
  two-sided interpretation, and decision trigger; internal gates are
  `analyst_policy`;
- insufficient evidence produces an explicit limited answer rather than extra
  prose;
- the final report includes every analyzed arXiv URL.
