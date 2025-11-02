from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="ShareYourSales API - Test",
    description="API de test pour ShareYourSales",
    version="1.0.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "ShareYourSales API is running!", "status": "success"}

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "ShareYourSales Backend",
        "version": "1.0.0"
    }

@app.get("/api/test")
async def test_endpoint():
    return {
        "message": "Test endpoint working!",
        "data": {
            "frontend_url": "http://localhost:3000",
            "backend_url": "http://localhost:8000"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)