import { useState, type FormEvent, type KeyboardEvent } from 'react'
import { Button } from '../ui/Button'
import styles from './ChatComposer.module.css'

interface ChatComposerProps {
  onSend: (content: string) => Promise<boolean>
  disabled?: boolean
  placeholder?: string
}

export function ChatComposer({
  onSend,
  disabled = false,
  placeholder = 'Opisz komponent systemu przemysłowego',
}: ChatComposerProps) {
  const [content, setContent] = useState('')
  const trimmed = content.trim()

  async function submit() {
    if (!trimmed || disabled) {
      return
    }
    setContent('')
    const sent = await onSend(trimmed)
    if (!sent) {
      setContent(trimmed)
    }
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    void submit()
  }

  function handleKeyDown(event: KeyboardEvent<HTMLTextAreaElement>) {
    if (event.key === 'Enter' && !event.shiftKey && !event.nativeEvent.isComposing) {
      event.preventDefault()
      void submit()
    }
  }

  return (
    <form className={styles.composer} onSubmit={handleSubmit}>
      <textarea
        className={styles.input}
        value={content}
        onChange={(event) => setContent(event.target.value)}
        onKeyDown={handleKeyDown}
        placeholder={placeholder}
        rows={3}
        maxLength={20000}
        autoFocus
        aria-label="Treść wiadomości"
      />
      <Button type="submit" disabled={disabled || !trimmed}>
        Wyślij
      </Button>
    </form>
  )
}
