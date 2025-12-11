import { Task } from '../api'
import { Trash2, Edit2 } from 'lucide-react'

interface TaskListProps {
  tasks: Task[]
  onEdit?: (task: Task) => void
  onDelete: (taskId: number) => Promise<void>
  isLoading?: boolean
}

const statusColors: Record<Task['status'], string> = {
  todo: 'bg-gray-100 text-gray-800',
  in_progress: 'bg-blue-100 text-blue-800',
  completed: 'bg-green-100 text-green-800',
  blocked: 'bg-red-100 text-red-800',
}

const getPriorityColor = (priority: number) => {
  if (priority >= 8) return 'text-red-600'
  if (priority >= 5) return 'text-yellow-600'
  return 'text-green-600'
}

export function TaskList({ tasks, onEdit, onDelete, isLoading = false }: TaskListProps) {
  return (
    <div className="space-y-3">
      {tasks.length === 0 ? (
        <div className="text-center py-8 bg-gray-50 rounded-lg">
          <p className="text-gray-500">No tasks yet</p>
        </div>
      ) : (
        tasks.map(task => (
          <div key={task.id} className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition">
            <div className="flex items-start justify-between gap-4">
              <div className="flex-1">
                <div className="flex items-center space-x-2 mb-2">
                  <h4 className="font-semibold text-gray-900">{task.title}</h4>
                  <span className={`px-2 py-1 rounded text-xs font-medium ${statusColors[task.status]}`}>
                    {task.status.replace('_', ' ')}
                  </span>
                </div>
                
                {task.description && (
                  <p className="text-sm text-gray-600 mb-2">{task.description}</p>
                )}

                <div className="flex items-center space-x-3 text-xs text-gray-500">
                  <span className={`font-medium ${getPriorityColor(task.priority)}`}>
                    Priority: {task.priority}/10
                  </span>
                  {task.estimated_hours && (
                    <span>Est: {task.estimated_hours}h</span>
                  )}
                  <span>Created: {new Date(task.created_at).toLocaleDateString()}</span>
                </div>
              </div>

              <div className="flex items-center space-x-2">
                {onEdit && (
                  <button
                    onClick={() => onEdit(task)}
                    className="text-blue-600 hover:bg-blue-50 p-2 rounded-md transition"
                    title="Edit task"
                  >
                    <Edit2 className="w-4 h-4" />
                  </button>
                )}
                <button
                  onClick={() => {
                    if (confirm('Are you sure you want to delete this task?')) {
                      onDelete(task.id)
                    }
                  }}
                  disabled={isLoading}
                  className="text-red-600 hover:bg-red-50 p-2 rounded-md transition disabled:opacity-50"
                  title="Delete task"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        ))
      )}
    </div>
  )
}
