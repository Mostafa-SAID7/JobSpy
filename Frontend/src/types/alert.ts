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
