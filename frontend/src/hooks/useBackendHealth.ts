import { useEffect, useState } from 'react'
import { ApiError } from '../api/client'
import { fetchHealth } from '../api/healthApi'

export type BackendStatus = 'checking' | 'online' | 'degraded' | 'offline'

export function useBackendHealth(): BackendStatus {
  const [status, setStatus] = useState<BackendStatus>('checking')

  useEffect(() => {
    const controller = new AbortController()

    fetchHealth(controller.signal)
      .then(() => setStatus('online'))
      .catch((error: unknown) => {
        if (controller.signal.aborted) {
          return
        }
        const databaseDown = error instanceof ApiError && error.status === 503
        setStatus(databaseDown ? 'degraded' : 'offline')
      })

    return () => controller.abort()
  }, [])

  return status
}
