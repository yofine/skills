import type { DesignSystemEntry, TokenSection } from '../data/types.ts'

const esc = (value: string) => value.replace(/[&<>"']/g, (character) => ({
  '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;',
}[character] ?? character))

const moduleTitle = (index: number, title: string) => `## ${index}. ${title}`

const tokenMarkdown = (section: TokenSection) => [
  moduleTitle(['neutral', 'text', 'accent', 'typography', 'foundation'].indexOf(section.id) + 1, section.title),
  '',
  section.description,
  '',
  '| Token | Value | Fallback | Usage |',
  '|---|---|---|---|',
  ...section.tokens.map((token) => `| \`${token.name}\` | \`${token.value}\` | ${token.fallback ? `\`${token.fallback}\`` : '—'} | ${token.usage} |`),
].join('\n')

export function toDesignMarkdown(entry: DesignSystemEntry) {
  const extraModule = entry.iconography ? 1 : 0
  const iconMarkdown = entry.iconography ? [
    moduleTitle(6, 'Iconography'), '', entry.iconography.description, '',
    `- Size: \`${entry.iconography.size}\``, `- Stroke: \`${entry.iconography.stroke}\``, `- Style: ${entry.iconography.style}`, '',
    ...entry.iconography.icons.map((icon) => `- **${icon.name}:** ${icon.label}`), '',
  ] : []
  return [
    `# ${entry.name} Design System`,
    '',
    `> ${entry.tagline} · v${entry.version} · ${entry.platform}`,
    '',
    entry.description,
    '',
    moduleTitle(0, 'Design DNA'),
    '',
    ...entry.dna.flatMap((pillar) => [`### ${pillar.name}`, pillar.belief, `**In practice:** ${pillar.implication}`, '']),
    ...entry.tokens.flatMap((section) => [tokenMarkdown(section), '']),
    ...iconMarkdown,
    moduleTitle(6 + extraModule, 'Live Mock'),
    '',
    `Layout: \`${entry.mock.layout}\`. ${entry.layoutNote}`,
    '',
    moduleTitle(7 + extraModule, 'Component Recipes'),
    '',
    ...entry.components.flatMap((component) => [
      `### ${component.name}`,
      component.summary,
      `- Anatomy: ${component.anatomy.join(', ')}`,
      `- States: ${component.states.join(', ')}`,
      `- Tokens: ${component.tokenNotes.map((note) => `\`${note}\``).join(', ')}`,
      '',
    ]),
    moduleTitle(8 + extraModule, 'Layout Patterns'),
    '',
    ...entry.layoutPatterns.flatMap((layout) => [`### ${layout.name}`, layout.description, `- Grid: ${layout.grid}`, `- Responsive: ${layout.responsive}`, '']),
    `**Layout note:** ${entry.layoutNote}`,
    '',
    moduleTitle(9 + extraModule, 'Interactions'),
    '',
    ...entry.interactions.flatMap((rule) => [`### ${rule.trigger}`, rule.response, `**Accessibility:** ${rule.accessibility}`, '']),
    moduleTitle(10 + extraModule, 'Guidelines'),
    '',
    '| Topic | Do | Don’t |',
    '|---|---|---|',
    ...entry.guidelines.map((rule) => `| ${rule.topic} | ${rule.do} | ${rule.dont} |`),
    '',
    '## Conventions',
    '',
    ...entry.conventions.map((item) => `- **${item.key}:** ${item.rule}`),
    '',
    '## Token preset mappings',
    '',
    ...entry.presetMappings.map((item) => `- \`${item.variable}\` → \`${item.token}\``),
    '',
  ].join('\n')
}

export function toAgentApiMarkdown(entry: DesignSystemEntry) {
  const collection = '/api/design-systems'
  const detail = `${collection}/${entry.slug}`
  return [
    '# Design System Hub — Agent API',
    '',
    '> 本文档供 Agent 读取。它描述如何发现并获取结构化设计系统数据，本身不是设计系统数据响应。',
    '',
    `当前设计系统：**${entry.name}**（slug: \`${entry.slug}\`，version: \`${entry.version}\`）`,
    '',
    '## 推荐读取流程',
    '',
    `1. 请求 \`GET ${collection}\` 发现可用设计系统与 slug。`,
    `2. 请求 \`GET ${detail}\` 获取当前系统的完整结构化 JSON。`,
    `3. 从响应的 \`data\` 中读取 token、设计原则、图标规范、组件、布局、交互与使用规则。`,
    `4. 需要面向实现的连续文本时，再请求 \`GET ${detail}/DESIGN.md\`。`,
    '',
    '## 端点',
    '',
    `- \`GET ${collection}\` — 返回设计系统索引，用于发现 slug。`,
    `- \`GET ${detail}\` — 返回 ${entry.name} 的完整机器可读数据。`,
    `- \`GET ${detail}/API.md\` — 返回当前这份 Agent API 说明。`,
    `- \`GET ${detail}/DESIGN.md\` — 返回面向设计与实现的 Markdown 规范。`,
    `- \`GET ${detail}/design-system.html\` — 返回可独立浏览的设计系统 HTML。`,
    '',
    '不提供 `tokens.json` 下载；token 已包含在详情响应的 `data.tokens` 与 `data.tokenExport` 中。',
    '',
    '## 详情响应契约',
    '',
    '```json',
    '{',
    '  "data": {',
    '    "slug": "string",',
    '    "name": "string",',
    '    "version": "string",',
    '    "tagline": "string",',
    '    "description": "string",',
    '    "primaryColor": "CSS color",',
    '    "palette": "Token[]",',
    '    "dna": "DnaPillar[]",',
    '    "tokens": "TokenSection[]",',
    '    "iconography": "Iconography",',
    '    "components": "ComponentRecipe[]",',
    '    "layoutPatterns": "LayoutPattern[]",',
    '    "interactions": "InteractionRule[]",',
    '    "guidelines": "Guideline[]",',
    '    "conventions": "Convention[]",',
    '    "presetMappings": "PresetMapping[]"',
    '  }',
    '}',
    '```',
    '',
    '## Agent 使用约束',
    '',
    '- 以 API 返回值为事实来源，不从页面截图反推已有 token。',
    '- 实现界面时优先使用 `tokens`、`components`、`layoutPatterns` 和 `interactions`。',
    '- 图标必须遵循 `iconography` 的尺寸、描边与端点规则。',
    '- 不把 Live Mock 中的示例内容当成真实用户或业务数据。',
    '- 保留语义 token 名称；只有目标技术栈要求时才转换格式。',
    '',
  ].join('\n')
}

function tokenTable(section: TokenSection) {
  const colorSection = section.id === 'neutral' || section.id === 'text' || section.id === 'accent'
  return `<p>${esc(section.description)}</p><div class="tokens">${section.tokens.map((token) => `<article><span class="swatch" style="--swatch:${esc(token.value)}"></span><div><strong>${esc(token.name)}</strong><code>${esc(colorSection ? token.fallback ?? token.value : token.value)}</code>${colorSection ? '' : `<small>${esc(token.usage)}</small>`}</div></article>`).join('')}</div>`
}

export function toStandaloneHtml(entry: DesignSystemEntry) {
  const sections = entry.tokens.map((section, index) => `<section><div class="rule"><span>§${index + 1}</span></div><h2><em>${index + 1}.</em> ${esc(section.title)}</h2>${tokenTable(section)}</section>`).join('')
  const extraModule = entry.iconography ? 1 : 0
  const icons = entry.iconography ? `<section><div class="rule"><span>§6</span></div><h2><em>6.</em> Iconography</h2><p>${esc(entry.iconography.description)}</p><div class="cards">${entry.iconography.icons.map((icon) => `<article><strong>${esc(icon.name)}</strong><small>${esc(icon.label)}</small></article>`).join('')}</div></section>` : ''
  return `<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${esc(entry.name)} Design System</title>
<style>
:root{color-scheme:light;--ink:#1d1b18;--muted:#777169;--line:#ddd8d0;--paper:#faf9f6}*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font:15px/1.6 Inter,ui-sans-serif,system-ui,sans-serif}.top{height:46px;border-bottom:1px solid var(--line);display:flex;align-items:center;padding:0 3vw;font-size:13px}.wrap{width:min(1024px,calc(100% - 40px));margin:auto;padding:56px 0 120px}.cover{height:190px;border-radius:24px;background:${esc(entry.primaryColor)};display:flex;align-items:flex-end;padding:28px;gap:7px}.cover i{width:30px;height:30px;border:2px solid #ffffff70;border-radius:8px}.eyebrow{margin:36px 0 8px;text-transform:uppercase;letter-spacing:.15em;font-size:11px;color:var(--muted)}h1{font-size:clamp(34px,6vw,56px);line-height:1;margin:0}h2{font-size:25px;margin:18px 0 6px}h2 em{color:#aaa49b;font-style:normal}p{color:var(--muted);max-width:760px}.rule{display:flex;align-items:center;gap:12px;margin:64px 0 30px;color:#8f887e;font-size:11px;font-weight:700}.rule:before,.rule:after{content:"";height:1px;background:#c5beb4;flex:1}.cards,.tokens{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}.cards article,.tokens article{border:1px solid var(--line);border-radius:14px;padding:18px;background:#fff8;box-shadow:0 6px 20px #302b2510}.cards strong,.tokens strong{display:block}.cards small,.tokens small{display:block;color:var(--muted)}.tokens article{display:flex;gap:12px}.swatch{width:34px;height:34px;border-radius:9px;background:var(--swatch);border:0;flex:none}code{display:block;color:#777169;font-size:11px;overflow-wrap:anywhere}.spec-table{overflow:auto;border:1px solid var(--line);border-radius:14px;background:#fff8}.spec-table table{width:100%;min-width:720px;border-collapse:collapse;table-layout:fixed}.spec-table th{padding:12px 15px;background:#f1ede7;text-align:left;text-transform:uppercase;letter-spacing:.08em;font-size:10px;color:var(--muted)}.spec-table td{padding:14px 15px;border-top:1px solid var(--line);vertical-align:top;color:var(--muted);font-size:12px}.spec-table th:nth-child(1){width:18%}.spec-table th:nth-child(2){width:34%}.spec-table th:nth-child(3){width:21%}.spec-table th:nth-child(4){width:27%}.spec-table td strong{color:var(--ink)}.spec-table td code{padding:2px 5px;border-radius:5px;background:#efebe5;color:var(--ink)}.do{color:#3f7b4d}.dont{color:#b04d46}@media(max-width:720px){.cards,.tokens{grid-template-columns:1fr}.wrap{padding-top:24px}.cover{height:130px}}
</style></head><body><header class="top">Design System Hub&nbsp; / &nbsp;<strong>${esc(entry.name)}</strong></header><main class="wrap"><div class="cover">${entry.palette.slice(0, 9).map((token) => `<i style="background:${esc(token.value)}"></i>`).join('')}</div><p class="eyebrow">${esc(entry.style)} · ${esc(entry.platform)}</p><h1>${esc(entry.name)} Design System</h1><p>${esc(entry.description)}</p><section><div class="rule"><span>§0</span></div><h2><em>0.</em> Design DNA</h2><div class="cards">${entry.dna.map((pillar) => `<article><strong>${esc(pillar.name)}</strong><small>${esc(pillar.belief)} ${esc(pillar.implication)}</small></article>`).join('')}</div></section>${sections}${icons}<section><div class="rule"><span>§${6 + extraModule}</span></div><h2><em>${6 + extraModule}.</em> Live Mock</h2><p>Layout: ${esc(entry.mock.layout)}. ${esc(entry.layoutNote)}</p></section><section><div class="rule"><span>§${7 + extraModule}</span></div><h2><em>${7 + extraModule}.</em> Component Recipes</h2><div class="cards">${entry.components.map((component) => `<article><strong>${esc(component.name)}</strong><small>${esc(component.summary)}</small><code>${esc(component.tokenNotes.join(' · '))}</code></article>`).join('')}</div></section><section><div class="rule"><span>§${8 + extraModule}</span></div><h2><em>${8 + extraModule}.</em> Layout Patterns</h2><div class="spec-table"><table><thead><tr><th>Pattern</th><th>Purpose</th><th>Grid</th><th>Responsive rule</th></tr></thead><tbody>${entry.layoutPatterns.map((layout) => `<tr><td><strong>${esc(layout.name)}</strong></td><td>${esc(layout.description)}</td><td><code>${esc(layout.grid)}</code></td><td>${esc(layout.responsive)}</td></tr>`).join('')}</tbody></table></div></section><section><div class="rule"><span>§${9 + extraModule}</span></div><h2><em>${9 + extraModule}.</em> Interactions</h2><div class="cards">${entry.interactions.map((rule) => `<article><strong>${esc(rule.trigger)}</strong><small>${esc(rule.response)} ${esc(rule.accessibility)}</small></article>`).join('')}</div></section><section><div class="rule"><span>§${10 + extraModule}</span></div><h2><em>${10 + extraModule}.</em> Guidelines</h2><div class="cards">${entry.guidelines.map((rule) => `<article><strong>${esc(rule.topic)}</strong><small class="do">Do — ${esc(rule.do)}</small><small class="dont">Don’t — ${esc(rule.dont)}</small></article>`).join('')}</div></section></main></body></html>`
}
