import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { projectsAPI, Project } from '../api'
import { ProjectForm } from '../components'
import { ArrowLeft } from 'lucide-react'

export function NewProjectPage() {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string>('')

  const handleSubmit = async (data: Omit<Project, 'id' | 'created_at' | 'updated_at' | 'tasks'>) => {
    try {
      setLoading(true)
      setError('')
      const newProject = await projectsAPI.create(data)
      navigate(`/projects/${newProject.id}`)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create project')
      throw err
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <button
        onClick={() => navigate('/')}
        className="flex items-center space-x-2 text-blue-600 hover:text-blue-700 mb-6"
      >
        <ArrowLeft className="w-4 h-4" />
        <span>Back to Projects</span>
      </button>

      <h1 className="text-3xl font-bold text-gray-900 mb-8">Create New Project</h1>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded mb-6">
          {error}
        </div>
      )}

      <ProjectForm
        onSubmit={handleSubmit}
        isLoading={loading}
      />
    </div>
  )
}
