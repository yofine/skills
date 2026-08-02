export type Token = {
  name: string
  value: string
  fallback?: string
  usage: string
}

export type TokenSection = {
  id: 'neutral' | 'text' | 'accent' | 'typography' | 'foundation'
  title: string
  description: string
  tokens: Token[]
}

export type DnaPillar = {
  name: string
  belief: string
  implication: string
}

export type ComponentRecipe = {
  name: string
  summary: string
  anatomy: string[]
  states: string[]
  tokenNotes: string[]
}

export type LayoutPattern = {
  name: string
  description: string
  grid: string
  responsive: string
}

export type InteractionRule = {
  trigger: string
  response: string
  accessibility: string
}

export type Guideline = {
  topic: string
  do: string
  dont: string
}

export type MockConfig =
  | {
      layout: 'sidebar-content'
      productName: string
      navItems: string[]
      activeItem: string
      eyebrow: string
      heading: string
      body: string
      metric: string
      metricLabel: string
    }
  | {
      layout: 'full-viewport-scroll'
      productName: string
      eyebrow: string
      heading: string
      body: string
      sections: string[]
      cta: string
    }
  | {
      layout: 'collaboration-shell'
      productName: string
      workspaceName: string
      railItems: string[]
      sections: Array<{ label: string; items: string[] }>
      activeChannel: string
      channelDescription: string
      tabs: string[]
      activeTab: string
      emptyTitle: string
      emptyBody: string
      composerPlaceholder: string
      notice: string
    }
  | {
      layout: 'agent-workbench'
      productName: string
      primaryNav: Array<{ label: string; icon: string }>
      utilityNav: Array<{ label: string; icon: string }>
      navGroups: Array<{ label: string; items: string[] }>
      activeTask: string
      threadTitle: string
      artifact: {
        name: string
        previewTitle: string
        previewStats: string[]
      }
      composerPlaceholder: string
      monitorTitle: string
      checklist: string[]
      monitorArtifact: string
      monitorSkill: string
      profileName: string
    }
  | {
      layout: 'system-specific'
      composition: string
      data: Record<string, unknown>
    }

export type Convention = { key: string; rule: string }
export type PresetMapping = { variable: string; token: string }

export type Iconography = {
  description: string
  size: string
  stroke: string
  style: string
  icons: Array<{ name: string; label: string; paths: string[] }>
}

export type DesignSystemEntry = {
  slug: string
  name: string
  version: string
  tagline: string
  description: string
  style: string
  platform: string
  primaryColor: string
  onPrimaryColor: string
  palette: Token[]
  dna: DnaPillar[]
  tokens: TokenSection[]
  iconography: Iconography
  mock: MockConfig
  components: ComponentRecipe[]
  layoutPatterns: LayoutPattern[]
  layoutNote: string
  interactions: InteractionRule[]
  guidelines: Guideline[]
  tokenExport: string
  conventions: Convention[]
  presetMappings: PresetMapping[]
}
