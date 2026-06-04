import { ArrowLeft, CalendarDays, Clock, ExternalLink } from 'lucide-react'
import { useParams } from 'react-router-dom'
import { MotionLink } from '@/components/motion-link'
import { ReportFrame } from '@/components/reports/report-frame'
import { ThemeToggle } from '@/components/theme-toggle'
import { Separator } from '@/components/ui/separator'
import { getReportBySlug } from '@/content/reports'
import type { Theme } from '@/lib/theme'

type ReportPageProps = {
  theme: Theme
  onThemeChange: (theme: Theme) => void
}

function ReportPage({ theme, onThemeChange }: ReportPageProps) {
  const { slug } = useParams()
  const report = getReportBySlug(slug)

  if (!report) {
    return (
      <main className="not-found-page">
        <p className="section-eyebrow">Report not found</p>
        <h1>请求的报告不在登记表中。</h1>
        <MotionLink className="sidebar-link" to="/">
          <ArrowLeft />
          返回首页
        </MotionLink>
        <ThemeToggle onThemeChange={onThemeChange} theme={theme} />
      </main>
    )
  }

  const fileName = report.docSrc.split('/').at(-1) ?? report.docSrc

  return (
    <main className="report-page">
      <aside className="report-sidebar">
        <div className="report-sidebar__content">
          <div className="report-sidebar__top">
            <MotionLink className="sidebar-link" to="/">
              <ArrowLeft />
              全部报告
            </MotionLink>
            <ThemeToggle onThemeChange={onThemeChange} theme={theme} />
          </div>

          <h1 className="font-serif text-4xl leading-[1.02] text-[var(--foreground)] md:text-5xl">
            {report.title}
          </h1>
          <p className="mt-5 text-base leading-7 text-[var(--muted-foreground)]">{report.summary}</p>

          <div className="mt-8 grid gap-3 text-sm text-[var(--muted-foreground)]">
            <div className="report-fact">
              <CalendarDays className="size-4" />
              {report.publishedAt}
            </div>
            <div className="report-fact">
              <Clock className="size-4" />
              {report.readingTime}
            </div>
          </div>

          <Separator className="my-8" />

          <section>
            <h2 className="summary-heading">核心结论</h2>
            <ol className="mt-4 grid gap-4">
              {report.keyFindings.map((finding) => (
                <li className="finding-item" key={finding}>
                  {finding}
                </li>
              ))}
            </ol>
          </section>
        </div>

        <section className="document-panel">
          <p className="document-path">{fileName}</p>
          <a className="document-open" href={report.docSrc} rel="noreferrer" target="_blank">
            打开原文
            <ExternalLink />
          </a>
        </section>
      </aside>

      <ReportFrame report={report} theme={theme} />
    </main>
  )
}

export { ReportPage }
