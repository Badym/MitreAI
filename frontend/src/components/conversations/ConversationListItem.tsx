import { useRef, useState, type KeyboardEvent } from 'react'
import { NavLink, useMatch, useNavigate } from 'react-router'
import { errorMessage } from '../../api/client'
import { useConversations } from '../../hooks/useConversations'
import type { Conversation } from '../../types/chat'
import { PencilIcon, TrashIcon } from '../ui/Icons'
import styles from './ConversationListItem.module.css'

const UNTITLED = 'Nowa rozmowa'

interface ConversationListItemProps {
  conversation: Conversation
  onNavigate: () => void
}

export function ConversationListItem({ conversation, onNavigate }: ConversationListItemProps) {
  const { renameConversation, deleteConversation } = useConversations()
  const activeId = useMatch('/c/:conversationId')?.params.conversationId
  const navigate = useNavigate()
  const [isEditing, setIsEditing] = useState(false)
  const title = conversation.title || UNTITLED

  async function handleRename(newTitle: string) {
    setIsEditing(false)
    const trimmed = newTitle.trim()
    if (!trimmed || trimmed === conversation.title) {
      return
    }
    try {
      await renameConversation(conversation.id, trimmed)
    } catch (caught) {
      window.alert(errorMessage(caught))
    }
  }

  async function handleDelete() {
    if (!window.confirm(`Usunąć rozmowę „${title}”? Tej operacji nie można cofnąć.`)) {
      return
    }
    try {
      await deleteConversation(conversation.id)
      if (activeId === conversation.id) {
        navigate('/')
      }
    } catch (caught) {
      window.alert(errorMessage(caught))
    }
  }

  if (isEditing) {
    return (
      <li className={styles.item}>
        <RenameInput
          initialValue={conversation.title}
          onSubmit={handleRename}
          onCancel={() => setIsEditing(false)}
        />
      </li>
    )
  }

  return (
    <li className={styles.item}>
      <NavLink
        to={`/c/${conversation.id}`}
        className={({ isActive }) => (isActive ? `${styles.link} ${styles.active}` : styles.link)}
        onClick={onNavigate}
        title={title}
      >
        {title}
      </NavLink>
      <div className={styles.actions}>
        <button
          type="button"
          className={styles.iconButton}
          onClick={() => setIsEditing(true)}
          aria-label={`Zmień nazwę rozmowy ${title}`}
        >
          <PencilIcon />
        </button>
        <button
          type="button"
          className={styles.iconButton}
          onClick={handleDelete}
          aria-label={`Usuń rozmowę ${title}`}
        >
          <TrashIcon />
        </button>
      </div>
    </li>
  )
}

interface RenameInputProps {
  initialValue: string
  onSubmit: (value: string) => void
  onCancel: () => void
}

function RenameInput({ initialValue, onSubmit, onCancel }: RenameInputProps) {
  const [value, setValue] = useState(initialValue)
  const cancelled = useRef(false)

  function handleKeyDown(event: KeyboardEvent<HTMLInputElement>) {
    if (event.key === 'Enter') {
      event.preventDefault()
      event.currentTarget.blur()
    }
    if (event.key === 'Escape') {
      cancelled.current = true
      onCancel()
    }
  }

  return (
    <input
      className={styles.renameInput}
      value={value}
      maxLength={200}
      autoFocus
      aria-label="Nowa nazwa rozmowy"
      onChange={(event) => setValue(event.target.value)}
      onKeyDown={handleKeyDown}
      onBlur={() => {
        if (!cancelled.current) {
          onSubmit(value)
        }
      }}
    />
  )
}
