import { useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router'
import { ChatComposer } from '../components/chat/ChatComposer'
import { MessageList } from '../components/chat/MessageList'
import { ModelSelect } from '../components/chat/ModelSelect'
import { useChat } from '../hooks/useChat'
import { useModels } from '../hooks/useModels'
import styles from './ChatPage.module.css'

interface ModelChoice {
  conversationId: string | undefined
  model: string
}

export function ChatPage() {
  const { conversationId } = useParams()
  const navigate = useNavigate()
  const chat = useChat(conversationId)
  const { models, defaultModel } = useModels()
  const [modelChoice, setModelChoice] = useState<ModelChoice | null>(null)

  const chosenModel =
    modelChoice !== null && modelChoice.conversationId === conversationId ? modelChoice.model : null
  const selectedModel = chosenModel ?? chat.conversation?.model ?? defaultModel

  async function handleSend(content: string): Promise<boolean> {
    const result = await chat.send(content, selectedModel)
    if (result.conversationId && result.conversationId !== conversationId) {
      navigate(`/c/${result.conversationId}`)
    }
    return result.ok
  }

  if (chat.notFound) {
    return (
      <section className={styles.notFound}>
        <h1 className={styles.title}>Nie znaleziono rozmowy</h1>
        <Link to="/">Zacznij nową rozmowę</Link>
      </section>
    )
  }

  const composer = (
    <div className={styles.composer}>
      {chat.error && (
        <p className={styles.error} role="alert">
          {chat.error}
        </p>
      )}
      <ChatComposer onSend={handleSend} disabled={chat.isSending || chat.isLoading} />
      <p className={styles.hint}>
        Enter wysyła, Shift+Enter dodaje nową linię. Na razie odpowiada atrapa modelu.
      </p>
    </div>
  )

  const isNewChat = !chat.isLoading && chat.messages.length === 0

  return (
    <section className={styles.page}>
      <header className={styles.header}>
        <ModelSelect
          models={models}
          value={selectedModel}
          onChange={(model) => setModelChoice({ conversationId, model })}
          disabled={chat.isSending}
        />
      </header>

      {isNewChat ? (
        <div className={styles.emptyState}>
          <div className={styles.intro}>
            <h1 className={styles.title}>W czym mogę pomóc?</h1>
            <p className={styles.subtitle}>
              Opisz urządzenie, protokół i sposób dostępu, a wskażę pasujące techniki MITRE
              ATT&amp;CK.
            </p>
          </div>
          {composer}
        </div>
      ) : (
        <>
          {chat.isLoading ? (
            <p className={styles.loading}>Ładowanie rozmowy</p>
          ) : (
            <MessageList messages={chat.messages} isTyping={chat.isSending} />
          )}
          <div className={styles.bottom}>{composer}</div>
        </>
      )}
    </section>
  )
}
