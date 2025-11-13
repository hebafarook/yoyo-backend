from datetime import datetime

from fastapi import APIRouter, HTTPException, Header

from models.player import PlayerRegister, PlayerLogin, PlayerPublic
from utils.database import db
from utils.auth import hash_password, create_session, get_player_by_token

router = APIRouter()


def serialize_player(doc: dict) -> dict:
    """Convert Mongo doc to safe JSON (no password_hash)."""
    if not doc:
        return {}
    out = {
        "id": str(doc.get("_id")),
        "player_id": doc.get("player_id"),
        "name": doc.get("name"),
        "age": doc.get("age"),
        "position": doc.get("position"),
        "dominant_foot": doc.get("dominant_foot"),
        "coach_id": doc.get("coach_id"),
        "email": doc.get("email"),
        "created_at": doc.get("created_at"),
    }
    return out


@router.post("/players/register")
async def register_player(payload: PlayerRegister):
    # Check if player_id already exists
    existing = await db.players.find_one({"player_id": payload.player_id})
    if existing:
        raise HTTPException(status_code=400, detail="Player ID already exists")

    doc = payload.dict()
    raw_password = doc.pop("password")
    doc["password_hash"] = hash_password(raw_password)
    doc["created_at"] = datetime.utcnow()

    await db.players.insert_one(doc)

    # Create session token
    token = await create_session(payload.player_id)

    return {
        "token": token,
        "player": serialize_player(doc),
    }


@router.post("/players/login")
async def login_player(payload: PlayerLogin):
    player = await db.players.find_one({"player_id": payload.player_id})
    if not player:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if player.get("password_hash") != hash_password(payload.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = await create_session(payload.player_id)

    return {
        "token": token,
        "player": serialize_player(player),
    }


@router.get("/players/me")
async def get_me(x_auth_token: str = Header(..., alias="X-Auth-Token")):
    """
    Returns the profile of the currently logged-in player,
    based on the X-Auth-Token header.
    """
    player = await get_player_by_token(x_auth_token)
    if not player:
        raise HTTPException(status_code=401, detail="Invalid or expired session")

    return serialize_player(player)
