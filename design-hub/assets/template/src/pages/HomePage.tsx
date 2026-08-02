import { Link } from 'react-router-dom'
import { useEffect, useState } from 'react'
import { registry } from '../data/registry'

const extractionSteps = [
  '读取并归组同一站点的 5 个页面',
  '提取 Design DNA、Tokens 与 Iconography',
  '生成组件、布局规则与脱敏 Live Mock',
  '写入 Hub 并准备 Agent API',
]

function HowToAddCard() {
  const [stage, setStage] = useState(0)

  useEffect(() => {
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      setStage(extractionSteps.length)
      return
    }
    const timers = [900, 1800, 2900, 4100].map((delay, index) => window.setTimeout(() => setStage(index + 1), delay))
    return () => timers.forEach((timer) => window.clearTimeout(timer))
  }, [])

  const complete = stage === extractionSteps.length
  return <article className="how-card">
    <header><span className="traffic"><i /><i /><i /></span><strong>How to add</strong><span>Screenshot → System</span></header>
    <div className="how-conversation">
      <div className="prompt">帮我把这 5 张截图提取成一套设计系统</div>
      <div className="how-shots" aria-label="同一站点的 5 张界面参考图">
        {Array.from({ length: 5 }, (_, index) => <div className="how-shot" key={index} aria-label={`站点页面 ${index + 1}`}><i /><b /><span /></div>)}
      </div>
      <div className={`analysis${complete ? ' complete' : ''}`}>
        <div className="agent-status"><i />Agent · {complete ? '抽取完成' : '正在处理'}</div>
        <strong>{complete ? '已添加到 Hub' : '正在构建设计系统'}</strong>
        <ul>{extractionSteps.map((step, index) => <li className={index < stage ? 'done' : index === stage ? 'active' : ''} key={step}>{step}</li>)}</ul>
        <footer><span>{complete ? '完成 · 未修改存量内容' : `处理中 ${stage + 1} / ${extractionSteps.length}`}</span><code>DESIGN.md · HTML · API</code></footer>
      </div>
    </div>
  </article>
}

export function HomePage() {
  useEffect(() => { document.title = 'Design System Hub' }, [])
  return (
    <main className="home wrap">
      <header className="home-hero">
        <span className="eyebrow">Design System Hub</span>
        <h1>Every pixel,<br /><span>intentional.</span></h1>
        <p>A curated collection of design systems — tokens, components, and guidelines — all in one place.</p>
      </header>

      <section className="system-grid" aria-label="Design systems">
        {registry.map((entry) => (
          <Link className="system-card" to={`/${entry.slug}`} key={entry.slug}>
            <div className="card-cover" style={{ background: entry.primaryColor, color: entry.onPrimaryColor }}>
              <span className="version">v{entry.version}</span>
              <div className="mini-palette" aria-hidden="true">{entry.palette.slice(0, 9).map((token) => <i key={token.name} style={{ background: token.value }} title={token.name} />)}</div>
            </div>
            <div className="card-body">
              <div className="card-title"><h2>{entry.name}</h2><span>{entry.platform}</span></div>
              <p>{entry.tagline}</p>
              <small>{entry.description}</small>
            </div>
          </Link>
        ))}
        <HowToAddCard />
      </section>
    </main>
  )
}
