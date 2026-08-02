import type { CSSProperties } from 'react'
import {
  ArrowUp,
  BarChart3,
  Bell,
  Box,
  Clapperboard,
  Command,
  Download,
  Gamepad2,
  Globe2,
  Grid2X2,
  HardDrive,
  Image as ImageIcon,
  Monitor,
  PanelLeftClose,
  Plus,
  Search,
  ShoppingBag,
  Sparkles,
  Terminal,
  Video,
  WandSparkles,
} from 'lucide-react'
import type { DesignSystemEntry } from '../data/types'
import './mulerun.css'

type MuleMockData = {
  profile?: string
  credits?: string
  activeTask?: string
}

export default function MuleRunMock({ entry }: { entry: DesignSystemEntry }) {
  const data = (entry.mock.layout === 'system-specific' ? entry.mock.data : {}) as MuleMockData
  const profile = data.profile ?? 'Mira'
  const credits = data.credits ?? '3,280'
  const activeTask = data.activeTask ?? 'Research brief'
  const style = {
    '--mule-primary': entry.primaryColor,
    '--mule-on-primary': entry.onPrimaryColor,
  } as CSSProperties

  return (
    <div className="live-window mule-window" style={style}>
      <div className="mule-shell">
        <aside className="mule-sidebar" aria-label="Workspace navigation">
          <header className="mule-brand-row">
            <span className="mule-mark"><WandSparkles /></span>
            <button type="button" aria-label="Collapse sidebar"><PanelLeftClose /></button>
          </header>

          <button className="mule-new-task" type="button">
            <Plus /><strong>New task</strong><kbd>⌘ K</kbd>
          </button>

          <nav className="mule-nav mule-nav-primary">
            <span><Search /><b>Search</b></span>
          </nav>

          <div className="mule-divider" />

          <nav className="mule-nav mule-nav-tools">
            <span><Clapperboard /><b>Studio</b><small>Beta</small></span>
            <span><Terminal /><b>CLI</b><small>Beta</small></span>
            <span><Monitor /><b>Computer</b></span>
            <span><HardDrive /><b>Drive</b></span>
          </nav>

          <div className="mule-divider" />

          <nav className="mule-nav">
            <span><Grid2X2 /><b>Toolbox</b><i>›</i></span>
          </nav>

          <section className="mule-tasks">
            <header><span>Your tasks</span><i>⌄</i></header>
            <div className="active"><em /><Command /><span>{activeTask}</span></div>
            <div><Command /><span>Campaign outline</span></div>
          </section>

          <footer className="mule-sidebar-footer">
            <span><Download />Download apps</span><Bell />
          </footer>
        </aside>

        <main className="mule-workspace">
          <header className="mule-account-row">
            <button type="button"><Globe2 />EN <span>⌄</span></button>
            <button type="button" className="mule-credit"><Sparkles />{credits}</button>
            <span className="mule-avatar" aria-label={`${profile} profile`}>{profile.slice(0, 1)}</span>
          </header>

          <section className="mule-center">
            <span className="mule-computer-badge"><small>Beta</small><Monitor /> Start a cloud computer <b>↗</b></span>
            <h3>Hello, <strong>{profile}</strong></h3>
            <h4>What would you like to move forward?</h4>

            <div className="mule-composer">
              <div className="mule-composer-prompt">
                <span>Plan a concise research brief from my workspace</span>
                <kbd>TAB</kbd>
              </div>
              <div className="mule-composer-tools">
                <nav>
                  <button type="button" aria-label="Add context"><Plus /></button>
                  <button type="button" aria-label="Open tools"><Command /></button>
                </nav>
                <nav>
                  <button className="mule-mode" type="button"><Sparkles />Pro <span>⌄</span></button>
                  <button className="mule-send" type="button" aria-label="Send"><ArrowUp /></button>
                </nav>
              </div>
            </div>

            <div className="mule-shortcuts" aria-label="Capability shortcuts">
              <button type="button" className="mule-shortcut-featured"><ImageIcon /><span>Generate image</span><small>Vision 2</small></button>
              <button type="button"><Video /><span>Create video</span></button>
              <button type="button"><BarChart3 /><span>Analyze data</span></button>
              <button type="button"><Globe2 /><span>Build website</span></button>
              <button type="button"><ShoppingBag /><span>Storefront</span></button>
              <button type="button"><Gamepad2 /><span>Prototype</span></button>
            </div>

            <article className="mule-run-card">
              <header><div><Box /><span><strong>Research brief</strong><small>Workspace agent</small></span></div><b>In progress</b></header>
              <div className="mule-run-steps">
                <span className="done"><i>✓</i><b>Collect sources</b><small>8 references</small></span>
                <span className="active"><i>2</i><b>Build outline</b><small>Working now</small></span>
                <span><i>3</i><b>Review tone</b><small>Up next</small></span>
              </div>
            </article>
          </section>
        </main>
      </div>
    </div>
  )
}
