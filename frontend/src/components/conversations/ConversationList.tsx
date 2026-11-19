import { useConversations } from '../../hooks/useConversations'
import { ConversationListItem } from './ConversationListItem'
import styles from './ConversationList.module.css'

interface ConversationListProps {
  onNavigate: () => void
}

export function ConversationList({ onNavigate }: ConversationListProps) {
  const { conversations, isLoading, error } = useConversations()

  if (isLoading) {
    return <p className={styles.info}>Ładowanie</p>
  }
  if (error) {
    return <p className={styles.info}>{error}</p>
  }
  if (conversations.length === 0) {
    return <p className={styles.info}>Brak rozmów</p>
  }

  return (
    <ul className={styles.list}>
      {conversations.map((conversation) => (
        <ConversationListItem
          key={conversation.id}
          conversation={conversation}
          onNavigate={onNavigate}
        />
      ))}
    </ul>
  )
}
