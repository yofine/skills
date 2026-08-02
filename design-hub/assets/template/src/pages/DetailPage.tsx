import { Check, Clipboard, Code2, FileText } from 'lucide-react'
import type { CSSProperties } from 'react'
import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { MockPreview } from '../components/MockPreview'
import { findDesignSystem } from '../data/registry'
import type { Token, TokenSection } from '../data/types'

function Divider({ index }: { index: number }) {
  return <div className="section-divider"><span>§{index}</span></div>
}

function ModuleHeading({ index, title, note }: { index: number; title: string; note?: string }) {
  return <><h2 className="module-title"><span>{index}.</span> {title}</h2>{note && <p className="module-note">{note}</p>}</>
}

function tokenLabel(name: string) {
  return name.replaceAll('-', ' ').replaceAll('/', ' · ')
}

function tokenUsage(token: Token) {
  if (/[\u3400-\u9fff]/.test(token.usage)) return token.usage
  const key = token.name.toLowerCase()
  if (key.includes('font-ui')) return '应用界面与控件文字'
  if (key.includes('font-mono')) return '命令、代码与技术数值'
  if (key.includes('display') || key.includes('hero')) return '主视觉与欢迎区标题'
  if (key.includes('page') || key.includes('title')) return '页面与分组标题'
  if (key.includes('body')) return '正文与说明文字'
  if (key.includes('control')) return '导航、按钮与字段'
  if (key.includes('caption') || key.includes('micro')) return '元数据与辅助说明'
  if (key.includes('space')) return '间距与布局节奏'
  if (key.includes('radius')) return '控件与表面圆角'
  if (key.includes('shadow') || key.includes('elevation')) return '层级与浮动反馈'
  if (key.includes('motion') || key.includes('duration') || key.includes('ease')) return '状态切换与面板过渡'
  if (key.includes('width') || key.includes('content') || key.includes('rail')) return '桌面布局尺寸'
  if (key.includes('border')) return '面板与控件边界'
  return '设计系统规格用途'
}

function typographySample(name: string, systemName: string) {
  const key = name.toLowerCase()
  if (key.includes('mono')) return 'npm run workspace'
  if (key.includes('display')) return `Hello, ${systemName}`
  if (key.includes('page') || key.includes('title')) return 'Recent activity'
  if (key.includes('section')) return 'Always ready'
  if (key.includes('body')) return 'Focused tools for everyday work.'
  if (key.includes('control')) return 'Create new task'
  if (key.includes('caption')) return 'Available across desktop'
  if (key.includes('font')) return 'Aa 0123 — 设计系统'
  return 'Clear hierarchy, quiet rhythm.'
}

function typographyStyle(token: Token): CSSProperties {
  const key = token.name.toLowerCase()
  const weight = token.value.match(/(?:^|\/)\s*([1-9]00)\s*$/)?.[1]
  const style: CSSProperties = { fontWeight: weight ? Number(weight) : undefined }
  if (key.includes('font')) style.fontFamily = token.value
  if (key.includes('display')) style.fontSize = 'clamp(30px, 4vw, 46px)'
  else if (key.includes('page') || key.includes('title')) style.fontSize = 'clamp(24px, 3vw, 34px)'
  else if (key.includes('section')) style.fontSize = '24px'
  else if (key.includes('body')) style.fontSize = '17px'
  else if (key.includes('control')) style.fontSize = '15px'
  else if (key.includes('caption')) style.fontSize = '13px'
  else if (key.includes('mono')) style.fontSize = '17px'
  else style.fontSize = '22px'
  return style
}

function foundationCategory(name: string) {
  const key = name.toLowerCase()
  if (key.includes('radius')) return 'Radius'
  if (key.includes('space')) return 'Spacing'
  if (key.includes('shadow') || key.includes('elevation')) return 'Elevation'
  if (key.includes('motion') || key.includes('duration') || key.includes('ease')) return 'Motion'
  if (key.includes('width') || key.includes('content') || key.includes('sidebar') || key.includes('layout')) return 'Layout'
  return 'Foundation'
}

function ColorSpec({ section }: { section: TokenSection }) {
  return <div className="color-spec-grid">{section.tokens.map((token) => <article className="color-spec" key={token.name}><i style={{ background: token.value }} /><div><strong>{tokenLabel(token.name)}</strong><code>{token.fallback ?? token.value}</code></div></article>)}</div>
}

function TypographySpec({ section, systemName }: { section: TokenSection; systemName: string }) {
  return <div className="type-spec-list">{section.tokens.map((token) => <article className="type-spec" key={token.name}><span>{tokenLabel(token.name)}</span><strong style={typographyStyle(token)}>{typographySample(token.name, systemName)}</strong><footer><code>{token.value}</code><small>{tokenUsage(token)}</small></footer></article>)}</div>
}

function FoundationSpec({ section }: { section: TokenSection }) {
  return <div className="spec-table"><table><thead><tr><th>Category</th><th>Token</th><th>Value</th><th>Usage</th></tr></thead><tbody>{section.tokens.map((token) => <tr key={token.name}><td>{foundationCategory(token.name)}</td><td><code>{token.name}</code></td><td>{token.value}</td><td>{tokenUsage(token)}</td></tr>)}</tbody></table></div>
}

function TokenModule({ section, index, systemName }: { section: TokenSection; index: number; systemName: string }) {
  let content
  if (section.id === 'typography') content = <TypographySpec section={section} systemName={systemName} />
  else if (section.id === 'foundation') content = <FoundationSpec section={section} />
  else content = <ColorSpec section={section} />
  return <section><Divider index={index} /><ModuleHeading index={index} title={section.title} note={section.description} />{content}</section>
}

function IconographySpec({ entry }: { entry: NonNullable<ReturnType<typeof findDesignSystem>> }) {
  const rounded = entry.iconography.style.toLowerCase().includes('round') || entry.iconography.style.toLowerCase().includes('soft')
  return <div className="icon-spec"><header><span>Size <code>{entry.iconography.size}</code></span><span>Stroke <code>{entry.iconography.stroke}</code></span><span>Style <code>{entry.iconography.style}</code></span></header><div>{entry.iconography.icons.map((icon) => <article key={icon.name}><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={Number.parseFloat(entry.iconography.stroke)} strokeLinecap={rounded ? 'round' : 'square'} strokeLinejoin={rounded ? 'round' : 'miter'} aria-hidden="true">{icon.paths.map((path) => <path d={path} key={path} />)}</svg><strong>{icon.name}</strong><small>{icon.label}</small></article>)}</div></div>
}

export function DetailPage() {
  const { slug = '' } = useParams()
  const entry = findDesignSystem(slug)
  const [copied, setCopied] = useState(false)
  useEffect(() => { document.title = entry ? `${entry.name} · Design System Hub` : 'Design system not found · Design System Hub' }, [entry])
  if (!entry) return <main className="not-found"><h1>Design system not found.</h1><Link to="/">Back to Hub</Link></main>

  async function copyTokens() {
    await navigator.clipboard.writeText(entry!.tokenExport)
    setCopied(true)
    window.setTimeout(() => setCopied(false), 1600)
  }

  const api = `/api/design-systems/${entry.slug}`
  const extraModule = 1
  return <>
    <nav className="detail-nav"><Link to="/">← Hub</Link><span>/</span><strong>{entry.name}</strong><span className="nav-meta">v{entry.version} · {entry.platform}</span></nav>
    <main className="detail wrap">
      <div className="detail-cover" style={{ '--detail-primary': entry.primaryColor, color: entry.onPrimaryColor } as CSSProperties}><div className="mini-palette" aria-hidden="true">{entry.palette.slice(0, 10).map((token) => <i key={token.name} style={{ background: token.value }} title={token.name} />)}</div></div>
      <header className="detail-header">
        <span className="eyebrow">{entry.style} · {entry.platform}</span>
        <h1>{entry.name} Design System</h1>
        <p>{entry.description}</p>
        <div className="export-bar">
          <button onClick={copyTokens}>{copied ? <Check /> : <Clipboard />}{copied ? 'Copied' : 'Copy Tokens'}</button>
          <a href={`${api}/DESIGN.md`}><FileText /> DESIGN.md</a>
          <a href={`${api}/design-system.html`}><Code2 /> HTML</a>
          <a href={`${api}/API.md`} target="_blank" rel="noreferrer"><FileText /> API Doc</a>
        </div>
      </header>

      <section><Divider index={0} /><ModuleHeading index={0} title="Design DNA" /><div className="dna-grid">{entry.dna.map((pillar, index) => <article key={pillar.name}><span>{String(index + 1).padStart(2, '0')}</span><strong>{pillar.name}</strong><p>{pillar.belief}</p><small>{pillar.implication}</small></article>)}</div></section>
      {entry.tokens.map((section, index) => <TokenModule section={section} index={index + 1} systemName={entry.name} key={section.id} />)}
      <section><Divider index={6} /><ModuleHeading index={6} title="Iconography" note={entry.iconography.description} /><IconographySpec entry={entry} /></section>
      <section><Divider index={6 + extraModule} /><ModuleHeading index={6 + extraModule} title={`${entry.platform} — Live Mock`} note="使用该设计系统的 token、组件与状态构建的代表性应用场景。" /><MockPreview entry={entry} /></section>
      <section><Divider index={7 + extraModule} /><ModuleHeading index={7 + extraModule} title="Component Recipes" note="可复用组件规格，包含结构、状态以及塑造其特征的 token 组合。" /><div className="recipe-grid">{entry.components.map((component) => <article key={component.name}><strong>{component.name}</strong><p>{component.summary}</p><small>{component.anatomy.join(' · ')}</small><code>{component.tokenNotes.join(' · ')}</code><div>{component.states.map((state) => <span key={state}>{state}</span>)}</div></article>)}</div></section>
      <section><Divider index={8 + extraModule} /><ModuleHeading index={8 + extraModule} title="Layout Patterns" note={entry.layoutNote} /><div className="spec-table layout-table"><table><thead><tr><th>Pattern</th><th>Purpose</th><th>Grid</th><th>Responsive rule</th></tr></thead><tbody>{entry.layoutPatterns.map((layout) => <tr key={layout.name}><td><strong>{layout.name}</strong></td><td>{layout.description}</td><td><code>{layout.grid}</code></td><td>{layout.responsive}</td></tr>)}</tbody></table></div></section>
      <section><Divider index={9 + extraModule} /><ModuleHeading index={9 + extraModule} title="Interactions" note="面向桌面端与键盘操作的行为、反馈和无障碍规则。" /><div className="spec-table interaction-table"><table><thead><tr><th>Trigger</th><th>Response</th><th>Accessibility</th></tr></thead><tbody>{entry.interactions.map((rule) => <tr key={rule.trigger}><td><strong>{rule.trigger}</strong></td><td>{rule.response}</td><td>{rule.accessibility}</td></tr>)}</tbody></table></div></section>
      <section><Divider index={10 + extraModule} /><ModuleHeading index={10 + extraModule} title="Do / Don’t" note="通过成对规则保护设计系统的视觉特征。" /><div className="guideline-pairs">{entry.guidelines.map((rule) => <article key={rule.topic}><div className="guideline-do"><span>✓</span><p><strong>{rule.topic}</strong>{rule.do}</p></div><div className="guideline-dont"><span>×</span><p><strong>{rule.topic}</strong>{rule.dont}</p></div></article>)}</div></section>
    </main>
  </>
}
