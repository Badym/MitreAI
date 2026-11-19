import { readToken } from './tokenStorage'

const API_BASE_URL = '/api'

export const UNAUTHORIZED_EVENT = 'mitreai:unauthorized'

export class ApiError extends Error {
  readonly status: number

  constructor(status: number, message: string) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

interface RequestOptions {
  method?: 'GET' | 'POST' | 'PATCH' | 'DELETE'
  body?: BodyInit
  json?: unknown
  signal?: AbortSignal
}

export async function apiRequest<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { method = 'GET', json, signal } = options
  const headers = new Headers({ Accept: 'application/json' })
  const token = readToken()
  if (token) {
    headers.set('Authorization', `Bearer ${token}`)
  }
  if (json !== undefined) {
    headers.set('Content-Type', 'application/json')
  }
  const body = json === undefined ? options.body : JSON.stringify(json)

  const response = await fetch(`${API_BASE_URL}${path}`, { method, headers, body, signal })

  if (response.status === 401 && token) {
    window.dispatchEvent(new Event(UNAUTHORIZED_EVENT))
  }
  if (!response.ok) {
    throw new ApiError(response.status, await readErrorMessage(response))
  }
  if (response.status === 204) {
    return undefined as T
  }
  return (await response.json()) as T
}

export function errorMessage(error: unknown): string {
  return error instanceof ApiError ? error.message : 'Brak połączenia z serwerem'
}

async function readErrorMessage(response: Response): Promise<string> {
  const data: unknown = await response.json().catch(() => null)
  if (hasDetailMessage(data)) {
    return data.detail
  }
  return `Serwer zwrócił błąd ${response.status}`
}

function hasDetailMessage(data: unknown): data is { detail: string } {
  return (
    typeof data === 'object' &&
    data !== null &&
    typeof (data as { detail?: unknown }).detail === 'string'
  )
}
