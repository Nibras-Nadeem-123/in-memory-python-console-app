# How to Run Phase 1 - Quick Reference

## 🚀 3-Step Quick Start

### Step 1: Start Backend (Terminal 1)
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```


**✅ Success**: See "Application startup complete" → Backend ready at http://localhost:8000

### Step 2: Start Frontend (Terminal 2)
```bash
cd frontend
npm install
npm run dev
```

**✅ Success**: See "Local: http://localhost:5173/" → Frontend ready

### Step 3: Test in Browser
1. Open: http://localhost:5173
2. Paste this 100-word test:
```
Create a task management application where users can create, edit, and delete tasks.
Each task should have a title, description, priority level, and due date. Users should
be able to categorize tasks using tags and filter tasks by priority or tag. The system
must support multiple users and each user should only see their own tasks. Tasks should
have three priority levels: high, medium, and low. Users must be able to search for
tasks by keyword and sort tasks by due date or priority.
```
3. Click "Generate Specification"
4. ✅ See structured output in 1-3 seconds

---

## 🔍 Quick Health Check

**Backend**:
```bash
curl http://localhost:8000/api/v1/health
# Should return: {"status":"healthy","version":"0.1.0",...}
```

**Frontend**:
- Open http://localhost:5173
- Should show input form with word counter

**API Docs**:
- Open http://localhost:8000/docs
- Interactive API testing interface

---

## 📋 What You Should See

### Backend Terminal Output:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
INFO:     SDD Phase 1 Backend API starting up...
```

### Frontend Terminal Output:
```
VITE v5.0.8  ready in 500 ms
➜  Local:   http://localhost:5173/
```

### Browser (http://localhost:5173):
```
┌─────────────────────────────────────────┐
│ Spec-Driven Development System          │
│ Phase 1: Transform your intent into     │
│         a structured specification      │
├─────────────────────────────────────────┤
│                                         │
│  Describe your system intent            │
│  ┌─────────────────────────────────┐   │
│  │ [Large text area for input]     │   │
│  │                                 │   │
│  │                                 │   │
│  └─────────────────────────────────┘   │
│  0 / 50-500 words                      │
│                                         │
│  [Generate Specification] button        │
│                                         │
└─────────────────────────────────────────┘
```

### After Submitting:
```
┌─────────────────────────────────────────┐
│ Generated Specification    [85% ✓]      │
├─────────────────────────────────────────┤
│ 🎯 Goal                                 │
│   Build a task management system...     │
├─────────────────────────────────────────┤
│ 📦 Entities (3)                         │
│   ┌─Task─────────────────[Domain]──┐   │
│   │ Attributes: title, priority... │   │
│   └────────────────────────────────┘   │
│   ┌─User─────────────────[Actor]───┐   │
│   └────────────────────────────────┘   │
│   ┌─Tag──────────────────[Resource]┐   │
│   └────────────────────────────────┘   │
├─────────────────────────────────────────┤
│ 📋 Constraints (5)                      │
│   Must Have (3)                         │
│   Should Have (2)                       │
├─────────────────────────────────────────┤
│ 💭 Assumptions (3)                      │
│   ⚠️ Needs clarification                │
├─────────────────────────────────────────┤
│ 📊 Metadata                             │
│   Processing: 234ms                     │
│   Confidence: 85%                       │
└─────────────────────────────────────────┘
```

---

## 🧪 Quick Backend Test

```bash
# Make script executable
chmod +x test_backend.sh

# Run tests
./test_backend.sh
```

Expected output:
```
🧪 Testing SDD Phase 1 Backend...

Test 1: Health Check
====================
✅ Health check successful

Test 2: Generate Specification
===============================
✅ Spec generation successful

Test 3: Validation (too short)
===============================
✅ Validation working correctly

✅ All backend tests passed!
```

---

## ❌ Common Issues & Fixes

### Issue 1: "Port already in use"
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Or use different port
uvicorn app.main:app --reload --port 8001
```

### Issue 2: "Module not found"
```bash
# Make sure you're in backend/ directory
pwd  # Should show .../backend

# Activate venv
source venv/bin/activate

# Reinstall
pip install -r requirements.txt
```

### Issue 3: "Cannot connect to backend"
```bash
# Verify backend is running
curl http://localhost:8000/api/v1/health

# Check CORS - backend should allow http://localhost:5173
# See backend/app/main.py line 50
```

### Issue 4: Frontend blank page
```bash
# Check browser console (F12)
# Usually means:
# 1. Backend not running
# 2. Wrong API URL
# 3. Missing dependencies

# Fix:
cd frontend
rm -rf node_modules
npm install
npm run dev
```

---

## 📂 Project Structure

```
.
├── backend/
│   ├── app/
│   │   ├── main.py          ← Start here
│   │   ├── api/spec.py      ← API endpoints
│   │   ├── core/            ← Engine, SpecBuilder
│   │   ├── models/          ← Data models
│   │   └── skills/          ← 4 NLP skills
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── App.tsx          ← Main component
│   │   ├── components/      ← 8 UI components
│   │   ├── api/client.ts    ← API calls
│   │   └── hooks/           ← React Query
│   └── package.json
│
├── QUICKSTART.md            ← Detailed guide
├── HOW_TO_RUN.md           ← This file
└── MVP_COMPLETE.md         ← Full documentation
```

---

## 🎯 Success Checklist

- [ ] Backend starts without errors
- [ ] Health endpoint returns JSON
- [ ] Frontend loads at http://localhost:5173
- [ ] Can type in text area
- [ ] Word counter updates
- [ ] Generate button works
- [ ] Spec appears in 1-3 seconds
- [ ] All sections display correctly
- [ ] No console errors (F12)

---

## 📚 More Help

- **Detailed Setup**: See `QUICKSTART.md`
- **Full Documentation**: See `MVP_COMPLETE.md`
- **API Testing**: http://localhost:8000/docs
- **Backend Code**: Start at `backend/app/main.py`
- **Frontend Code**: Start at `frontend/src/App.tsx`

---

## 🎉 You're Ready!

Once both servers are running and the browser shows the form, you're good to go!

Try different system descriptions:
- Todo app with priorities
- Blog platform with comments
- CRM system with leads
- E-commerce store with cart

The system will extract entities, constraints, and assumptions from any description!

**Happy spec generating!** 🚀
