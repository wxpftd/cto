import client from './client'
import { Feedback, FeedbackResponse } from './types'

export const feedbackAPI = {
  list: async (projectId?: number, taskId?: number, status?: string, skip: number = 0, limit: number = 100) => {
    const response = await client.get<Feedback[]>('/feedback/', {
      params: { project_id: projectId, task_id: taskId, status, skip, limit }
    })
    return response.data
  },

  get: async (feedbackId: number) => {
    const response = await client.get<Feedback>(`/feedback/${feedbackId}`)
    return response.data
  },

  submit: async (data: {
    project_id: number
    task_id?: number
    user_name?: string
    feedback_text: string
  }) => {
    const response = await client.post<FeedbackResponse>('/feedback/', data)
    return response.data
  }
}
