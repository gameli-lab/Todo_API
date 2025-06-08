#!/bin/bash
# API Test Script for Todo API

# Base URL
BASE_URL="http://localhost:8000/api"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}===== Todo API Testing =====${NC}"
echo

# 1. Register a new user
echo -e "${GREEN}1. Registering a new user...${NC}"
REGISTER_RESPONSE=$(curl -s -X POST $BASE_URL/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "fullname": "Test User",
    "email": "test@example.com",
    "phone": "1234567890",
    "password": "securepassword123",
    "confirm_password": "securepassword123"
  }')

echo $REGISTER_RESPONSE | python -m json.tool
echo

# 2. Login to get access token
echo -e "${GREEN}2. Logging in...${NC}"
LOGIN_RESPONSE=$(curl -s -X POST $BASE_URL/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "securepassword123"
  }')

echo $LOGIN_RESPONSE | python -m json.tool
echo

# Extract tokens from login response
ACCESS_TOKEN=$(echo $LOGIN_RESPONSE | python -c "import sys, json; print(json.load(sys.stdin)['access'])")
REFRESH_TOKEN=$(echo $LOGIN_RESPONSE | python -c "import sys, json; print(json.load(sys.stdin)['refresh'])")

echo "Access Token: ${ACCESS_TOKEN:0:15}..."
echo "Refresh Token: ${REFRESH_TOKEN:0:15}..."
echo

# 3. Create a new task
echo -e "${GREEN}3. Creating a new task...${NC}"
CREATE_RESPONSE=$(curl -s -X POST $BASE_URL/tasks/ \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Complete API testing",
    "description": "Test all endpoints using curl",
    "due_date": "2025-12-31"
  }')

echo $CREATE_RESPONSE | python -m json.tool
echo

# Extract task ID from create response
TASK_ID=$(echo $CREATE_RESPONSE | python -c "import sys, json; print(json.load(sys.stdin)['data']['id'])")
echo "Created task with ID: $TASK_ID"
echo

# 4. List all tasks
echo -e "${GREEN}4. Listing all tasks...${NC}"
LIST_RESPONSE=$(curl -s -X GET $BASE_URL/tasks/ \
  -H "Authorization: Bearer $ACCESS_TOKEN")

echo $LIST_RESPONSE | python -m json.tool
echo

# 5. Get a specific task
echo -e "${GREEN}5. Getting task with ID $TASK_ID...${NC}"
GET_RESPONSE=$(curl -s -X GET $BASE_URL/tasks/$TASK_ID/ \
  -H "Authorization: Bearer $ACCESS_TOKEN")

echo $GET_RESPONSE | python -m json.tool
echo

# 6. Update a task
echo -e "${GREEN}6. Updating task with ID $TASK_ID...${NC}"
UPDATE_RESPONSE=$(curl -s -X PUT $BASE_URL/tasks/$TASK_ID/ \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Updated: Complete API testing",
    "description": "Testing PUT endpoint using curl",
    "due_date": "2025-12-25"
  }')

echo $UPDATE_RESPONSE | python -m json.tool
echo

# 7. Update just the status of a task
echo -e "${GREEN}7. Updating status of task with ID $TASK_ID...${NC}"
STATUS_RESPONSE=$(curl -s -X PATCH $BASE_URL/tasks/$TASK_ID/status/ \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "in_progress"
  }')

echo $STATUS_RESPONSE | python -m json.tool
echo

# 8. Filter tasks by status
echo -e "${GREEN}8. Filtering tasks by status 'in_progress'...${NC}"
FILTER_RESPONSE=$(curl -s -X GET "$BASE_URL/tasks/?status=in_progress" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

echo $FILTER_RESPONSE | python -m json.tool
echo

# 9. Search tasks
echo -e "${GREEN}9. Searching tasks with keyword 'API'...${NC}"
SEARCH_RESPONSE=$(curl -s -X GET "$BASE_URL/tasks/?search=API" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

echo $SEARCH_RESPONSE | python -m json.tool
echo

# 10. Order tasks by due date
echo -e "${GREEN}10. Ordering tasks by due date (descending)...${NC}"
ORDER_RESPONSE=$(curl -s -X GET "$BASE_URL/tasks/?ordering=-due_date" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

echo $ORDER_RESPONSE | python -m json.tool
echo

# 11. Delete a task
echo -e "${GREEN}11. Deleting task with ID $TASK_ID...${NC}"
DELETE_RESPONSE=$(curl -s -X DELETE $BASE_URL/tasks/$TASK_ID/ \
  -H "Authorization: Bearer $ACCESS_TOKEN")

echo $DELETE_RESPONSE | python -m json.tool
echo

# 12. Verify task was deleted
echo -e "${GREEN}12. Verifying task was deleted...${NC}"
VERIFY_DELETE=$(curl -s -X GET $BASE_URL/tasks/$TASK_ID/ \
  -H "Authorization: Bearer $ACCESS_TOKEN")

echo $VERIFY_DELETE | python -m json.tool
echo

echo -e "${GREEN}===== Test Complete =====${NC}"
