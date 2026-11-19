import type { Message, SendMessageResult } from '../types/chat'
import { apiRequest } from './client'

function messagesPath(conversationId: string): string {
  return `/conversations/${encodeURIComponent(conversationId)}/messages`
}

export function fetchMessages(conversationId: string, signal?: AbortSignal): Promise<Message[]> {
  return apiRequest<Message[]>(messagesPath(conversationId), { signal })
}

export function sendMessage(
  conversationId: string,
  content: string,
  model: string | null,
): Promise<SendMessageResult> {
  const form = new FormData()
  form.append('content', content)
  if (model) {
    form.append('model', model)
  }
  return apiRequest<SendMessageResult>(messagesPath(conversationId), { method: 'POST', body: form })
}
