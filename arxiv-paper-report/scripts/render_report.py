#!/usr/bin/env python3
"""Render validated arxiv-paper-report v3 JSON as deterministic standalone HTML."""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path
from typing import Any, Iterable

from validate_report_data import load_report, validate_report


SKILL_DIR = Path(__file__).resolve().parent.parent
CSS_PATH = SKILL_DIR / "assets" / "report.css"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    return parser.parse_args()


def h(value: Any) -> str:
    return html.escape(str(value), quote=True)


def as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def first_value(mapping: dict[str, Any], *keys: str, default: Any = "") -> Any:
    for key in keys:
        value = mapping.get(key)
        if value is not None and value != "":
            return value
    return default


def text_value(mapping: dict[str, Any], *keys: str, default: str = "") -> str:
    value = first_value(mapping, *keys, default=default)
    return str(value) if isinstance(value, (str, int, float)) else default


def safe_token(value: Any) -> str:
    token = re.sub(r"[^a-z0-9-]+", "-", str(value).strip().lower()).strip("-")
    return token or "unknown"


def unique(values: Iterable[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for value in values:
        if value and value not in seen:
            result.append(value)
            seen.add(value)
    return result


def paper_anchor(value: str) -> str:
    return "paper-" + safe_token(value)


def evidence_anchor(value: str) -> str:
    return "evidence-" + safe_token(value)


def proposition_anchor(value: str) -> str:
    return "proposition-" + safe_token(value)


def enum_label(value: Any) -> str:
    labels = {
        "mechanism": "机制 · Mechanism",
        "capability": "能力 · Capability",
        "evaluation": "评测 · Evaluation",
        "deployment": "部署 · Deployment",
        "governance": "治理 · Governance",
        "pre_paradigm": "前范式期 · Pre-paradigm",
        "consolidating": "收敛期 · Consolidating",
        "maturing": "成熟化 · Maturing",
        "deployed": "部署期 · Deployed",
        "established": "已建立 · Established",
        "credible_emerging": "可信新兴 · Credible emerging",
        "contested": "有争议 · Contested",
        "unknown": "未知 · Unknown",
        "weakened": "证据减弱 · Weakened",
        "insufficient_evidence": "证据不足 · Insufficient evidence",
        "indirect": "间接 · Indirect",
        "author_claim": "作者主张 · Author claim",
        "measured": "测量结果 · Measured",
        "replicated": "已复现 · Replicated",
        "single_source": "单一来源 · Single source",
        "multi_source_aligned": "多源一致 · Multi-source aligned",
        "mixed": "混合 · Mixed",
        "conflicting": "冲突 · Conflicting",
        "benchmark_only": "仅基准 · Benchmark only",
        "controlled": "受控研究 · Controlled",
        "real_world": "真实环境 · Real world",
        "longitudinal": "纵向部署 · Longitudinal",
        "materials_available": "材料可用 · Materials available",
        "independently_reproduced": "独立复现 · Independently reproduced",
        "conceptual": "概念 · Conceptual",
        "prototype": "原型 · Prototype",
        "benchmark": "基准 · Benchmark",
        "controlled_user_study": "受控用户研究 · Controlled user study",
        "longitudinal_deployment": "长期部署 · Longitudinal deployment",
        "none": "无 · None",
        "provisional": "暂定 · Provisional",
        "supported": "有支持 · Supported",
        "signals_only": "仅提交信号 · Signals only",
        "signal": "信号假设 · Signal hypothesis",
        "emerging": "形成中 · Emerging",
        "structural": "结构性 · Structural",
        "reversal": "逆转 · Reversal",
        "scientific_mechanism": "科学机制 · Scientific mechanism",
        "engineering": "工程 · Engineering",
        "absent": "缺失 · Absent",
        "early": "早期 · Early",
        "validated": "已验证 · Validated",
        "mature": "成熟 · Mature",
        "research_agenda": "研究议程 · Research agenda",
        "architecture": "架构 · Architecture",
        "product": "产品 · Product",
        "due_diligence": "尽调 · Due diligence",
        "technology_strategy": "技术战略 · Technology strategy",
        "reversible": "可逆 · Reversible",
        "partially_reversible": "部分可逆 · Partially reversible",
        "hard_to_reverse": "难以逆转 · Hard to reverse",
        "source_synthesized": "来源综合 · Source-synthesized",
        "analyst_reference": "分析者参考模型 · Analyst reference",
        "hypothesis": "假设 · Hypothesis",
        "design_completion": "设计补全 · Design completion",
        "source_supported": "来源支持 · Source-supported",
        "cross_paper_inference": "跨论文推断 · Cross-paper inference",
        "analyst_design_completion": "分析者设计补全 · Analyst design completion",
        "alternative": "替代关系 · Alternative",
        "complementary": "互补关系 · Complementary",
        "baseline": "基线 · Baseline",
        "hybrid": "混合关系 · Hybrid",
        "comparable": "可比较 · Comparable",
        "partially_comparable": "部分可比较 · Partially comparable",
        "not_comparable": "不可直接比较 · Not comparable",
        "source_derived": "来源导出 · Source-derived",
        "analyst_policy": "分析者决策规则 · Analyst policy",
        "metadata": "元数据 · Metadata",
        "abstract": "摘要 · Abstract",
        "full_text": "全文 · Full text",
        "external": "外部验证 · External",
        "measured_result": "测量结果 · Measured result",
        "negative_result": "负向结果 · Negative result",
        "replication": "复现 · Replication",
        "external_validation": "外部验证 · External validation",
        "analyst_inference": "分析推断 · Analyst inference",
        "derived_comparison": "推导比较 · Derived comparison",
        "metadata_only": "仅元数据 · Metadata only",
        "abstract_screened": "摘要筛选 · Abstract screened",
        "mixed_depth": "混合深度 · Mixed depth",
        "full_text_reviewed": "全文审阅 · Full text reviewed",
        "anchor": "历史锚点 · Anchor",
        "frontier": "前沿 · Frontier",
        "counterpoint": "反向证据 · Counterpoint",
        "counterevidence": "反向证据 · Counterevidence",
        "early_signal": "早期信号 · Early signal",
        "searched": "已检索 · Searched",
        "verified": "已验证 · Verified",
        "partial": "部分验证 · Partial",
        "unverified": "未验证 · Unverified",
        "covered": "已覆盖 · Covered",
        "not_searched": "未检索 · Not searched",
        "gap": "缺口 · Gap",
    }
    value_text = str(value)
    return labels.get(value_text, value_text.replace("_", " ").title())


def confidence_label(value: Any) -> str:
    return {
        "high": "高置信度 · High",
        "medium": "中等置信度 · Medium",
        "low": "低置信度 · Low",
    }.get(str(value), enum_label(value))


def string_list(value: Any) -> list[str]:
    return [str(item) for item in as_list(value) if isinstance(item, (str, int, float))]


def empty_state(zh: str, en: str) -> str:
    return f'<p class="empty"><span>{h(zh)}</span><span lang="en">{h(en)}</span></p>'


def plain_list(value: Any, zh: str = "未报告", en: str = "Not reported") -> str:
    rows = string_list(value)
    if not rows:
        return empty_state(zh, en)
    return '<ul class="plain-list">' + "".join(f'<li>{h(row)}</li>' for row in rows) + '</ul>'


def section_heading(number: str, zh: str, en: str) -> str:
    return (
        '<div class="section-heading">'
        f'<span>{h(number)}</span><div><h2>{h(zh)}</h2><p lang="en">{h(en)}</p></div></div>'
    )


def link_chips(
    ids: Any,
    index: dict[str, dict[str, Any]],
    *,
    anchor_fn: Any,
    css_class: str,
    aria_label: str,
    prefix: str = "",
    numbered: bool = False,
    empty: tuple[str, str] | None = None,
) -> str:
    links: list[str] = []
    for item_id in unique(str(value) for value in as_list(ids) if isinstance(value, str)):
        item = index.get(item_id)
        if item is None:
            continue
        title = text_value(item, "statement", "label_zh", "label", "title", default=item_id)
        if numbered:
            ordinal = list(index).index(item_id) + 1
            visible_label = f"{prefix}{ordinal}"
        else:
            visible_label = prefix + item_id
        links.append(
            f'<a class="{h(css_class)}" href="#{h(anchor_fn(item_id))}" title="{h(title)}">'
            f'{h(visible_label)}</a>'
        )
    if not links:
        if empty is None:
            return ""
        return f'<span class="semantic-empty">{h(empty[0])} / {h(empty[1])}</span>'
    return f'<span class="ref-set" aria-label="{h(aria_label)}">' + "".join(links) + '</span>'


def evidence_refs(
    ids: Any,
    evidence_index: dict[str, dict[str, Any]],
    *,
    empty: tuple[str, str] | None = None,
) -> str:
    return link_chips(
        ids,
        evidence_index,
        anchor_fn=evidence_anchor,
        css_class="evidence-ref",
        aria_label="证据引用 / Evidence references",
        prefix="E",
        numbered=True,
        empty=empty,
    )


def proposition_refs(
    ids: Any,
    proposition_index: dict[str, dict[str, Any]],
    *,
    empty: tuple[str, str] | None = None,
) -> str:
    return link_chips(
        ids,
        proposition_index,
        anchor_fn=proposition_anchor,
        css_class="proposition-ref",
        aria_label="命题引用 / Proposition references",
        prefix="P",
        numbered=True,
        empty=empty,
    )


def paper_refs(ids: Any, paper_index: dict[str, dict[str, Any]]) -> str:
    return link_chips(
        ids,
        paper_index,
        anchor_fn=paper_anchor,
        css_class="paper-ref",
        aria_label="论文引用 / Paper references",
    )


def entity_refs(
    ids: Any,
    index: dict[str, dict[str, Any]],
    prefix: str,
    label: str,
) -> str:
    return link_chips(
        ids,
        index,
        anchor_fn=lambda value: f"{prefix}-{safe_token(value)}",
        css_class="entity-ref",
        aria_label=label,
    )


def render_header(report: dict[str, Any]) -> str:
    scope = as_dict(report.get("scope"))
    context = as_dict(scope.get("decision_context"))
    return f"""
<header class="report-header">
  <div class="eyebrow">ARXIV DECISION INTELLIGENCE · {h(report.get('as_of', ''))}</div>
  <h1>{h(report.get('title_zh', ''))}</h1>
  <p class="title-en" lang="en">{h(report.get('title_en', ''))}</p>
  <p class="research-question">{h(scope.get('research_question', ''))}</p>
  <dl class="decision-context-header">
    <div><dt>主要决策人 <span lang="en">Decision maker</span></dt><dd>{h(context.get('decision_maker', ''))}</dd></div>
    <div><dt>待决选择 <span lang="en">Choice at stake</span></dt><dd>{h(context.get('choice_at_stake', ''))}</dd></div>
    <div><dt>时间窗口 <span lang="en">Time horizon</span></dt><dd>{h(context.get('time_horizon', ''))}</dd></div>
  </dl>
</header>"""


def render_toc() -> str:
    rows = (
        ("direct-answer", "直接回答", "Direct Answer"),
        ("knowledge-state", "知识状态", "Knowledge State"),
        ("capability-frontier", "能力边界", "Capability Frontier"),
        ("mechanism-model", "机制模型", "Mechanism Model"),
        ("technical-options", "技术选项", "Technical Options"),
        ("submission-signals", "提交信号", "Submission Signals"),
        ("maturity-assessment", "五维成熟度", "Maturity"),
        ("decision-consequences", "决策后果", "Decisions"),
        ("monitoring", "监测触发", "Monitoring"),
        ("evidence-base", "证据基础", "Evidence Base"),
    )
    links = "".join(
        f'<li><a href="#{section_id}"><span>{h(zh)}</span><small lang="en">{h(en)}</small></a></li>'
        for section_id, zh, en in rows
    )
    return f'<nav class="toc" aria-label="报告目录 / Report contents"><ol>{links}</ol></nav>'


def render_direct_answer(
    report: dict[str, Any], proposition_index: dict[str, dict[str, Any]]
) -> str:
    thesis = as_dict(report.get("field_thesis"))
    updates = []
    for update in as_list(thesis.get("belief_updates")):
        item = as_dict(update)
        updates.append(
            '<article class="belief-update reasoning-bound">'
            f'<div><span>此前判断 / Prior</span><p>{h(item.get("prior_belief", ""))}</p></div>'
            f'<div><span>更新后 / Updated</span><p>{h(item.get("updated_belief", ""))}</p></div>'
            f'<footer>{proposition_refs(item.get("proposition_ids"), proposition_index)}</footer></article>'
        )
    updates_html = "".join(updates) or empty_state("没有记录信念更新", "No belief update recorded")
    ceiling = as_dict(thesis.get("epistemic_ceiling"))
    return f"""
<section class="section" id="direct-answer">
  {section_heading('01', '直接回答与证据上限', 'Direct Answer & Epistemic Ceiling')}
  <article class="thesis-block reasoning-bound">
    <span class="thesis-stage">{h(enum_label(thesis.get('field_stage', '')))}</span>
    <p class="direct-answer">{h(thesis.get('direct_answer', ''))}</p>
    <p class="stage-rationale">{h(thesis.get('stage_rationale', ''))}</p>
    <dl class="epistemic-ceilings">
      <div class="epistemic-ceiling-item"><dt>权威结论上限 <span lang="en">Authority ceiling</span></dt><dd>{h(enum_label(ceiling.get('authority', '')))}</dd></div>
      <div class="epistemic-ceiling-item"><dt>趋势判断上限 <span lang="en">Trend ceiling</span></dt><dd>{h(enum_label(ceiling.get('trend', '')))}</dd></div>
      <div class="epistemic-ceiling-item"><dt>能力证据上限 <span lang="en">Capability ceiling</span></dt><dd>{h(enum_label(ceiling.get('capability', '')))}</dd></div>
    </dl>
    <p class="ceiling-rationale">{h(ceiling.get('rationale', ''))}</p>
    <div class="thesis-relevance"><h3>决策意义 <span lang="en">Decision relevance</span></h3><p>{h(thesis.get('decision_relevance', ''))}</p></div>
    <footer>{proposition_refs(thesis.get('bottom_line_proposition_ids'), proposition_index)}</footer>
  </article>
  <div class="subsection"><h3 class="subsection-title">本次调研改变了什么判断 <span lang="en">Belief Updates</span></h3><div class="belief-updates">{updates_html}</div></div>
</section>"""


def render_knowledge_state(
    report: dict[str, Any], evidence_index: dict[str, dict[str, Any]]
) -> str:
    rows = []
    for proposition_number, proposition in enumerate(as_list(report.get("propositions")), start=1):
        item = as_dict(proposition)
        proposition_id = text_value(item, "id", default="proposition")
        profile = as_dict(item.get("evidence_profile"))
        scope = "；".join(string_list(item.get("scope_conditions"))) or "—"
        alternatives = "；".join(string_list(item.get("alternative_explanations"))) or "—"
        changes = "；".join(string_list(item.get("what_would_change"))) or "—"
        support_ids = as_list(item.get("supporting_evidence_ids"))
        counter_ids = as_list(item.get("counter_evidence_ids"))
        support = evidence_refs(
            support_ids,
            evidence_index,
            empty=("没有直接支持证据", "No direct supporting evidence"),
        )
        counter = evidence_refs(
            counter_ids,
            evidence_index,
            empty=("本次语料未纳入反向证据", "No counter-evidence in this corpus"),
        )
        rows.append(f"""
<tr class="proposition-row {'reasoning-bound' if support_ids or counter_ids else 'evidence-absence-declared'}" id="{proposition_anchor(proposition_id)}">
  <th scope="row"><span class="proposition-id">P{proposition_number}</span><p>{h(item.get('statement', ''))}</p><small>{h(enum_label(item.get('proposition_type', '')))}</small><p class="decision-relevance">{h(item.get('decision_relevance', ''))}</p></th>
  <td><span class="status status-{safe_token(item.get('status', ''))}">{h(enum_label(item.get('status', '')))}</span><span class="confidence">{h(confidence_label(item.get('confidence', '')))}</span><small>{h(enum_label(item.get('evidence_ceiling', '')))}</small></td>
  <td><div class="evidence-pair"><div><b>支持证据 · Support</b>{support}</div><div><b>反向证据 · Counter</b>{counter}</div></div><dl class="profile-list"><div><dt>Directness</dt><dd>{h(enum_label(profile.get('directness', '')))}</dd></div><div><dt>Consistency</dt><dd>{h(enum_label(profile.get('consistency', '')))}</dd></div><div><dt>Validity</dt><dd>{h(enum_label(profile.get('external_validity', '')))}</dd></div><div><dt>Reproducibility</dt><dd>{h(enum_label(profile.get('reproducibility', '')))}</dd></div></dl><p class="profile-rationale">{h(profile.get('rationale', ''))}</p></td>
  <td><dl class="qualification-list"><div><dt>Scope</dt><dd>{h(scope)}</dd></div><div><dt>Uncertainty</dt><dd>{h(item.get('uncertainty', ''))}</dd></div><div><dt>Alternatives</dt><dd>{h(alternatives)}</dd></div><div><dt>Would change</dt><dd>{h(changes)}</dd></div></dl></td>
</tr>""")
    body = "".join(rows) or '<tr><td colspan="4">' + empty_state("尚无可审查命题", "No auditable proposition") + '</td></tr>'
    return f"""
<section class="section" id="knowledge-state">
  {section_heading('02', '当前知识状态', 'Current Knowledge State')}
  <p class="section-note">状态表示证据支持程度，而不是论文热度；共同假设、直接测量、冲突结果与未知项被明确区分。</p>
  <div class="table-wrap"><table class="proposition-matrix"><thead><tr><th>Proposition & decision relevance</th><th>State</th><th>Evidence & profile</th><th>Boundary & falsification</th></tr></thead><tbody>{body}</tbody></table></div>
</section>"""


def render_mechanism_model(
    report: dict[str, Any], proposition_index: dict[str, dict[str, Any]]
) -> str:
    model = as_dict(report.get("mechanism_model"))
    critical = set(string_list(model.get("critical_path_stage_ids")))
    bottleneck_items = [as_dict(item) for item in as_list(model.get("bottlenecks"))]
    bottleneck_stages = {
        text_value(item, "stage_id", default="") for item in bottleneck_items
    }
    stages = []
    stage_index: dict[str, dict[str, Any]] = {}
    for number, stage in enumerate(as_list(model.get("stages")), start=1):
        item = as_dict(stage)
        stage_id = text_value(item, "id", default=f"stage-{number}")
        stage_index[stage_id] = item
        proposition_ids = as_list(item.get("proposition_ids"))
        flags = []
        if stage_id in critical:
            flags.append('<span class="mechanism-flag">关键路径 · Critical</span>')
        if stage_id in bottleneck_stages:
            flags.append('<span class="mechanism-flag bottleneck">证据瓶颈 · Evidence bottleneck</span>')
        stages.append(f"""
<article class="mechanism-stage {'reasoning-bound' if proposition_ids else 'evidence-absence-declared'} {'is-critical' if stage_id in critical else ''} {'is-bottleneck' if stage_id in bottleneck_stages else ''}" id="stage-{safe_token(stage_id)}">
  <header><span class="stage-number">{number:02d}</span><div><h3>{h(item.get('label_zh', ''))}</h3><p lang="en">{h(item.get('label_en', ''))}</p></div></header>
  <div class="mechanism-flags">{''.join(flags)}</div>
  <p class="stage-purpose">{h(item.get('purpose', ''))}</p>
  <dl class="stage-io"><div><dt>Inputs</dt><dd>{h('；'.join(string_list(item.get('inputs'))) or '—')}</dd></div><div><dt>Outputs</dt><dd>{h('；'.join(string_list(item.get('outputs'))) or '—')}</dd></div></dl>
  <div class="stage-detail"><div><h4>当前方法 <span lang="en">Current methods</span></h4>{plain_list(item.get('current_methods'))}</div><div><h4>失败模式 <span lang="en">Failure modes</span></h4>{plain_list(item.get('failure_modes'))}</div></div>
  <footer>{proposition_refs(item.get('proposition_ids'), proposition_index)}</footer>
</article>""")
    stage_html = "".join(stages) or empty_state("尚未建立机制阶段", "Mechanism stages not modeled")
    edges = []
    for edge in as_list(model.get("edges")):
        item = as_dict(edge)
        source = text_value(item, "from_stage_id", default="")
        target = text_value(item, "to_stage_id", default="")
        source_label = text_value(stage_index.get(source, {}), "label_zh", default=source)
        target_label = text_value(stage_index.get(target, {}), "label_zh", default=target)
        proposition_ids = as_list(item.get("proposition_ids"))
        edges.append(
            f'<li class="mechanism-edge {"reasoning-bound" if proposition_ids else "evidence-absence-declared"}">'
            f'<a href="#stage-{safe_token(source)}">{h(source_label)}</a><span aria-hidden="true">→</span>'
            f'<a href="#stage-{safe_token(target)}">{h(target_label)}</a><p>{h(item.get("relation", ""))}</p>'
            f'<span class="edge-support">{h(enum_label(item.get("support_type", "")))}</span>'
            f'{proposition_refs(item.get("proposition_ids"), proposition_index)}</li>'
        )
    edge_html = '<ol class="edge-list">' + "".join(edges) + '</ol>' if edges else empty_state("未定义阶段依赖", "Stage dependencies not defined")
    bottlenecks = []
    for number, bottleneck in enumerate(bottleneck_items, start=1):
        stage_id = text_value(bottleneck, "stage_id", default="")
        stage_label = text_value(stage_index.get(stage_id, {}), "label_zh", default=stage_id)
        bottlenecks.append(
            f'<article class="mechanism-bottleneck reasoning-bound" id="bottleneck-{number}-{safe_token(stage_id)}">'
            f'<header><a href="#stage-{safe_token(stage_id)}">{h(stage_label)}</a><span>{h(confidence_label(bottleneck.get("confidence", "")))}</span></header>'
            f'<p>{h(bottleneck.get("statement", ""))}</p><footer>{proposition_refs(bottleneck.get("proposition_ids"), proposition_index)}</footer></article>'
        )
    bottleneck_html = "".join(bottlenecks) or empty_state(
        "本次模型未识别可证据化瓶颈", "No evidence-bound bottleneck identified"
    )
    return f"""
<section class="section" id="mechanism-model">
  {section_heading('04', '来源与分析者机制模型', 'Source & Analyst Mechanism Model')}
  <div class="model-provenance"><div><span>{h(enum_label(model.get('model_type', '')))}</span><span>{h(enum_label(model.get('epistemic_status', '')))}</span></div><p>{h(model.get('critical_path_note', ''))}</p></div>
  <p class="mechanism-statement">{h(model.get('system_statement', ''))}</p>
  <figure class="mechanism-figure"><figcaption>这是解释或决策模型，不自动等同于来源共同验证的因果机制；每条边明确区分来源支持、跨论文推断与分析者设计补全。</figcaption><div class="mechanism-pipeline stage-count-{len(stages)}">{stage_html}</div></figure>
  <div class="subsection"><h3 class="subsection-title">阶段依赖与反馈 <span lang="en">Edges & Feedback</span></h3>{edge_html}</div>
  <div class="subsection"><h3 class="subsection-title">当前瓶颈判断 <span lang="en">Evidence-bound Bottlenecks</span></h3><div class="mechanism-bottlenecks">{bottleneck_html}</div></div>
  <div class="model-limitations"><h3>模型边界 <span lang="en">Model limitations</span></h3>{plain_list(model.get('model_limitations'))}</div>
</section>"""


def render_technical_options(
    report: dict[str, Any],
    proposition_index: dict[str, dict[str, Any]],
    paper_index: dict[str, dict[str, Any]],
) -> str:
    stage_index = {
        text_value(item, "id", default=""): item
        for item in as_list(as_dict(report.get("mechanism_model")).get("stages"))
        if isinstance(item, dict)
    }
    rows = []
    options = [as_dict(option) for option in as_list(report.get("technical_options"))]
    for option in options:
        item = as_dict(option)
        option_id = text_value(item, "id", default="option")
        rows.append(f"""
<article class="technical-option reasoning-bound" id="option-{safe_token(option_id)}">
  <header><div><h3>{h(item.get('label_zh', ''))} <span lang="en">{h(item.get('label_en', ''))}</span></h3><div class="option-classification"><span>{h(enum_label(item.get('relationship', '')))}</span><span class="comparison-status status-{safe_token(item.get('comparison_status', ''))}">{h(enum_label(item.get('comparison_status', '')))}</span></div></div>{entity_refs(item.get('mechanism_stage_ids'), stage_index, 'stage', '机制阶段 / Mechanism stages')}</header>
  <p class="technical-bet">{h(item.get('technical_bet', ''))}</p>
  <div class="comparison-note"><span>可比性边界 <span lang="en">Comparison boundary</span></span><p>{h(item.get('comparison_note', ''))}</p></div>
  <div class="hypothesis"><span>Core hypothesis</span><p>{h(item.get('core_hypothesis', ''))}</p></div>
  <div class="option-grid"><div><h4>优势 <span lang="en">Advantages</span></h4>{plain_list(item.get('advantages'))}</div><div><h4>成本 <span lang="en">Costs</span></h4>{plain_list(item.get('costs'))}</div><div><h4>失败模式 <span lang="en">Failure modes</span></h4>{plain_list(item.get('failure_modes'))}</div><div><h4>可证伪条件 <span lang="en">Falsifiers</span></h4>{plain_list(item.get('falsifiers'))}</div></div>
  <div class="validity-grid"><div><h4>成立条件 <span lang="en">Valid when</span></h4>{plain_list(item.get('valid_when'))}</div><div><h4>失效条件 <span lang="en">Invalid when</span></h4>{plain_list(item.get('invalid_when'))}</div></div>
  <footer>{proposition_refs(item.get('supporting_proposition_ids'), proposition_index)}{paper_refs(item.get('representative_paper_ids'), paper_index)}</footer>
</article>""")
    content = "".join(rows) or empty_state("尚未形成技术选项", "No technical option identified")
    statuses = {text_value(item, "comparison_status", default="") for item in options}
    if options and statuses == {"not_comparable"}:
        comparison_summary = "这些选项作用于不同阶段或使用不同任务、数据和效用函数；本报告不做路线排名。"
    elif options:
        comparison_summary = "只有明确标注为可比较或部分可比较的选项才能在其 comparison note 所限定的共同基础上比较；其余选项不构成隐含排名。"
    else:
        comparison_summary = "当前证据不足以定义或比较技术选项。"
    return f'<section class="section" id="technical-options">{section_heading("05", "技术选项与可比性", "Technical Options & Comparability")}<p class="section-note">{h(comparison_summary)}</p><div class="technical-option-list">{content}</div></section>'


def frontier_rail(level: Any) -> str:
    current = str(level)
    stages = (
        ("conceptual", "概念"),
        ("prototype", "原型"),
        ("benchmark", "基准"),
        ("controlled_user_study", "受控用户研究"),
        ("longitudinal_deployment", "长期部署"),
    )
    return '<ol class="categorical-rail frontier-rail" aria-label="能力边界：' + h(enum_label(level)) + '">' + "".join(
        f'<li class="{"is-current" if key == current else ""}"><span></span><b>{h(label)}</b><small>{h(key.replace("_", " ").title())}</small></li>'
        for key, label in stages
    ) + '</ol>'


def render_boundary_evidence(
    ids: Any, evidence_index: dict[str, dict[str, Any]]
) -> str:
    rows = []
    for evidence_id in unique(
        str(value) for value in as_list(ids) if isinstance(value, str)
    ):
        evidence = evidence_index.get(evidence_id)
        if evidence is None:
            continue
        ordinal = list(evidence_index).index(evidence_id) + 1
        rows.append(
            f'<li class="boundary-evidence-item reasoning-bound" data-evidence-id="{h(evidence_id)}">'
            f'<a class="evidence-ref" href="#{h(evidence_anchor(evidence_id))}">E{ordinal}</a>'
            f'<div><p>{h(evidence.get("statement", ""))}</p>'
            f'<small>{h(enum_label(evidence.get("source_depth", "")))} · {h(confidence_label(evidence.get("confidence", "")))}</small></div></li>'
        )
    if not rows:
        return empty_state("尚无可展示的边界证据", "No boundary evidence available")
    return '<ol class="boundary-evidence-list">' + "".join(rows) + '</ol>'


def render_observed_failures(
    failures: Any, evidence_index: dict[str, dict[str, Any]]
) -> str:
    rows = []
    for failure in as_list(failures):
        item = as_dict(failure)
        evidence_ids = unique(
            str(value)
            for value in as_list(item.get("evidence_ids"))
            if isinstance(value, str)
        )
        rows.append(
            f'<li class="observed-failure-item reasoning-bound" data-evidence-ids="{h(" ".join(evidence_ids))}">'
            f'<p>{h(item.get("statement", ""))}</p>'
            f'{evidence_refs(evidence_ids, evidence_index)}</li>'
        )
    if not rows:
        return empty_state("本次语料未提取已观察失败", "No observed failure extracted")
    return '<ul class="observed-failure-list">' + "".join(rows) + '</ul>'


def render_capability_frontier(
    report: dict[str, Any],
    evidence_index: dict[str, dict[str, Any]],
    proposition_index: dict[str, dict[str, Any]],
) -> str:
    frontier = as_dict(report.get("capability_frontier"))
    cards = []
    for capability in as_list(frontier.get("capabilities")):
        item = as_dict(capability)
        capability_id = text_value(item, "id", default="capability")
        cards.append(f"""
<article class="capability reasoning-bound" id="capability-{safe_token(capability_id)}">
  <header><h3>{h(item.get('label_zh', ''))} <span lang="en">{h(item.get('label_en', ''))}</span></h3></header>
  {frontier_rail(item.get('frontier_level', ''))}
  <div class="boundary-shift"><div><span>Current boundary</span><p>{h(item.get('current_boundary', ''))}</p></div><div><span>Next boundary</span><p>{h(item.get('next_boundary', ''))}</p></div></div>
  <dl class="capability-context"><div><dt>Demonstration context</dt><dd>{h(item.get('demonstration_context', ''))}</dd></div><div><dt>Generalization ceiling</dt><dd>{h(item.get('generalization_ceiling', ''))}</dd></div></dl>
  <div class="capability-evidence"><h4>构成当前边界的最强证据 <span lang="en">Strongest boundary evidence</span></h4>{render_boundary_evidence(item.get('strongest_evidence_ids'), evidence_index)}</div>
  <div class="observed-failures"><h4>来源已观察失败 <span lang="en">Source-observed failures</span></h4>{render_observed_failures(item.get('observed_failures'), evidence_index)}</div>
  <div class="capability-grid"><div class="anticipated-risks"><h4>分析者预期风险 <span lang="en">Analyst-anticipated risks</span></h4>{plain_list(item.get('anticipated_risks'))}</div><div><h4>未满足要求 <span lang="en">Unresolved requirements</span></h4>{plain_list(item.get('unresolved_requirements'))}</div></div>
  <footer>{proposition_refs(item.get('proposition_ids'), proposition_index)}</footer>
</article>""")
    content = "".join(cards) or empty_state("尚不能定义能力边界", "Capability frontier is not yet defined")
    gaps = []
    for gap in as_list(frontier.get("readiness_gaps")):
        item = as_dict(gap)
        gap_id = text_value(item, "id", default="readiness-gap")
        gaps.append(f"""
<article class="readiness-gap reasoning-bound" id="readiness-gap-{safe_token(gap_id)}">
  <header><h3>{h(item.get('label_zh', ''))} <span lang="en">{h(item.get('label_en', ''))}</span></h3></header>
  <dl><div><dt>当前状态 <span lang="en">Current state</span></dt><dd>{h(item.get('current_state', ''))}</dd></div><div><dt>阻断证据 <span lang="en">Blocking evidence</span></dt><dd>{h(item.get('blocking_evidence', ''))}</dd></div></dl>
  <div><h4>跨越条件 <span lang="en">What would close the gap</span></h4>{plain_list(item.get('what_would_close'))}</div>
  <footer>{proposition_refs(item.get('proposition_ids'), proposition_index)}</footer>
</article>""")
    gaps_html = "".join(gaps) or empty_state("未单列就绪缺口", "No readiness gap recorded")
    return f"""
<section class="section" id="capability-frontier">
  {section_heading('03', '当前能力边界与就绪缺口', 'Capability Frontier & Readiness Gaps')}
  <p class="frontier-statement">{h(frontier.get('overall_statement', ''))}</p>
  <div class="capability-list">{content}</div>
  <div class="subsection"><h3 class="subsection-title">从展示能力到可部署能力的缺口 <span lang="en">Readiness Gaps</span></h3><div class="readiness-gap-list">{gaps_html}</div></div>
</section>"""


def render_transition_theses(
    report: dict[str, Any],
    proposition_index: dict[str, dict[str, Any]],
    indicator_index: dict[str, dict[str, Any]],
) -> str:
    cards = []
    for thesis in as_list(report.get("transition_theses")):
        item = as_dict(thesis)
        thesis_id = text_value(item, "id", default="transition")
        is_signal = item.get("status") == "signal"
        from_label = "本批提交的起点叙事 · Observed framing" if is_signal else "From"
        to_label = "待验证方向 · Hypothesized direction" if is_signal else "To"
        counter = proposition_refs(
            item.get("counter_proposition_ids"),
            proposition_index,
            empty=("当前没有反向命题", "No counter-proposition in the current model"),
        )
        cards.append(f"""
<article class="transition reasoning-bound {'signal-transition' if is_signal else ''}" id="transition-{safe_token(thesis_id)}">
  <header><div><span class="status status-{safe_token(item.get('status', ''))}">{h(enum_label(item.get('status', '')))}</span><h3>{h(item.get('statement', ''))}</h3></div><time>{h(item.get('time_from', ''))} — {h(item.get('time_to', ''))}</time></header>
  <div class="transition-shift"><div><span>{h(from_label)}</span><p>{h(item.get('from_state', ''))}</p></div><i aria-hidden="true">{'⇢' if is_signal else '→'}</i><div><span>{h(to_label)}</span><p>{h(item.get('to_state', ''))}</p></div></div>
  <div class="old-constraint"><span>旧范式瓶颈 / Old constraint</span><p>{h(item.get('old_constraint', ''))}</p></div>
  <div class="transition-grid"><div><h4>推动因素 <span lang="en">Drivers</span></h4>{plain_list(item.get('drivers'))}</div><div><h4>替代解释 <span lang="en">Alternative explanations</span></h4>{plain_list(item.get('alternative_explanations'))}</div><div><h4>可证伪条件 <span lang="en">Falsifiers</span></h4>{plain_list(item.get('falsifiers'))}</div></div>
  <div class="support-counter"><div><h4>支持命题 <span lang="en">Support</span></h4>{proposition_refs(item.get('supporting_proposition_ids'), proposition_index)}</div><div><h4>反向命题 <span lang="en">Counter</span></h4>{counter}</div></div>
  <footer><span>{h(confidence_label(item.get('confidence', '')))}</span>{entity_refs(item.get('leading_indicator_ids'), indicator_index, 'indicator', '领先指标 / Leading indicators')}</footer>
</article>""")
    content = "".join(cards) or empty_state("证据不足以形成转型论点", "Evidence is insufficient for a transition thesis")
    trend_ceiling = as_dict(as_dict(report.get("field_thesis")).get("epistemic_ceiling")).get("trend", "")
    return f'<section class="section" id="submission-signals">{section_heading("06", "提交信号与可证伪方向", "Submission Signals & Falsifiable Directions")}<p class="section-note">当前趋势判断上限为 {h(enum_label(trend_ceiling))}。标为 signal 的内容只表示本批提交中的聚类与方向假设，不构成历史趋势证明。</p><div class="transition-list">{content}</div></section>'


def maturity_rail(level: Any) -> str:
    current = str(level)
    stages = (("absent", "缺失"), ("early", "早期"), ("emerging", "形成中"), ("validated", "已验证"), ("mature", "成熟"))
    return '<ol class="categorical-rail maturity-rail" aria-label="成熟度：' + h(enum_label(level)) + '">' + "".join(
        f'<li class="{"is-current" if key == current else ""}"><span></span><b>{h(label)}</b><small>{h(key.title())}</small></li>'
        for key, label in stages
    ) + '</ol>'


def render_maturity(
    report: dict[str, Any], proposition_index: dict[str, dict[str, Any]]
) -> str:
    cards = []
    for assessment in as_list(report.get("maturity_assessment")):
        item = as_dict(assessment)
        dimension = text_value(item, "dimension", default="dimension")
        proposition_ids = as_list(item.get("proposition_ids"))
        cards.append(f"""
<article class="maturity-dimension {'reasoning-bound' if proposition_ids else 'evidence-absence-declared'}" id="maturity-{safe_token(dimension)}">
  <header><h3>{h(enum_label(dimension))}</h3><span class="status status-{safe_token(item.get('level', ''))}">{h(enum_label(item.get('level', '')))}</span></header>
  <p>{h(item.get('statement', ''))}</p>
  {maturity_rail(item.get('level', ''))}
  <div class="maturity-detail"><div><h4>阻碍项 <span lang="en">Blockers</span></h4>{plain_list(item.get('blockers'))}</div><div><h4>升级条件 <span lang="en">Upgrade conditions</span></h4>{plain_list(item.get('upgrade_conditions'))}</div></div>
  <footer>{proposition_refs(item.get('proposition_ids'), proposition_index, empty=('本次语料没有足够命题支持该维度', 'No proposition support in this corpus'))}</footer>
</article>""")
    content = "".join(cards) or empty_state("尚未完成五维成熟度判断", "Five-dimensional maturity is not assessed")
    return f'<section class="section" id="maturity-assessment">{section_heading("07", "五维成熟度", "Five-dimensional Maturity")}<p class="section-note">成熟度是五个相互独立的类别判断，不合成为虚假的总分。</p><div class="maturity-list">{content}</div></section>'


def render_decision_card(
    item: dict[str, Any], proposition_index: dict[str, dict[str, Any]]
) -> str:
    decision_id = text_value(item, "id", default="decision")
    return f"""
<article class="decision reasoning-bound" id="decision-{safe_token(decision_id)}">
  <header><div><span class="status">{h(enum_label(item.get('decision_type', '')))}</span><h3>{h(item.get('decision', ''))}</h3></div><span>{h(item.get('audience', ''))}</span></header>
  <p class="decision-action">{h(item.get('action', ''))}</p>
  <div class="decision-grid"><div><h4>成立条件 <span lang="en">Conditions</span></h4>{plain_list(item.get('conditions'))}</div><div><h4>主要风险 <span lang="en">Risks</span></h4>{plain_list(item.get('risks'))}</div></div>
  <footer><span>{h(enum_label(item.get('reversibility', '')))}</span><span>{h(confidence_label(item.get('confidence', '')))}</span>{proposition_refs(item.get('because_proposition_ids'), proposition_index)}</footer>
</article>"""


def render_decisions(
    report: dict[str, Any], proposition_index: dict[str, dict[str, Any]]
) -> str:
    items = [as_dict(item) for item in as_list(report.get("decision_consequences"))]
    decisions = [item for item in items if item.get("decision_type") != "research_agenda"]
    agenda = [item for item in items if item.get("decision_type") == "research_agenda"]
    decision_html = "".join(render_decision_card(item, proposition_index) for item in decisions) or empty_state("暂无可执行决策后果", "No actionable decision consequence")
    agenda_html = "".join(render_decision_card(item, proposition_index) for item in agenda) or empty_state("暂无优先研究议程", "No prioritized research agenda")
    return f"""
<section class="section" id="decision-consequences">
  {section_heading('08', '决策后果与研究议程', 'Decision Consequences & Research Agenda')}
  <div class="decision-list">{decision_html}</div>
  <div class="subsection"><h3 class="subsection-title">最能改变判断的下一步研究 <span lang="en">Research Agenda</span></h3><div class="decision-list agenda-list">{agenda_html}</div></div>
</section>"""


def render_monitoring(
    report: dict[str, Any], proposition_index: dict[str, dict[str, Any]]
) -> str:
    cards = []
    for indicator in as_list(report.get("leading_indicators")):
        item = as_dict(indicator)
        indicator_id = text_value(item, "id", default="indicator")
        cards.append(f"""
<article class="indicator reasoning-bound" id="indicator-{safe_token(indicator_id)}">
  <header><h3>{h(item.get('label', ''))}</h3></header>
  <p class="indicator-observation">{h(item.get('observation', ''))}</p>
  <dl class="indicator-meta"><div><dt>Current baseline</dt><dd>{h(item.get('current_baseline', ''))}</dd></div><div><dt>Data source</dt><dd>{h(item.get('data_source', ''))}</dd></div><div><dt>Window</dt><dd>{h(item.get('observation_window', ''))}</dd></div></dl>
  <div class="threshold-rule"><header><span>阈值与来源 <span lang="en">Threshold & basis</span></span><b>{h(enum_label(item.get('threshold_basis', '')))}</b></header><p>{h(item.get('threshold_or_trigger', ''))}</p><small>{h(item.get('threshold_rationale', ''))}</small></div>
  <div class="indicator-grid"><div><h4>达到阈值 <span lang="en">If met</span></h4><p>{h(item.get('interpretation_if_met', ''))}</p></div><div><h4>未达到阈值 <span lang="en">If missed</span></h4><p>{h(item.get('interpretation_if_missed', ''))}</p></div></div>
  <div class="decision-trigger"><span>Decision trigger</span><p>{h(item.get('decision_trigger', ''))}</p></div>
  <footer>{proposition_refs(item.get('affects_proposition_ids'), proposition_index)}</footer>
</article>""")
    content = "".join(cards) or empty_state("尚未定义领先指标", "No leading indicator defined")
    return f'<section class="section" id="monitoring">{section_heading("09", "领先指标与监测触发", "Leading Indicators & Monitoring Triggers")}<div class="indicator-list">{content}</div></section>'


def render_metric_rows(metrics: Any, evidence_index: dict[str, dict[str, Any]]) -> str:
    rows = []
    for metric in as_list(metrics):
        item = as_dict(metric)
        evidence_ids = [item["evidence_id"]] if isinstance(item.get("evidence_id"), str) else item.get("evidence_ids", [])
        rows.append(
            '<tr class="reasoning-bound">'
            f'<th scope="row">{h(item.get("name", ""))}</th><td class="metric-value">{h(item.get("value", ""))}</td>'
            f'<td>{h(item.get("context", ""))}</td><td>{h(enum_label(item.get("basis", "")))}</td><td>{evidence_refs(evidence_ids, evidence_index)}</td></tr>'
        )
    return "".join(rows) or '<tr><td colspan="5">' + empty_state("未提取可比较指标", "No comparable metric extracted") + '</td></tr>'


def render_paper(
    paper: dict[str, Any],
    evidence_index: dict[str, dict[str, Any]],
    proposition_index: dict[str, dict[str, Any]],
    stage_index: dict[str, dict[str, Any]],
    option_index: dict[str, dict[str, Any]],
    capability_index: dict[str, dict[str, Any]],
) -> str:
    paper_id = text_value(paper, "arxiv_id", default="paper")
    authors = "; ".join(string_list(paper.get("authors")))
    analysis = as_dict(paper.get("analysis"))
    links = as_dict(paper.get("model_links"))
    findings = []
    for finding in as_list(analysis.get("key_findings")):
        item = as_dict(finding)
        evidence_ids = first_value(item, "evidence_ids", default=[])
        findings.append(
            '<li class="reasoning-bound"><p>' + h(item.get("statement", "")) + '</p>'
            + evidence_refs(evidence_ids, evidence_index) + '</li>'
        )
    findings_html = '<ul class="finding-list">' + "".join(findings) + '</ul>' if findings else empty_state("未提取关键发现", "No key finding extracted")
    external = as_dict(paper.get("external_verification"))
    source_urls = string_list(external.get("source_urls"))
    verification_links = "".join(f'<a href="{h(url)}" rel="noreferrer">External verification</a>' for url in source_urls)
    abstract = text_value(paper, "abstract_original", "abstract", default="")
    abstract_html = (
        '<details class="abstract-source"><summary>原始摘要 <span lang="en">Original abstract</span></summary>'
        f'<p lang="en">{h(abstract)}</p></details>'
        if abstract
        else ""
    )
    return f"""
<article class="paper-record" id="{paper_anchor(paper_id)}">
  <header class="paper-header"><div class="paper-kicker">{h(paper_id)}{h(paper.get('version', ''))} · {h(paper.get('published', ''))} · {h(paper.get('primary_category', ''))}</div><h4 lang="en"><a href="{h(paper.get('source_url', ''))}">{h(paper.get('title', ''))}</a></h4><p class="paper-title-zh">{h(paper.get('title_zh', ''))}</p><p class="authors" lang="en">{h(authors)}</p><div class="paper-tags"><span>{h(enum_label(paper.get('corpus_role', '')))}</span><span>{h(enum_label(paper.get('evidence_basis', '')))}</span><span>{h(paper.get('independence_cluster_id', ''))}</span></div></header>
  <p class="paper-synopsis">{h(text_value(paper, 'synopsis_zh', 'synopsis', default=''))}</p>
  <div class="model-links"><div><b>Stages</b>{entity_refs(links.get('stage_ids'), stage_index, 'stage', '机制阶段')}</div><div><b>Options</b>{entity_refs(links.get('option_ids'), option_index, 'option', '技术选项')}</div><div><b>Capabilities</b>{entity_refs(links.get('capability_ids'), capability_index, 'capability', '能力')}</div><div><b>Propositions</b>{proposition_refs(links.get('proposition_ids'), proposition_index)}</div></div>
  <dl class="paper-analysis"><div><dt>Research object</dt><dd>{h(analysis.get('research_object', ''))}</dd></div><div><dt>Mechanism</dt><dd>{h(analysis.get('mechanism', ''))}</dd></div><div><dt>Evaluation</dt><dd>{h(analysis.get('evaluation', ''))}</dd></div></dl>
  <div class="paper-subsection"><h5>关键发现 <span lang="en">Key findings</span></h5>{findings_html}</div>
  <div class="paper-subsection"><h5>定量证据 <span lang="en">Metrics</span></h5><div class="table-wrap"><table class="metric-table"><thead><tr><th>Metric</th><th>Value</th><th>Context</th><th>Depth</th><th>Evidence</th></tr></thead><tbody>{render_metric_rows(paper.get('metrics'), evidence_index)}</tbody></table></div></div>
  <div class="paper-limitations"><div><h5>作者声明局限 <span lang="en">Author-stated</span></h5>{plain_list(analysis.get('author_stated_limitations'))}</div><div><h5>分析推断局限 <span lang="en">Analyst-inferred</span></h5>{plain_list(analysis.get('analyst_inferred_limitations'))}</div></div>
  {abstract_html}
  <footer class="paper-links"><a href="{h(paper.get('source_url', ''))}">arXiv abstract</a><a href="{h(paper.get('pdf_url', ''))}">PDF</a>{verification_links}</footer>
</article>"""


def render_evidence_ledger(report: dict[str, Any], paper_index: dict[str, dict[str, Any]]) -> str:
    rows = []
    for evidence_number, evidence in enumerate(as_list(report.get("evidence")), start=1):
        item = as_dict(evidence)
        evidence_id = text_value(item, "id", default="evidence")
        locator = item.get("locator")
        if isinstance(locator, dict):
            locator_text = " · ".join(
                str(value) for value in (locator.get("type"), locator.get("label")) if value
            )
        else:
            locator_text = str(locator or "")
        excerpt = text_value(item, "excerpt", default="")
        evidence_source = text_value(item, "source_url", default="")
        source_link = (
            f'<a href="{h(evidence_source)}" rel="noreferrer">Evidence source</a>'
            if evidence_source
            else ""
        )
        rows.append(f"""
<article class="evidence-record" id="{evidence_anchor(evidence_id)}">
  <header><span class="evidence-id">E{evidence_number} · {h(evidence_id)}</span><div><span>{h(enum_label(item.get('source_depth', '')))}</span><span>{h(enum_label(item.get('evidence_type', '')))}</span><span>{h(confidence_label(item.get('confidence', '')))}</span></div></header>
  <p>{h(item.get('statement', ''))}</p>{f'<blockquote>{h(excerpt)}</blockquote>' if excerpt else ''}
  <footer><span>{h(locator_text or 'Locator not supplied')}</span>{paper_refs([item.get('paper_id')], paper_index)}{source_link}</footer>
</article>""")
    content = "".join(rows) or empty_state("证据账本为空", "Evidence ledger is empty")
    return f'<div class="evidence-ledger" id="evidence-ledger"><h3 class="subsection-title">原子证据账本 <span lang="en">Atomic Evidence Ledger</span></h3>{content}</div>'


def render_proposition_index(report: dict[str, Any]) -> str:
    rows = []
    for number, proposition in enumerate(as_list(report.get("propositions")), start=1):
        item = as_dict(proposition)
        rows.append(
            f'<tr class="proposition-index-row"><th scope="row">P{number}</th>'
            f'<td><code>{h(item.get("id", ""))}</code></td>'
            f'<td>{h(item.get("statement", ""))}</td></tr>'
        )
    body = "".join(rows) or '<tr><td colspan="3">No proposition index</td></tr>'
    return (
        '<div class="proposition-index" id="proposition-index">'
        '<h3 class="subsection-title">命题编号索引 <span lang="en">Proposition ID Index</span></h3>'
        '<div class="table-wrap"><table class="proposition-index-table"><thead><tr><th>Short ref</th><th>Raw ID</th><th>Statement</th></tr></thead>'
        f'<tbody>{body}</tbody></table></div></div>'
    )


def render_evidence_base(
    report: dict[str, Any],
    evidence_index: dict[str, dict[str, Any]],
    proposition_index: dict[str, dict[str, Any]],
    paper_index: dict[str, dict[str, Any]],
) -> str:
    scope = as_dict(report.get("scope"))
    coverage = as_dict(report.get("evidence_coverage"))
    screening = as_dict(scope.get("screening"))
    mechanism = as_dict(report.get("mechanism_model"))
    stage_index = {text_value(item, "id", default=""): item for item in as_list(mechanism.get("stages")) if isinstance(item, dict)}
    option_index = {text_value(item, "id", default=""): item for item in as_list(report.get("technical_options")) if isinstance(item, dict)}
    frontier = as_dict(report.get("capability_frontier"))
    capability_index = {text_value(item, "id", default=""): item for item in as_list(frontier.get("capabilities")) if isinstance(item, dict)}
    query_rows = []
    for query in as_list(scope.get("queries")):
        item = as_dict(query)
        query_rows.append(f'<tr><th scope="row">{h(item.get("label", ""))}</th><td><code>{h(item.get("query", ""))}</code></td><td>{h(item.get("layer_id", ""))}</td><td>{h(item.get("sort", ""))}</td><td>{h(item.get("max_results", ""))}</td></tr>')
    query_html = "".join(query_rows) or '<tr><td colspan="5">No recorded query</td></tr>'
    coverage_rows = "".join(
        f'<div><dt>{h(label)}</dt><dd>{h(coverage.get(key, 0))}</dd></div>'
        for key, label in (
            ("papers_total", "Papers"),
            ("metadata_only", "Metadata"),
            ("abstract_screened", "Abstract"),
            ("full_text_reviewed", "Full text"),
            ("externally_verified", "Verified"),
        )
    )
    screening_rows = "".join(
        f'<div><dt>{h(key.replace("_", " ").title())}</dt><dd>{h(value)}</dd></div>'
        for key, value in screening.items()
        if isinstance(value, int)
    )
    papers = "".join(
        render_paper(item, evidence_index, proposition_index, stage_index, option_index, capability_index)
        for item in as_list(report.get("papers"))
        if isinstance(item, dict)
    ) or empty_state("未纳入论文", "No paper included")
    sources = "".join(
        f'<li><a href="{h(item.get("source_url", ""))}" lang="en">{h(item.get("title", ""))}</a><span>{h(item.get("arxiv_id", ""))}{h(item.get("version", ""))} · {h(item.get("published", ""))}</span></li>'
        for item in as_list(report.get("papers"))
        if isinstance(item, dict)
    )
    inclusion = first_value(scope, "inclusion_criteria", "criteria", default=[])
    exclusion = first_value(scope, "exclusion_criteria", default=[])
    gaps = first_value(scope, "coverage_gaps", "evidence_gaps", "known_gaps", "gaps", default=[])
    terminology_rows = []
    for term in as_list(scope.get("terminology")):
        item = as_dict(term)
        variants = " · ".join(string_list(item.get("included_variants"))) or "—"
        terminology_rows.append(
            f'<tr><th scope="row">{h(item.get("term", ""))}</th><td>{h(item.get("definition", ""))}</td><td>{h(variants)}</td></tr>'
        )
    terminology_html = "".join(terminology_rows) or '<tr><td colspan="3">Terminology not recorded</td></tr>'
    layer_rows = []
    for layer in as_list(scope.get("corpus_layers")):
        item = as_dict(layer)
        date_from = item.get("date_from") or "open"
        date_to = item.get("date_to") or "open"
        layer_rows.append(
            f'<tr><th scope="row">{h(item.get("id", ""))}<small>{h(enum_label(item.get("role", "")))}</small></th>'
            f'<td><span class="status status-{safe_token(item.get("status", ""))}">{h(enum_label(item.get("status", "")))}</span></td>'
            f'<td>{h(date_from)} — {h(date_to)}</td><td>{h(item.get("purpose", ""))}</td><td>{h(item.get("coverage_note", ""))}</td></tr>'
        )
    layers_html = "".join(layer_rows) or '<tr><td colspan="5">Corpus layers not recorded</td></tr>'
    return f"""
<section class="section" id="evidence-base">
  {section_heading('10', '证据基础与审计附录', 'Evidence Base & Audit Appendix')}
  <div class="scope-summary"><div class="lead-rule"><h3>操作性定义 <span lang="en">Operational definition</span></h3><p>{h(scope.get('operational_definition', ''))}</p></div><dl><div><dt>Date range</dt><dd>{h(scope.get('date_from', ''))} — {h(scope.get('date_to', ''))}</dd></div><div><dt>Categories</dt><dd>{h(' · '.join(string_list(scope.get('categories'))) or '—')}</dd></div></dl></div>
  <div class="method-counts"><dl class="screening-counts">{screening_rows}</dl><dl class="coverage-counts">{coverage_rows}</dl></div>
  <div class="criteria-grid"><div><h3>纳入标准 <span lang="en">Inclusion</span></h3>{plain_list(inclusion)}</div><div><h3>排除标准 <span lang="en">Exclusion</span></h3>{plain_list(exclusion)}</div><div><h3>证据缺口 <span lang="en">Evidence gaps</span></h3>{plain_list(gaps)}</div></div>
  <div class="subsection"><h3 class="subsection-title">术语与语料层 <span lang="en">Terminology & Corpus Layers</span></h3><div class="table-wrap"><table class="terminology-table"><thead><tr><th>Term</th><th>Operational meaning</th><th>Included variants</th></tr></thead><tbody>{terminology_html}</tbody></table></div><div class="table-wrap layer-table-wrap"><table class="layer-table"><thead><tr><th>Layer</th><th>Status</th><th>Date range</th><th>Purpose</th><th>Coverage note</th></tr></thead><tbody>{layers_html}</tbody></table></div></div>
  <div class="subsection"><h3 class="subsection-title">检索方法 <span lang="en">Exact Search Method</span></h3><div class="table-wrap"><table class="query-table"><thead><tr><th>Query</th><th>Exact expression</th><th>Layer</th><th>Sort</th><th>Limit</th></tr></thead><tbody>{query_html}</tbody></table></div></div>
  <div class="paper-dossiers" id="papers"><h3 class="subsection-title">代表论文档案 <span lang="en">Paper Dossiers</span></h3>{papers}</div>
  {render_proposition_index(report)}
  {render_evidence_ledger(report, paper_index)}
  <div class="report-limitations"><h3 class="subsection-title">报告边界 <span lang="en">Report Limitations</span></h3>{plain_list(report.get('report_limitations'))}</div>
  <div class="sources"><h3 class="subsection-title">论文来源 <span lang="en">arXiv Sources</span></h3><ol class="source-list">{sources}</ol></div>
</section>"""


def render_document(data: dict[str, Any], css: str) -> str:
    report = data["report"]
    proposition_index = {
        text_value(item, "id", default=""): item
        for item in as_list(report.get("propositions"))
        if isinstance(item, dict)
    }
    evidence_index = {
        text_value(item, "id", default=""): item
        for item in as_list(report.get("evidence"))
        if isinstance(item, dict)
    }
    paper_index = {
        text_value(item, "arxiv_id", default=""): item
        for item in as_list(report.get("papers"))
        if isinstance(item, dict)
    }
    indicator_index = {
        text_value(item, "id", default=""): item
        for item in as_list(report.get("leading_indicators"))
        if isinstance(item, dict)
    }
    body = "".join(
        (
            render_header(report),
            render_toc(),
            '<main class="report">',
            render_direct_answer(report, proposition_index),
            render_knowledge_state(report, evidence_index),
            render_capability_frontier(report, evidence_index, proposition_index),
            render_mechanism_model(report, proposition_index),
            render_technical_options(report, proposition_index, paper_index),
            render_transition_theses(report, proposition_index, indicator_index),
            render_maturity(report, proposition_index),
            render_decisions(report, proposition_index),
            render_monitoring(report, proposition_index),
            render_evidence_base(report, evidence_index, proposition_index, paper_index),
            '</main>',
            f'<footer class="site-footer"><p>Schema {h(data.get("schema_version", ""))} · arxiv-paper-report · As of {h(report.get("as_of", ""))}</p></footer>',
        )
    )
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="color-scheme" content="light">
  <title>{h(report.get('title_zh', ''))}</title>
  <style>
{css.rstrip()}
  </style>
</head>
<body>
{body}
</body>
</html>
"""


def main() -> int:
    args = parse_args()
    try:
        data = load_report(args.input)
        errors = validate_report(data)
        if errors:
            for error in errors:
                print(f"ERROR: {error}", file=sys.stderr)
            return 1
        css = CSS_PATH.read_text(encoding="utf-8")
        document = render_document(data, css)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(document, encoding="utf-8")
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"render_report: {exc}", file=sys.stderr)
        return 1

    print(
        f"Rendered v3 decision-intelligence report with "
        f"{len(as_list(data['report'].get('propositions')))} proposition(s), "
        f"{len(as_list(data['report'].get('papers')))} paper(s), and "
        f"{len(as_list(data['report'].get('evidence')))} evidence record(s) -> {args.output}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
