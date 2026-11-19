import { useEffect, useRef } from 'react'
import type { DisplayMessage } from '../../types/chat'
import { MessageBubble } from './MessageBubble'
import styles from './MessageList.module.css'

interface MessageListProps {
  messages: DisplayMessage[]
  isTyping: boolean
}

export function MessageList({ messages, isTyping }: MessageListProps) {
  const endRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    endRef.current?.scrollIntoView({ block: 'end' })
  }, [messages, isTyping])

  return (
    <div className={styles.scroller}>
      <ol className={styles.list} aria-live="polite">
        {messages.map((message) => (
          <li key={message.id}>
            <MessageBubble role={message.role} content={message.content} />
          </li>
        ))}
        {isTyping && (
          <li>
            <TypingIndicator />
          </li>
        )}
      </ol>
      <div ref={endRef} />
    </div>
  )
}

function TypingIndicator() {
  return (
    <span className={styles.typing} aria-label="Model pisze odpowiedź">
      <span />
      <span />
      <span />
    </span>
  )
}
