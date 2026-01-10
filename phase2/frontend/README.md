# Phase 2 Frontend

Next.js frontend for the Phase 2 Spec-Driven Todo System.

## Setup

1. Install dependencies:
```bash
npm install
```

2. Configure environment:
```bash
cp ../../.env.example .env.local
# Edit NEXT_PUBLIC_API_URL to point to backend
```

## Run

Development server:
```bash
npm run dev
```

Build for production:
```bash
npm run build
npm start
```

## Features

- ✅ List todos with filtering and search
- ✅ Create new todos
- ✅ Edit todos
- ✅ Delete todos
- ✅ Toggle completion status
- ✅ Responsive design (mobile, tablet, desktop)
- ✅ Loading and error states

## Environment Variables

- `NEXT_PUBLIC_API_URL`: Backend API URL (default: http://localhost:8000)
