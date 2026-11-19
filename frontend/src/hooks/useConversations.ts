import { useContext } from 'react'
import {
  ConversationsContext,
  type ConversationsContextValue,
} from '../context/ConversationsContext'

export function useConversations(): ConversationsContextValue {
  const context = useContext(ConversationsContext)
  if (context === null) {
    throw new Error('useConversations musi być użyty wewnątrz ConversationsProvider')
  }
  return context
}
