import type { SVGProps } from 'react'
import type { DesignSystemEntry } from '../data/types'
import './raft.css'

type IconName = 'search' | 'chat' | 'pulse' | 'task' | 'team' | 'screen' | 'bookmark' | 'chevron' | 'sort' | 'plus' | 'image' | 'paperclip' | 'bell' | 'help' | 'settings' | 'send'

function Icon({ name, ...props }: { name: IconName } & SVGProps<SVGSVGElement>) {
  const paths: Record<IconName, React.ReactNode> = {
    search: <><circle cx="11" cy="11" r="6" /><path d="m16 16 4 4" /></>,
    chat: <path d="M4 5.5h16v12H9l-5 3v-15Z" />,
    pulse: <path d="M3 12h4l2.2-6 4.1 12 2.1-6H21" />,
    task: <><rect x="4" y="4" width="16" height="16" rx="1" /><path d="m8 12 2.5 2.5L16 9" /></>,
    team: <><circle cx="9" cy="9" r="3" /><circle cx="17" cy="10" r="2.3" /><path d="M3.5 20c.4-4 2.1-6 5.5-6s5.1 2 5.5 6M14 15c3.7-.4 5.7 1.3 6.3 4.4" /></>,
    screen: <><rect x="3.5" y="5" width="17" height="12" rx="1" /><path d="M9 21h6M12 17v4" /></>,
    bookmark: <path d="M7 4.5h10v16l-5-3.2-5 3.2v-16Z" />,
    chevron: <path d="m8 10 4 4 4-4" />,
    sort: <path d="M8 4v16m0-16L5 7m3-3 3 3m5 13V4m0 16-3-3m3 3 3-3" />,
    plus: <path d="M12 5v14M5 12h14" />,
    image: <><rect x="3.5" y="4.5" width="17" height="15" rx="1" /><circle cx="9" cy="9" r="1.5" /><path d="m5 17 4.5-4.5 3 3 2.5-2.5 4 4" /></>,
    paperclip: <path d="m8 12 6.7-6.7a3 3 0 1 1 4.2 4.2L10 18.4a4 4 0 0 1-5.7-5.7l8.3-8.3" />,
    bell: <><path d="M5 17h14l-1.6-2.2V10a5.4 5.4 0 0 0-10.8 0v4.8L5 17Z" /><path d="M10 20h4" /></>,
    help: <><circle cx="12" cy="12" r="9" /><path d="M9.7 9a2.5 2.5 0 1 1 3.1 2.4c-.8.3-.8.9-.8 1.6M12 17h.01" /></>,
    settings: <><circle cx="12" cy="12" r="3" /><path d="M12 3v2m0 14v2M3 12h2m14 0h2M5.6 5.6 7 7m10 10 1.4 1.4M18.4 5.6 17 7M7 17l-1.4 1.4" /></>,
    send: <path d="m4 4 16 8-16 8 3-8-3-8Zm3 8h13" />,
  }
  return <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="square" strokeLinejoin="miter" aria-hidden="true" {...props}>{paths[name]}</svg>
}

export default function RaftMock({ entry }: { entry: DesignSystemEntry }) {
  const mock = entry.mock.layout === 'collaboration-shell' ? entry.mock : null
  if (!mock) return null
  return (
    <div className="live-window raft2-window">
      <div className="raft2-shell">
        <aside className="raft2-rail">
          <strong>R</strong>
          <nav><Icon name="search" /><span className="active"><Icon name="chat" /></span><Icon name="pulse" /><Icon name="task" /><Icon name="team" /><Icon name="screen" /></nav>
          <footer><Icon name="bell" /><Icon name="help" /><Icon name="settings" /></footer>
        </aside>
        <aside className="raft2-sidebar">
          <header><strong>{mock.workspaceName}</strong></header>
          <div className="raft2-saved"><Icon name="bookmark" /> Saved</div>
          <section><header><span><Icon name="chevron" /> Pinned <small>0</small></span></header><p>Drag channels or DMs here to pin</p></section>
          <section><header><span><Icon name="chevron" /> Joint channels <small>0</small></span><i><Icon name="sort" /><Icon name="plus" /></i></header><p>No joint channels yet</p></section>
          <section><header><span><Icon name="chevron" /> Channels <small>1</small></span><i><Icon name="sort" /><Icon name="plus" /></i></header><b className="selected">#&nbsp;&nbsp;all</b></section>
          <section><header><span><Icon name="chevron" /> Direct messages <small>0</small></span><i><Icon name="sort" /><Icon name="plus" /></i></header></section>
        </aside>
        <main className="raft2-main">
          <header className="raft2-channel"><b>#</b><div><strong>{mock.activeChannel}</strong><small>{mock.channelDescription}</small></div><nav><span><Icon name="search" /></span><span><Icon name="bell" /></span><span><Icon name="task" /></span><span><Icon name="settings" /></span><span className="members"><Icon name="team" /> 1</span></nav></header>
          <nav className="raft2-tabs"><span className="active"><Icon name="chat" /> Chat</span><span><Icon name="task" /> Tasks</span><span><Icon name="paperclip" /> Files</span></nav>
          <section className="raft2-empty"><Icon name="chat" /><strong>{mock.emptyTitle}</strong><p>{mock.emptyBody}</p></section>
          <footer className="raft2-compose-wrap">
            <div className="raft2-composer"><span>{mock.composerPlaceholder}</span><nav><button><Icon name="image" /></button><button><Icon name="paperclip" /></button><label><i /> As Task</label><button className="send"><Icon name="send" /></button></nav></div>
            <div className="raft2-notice"><Icon name="bell" /><span><strong>Your agents keep working after you leave.</strong><small>Turn on notifications so you don’t miss when they finish or need you.</small></span><button>Enable notifications</button><b>×</b></div>
          </footer>
        </main>
      </div>
    </div>
  )
}
