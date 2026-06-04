export type ReportTag = {
  label: string
  value: string
}

export type Report = {
  slug: string
  title: string
  deck: string
  publishedAt: string
  readingTime: string
  docSrc: string
  sourceUrl: string
  featured?: boolean
  tags: string[]
  summary: string
  commentary: string
  watchlist: string[]
  keyFindings: string[]
}

export const reportTags: ReportTag[] = [
  { label: '全部', value: 'all' },
  { label: '架构', value: 'architecture' },
  { label: '长任务', value: 'long-running' },
  { label: '应用', value: 'apps' },
]

export const reports: Report[] = [
  {
    slug: 'harness-design-long-running-apps',
    title: '面向长运行应用的 Harness 架构',
    deck:
      '当 Agent 进入真实应用，harness 不再只是后台执行器，而要同时承担产品界面、执行控制、质量评价与长期状态管理。它的价值在于把长时间运行转化为用户可观察、可理解、可接管的交付过程。',
    publishedAt: '2026-03-24',
    readingTime: '10 分钟',
    docSrc: '/reports/harness-design-long-running-apps.html',
    sourceUrl: 'https://www.anthropic.com/engineering/harness-design-long-running-apps',
    featured: true,
    tags: ['long-running', 'apps'],
    summary:
      '这篇报告分析 Anthropic 对长运行应用 harness 的设计建议，重点是应用如何承接用户意图、代理执行、审计记录、权限控制和交付物状态。',
    commentary:
      '重点不在“让 Agent 跑更久”，而在把长期执行变成可审阅的产品过程。真正的门槛，是应用能否把计划、证据、动作和产物拆成稳定对象，并在关键节点让人理解它为什么继续、何时该停、哪里需要接管。',
    watchlist: ['评价器是否足够挑剔', '上下文重置后的交接质量', '用户接管节点是否自然'],
    keyFindings: [
      '长运行应用的 harness 不只是后台执行器，它也是用户理解进度、修正方向和接管风险的界面。',
      '应用需要把计划、证据、动作和产物拆成稳定对象，避免把所有状态埋在对话历史里。',
      '优秀 harness 会让 Agent 的连续工作可暂停、可解释、可恢复，并能在关键节点请求人工判断。',
    ],
  },
]

export function getReportBySlug(slug: string | undefined) {
  return reports.find((report) => report.slug === slug)
}
