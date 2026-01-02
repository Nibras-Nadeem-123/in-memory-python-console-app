# Quick Start Guide - Phase 1 MVP

**Estimated Time**: 10 minutes to get running

## Prerequisites

Before starting, ensure you have:

- ✅ Python 3.11 or higher ([Download](https://www.python.org/downloads/))
- ✅ Node.js 18 or higher ([Download](https://nodejs.org/))
- ✅ Git (for cloning if needed)

Verify installations:
```bash
python --version   # Should show 3.11+
node --version     # Should show 18+
npm --version      # Should show 9+
```

---

## Step 1: Navigate to Project Directory

```bash
cd /mnt/c/Users/DELL/OneDrive/Desktop/ai-driven-development/in-memory-python-console-app
```

Or from Windows:
```cmd
cd C:\Users\DELL\OneDrive\Desktop\ai-driven-development\in-memory-python-console-app
```

---

## Step 2: Start the Backend (Terminal 1)

### 2.1 Navigate to Backend Directory
```bash
cd backend
```

### 2.2 Create Virtual Environment (First Time Only)
```bash
python -m venv venv
```

### 2.3 Activate Virtual Environment

**On macOS/Linux/WSL**:
```bash
source venv/bin/activate
```

**On Windows CMD**:
```cmd
venv\Scripts\activate.bat
```

**On Windows PowerShell**:
```powershell
venv\Scripts\Activate.ps1
```

You should see `(venv)` prefix in your terminal.

### 2.4 Install Dependencies (First Time Only)
```bash
pip install -r requirements.txt
```

Expected output:
```
Installing collected packages: fastapi, uvicorn, pydantic...
Successfully installed fastapi-0.104.1 uvicorn-0.24.0 ...
```

### 2.5 Start Backend Server
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

✅ **Success indicators**:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345]
INFO:     Started server process [12346]
INFO:     Application startup complete.
```

🔗 **Backend URLs**:
- API: http://localhost:8000
- Health Check: http://localhost:8000/api/v1/health
- API Docs: http://localhost:8000/docs

**Keep this terminal open!**

---

## Step 3: Verify Backend is Running

Open a **new terminal** and test:

```bash
curl http://localhost:8000/api/v1/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "timestamp": "2025-12-31T10:30:00Z"
}
```

Or open in browser: http://localhost:8000/docs

---

## Step 4: Start the Frontend (Terminal 2)

### 4.1 Navigate to Frontend Directory (New Terminal)
```bash
cd /mnt/c/Users/DELL/OneDrive/Desktop/ai-driven-development/in-memory-python-console-app/frontend
```

### 4.2 Install Dependencies (First Time Only)
```bash
npm install
```

Expected output:
```
added 234 packages in 30s
```

This may take 1-2 minutes.

### 4.3 Start Frontend Dev Server
```bash
npm run dev
```

✅ **Success indicators**:
```
VITE v5.0.8  ready in 500 ms

➜  Local:   http://localhost:5173/
➜  Network: use --host to expose
```

🔗 **Frontend URL**: http://localhost:5173

**Keep this terminal open!**

---

## Step 5: Test the Application

### 5.1 Open Browser
Navigate to: **http://localhost:5173**

You should see:
- Title: "Spec-Driven Development System"
- Subtitle: "Phase 1: Transform your intent into a structured specification"
- Large text area for input

### 5.2 Enter Test Input

Copy and paste this test intent (exactly 100 words):

```
Create a task management application where users can create, edit, and delete tasks.
Each task should have a title, description, priority level, and due date. Users should
be able to categorize tasks using tags and filter tasks by priority or tag. The system
must support multiple users and each user should only see their own tasks. Tasks should
have three priority levels: high, medium, and low. Users must be able to search for
tasks by keyword and sort tasks by due date or priority.
```

### 5.3 Verify Word Count
- Word counter should show: **100 / 50-500 words** in green

### 5.4 Click "Generate Specification"
- Button should show "Generating..."
- Loading spinner appears
- Processing takes 1-3 seconds

### 5.5 Verify Output

You should see a structured specification with:

**✅ Goal Section** (🎯)
- Example: "Create a task management application..."

**✅ Entities Section** (📦)
- Should show: Task, User, Tag entities
- Each with type badges (Domain/Actor/Resource)
- Attributes listed (title, description, priority, etc.)
- Relationships shown (Task belongs_to User, etc.)

**✅ Constraints Section** (📋)
- Grouped by priority:
  - Must Have (red badges)
  - Should Have (orange badges)
  - Could Have (blue badges)
- Type icons (💼 Business, ⚡ Performance, etc.)

**✅ Assumptions Section** (💭)
- Yellow background
- Confidence levels (High/Medium/Low)
- "Needs Clarification" flags

**✅ Metadata Section** (📊)
- Generated timestamp
- Processing time (in milliseconds)
- Confidence score with progress bar
- Warnings (if any)

---

## Step 6: Test Error Handling

### 6.1 Test Word Count Validation

**Too Short**:
1. Clear the textarea
2. Type: "Build an app"
3. Try to submit
4. Should show error: "Intent must be at least 50 words. Current: 3 words."

**Too Long**:
1. Paste text with 600 words
2. Try to submit
3. Should show error: "Intent must be at most 500 words. Current: 600 words."

### 6.2 Test Retry Functionality
1. Stop the backend (Ctrl+C in Terminal 1)
2. Try to generate a spec
3. Should show network error with "Try Again" button
4. Restart backend
5. Click "Try Again"
6. Should work normally

---

## Troubleshooting

### Backend Issues

**Problem**: `ModuleNotFoundError: No module named 'app'`
**Solution**:
```bash
cd backend
source venv/bin/activate  # Make sure venv is activated
pwd  # Should show .../backend
ls app/  # Should list __init__.py, main.py, etc.
```

**Problem**: `Port 8000 already in use`
**Solution**:
```bash
# Use a different port
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001

# Update frontend/.env
echo "VITE_API_URL=http://localhost:8001" > frontend/.env
```

**Problem**: `ImportError: cannot import name 'UserIntent'`
**Solution**:
```bash
# Make sure you're in the backend directory
cd backend
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Frontend Issues

**Problem**: `Cannot connect to backend`
**Solution**:
1. Check backend is running: http://localhost:8000/api/v1/health
2. Check CORS in browser console (F12)
3. Verify frontend is using correct API URL

**Problem**: `npm install fails`
**Solution**:
```bash
# Clear cache
rm -rf node_modules package-lock.json
npm cache clean --force
npm install
```

**Problem**: `Port 5173 already in use`
**Solution**:
```bash
# Vite will automatically try 5174, 5175, etc.
# Or specify a port:
npm run dev -- --port 3000
```

**Problem**: TypeScript errors
**Solution**:
```bash
npm run type-check  # See specific errors
# Usually means dependencies need reinstalling
npm install
```

### General Issues

**Problem**: CORS errors in browser console
**Solution**:
- Verify backend is running on port 8000
- Check `backend/app/main.py` has correct CORS origins
- Restart both servers

**Problem**: Blank page
**Solution**:
1. Open browser DevTools (F12)
2. Check Console tab for errors
3. Check Network tab for failed requests
4. Verify both servers are running

---

## Verification Checklist

Use this checklist to verify everything works:

- [ ] Backend runs without errors on port 8000
- [ ] Health check returns JSON: http://localhost:8000/api/v1/health
- [ ] API docs load: http://localhost:8000/docs
- [ ] Frontend runs without errors on port 5173
- [ ] Home page loads with form
- [ ] Word counter updates as you type
- [ ] Validation prevents submission <50 or >500 words
- [ ] Generate button shows loading state
- [ ] Spec generates successfully (1-3 seconds)
- [ ] All sections display (Goal, Entities, Constraints, Assumptions, Metadata)
- [ ] Confidence score shows as percentage
- [ ] No console errors in browser (F12)
- [ ] Error display works when backend is down
- [ ] Retry button works

---

## Quick Test Script

Run this to test the backend API directly:

```bash
curl -X POST http://localhost:8000/api/v1/spec \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Create a task management application where users can create, edit, and delete tasks. Each task should have a title, description, priority level, and due date. Users should be able to categorize tasks using tags and filter tasks by priority or tag. The system must support multiple users and each user should only see their own tasks. Tasks should have three priority levels: high, medium, and low. Users must be able to search for tasks by keyword and sort tasks by due date or priority."
  }'
```

Expected: JSON response with `goal`, `entities`, `constraints`, `assumptions`, `metadata`

---

## Next Steps

Once everything is running:

1. **Try different intents**: Blog platform, CRM system, E-commerce site
2. **Explore the API docs**: http://localhost:8000/docs
3. **Check the code**: Start with `backend/app/main.py` and `frontend/src/App.tsx`
4. **Read the documentation**: See `MVP_COMPLETE.md` for full details

---

## Need Help?

**Backend logs**: Check Terminal 1 for error messages
**Frontend logs**: Check browser DevTools Console (F12)
**API testing**: Use http://localhost:8000/docs for interactive testing

---

## Stopping the Application

To stop the servers:

1. **Terminal 1 (Backend)**: Press `Ctrl+C`
2. **Terminal 2 (Frontend)**: Press `Ctrl+C`

To deactivate Python virtual environment:
```bash
deactivate
```

---

**Ready to build!** 🚀
