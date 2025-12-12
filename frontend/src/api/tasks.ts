import client from './client'
import { Task } from './types'

export const tasksAPI = {
  list: async (projectId?: number, skip: number = 0, limit: number = 100) => {
    const response = await client.get<Task[]>('/tasks/', {
      params: { project_id: projectId, skip, limit }
    })
    return response.data
  },

  get: async (taskId: number) => {
    const response = await client.get<Task>(`/tasks/${taskId}`)
    return response.data
  },

  create: async (data: Omit<Task, 'id' | 'created_at' | 'updated_at'>) => {
    const response = await client.post<Task>('/tasks/', data)
    return response.data
  },

  update: async (taskId: number, data: Omit<Task, 'id' | 'created_at' | 'updated_at'>) => {
    const response = await client.put<Task>(`/tasks/${taskId}`, data)
    return response.data
  },

  delete: async (taskId: number) => {
    await client.delete(`/tasks/${taskId}`)
  }
}
