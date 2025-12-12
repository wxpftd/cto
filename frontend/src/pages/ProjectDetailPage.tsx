import { useState, useEffect } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { projectsAPI, tasksAPI, feedbackAPI, Project, Task, Feedback } from '../api'
import { ProjectForm, TaskForm, FeedbackForm, TaskList, FeedbackList } from '../components'
import { ArrowLeft, Loader, Plus, X } from 'lucide-react'

type Modal = 'addTask' | 'editTask' | 'feedback' | null

export function ProjectDetailPage() {
  const { projectId } = useParams<{ projectId: string }>()
  const navigate = useNavigate()
  const id = parseInt(projectId!)

  const [project, setProject] = useState<Project | null>(null)
  const [tasks, setTasks] = useState<Task[]>([])
  const [feedbackList, setFeedbackList] = useState<Feedback[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string>('')
  const [modal, setModal] = useState<Modal>(null)
  const [editingTask, setEditingTask] = useState<Task | null>(null)
  const [activeTab, setActiveTab] = useState<'tasks' | 'feedback'>('tasks')

  useEffect(() => {
    loadProject()
  }, [id])

  const loadProject = async () => {
    try {
      setLoading(true)
      setError('')
      const projectData = await projectsAPI.get(id)
      setProject(projectData)
      setTasks(projectData.tasks || [])
      
      const feedbackData = await feedbackAPI.list(id)
      setFeedbackList(feedbackData)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load project')
    } finally {
      setLoading(false)
    }
  }

  const handleUpdateProject = async (data: Omit<Project, 'id' | 'created_at' | 'updated_at' | 'tasks'>) => {
    try {
      const updated = await projectsAPI.update(id, data)
      setProject(updated)
    } catch (err) {
      throw err
    }
  }

  const handleAddTask = async (data: Omit<Task, 'id' | 'created_at' | 'updated_at'>) => {
    try {
      const newTask = await tasksAPI.create(data)
      setTasks([...tasks, newTask])
      setModal(null)
    } catch (err) {
      throw err
    }
  }

  const handleUpdateTask = async (data: Omit<Task, 'id' | 'created_at' | 'updated_at'>) => {
    if (!editingTask) return
    try {
      const updated = await tasksAPI.update(editingTask.id, data)
      setTasks(tasks.map(t => t.id === editingTask.id ? updated : t))
      setModal(null)
      setEditingTask(null)
    } catch (err) {
      throw err
    }
  }

  const handleDeleteTask = async (taskId: number) => {
    try {
      await tasksAPI.delete(taskId)
      setTasks(tasks.filter(t => t.id !== taskId))
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete task')
    }
  }

  const handleSubmitFeedback = async (data: any) => {
    try {
      await feedbackAPI.submit(data)
      const updatedFeedback = await feedbackAPI.list(id)
      setFeedbackList(updatedFeedback)
      setModal(null)
    } catch (err) {
      throw err
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader className="w-8 h-8 text-blue-600 animate-spin" />
      </div>
    )
  }

  if (!project) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <p className="text-red-600">Project not found</p>
        <button onClick={() => navigate('/')} className="text-blue-600 mt-4">
          Back to Projects
        </button>
      </div>
    )
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <button
        onClick={() => navigate('/')}
        className="flex items-center space-x-2 text-blue-600 hover:text-blue-700 mb-6"
      >
        <ArrowLeft className="w-4 h-4" />
        <span>Back to Projects</span>
      </button>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded mb-6">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Project Info */}
        <div className="lg:col-span-1">
          <h1 className="text-3xl font-bold text-gray-900 mb-6">
            {project.name}
          </h1>

          <div className="space-y-6">
            <div>
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Project Settings</h2>
              <ProjectForm
                initialData={project}
                onSubmit={handleUpdateProject}
                isLoading={false}
              />
            </div>
          </div>
        </div>

        {/* Tasks and Feedback */}
        <div className="lg:col-span-2">
          <div className="space-y-6">
            {/* Tabs */}
            <div className="flex space-x-4 border-b border-gray-200">
              <button
                onClick={() => setActiveTab('tasks')}
                className={`px-4 py-2 font-medium transition ${
                  activeTab === 'tasks'
                    ? 'border-b-2 border-blue-600 text-blue-600'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                Tasks ({tasks.length})
              </button>
              <button
                onClick={() => setActiveTab('feedback')}
                className={`px-4 py-2 font-medium transition ${
                  activeTab === 'feedback'
                    ? 'border-b-2 border-blue-600 text-blue-600'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                Feedback ({feedbackList.length})
              </button>
            </div>

            {/* Tasks Tab */}
            {activeTab === 'tasks' && (
              <div className="space-y-4">
                <button
                  onClick={() => {
                    setEditingTask(null)
                    setModal('addTask')
                  }}
                  className="flex items-center space-x-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition"
                >
                  <Plus className="w-4 h-4" />
                  <span>Add Task</span>
                </button>

                <TaskList
                  tasks={tasks}
                  onEdit={(task) => {
                    setEditingTask(task)
                    setModal('editTask')
                  }}
                  onDelete={handleDeleteTask}
                />
              </div>
            )}

            {/* Feedback Tab */}
            {activeTab === 'feedback' && (
              <div className="space-y-4">
                <button
                  onClick={() => setModal('feedback')}
                  className="flex items-center space-x-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition"
                >
                  <Plus className="w-4 h-4" />
                  <span>Add Feedback</span>
                </button>

                <FeedbackList feedbackList={feedbackList} />
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Modals */}
      {modal === 'addTask' && (
        <Modal onClose={() => setModal(null)}>
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Add New Task</h2>
          <TaskForm
            projectId={id}
            onSubmit={handleAddTask}
          />
        </Modal>
      )}

      {modal === 'editTask' && editingTask && (
        <Modal onClose={() => setModal(null)}>
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Edit Task</h2>
          <TaskForm
            projectId={id}
            initialData={editingTask}
            onSubmit={handleUpdateTask}
          />
        </Modal>
      )}

      {modal === 'feedback' && (
        <Modal onClose={() => setModal(null)}>
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Submit Feedback</h2>
          <FeedbackForm
            projectId={id}
            tasks={tasks}
            onSubmit={handleSubmitFeedback}
          />
        </Modal>
      )}
    </div>
  )
}

function Modal({ onClose, children }: { onClose: () => void; children: React.ReactNode }) {
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg max-w-md w-full max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between p-6 border-b border-gray-200 sticky top-0 bg-white">
          <div />
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700"
          >
            <X className="w-6 h-6" />
          </button>
        </div>
        <div className="p-6">
          {children}
        </div>
      </div>
    </div>
  )
}
