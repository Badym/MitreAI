import { useState, type FormEvent } from 'react'
import { Navigate } from 'react-router'
import { errorMessage } from '../api/client'
import { Button } from '../components/ui/Button'
import { TextInput } from '../components/ui/TextInput'
import { useAuth } from '../hooks/useAuth'
import styles from './LoginPage.module.css'

export function LoginPage() {
  const { user, login } = useAuth()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  if (user !== null) {
    return <Navigate to="/" replace />
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError(null)
    setIsSubmitting(true)
    try {
      await login(email, password)
    } catch (caught) {
      setError(errorMessage(caught))
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <section className={styles.page}>
      <form className={styles.card} onSubmit={handleSubmit}>
        <h1 className={styles.title}>Zaloguj się do MitreAI</h1>
        <TextInput
          label="E-mail"
          type="email"
          name="email"
          autoComplete="email"
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          required
        />
        <TextInput
          label="Hasło"
          type="password"
          name="password"
          autoComplete="current-password"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          required
        />
        {error && (
          <p className={styles.error} role="alert">
            {error}
          </p>
        )}
        <Button type="submit" fullWidth disabled={isSubmitting}>
          {isSubmitting ? 'Logowanie…' : 'Zaloguj się'}
        </Button>
        <p className={styles.hint}>Konto zakłada administrator.</p>
      </form>
    </section>
  )
}
