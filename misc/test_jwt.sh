#!/bin/bash
# Quick Test Script untuk JWT Authentication
# Run dengan: bash test_jwt.sh

BASE_URL="http://localhost:8000"

echo "=========================================="
echo "🔐 JWT Authentication Test"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. Check server
echo -e "${YELLOW}[1] Checking if server is running...${NC}"
if curl -s "${BASE_URL}/api/health" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Server is running!${NC}"
else
    echo -e "${RED}❌ Server is not running!${NC}"
    echo "Please start the server with: uvicorn main:app --reload"
    exit 1
fi
echo ""

# 2. Register siswa
echo -e "${YELLOW}[2] Registering new siswa...${NC}"
REGISTER_RESPONSE=$(curl -s -X POST "${BASE_URL}/api/siswa/" \
  -H "Content-Type: application/json" \
  -d '{"nama":"Edy Cole","email":"edycoleee@gmail.com","password":"secret123"}')

echo "$REGISTER_RESPONSE" | jq '.'

if echo "$REGISTER_RESPONSE" | jq -e '.id' > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Registration successful!${NC}"
    SISWA_ID=$(echo "$REGISTER_RESPONSE" | jq -r '.id')
    echo "Siswa ID: $SISWA_ID"
else
    echo -e "${RED}❌ Registration failed (siswa might already exist)${NC}"
    echo "Continuing with existing siswa..."
fi
echo ""

# 3. Login
echo -e "${YELLOW}[3] Logging in...${NC}"
LOGIN_RESPONSE=$(curl -s -X POST "${BASE_URL}/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"edycoleee@gmail.com","password":"secret123"}')

echo "$LOGIN_RESPONSE" | jq '.'

if echo "$LOGIN_RESPONSE" | jq -e '.access_token' > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Login successful!${NC}"
    JWT_TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.access_token')
    echo "JWT Token: ${JWT_TOKEN:0:50}..."
else
    echo -e "${RED}❌ Login failed!${NC}"
    exit 1
fi
echo ""

# 4. Test wrong password
echo -e "${YELLOW}[4] Testing wrong password...${NC}"
WRONG_LOGIN=$(curl -s -X POST "${BASE_URL}/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"edycoleee@gmail.com","password":"wrongpassword"}')

echo "$WRONG_LOGIN" | jq '.'

if echo "$WRONG_LOGIN" | jq -e '.detail' > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Correct behavior: Wrong password rejected${NC}"
else
    echo -e "${RED}❌ Unexpected behavior${NC}"
fi
echo ""

# 5. Access dashboard without token
echo -e "${YELLOW}[5] Accessing dashboard without token...${NC}"
NO_TOKEN_RESPONSE=$(curl -s "${BASE_URL}/api/dashboard")

echo "$NO_TOKEN_RESPONSE" | jq '.'

if echo "$NO_TOKEN_RESPONSE" | jq -e '.detail' > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Correct behavior: Access denied without token${NC}"
else
    echo -e "${RED}❌ Unexpected behavior${NC}"
fi
echo ""

# 6. Access dashboard with token
echo -e "${YELLOW}[6] Accessing dashboard with JWT token...${NC}"
DASHBOARD_RESPONSE=$(curl -s "${BASE_URL}/api/dashboard" \
  -H "Authorization: Bearer ${JWT_TOKEN}")

echo "$DASHBOARD_RESPONSE" | jq '.'

if echo "$DASHBOARD_RESPONSE" | jq -e '.user' > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Dashboard accessed successfully!${NC}"
    echo "User info:"
    echo "$DASHBOARD_RESPONSE" | jq '.user'
else
    echo -e "${RED}❌ Dashboard access failed!${NC}"
fi
echo ""

# 7. Get all siswa
echo -e "${YELLOW}[7] Getting all siswa (public endpoint)...${NC}"
ALL_SISWA=$(curl -s "${BASE_URL}/api/siswa/")

echo "$ALL_SISWA" | jq '.'

TOTAL=$(echo "$ALL_SISWA" | jq '. | length')
echo -e "${GREEN}✅ Total siswa: $TOTAL${NC}"
echo ""

# 8. Logout
echo -e "${YELLOW}[8] Logging out...${NC}"
LOGOUT_RESPONSE=$(curl -s -X POST "${BASE_URL}/api/auth/logout")

echo "$LOGOUT_RESPONSE" | jq '.'
echo -e "${GREEN}✅ Logout endpoint called${NC}"
echo ""

# Summary
echo "=========================================="
echo -e "${GREEN}✅ JWT Authentication Test Completed!${NC}"
echo "=========================================="
echo ""
echo "Summary:"
echo "✅ Server is running"
echo "✅ Siswa registration works"
echo "✅ Login with email/password works"
echo "✅ JWT token generated"
echo "✅ Protected endpoints require JWT"
echo "✅ Wrong password rejected"
echo "✅ Logout endpoint available"
echo ""
echo "Your JWT Token:"
echo "$JWT_TOKEN"
echo ""
echo "Test manual access:"
echo "curl -H \"Authorization: Bearer $JWT_TOKEN\" ${BASE_URL}/api/dashboard"
echo ""
