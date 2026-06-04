export type Theme = 'light' | 'dark'

export function getNextTheme(theme: Theme): Theme {
  return theme === 'light' ? 'dark' : 'light'
}
