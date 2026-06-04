import { Loader2 } from 'lucide-react'
import { useEffect, useLayoutEffect, useMemo, useRef, useState } from 'react'
import type { Report } from '@/content/reports'
import type { Theme } from '@/lib/theme'

type LoadState =
  | { status: 'loading'; html: string | null; error: null }
  | { status: 'ready'; html: string; error: null }
  | { status: 'error'; html: null; error: string }

type ReportFrameProps = {
  report: Report
  theme: Theme
}

const reportThemeOverrides = `
  :root {
    background: var(--paper, #fbf6ed) !important;
    color-scheme: light;
    overscroll-behavior: none;
    scrollbar-width: none;
  }

  :root::-webkit-scrollbar,
  body::-webkit-scrollbar {
    display: none;
    height: 0;
    width: 0;
  }

  :root,
  body {
    min-height: 100%;
    scrollbar-width: none;
  }

  body {
    background: var(--paper, #fbf6ed) !important;
    overscroll-behavior: none;
  }

  main {
    background: var(--paper, #fbf6ed) !important;
    min-height: 100vh;
  }

  :root[data-brief-theme="dark"] {
    color-scheme: dark;
    --ink: #f4efe6;
    --muted: #c9bdad;
    --line: #4d443b;
    --paper: #151412;
    --wash: #24211d;
    --wash-strong: #2c2822;
    --subtle: #9d8f80;
    --accent: #d69b72;
    --gold: #c3a45d;
  }

  :root[data-brief-theme="dark"],
  :root[data-brief-theme="dark"] body {
    background: var(--paper) !important;
    color: var(--ink) !important;
  }

  :root[data-brief-theme="dark"] p,
  :root[data-brief-theme="dark"] li,
  :root[data-brief-theme="dark"] td,
  :root[data-brief-theme="dark"] .meta,
  :root[data-brief-theme="dark"] .deck {
    color: var(--muted) !important;
  }

  :root[data-brief-theme="dark"] .tile,
  :root[data-brief-theme="dark"] .panel,
  :root[data-brief-theme="dark"] .box {
    background: var(--wash) !important;
    border-color: var(--line) !important;
  }
`

function injectReportDocument(html: string, docSrc: string, theme: Theme) {
  const documentUrl = new URL(docSrc, window.location.origin)
  const documentBase = documentUrl.href.slice(0, documentUrl.href.lastIndexOf('/') + 1)
  const parsed = new DOMParser().parseFromString(html, 'text/html')
  parsed.documentElement.dataset.briefTheme = theme

  const existingBase = parsed.head.querySelector('base')
  const base = existingBase ?? parsed.createElement('base')

  base.setAttribute('href', documentBase)

  if (!existingBase) {
    parsed.head.prepend(base)
  }

  const themeStyle = parsed.createElement('style')
  themeStyle.setAttribute('data-brief-theme-overrides', 'true')
  themeStyle.textContent = reportThemeOverrides
  parsed.head.append(themeStyle)

  return `<!doctype html>\n${parsed.documentElement.outerHTML}`
}

function getReportRequestUrl(docSrc: string) {
  if (!import.meta.env.DEV) {
    return docSrc
  }

  const separator = docSrc.includes('?') ? '&' : '?'

  return `${docSrc}${separator}brief-cache=${Date.now()}`
}

function ReportFrame({ report, theme }: ReportFrameProps) {
  const iframeRef = useRef<HTMLIFrameElement>(null)
  const themeRef = useRef(theme)
  const [loadState, setLoadState] = useState<LoadState>({
    status: 'loading',
    html: null,
    error: null,
  })

  useEffect(() => {
    themeRef.current = theme
  }, [theme])

  useEffect(() => {
    let cancelled = false

    async function loadReport() {
      setLoadState({ status: 'loading', html: null, error: null })

      try {
        const response = await fetch(getReportRequestUrl(report.docSrc), { cache: 'no-store' })

        if (!response.ok) {
          throw new Error(`Unable to load ${report.docSrc}: ${response.status}`)
        }

        const html = injectReportDocument(await response.text(), report.docSrc, themeRef.current)

        if (!cancelled) {
          setLoadState({ status: 'ready', html, error: null })
        }
      } catch (error) {
        if (!cancelled) {
          setLoadState({
            status: 'error',
            html: null,
            error: error instanceof Error ? error.message : 'Unknown loading error',
          })
        }
      }
    }

    loadReport()

    return () => {
      cancelled = true
    }
  }, [report.docSrc])

  useLayoutEffect(() => {
    const iframeDocument = iframeRef.current?.contentDocument

    if (iframeDocument?.documentElement) {
      iframeDocument.documentElement.dataset.briefTheme = theme
    }
  }, [theme, loadState.status])

  const iframeAttributes = useMemo(() => ({ 'doc-src': report.docSrc }), [report.docSrc])

  return (
    <section className="report-frame-shell" aria-label={`${report.title} report document`}>
      {loadState.status === 'loading' && (
        <div className="report-frame-state">
          <Loader2 className="size-5 animate-spin" />
          Loading standalone HTML report
        </div>
      )}

      {loadState.status === 'error' && (
        <div className="report-frame-state report-frame-state--error">
          <p>{loadState.error}</p>
        </div>
      )}

      {loadState.status === 'ready' && (
        <iframe
          {...iframeAttributes}
          className="report-frame"
          ref={iframeRef}
          sandbox="allow-same-origin"
          srcDoc={loadState.html}
          title={`${report.title} HTML report`}
        />
      )}
    </section>
  )
}

export { ReportFrame }
