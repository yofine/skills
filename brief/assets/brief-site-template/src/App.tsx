import { useEffect, useRef, useState } from 'react'
import { flushSync } from 'react-dom'
import { Navigate, Route, Routes } from 'react-router-dom'
import { HomePage } from '@/pages/home-page'
import { ReportPage } from '@/pages/report-page'
import type { Theme } from '@/lib/theme'

function getInitialTheme(): Theme {
  const storedTheme = window.localStorage.getItem('brief-theme')

  if (storedTheme === 'light' || storedTheme === 'dark') {
    return storedTheme
  }

  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
}

function App() {
  const [theme, setTheme] = useState<Theme>(getInitialTheme)
  const activeTransitionRef = useRef<ViewTransition | null>(null)

  function handleThemeChange(nextTheme: Theme) {
    const applyTheme = () => {
      document.documentElement.dataset.theme = nextTheme
      document.documentElement.style.colorScheme = nextTheme
      window.localStorage.setItem('brief-theme', nextTheme)

      flushSync(() => {
        setTheme(nextTheme)
      })
    }

    if (!document.startViewTransition) {
      applyTheme()
      return
    }

    document.documentElement.dataset.themeTransition = nextTheme
    activeTransitionRef.current?.skipTransition()

    const transition = document.startViewTransition(applyTheme)
    activeTransitionRef.current = transition

    transition.finished.finally(() => {
      if (activeTransitionRef.current === transition) {
        delete document.documentElement.dataset.themeTransition
        activeTransitionRef.current = null
      }
    })
  }

  useEffect(() => {
    document.documentElement.dataset.theme = theme
    document.documentElement.style.colorScheme = theme
    window.localStorage.setItem('brief-theme', theme)
  }, [theme])

  return (
    <Routes>
      <Route path="/" element={<HomePage onThemeChange={handleThemeChange} theme={theme} />} />
      <Route
        path="/reports/:slug"
        element={<ReportPage onThemeChange={handleThemeChange} theme={theme} />}
      />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

export default App
