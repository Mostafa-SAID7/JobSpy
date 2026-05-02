export interface SearchHistory {
  id: number
  user_id: number
  query: string
  filters: Record<string, any>
  results_count: number
  searched_at: string
}

export interface SearchParams {
  query: string
  location?: string
  job_type?: string
  experience_level?: string
  salary_min?: number
  salary_max?: number
  is_remote?: number
  // New Scraping Parameters
  site_names?: string[]
  distance?: number
  easy_apply?: boolean
  skip: number
  limit: number
}

export interface PaginatedResponse<T> {
  results: T[]
  total: number
  skip: number
  limit: number
}

export interface ApiError {
  detail: string
  status_code: number
}
