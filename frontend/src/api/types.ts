export interface Project {
  id: number
  name: string
  description?: string
  status: 'active' | 'completed' | 'on_hold' | 'cancelled'
  created_at: string
  updated_at: string
  tasks?: Task[]
}

export interface Task {
  id: number
  project_id: number
  title: string
  description?: string
  status: 'todo' | 'in_progress' | 'completed' | 'blocked'
  priority: number
  estimated_hours?: number
  created_at: string
  updated_at: string
}

export interface Feedback {
  id: number
  project_id: number
  task_id?: number
  user_name?: string
  feedback_text: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  created_at: string
  processed_at?: string
  adjustments?: Adjustment[]
}

export interface Adjustment {
  id: number
  feedback_id: number
  adjustment_type: string
  title: string
  description: string
  impact: string
  created_at: string
}

export interface FeedbackResponse {
  feedback_id: number
  status: string
  message: string
  task_id: string
}
