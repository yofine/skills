import type React from 'react'
import { MotionLink } from '@/components/motion-link'
import type { Report } from '@/content/reports'
import { cn } from '@/lib/utils'

type ReportCardProps = {
  report: Report
  index?: number
  variant?: 'feature' | 'archive' | 'rail'
}

function ReportCard({ index = 0, report, variant = 'archive' }: ReportCardProps) {
  const isFeature = variant === 'feature'

  return (
    <article
      className={cn('story', {
        'story--lead': variant === 'feature',
        'story--archive': variant === 'archive',
        'story--rail': variant === 'rail',
      })}
      style={{ '--item-index': index } as React.CSSProperties}
    >
      <MotionLink className="story__link" to={`/reports/${report.slug}`}>
        <div className="story__content">
          <div>
            <div className="story__meta">
              <span>
                {report.publishedAt} / {report.readingTime}
              </span>
            </div>
            <h2
              className={cn('story__title', {
                'story__title--lead': isFeature,
                'story__title--rail': variant === 'rail',
              })}
            >
              {report.title}
            </h2>
            <p
              className={cn('story__deck', {
                'story__deck--lead': isFeature,
                'story__deck--rail': variant === 'rail',
              })}
            >
              {report.deck}
            </p>

            {isFeature && (
              <div className="story__brief">
                <aside className="story__commentary" aria-label="Brief Commentary">
                  <span>Commentary</span>
                  <p className="story__summary">{report.commentary}</p>
                </aside>
              </div>
            )}
          </div>
        </div>
      </MotionLink>
    </article>
  )
}

export { ReportCard }
