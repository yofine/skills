import type { DesignSystemEntry } from './types.ts'
import { mulerun } from './mulerun.ts'
import { raft } from './raft.ts'
import { qoderwork } from './qoderwork.ts'
import { superset } from './superset.ts'

export const registry: DesignSystemEntry[] = [mulerun, raft, qoderwork, superset]

export function findDesignSystem(slug: string) {
  return registry.find((entry) => entry.slug === slug)
}
