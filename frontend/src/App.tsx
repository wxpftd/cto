import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { Navbar } from './components'
import { HomePage, NewProjectPage, ProjectDetailPage } from './pages'

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/projects/new" element={<NewProjectPage />} />
          <Route path="/projects/:projectId" element={<ProjectDetailPage />} />
        </Routes>
      </div>
    </Router>
  )
}

export default App
