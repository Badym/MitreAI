import type { Conversation } from '../types/chat'
import { apiRequest } from './client'

function conversationPath(conversationId: string): string {
  return `/conversations/${encodeURIComponent(conversationId)}`
}

export function fetchConversations(signal?: AbortSignal): Promise<Conversation[]> {
  return apiRequest<Conversation[]>('/conversations', { signal })
}

export function fetchConversation(conversationId: string, signal?: AbortSignal): Promise<Conversation> {
  return apiRequest<Conversation>(conversationPath(conversationId), { signal })
}

export function createConversation(model: string | null): Promise<Conversation> {
  return apiRequest<Conversation>('/conversations', { method: 'POST', json: { model } })
}

export function renameConversation(conversationId: string, title: string): Promise<Conversation> {
  return apiRequest<Conversation>(conversationPath(conversationId), {
    method: 'PATCH',
    json: { title },
  })
}

export function deleteConversation(conversationId: string): Promise<void> {
  return apiRequest<void>(conversationPath(conversationId), { method: 'DELETE' })
}
