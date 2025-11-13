from fastapi import APIRouter, HTTPException
from datetime import datetime

from utils.database import db
from utils.llm_integration import generate_training_program

# Router with tag for cleaner API docs (optional but recommended)
router = APIRouter(tags=["training"])


@router.post("/programs/generate")
async def generate_program(player_id: str):
    """
    Generate a 4-week AI training program for the given player_id.
    """

    # Get the most recent assessment for this player
    assessment = await db.assessments.find_one(
        {"player_id": player_id},
        sort=[("created_at", -1)]
    )

    if not assessment:
        raise HTTPException(
            status_code=404,
            detail="No assessment found for this player"
        )

    # Get player info from database or fallback to basic info from assessment
    player = await db.players.find_one({"player_id": player_id}) or {
        "player_id": player_id,
        "player_name": assessment.get("player_name", "Player"),
        "age": assessment.get("age", 15),
        "position": assessment.get("position", "midfielder"),
    }

    # Generate personalized training program using OpenAI
    program_text = await generate_training_program(assessment, player)

    # Save generated program into database
    await db.training_programs.insert_one({
        "player_id": player_id,
        "program_markdown": program_text,
        "created_at": datetime.utcnow(),
        "source": "chatgpt"
    })

    # Return the program back to frontend / caller
    return {
        "player_id": player_id,
        "program": program_text
    }
