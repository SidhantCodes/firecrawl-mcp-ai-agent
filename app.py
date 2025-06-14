from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from src.workflow import Workflow
from src.models import CompanyInfo, QueryRequest, ResearchResponse

app = FastAPI(title="Developer Tools Research API")

# Enable CORS (adjust for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with your Next.js domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

workflow = Workflow()

# Root check
@app.get("/")
def root():
    return {"message": "Developer Tools Research API is running."}

# Analysis endpoint
@app.post("/analyze", response_model=ResearchResponse)
def analyze(request: QueryRequest):
    try:
        result = workflow.run(request.query)
        return ResearchResponse(**result.dict())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze: {str(e)}")
