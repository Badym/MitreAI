export type UserRole = 'admin' | 'user'

export interface CurrentUser {
  id: string
  email: string
  display_name: string
  role: UserRole
  is_active: boolean
  created_at: string
  last_login_at: string | null
}

export interface TokenResponse {
  access_token: string
  token_type: 'bearer'
}
