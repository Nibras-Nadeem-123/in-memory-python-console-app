# Troubleshooting Guide

## Issue: "Todo system is not generated"

### Common Causes & Solutions

### 1. Input Too Short (Most Common)

**Problem**: The spec generation requires 50-500 words, but you're entering less.

**Solution**: Make sure your input has at least 50 words. The frontend shows a word counter.

**Test Input (100 words)** - Copy this:
```
Create a task management application where users can create, edit, and delete tasks.
Each task should have a title, description, priority level, and due date. Users should
be able to categorize tasks using tags and filter tasks by priority or tag. The system
must support multiple users and each user should only see their own tasks. Tasks should
have three priority levels: high, medium, and low. Users must be able to search for
tasks by keyword and sort tasks by due date or priority.
```

### 2. Backend Not Running

**Check**: Is the backend running?
```bash
curl http://localhost:8000/api/v1/health
```

**Expected**: `{"status":"healthy","version":"0.1.0",...}`

**If not working**:
```bash
cd backend
./venv/bin/uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Frontend Can't Connect to Backend

**Check Browser Console**:
1. Press F12 (Developer Tools)
2. Go to "Console" tab
3. Look for red errors like "Failed to fetch" or "CORS error"

**Common Issues**:

**A. Backend URL Wrong**
- Frontend expects backend at: `http://localhost:8000`
- Check: `frontend/.env` should have `VITE_API_URL=http://localhost:8000`

**B. CORS Issue**
- Backend must allow `http://localhost:5173`
- Check: `backend/app/main.py` line 50-55 has correct CORS config

### 4. Frontend Not Displaying Results

**Check Network Tab**:
1. Press F12 (Developer Tools)
2. Go to "Network" tab
3. Submit a spec generation request
4. Look for `POST /api/v1/spec` request
5. Click on it and check:
   - Status: Should be `200 OK`
   - Response: Should show JSON with `goal`, `entities`, etc.

**If Status is 400**: Input validation failed (too short/too long)
**If Status is 500**: Backend error (check backend logs)
**If No request appears**: Frontend not sending request (JS error)

### 5. Word Count Not Updating

**Problem**: You type but word counter stays at 0

**Solution**:
- Make sure you're typing in the textarea (not elsewhere)
- Try refreshing the page
- Check browser console for JavaScript errors

## Step-by-Step Debugging

### Step 1: Verify Backend

```bash
# Test health endpoint
curl http://localhost:8000/api/v1/health

# Test spec generation (100 words)
curl -X POST http://localhost:8000/api/v1/spec \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Create a task management application where users can create, edit, and delete tasks. Each task should have a title, description, priority level, and due date. Users should be able to categorize tasks using tags and filter tasks by priority or tag. The system must support multiple users and each user should only see their own tasks. Tasks should have three priority levels: high, medium, and low. Users must be able to search for tasks by keyword and sort tasks by due date or priority."
  }'
```

**Expected**: JSON response with entities, constraints, etc.

### Step 2: Verify Frontend

1. Open: http://localhost:5173
2. Should see form with textarea
3. Type some text
4. Word counter should update
5. If < 50 words, submit button should be disabled

### Step 3: Test Complete Flow

1. Copy the 100-word test input above
2. Paste into frontend textarea
3. Word counter should show: **100 / 50-500 words** in green
4. Click "Generate Specification"
5. Should see loading spinner
6. After 1-3 seconds, see structured output

### Step 4: Check Browser Console

Press F12 and look for:

**✅ Good signs**:
```
Spec generated successfully: {goal: "...", entities: [...]}
```

**❌ Bad signs**:
```
Error: Network request failed
Error: Failed to fetch
CORS policy blocked
TypeError: Cannot read property
```

## Quick Fixes

### Fix 1: Restart Everything

```bash
# Kill backend
ps aux | grep uvicorn | grep -v grep | awk '{print $2}' | xargs kill

# Restart backend
cd backend
./venv/bin/uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# In another terminal, restart frontend
cd frontend
npm run dev
```

### Fix 2: Clear Browser Cache

1. Press Ctrl+Shift+Delete (or Cmd+Shift+Delete on Mac)
2. Clear cached images and files
3. Refresh page

### Fix 3: Check Ports

```bash
# Is backend on 8000?
lsof -i :8000

# Is frontend on 5173?
lsof -i :5173
```

Both should show active processes.

## Error Messages & Meanings

### Frontend Errors

**"Intent must be at least 50 words"**
- **Meaning**: Input too short
- **Fix**: Add more text

**"Cannot connect to the API server"**
- **Meaning**: Frontend can't reach backend
- **Fix**: Check backend is running on port 8000

**"Ambiguous intent"**
- **Meaning**: Backend couldn't extract enough information
- **Fix**: Provide more detailed description

### Backend Errors

**"VALIDATION_ERROR"**
- **Meaning**: Input doesn't meet requirements (word count)
- **Fix**: Check input length

**"INTERNAL_ERROR"**
- **Meaning**: Unexpected error in backend
- **Fix**: Check backend logs for details

## Still Not Working?

### Collect Diagnostics

Run these and share output:

```bash
# 1. Backend health
curl http://localhost:8000/api/v1/health

# 2. Backend test
curl -X POST http://localhost:8000/api/v1/spec \
  -H "Content-Type: application/json" \
  -d '{"text": "Create a task management application where users can create, edit, and delete tasks. Each task should have a title, description, priority level, and due date. Users should be able to categorize tasks using tags and filter tasks by priority or tag. The system must support multiple users and each user should only see their own tasks. Tasks should have three priority levels: high, medium, and low. Users must be able to search for tasks by keyword and sort tasks by due date or priority."}'

# 3. Frontend accessibility
curl -I http://localhost:5173

# 4. Check processes
ps aux | grep -E "uvicorn|vite"
```

### Check Browser Console

1. Open http://localhost:5173
2. Press F12
3. Go to Console tab
4. Try generating spec
5. Copy any error messages

---

## Quick Success Test

Try this exact sequence:

1. **Backend**:
```bash
cd backend
./venv/bin/uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
Wait for "Application startup complete"

2. **Test backend**:
```bash
curl http://localhost:8000/api/v1/health
```
Should return healthy status

3. **Frontend** (new terminal):
```bash
cd frontend
npm run dev
```
Wait for "Local: http://localhost:5173/"

4. **Open browser**: http://localhost:5173

5. **Paste this exact text**:
```
Create a task management application where users can create, edit, and delete tasks. Each task should have a title, description, priority level, and due date. Users should be able to categorize tasks using tags and filter tasks by priority or tag. The system must support multiple users and each user should only see their own tasks. Tasks should have three priority levels: high, medium, and low. Users must be able to search for tasks by keyword and sort tasks by due date or priority.
```

6. **Click "Generate Specification"**

Should work! If not, check browser console (F12) for errors.

---

**Most common issue**: Input is less than 50 words. The system needs detailed descriptions!
