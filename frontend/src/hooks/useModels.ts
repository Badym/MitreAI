import { useEffect, useState } from 'react'
import { fetchModels } from '../api/modelsApi'
import type { ModelOption } from '../types/chat'

interface ModelsState {
  models: ModelOption[]
  defaultModel: string | null
}

export function useModels(): ModelsState {
  const [models, setModels] = useState<ModelOption[]>([])

  useEffect(() => {
    const controller = new AbortController()
    fetchModels(controller.signal)
      .then(setModels)
      .catch(() => undefined)
    return () => controller.abort()
  }, [])

  const defaultModel = models.find((model) => model.is_default)?.id ?? null
  return { models, defaultModel }
}
