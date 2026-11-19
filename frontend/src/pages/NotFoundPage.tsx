import { Link } from 'react-router'
import styles from './NotFoundPage.module.css'

export function NotFoundPage() {
  return (
    <section className={styles.page}>
      <h1 className={styles.title}>Nie znaleziono strony</h1>
      <Link to="/">Wróć do czatu</Link>
    </section>
  )
}
