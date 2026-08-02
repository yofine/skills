import type { CSSProperties } from 'react'
import type { DesignSystemEntry } from '../data/types'
import './qoderwork.css'

type QoderWorkMock = Extract<DesignSystemEntry['mock'], { layout: 'agent-workbench' }>

export default function QoderWorkMock({ entry }: { entry: DesignSystemEntry }) {
  const mock = entry.mock as QoderWorkMock
  const accent = entry.tokens.find((section) => section.id === 'accent')?.tokens[0]?.value ?? entry.primaryColor
  const style = { '--mock-accent': accent } as CSSProperties

  return (
    <div className="live-window qoder-window" style={style}>
      <div className="qoder-shell">
        <aside className="qoder-sidebar" aria-label="QoderWork navigation">
          <div className="qoder-sidebar-top">
            <span className="qoder-traffic" aria-hidden="true"><i /><i /><i /></span>
            <span className="qoder-window-tools" aria-hidden="true">⌕&nbsp;&nbsp;▯</span>
          </div>
          <nav className="qoder-primary-nav">
            {mock.primaryNav.map((item) => <span key={item.label}><b>{item.icon}</b>{item.label}</span>)}
          </nav>
          <div className="qoder-segment" aria-label="Workspace view">
            {mock.utilityNav.map((item, index) => <span className={index === 0 ? 'active' : ''} key={item.label}><b>{item.icon}</b>{item.label}</span>)}
          </div>
          <div className="qoder-history">
            {mock.navGroups.map((group) => (
              <section key={group.label}>
                <strong>{group.label}</strong>
                {group.items.map((item) => <span className={item === mock.activeTask ? 'active' : ''} key={item}>{item}</span>)}
              </section>
            ))}
          </div>
          <footer className="qoder-profile"><b>{mock.profileName.slice(0, 1).toUpperCase()}</b><span><strong>{mock.profileName}</strong><small>体验版</small></span><i>⚙</i></footer>
        </aside>

        <main className="qoder-task">
          <header className="qoder-task-header"><strong>{mock.threadTitle}</strong><nav><span>▣ 问题反馈</span><span>⌘</span><span>◌</span></nav></header>
          <section className="qoder-thread">
            <div className="qoder-response-copy"><span>分析完成，关键结果已整理为可审阅的技术报告。</span><small>查看分析报告</small></div>
            <article className="qoder-artifact">
              <header><span className="qoder-file-icon">5</span><strong>{mock.artifact.name}</strong><b>···</b></header>
              <div className="qoder-preview">
                <div className="qoder-preview-title"><span>{mock.artifact.previewTitle}</span><i /></div>
                <small>核心指标概览</small>
                <div className="qoder-preview-stats">
                  {mock.artifact.previewStats.map((stat, index) => <span key={`${stat}-${index}`}><b>{stat}</b><small>{['SWE verified', 'SWE Pro', '视觉推理', '美元 / 1M'][index] ?? 'metric'}</small></span>)}
                </div>
                <div className="qoder-preview-lines"><i /><i /><i /></div>
              </div>
              <footer>此为预览，点击查看详情。</footer>
            </article>
          </section>
          <footer className="qoder-composer">
            <span>{mock.composerPlaceholder}</span>
            <div><nav><button type="button">＋</button><button type="button">♧</button></nav><nav><small>♧ 增强</small><i className="qoder-live-dot" /><button className="qoder-mic" type="button">♩</button><button className="qoder-send" type="button">↑</button></nav></div>
          </footer>
        </main>

        <aside className="qoder-monitor" aria-label={mock.monitorTitle}>
          <header><strong>{mock.monitorTitle}</strong><span>▣</span></header>
          <section>
            <div className="qoder-monitor-title"><strong>待办</strong><span>⌄</span></div>
            <ul>{mock.checklist.map((item) => <li key={item}><b>✓</b><span>{item}</span></li>)}</ul>
          </section>
          <section>
            <div className="qoder-monitor-title"><strong>产物</strong><span>⌄</span></div>
            <small>默认工作目录</small>
            <span className="qoder-monitor-item"><b>5</b>{mock.monitorArtifact}</span>
          </section>
          <section>
            <div className="qoder-monitor-title"><strong>技能与 MCP</strong><span>⌄</span></div>
            <span className="qoder-monitor-item"><b>⌁</b>{mock.monitorSkill}</span>
          </section>
        </aside>
      </div>
    </div>
  )
}
