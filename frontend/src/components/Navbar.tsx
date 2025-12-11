import { Link } from 'react-router-dom'
import { BarChart3, Home, Settings } from 'lucide-react'

export function Navbar() {
  return (
    <nav className="bg-gradient-to-r from-blue-600 to-blue-700 text-white shadow-lg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <Link to="/" className="flex items-center space-x-2 hover:opacity-90">
            <BarChart3 className="w-6 h-6" />
            <span className="text-xl font-bold">Feedback Loop</span>
          </Link>
          
          <div className="hidden md:flex items-center space-x-1">
            <Link
              to="/"
              className="flex items-center px-3 py-2 rounded-md text-sm font-medium hover:bg-blue-500 transition"
            >
              <Home className="w-4 h-4 mr-2" />
              Projects
            </Link>
            <a
              href="http://localhost:8000/docs"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center px-3 py-2 rounded-md text-sm font-medium hover:bg-blue-500 transition"
            >
              <Settings className="w-4 h-4 mr-2" />
              API Docs
            </a>
          </div>
        </div>
      </div>
    </nav>
  )
}
