# Docker Build Debug Script
# Use this to test Docker build and diagnose issues

echo "=== Docker Build Diagnostics ==="
echo ""
echo "1. Current directory:"
pwd
echo ""

echo "2. Checking if backend directory exists:"
if [ -d "backend" ]; then
    echo "✅ backend/ directory exists"
    ls -la backend/ | head -5
else
    echo "❌ backend/ directory NOT FOUND"
    exit 1
fi
echo ""

echo "3. Checking critical files:"
files=("backend/requirements.txt" "backend/server.py" "backend/supabase_client.py")
for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file exists"
    else
        echo "❌ $file NOT FOUND"
    fi
done
echo ""

echo "4. Checking Dockerfile:"
if [ -f "Dockerfile" ]; then
    echo "✅ Dockerfile exists"
    echo "First 10 lines:"
    head -10 Dockerfile
else
    echo "❌ Dockerfile NOT FOUND"
    exit 1
fi
echo ""

echo "5. Attempting Docker build..."
echo "Command: docker build -t getyourshare-debug ."
echo ""

docker build -t getyourshare-debug . 2>&1 | tee docker-build.log

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Build succeeded!"
    echo "Image created: getyourshare-debug"
    echo ""
    echo "To test the image:"
    echo "  docker run -p 8000:8000 -e JWT_SECRET=test-secret getyourshare-debug"
else
    echo ""
    echo "❌ Build failed. Check docker-build.log for details"
    echo ""
    echo "Last 20 lines of build log:"
    tail -20 docker-build.log
fi
