import { useAuth } from '../../hooks/useAuth'
import { Button } from '../ui/Button'
import styles from './AccountPanel.module.css'

export function AccountPanel() {
  const { user, logout } = useAuth()

  if (user === null) {
    return null
  }

  return (
    <div className={styles.panel}>
      <div className={styles.identity}>
        <span className={styles.name}>{user.display_name}</span>
        <span className={styles.email}>{user.email}</span>
      </div>
      <Button variant="ghost" onClick={logout}>
        Wyloguj
      </Button>
    </div>
  )
}
