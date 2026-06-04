import type { ComponentProps } from 'react'
import { cn } from '@/lib/utils'

function Badge({ className, ...props }: ComponentProps<'span'>) {
  return (
    <span
      className={cn(
        'inline-flex items-center border border-[var(--border)] bg-transparent px-2 py-0.5 text-[11px] font-medium uppercase tracking-[0.12em] text-[var(--muted-foreground)]',
        className,
      )}
      data-slot="badge"
      {...props}
    />
  )
}

export { Badge }
