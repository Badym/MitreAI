import { useId, type InputHTMLAttributes } from 'react'
import styles from './TextInput.module.css'

interface TextInputProps extends InputHTMLAttributes<HTMLInputElement> {
  label: string
}

export function TextInput({ label, id, className, ...props }: TextInputProps) {
  const generatedId = useId()
  const inputId = id ?? generatedId

  return (
    <div className={styles.field}>
      <label htmlFor={inputId} className={styles.label}>
        {label}
      </label>
      <input
        id={inputId}
        className={[styles.input, className].filter(Boolean).join(' ')}
        {...props}
      />
    </div>
  )
}
