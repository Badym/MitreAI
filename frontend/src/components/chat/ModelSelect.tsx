import type { ModelOption } from '../../types/chat'
import styles from './ModelSelect.module.css'

interface ModelSelectProps {
  models: ModelOption[]
  value: string | null
  onChange: (model: string) => void
  disabled?: boolean
}

export function ModelSelect({ models, value, onChange, disabled = false }: ModelSelectProps) {
  return (
    <label className={styles.wrapper}>
      <span className={styles.label}>Model</span>
      <select
        className={styles.select}
        value={value ?? ''}
        onChange={(event) => onChange(event.target.value)}
        disabled={disabled || models.length === 0}
      >
        {models.map((model) => (
          <option key={model.id} value={model.id}>
            {model.id}
          </option>
        ))}
      </select>
    </label>
  )
}
