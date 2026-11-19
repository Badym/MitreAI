export type MessageRole = 'user' | 'assistant'

export interface Conversation {
  id: string
  title: string
  model: string
  created_at: string
  updated_at: string
  is_archived: boolean
}

export interface Message {
  id: string
  conversation_id: string
  role: MessageRole
  content: string
  model: string | null
  tokens_in: number | null
  tokens_out: number | null
  analysis: Record<string, unknown> | null
  created_at: string
}

export type DisplayMessage = Pick<Message, 'id' | 'role' | 'content'>

export interface SendMessageResult {
  user_message: Message
  assistant_message: Message
  conversation: Conversation
}

export interface ModelOption {
  id: string
  is_default: boolean
}
