import { useState } from 'react'
import { Task } from '../api'

interface FeedbackFormProps {
  projectId: number
  tasks?: Task[]
  onSubmit: (data: {
    project_id: number
    task_id?: number
    user_name?: string
    feedback_text: string
  }) => Promise<void>
  isLoading?: boolean
}

export function FeedbackForm({ projectId, tasks = [], onSubmit, isLoading = false }: FeedbackFormProps) {
  const [formData, setFormData] = useState({
    project_id: projectId,
    task_id: undefined as number | undefined,
    user_name: '',
    feedback_text: '',
  })

  const [error, setError] = useState<string>('')
  const [success, setSuccess] = useState<string>('')

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target
    
    if (name === 'task_id') {
      setFormData(prev => ({ ...prev, [name]: value === '' ? undefined : parseInt(value) }))
    } else {
      setFormData(prev => ({ ...prev, [name]: value }))
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setSuccess('')

    if (!formData.feedback_text.trim()) {
      setError('Feedback text is required')
      return
    }

    try {
      await onSubmit(formData)
      setSuccess('Feedback submitted successfully! AI is processing your feedback...')
      setFormData({
        project_id: projectId,
        task_id: undefined,
        user_name: '',
        feedback_text: '',
      })
      setTimeout(() => setSuccess(''), 5000)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4 bg-white p-6 rounded-lg shadow">
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded">
          {error}
        </div>
      )}

      {success && (
        <div className="bg-green-50 border border-green-200 text-green-600 px-4 py-3 rounded">
          {success}
        </div>
      )}

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Your Name
        </label>
        <input
          type="text"
          name="user_name"
          value={formData.user_name}
          onChange={handleChange}
          maxLength={255}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Enter your name (optional)"
        />
      </div>

      {tasks.length > 0 && (
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Related Task (optional)
          </label>
          <select
            name="task_id"
            value={formData.task_id || ''}
            onChange={handleChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">No specific task</option>
            {tasks.map(task => (
              <option key={task.id} value={task.id}>
                {task.title}
              </option>
            ))}
          </select>
        </div>
      )}

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Feedback *
        </label>
        <textarea
          name="feedback_text"
          value={formData.feedback_text}
          onChange={handleChange}
          rows={5}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Enter your feedback. AI will analyze it and suggest adjustments..."
        />
      </div>

      <button
        type="submit"
        disabled={isLoading}
        className="w-full bg-blue-600 text-white py-2 rounded-md font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition"
      >
        {isLoading ? 'Submitting...' : 'Submit Feedback'}
      </button>
    </form>
  )
}
