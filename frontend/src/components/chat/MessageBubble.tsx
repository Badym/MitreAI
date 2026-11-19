import type { MessageRole } from '../../types/chat'
import styles from './MessageBubble.module.css'

interface MessageBubbleProps {
  role: MessageRole
  content: string
}

export function MessageBubble({ role, content }: MessageBubbleProps) {
  return (
    <div className={`${styles.row} ${styles[role]}`}>
      <div className={styles.bubble}>{content}</div>
    </div>
  )
}
