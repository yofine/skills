import { type MouseEvent } from 'react'
import { flushSync } from 'react-dom'
import { Link, type LinkProps, useNavigate } from 'react-router-dom'

function MotionLink({ onClick, replace, state, target, to, ...props }: LinkProps) {
  const navigate = useNavigate()

  function handleClick(event: MouseEvent<HTMLAnchorElement>) {
    onClick?.(event)

    if (
      event.defaultPrevented ||
      event.button !== 0 ||
      event.metaKey ||
      event.altKey ||
      event.ctrlKey ||
      event.shiftKey ||
      target ||
      !document.startViewTransition
    ) {
      return
    }

    event.preventDefault()
    document.documentElement.dataset.pageTransition = 'route'

    const transition = document.startViewTransition(() => {
      flushSync(() => {
        navigate(to, { replace, state })
      })
    })

    transition.finished.finally(() => {
      delete document.documentElement.dataset.pageTransition
    })
  }

  return <Link {...props} onClick={handleClick} replace={replace} state={state} target={target} to={to} />
}

export { MotionLink }
