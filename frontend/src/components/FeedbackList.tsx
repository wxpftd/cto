import { Feedback } from '../api'
import { CheckCircle, Clock, AlertCircle, RefreshCw } from 'lucide-react'

interface FeedbackListProps {
  feedbackList: Feedback[]
}

const statusIcons: Record<Feedback['status'], React.ReactNode> = {
  completed: <CheckCircle className="w-5 h-5 text-green-600" />,
  pending: <Clock className="w-5 h-5 text-yellow-600" />,
  processing: <RefreshCw className="w-5 h-5 text-blue-600 animate-spin" />,
  failed: <AlertCircle className="w-5 h-5 text-red-600" />,
}

const statusColors: Record<Feedback['status'], string> = {
  completed: 'bg-green-50',
  pending: 'bg-yellow-50',
  processing: 'bg-blue-50',
  failed: 'bg-red-50',
}

export function FeedbackList({ feedbackList }: FeedbackListProps) {
  return (
    <div className="space-y-3">
      {feedbackList.length === 0 ? (
        <div className="text-center py-8 bg-gray-50 rounded-lg">
          <p className="text-gray-500">No feedback yet</p>
        </div>
      ) : (
        feedbackList.map(feedback => (
          <div key={feedback.id} className={`rounded-lg p-4 border ${statusColors[feedback.status]} border-gray-200`}>
            <div className="flex items-start gap-4">
              <div className="mt-1">
                {statusIcons[feedback.status]}
              </div>

              <div className="flex-1">
                <div className="flex items-center space-x-2 mb-1">
                  {feedback.user_name && (
                    <span className="font-medium text-gray-900">{feedback.user_name}</span>
                  )}
                  <span className="text-xs text-gray-500">
                    {new Date(feedback.created_at).toLocaleDateString()} at {new Date(feedback.created_at).toLocaleTimeString()}
                  </span>
                </div>

                <p className="text-gray-700 text-sm mb-2">{feedback.feedback_text}</p>

                {feedback.status === 'completed' && feedback.adjustments && feedback.adjustments.length > 0 && (
                  <div className="mt-3 bg-white rounded border border-gray-200 p-3">
                    <p className="text-xs font-semibold text-gray-900 mb-2">AI Suggestions:</p>
                    <div className="space-y-2">
                      {feedback.adjustments.map(adj => (
                        <div key={adj.id} className="text-xs">
                          <p className="font-medium text-gray-900">{adj.title}</p>
                          <p className="text-gray-600">{adj.description}</p>
                          <p className="text-gray-500 italic">{adj.impact}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        ))
      )}
    </div>
  )
}
