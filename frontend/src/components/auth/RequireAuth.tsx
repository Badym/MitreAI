import type { ReactNode } from 'react'
import { Navigate } from 'react-router'
import { useAuth } from '../../hooks/useAuth'

export function RequireAuth({ children }: { children: ReactNode }) {
  const { user, isLoading } = useAuth()

  if (isLoading) {
    return null
  }
  if (user === null) {
    return <Navigate to="/login" replace />
  }
  return children
}
