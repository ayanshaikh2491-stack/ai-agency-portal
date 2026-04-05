# AI Agency Portal - Multi-Agent Corporate System

## Tech Stack: JavaScript + Python + Next.js ONLY

## Architecture

CEO Agent assigns tasks to departments. Departments communicate with each other. Workflows move tasks through Backend -> QA -> Frontend -> Deployment.

## Structure

```
ai-agency-portal/
├── backend/          (Python - FastAPI)
│   ├── main.py       - API server
│   ├── agents/       - Agent classes
│   ├── communication/ - Message system
│   ├── workflows/    - Workflow engine
│   └── database/     - Memory + models
└── frontend/         (JavaScript + Next.js)
    ├── app/page.js   - Main portal UI
    ├── next.config.js
    └── package.json
```

## Run

```bash
# Backend
cd ai-agency-portal/backend
pip install -r requirements.txt
python main.py

# Frontend (new terminal)
cd ai-agency-portal/frontend
npm install
npm run dev
```

## Departments
- Backend (API, databases)
- Frontend (UI, components)
- Website (full-stack)
- QA (testing)
- Marketing (content)

## Features
- CEO task assignment
- Inter-agent communication
- Workflow pipelines
- Memory system
- Issue tracking
- Knowledge base