import { useBackendHealth, type BackendStatus } from '../../hooks/useBackendHealth'
import { StatusBadge, type StatusTone } from '../ui/StatusBadge'

const STATUS_VIEW: Record<BackendStatus, { tone: StatusTone; label: string }> = {
  checking: { tone: 'neutral', label: 'Sprawdzanie backendu' },
  online: { tone: 'success', label: 'Backend i baza działają' },
  degraded: { tone: 'warning', label: 'Baza danych niedostępna' },
  offline: { tone: 'danger', label: 'Backend niedostępny' },
}

export function BackendStatusBadge() {
  const status = useBackendHealth()
  const { tone, label } = STATUS_VIEW[status]

  return <StatusBadge tone={tone}>{label}</StatusBadge>
}
