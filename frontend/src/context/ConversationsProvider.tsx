import { useCallback, useEffect, useMemo, useState, type ReactNode } from 'react'
import { errorMessage } from '../api/client'
import * as conversationsApi from '../api/conversationsApi'
import type { Conversation } from '../types/chat'
import { ConversationsContext } from './ConversationsContext'

function byLastActivity(first: Conversation, second: Conversation): number {
  return second.updated_at.localeCompare(first.updated_at)
}

export function ConversationsProvider({ children }: { children: ReactNode }) {
  const [conversations, setConversations] = useState<Conversation[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const controller = new AbortController()
    conversationsApi
      .fetchConversations(controller.signal)
      .then(setConversations)
      .catch((caught: unknown) => {
        if (!controller.signal.aborted) {
          setError(errorMessage(caught))
        }
      })
      .finally(() => {
        if (!controller.signal.aborted) {
          setIsLoading(false)
        }
      })
    return () => controller.abort()
  }, [])

  const saveConversation = useCallback((conversation: Conversation) => {
    setConversations((current) =>
      [conversation, ...current.filter((item) => item.id !== conversation.id)].sort(byLastActivity),
    )
  }, [])

  const renameConversation = useCallback(
    async (conversationId: string, title: string) => {
      saveConversation(await conversationsApi.renameConversation(conversationId, title))
    },
    [saveConversation],
  )

  const deleteConversation = useCallback(async (conversationId: string) => {
    await conversationsApi.deleteConversation(conversationId)
    setConversations((current) => current.filter((item) => item.id !== conversationId))
  }, [])

  const value = useMemo(
    () => ({
      conversations,
      isLoading,
      error,
      saveConversation,
      renameConversation,
      deleteConversation,
    }),
    [conversations, isLoading, error, saveConversation, renameConversation, deleteConversation],
  )

  return <ConversationsContext value={value}>{children}</ConversationsContext>
}
