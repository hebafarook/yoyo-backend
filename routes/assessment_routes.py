from datetime import datetime
from typing import List

from fastapi import APIRouter, HTTPException

from models.assessment import AssessmentCreate
from utils.database import db

router = APIRouter()


def _serialise(doc: dict) -> dict:
    """Convert Mongo _id to a string for JSON responses."""
    if not doc:
        return doc
    doc["id"] = str(doc.pop("_id"))
    return doc


@router.post("/assessments")
async def create_assessment(assessment: AssessmentCreate):
    """
    Save a new assessment document for a player.
    """
    doc = assessment.dict()
    doc["created_at"] = datetime.utcnow()
    result = await db.assessments.insert_one(doc)
    doc["id"] = str(result.inserted_id)
    return doc


@router.get("/players/{player_id}/latest-assessment")
async def get_latest_assessment(player_id: str):
    """
    Get the most recent assessment for a given player.
    """
    assessment = await db.assessments.find_one(
        {"player_id": player_id},
        sort=[("created_at", -1)],
    )

    if not assessment:
        raise HTTPException(status_code=404, detail="No assessment found for this player")

    return _serialise(assessment)


@router.get("/players/{player_id}/assessments")
async def list_assessments(player_id: str) -> List[dict]:
    """
    List all assessments for a player, oldest → newest.
    """
    cursor = db.assessments.find({"player_id": player_id}).sort("created_at", 1)
    assessments: List[dict] = []
    async for doc in cursor:
        assessments.append(_serialise(doc))
    return assessments
