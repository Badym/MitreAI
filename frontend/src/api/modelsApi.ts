import type { ModelOption } from '../types/chat'
import { apiRequest } from './client'

export function fetchModels(signal?: AbortSignal): Promise<ModelOption[]> {
  return apiRequest<ModelOption[]>('/models', { signal })
}
