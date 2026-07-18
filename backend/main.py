# Ye file ek Web Server (FastAPI) start karegi aur frontend (Next.js) ke liye endpoints degi.
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware # For React frontend access
from pydantic import BaseModel # For request body validation
import uvicorn # For running the server

from config import settings # For environment variables
from db_services import create_profile, get_profile # For database operations
from agent import app_agent # AI Agent

# Initialize FastAPI App
app = FastAPI(title=settings.PROJECT_NAME)

# CORS Middleware setup (Taaki Next.js frontend bina cross-origin block ke call kar sake)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Development me saare origins allow karte hain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Request schemas using Pydantic (Loose Coupling) ---
class profileRequest(BaseModel):
    name: str
    profession: str

class AnalyzeRequest(BaseModel):
    profile_id: str
    raw_log: str
    profession: str

# 1. Health Check Endpoint
@app.get("/")
def read_root():
    return {"status": "online", "message": "Welcome to FocusAI API Server!"}

# 2. Create User Profile Endpoint
@app.post("/profile")
def api_create_profile(payload: profileRequest):
    try:
        profile = create_profile(name=payload.name, profession=payload.profession)
        return {"success": True, "profile": profile}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# 3. Analyze Daily Log Endpoint (LangGraph Trigger)
@app.post("/analyze")
def api_analyze_log(payload: AnalyzeRequest):
    profile = get_profile(payload.profile_id)
    # Check if profile exists in database
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found in database.")
    # user valid hai  
    try:
        # LangGraph invoke() call (Hum notebook state me variables daal kar employee node trigger kar rahe hain)
        state_input = {
            "raw_log": payload.raw_log,
            "profession": payload.profession,
            "profile_id": payload.profile_id,
            "analysis": {},
            "search_queries": [],
            "search_results": "",
            "final_report": ""
        }

         # Pura flowchart background me execute hoga
        print("Starting LangGraph agent workflow...")
        final_state = app_agent.invoke(state_input)
        print("LangGraph workflow finished!")
        
        return {
            "success": True,
            "analysis": final_state["analysis"],
            "final_report": final_state["final_report"]
        }
    except Exception as e:
        print(f"[ERROR] Agent execution failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Running the app locally via uvicorn if run directly
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=settings.PORT, reload=True)