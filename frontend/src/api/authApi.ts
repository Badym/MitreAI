import type { CurrentUser, TokenResponse } from '../types/auth'
import { apiRequest } from './client'

export function requestToken(email: string, password: string): Promise<TokenResponse> {
  const body = new URLSearchParams({ username: email, password })
  return apiRequest<TokenResponse>('/auth/login', { method: 'POST', body })
}

export function fetchCurrentUser(signal?: AbortSignal): Promise<CurrentUser> {
  return apiRequest<CurrentUser>('/auth/me', { signal })
}
