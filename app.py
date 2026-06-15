import os
from fastapi import FastAPI, HTTPException, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agent import generate_video_pipeline

app = FastAPI()

# Enable CORS so your frontend can communicate with this backend securely
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock database for user credits
USER_DATABASE = {
    "default_user": {"credits": 1000}
}

class GenerationRequest(BaseModel):
    prompt: str
    user_id: str = "default_user"

@app.get("/")
def read_root():
    return {"status": "running", "service": "AI Video Generator API"}

@app.post("/api/generate")
def generate_video(payload: GenerationRequest):
    user_id = payload.user_id
    
    if user_id not in USER_DATABASE:
        raise HTTPException(status_code=404, detail="User not found")
        
    # Check if user has enough credits (15 credits per video generation)
    if USER_DATABASE[user_id]["credits"] < 15:
        raise HTTPException(status_code=400, detail="Insufficient credits")
        
    # Deduct credits
    USER_DATABASE[user_id]["credits"] -= 15
    
    try:
        # Trigger the video pipeline from agent.py
        result = generate_video_pipeline(payload.prompt)
        return {
            "status": "success",
            "blueprint": result["blueprint"],
            "videos": result["videos"],
            "credits_remaining": USER_DATABASE[user_id]["credits"]
        }
    except Exception as e:
        # Refund credits if generation fails
        USER_DATABASE[user_id]["credits"] += 15
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/flutterwave-webhook")
async def flutterwave_webhook(request: Request, flw_signature: str = Header(None)):
    # Simple simulation of Flutterwave webhook event verification
    # In a real app, you verify 'flw_signature' against your secret hash
    try:
        payload = await request.json()
        
        # Example structure update: add 1000 credits upon successful transaction
        user_id = "default_user" 
        if payload.get("status") == "successful" or payload.get("data", {}).get("status") == "successful":
            USER_DATABASE[user_id]["credits"] += 1000
            print(f"Webhook Success: Credited 1000 points to {user_id}")
            return {"status": "verified", "message": "Credits applied"}
            
        return {"status": "ignored", "message": "Transaction not successful"}
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid webhook payload")
