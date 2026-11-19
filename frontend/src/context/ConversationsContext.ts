import { createContext } from 'react'
import type { Conversation } from '../types/chat'

export interface ConversationsContextValue {
  conversations: Conversation[]
  isLoading: boolean
  error: string | null
  saveConversation: (conversation: Conversation) => void
  renameConversation: (conversationId: string, title: string) => Promise<void>
  deleteConversation: (conversationId: string) => Promise<void>
}

export const ConversationsContext = createContext<ConversationsContextValue | null>(null)
