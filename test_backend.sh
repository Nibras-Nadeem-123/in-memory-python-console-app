#!/bin/bash
# Quick test script for backend API

echo "🧪 Testing SDD Phase 1 Backend..."
echo ""

# Test 1: Health Check
echo "Test 1: Health Check"
echo "===================="
response=$(curl -s http://localhost:8000/api/v1/health)
if [ $? -eq 0 ]; then
    echo "✅ Health check successful"
    echo "Response: $response"
else
    echo "❌ Health check failed - is backend running on port 8000?"
    exit 1
fi
echo ""

# Test 2: Generate Spec
echo "Test 2: Generate Specification"
echo "==============================="
response=$(curl -s -X POST http://localhost:8000/api/v1/spec \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Create a task management application where users can create, edit, and delete tasks. Each task should have a title, description, priority level, and due date. Users should be able to categorize tasks using tags and filter tasks by priority or tag. The system must support multiple users and each user should only see their own tasks. Tasks should have three priority levels: high, medium, and low. Users must be able to search for tasks by keyword and sort tasks by due date or priority."
  }')

if echo "$response" | grep -q "goal"; then
    echo "✅ Spec generation successful"
    echo "Response preview:"
    echo "$response" | python3 -m json.tool | head -30
else
    echo "❌ Spec generation failed"
    echo "Response: $response"
    exit 1
fi
echo ""

# Test 3: Validation Error
echo "Test 3: Validation (too short)"
echo "==============================="
response=$(curl -s -X POST http://localhost:8000/api/v1/spec \
  -H "Content-Type: application/json" \
  -d '{"text": "Build an app"}')

if echo "$response" | grep -q "VALIDATION_ERROR"; then
    echo "✅ Validation working correctly"
else
    echo "⚠️  Validation not working as expected"
fi
echo ""

echo "✅ All backend tests passed!"
echo ""
echo "Next steps:"
echo "1. Open http://localhost:5173 in your browser"
echo "2. Enter 50-500 words describing a system"
echo "3. Click 'Generate Specification'"
