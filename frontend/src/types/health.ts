export interface HealthResponse {
  status: 'ok' | 'error'
  database: 'ok' | 'unavailable'
}
