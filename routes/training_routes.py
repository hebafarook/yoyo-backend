from fastapi import APIRouter, HTTPException
from utils.database import db
from utils.llm_integration import generate_training_program
from datetime import datetime

router = APIRouter()

@router.post("/programs/generate")
async def generate_program(player_id: str):
    assessment = await db.assessments.find_one({"player_id": player_id}, sort=[("created_at", -1)])
    if not assessment:
        raise HTTPException(status_code=404, detail="No assessment found for this player")

    player = await db.players.find_one({"player_id": player_id}) or {
        "player_id": player_id,
        "player_name": assessment.get("player_name", "Player"),
        "age": assessment.get("age", 15),
        "position": assessment.get("position", "midfielder"),
    }

    program_text = await generate_training_program(assessment, player)

    await db.training_programs.insert_one({
        "player_id": player_id,
        "program_markdown": program_text,
        "created_at": datetime.utcnow(),
        "source": "chatgpt"
    })

    return {"player_id": player_id, "program": program_text}
