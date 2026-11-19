import { useNavigate } from 'react-router'
import { AccountPanel } from '../auth/AccountPanel'
import { ConversationList } from '../conversations/ConversationList'
import { BackendStatusBadge } from '../system/BackendStatusBadge'
import { Button } from '../ui/Button'
import { PlusIcon } from '../ui/Icons'
import styles from './Sidebar.module.css'

interface SidebarProps {
  isOpen: boolean
  onClose: () => void
}

export function Sidebar({ isOpen, onClose }: SidebarProps) {
  const navigate = useNavigate()

  function startNewChat() {
    navigate('/')
    onClose()
  }

  return (
    <aside className={isOpen ? `${styles.sidebar} ${styles.open}` : styles.sidebar}>
      <div className={styles.brand}>MitreAI</div>

      <Button variant="secondary" fullWidth onClick={startNewChat}>
        <PlusIcon />
        Nowa rozmowa
      </Button>

      <nav className={styles.history} aria-label="Historia rozmów">
        <h2 className={styles.sectionTitle}>Historia</h2>
        <ConversationList onNavigate={onClose} />
      </nav>

      <footer className={styles.footer}>
        <BackendStatusBadge />
        <AccountPanel />
      </footer>
    </aside>
  )
}
