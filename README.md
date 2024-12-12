# Gantt Chart Project Manager

A full-stack web application for creating and managing project timelines using interactive Gantt charts. The application allows users to create projects, add tasks with responsibilities, and visualize project timelines in a dynamic Gantt chart format.

## Features

- Create and manage multiple projects
- Add tasks with start dates, end dates, and responsibilities
- Interactive Gantt chart visualization
- Dynamic width adjustment for task names
- Horizontal scrolling for long timelines
- Download charts in SVG or JPEG format
- Responsive design

## Tech Stack

### Frontend
- Vue.js 3 with TypeScript
- D3.js for Gantt chart visualization
- Vite for development and building

### Backend
- FastAPI (Python)
- Matplotlib for chart generation
- SQLite for data storage

## Project Structure

```
.
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI application
│   │   └── schemas.py       # Data models
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── GanttChart.vue   # Gantt chart component
│   │   │   ├── ProjectForm.vue  # Project creation form
│   │   │   └── TaskForm.vue     # Task management form
│   │   ├── types/
│   │   │   └── index.ts         # TypeScript definitions
│   │   └── App.vue             # Main application component
│   ├── package.json
│   └── vite.config.ts
├── start_servers.sh         # Script to start both servers
└── README.md
```

## Setup and Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd gantt-chart
   ```

2. Set up the backend:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Set up the frontend:
   ```bash
   cd frontend
   npm install
   ```

4. Start both servers:
   ```bash
   ./start_servers.sh
   ```
   This will start:
   - Backend server at http://localhost:8000
   - Frontend server at http://localhost:5173

## Usage

1. **Create a New Project**
   - Click "New Project" button
   - Enter project name and description
   - Add tasks with their details:
     - Task name
     - Responsibility
     - Start date
     - End date
     - Progress percentage

2. **View and Edit Projects**
   - All projects are listed on the main page
   - Click on a project to view its Gantt chart
   - Edit tasks or project details using the edit buttons
   - Download the Gantt chart in SVG or JPEG format

3. **Gantt Chart Features**
   - Horizontal scrolling for long timelines
   - Dynamic left margin that adjusts to task name length
   - Color-coded tasks by responsibility
   - Progress indicators within task bars
   - Weekly date markers
   - Vertical grid lines for better date tracking

## API Endpoints

- `GET /projects/` - List all projects
- `POST /projects/` - Create a new project
- `GET /projects/{id}` - Get project details
- `PUT /projects/{id}` - Update project
- `DELETE /projects/{id}` - Delete project
- `POST /generate-chart/` - Generate Gantt chart
- `GET /download-chart/` - Download generated chart

## Development

- Backend development server (with auto-reload):
  ```bash
  cd backend
  uvicorn app.main:app --reload --port 8000
  ```

- Frontend development server:
  ```bash
  cd frontend
  npm run dev
  ```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
