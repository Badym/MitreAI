import { useCallback, useEffect, useRef, useState } from 'react'
import { ApiError, errorMessage } from '../api/client'
import { createConversation, fetchConversation } from '../api/conversationsApi'
import { fetchMessages, sendMessage } from '../api/messagesApi'
import type { Conversation, DisplayMessage } from '../types/chat'
import { useConversations } from './useConversations'

export interface SendResult {
  ok: boolean
  conversationId: string | null
}

interface ChatState {
  conversationId: string | undefined
  conversation: Conversation | null
  messages: DisplayMessage[]
  notFound: boolean
  error: string | null
}

function emptyState(conversationId: string | undefined): ChatState {
  return { conversationId, conversation: null, messages: [], notFound: false, error: null }
}

export function useChat(conversationId: string | undefined) {
  const { saveConversation } = useConversations()
  const [state, setState] = useState<ChatState>(() => emptyState(undefined))
  const [isSending, setIsSending] = useState(false)
  const loadedConversationId = useRef<string | undefined>(undefined)

  useEffect(() => {
    if (conversationId === undefined || loadedConversationId.current === conversationId) {
      return
    }

    const controller = new AbortController()
    Promise.all([
      fetchConversation(conversationId, controller.signal),
      fetchMessages(conversationId, controller.signal),
    ])
      .then(([conversation, messages]) => {
        loadedConversationId.current = conversationId
        setState({ ...emptyState(conversationId), conversation, messages })
      })
      .catch((caught: unknown) => {
        if (controller.signal.aborted) {
          return
        }
        const notFound = caught instanceof ApiError && caught.status === 404
        setState({
          ...emptyState(conversationId),
          notFound,
          error: notFound ? null : errorMessage(caught),
        })
      })

    return () => controller.abort()
  }, [conversationId])

  const current = state.conversationId === conversationId ? state : null

  const send = useCallback(
    async (content: string, model: string | null): Promise<SendResult> => {
      const previousMessages = current?.messages ?? []
      const pending: DisplayMessage = { id: `pending-${Date.now()}`, role: 'user', content }
      let target = current?.conversation ?? null

      setIsSending(true)
      setState({
        ...emptyState(conversationId),
        conversation: target,
        messages: [...previousMessages, pending],
      })

      try {
        if (target === null) {
          target = await createConversation(model)
          saveConversation(target)
        }
        const result = await sendMessage(target.id, content, model)
        loadedConversationId.current = target.id
        setState({
          ...emptyState(target.id),
          conversation: result.conversation,
          messages: [...previousMessages, result.user_message, result.assistant_message],
        })
        saveConversation(result.conversation)
        return { ok: true, conversationId: target.id }
      } catch (caught) {
        if (target !== null) {
          loadedConversationId.current = target.id
        }
        setState({
          ...emptyState(target?.id ?? conversationId),
          conversation: target,
          messages: previousMessages,
          error: errorMessage(caught),
        })
        return { ok: false, conversationId: target?.id ?? null }
      } finally {
        setIsSending(false)
      }
    },
    [conversationId, current, saveConversation],
  )

  return {
    conversation: current?.conversation ?? null,
    messages: current?.messages ?? [],
    isLoading: conversationId !== undefined && current === null,
    notFound: current?.notFound ?? false,
    error: current?.error ?? null,
    isSending,
    send,
  }
}
