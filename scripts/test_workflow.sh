#!/bin/bash

# Feedback Loop API - End-to-End Test Workflow
# This script demonstrates the complete workflow from project creation to AI feedback processing

set -e

API_URL="${API_URL:-http://localhost:8000}"
BOLD='\033[1m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BOLD}Feedback Loop API - Test Workflow${NC}"
echo "=================================="
echo ""

# Check if API is running
echo -e "${BLUE}Checking API availability...${NC}"
if ! curl -s "$API_URL/health" > /dev/null; then
    echo "Error: API is not running at $API_URL"
    echo "Start it with: docker-compose up -d"
    exit 1
fi
echo -e "${GREEN}✓ API is running${NC}"
echo ""

# Create a project
echo -e "${BLUE}1. Creating project...${NC}"
PROJECT_RESPONSE=$(curl -s -X POST "$API_URL/projects/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Project - E-Commerce Upgrade",
    "description": "Testing the feedback loop system",
    "status": "active"
  }')

PROJECT_ID=$(echo "$PROJECT_RESPONSE" | jq -r '.id')
echo -e "${GREEN}✓ Project created with ID: $PROJECT_ID${NC}"
echo ""

# Create tasks
echo -e "${BLUE}2. Creating tasks...${NC}"

TASK1_RESPONSE=$(curl -s -X POST "$API_URL/tasks/" \
  -H "Content-Type: application/json" \
  -d "{
    \"project_id\": $PROJECT_ID,
    \"title\": \"Implement new search functionality\",
    \"description\": \"Add advanced filtering and faceted search\",
    \"status\": \"in_progress\",
    \"priority\": 7,
    \"estimated_hours\": 80
  }")
TASK1_ID=$(echo "$TASK1_RESPONSE" | jq -r '.id')
echo -e "${GREEN}✓ Task 1 created: Implement search (ID: $TASK1_ID)${NC}"

TASK2_RESPONSE=$(curl -s -X POST "$API_URL/tasks/" \
  -H "Content-Type: application/json" \
  -d "{
    \"project_id\": $PROJECT_ID,
    \"title\": \"Optimize database queries\",
    \"description\": \"Improve query performance\",
    \"status\": \"todo\",
    \"priority\": 5,
    \"estimated_hours\": 40
  }")
TASK2_ID=$(echo "$TASK2_RESPONSE" | jq -r '.id')
echo -e "${GREEN}✓ Task 2 created: Database optimization (ID: $TASK2_ID)${NC}"

TASK3_RESPONSE=$(curl -s -X POST "$API_URL/tasks/" \
  -H "Content-Type: application/json" \
  -d "{
    \"project_id\": $PROJECT_ID,
    \"title\": \"Update payment gateway\",
    \"description\": \"Migrate to new payment provider\",
    \"status\": \"todo\",
    \"priority\": 9,
    \"estimated_hours\": 100
  }")
TASK3_ID=$(echo "$TASK3_RESPONSE" | jq -r '.id')
echo -e "${GREEN}✓ Task 3 created: Payment gateway (ID: $TASK3_ID)${NC}"
echo ""

# View project
echo -e "${BLUE}3. Viewing project with tasks...${NC}"
PROJECT_DETAILS=$(curl -s "$API_URL/projects/$PROJECT_ID")
echo "$PROJECT_DETAILS" | jq '.'
echo ""

# Submit feedback
echo -e "${BLUE}4. Submitting feedback...${NC}"
FEEDBACK_RESPONSE=$(curl -s -X POST "$API_URL/feedback/" \
  -H "Content-Type: application/json" \
  -d "{
    \"project_id\": $PROJECT_ID,
    \"task_id\": $TASK1_ID,
    \"user_name\": \"Test User\",
    \"feedback_text\": \"The search task is too complex and taking too long. We should break it into smaller pieces: first deploy a basic search, then add advanced features. Also, the database optimization should be higher priority since it's blocking performance improvements. The payment gateway work is critical but we need to ensure we have proper testing in place before deployment.\"
  }")

FEEDBACK_ID=$(echo "$FEEDBACK_RESPONSE" | jq -r '.feedback_id')
CELERY_TASK_ID=$(echo "$FEEDBACK_RESPONSE" | jq -r '.task_id')
echo -e "${GREEN}✓ Feedback submitted (ID: $FEEDBACK_ID)${NC}"
echo "  Celery Task ID: $CELERY_TASK_ID"
echo ""

# Wait for processing
echo -e "${BLUE}5. Waiting for AI processing...${NC}"
echo "This may take 10-30 seconds depending on OpenAI API response time..."
MAX_ATTEMPTS=30
ATTEMPT=0

while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
    FEEDBACK_STATUS=$(curl -s "$API_URL/feedback/$FEEDBACK_ID" | jq -r '.status')
    
    if [ "$FEEDBACK_STATUS" = "completed" ]; then
        echo -e "${GREEN}✓ Processing completed!${NC}"
        break
    elif [ "$FEEDBACK_STATUS" = "failed" ]; then
        echo -e "Error: Processing failed"
        exit 1
    fi
    
    echo -n "."
    sleep 1
    ATTEMPT=$((ATTEMPT + 1))
done
echo ""

if [ $ATTEMPT -eq $MAX_ATTEMPTS ]; then
    echo "Warning: Processing is taking longer than expected"
    echo "Check worker logs: docker-compose logs celery_worker"
fi
echo ""

# View results
echo -e "${BLUE}6. Viewing AI-generated adjustments...${NC}"
FEEDBACK_DETAILS=$(curl -s "$API_URL/feedback/$FEEDBACK_ID")
echo "$FEEDBACK_DETAILS" | jq '.'
echo ""

# Summary
echo -e "${BOLD}Summary${NC}"
echo "======="
ADJUSTMENT_COUNT=$(echo "$FEEDBACK_DETAILS" | jq '.adjustments | length')
echo -e "Total adjustments suggested: ${GREEN}$ADJUSTMENT_COUNT${NC}"
echo ""

if [ "$ADJUSTMENT_COUNT" -gt 0 ]; then
    echo "Adjustments:"
    echo "$FEEDBACK_DETAILS" | jq -r '.adjustments[] | "- [\(.adjustment_type)] \(.description)"'
fi
echo ""

echo -e "${BOLD}Test Complete! 🎉${NC}"
echo ""
echo "Next steps:"
echo "1. View all feedback: curl $API_URL/feedback/"
echo "2. View project: curl $API_URL/projects/$PROJECT_ID"
echo "3. Apply suggested adjustments manually or programmatically"
echo "4. Submit more feedback to see different AI suggestions"
echo ""
echo "Clean up:"
echo "  curl -X DELETE $API_URL/projects/$PROJECT_ID"
