import type { CSSProperties } from 'react'
import type { DesignSystemEntry } from '../data/types'
import './superset.css'

export default function SupersetMock({ entry }: { entry: DesignSystemEntry }) {
  const data = entry.mock.layout === 'system-specific' ? entry.mock.data : {}
  const workspace = String(data.workspace ?? 'Atlas')
  const branch = String(data.branch ?? 'feature/runtime')
  const accentColor =
    entry.tokens.find((section) => section.id === 'accent')?.tokens[0]?.value ?? '#16c8a3'
  const style = { '--super-accent': accentColor } as CSSProperties

  return (
    <div className="live-window super-window" style={style}>
      <div className="super-app">
        <header className="super-titlebar">
          <span className="super-traffic"><i /><i /><i /></span>
          <nav className="super-history"><button>←</button><button>→</button><button>↻</button></nav>
          <div className="super-search">⌕&nbsp;&nbsp;Search {workspace.toLowerCase()}… <kbd>⌘ P</kbd></div>
          <div className="super-title-actions"><span>▦</span><button>Open⌄</button><b>W</b></div>
        </header>

        <div className="super-body">
          <aside className="super-sidebar">
            <nav className="super-global-nav"><span>▱ <b>Workspaces</b></span><span>▣ <b>Issues &amp; PRs</b></span><span>＋ <b>New Workspace</b><kbd>⌘N</kbd></span></nav>
            <section className="super-project">
              <header><b>A</b><strong>{workspace}</strong><small>1</small><span>＋⌄</span></header>
              <article className="active"><i>▰</i><div><strong>local</strong><small>{branch}</small></div></article>
            </section>
            <div className="super-setup-card"><span>SETUP</span><strong>Workspace scripts</strong><p>Prepare dependencies and checks for this project.</p><button>Configure</button></div>
            <footer>▣&nbsp;&nbsp;Add repository</footer>
          </aside>

          <main className="super-workbench">
            <div className="super-tabs"><span>planner</span><span>reviewer</span><span className="active">builder</span><button>＋</button></div>
            <div className="super-models"><button>⚙</button><span>✦ nova</span><span>◈ atlas</span><span>◇ orbit</span><span>● forge</span><span>◉ relay</span><button className="super-run">⚙ Run <kbd>⌘G</kbd>⌄</button></div>
            <div className="super-context"><span>workspace@local: ~/{workspace}</span><span>▯ ×</span></div>
            <section className="super-terminal">
              <div className="super-prompt"><b>→</b><strong>{workspace}</strong><span>git:</span><em>({branch})</em><i>▌</i></div>
              <div className="super-run-card">
                <header><span><i /> Build verification</span><small>RUNNING</small></header>
                <div className="super-run-grid">
                  <article><b>01</b><span>Resolve workspace</span><i className="done">✓</i></article>
                  <article><b>02</b><span>Check type contracts</span><i className="done">✓</i></article>
                  <article><b>03</b><span>Run component tests</span><i className="progress" /></article>
                  <article><b>04</b><span>Prepare review summary</span><i /></article>
                </div>
              </div>
            </section>
          </main>

          <aside className="super-inspector">
            <header><span>⌁</span><span>▯</span><span>⛶</span><span>×</span></header>
            <nav><b>Diffs <small>3</small></b><span>Review <small>0</small></span></nav>
            <div className="super-inspector-tools"><span>⌁</span><span>⇩</span><span>≡</span><span>↻</span></div>
            <section className="super-change-list">
              <article><i className="modified">M</i><span><strong>runtime.ts</strong><small>src/engine</small></span><b>+12</b></article>
              <article><i className="added">A</i><span><strong>review.ts</strong><small>src/checks</small></span><b>+48</b></article>
              <article><i className="modified">M</i><span><strong>tokens.css</strong><small>src/ui</small></span><b>+6</b></article>
            </section>
            <footer><textarea aria-label="Commit message" placeholder="Commit message" /><button>✓&nbsp;&nbsp;Commit</button></footer>
          </aside>
        </div>
      </div>
    </div>
  )
}
