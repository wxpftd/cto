import { Link } from 'react-router-dom'
import { Project } from '../api'
import { ChevronRight, Trash2 } from 'lucide-react'

interface ProjectListProps {
  projects: Project[]
  onDelete: (projectId: number) => Promise<void>
  isLoading?: boolean
}

const statusColors: Record<Project['status'], string> = {
  active: 'bg-green-100 text-green-800',
  on_hold: 'bg-yellow-100 text-yellow-800',
  completed: 'bg-blue-100 text-blue-800',
  cancelled: 'bg-red-100 text-red-800',
}

export function ProjectList({ projects, onDelete, isLoading = false }: ProjectListProps) {
  return (
    <div className="space-y-4">
      {projects.length === 0 ? (
        <div className="text-center py-12 bg-white rounded-lg shadow">
          <p className="text-gray-500 mb-4">No projects yet</p>
          <Link to="/projects/new" className="text-blue-600 hover:text-blue-700 font-medium">
            Create your first project
          </Link>
        </div>
      ) : (
        projects.map(project => (
          <div key={project.id} className="bg-white rounded-lg shadow hover:shadow-lg transition p-6">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center space-x-3 mb-2">
                  <h3 className="text-lg font-semibold text-gray-900">{project.name}</h3>
                  <span className={`px-3 py-1 rounded-full text-xs font-medium ${statusColors[project.status]}`}>
                    {project.status}
                  </span>
                </div>
                {project.description && (
                  <p className="text-gray-600 text-sm mb-3">{project.description}</p>
                )}
                <div className="flex items-center space-x-4 text-xs text-gray-500">
                  <span>{project.tasks?.length || 0} tasks</span>
                  <span>Created: {new Date(project.created_at).toLocaleDateString()}</span>
                </div>
              </div>

              <div className="flex items-center space-x-2 ml-4">
                <Link
                  to={`/projects/${project.id}`}
                  className="text-blue-600 hover:bg-blue-50 p-2 rounded-md transition"
                  title="View project"
                >
                  <ChevronRight className="w-5 h-5" />
                </Link>
                <button
                  onClick={() => {
                    if (confirm('Are you sure you want to delete this project?')) {
                      onDelete(project.id)
                    }
                  }}
                  disabled={isLoading}
                  className="text-red-600 hover:bg-red-50 p-2 rounded-md transition disabled:opacity-50"
                  title="Delete project"
                >
                  <Trash2 className="w-5 h-5" />
                </button>
              </div>
            </div>
          </div>
        ))
      )}
    </div>
  )
}
