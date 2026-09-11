from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from ai_qa_analyzer import analyze_requirement_with_ai


app = FastAPI(
    title="MSSPL SmartQA",
    description="AI-Powered Assistant for Manual Testing",
    version="1.0.0"
)


# =========================
# CORS CONFIGURATION
# =========================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================
# REQUEST MODEL
# =========================

class RequirementRequest(BaseModel):
    requirement: str
    coverage_mode: str = "standard"


# =========================
# HOME
# =========================

@app.get("/")
def home():
    return {
        "message": "Welcome to MSSPL SmartQA",
        "status": "Backend is running"
    }


# =========================
# REQUIREMENT ANALYSIS
# =========================

@app.post("/analyze-requirement")
def analyze(request: RequirementRequest):

    result = analyze_requirement_with_ai(
        request.requirement,
        request.coverage_mode
    )

    return result