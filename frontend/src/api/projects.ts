import client from './client'
import { Project } from './types'

export const projectsAPI = {
  list: async (skip: number = 0, limit: number = 100) => {
    const response = await client.get<Project[]>('/projects/', {
      params: { skip, limit }
    })
    return response.data
  },

  get: async (projectId: number) => {
    const response = await client.get<Project>(`/projects/${projectId}`)
    return response.data
  },

  create: async (data: Omit<Project, 'id' | 'created_at' | 'updated_at' | 'tasks'>) => {
    const response = await client.post<Project>('/projects/', data)
    return response.data
  },

  update: async (projectId: number, data: Omit<Project, 'id' | 'created_at' | 'updated_at' | 'tasks'>) => {
    const response = await client.put<Project>(`/projects/${projectId}`, data)
    return response.data
  },

  delete: async (projectId: number) => {
    await client.delete(`/projects/${projectId}`)
  }
}
