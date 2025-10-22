from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta
import jwt
from mock_data import *

app = FastAPI(title="Tracknow API")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()
JWT_SECRET = "your-secret-key-change-this-in-production-12345"
JWT_ALGORITHM = "HS256"

# Pydantic Models
class LoginRequest(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict

class MessageResponse(BaseModel):
    message: str

# Helper Functions
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=24)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Tracknow API - Mock Version", "status": "running"}

# Authentication Endpoints
@app.post("/api/auth/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    # Find user in mock data
    user = next((u for u in MOCK_USERS if u["email"] == request.email and u["password"] == request.password), None)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Create access token
    access_token = create_access_token({
        "sub": user["id"],
        "email": user["email"],
        "role": user["role"]
    })
    
    # Remove password from response
    user_data = {k: v for k, v in user.items() if k != "password"}
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_data
    }

@app.get("/api/auth/me")
async def get_current_user(payload: dict = Depends(verify_token)):
    user = next((u for u in MOCK_USERS if u["id"] == payload["sub"]), None)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user_data = {k: v for k, v in user.items() if k != "password"}
    return user_data

@app.post("/api/auth/logout")
async def logout(payload: dict = Depends(verify_token)):
    return {"message": "Logged out successfully"}

# Dashboard Endpoint
@app.get("/api/dashboard/stats")
async def get_dashboard_stats(payload: dict = Depends(verify_token)):
    return MOCK_DASHBOARD_STATS

# Advertisers Endpoints
@app.get("/api/advertisers")
async def get_advertisers(payload: dict = Depends(verify_token)):
    return {"data": MOCK_ADVERTISERS, "total": len(MOCK_ADVERTISERS)}

@app.get("/api/advertisers/{advertiser_id}")
async def get_advertiser(advertiser_id: str, payload: dict = Depends(verify_token)):
    advertiser = next((a for a in MOCK_ADVERTISERS if a["id"] == advertiser_id), None)
    if not advertiser:
        raise HTTPException(status_code=404, detail="Advertiser not found")
    return advertiser

@app.post("/api/advertisers")
async def create_advertiser(advertiser: dict, payload: dict = Depends(verify_token)):
    new_advertiser = {
        "id": f"adv_{len(MOCK_ADVERTISERS) + 1}",
        **advertiser,
        "created_at": datetime.now().isoformat()
    }
    MOCK_ADVERTISERS.append(new_advertiser)
    return new_advertiser

@app.put("/api/advertisers/{advertiser_id}")
async def update_advertiser(advertiser_id: str, advertiser: dict, payload: dict = Depends(verify_token)):
    idx = next((i for i, a in enumerate(MOCK_ADVERTISERS) if a["id"] == advertiser_id), None)
    if idx is None:
        raise HTTPException(status_code=404, detail="Advertiser not found")
    MOCK_ADVERTISERS[idx].update(advertiser)
    return MOCK_ADVERTISERS[idx]

# Campaigns Endpoints
@app.get("/api/campaigns")
async def get_campaigns(payload: dict = Depends(verify_token)):
    return {"data": MOCK_CAMPAIGNS, "total": len(MOCK_CAMPAIGNS)}

@app.get("/api/campaigns/{campaign_id}")
async def get_campaign(campaign_id: str, payload: dict = Depends(verify_token)):
    campaign = next((c for c in MOCK_CAMPAIGNS if c["id"] == campaign_id), None)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign

@app.post("/api/campaigns")
async def create_campaign(campaign: dict, payload: dict = Depends(verify_token)):
    new_campaign = {
        "id": f"camp_{len(MOCK_CAMPAIGNS) + 1}",
        **campaign,
        "clicks": 0,
        "conversions": 0,
        "revenue": 0,
        "created_at": datetime.now().isoformat()
    }
    MOCK_CAMPAIGNS.append(new_campaign)
    return new_campaign

# Affiliates Endpoints
@app.get("/api/affiliates")
async def get_affiliates(payload: dict = Depends(verify_token)):
    return {"data": MOCK_AFFILIATES, "total": len(MOCK_AFFILIATES)}

@app.get("/api/affiliates/{affiliate_id}")
async def get_affiliate(affiliate_id: str, payload: dict = Depends(verify_token)):
    affiliate = next((a for a in MOCK_AFFILIATES if a["id"] == affiliate_id), None)
    if not affiliate:
        raise HTTPException(status_code=404, detail="Affiliate not found")
    return affiliate

@app.put("/api/affiliates/{affiliate_id}/status")
async def update_affiliate_status(affiliate_id: str, data: dict, payload: dict = Depends(verify_token)):
    idx = next((i for i, a in enumerate(MOCK_AFFILIATES) if a["id"] == affiliate_id), None)
    if idx is None:
        raise HTTPException(status_code=404, detail="Affiliate not found")
    MOCK_AFFILIATES[idx]["status"] = data["status"]
    return MOCK_AFFILIATES[idx]

# Conversions Endpoints
@app.get("/api/conversions")
async def get_conversions(payload: dict = Depends(verify_token)):
    return {"data": MOCK_CONVERSIONS[:20], "total": len(MOCK_CONVERSIONS)}

# Clicks Endpoints
@app.get("/api/clicks")
async def get_clicks(payload: dict = Depends(verify_token)):
    return {"data": MOCK_CLICKS[:50], "total": len(MOCK_CLICKS)}

# Payouts Endpoints
@app.get("/api/payouts")
async def get_payouts(payload: dict = Depends(verify_token)):
    return {"data": MOCK_PAYOUTS, "total": len(MOCK_PAYOUTS)}

@app.put("/api/payouts/{payout_id}/status")
async def update_payout_status(payout_id: str, data: dict, payload: dict = Depends(verify_token)):
    idx = next((i for i, p in enumerate(MOCK_PAYOUTS) if p["id"] == payout_id), None)
    if idx is None:
        raise HTTPException(status_code=404, detail="Payout not found")
    MOCK_PAYOUTS[idx]["status"] = data["status"]
    if data["status"] == "approved":
        MOCK_PAYOUTS[idx]["processed_at"] = datetime.now().isoformat()
    return MOCK_PAYOUTS[idx]

# Coupons Endpoints
@app.get("/api/coupons")
async def get_coupons(payload: dict = Depends(verify_token)):
    return {"data": MOCK_COUPONS, "total": len(MOCK_COUPONS)}

# Settings Endpoints
@app.get("/api/settings")
async def get_settings(payload: dict = Depends(verify_token)):
    return MOCK_SETTINGS

@app.put("/api/settings")
async def update_settings(settings: dict, payload: dict = Depends(verify_token)):
    MOCK_SETTINGS.update(settings)
    return MOCK_SETTINGS

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
