import { useCallback, useEffect, useMemo, useState, type ReactNode } from 'react'
import { fetchCurrentUser, requestToken } from '../api/authApi'
import { UNAUTHORIZED_EVENT } from '../api/client'
import { clearToken, readToken, saveToken } from '../api/tokenStorage'
import type { CurrentUser } from '../types/auth'
import { AuthContext } from './AuthContext'

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<CurrentUser | null>(null)
  const [isLoading, setIsLoading] = useState(() => readToken() !== null)

  useEffect(() => {
    if (readToken() === null) {
      return
    }

    const controller = new AbortController()
    fetchCurrentUser(controller.signal)
      .then(setUser)
      .catch(() => {
        if (!controller.signal.aborted) {
          clearToken()
        }
      })
      .finally(() => {
        if (!controller.signal.aborted) {
          setIsLoading(false)
        }
      })

    return () => controller.abort()
  }, [])

  const login = useCallback(async (email: string, password: string) => {
    const { access_token } = await requestToken(email, password)
    saveToken(access_token)
    try {
      setUser(await fetchCurrentUser())
    } catch (error) {
      clearToken()
      throw error
    }
  }, [])

  const logout = useCallback(() => {
    clearToken()
    setUser(null)
  }, [])

  useEffect(() => {
    window.addEventListener(UNAUTHORIZED_EVENT, logout)
    return () => window.removeEventListener(UNAUTHORIZED_EVENT, logout)
  }, [logout])

  const value = useMemo(
    () => ({ user, isLoading, login, logout }),
    [user, isLoading, login, logout],
  )

  return <AuthContext value={value}>{children}</AuthContext>
}
