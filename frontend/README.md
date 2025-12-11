# Feedback Loop Frontend

A modern React + TypeScript frontend application for the Feedback Loop API. This application provides a user-friendly interface to manage projects, tasks, and feedback, with integrated AI-powered re-planning suggestions.

## Features

- 📋 **Project Management**: Create, read, update, and delete projects
- ✅ **Task Management**: Manage tasks within projects with priority levels and status tracking
- 💬 **Feedback System**: Submit feedback that triggers AI-powered analysis
- 🤖 **AI Suggestions**: View AI-generated adjustment suggestions from the backend
- 📊 **Real-time Updates**: Live status tracking for feedback processing
- 🎨 **Modern UI**: Clean, responsive interface built with Tailwind CSS

## Tech Stack

- **React 18** - UI framework
- **TypeScript** - Type safety
- **React Router** - Client-side routing
- **Axios** - HTTP client for API communication
- **Tailwind CSS** - Styling
- **Vite** - Build tool
- **Lucide React** - Icon library

## Getting Started

### Prerequisites

- Node.js 16+ and npm/yarn
- Backend API running on `http://localhost:8000`

### Installation

1. Install dependencies:
```bash
npm install
```

2. Create `.env` file from example:
```bash
cp .env.example .env
```

3. Update `.env` if backend is running on a different URL:
```
VITE_API_URL=http://localhost:8000
```

### Development

Start the development server:
```bash
npm run dev
```

The application will be available at `http://localhost:5173`

### Build

Build for production:
```bash
npm run build
```

Preview the production build:
```bash
npm run preview
```

## Project Structure

```
frontend/
├── src/
│   ├── api/               # API client and types
│   │   ├── client.ts      # Axios instance
│   │   ├── types.ts       # TypeScript interfaces
│   │   ├── projects.ts    # Project endpoints
│   │   ├── tasks.ts       # Task endpoints
│   │   ├── feedback.ts    # Feedback endpoints
│   │   └── index.ts       # Exports
│   ├── components/        # Reusable components
│   │   ├── Navbar.tsx
│   │   ├── ProjectForm.tsx
│   │   ├── TaskForm.tsx
│   │   ├── FeedbackForm.tsx
│   │   ├── ProjectList.tsx
│   │   ├── TaskList.tsx
│   │   ├── FeedbackList.tsx
│   │   └── index.ts
│   ├── pages/            # Page components
│   │   ├── HomePage.tsx
│   │   ├── NewProjectPage.tsx
│   │   ├── ProjectDetailPage.tsx
│   │   └── index.ts
│   ├── App.tsx           # Main app component with routing
│   ├── main.tsx          # Entry point
│   └── index.css         # Global styles
├── index.html
├── package.json
├── vite.config.ts
├── tsconfig.json
├── tailwind.config.js
└── postcss.config.js
```

## API Integration

The frontend integrates with the following backend endpoints:

### Projects
- `GET /projects/` - List all projects
- `POST /projects/` - Create a project
- `GET /projects/{id}` - Get project details
- `PUT /projects/{id}` - Update a project
- `DELETE /projects/{id}` - Delete a project

### Tasks
- `GET /tasks/` - List tasks (with optional project_id filter)
- `POST /tasks/` - Create a task
- `GET /tasks/{id}` - Get task details
- `PUT /tasks/{id}` - Update a task
- `DELETE /tasks/{id}` - Delete a task

### Feedback
- `GET /feedback/` - List feedback entries
- `POST /feedback/` - Submit feedback
- `GET /feedback/{id}` - Get feedback with adjustments

For detailed API documentation, see [API_REFERENCE.md](../API_REFERENCE.md)

## Usage

### Creating a Project

1. Click "New Project" button
2. Fill in project details (name, description, status)
3. Click "Save Project"

### Managing Tasks

1. Open a project detail page
2. Go to "Tasks" tab
3. Click "Add Task" to create new tasks
4. Edit or delete existing tasks as needed

### Submitting Feedback

1. Open a project detail page
2. Go to "Feedback" tab
3. Click "Add Feedback"
4. Enter your feedback (optionally link to a specific task)
5. Click "Submit Feedback"
6. The backend will process your feedback and generate AI suggestions

### Viewing AI Suggestions

After feedback is submitted:
1. Feedback status changes from "pending" to "processing"
2. Once processed, status becomes "completed"
3. AI-generated suggestions appear under the feedback entry

## Environment Variables

Create a `.env` file with the following variables:

```
# Backend API URL
VITE_API_URL=http://localhost:8000
```

## Development Guidelines

### Code Style

- Use TypeScript for type safety
- Follow React hooks patterns
- Use functional components
- Keep components small and focused
- Name components with PascalCase
- Name utility functions with camelCase

### Styling

- Use Tailwind CSS utility classes
- Follow mobile-first responsive design
- Use semantic HTML
- Maintain consistent spacing using Tailwind scale

### API Client

- Use the API module (`src/api/`) for all requests
- Leverage TypeScript types from `api/types.ts`
- Handle errors gracefully with user-friendly messages
- Show loading states during operations

## Troubleshooting

### API Connection Issues

If the frontend can't connect to the backend:

1. Verify backend is running on the correct port (default: 8000)
2. Check CORS is enabled on backend (it is by default)
3. Update `VITE_API_URL` in `.env` if backend URL differs
4. Check browser console for specific error messages

### Module Not Found Errors

Run `npm install` to ensure all dependencies are installed:
```bash
npm install
```

## Production Deployment

The built application can be served from any static hosting:

```bash
npm run build
# The dist/ folder contains the production build
```

Deploy the contents of `dist/` to your hosting platform.

## Contributing

When adding new features:

1. Create components in `src/components/`
2. Create pages in `src/pages/` for new routes
3. Add API methods in `src/api/`
4. Update types in `src/api/types.ts`
5. Follow existing code style and patterns

## License

This project is part of the Feedback Loop system.
