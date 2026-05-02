export interface Job {
  id: number | string
  job_id?: string | number
  title: string
  company: string
  location: string
  salary_min?: number
  salary_max?: number
  salary_currency?: string
  job_type: string
  description: string
  requirements?: string[]
  benefits?: string[]
  source?: string
  site_name?: string
  source_url?: string
  job_url?: string
  source_job_id?: string
  posted_date: string
  deadline?: string
  company_logo_url?: string
  company_website?: string
  experience_level?: string
  skills?: string[]
  is_remote: number | boolean
  created_at?: string
  updated_at?: string
}

export interface SavedJob {
  id: number | string
  user_id: number | string
  job_id: number | string
  job: Job
  saved_at: string
}
