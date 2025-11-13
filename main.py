from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# OLD: you already had this
from routes.training_routes import router as training_router

# NEW: only if you created these files
from routes.assessment_routes import router as assessment_router
from routes.player_routes import router as player_router

load_dotenv()

app = FastAPI(
    title="YoYo Elite Soccer AI",
    description="Backend for assessments and AI training programs",
    version="1.0.0"
)

origins = os.getenv("CORS_ORIGINS", "*").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    return {"status": "ok"}


# ===== OLD BEHAVIOR (still here) =====
app.include_router(training_router, prefix="/api", tags=["training"])

# ===== NEW ROUTES (only work if files exist) =====
app.include_router(player_router, prefix="/api", tags=["players"])
app.include_router(assessment_router, prefix="/api", tags=["assessments"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
