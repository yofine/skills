import { Moon, Sun } from 'lucide-react'
import type { MouseEvent } from 'react'
import { getNextTheme, type Theme } from '@/lib/theme'

type ThemeToggleProps = {
  theme: Theme
  onThemeChange: (theme: Theme) => void
}

function ThemeToggle({ theme, onThemeChange }: ThemeToggleProps) {
  const nextTheme = getNextTheme(theme)

  function handleClick(event: MouseEvent<HTMLButtonElement>) {
    const rect = event.currentTarget.getBoundingClientRect()
    const x = rect.left + rect.width / 2
    const y = rect.top + rect.height / 2

    document.documentElement.style.setProperty('--theme-x', `${x}px`)
    document.documentElement.style.setProperty('--theme-y', `${y}px`)
    onThemeChange(nextTheme)
  }

  return (
    <button
      aria-label={`Switch to ${nextTheme} mode`}
      className="theme-toggle"
      data-theme={theme}
      onClick={handleClick}
      title={`Switch to ${nextTheme} mode`}
      type="button"
    >
      <Sun className="theme-toggle__sun" />
      <Moon className="theme-toggle__moon" />
    </button>
  )
}

export { ThemeToggle }
