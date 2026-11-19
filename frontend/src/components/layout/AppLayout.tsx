import { useCallback, useState } from 'react'
import { Outlet } from 'react-router'
import { ConversationsProvider } from '../../context/ConversationsProvider'
import { MenuIcon } from '../ui/Icons'
import { Sidebar } from './Sidebar'
import styles from './AppLayout.module.css'

export function AppLayout() {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false)
  const closeSidebar = useCallback(() => setIsSidebarOpen(false), [])

  return (
    <ConversationsProvider>
      <div className={styles.layout}>
        <Sidebar isOpen={isSidebarOpen} onClose={closeSidebar} />
        {isSidebarOpen && (
          <div className={styles.backdrop} onClick={closeSidebar} aria-hidden="true" />
        )}

        <main className={styles.content}>
          <header className={styles.mobileBar}>
            <button
              type="button"
              className={styles.menuButton}
              onClick={() => setIsSidebarOpen(true)}
              aria-label="Otwórz menu"
            >
              <MenuIcon />
            </button>
            <span className={styles.mobileTitle}>MitreAI</span>
          </header>
          <Outlet />
        </main>
      </div>
    </ConversationsProvider>
  )
}
