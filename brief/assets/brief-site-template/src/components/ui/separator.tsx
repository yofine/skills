import type { ComponentProps } from 'react'
import { cn } from '@/lib/utils'

function Separator({ className, ...props }: ComponentProps<'div'>) {
  return (
    <div
      className={cn('h-px w-full bg-[var(--border)]', className)}
      data-slot="separator"
      role="separator"
      {...props}
    />
  )
}

export { Separator }
