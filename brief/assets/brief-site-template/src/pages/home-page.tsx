import type React from 'react'
import { MotionLink } from '@/components/motion-link'
import { ReportCard } from '@/components/reports/report-card'
import { ThemeToggle } from '@/components/theme-toggle'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { reports, reportTags } from '@/content/reports'
import type { Theme } from '@/lib/theme'

type HomePageProps = {
  theme: Theme
  onThemeChange: (theme: Theme) => void
}

function HomePage({ theme, onThemeChange }: HomePageProps) {
  const featuredReport = reports.find((report) => report.featured) ?? reports[0]
  const remainingReports = reports.filter((report) => report.slug !== featuredReport.slug)
  const topicTags = reportTags.filter((tag) => tag.value !== 'all')

  return (
    <Tabs className="home-shell min-h-screen bg-[var(--background)]" defaultValue="front">
      <main className="min-h-screen">
        <header className="site-masthead">
          <div className="site-title-row">
            <div className="site-title" aria-label="Brief">
              Brief
            </div>
            <div className="site-actions">
              <TabsList className="home-tabs" aria-label="首页视图">
                <TabsTrigger value="front">Edition</TabsTrigger>
                <TabsTrigger value="archive">Archive</TabsTrigger>
                <TabsTrigger value="tags">Tags</TabsTrigger>
              </TabsList>
              <ThemeToggle onThemeChange={onThemeChange} theme={theme} />
            </div>
          </div>
        </header>

        <section className="front-page">
          <TabsContent className="home-panel" value="front">
            <div className="front-page__stack">
              <section className="front-hero" style={{ '--item-index': 0 } as React.CSSProperties}>
                <aside className="front-hero__folio" aria-hidden="true">
                  <span>Lead</span>
                </aside>
                <MotionLink className="front-hero__main" to={`/reports/${featuredReport.slug}`}>
                  <span className="front-hero__meta">
                    {featuredReport.publishedAt} / {featuredReport.readingTime}
                  </span>
                  <h1>{featuredReport.title}</h1>
                  <p className="front-hero__deck">{featuredReport.deck}</p>
                </MotionLink>

                <aside className="front-hero__commentary" aria-label="Brief Commentary">
                  <span>Commentary</span>
                  <p>{featuredReport.commentary}</p>
                </aside>
              </section>
              <div className="front-page__below" aria-label="近期简报">
                {remainingReports.map((report, index) => (
                  <ReportCard index={index + 1} key={report.slug} report={report} variant="archive" />
                ))}
              </div>
            </div>
          </TabsContent>

          <TabsContent className="home-panel" value="archive">
            <section className="brief-index" aria-label="全部报告">
              <div className="brief-index__head">
                <span>Archive</span>
                <span>{reports.length} 篇</span>
              </div>

              {reports.map((report, index) => (
                <MotionLink
                  className="brief-index__row"
                  key={report.slug}
                  style={{ '--item-index': index } as React.CSSProperties}
                  to={`/reports/${report.slug}`}
                >
                  <span className="brief-index__date">{report.publishedAt}</span>
                  <span className="brief-index__title">{report.title}</span>
                  <span className="brief-index__deck">{report.deck}</span>
                  <span className="brief-index__time">{report.readingTime}</span>
                </MotionLink>
              ))}
            </section>
          </TabsContent>

          <TabsContent className="home-panel" value="tags">
            <section className="tag-board" aria-label="按标签浏览">
              {topicTags.map((tag, tagIndex) => {
                const filteredReports = reports.filter((report) => report.tags.includes(tag.value))

                return (
                  <article
                    className="tag-section"
                    key={tag.value}
                    style={{ '--item-index': tagIndex } as React.CSSProperties}
                  >
                    <header className="tag-section__head">
                      <h2>{tag.label}</h2>
                      <span>{filteredReports.length} 篇</span>
                    </header>

                    <div className="tag-section__list">
                      {filteredReports.map((report) => (
                        <MotionLink className="tag-report" key={report.slug} to={`/reports/${report.slug}`}>
                          <span className="tag-report__date">{report.publishedAt}</span>
                          <span className="tag-report__title">{report.title}</span>
                          <span className="tag-report__line">{report.keyFindings[0]}</span>
                        </MotionLink>
                      ))}
                    </div>
                  </article>
                )
              })}
            </section>
          </TabsContent>
        </section>
      </main>
    </Tabs>
  )
}

export { HomePage }
