/**
 * أنواع TypeScript - JobSpy
 * TypeScript types for JobSpy
 */

export interface User {
  id: number
  email: string
  full_name: string
  phone?: string
  bio?: string
  created_at: string
  updated_at: string
}

export interface Job {
  id: number
  title: string
  company: string
  location: string
  salary_min?: number
  salary_max?: number
  salary_currency: string
  job_type: string
  description: string
  requirements?: string[]
  benefits?: string[]
  source: string
  source_url: string
  source_job_id: string
  posted_date: string
  deadline?: string
  company_logo_url?: string
  company_website?: string
  experience_level?: string
  skills?: string[]
  is_remote: number
  created_at: string
  updated_at: string
}

export interface SavedJob {
  id: number
  user_id: number
  job_id: number
  job: Job
  saved_at: string
}

export interface Alert {
  id: number
  user_id: number
  query: string
  frequency: string
  filters: Record<string, any>
  is_active: boolean
  new_jobs_count: number
  last_triggered?: string
  next_trigger: string
  created_at: string
  updated_at: string
}

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
