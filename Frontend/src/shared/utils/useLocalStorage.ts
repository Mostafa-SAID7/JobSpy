/**
 * Local Storage Composable
 * Helper functions for storing/retrieving data with JSON serialization
 */

export interface StorageOptions {
  ttl?: number // Time to live in milliseconds
}

export interface StorageData<T> {
  value: T
  expiresAt?: number
}

/**
 * Set item in localStorage with optional TTL
 */
export function setLocalStorage<T>(
  key: string,
  value: T,
  options?: StorageOptions
): void {
  try {
    const data: StorageData<T> = {
      value,
      expiresAt: options?.ttl ? Date.now() + options.ttl : undefined,
    }
    localStorage.setItem(key, JSON.stringify(data))
  } catch (error) {
    if (error instanceof Error) {
      if (error.name === 'QuotaExceededError') {
        console.error(`localStorage quota exceeded for key: ${key}`)
      } else {
        console.error(`Error storing data in localStorage: ${error.message}`)
      }
    }
  }
}

/**
 * Get item from localStorage with expiration check
 */
export function getLocalStorage<T>(key: string, defaultValue?: T): T | null {
  try {
    const item = localStorage.getItem(key)
    if (!item) return defaultValue ?? null

    try {
      const parsed = JSON.parse(item)
      
      // Check if it matches our StorageData structure
      if (parsed && typeof parsed === 'object' && 'value' in parsed) {
        const data = parsed as StorageData<T>
        // Check if data has expired
        if (data.expiresAt && Date.now() > data.expiresAt) {
          localStorage.removeItem(key)
          return defaultValue ?? null
        }
        return data.value
      }
      
      // If it's valid JSON but not our structure, return as is (could be a direct boolean/number/array)
      return parsed as T
    } catch {
      // If parsing fails, it's likely a plain string value
      return item as unknown as T
    }
  } catch (error) {
    if (error instanceof Error) {
      console.error(`Error retrieving data from localStorage for key ${key}: ${error.message}`)
    }
    return defaultValue ?? null
  }
}

/**
 * Remove item from localStorage
 */
export function removeLocalStorage(key: string): void {
  try {
    localStorage.removeItem(key)
  } catch (error) {
    if (error instanceof Error) {
      console.error(`Error removing data from localStorage: ${error.message}`)
    }
  }
}

/**
 * Clear all items from localStorage
 */
export function clearLocalStorage(): void {
  try {
    localStorage.clear()
  } catch (error) {
    if (error instanceof Error) {
      console.error(`Error clearing localStorage: ${error.message}`)
    }
  }
}

/**
 * Check if localStorage is available
 */
export function isLocalStorageAvailable(): boolean {
  try {
    const test = '__localStorage_test__'
    localStorage.setItem(test, test)
    localStorage.removeItem(test)
    return true
  } catch {
    return false
  }
}

/**
 * Get all keys from localStorage
 */
export function getLocalStorageKeys(): string[] {
  try {
    return Object.keys(localStorage)
  } catch (error) {
    if (error instanceof Error) {
      console.error(`Error getting localStorage keys: ${error.message}`)
    }
    return []
  }
}

/**
 * Get localStorage size in bytes
 */
export function getLocalStorageSize(): number {
  try {
    let size = 0
    for (const key in localStorage) {
      if (localStorage.hasOwnProperty(key)) {
        size += localStorage[key].length + key.length
      }
    }
    return size
  } catch (error) {
    if (error instanceof Error) {
      console.error(`Error calculating localStorage size: ${error.message}`)
    }
    return 0
  }
}
