function isObject(value: unknown): value is Record<string, unknown> {
  return value !== null && typeof value === 'object' && !Array.isArray(value)
}

function toCamelCaseKey(key: string): string {
  return key.replace(/_([a-z])/g, (_, letter: string) => letter.toUpperCase())
}

function toSnakeCaseKey(key: string): string {
  return key.replace(/[A-Z]/g, (letter) => `_${letter.toLowerCase()}`)
}

export function toCamelCase<T>(value: unknown): T {
  if (Array.isArray(value)) {
    return value.map((item) => toCamelCase(item)) as T
  }

  if (!isObject(value)) {
    return value as T
  }

  const result: Record<string, unknown> = {}
  for (const key of Object.keys(value)) {
    result[toCamelCaseKey(key)] = toCamelCase(value[key])
  }
  return result as T
}

export function toSnakeCase<T>(value: unknown): T {
  if (Array.isArray(value)) {
    return value.map((item) => toSnakeCase(item)) as T
  }

  if (!isObject(value)) {
    return value as T
  }

  const result: Record<string, unknown> = {}
  for (const key of Object.keys(value)) {
    result[toSnakeCaseKey(key)] = toSnakeCase(value[key])
  }
  return result as T
}
