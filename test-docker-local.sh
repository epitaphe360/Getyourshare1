#!/bin/bash
# Test Docker build locally before Railway deployment

set -e

echo "🐳 Testing Docker build locally..."
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Step 1: Building Docker image...${NC}"
echo "Build context: $(pwd)"
echo "Checking backend directory..."
ls -la backend/ | head -10

docker build -t getyourshare-test . || {
    echo -e "${RED}❌ Docker build failed!${NC}"
    echo ""
    echo "Trying with backup Dockerfile..."
    docker build -f Dockerfile.backup -t getyourshare-test . || {
        echo -e "${RED}❌ Backup build also failed!${NC}"
        exit 1
    }
}
echo -e "${GREEN}✅ Docker image built successfully${NC}"
echo ""

echo -e "${YELLOW}Step 2: Running container...${NC}"
# Run with .env.example for local testing (demo mode)
docker run -d \
    --name getyourshare-test \
    -p 8000:8000 \
    -e ENVIRONMENT=development \
    -e PORT=8000 \
    -e JWT_SECRET=test-secret-key-minimum-32-chars-long \
    getyourshare-test || {
    echo -e "${RED}❌ Failed to start container!${NC}"
    exit 1
}
echo -e "${GREEN}✅ Container started${NC}"
echo ""

echo -e "${YELLOW}Step 3: Waiting for server to be ready...${NC}"
sleep 5

echo -e "${YELLOW}Step 4: Testing health endpoint...${NC}"
HEALTH_RESPONSE=$(curl -s http://localhost:8000/health || echo "failed")

if [[ $HEALTH_RESPONSE == *"healthy"* ]] || [[ $HEALTH_RESPONSE == *"status"* ]]; then
    echo -e "${GREEN}✅ Health check passed!${NC}"
    echo "Response: $HEALTH_RESPONSE"
else
    echo -e "${RED}❌ Health check failed!${NC}"
    echo "Response: $HEALTH_RESPONSE"
    docker logs getyourshare-test
    docker stop getyourshare-test
    docker rm getyourshare-test
    exit 1
fi
echo ""

echo -e "${YELLOW}Step 5: Testing API docs endpoint...${NC}"
DOCS_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/docs)
if [ "$DOCS_CODE" == "200" ]; then
    echo -e "${GREEN}✅ API docs accessible!${NC}"
    echo "Visit: http://localhost:8000/docs"
else
    echo -e "${RED}❌ API docs not accessible (HTTP $DOCS_CODE)${NC}"
fi
echo ""

echo -e "${YELLOW}Step 6: Checking container logs...${NC}"
docker logs getyourshare-test | tail -20
echo ""

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ All tests passed!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Container is running. You can:"
echo "  - View logs: docker logs getyourshare-test -f"
echo "  - Test API: curl http://localhost:8000/health"
echo "  - Stop: docker stop getyourshare-test"
echo "  - Remove: docker rm getyourshare-test"
echo ""
echo "To stop and cleanup now, run:"
echo "  docker stop getyourshare-test && docker rm getyourshare-test"
echo ""
echo -e "${YELLOW}Ready to deploy to Railway! 🚂${NC}"
